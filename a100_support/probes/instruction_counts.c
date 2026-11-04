/* Dynamic instruction observer using the installed QEMU 10 plugin API.
 * Counts execution callbacks, not translated/static instruction listings.
 */
#include <qemu-plugin.h>
#include <stdatomic.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

QEMU_PLUGIN_EXPORT int qemu_plugin_version=QEMU_PLUGIN_VERSION;
struct observed {
  char mnemonic[64],format[32]; uint64_t pc;
  _Atomic uint64_t count;
  struct observed *next;
};
static struct observed *head;
static pthread_mutex_t lock=PTHREAD_MUTEX_INITIALIZER;
static char *output;
static void execute(unsigned int vcpu,void *opaque) {
  (void)vcpu;
  struct observed *row=opaque;
  atomic_fetch_add_explicit(&row->count,1,memory_order_relaxed);
}
static void translate(qemu_plugin_id_t id,struct qemu_plugin_tb *tb) {
  (void)id;
  for(size_t i=0;i<qemu_plugin_tb_n_insns(tb);i++) {
    struct qemu_plugin_insn *insn=qemu_plugin_tb_get_insn(tb,i);
    char *disassembly=qemu_plugin_insn_disas(insn);
    unsigned char bytes[4];
    const char *decoded=0;
    const char *format="";
    if(qemu_plugin_insn_data(insn,bytes,4)==4) {
      uint32_t word=bytes[0]|((uint32_t)bytes[1]<<8)|((uint32_t)bytes[2]<<16)|((uint32_t)bytes[3]<<24);
      /* Vendor as encodings for the three probe forms. The stock disassembler
       * in this QEMU package does not spell these custom instructions. */
      switch(word & 0xfe00707fU) {
        case 0xe200302bU: decoded="smt.vmadot";format="i8";break;
        case 0xc200302bU: decoded="smt.vmadot";format="i4";break;
        case 0x9e00402bU: decoded="smt.vfwmadot";format="MCPM-selected-float16";break;
      }
    }
    if(decoded || (disassembly && (strstr(disassembly,"vmadot") || strstr(disassembly,"vfwmadot")))) {
      struct observed *row=calloc(1,sizeof(*row));
      if(!row) abort();
      sscanf(decoded?decoded:disassembly,"%63s",row->mnemonic);
      snprintf(row->format,sizeof(row->format),"%s",format);
      row->pc=qemu_plugin_insn_vaddr(insn);
      pthread_mutex_lock(&lock);row->next=head;head=row;pthread_mutex_unlock(&lock);
      qemu_plugin_register_vcpu_insn_exec_cb(insn,execute,QEMU_PLUGIN_CB_NO_REGS,row);
    }
    free(disassembly);
  }
}
static void finished(qemu_plugin_id_t id,void *opaque) {
  (void)id;(void)opaque;
  FILE *file=fopen(output,"w");
  if(!file) {perror(output);return;}
  fputs("{\"schema\":\"qemu-dynamic-instructions/v1\",\"instructions\":[",file);
  int first=1;
  for(struct observed *row=head;row;row=row->next) {
    fprintf(file,"%s{\"mnemonic\":\"%s\",\"operand_format\":\"%s\",\"pc\":%llu,\"executions\":%llu}",
            first?"":",",row->mnemonic,row->format,(unsigned long long)row->pc,
            (unsigned long long)atomic_load(&row->count));
    first=0;
  }
  fputs("]}\n",file);fclose(file);
}
QEMU_PLUGIN_EXPORT int qemu_plugin_install(qemu_plugin_id_t id,const qemu_info_t *info,
                                          int argc,char **argv) {
  if(strcmp(info->target_name,"riscv64")) return -1;
  for(int i=0;i<argc;i++) if(!strncmp(argv[i],"out=",4)) output=strdup(argv[i]+4);
  if(!output) return -1;
  qemu_plugin_register_vcpu_tb_trans_cb(id,translate);
  qemu_plugin_register_atexit_cb(id,finished,0);
  return 0;
}
