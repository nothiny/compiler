.section .text.start,"ax",@progbits
.globl _start
_start:
  la sp, stack_end
  la t0, trap
  csrw mtvec, t0
  li t0, 0x6600
  csrs mstatus, t0
  call bare_main
  beqz a0, 1f
  slli a0, a0, 16
  li t0, 0x3333
  or a0, a0, t0
  j 2f
1:
  li a0, 0x5555
2:
  li t0, 0x100000
  sw a0, 0(t0)
3:
  wfi
  j 3b
trap:
  li t0, 0x100000
  li t1, 0x000c3333
  sw t1, 0(t0)
  j 3b
.section .bss
.balign 16
stack:
  .space 16384
stack_end:
