/* Environment probes, not compiler-generated code. Matrix semantics are from
 * the archived SpacemiT matrix extension v0.6 chapters 5.1 and 6.1.
 */
.text
.globl probe_vlenb
.type probe_vlenb,@function
probe_vlenb:
  csrr a0, vlenb
  ret

.globl probe_rvv_add
.type probe_rvv_add,@function
probe_rvv_add:
  beqz a3, 2f
1:
  vsetvli t0, a3, e32, m1, ta, ma
  vle32.v v2, (a1)
  vle32.v v4, (a2)
  vadd.vv v6, v2, v4
  vse32.v v6, (a0)
  slli t1, t0, 2
  add a0, a0, t1
  add a1, a1, t1
  add a2, a2, t1
  sub a3, a3, t0
  bnez a3, 1b
2:
  ret

.macro matrix_integer name, fmt
.globl \name
.type \name,@function
\name:
  vsetvli t0, zero, e32, m2, ta, ma
  vmv.v.i v16, 0
  vsetvli t0, zero, e8, m1, ta, ma
  vle8.v v2, (a0)
  vle8.v v8, (a1)
  smt.vmadot v16, v2, v8, \fmt
  vsetvli t0, zero, e32, m2, ta, ma
  vse32.v v16, (a2)
  ret
.endm
matrix_integer probe_ime_i8, i8
matrix_integer probe_ime_i4, i4

.globl probe_read_mcpm
.type probe_read_mcpm,@function
probe_read_mcpm:
  csrr a0, mcpm
  ret

.globl probe_ime_float
.type probe_ime_float,@function
probe_ime_float:
  vsetvli t0, zero, e32, m2, ta, ma
  vmv.v.i v16, 0
  vsetvli t0, zero, e16, m1, ta, ma
  vle16.v v2, (a0)
  vle16.v v8, (a1)
  smt.vfwmadot v16, v2, v8
  vsetvli t0, zero, e32, m2, ta, ma
  vse32.v v16, (a2)
  ret
.section .note.GNU-stack,"",@progbits
