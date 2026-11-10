# Straight-line validation program: every instruction executes exactly
# once; expected per-category dynamic counts are hand-computed in
# tools/profiling/validate_counts.py.  Freestanding, static, exits via
# sys_exit with code 0 (same shape as a100_support/probes/smoke_asm.S).
    .text
    .globl _start
_start:
    addi a7, x0, 93          #  1 scalar-arith  sys_exit nr
    addi a6, x0, 1           #  2 scalar-arith
    addi sp, sp, -64         #  3 scalar-arith
    ld   a0, 32(sp)          #  4 scalar-load   (uninitialized, address valid)
    sd   a0, 40(sp)          #  5 scalar-store
    add  a0, a0, a6          #  6 scalar-arith
    vsetvli t0, x0, e32, m1  #  7 vec-config    vl = VLEN/32 = 32
    vmv.v.i v1, 1            #  8 vec-arith
    beq  a6, x0, 1f          #  9 branch        NOT taken (a6 == 1)
    addi a0, a0, 55          # 10 scalar-arith  (fall-through)
1:  addi a0, x0, 0           # 11 scalar-arith  exit code 0
    ecall                    # 12 system        exit(0)
