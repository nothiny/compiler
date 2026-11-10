/* Guest dynamic instruction profiler -- human-guided matmul optimization
 * round (evidence: docs/compiler-agent/optimizations/matmul/tooling/).
 *
 * Modeled on a100_support/probes/instruction_counts.c (the IME-only
 * counter), but registers an execution callback for EVERY translated guest
 * instruction and keys rows by pc in a hash table, so one pc has one row
 * even when it is translated inside several translation blocks.  Counts
 * are guest dynamic executions (per-insn exec callbacks -- the round's
 * judge quantity), per row, per vcpu, and as per-vcpu grand totals.  The
 * raw mnemonic, encoding size and category are kept in every row so the
 * categorization is auditable and re-mappable offline.
 *
 * Vendor smt.* encodings are decoded exactly like the original probe: the
 * stock disassembler in this QEMU package does not spell them.
 *
 * Category notes: "scalar-arith" includes scalar FP ops; "system" holds
 * ecall/ebreak/fence/csr*; "atomic" holds lr./sc./amo*; compressed forms
 * are bucketed with their uncompressed class.
 *
 * Usage:   -plugin full_instruction_counts.so,out=<path.json>
 * Schema:  a100c-dynamic-instruction-profile/v1
 */
#include <qemu-plugin.h>
#include <pthread.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

QEMU_PLUGIN_EXPORT int qemu_plugin_version = QEMU_PLUGIN_VERSION;

#define MAX_VCPU 16
#define HASH_BUCKETS 8192u

enum {
    CAT_IME = 0, CAT_VEC_CONFIG, CAT_VEC_MEM, CAT_VEC_ARITH,
    CAT_SCALAR_LOAD, CAT_SCALAR_STORE, CAT_ATOMIC,
    CAT_SCALAR_ARITH, CAT_BRANCH, CAT_SYSTEM, CAT_COUNT
};
static const char *const CATEGORY_NAMES[CAT_COUNT] = {
    "ime", "vec-config", "vec-mem", "vec-arith",
    "scalar-load", "scalar-store", "atomic",
    "scalar-arith", "branch", "system"
};

struct row {
    uint64_t pc;
    char mnemonic[48];
    char operand_format[32];
    uint8_t size;
    uint8_t category;
    _Atomic uint64_t total;
    _Atomic uint64_t per_vcpu[MAX_VCPU];
    _Atomic uint64_t overflow_vcpu; /* executions on vcpu >= MAX_VCPU */
    struct row *next;
};

static struct row *buckets[HASH_BUCKETS];
static size_t row_count;
static pthread_mutex_t lock = PTHREAD_MUTEX_INITIALIZER;
static char *output;
static _Atomic uint64_t grand[MAX_VCPU];
static _Atomic uint64_t grand_overflow;

static int starts_with(const char *s, const char *prefix)
{
    return strncmp(s, prefix, strlen(prefix)) == 0;
}

static int in_set(const char *m, const char *const *set)
{
    for (size_t i = 0; set[i]; i++) {
        if (strcmp(m, set[i]) == 0) {
            return 1;
        }
    }
    return 0;
}

/* One central categorization table.  The raw mnemonic is retained in every
 * output row, so any mis-bucketing is auditable and re-mappable offline. */
static int categorize(const char *m)
{
    static const char *const scalar_loads[] =
        {"ld", "lw", "lwu", "lh", "lhu", "lb", "lbu",
         "fld", "flw", "flh", NULL};
    static const char *const scalar_stores[] =
        {"sd", "sw", "sh", "sb", "fsd", "fsw", "fsh", NULL};
    static const char *const branches[] =
        {"beq", "bne", "blt", "bge", "bltu", "bgeu",
         "beqz", "bnez", "bltz", "bgez", "bgt", "ble", "bgtu", "bleu",
         "jal", "jalr", "j", "jr", "ret", "call", "tail", NULL};
    static const char *const c_loads[] =
        {"ld", "lw", "ldsp", "lwsp", "fld", "flw", "fldsp", "flwsp", NULL};
    static const char *const c_stores[] =
        {"sd", "sw", "sdsp", "swsp", "fsd", "fsw", "fsdsp", "fswsp", NULL};
    static const char *const c_branches[] =
        {"beqz", "bnez", "j", "jal", "jr", "jalr", NULL};

    if (starts_with(m, "smt.")) {
        return CAT_IME;
    }
    if (strcmp(m, "vsetvli") == 0 || strcmp(m, "vsetivli") == 0 ||
        strcmp(m, "vsetvl") == 0) {
        return CAT_VEC_CONFIG;
    }
    if (m[0] == 'v') {
        if (starts_with(m, "vle") || starts_with(m, "vse") ||
            starts_with(m, "vlse") || starts_with(m, "vsse") ||
            starts_with(m, "vlox") || starts_with(m, "vlux") ||
            starts_with(m, "vsox") || starts_with(m, "vsux") ||
            starts_with(m, "vlseg") || starts_with(m, "vsseg") ||
            starts_with(m, "vlrei") || starts_with(m, "vl1r") ||
            starts_with(m, "vl2r") || starts_with(m, "vl4r") ||
            starts_with(m, "vl8r") || starts_with(m, "vs1r") ||
            starts_with(m, "vs2r") || starts_with(m, "vs4r") ||
            starts_with(m, "vs8r")) {
            return CAT_VEC_MEM;
        }
        return CAT_VEC_ARITH;
    }
    if (starts_with(m, "c.")) {
        const char *r = m + 2;
        if (in_set(r, c_loads)) {
            return CAT_SCALAR_LOAD;
        }
        if (in_set(r, c_stores)) {
            return CAT_SCALAR_STORE;
        }
        if (in_set(r, c_branches)) {
            return CAT_BRANCH;
        }
        return CAT_SCALAR_ARITH;
    }
    if (in_set(m, scalar_loads)) {
        return CAT_SCALAR_LOAD;
    }
    if (in_set(m, scalar_stores)) {
        return CAT_SCALAR_STORE;
    }
    if (starts_with(m, "amo") || starts_with(m, "lr.") ||
        starts_with(m, "sc.")) {
        return CAT_ATOMIC;
    }
    if (in_set(m, branches)) {
        return CAT_BRANCH;
    }
    if (strcmp(m, "ecall") == 0 || strcmp(m, "ebreak") == 0 ||
        strcmp(m, "fence") == 0 || starts_with(m, "fence") ||
        strcmp(m, "wfi") == 0 || strcmp(m, "sret") == 0 ||
        strcmp(m, "mret") == 0 || starts_with(m, "csr") ||
        starts_with(m, "sfence")) {
        return CAT_SYSTEM;
    }
    return CAT_SCALAR_ARITH;
}

static void execute(unsigned int vcpu, void *opaque)
{
    struct row *row = opaque;
    atomic_fetch_add_explicit(&row->total, 1, memory_order_relaxed);
    if (vcpu < MAX_VCPU) {
        atomic_fetch_add_explicit(&row->per_vcpu[vcpu], 1,
                                  memory_order_relaxed);
        atomic_fetch_add_explicit(&grand[vcpu], 1, memory_order_relaxed);
    } else {
        atomic_fetch_add_explicit(&row->overflow_vcpu, 1,
                                  memory_order_relaxed);
        atomic_fetch_add_explicit(&grand_overflow, 1, memory_order_relaxed);
    }
}

static void translate(qemu_plugin_id_t id, struct qemu_plugin_tb *tb)
{
    (void)id;
    for (size_t i = 0; i < qemu_plugin_tb_n_insns(tb); i++) {
        struct qemu_plugin_insn *insn = qemu_plugin_tb_get_insn(tb, i);
        char *disassembly = qemu_plugin_insn_disas(insn);
        unsigned char bytes[4] = {0, 0, 0, 0};
        const char *decoded = NULL;
        const char *fmt = "";
        if (qemu_plugin_insn_data(insn, bytes, 4) == 4) {
            uint32_t word = (uint32_t)bytes[0] |
                            ((uint32_t)bytes[1] << 8) |
                            ((uint32_t)bytes[2] << 16) |
                            ((uint32_t)bytes[3] << 24);
            /* Vendor encodings for the probe forms; the stock
             * disassembler in this QEMU package does not spell them. */
            switch (word & 0xfe00707fU) {
            case 0xe200302bU:
                decoded = "smt.vmadot";
                fmt = "i8";
                break;
            case 0xc200302bU:
                decoded = "smt.vmadot";
                fmt = "i4";
                break;
            case 0x9e00402bU:
                decoded = "smt.vfwmadot";
                fmt = "MCPM-selected-float16";
                break;
            }
        }
        char mn[48];
        if (decoded) {
            snprintf(mn, sizeof mn, "%s", decoded);
        } else if (disassembly) {
            if (strstr(disassembly, "vfwmadot")) {
                snprintf(mn, sizeof mn, "smt.vfwmadot");
            } else if (strstr(disassembly, "vmadot")) {
                snprintf(mn, sizeof mn, "smt.vmadot");
            } else if (sscanf(disassembly, "%47s", mn) != 1) {
                snprintf(mn, sizeof mn, "unknown");
            }
        } else {
            snprintf(mn, sizeof mn, "unknown");
        }
        uint64_t pc = qemu_plugin_insn_vaddr(insn);
        uint8_t size = (uint8_t)qemu_plugin_insn_size(insn);
        uint32_t h = (uint32_t)((pc >> 2) * 2654435761u) &
                     (HASH_BUCKETS - 1);
        struct row *row = NULL;
        pthread_mutex_lock(&lock);
        for (struct row *r = buckets[h]; r; r = r->next) {
            if (r->pc == pc) {
                row = r;
                break;
            }
        }
        if (!row) {
            row = calloc(1, sizeof *row);
            if (!row) {
                abort();
            }
            row->pc = pc;
            snprintf(row->mnemonic, sizeof row->mnemonic, "%s", mn);
            snprintf(row->operand_format, sizeof row->operand_format, "%s",
                     fmt);
            row->size = size;
            row->category = (uint8_t)categorize(mn);
            row->next = buckets[h];
            buckets[h] = row;
            row_count++;
        }
        pthread_mutex_unlock(&lock);
        qemu_plugin_register_vcpu_insn_exec_cb(
            insn, execute, QEMU_PLUGIN_CB_NO_REGS, row);
        free(disassembly);
    }
}

static int by_pc(const void *a, const void *b)
{
    const struct row *x = *(const struct row *const *)a;
    const struct row *y = *(const struct row *const *)b;
    if (x->pc < y->pc) {
        return -1;
    }
    if (x->pc > y->pc) {
        return 1;
    }
    return strcmp(x->mnemonic, y->mnemonic);
}

static void finished(qemu_plugin_id_t id, void *ud)
{
    (void)id;
    (void)ud;
    struct row **all = malloc(sizeof(*all) * (row_count ? row_count : 1));
    if (!all) {
        perror("malloc");
        return;
    }
    size_t n = 0;
    unsigned long long total = 0;
    for (unsigned b = 0; b < HASH_BUCKETS; b++) {
        for (struct row *r = buckets[b]; r; r = r->next) {
            all[n++] = r;
            total += (unsigned long long)atomic_load(&r->total);
        }
    }
    qsort(all, n, sizeof(*all), by_pc);
    FILE *file = fopen(output, "w");
    if (!file) {
        perror(output);
        free(all);
        return;
    }
    fputs("{\"schema\":\"a100c-dynamic-instruction-profile/v1\",", file);
    fputs("\"categories\":[", file);
    for (int i = 0; i < CAT_COUNT; i++) {
        fprintf(file, "%s\"%s\"", i ? "," : "", CATEGORY_NAMES[i]);
    }
    fprintf(file, "],\"max_vcpu\":%d,", MAX_VCPU);
    fputs("\"per_vcpu_totals\":[", file);
    for (int i = 0; i < MAX_VCPU; i++) {
        fprintf(file, "%s%llu", i ? "," : "",
                (unsigned long long)atomic_load(&grand[i]));
    }
    fprintf(file, "],\"per_vcpu_totals_overflow\":%llu,",
            (unsigned long long)atomic_load(&grand_overflow));
    fprintf(file, "\"total_dynamic_instructions\":%llu,", total);
    fprintf(file, "\"distinct_pcs\":%zu,", n);
    fputs("\"instructions\":[", file);
    for (size_t i = 0; i < n; i++) {
        struct row *r = all[i];
        fprintf(file,
                "%s{\"pc\":%llu,\"mnemonic\":\"%s\",\"format\":\"%s\","
                "\"size\":%u,\"category\":\"%s\",\"executions\":%llu,"
                "\"per_vcpu\":[",
                i ? "," : "", (unsigned long long)r->pc, r->mnemonic,
                r->operand_format, r->size, CATEGORY_NAMES[r->category],
                (unsigned long long)atomic_load(&r->total));
        for (int v = 0; v < MAX_VCPU; v++) {
            fprintf(file, "%s%llu", v ? "," : "",
                    (unsigned long long)atomic_load(&r->per_vcpu[v]));
        }
        fprintf(file, "],\"per_vcpu_overflow\":%llu}",
                (unsigned long long)atomic_load(&r->overflow_vcpu));
    }
    fputs("]}\n", file);
    fclose(file);
    free(all);
}

QEMU_PLUGIN_EXPORT int qemu_plugin_install(qemu_plugin_id_t id,
                                           const qemu_info_t *info,
                                           int argc, char **argv)
{
    if (strcmp(info->target_name, "riscv64")) {
        return -1;
    }
    for (int i = 0; i < argc; i++) {
        if (strncmp(argv[i], "out=", 4) == 0) {
            output = strdup(argv[i] + 4);
        }
    }
    if (!output) {
        return -1;
    }
    qemu_plugin_register_vcpu_tb_trans_cb(id, translate);
    qemu_plugin_register_atexit_cb(id, finished, 0);
    return 0;
}
