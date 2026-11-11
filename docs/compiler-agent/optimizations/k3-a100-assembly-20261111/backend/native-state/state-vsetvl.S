.option norelax
.text
.globl _start
_start:
    # [peephole] removed 0 redundant vsetvli, 1 redundant li
li t0, 16
vsetvli t1, t0, e64, m1, ta,ma
li t2, 217
vsetvl t1, t0, t2
vsetvli t1, t0, e64, m1, ta,ma
csrr t2, vtype
li t3, 216
bne t2, t3, fail
 li a0, 0
 j exit
fail:
 li a0, 1
exit:
 li a7, 93
 ecall
