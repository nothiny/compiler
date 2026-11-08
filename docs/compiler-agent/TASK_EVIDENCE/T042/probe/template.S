    .text
    .globl _start
_start:
    li   t0, 32
    vsetvli t0, t0, e64, m2, ta, ma
    li   t1, 1
    vmv.v.x v2, t1
    li   t1, 2
    vmv.v.x v4, t1
LMUL1_BLOCK
COMPARE
    li   a0, 42
    li   a7, 93
    ecall
