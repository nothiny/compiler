# Vendor-decode validation program: exercises the smt.vmadot (i8) encoding
# through the plugin's encoding-based decode path (the stock disassembler
# does not spell it).  The instruction sequence mirrors the known-good
# probe form in a100_support/probes/vector_matrix.S (e32/m2 accumulator
# zero-init, e8/m1 operands, vd even for MUL_C=2); a first attempt using
# the bare word 0xe200302b faulted (SIGILL, recorded in TOOLING.md).
# Vector memory operands take a bare base register (no immediate offset),
# so the two operand addresses are materialized in a1/a2.
    .text
    .globl _start
_start:
    addi a7, x0, 93                    #  1 scalar-arith  sys_exit nr
    addi a0, x0, 0                     #  2 scalar-arith  exit code 0
    addi sp, sp, -64                   #  3 scalar-arith
    addi a1, sp, 8                     #  4 scalar-arith  operand B address
    addi a2, sp, 16                    #  5 scalar-arith  accumulator address
    vsetvli t0, x0, e32, m2, ta, ma    #  6 vec-config
    vmv.v.i v16, 0                     #  7 vec-arith    (zero the accumulator)
    vsetvli t0, x0, e8, m1, ta, ma     #  8 vec-config
    vle8.v v2, (sp)                    #  9 vec-mem      (garbage operand A)
    vle8.v v8, (a1)                    # 10 vec-mem      (garbage operand B)
    smt.vmadot v16, v2, v8, i8         # 11 ime
    vsetvli t0, x0, e32, m2, ta, ma    # 12 vec-config
    vse32.v v16, (a2)                  # 13 vec-mem      (store accumulator)
    ecall                              # 14 system       exit(0)
