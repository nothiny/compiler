/* a100rt.h -- the single runtime <-> generated-code ABI declaration.
 *
 * This header is the ONE place the contract between the precompiled native C
 * runtime (a100c/runtime) and a generated operator program is declared
 * (RT-ARGUMENT-MARSHALLING).  The emitter and the runtime both derive from it;
 * there are never two independent assumptions.  Calling conventions follow the
 * RISC-V psABI as configured for this target: lp64d, rv64gcv (integer arguments
 * in a0-a7, floating arguments in fa0-fa7, t0-t6/ra caller-saved, s0-s11
 * callee-saved, stack 16-byte aligned at call boundaries; facts F045/F002).
 *
 * Process contract (the runtime owns main, F043):
 *   operator_exec --bundle <path> --threads <n> [--repeats <k>]
 *     --threads  1, 2, 4 or 8 compute workers (F053: at most 8)
 *     --repeats  execute the operator k independent times on the same case
 *
 * Execution model:
 *   - The runtime opens the a100-native-io/v1 bundle (validation, pointer-table
 *     relocation patching), snapshots the mapped image, creates the persistent
 *     worker pool ONCE per process, then for each repeat restores the snapshot
 *     (every repeat is an independent execution on the same case), zeroes the
 *     workspace and releases the workers.  Outputs are read back by the host
 *     after the process exits.
 *   - Each worker thread calls operator_entry(launch) once per repeat with its
 *     own launch context.  operator_entry must return; a stage barrier
 *     (a100rt_stage_barrier) must be called the same number of times by every
 *     worker of a call -- the stage contract.  Work partition is the operator's
 *     responsibility: it derives its ranges from (worker_id, worker_count).
 *   - Workspace regions are allocated once per process and zeroed by the
 *     runtime before every call: an operator must not rely on workspace
 *     contents across calls.  Thread-private regions are 64-byte aligned and
 *     padded so no two workers share a 64-byte line.
 *   - The operator writes only elements reachable through output-marked views
 *     (flags & A100RT_VIEW_OUTPUT); the input snapshot/restore makes repeated
 *     calls independent.
 *   - It records the number of work items it owned in launch->stats->items
 *     (observation contract for pool coverage evidence).
 *
 * The delivered executable neither starts, embeds nor calls Python (F043).
 */
#ifndef A100RT_H
#define A100RT_H

#include <stddef.h>
#include <stdint.h>

#define A100RT_ABI_VERSION 1
#define A100RT_MAX_WORKERS 8

/* Process exit codes (the host transport distinguishes these). */
#define A100RT_EXIT_OK 0
#define A100RT_EXIT_USAGE 2            /* command line outside the contract */
#define A100RT_EXIT_REJECTED 3         /* bundle violates a100-native-io/v1 */
#define A100RT_EXIT_RESOURCE 4         /* pool/workspace allocation failure */
#define A100RT_EXIT_REPEAT_MISMATCH 5  /* repeats produced different outputs */
#define A100RT_EXIT_SYNC 6             /* bundle close/msync failed */

/* dtype codes of the a100-native-io/v1 format (little-endian value bits). */
enum a100rt_dtype {
  A100RT_DTYPE_BOOL = 1,
  A100RT_DTYPE_INT8 = 2,
  A100RT_DTYPE_UINT8 = 3,
  A100RT_DTYPE_INT16 = 4,
  A100RT_DTYPE_UINT16 = 5,
  A100RT_DTYPE_INT32 = 6,
  A100RT_DTYPE_UINT32 = 7,
  A100RT_DTYPE_INT64 = 8,
  A100RT_DTYPE_UINT64 = 9,
  A100RT_DTYPE_FLOAT16 = 10,
  A100RT_DTYPE_BFLOAT16 = 11,
  A100RT_DTYPE_FLOAT32 = 12,
  A100RT_DTYPE_FLOAT64 = 13,
};

/* view flags */
#define A100RT_VIEW_OUTPUT 1u

/* A strided view over one bundle storage payload.  Filled by the runtime's
 * bundle reader; read by generated code. */
struct a100rt_view {
  unsigned char *data;    /* element base = storage + offset */
  int64_t *shape;         /* ndim extents (points into the bundle image) */
  int64_t *strides;       /* ndim byte strides (points into the bundle image) */
  uint64_t storage_size;  /* backing payload size in bytes */
  uint32_t dtype;         /* enum a100rt_dtype */
  uint32_t ndim;
  uint32_t flags;         /* bit 0: A100RT_VIEW_OUTPUT */
  uint32_t reserved_;
  unsigned char *storage; /* payload base */
};

/* A typed scalar argument.  The in-memory layout equals the on-disk
 * a100-native-io/v1 record (dtype, size, bits) because scalars are read
 * directly out of the mapped bundle image. */
struct a100rt_scalar {
  uint32_t dtype; /* enum a100rt_dtype */
  uint32_t size;  /* value width in bytes */
  uint64_t bits;  /* raw little-endian value bits */
};

/* The opened bundle: the argument layout both sides derive from (F046/F047).
 * Views and scalars appear in the sorted-argument-name order the host packer
 * declares; the binary carries no names. */
struct a100rt_bundle {
  /* operator-visible */
  struct a100rt_view *views;     /* nviews entries (heap) */
  struct a100rt_scalar *scalars; /* nscalars entries (in the image) */
  uint32_t nviews;
  uint32_t nscalars;
  uint32_t nrelocations;
  uint32_t reserved_;
  unsigned char *mapping; /* whole image; snapshot/restore span */
  uint64_t size;          /* image bytes */
  /* runtime-internal bookkeeping -- generated code must not rely on it */
  unsigned char *relocations; /* nrelocations * 24 bytes (in the image) */
  uint64_t *originals;        /* saved pointer-table words, restored on close */
  int fd;
  /* appended AFTER every asm-read field (the _Static_assert pins their
   * offsets; appending shifts nothing): the storage-union span the
   * repeat loop restores/compares */
  uint64_t writable_start, writable_end;
};

/* Per-worker observation record, written by the operator during a call. */
struct a100rt_stats {
  uint64_t items;       /* work items owned by this worker in this call */
  uint64_t reserved_[7]; /* pad the record to one 64-byte line */
};

/* The per-worker launch context passed to operator_entry in a0 (lp64d). */
struct a100rt_launch {
  const struct a100rt_bundle *bundle; /* argument layout */
  void *workspace_shared;             /* shared scratch, zeroed before each call */
  void *workspace_private;            /* this worker's padded region, zeroed */
  struct a100rt_stats *stats;         /* this worker's observation record */
  void *runtime;                      /* opaque runtime handle (stage barrier) */
  uint32_t worker_id;                 /* 0 .. worker_count-1 */
  uint32_t worker_count;              /* 1, 2, 4 or 8 */
};

/* ---- runtime-provided helpers (callable from generated assembly) ---- */

/* Cross-worker stage barrier for one operator call: every worker of the call
 * must reach it the same number of times (visibility point between stages,
 * F054/A006: explicit synchronization, no assumed coherence).  With one worker
 * it returns immediately. */
void a100rt_stage_barrier(const struct a100rt_launch *launch);

/* Bundle reader: validates the whole a100-native-io/v1 image and patches the
 * pointer-table relocations only after every record validated, so a rejected
 * bundle is never written (recorded refusal, never a wrong result).  Returns 0
 * on success; on failure returns -1, sets *reason and leaves the file
 * untouched (a100rt_reject_reason names the reason). */
int a100rt_bundle_open(struct a100rt_bundle *b, const char *path, int *reason);
int a100rt_bundle_close(struct a100rt_bundle *b); /* restores relocated words */
void a100rt_bundle_writable(const struct a100rt_bundle *b, uint64_t *start,
                            uint64_t *end); /* storage-union span */
const char *a100rt_reject_reason(int code);

/* Persistent worker pool (opaque; defined in pool.c). */
struct a100rt_pool;
int a100rt_pool_create(struct a100rt_pool **out, int workers,
                       const struct a100rt_bundle *bundle,
                       uint64_t private_bytes, uint64_t shared_bytes);
void a100rt_pool_call(struct a100rt_pool *pool);
void a100rt_pool_observe(const struct a100rt_pool *pool, uint64_t *tids, uint64_t *items);
void a100rt_pool_destroy(struct a100rt_pool *pool);

/* Pool diagnostics: number of successful pool creations in this process
 * (the contract is exactly one per process, F019). */
uint64_t a100rt_pool_initializations(void);

/* ---- operator-program-provided symbols (the emitter generates these;
 *      a100c/runtime/operator_stub.S is the hand-written boundary witness) ---- */

/* One worker's execution of the operator for one call. */
void operator_entry(const struct a100rt_launch *launch);

/* Workspace requirements in bytes.  The runtime provides weak defaults; a
 * generated program defines its own to override them. */
uint64_t operator_workspace_private(void);
uint64_t operator_workspace_shared(void);

/* Struct layout pins: the hand-written stub (and later the emitter) address
 * these fields at fixed offsets; the header is the single declaration, so a
 * layout change must update these assertions and the assembly together. */
_Static_assert(offsetof(struct a100rt_view, data) == 0, "asm: view.data");
_Static_assert(offsetof(struct a100rt_view, shape) == 8, "asm: view.shape");
_Static_assert(offsetof(struct a100rt_view, strides) == 16, "asm: view.strides");
_Static_assert(offsetof(struct a100rt_view, storage_size) == 24, "asm: view.storage_size");
_Static_assert(offsetof(struct a100rt_view, dtype) == 32, "asm: view.dtype");
_Static_assert(offsetof(struct a100rt_view, ndim) == 36, "asm: view.ndim");
_Static_assert(offsetof(struct a100rt_view, flags) == 40, "asm: view.flags");
_Static_assert(offsetof(struct a100rt_view, storage) == 48, "asm: view.storage");
_Static_assert(sizeof(struct a100rt_view) == 56, "asm: sizeof(view)");

_Static_assert(offsetof(struct a100rt_scalar, dtype) == 0, "asm: scalar.dtype");
_Static_assert(offsetof(struct a100rt_scalar, size) == 4, "asm: scalar.size");
_Static_assert(offsetof(struct a100rt_scalar, bits) == 8, "asm: scalar.bits");
_Static_assert(sizeof(struct a100rt_scalar) == 16, "asm: sizeof(scalar)");

_Static_assert(offsetof(struct a100rt_bundle, views) == 0, "asm: bundle.views");
_Static_assert(offsetof(struct a100rt_bundle, scalars) == 8, "asm: bundle.scalars");
_Static_assert(offsetof(struct a100rt_bundle, nviews) == 16, "asm: bundle.nviews");
_Static_assert(offsetof(struct a100rt_bundle, nscalars) == 20, "asm: bundle.nscalars");
_Static_assert(offsetof(struct a100rt_bundle, mapping) == 32, "asm: bundle.mapping");
_Static_assert(offsetof(struct a100rt_bundle, size) == 40, "asm: bundle.size");

_Static_assert(offsetof(struct a100rt_launch, bundle) == 0, "asm: launch.bundle");
_Static_assert(offsetof(struct a100rt_launch, workspace_shared) == 8, "asm: launch.workspace_shared");
_Static_assert(offsetof(struct a100rt_launch, workspace_private) == 16, "asm: launch.workspace_private");
_Static_assert(offsetof(struct a100rt_launch, stats) == 24, "asm: launch.stats");
_Static_assert(offsetof(struct a100rt_launch, runtime) == 32, "asm: launch.runtime");
_Static_assert(offsetof(struct a100rt_launch, worker_id) == 40, "asm: launch.worker_id");
_Static_assert(offsetof(struct a100rt_launch, worker_count) == 44, "asm: launch.worker_count");
_Static_assert(sizeof(struct a100rt_launch) == 48, "asm: sizeof(launch)");
_Static_assert(sizeof(struct a100rt_stats) == 64, "asm: sizeof(stats)");

#endif /* A100RT_H */
