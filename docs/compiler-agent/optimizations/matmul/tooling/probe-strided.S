# Strided-form probe for the matmul round: does the pinned QEMU execute
# vlse/vsse (RVV 1.0 strided vector memory) correctly at the shapes the
# B-operand pack needs?  The recorded emulator defect covers only INDEXED
# forms (e64 index + sub-32-bit data SEGFAULT, vectorize.py:2579); strided
# forms were never probed.
#
# Shapes probed (VLEN=1024, -cpu max):
#   1. vlse16.v stride 128B, vl 8   -- the pack's exact gather shape
#   2. vlse16.v stride 2B,  vl 32   -- near-unit stride
#   3. vlse8.v  stride 3B,  vl 5    -- odd byte stride, 8-bit data
#   4. vsse16.v stride 128B, vl 8   -- the strided store side
#   5. e64m2 region first, then e16m1 + vlse -- the region-transition
#      shape adjacent to the recorded indexed-form crash
#   6. avl 0: vlse/vse must be a no-op and must not fault
# exit code 0 = every lane matched its expected pattern; 1 = mismatch
# (a0 = the failing test's ordinal is NOT tracked -- stderr-free program;
#  a mismatch narrows by re-running with tests commented out if ever hit).
    .macro WMARK ch
    li   t5, 2048
    add  t5, sp, t5
    sd   a0, 2016(t5)
    sd   a1, 2024(t5)
    li   t6, \ch
    sb   t6, 2032(t5)
    addi a1, t5, 2032
    li   a0, 1
    li   a2, 1
    li   a7, 64
    ecall
    ld   a0, 2016(t5)
    ld   a1, 2024(t5)
    .endm

    .text
    .globl _start
_start:
    li   t6, 4096
    sub  sp, sp, t6
    addi a0, sp, 0        # buf16: 512 x i16, filled buf16[i] = i
    addi a4, sp, 1024     # buf8:  512 x i8,  filled buf8[i]  = i
    addi a1, sp, 1536     # out16: 512 x i16 scratch
    addi a6, a1, 1024     # out2:  512 x i16 scratch (test 4)

    li   t0, 0
fill16:
    slli t1, t0, 1
    add  t2, a0, t1
    sh   t0, 0(t2)
    addi t0, t0, 1
    li   t3, 512
    blt  t0, t3, fill16
    li   t0, 0
fill8:
    add  t2, a4, t0
    sb   t0, 0(t2)
    addi t0, t0, 1
    li   t3, 512
    blt  t0, t3, fill8

    WMARK '1'
    # --- test 1: vlse16 stride 128B, vl 8 -> lane l holds buf16[64*l]
    li   a2, 128
    li   a3, 8
    vsetvli t0, a3, e16, m1, ta, ma
    vlse16.v v1, (a0), a2
    vse16.v  v1, (a1)
    li   t0, 0
t1cmp:
    slli t1, t0, 1
    add  t2, a1, t1
    lhu  t3, 0(t2)
    slli t4, t0, 6
    bne  t3, t4, fail
    addi t0, t0, 1
    li   t5, 8
    blt  t0, t5, t1cmp

    WMARK '2'
    # --- test 2: vlse16 stride 2B, vl 32 -> lane l holds buf16[l]
    li   a2, 2
    li   a3, 32
    vsetvli t0, a3, e16, m1, ta, ma
    vlse16.v v1, (a0), a2
    vse16.v  v1, (a1)
    li   t0, 0
t2cmp:
    slli t1, t0, 1
    add  t2, a1, t1
    lhu  t3, 0(t2)
    bne  t3, t0, fail
    addi t0, t0, 1
    li   t5, 32
    blt  t0, t5, t2cmp

    WMARK '3'
    # --- test 3: vlse8 stride 3B, vl 5 -> lane l holds buf8[3*l]
    li   a2, 3
    li   a3, 5
    vsetvli t0, a3, e8, m1, ta, ma
    vlse8.v v2, (a4), a2
    vse8.v  v2, (a1)
    li   t0, 0
t3cmp:
    add  t2, a1, t0
    lbu  t3, 0(t2)
    slli t4, t0, 1
    add  t4, t4, t0
    bne  t3, t4, fail
    addi t0, t0, 1
    li   t5, 5
    blt  t0, t5, t3cmp

    WMARK '4'
    # --- test 4: vsse16 stride 128B, vl 8 -> out2[64*l] = 64*l, rest zero
    li   t0, 0
z4:
    slli t1, t0, 1
    add  t2, a6, t1
    sh   x0, 0(t2)
    addi t0, t0, 1
    li   t3, 512
    blt  t0, t3, z4
    li   a2, 128
    li   a3, 8
    vsetvli t0, a3, e16, m1, ta, ma
    vlse16.v v1, (a0), a2
    vsse16.v v1, (a6), a2
    li   t0, 0
t4cmp:
    slli t1, t0, 6
    slli t2, t1, 1
    add  t2, a6, t2
    lhu  t3, 0(t2)
    slli t4, t0, 6
    bne  t3, t4, fail
    addi t0, t0, 1
    li   t5, 8
    blt  t0, t5, t4cmp
    lhu  t3, 2(a6)
    bne  t3, x0, fail

    WMARK '5'
    # --- test 5: e64m2 region first, then e16m1 + vlse (transition shape)
    # NO vector op at e64m2: probe-e64m2.S shows vmv.v.i AND vmv.v.x at
    # e64/m2 SIGILL this QEMU (avl 16 and 32) -- a newly recorded emulator
    # constraint -- while the pure region transition plus vlse executes
    # correctly, which is the shape the pack actually needs.
    li   a3, 16
    vsetvli t0, a3, e64, m2, ta, ma
    li   a3, 8
    vsetvli t0, a3, e16, m1, ta, ma
    li   a2, 128
    vlse16.v v4, (a0), a2
    vse16.v  v4, (a1)
    li   t0, 0
t5cmp:
    slli t1, t0, 1
    add  t2, a1, t1
    lhu  t3, 0(t2)
    slli t4, t0, 6
    bne  t3, t4, fail
    addi t0, t0, 1
    li   t5, 8
    blt  t0, t5, t5cmp

    WMARK '6'
    # --- test 6: avl 0 -> vlse/vse are no-ops and do not fault
    li   a3, 0
    vsetvli t0, a3, e16, m1, ta, ma
    vlse16.v v5, (a0), a2
    sh   x0, 0(a1)
    vse16.v  v5, (a1)
    lhu  t3, 0(a1)
    bne  t3, x0, fail

    li   a7, 93
    li   a0, 0
    ecall
fail:
    li   a7, 93
    li   a0, 1
    ecall
