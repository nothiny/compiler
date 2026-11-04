/* Privileged format-control probe only; this is not the Linux operator runner. */
typedef unsigned short u16;
typedef unsigned int u32;
typedef unsigned long u64;
extern void probe_ime_float(const void *,const void *,float *,u64);
extern u64 probe_vlenb(void);
static void puts_uart(const char *s) {
  volatile unsigned char *uart=(volatile unsigned char *)0x10000000;
  while(*s) *uart=(unsigned char)*s++;
}
static int test(int bf16,u64 control) {
  u16 a[64],b[64]; float av[64],bv[64],out[64];
  for(int i=0;i<64;i++) {
    av[i]=(float)((i*3)%11-5)/4;bv[i]=(float)((i*5)%11-5)/4;
    if(bf16) {
      union {float f;u32 u;} x={.f=av[i]},y={.f=bv[i]};
      a[i]=(u16)(x.u>>16);b[i]=(u16)(y.u>>16);
    } else {
      union {_Float16 f;u16 u;} x={.f=(_Float16)av[i]},y={.f=(_Float16)bv[i]};
      a[i]=x.u;b[i]=y.u;
    }
  }
  __asm__ volatile("csrw mcpm,%0"::"r"(control):"memory");
  probe_ime_float(a,b,out,0);
  for(int m=0;m<8;m++) for(int n=0;n<8;n++) {
    float expected=0;
    for(int k=0;k<8;k++) expected+=av[m*8+k]*bv[n*8+k];
    if(out[m*8+n]!=expected) return 1;
  }
  return 0;
}
int bare_main(void) {
  if(probe_vlenb()!=128) return 2;
  if(test(0,0)) return 3;
  puts_uart("FP16_MACHINE_PASS\n");
  for(int bit=0;bit<64;bit++) if(!test(1,1UL<<bit)) {
    puts_uart("BF16_MACHINE_PASS control_bit=");
    char number[4]={(char)('0'+bit/10),(char)('0'+bit%10),'\n',0};
    puts_uart(number);
    return test(0,0)?5:0;
  }
  return 4;
}
