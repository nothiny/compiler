# Loop validation program: trip count 1000, body of 8 instructions
# (3 scalar-arith, 1 scalar-load, 1 scalar-store, 1 vec-config,
# 1 vec-arith, 1 branch), prologue of 4, epilogue of 2.  Expected dynamic
# counts are hand-computed in tools/profiling/validate_counts.py.
# Compressed encodings the assembler may choose keep the same category
# bucket and per-pc counts, so the assertions are encoding-agnostic.
    .text
    .globl _start
_start:
    addi a7, x0, 93          # prologue scalar-arith
    addi a6, x0, 1000        # prologue scalar-arith (trip count)
    addi a5, x0, 0           # prologue scalar-arith
    addi sp, sp, -64         # prologue scalar-arith
1:  addi a5, a5, 1           # body scalar-arith
    ld   a0, 32(sp)          # body scalar-load
    sd   a0, 40(sp)          # body scalar-store
    add  a0, a0, a5          # body scalar-arith
    vsetvli t0, x0, e32, m1  # body vec-config
    vmv.v.i v1, 1            # body vec-arith
    addi a6, a6, -1          # body scalar-arith
    bnez a6, 1b              # body branch (999 taken, 1 not taken)
    addi a0, x0, 0           # epilogue scalar-arith (exit code 0)
    ecall                    # epilogue system
