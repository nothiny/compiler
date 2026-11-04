/* Transport test fixture. This does not implement or masquerade as a compiler. */
#include "../native_bundle.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
int main(int argc,char **argv) {
  if(argc!=3) return 2;
  struct a100_bundle bundle;
  if(a100_bundle_open(&bundle,argv[1])) return 3;
  int result=0;
  if(!strcmp(argv[2],"roundtrip")) {
    /* Opening validates and patches all relocation records. */
  } else if(!strcmp(argv[2],"alias")) {
    if(bundle.nviews!=3) return 4;
    struct a100_view *a=&bundle.views[0],*b=&bundle.views[1],*table=&bundle.views[2];
    uint64_t pointer;memcpy(&pointer,table->data,8);
    if(pointer!=(uintptr_t)b->data) return 5;
    *(int32_t *)(uintptr_t)pointer+=100;
    for(int64_t i=1;i<b->shape[0];i++)
      *(int32_t *)(b->data+i*b->strides[0])+=100;
    if(a->storage!=b->storage) return 6;
  } else if(!strcmp(argv[2],"bf16")) {
    if(bundle.nviews!=1 || bundle.views[0].dtype!=11) return 7;
    struct a100_view *a=&bundle.views[0];
    for(int64_t i=0;i<a->shape[0];i++) {
      uint16_t *value=(uint16_t *)(a->data+i*a->strides[0]);
      *value^=0x8000;
    }
  } else if(!strcmp(argv[2],"scalars")) {
    if(bundle.nviews!=1 || bundle.views[0].dtype!=9) return 8;
    for(uint32_t i=0;i<bundle.nscalars;i++)
      memcpy(bundle.views[0].data+i*8,&bundle.scalars[i].bits,8);
  } else result=2;
  if(a100_bundle_close(&bundle)) return 9;
  printf("{\"fixture\":\"native-io\",\"passed\":%s}\n",result?"false":"true");
  return result;
}
