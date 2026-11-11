# a100c emitted program: puzzle1_kernel
# source: tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py
# specialization identity: 55e0b02c5a3302ab
# compiler revision: 92fa8b4b706f0a76
# target model: a100-rvv1-vlen1024/1 (VLEN=1024, file=4096B)
# options: no-guarded-narrow-access
# argument layout: cfa2689d1adec447
# every instruction below traces to a selected MIR op: [opN] carries the source location
# passes: passes=default
    .text
    .globl operator_workspace_private
    .type operator_workspace_private, @function
operator_workspace_private:
    li a0, 0
    ret
    .size operator_workspace_private, .-operator_workspace_private
    .globl operator_workspace_shared
    .type operator_workspace_shared, @function
operator_workspace_shared:
    li a0, 0
    ret
    .size operator_workspace_shared, .-operator_workspace_shared
    .globl operator_entry
    .type operator_entry, @function
operator_entry:  # fn operator_entry
addi sp, sp, -80
sd ra, 0(sp)
sd s1, 8(sp)
sd s2, 16(sp)
sd s3, 24(sp)
sd s4, 32(sp)
sd s5, 40(sp)
sd s6, 48(sp)
mv t0, a0
.Lentry:  # block entry
ld t2, 0(t0)  # [op0] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
ld t1, 0(t2)  # [op1] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
ld t2, 8(t2)  # [op2] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
ld a5, 24(t0)  # [op3] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
lwu a1, 40(t0)  # [op4] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
lwu t0, 44(t0)  # [op5] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
lw s1, 8(t2)  # [op6] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
mv a2, s1  # [op7] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
lwu a6, 24(t2)  # [op8] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
ld a7, 0(t1)  # [op9] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
ld s2, 56(t1)  # [op10] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
li t2, 1024  # [op11] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
li a3, 1  # [op12] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
sub t2, t2, a3  # [op13] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
add t2, a2, t2  # [op14] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
li a2, 1024  # [op15] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
divu t2, t2, a2  # [op16] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
li a2, 1  # [op17] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
mul s3, a2, t2  # [op18] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
mv a1, a1  # [op19] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
mv s4, t0  # [op20] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
li a2, 0  # [op21] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
li t2, 1  # [op22]
ld t0, 104(t1)  # [op23]
ld t1, 48(t1)  # [op24]
sltu a3, t0, t1  # [op25]
sltu t0, t1, t0  # [op26]
or t0, a3, t0  # [op27]
and t0, t2, t0  # [op28]
li t1, 96  # [op29]
mul t0, t0, t1  # [op30]
li t1, 32  # [op31]
add t0, t1, t0  # [op32]
addiw t2, t0, 0  # [op33]
mv t0, a1  # [op34] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
mv t1, a2  # [op34] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
j .Lprog_head  # [op34] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
.Lprog_head:  # block prog_head
slt a1, t0, s3  # [op35] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
bne a1, zero, .Lbrc36_true  # [op36] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
sd t1, 56(sp)  # [op36] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
mv t1, t0  # [op36] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
ld t0, 56(sp)  # [op36] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
j .Lprog_exit  # [op36] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
.Lbrc36_true:  # [op36] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
mv a1, t0  # [op36] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
mv t0, t1  # [op36] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
j .Lprog_body  # [op36] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
.Lprog_body:  # block prog_body
addiw t1, a1, 0  # [op37] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
li a2, 10  # [op38] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:21:19
sllw t1, t1, a2  # [op39] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:21:19
li a2, 0  # [op40] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
sd t0, 56(sp)  # [op41] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
mv t0, a2  # [op41] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
ld a2, 56(sp)  # [op41] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
j .Lchunk1_head  # [op41] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
.Lchunk1_head:  # block chunk1_head
subw a4, s1, t1  # [op42] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
li a3, 1024  # [op43] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
slt s5, a4, a3  # [op44] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
addiw s5, s5, 0  # [op45] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
li s6, 0  # [op46] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
subw s5, s6, s5  # [op47] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
subw a4, a4, a3  # [op48] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
and a4, a4, s5  # [op49] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
addw a3, a3, a4  # [op50] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
slt a3, t0, a3  # [op51] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
bne a3, zero, .Lbrc52_true  # [op52] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
mv t1, a1  # [op52] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
mv t0, a2  # [op52] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
j .Lchunk1_exit  # [op52] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
.Lbrc52_true:  # [op52] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
j .Lchunk1_body  # [op52] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
.Lchunk1_exit:  # block chunk1_exit
mv t1, t0  # [op53] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
mv t0, a1  # [op53] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
j .Lprog_next  # [op53] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
.Lchunk1_body:  # block chunk1_body
vsetvli a3, t2, e32, m4, ta,ma  # [op54] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
vid.v v4  # [op56] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:22:29
vadd.vx v4, v4, t0  # [op57] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:22:29
vmv.v.x v8, t1  # [op58] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:22:15
vadd.vv v4, v8, v4  # [op59] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:22:15
vmv.v.x v8, s1  # [op60] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:23:12
vmslt.vv v1, v4, v8  # [op61] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:23:12
li a3, 0  # [op62] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:24:9
vmv.v.x v4, a3  # [op63] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:24:9
mv a3, t0  # [op64] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:24:9
mv a4, t1  # [op65] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:24:9
add a3, a3, a4  # [op66] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:24:9
li a4, 4  # [op67] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:24:9
mul a3, a3, a4  # [op68] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:24:9
add a3, s2, a3  # [op69] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:24:9
vmv1r.v v0, v1  # [op70] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:24:9
vle32.v v8, 0(a3), v0.t  # [op71] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:24:9
vmv1r.v v0, v1  # [op72] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:24:9
vmerge.vvm v4, v4, v8, v0  # [op73] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:24:9
vmv.v.x v8, a6  # [op74] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:25:36
vfadd.vv v4, v4, v8  # [op75] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:25:36
mv a3, t0  # [op76] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:25:5
mv a4, t1  # [op77] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:25:5
add a3, a3, a4  # [op78] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:25:5
li a4, 4  # [op79] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:25:5
mul a3, a3, a4  # [op80] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:25:5
add a3, a7, a3  # [op81] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:25:5
vmv1r.v v0, v1  # [op82] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:25:5
vse32.v v4, 0(a3), v0.t  # [op83] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:25:5
vcpop.m a3, v1  # [op84] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:25:5
add a2, a2, a3  # [op85] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
addw t0, t0, t2  # [op86] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
j .Lchunk1_head  # [op88] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
.Lprog_next:  # block prog_next
add t0, t0, s4  # [op89] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
j .Lprog_head  # [op90] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
.Lprog_exit:  # block prog_exit
sd t0, 0(a5)  # [op91] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
ld ra, 0(sp)  # [op92] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
ld s1, 8(sp)  # [op92] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
ld s2, 16(sp)  # [op92] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
ld s3, 24(sp)  # [op92] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
ld s4, 32(sp)  # [op92] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
ld s5, 40(sp)  # [op92] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
ld s6, 48(sp)  # [op92] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
addi sp, sp, 80  # [op92] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
ret  # [op92] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
    .size operator_entry, .-operator_entry
    .section .note.GNU-stack,"",@progbits
