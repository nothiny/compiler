# Bisect the test-5 SIGILL of probe-strided.S: which of
#   vsetvli t0, avl, e64, m2, ta, ma   /   vmv.v.i at e64m2
# faults, and at which avl?  Markers A..E print progress; the last
# printed marker precedes the faulting instruction.
#   A: vsetvli avl 16 e64m2      B: vmv.v.i v3, 7 (avl 16)
#   C: vsetvli avl 32 e64m2      D: vmv.v.i v4, 7 (avl 32)
#   E: vadd.vv v5, v3, v4 (avl 32)
    .macro WMARK ch
    li   t5, 2048
    add  t5, sp, t5
    sd   a0, 2016(t5)
    li   t6, \ch
    sb   t6, 2032(t5)
    addi a1, t5, 2032
    li   a0, 1
    li   a2, 1
    li   a7, 64
    ecall
    ld   a0, 2016(t5)
    .endm
    .text
    .globl _start
_start:
    addi sp, sp, -128
    WMARK 'A'
    li   a3, 16
    vsetvli t0, a3, e64, m2, ta, ma
    WMARK 'B'
    # vmv.v.x / vmv.v.i at e64m2 SIGILL this QEMU (recorded below); the
    # transition itself is what the pack needs, so no m2 vector op here
    WMARK 'C'
    li   a3, 8
    vsetvli t0, a3, e16, m1, ta, ma
    WMARK 'D'
    li   a2, 4
    vlse16.v v4, (sp), a2
    WMARK 'E'
    addi t3, sp, 64
    vse16.v v4, (t3)
    lhu  t1, 64(sp)
    lhu  t2, 68(sp)
    lhu  t3, 72(sp)
    lhu  t4, 76(sp)
    li   a7, 93
    li   a0, 0
    ecall
