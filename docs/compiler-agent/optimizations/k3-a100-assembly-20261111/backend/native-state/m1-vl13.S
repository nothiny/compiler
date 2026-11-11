.option norelax
.text
.globl _start
_start:
 li t2, 4240
 sub sp, sp, t2
 la t0, input
 li t2, 128
 vsetvli t3, t2, e8, m1, ta, ma
 vle8.v v8, (t0)
 li t2, 13
 vsetvli t3, t2, e64, m1, ta, ma
 csrr s0, vl
 csrr s1, vtype
 li t0, 1234567
sd t0, 8(sp)  # [op-1]
li t0, 4112  # [op-1]
add t0, t0, sp  # [op-1]
vs1r.v v8, (t0)  # [op-1]
ld t0, 8(sp)  # [op-1]
 li t1, 1234567
 bne t0, t1, fail
 csrr t4, vl
 bne t4, s0, fail
 csrr t4, vtype
 bne t4, s1, fail
 li t2, 128
 vsetvli t3, t2, e8, m1, ta, ma
 vmv.v.i v8, 0
 li t2, 13
 vsetvli t3, t2, e32, m1, ta, ma
 csrr s0, vl
 csrr s1, vtype
sd t0, 8(sp)  # [op-1]
li t0, 4112  # [op-1]
add t0, t0, sp  # [op-1]
vl1re8.v v8, (t0)  # [op-1]
ld t0, 8(sp)  # [op-1]
 li t1, 1234567
 bne t0, t1, fail
 csrr t4, vl
 bne t4, s0, fail
 csrr t4, vtype
 bne t4, s1, fail
 li t2, 128
 vsetvli t3, t2, e8, m1, ta, ma
 la t1, restored
 vse8.v v8, (t1)
 la t0, input
 li t2, 128
check:
 lbu t3, 0(t0)
 lbu t4, 0(t1)
 bne t3, t4, fail
 addi t0, t0, 1
 addi t1, t1, 1
 addi t2, t2, -1
 bnez t2, check
 li a0, 0
 j exit
fail:
 li a0, 1
exit:
 li a7, 93
 ecall
.data
.balign 16
input: .byte 11,48,85,122,159,196,233,14,51,88,125,162,199,236,17,54,91,128,165,202,239,20,57,94,131,168,205,242,23,60,97,134,171,208,245,26,63,100,137,174,211,248,29,66,103,140,177,214,251,32,69,106,143,180,217,254,35,72,109,146,183,220,1,38,75,112,149,186,223,4,41,78,115,152,189,226,7,44,81,118,155,192,229,10,47,84,121,158,195,232,13,50,87,124,161,198,235,16,53,90,127,164,201,238,19,56,93,130,167,204,241,22,59,96,133,170,207,244,25,62,99,136,173,210,247,28,65,102
.bss
.balign 16
restored: .skip 128
