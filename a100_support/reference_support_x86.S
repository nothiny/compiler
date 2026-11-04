/* SysV x86 BF16 return ABI uses the low 16 bits of xmm0. The C helper takes
 * the double's integer representation so every rounding step is explicit.
 */
.text
.globl __truncdfbf2
.type __truncdfbf2,@function
__truncdfbf2:
  subq $8, %rsp
  movq %xmm0, %rdi
  call a100_reference_f64_bits_to_bf16@PLT
  movd %eax, %xmm0
  addq $8, %rsp
  ret
.size __truncdfbf2,.-__truncdfbf2
.section .note.GNU-stack,"",@progbits
