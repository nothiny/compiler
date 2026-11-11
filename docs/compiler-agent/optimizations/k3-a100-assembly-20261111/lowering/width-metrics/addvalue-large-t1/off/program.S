# a100c emitted program: puzzle1_kernel
# source: tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py
# specialization identity: 55e0b02c5a3302ab
# compiler revision: 92fa8b4b706f0a76
# target model: a100-rvv1-vlen1024/1 (VLEN=1024, file=4096B)
# options: no-guarded-narrow-access,no-elementwise-width
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
    # [peephole] removed 0 redundant vsetvli, 1 redundant li
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
ld t1, 0(t0)  # [op0] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
ld s1, 0(t1)  # [op1] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
ld t1, 8(t1)  # [op2] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
ld a5, 24(t0)  # [op3] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
lwu a1, 40(t0)  # [op4] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
lwu t0, 44(t0)  # [op5] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
lw t2, 8(t1)  # [op6] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
mv a2, t2  # [op7] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
lwu a6, 24(t1)  # [op8] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
ld a7, 0(s1)  # [op9] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
ld s2, 56(s1)  # [op10] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
li t1, 1024  # [op11] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
li s1, 1  # [op12] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
sub t1, t1, s1  # [op13] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
add t1, a2, t1  # [op14] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
li s1, 1024  # [op15] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
divu a3, t1, s1  # [op16] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
li t1, 1  # [op17] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
mul s3, t1, a3  # [op18] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
mv t1, a1  # [op19] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
mv s4, t0  # [op20] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
li t0, 0  # [op21] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
sd t0, 56(sp)  # [op22] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
mv t0, t1  # [op22] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
ld t1, 56(sp)  # [op22] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
j .Lprog_head  # [op22] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
.Lprog_head:  # block prog_head
slt s1, t0, s3  # [op23] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
bne s1, zero, .Lbrc24_true  # [op24] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
sd t1, 56(sp)  # [op24] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
mv t1, t0  # [op24] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
ld t0, 56(sp)  # [op24] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
j .Lprog_exit  # [op24] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
.Lbrc24_true:  # [op24] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
mv s1, t0  # [op24] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
mv t0, t1  # [op24] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
j .Lprog_body  # [op24] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
.Lprog_body:  # block prog_body
addiw t1, s1, 0  # [op25] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
addiw a1, a3, 0  # [op26] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
li a1, 10  # [op27] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:21:19
sllw t1, t1, a1  # [op28] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:21:19
li a1, 0  # [op29] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
sd t0, 56(sp)  # [op30] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
mv t0, a1  # [op30] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
ld a1, 56(sp)  # [op30] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
j .Lchunk1_head  # [op30] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
.Lchunk1_head:  # block chunk1_head
subw a4, t2, t1  # [op31] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
li a2, 1024  # [op32] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
slt s5, a4, a2  # [op33] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
addiw s5, s5, 0  # [op34] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
li s6, 0  # [op35] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
subw s5, s6, s5  # [op36] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
subw a4, a4, a2  # [op37] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
and a4, a4, s5  # [op38] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
addw a2, a2, a4  # [op39] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
slt a2, t0, a2  # [op40] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
bne a2, zero, .Lbrc41_true  # [op41] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
mv t1, s1  # [op41] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
mv t0, a1  # [op41] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
j .Lchunk1_exit  # [op41] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
.Lbrc41_true:  # [op41] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
j .Lchunk1_body  # [op41] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
.Lchunk1_exit:  # block chunk1_exit
mv t1, t0  # [op42] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
mv t0, s1  # [op42] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
j .Lprog_next  # [op42] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
.Lchunk1_body:  # block chunk1_body
li a2, 32  # [op43] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
vsetvli a2, a2, e32, m1, ta,ma  # [op44] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
li a2, 32  # [op45] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:22:29
vid.v v1  # [op47] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:22:29
vadd.vx v1, v1, t0  # [op48] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:22:29
vmv.v.x v2, t1  # [op49] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:22:15
vadd.vv v1, v2, v1  # [op50] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:22:15
vmv.v.x v2, t2  # [op51] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:23:12
vmslt.vv v1, v1, v2  # [op52] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:23:12
li a2, 0  # [op53] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:24:9
vmv.v.x v2, a2  # [op54] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:24:9
mv a2, t0  # [op55] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:24:9
mv a4, t1  # [op56] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:24:9
add a2, a2, a4  # [op57] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:24:9
li a4, 4  # [op58] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:24:9
mul a2, a2, a4  # [op59] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:24:9
add a2, s2, a2  # [op60] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:24:9
vmv1r.v v0, v1  # [op61] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:24:9
vle32.v v3, 0(a2), v0.t  # [op62] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:24:9
vmv1r.v v0, v1  # [op63] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:24:9
vmerge.vvm v2, v2, v3, v0  # [op64] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:24:9
vmv.v.x v3, a6  # [op65] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:25:36
vfadd.vv v2, v2, v3  # [op66] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:25:36
mv a2, t0  # [op67] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:25:5
mv a4, t1  # [op68] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:25:5
add a2, a2, a4  # [op69] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:25:5
li a4, 4  # [op70] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:25:5
mul a2, a2, a4  # [op71] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:25:5
add a2, a7, a2  # [op72] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:25:5
vmv1r.v v0, v1  # [op73] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:25:5
vse32.v v2, 0(a2), v0.t  # [op74] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:25:5
vcpop.m a2, v1  # [op75] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:25:5
add a1, a1, a2  # [op76] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
li a2, 32  # [op77] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
addw t0, t0, a2  # [op78] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
    # [peephole-li] [op79] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
j .Lchunk1_head  # [op81] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
.Lprog_next:  # block prog_next
add t0, t0, s4  # [op82] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
j .Lprog_head  # [op83] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
.Lprog_exit:  # block prog_exit
sd t0, 0(a5)  # [op84] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
ld ra, 0(sp)  # [op85] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
ld s1, 8(sp)  # [op85] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
ld s2, 16(sp)  # [op85] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
ld s3, 24(sp)  # [op85] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
ld s4, 32(sp)  # [op85] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
ld s5, 40(sp)  # [op85] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
ld s6, 48(sp)  # [op85] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
addi sp, sp, 80  # [op85] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
ret  # [op85] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/add_value.py:19:1
    .size operator_entry, .-operator_entry
    .section .note.GNU-stack,"",@progbits
