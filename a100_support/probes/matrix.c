#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

extern uint64_t probe_vlenb(void);
extern uint64_t probe_read_mcpm(void);
extern void probe_ime_i8(const void *, const void *, int32_t *);
extern void probe_ime_i4(const void *, const void *, int32_t *);
extern void probe_ime_float(const void *, const void *, float *, uint64_t);

static int integer_test(int bits) {
  int k = bits == 4 ? 32 : 16;
  int8_t a[256], b[256];
  uint8_t pa[128] = {0}, pb[128] = {0};
  int32_t out[64];
  for (int i=0;i<8*k;i++) {
    a[i]=(i*3+2)%13-6; b[i]=(i*5+1)%13-6;
    if (bits==4) {
      pa[i/2] |= ((uint8_t)a[i]&15) << ((i%2)*4);
      pb[i/2] |= ((uint8_t)b[i]&15) << ((i%2)*4);
    }
  }
  if (bits==4) probe_ime_i4(pa,pb,out); else probe_ime_i8(a,b,out);
  for (int m=0;m<8;m++) for (int n=0;n<8;n++) {
    int32_t expected=0;
    for (int q=0;q<k;q++) expected += a[m*k+q]*b[n*k+q];
    if (expected!=out[m*8+n]) {
      fprintf(stderr,"INT%d mismatch (%d,%d): %d != %d\n",bits,m,n,out[m*8+n],expected);
      return 1;
    }
  }
  return 0;
}

static int floating_test(int bf16, uint64_t mcpm) {
  uint16_t a[64],b[64]; float av[64],bv[64],out[64];
  for (int i=0;i<64;i++) {
    av[i]=(float)((i*3)%11-5)/4; bv[i]=(float)((i*5)%11-5)/4;
    if (bf16) {
      uint32_t ai,bi;
      memcpy(&ai,&av[i],4); memcpy(&bi,&bv[i],4);
      a[i]=(uint16_t)(ai>>16); b[i]=(uint16_t)(bi>>16);
    } else {
      _Float16 ah=(_Float16)av[i],bh=(_Float16)bv[i];
      memcpy(&a[i],&ah,2); memcpy(&b[i],&bh,2);
    }
  }
  probe_ime_float(a,b,out,mcpm);
  for (int m=0;m<8;m++) for (int n=0;n<8;n++) {
    float expected=0;
    for (int q=0;q<8;q++) expected += av[m*8+q]*bv[n*8+q];
    if (expected!=out[m*8+n]) return 1; /* dyadic values: exact FP32 result */
  }
  return 0;
}

int main(int argc,char **argv) {
  const char *kind=argc>1?argv[1]:"int8";
  if (!strcmp(kind,"csr")) {
    printf("mcpm=%llu\n",(unsigned long long)probe_read_mcpm());
    return 0;
  }
  if (probe_vlenb()!=128) return 2;
  int failed;
  uint64_t mcpm=0;
  if (!strcmp(kind,"int8")) failed=integer_test(8);
  else if (!strcmp(kind,"int4")) failed=integer_test(4);
  else if (!strcmp(kind,"fp16")) failed=floating_test(0,argc>2?strtoull(argv[2],0,0):mcpm);
  else if (!strcmp(kind,"bf16")) failed=floating_test(1,argc>2?strtoull(argv[2],0,0):mcpm);
  else return 2;
  printf("{\"probe\":\"%s\",\"passed\":%s,\"vlenb\":128,\"mcpm_control\":\"default-no-userspace-access\"}\n",
         kind,failed?"false":"true");
  return failed;
}
