/* Missing x86 compiler-rt helper support for the pinned reference backend.
 * Convert IEEE binary64 directly to BF16 with round-to-nearest, ties-to-even.
 * Do not route through binary32: that would introduce double rounding.
 */
#include <stdint.h>
uint16_t a100_reference_f64_bits_to_bf16(uint64_t bits) {
  uint16_t sign=(uint16_t)((bits>>48)&0x8000);
  uint64_t fraction=bits&0xfffffffffffffULL;
  unsigned exponent=(unsigned)((bits>>52)&0x7ff);
  if(exponent==0x7ff)
    return sign|0x7f80|(fraction?(uint16_t)((fraction>>45)|0x40):0);
  if(!exponent) return sign; /* binary64 subnormals are below BF16 half-ulp */
  int e=(int)exponent-1023;
  if(e>127) return sign|0x7f80;
  if(e < -134) return sign;
  uint64_t significand=(1ULL<<52)|fraction;
  unsigned shift=e>=-126?45:(unsigned)(-81-e);
  uint64_t value=significand>>shift;
  uint64_t remainder=significand&((1ULL<<shift)-1);
  uint64_t half=1ULL<<(shift-1);
  value+=(remainder>half || (remainder==half && (value&1)));
  if(e < -126) return sign|(uint16_t)value;
  /* Subtract the implicit leading 1; a rounded carry increments exponent. */
  return sign|(uint16_t)(((e+127)<<7)+(value-128));
}
