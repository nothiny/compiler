.option norelax
.text
.globl _start
_start:
li t0, 16
vsetvli t1, t0, e64, m1, ta,ma
li t2, 77
vsetvli t2, t0, e64, m1, ta,ma
bne t2, t0, fail
li t1, 99
vsetvli t1, t0, e64, m1, ta,ma
bne t1, t0, fail
 li a0, 0
 j exit
fail:
 li a0, 1
exit:
 li a7, 93
 ecall
