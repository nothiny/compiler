# a100c emitted program: matmul_kernel
# source: tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py
# specialization identity: 0902dd4daab0c2ff
# compiler revision: b5c42fbb75a242a8
# target model: a100-rvv1-vlen1024/1 (VLEN=1024, file=4096B)
# options: default
# argument layout: 52c2f99857bd772f
# every instruction below traces to a selected MIR op: [opN] carries the source location
# passes: passes=default
    .text
    .globl operator_workspace_private
    .type operator_workspace_private, @function
operator_workspace_private:
    li a0, 37576
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
    # [peephole] removed 0 redundant vsetvli, 165 redundant li
operator_entry:  # fn operator_entry
addi sp, sp, -160
sd ra, 0(sp)
sd s1, 8(sp)
sd s2, 16(sp)
sd s3, 24(sp)
sd s4, 32(sp)
sd s5, 40(sp)
sd s6, 48(sp)
sd s7, 56(sp)
sd s8, 64(sp)
sd s9, 72(sp)
sd s10, 80(sp)
sd s11, 88(sp)
mv t0, a0
.Lentry:  # block entry
sd t0, 112(sp)  # [op-1]
ld t0, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 0(t0)  # [op0] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t0, 0(t1)  # [op1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 8(t1)  # [op2] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t2, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld a6, 24(t2)  # [op3] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t2, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
lwu s1, 40(t2)  # [op4] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t2, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
lwu a1, 44(t2)  # [op5] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t2, 8(t1)  # [op6] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addiw t2, t2, 0  # [op7] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t2, 136(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t2, 24(t1)  # [op8] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addiw a7, t2, 0  # [op9] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 40(t1)  # [op10] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addiw a2, t1, 0  # [op11] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s2, 0(t0)  # [op12] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s3, 56(t0)  # [op13] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s4, 112(t0)  # [op14] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li t0, 15  # [op15] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t0, t2, t0  # [op16] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li t2, 16  # [op17] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
divu t0, t0, t2  # [op18] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t0, 120(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li t0, 15  # [op19] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t0, t1, t0  # [op20] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li t1, 16  # [op21] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
divu t0, t0, t1  # [op22] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t0, 128(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li t0, 1  # [op23] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 120(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mul t0, t0, t1  # [op24] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 128(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mul s5, t0, t1  # [op25] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, s1  # [op26] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv s6, a1  # [op27] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li t1, 0  # [op28] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lprog_head  # [op29] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lprog_head:  # block prog_head
slt t2, t0, s5  # [op30] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne t2, zero, .Lbrc31_true  # [op31] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t1, 96(sp)  # [op31] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t0  # [op31] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t0, 96(sp)  # [op31] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lprog_exit  # [op31] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc31_true:  # [op31] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t2, t0  # [op31] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv a1, t1  # [op31] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lprog_body  # [op31] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lprog_body:  # block prog_body
li t0, 1  # [op32] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 120(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
divu t1, t2, t1  # [op33] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s1, 120(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mul t1, t1, s1  # [op34] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sub s1, t2, t1  # [op35] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 120(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mul t0, t0, t1  # [op36] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
divu t1, t2, t0  # [op37] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld a3, 128(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
divu a3, t1, a3  # [op38] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld a4, 128(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mul a3, a3, a4  # [op39] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sub t1, t1, a3  # [op40] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld a3, 128(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mul t0, t0, a3  # [op41] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addiw t0, s1, 0  # [op42] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addiw a3, t1, 0  # [op43] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 120(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addiw t1, t1, 0  # [op44] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 128(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addiw t1, t1, 0  # [op45] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 8(t1)  # [op47] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 4  # [op48] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:14
sllw a4, t0, s1  # [op49] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:14
li t0, 0  # [op50] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, a1  # [op51] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk1_head  # [op51] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk1_head:  # block chunk1_head
li a1, 16  # [op52] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt a1, t0, a1  # [op53] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne a1, zero, .Lbrc54_true  # [op54] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op54] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op54] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk1_exit  # [op54] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc54_true:  # [op54] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk1_body  # [op54] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk1_exit:  # block chunk1_exit
li t1, 0  # [op55] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op56] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op56] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op56] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk2_head  # [op56] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk1_body:  # block chunk1_body
li a1, 16  # [op57] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli a1, a1, e32, m1, ta,ma  # [op58] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li a1, 16  # [op59] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:27
vid.v v1  # [op61] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:27
vadd.vx v1, v1, t0  # [op62] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:27
vmv.v.x v2, a4  # [op63] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:14
vadd.vv v2, v2, v1  # [op64] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:14
vid.v v3  # [op65] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:14
vadd.vx v3, v3, t0  # [op66] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:14
    # [peephole-li] [op67] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:14
vwadd.vx v4, v3, x0  # [op69] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:14
    # [peephole-li] [op70] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:14
vsetvli a1, a1, e64, m2, ta,ma  # [op71] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:14
li a1, 4  # [op72] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:14
vmul.vx v4, v4, a1  # [op73] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:14
li a1, 0  # [op74] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:14
ld a5, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:14
ld a5, 16(a5)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:14
add a1, a5, a1  # [op75] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:14
li a5, 16  # [op76] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:14
vsetvli a5, a5, e32, m1, ta,ma  # [op77] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:14
vsuxei64.v v2, (a1), v4  # [op78] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:14
li a1, 16  # [op79] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:14
sllw a1, a3, s1  # [op81] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:26:14
vmv.v.x v2, a1  # [op82] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:26:14
vadd.vv v1, v2, v1  # [op83] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:26:14
vid.v v2  # [op84] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:26:14
vadd.vx v2, v2, t0  # [op85] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:26:14
li a1, 16  # [op86] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:26:14
vwadd.vx v4, v2, x0  # [op88] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:26:14
    # [peephole-li] [op89] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:26:14
vsetvli a1, a1, e64, m2, ta,ma  # [op90] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:26:14
li a1, 4  # [op91] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:26:14
vmul.vx v2, v4, a1  # [op92] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:26:14
li a1, 64  # [op93] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:26:14
ld a5, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:26:14
ld a5, 16(a5)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:26:14
add a1, a5, a1  # [op94] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:26:14
li a5, 16  # [op95] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:26:14
vsetvli a5, a5, e32, m1, ta,ma  # [op96] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:26:14
vsuxei64.v v1, (a1), v2  # [op97] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:26:14
li a1, 16  # [op98] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:26:14
    # [peephole-li] [op100] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t1, t1, a1  # [op101] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op102] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t0, t0, a1  # [op103] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op104] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk1_head  # [op106] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk2_head:  # block chunk2_head
li s1, 32  # [op107] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op108] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc109_true  # [op109] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op109] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op109] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk2_exit  # [op109] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc109_true:  # [op109] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk2_body  # [op109] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk2_exit:  # block chunk2_exit
li t1, 0  # [op110] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op111] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op111] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op111] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk3_head  # [op111] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk2_body:  # block chunk2_body
li s1, 32  # [op112] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op113] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op114] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:27:14
vid.v v1  # [op116] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:27:14
vadd.vx v1, v1, t0  # [op117] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:27:14
vid.v v2  # [op118] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:27:14
vadd.vx v2, v2, t0  # [op119] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:27:14
    # [peephole-li] [op120] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:27:14
vwadd.vx v4, v2, x0  # [op122] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:27:14
    # [peephole-li] [op123] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:27:14
vsetvli s1, s1, e64, m2, ta,ma  # [op124] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:27:14
li s1, 4  # [op125] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:27:14
vmul.vx v2, v4, s1  # [op126] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:27:14
li s1, 128  # [op127] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:27:14
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:27:14
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:27:14
add s1, a1, s1  # [op128] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:27:14
li a1, 32  # [op129] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:27:14
vsetvli a1, a1, e32, m1, ta,ma  # [op130] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:27:14
vsuxei64.v v1, (s1), v2  # [op131] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:27:14
li s1, 32  # [op132] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:27:14
    # [peephole-li] [op134] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op135] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op136] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op137] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op138] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk2_head  # [op140] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk3_head:  # block chunk3_head
li s1, 256  # [op141] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op142] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc143_true  # [op143] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op143] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op143] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk3_exit  # [op143] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc143_true:  # [op143] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk3_body  # [op143] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk3_exit:  # block chunk3_exit
li t1, 0  # [op144] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op145] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op145] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op145] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk4_head  # [op145] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk3_body:  # block chunk3_body
li s1, 32  # [op146] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op147] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 0  # [op148] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:28:11
li a1, 32  # [op149] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:28:11
vmv.v.x v1, s1  # [op151] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:28:11
vid.v v2  # [op152] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:28:11
vadd.vx v2, v2, t0  # [op153] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:28:11
li s1, 32  # [op154] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:28:11
vwadd.vx v4, v2, x0  # [op156] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:28:11
    # [peephole-li] [op157] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:28:11
vsetvli s1, s1, e64, m2, ta,ma  # [op158] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:28:11
li s1, 4  # [op159] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:28:11
vmul.vx v2, v4, s1  # [op160] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:28:11
li s1, 256  # [op161] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:28:11
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:28:11
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:28:11
add s1, a1, s1  # [op162] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:28:11
li a1, 32  # [op163] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:28:11
vsetvli a1, a1, e32, m1, ta,ma  # [op164] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:28:11
vsuxei64.v v1, (s1), v2  # [op165] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:28:11
li s1, 32  # [op166] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:28:11
li s1, 0  # [op168] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
li s1, 32  # [op169] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
    # [peephole-li] [op170] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op171] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op172] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op173] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op174] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk3_head  # [op176] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk4_head:  # block chunk4_head
li s1, 16  # [op177] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op178] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc179_true  # [op179] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op179] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op179] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk4_exit  # [op179] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc179_true:  # [op179] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk4_body  # [op179] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk4_exit:  # block chunk4_exit
li t1, 0  # [op180] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op181] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op181] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op181] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk5_head  # [op181] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk4_body:  # block chunk4_body
li s1, 16  # [op182] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op183] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 16  # [op184] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
ld s1, 136(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vmv.v.x v1, s1  # [op186] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vid.v v2  # [op187] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vadd.vx v2, v2, t0  # [op188] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
li s1, 16  # [op189] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vwadd.vx v4, v2, x0  # [op191] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
    # [peephole-li] [op192] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vsetvli s1, s1, e64, m2, ta,ma  # [op193] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
li s1, 4  # [op194] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vmul.vx v2, v4, s1  # [op195] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
li s1, 1600  # [op196] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
add s1, a1, s1  # [op197] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
li a1, 16  # [op198] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vsetvli a1, a1, e32, m1, ta,ma  # [op199] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vsuxei64.v v1, (s1), v2  # [op200] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
li s1, 16  # [op201] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vmv.v.x v1, a7  # [op203] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
vid.v v2  # [op204] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
vadd.vx v2, v2, t0  # [op205] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
    # [peephole-li] [op206] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
vwadd.vx v4, v2, x0  # [op208] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
    # [peephole-li] [op209] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
vsetvli s1, s1, e64, m2, ta,ma  # [op210] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
li s1, 4  # [op211] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
vmul.vx v2, v4, s1  # [op212] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
li s1, 6080  # [op213] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
add s1, a1, s1  # [op214] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
li a1, 16  # [op215] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
vsetvli a1, a1, e32, m1, ta,ma  # [op216] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
vsuxei64.v v1, (s1), v2  # [op217] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
li s1, 16  # [op218] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
    # [peephole-li] [op220] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op221] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op222] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op223] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op224] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk4_head  # [op226] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk5_head:  # block chunk5_head
li s1, 32  # [op227] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op228] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc229_true  # [op229] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op229] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op229] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk5_exit  # [op229] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc229_true:  # [op229] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk5_body  # [op229] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk5_exit:  # block chunk5_exit
li t1, 0  # [op230] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op231] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op231] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op231] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk6_head  # [op231] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk5_body:  # block chunk5_body
li s1, 32  # [op232] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op233] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op234] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
ld s1, 136(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vmv.v.x v1, s1  # [op236] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vid.v v2  # [op237] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vadd.vx v2, v2, t0  # [op238] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li s1, 32  # [op239] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vwadd.vx v4, v2, x0  # [op241] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
    # [peephole-li] [op242] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vsetvli s1, s1, e64, m2, ta,ma  # [op243] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li s1, 4  # [op244] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vmul.vx v2, v4, s1  # [op245] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li s1, 6208  # [op246] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
add s1, a1, s1  # [op247] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li a1, 32  # [op248] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vsetvli a1, a1, e32, m1, ta,ma  # [op249] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vsuxei64.v v1, (s1), v2  # [op250] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li s1, 32  # [op251] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li s1, 0  # [op253] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.x v1, a2  # [op254] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vid.v v2  # [op255] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vadd.vx v2, v2, t0  # [op256] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li s1, 32  # [op257] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vwadd.vx v4, v2, x0  # [op259] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
    # [peephole-li] [op260] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vsetvli s1, s1, e64, m2, ta,ma  # [op261] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li s1, 4  # [op262] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vmul.vx v2, v4, s1  # [op263] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li s1, 16832  # [op264] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
add s1, a1, s1  # [op265] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li a1, 32  # [op266] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vsetvli a1, a1, e32, m1, ta,ma  # [op267] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vsuxei64.v v1, (s1), v2  # [op268] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li s1, 32  # [op269] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
    # [peephole-li] [op271] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op272] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op273] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op274] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op275] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk5_head  # [op277] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk6_head:  # block chunk6_head
li s1, 16  # [op278] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op279] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc280_true  # [op280] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op280] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op280] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk6_exit  # [op280] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc280_true:  # [op280] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk6_body  # [op280] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk6_exit:  # block chunk6_exit
li t1, 0  # [op281] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op282] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op282] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op282] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk7_head  # [op282] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk6_body:  # block chunk6_body
li s1, 16  # [op283] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op284] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 16  # [op285] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op286] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op287] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op288] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op289] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk6_head  # [op291] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk7_head:  # block chunk7_head
li s1, 32  # [op292] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op293] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc294_true  # [op294] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op294] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op294] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk7_exit  # [op294] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc294_true:  # [op294] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk7_body  # [op294] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk7_exit:  # block chunk7_exit
li t1, 0  # [op295] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op296] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op296] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op296] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk8_head  # [op296] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk7_body:  # block chunk7_body
li s1, 32  # [op297] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op298] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op299] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
ld s1, 136(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vmv.v.x v1, s1  # [op301] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vid.v v2  # [op302] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vadd.vx v2, v2, t0  # [op303] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li s1, 32  # [op304] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vwadd.vx v4, v2, x0  # [op306] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
    # [peephole-li] [op307] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vsetvli s1, s1, e64, m2, ta,ma  # [op308] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li s1, 4  # [op309] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vmul.vx v2, v4, s1  # [op310] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li s1, 21504  # [op311] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
add s1, a1, s1  # [op312] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li a1, 32  # [op313] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vsetvli a1, a1, e32, m1, ta,ma  # [op314] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vsuxei64.v v1, (s1), v2  # [op315] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li s1, 32  # [op316] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
    # [peephole-li] [op318] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op319] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op320] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op321] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op322] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk7_head  # [op324] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk8_head:  # block chunk8_head
li s1, 16  # [op325] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op326] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc327_true  # [op327] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op327] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op327] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk8_exit  # [op327] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc327_true:  # [op327] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk8_body  # [op327] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk8_exit:  # block chunk8_exit
li t1, 0  # [op328] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op329] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op329] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op329] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk9_head  # [op329] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk8_body:  # block chunk8_body
li s1, 16  # [op330] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op331] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 16  # [op332] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vmv.v.x v1, a2  # [op334] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vid.v v2  # [op335] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vadd.vx v2, v2, t0  # [op336] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
    # [peephole-li] [op337] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vwadd.vx v4, v2, x0  # [op339] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
    # [peephole-li] [op340] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vsetvli s1, s1, e64, m2, ta,ma  # [op341] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li s1, 4  # [op342] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vmul.vx v2, v4, s1  # [op343] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li s1, 21760  # [op344] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
add s1, a1, s1  # [op345] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li a1, 16  # [op346] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vsetvli a1, a1, e32, m1, ta,ma  # [op347] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vsuxei64.v v1, (s1), v2  # [op348] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li s1, 16  # [op349] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vid.v v1  # [op351] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vadd.vx v1, v1, t0  # [op352] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
    # [peephole-li] [op353] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vwadd.vx v2, v1, x0  # [op355] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
    # [peephole-li] [op356] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vsetvli s1, s1, e64, m2, ta,ma  # [op357] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
li s1, 4  # [op358] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vmul.vx v2, v2, s1  # [op359] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
li s1, 0  # [op360] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
add s1, a1, s1  # [op361] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
li a1, 16  # [op362] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vsetvli a1, a1, e32, m1, ta,ma  # [op363] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vluxei64.v v1, (s1), v2  # [op364] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
li s1, 16  # [op365] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vid.v v2  # [op367] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vadd.vx v2, v2, t0  # [op368] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
    # [peephole-li] [op369] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vwadd.vx v4, v2, x0  # [op371] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
    # [peephole-li] [op372] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vsetvli s1, s1, e64, m2, ta,ma  # [op373] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
li s1, 4  # [op374] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vmul.vx v2, v4, s1  # [op375] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
li s1, 1600  # [op376] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
add s1, a1, s1  # [op377] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
li a1, 16  # [op378] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vsetvli a1, a1, e32, m1, ta,ma  # [op379] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vluxei64.v v4, (s1), v2  # [op380] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
li s1, 16  # [op381] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vmul.vv v2, v1, v4  # [op383] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vid.v v3  # [op384] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vadd.vx v3, v3, t0  # [op385] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
    # [peephole-li] [op386] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vwadd.vx v4, v3, x0  # [op388] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
    # [peephole-li] [op389] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vsetvli s1, s1, e64, m2, ta,ma  # [op390] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
li s1, 4  # [op391] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vmul.vx v4, v4, s1  # [op392] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
li s1, 1664  # [op393] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
add s1, a1, s1  # [op394] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
li a1, 16  # [op395] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vsetvli a1, a1, e32, m1, ta,ma  # [op396] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vsuxei64.v v2, (s1), v4  # [op397] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
li s1, 16  # [op398] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vid.v v2  # [op400] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
vadd.vx v2, v2, t0  # [op401] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
    # [peephole-li] [op402] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
vwadd.vx v4, v2, x0  # [op404] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
    # [peephole-li] [op405] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
vsetvli s1, s1, e64, m2, ta,ma  # [op406] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
li s1, 4  # [op407] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
vmul.vx v2, v4, s1  # [op408] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
li s1, 6080  # [op409] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
add s1, a1, s1  # [op410] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
li a1, 16  # [op411] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
vsetvli a1, a1, e32, m1, ta,ma  # [op412] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
vluxei64.v v4, (s1), v2  # [op413] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
li s1, 16  # [op414] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
vmslt.vv v1, v1, v4  # [op416] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
vid.v v2  # [op417] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
vadd.vx v2, v2, t0  # [op418] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
    # [peephole-li] [op419] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
vwadd.vx v4, v2, x0  # [op421] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
    # [peephole-li] [op422] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
vsetvli s1, s1, e64, m2, ta,ma  # [op423] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
li s1, 4  # [op424] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
vmul.vx v2, v4, s1  # [op425] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
li s1, 6144  # [op426] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
add s1, a1, s1  # [op427] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
li a1, 16  # [op428] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
vsetvli a1, a1, e32, m1, ta,ma  # [op429] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
li a1, 1  # [op430] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
vmv.v.x v4, a1  # [op431] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
li a1, 0  # [op432] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
vmv.v.x v5, a1  # [op433] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
vmv1r.v v0, v1  # [op434] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
vmerge.vvm v1, v5, v4, v0  # [op435] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
vsuxei64.v v1, (s1), v2  # [op436] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
li s1, 16  # [op437] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op438] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op439] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op440] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op441] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk8_head  # [op443] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk9_head:  # block chunk9_head
li s1, 512  # [op444] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op445] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc446_true  # [op446] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op446] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op446] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk9_exit  # [op446] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc446_true:  # [op446] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk9_body  # [op446] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk9_exit:  # block chunk9_exit
li t1, 0  # [op447] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op448] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op448] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op448] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk10_head  # [op448] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk9_body:  # block chunk9_body
li s1, 32  # [op449] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op450] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 0  # [op451] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a1, 32  # [op452] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a1, a1, e16, m1, ta,ma  # [op453] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.x v1, s1  # [op454] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s1, 32  # [op455] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli s1, s1, e32, m1, ta,ma  # [op456] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vid.v v2  # [op457] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vadd.vx v2, v2, t0  # [op458] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s1, 32  # [op459] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vwadd.vx v4, v2, x0  # [op461] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op462] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli s1, s1, e64, m2, ta,ma  # [op463] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s1, 4  # [op464] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmul.vx v2, v4, s1  # [op465] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s1, 12608  # [op466] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add s1, a1, s1  # [op467] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a1, 32  # [op468] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a1, a1, e16, m1, ta,ma  # [op469] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.v v4, v1  # [op470] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vwaddu.vx v6, v4, x0  # [op471] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a1, 32  # [op472] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a1, a1, e32, m1, ta,ma  # [op473] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.v v1, v6  # [op474] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a1, 65536  # [op475] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmul.vx v1, v1, a1  # [op476] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.v v4, v1  # [op477] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a1, 32  # [op478] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsuxei64.v v4, (s1), v2  # [op480] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s1, 32  # [op481] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op483] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op484] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op485] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op486] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op487] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk9_head  # [op489] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk10_head:  # block chunk10_head
li s1, 16  # [op490] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op491] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc492_true  # [op492] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op492] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op492] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk10_exit  # [op492] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc492_true:  # [op492] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk10_body  # [op492] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk10_exit:  # block chunk10_exit
li t1, 0  # [op493] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op494] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op494] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op494] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk11_head  # [op494] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk10_body:  # block chunk10_body
li s1, 16  # [op495] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op496] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 16  # [op497] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vid.v v1  # [op499] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vadd.vx v1, v1, t0  # [op500] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
    # [peephole-li] [op501] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vwadd.vx v2, v1, x0  # [op503] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
    # [peephole-li] [op504] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vsetvli s1, s1, e64, m2, ta,ma  # [op505] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li s1, 4  # [op506] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vmul.vx v2, v2, s1  # [op507] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li s1, 64  # [op508] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
add s1, a1, s1  # [op509] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li a1, 16  # [op510] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vsetvli a1, a1, e32, m1, ta,ma  # [op511] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vluxei64.v v1, (s1), v2  # [op512] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li s1, 16  # [op513] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vid.v v2  # [op515] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vadd.vx v2, v2, t0  # [op516] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
    # [peephole-li] [op517] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vwadd.vx v4, v2, x0  # [op519] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
    # [peephole-li] [op520] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vsetvli s1, s1, e64, m2, ta,ma  # [op521] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li s1, 4  # [op522] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vmul.vx v2, v4, s1  # [op523] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li s1, 21760  # [op524] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
add s1, a1, s1  # [op525] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li a1, 16  # [op526] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vsetvli a1, a1, e32, m1, ta,ma  # [op527] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vluxei64.v v4, (s1), v2  # [op528] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li s1, 16  # [op529] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vmslt.vv v1, v1, v4  # [op531] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vid.v v2  # [op532] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vadd.vx v2, v2, t0  # [op533] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
    # [peephole-li] [op534] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vwadd.vx v4, v2, x0  # [op536] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
    # [peephole-li] [op537] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vsetvli s1, s1, e64, m2, ta,ma  # [op538] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li s1, 4  # [op539] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vmul.vx v2, v4, s1  # [op540] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li s1, 21824  # [op541] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
add s1, a1, s1  # [op542] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li a1, 16  # [op543] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vsetvli a1, a1, e32, m1, ta,ma  # [op544] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li a1, 1  # [op545] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vmv.v.x v4, a1  # [op546] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li a1, 0  # [op547] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vmv.v.x v5, a1  # [op548] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vmv1r.v v0, v1  # [op549] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vmerge.vvm v1, v5, v4, v0  # [op550] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vsuxei64.v v1, (s1), v2  # [op551] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li s1, 16  # [op552] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op553] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op554] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op555] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op556] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk10_head  # [op558] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk11_head:  # block chunk11_head
li s1, 512  # [op559] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op560] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc561_true  # [op561] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op561] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op561] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk11_exit  # [op561] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc561_true:  # [op561] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk11_body  # [op561] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk11_exit:  # block chunk11_exit
li t1, 0  # [op562] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op563] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op563] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op563] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk12_head  # [op563] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk11_body:  # block chunk11_body
li s1, 32  # [op564] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op565] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 0  # [op566] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a1, 32  # [op567] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a1, a1, e16, m1, ta,ma  # [op568] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.x v1, s1  # [op569] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s1, 32  # [op570] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s1, s1, e32, m1, ta,ma  # [op571] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vid.v v2  # [op572] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vadd.vx v2, v2, t0  # [op573] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s1, 32  # [op574] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vwadd.vx v4, v2, x0  # [op576] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
    # [peephole-li] [op577] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s1, s1, e64, m2, ta,ma  # [op578] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s1, 4  # [op579] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmul.vx v2, v4, s1  # [op580] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s1, 28032  # [op581] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add s1, a1, s1  # [op582] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a1, 32  # [op583] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a1, a1, e16, m1, ta,ma  # [op584] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.v v4, v1  # [op585] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vwaddu.vx v6, v4, x0  # [op586] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a1, 32  # [op587] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a1, a1, e32, m1, ta,ma  # [op588] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.v v1, v6  # [op589] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a1, 65536  # [op590] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmul.vx v1, v1, a1  # [op591] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.v v4, v1  # [op592] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a1, 32  # [op593] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsuxei64.v v4, (s1), v2  # [op595] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s1, 32  # [op596] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
    # [peephole-li] [op598] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op599] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op600] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op601] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op602] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk11_head  # [op604] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk12_head:  # block chunk12_head
li s1, 16  # [op605] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op606] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc607_true  # [op607] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t2  # [op607] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv a4, t1  # [op607] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk12_exit  # [op607] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc607_true:  # [op607] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk12_body  # [op607] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk12_exit:  # block chunk12_exit
li t0, 0  # [op608] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
j .Lstg13_head  # [op609] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
.Lchunk12_body:  # block chunk12_body
li s1, 16  # [op610] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op611] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 16  # [op612] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op613] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op614] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op615] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op616] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk12_head  # [op618] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lstg13_head:  # block stg13_head
li t1, 512  # [op619] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
slt t1, t0, t1  # [op620] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
bne t1, zero, .Lbrc621_true  # [op621] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
j .Lstg13_exit  # [op621] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
.Lbrc621_true:  # [op621] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
j .Lstg13_body  # [op621] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
.Lstg13_body:  # block stg13_body
li t1, 32  # [op622] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t1, t1, e32, m1, ta,ma  # [op623] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vid.v v1  # [op624] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vadd.vx v1, v1, t0  # [op625] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t1, 32  # [op626] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv.v.x v2, t1  # [op627] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vdiv.vv v2, v1, v2  # [op628] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t1, 16  # [op629] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv.v.x v3, t1  # [op630] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vrem.vv v2, v2, v3  # [op631] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t1, 32  # [op632] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv.v.x v3, t1  # [op633] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vrem.vv v3, v1, v3  # [op634] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op635] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vwadd.vx v4, v2, x0  # [op637] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op638] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t1, t1, e64, m2, ta,ma  # [op639] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t1, 4  # [op640] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmul.vx v2, v4, t1  # [op641] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t1, 6144  # [op642] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld s1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld s1, 16(s1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
add t1, s1, t1  # [op643] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li s1, 32  # [op644] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli s1, s1, e32, m1, ta,ma  # [op645] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vluxei64.v v4, (t1), v2  # [op646] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t1, 32  # [op647] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vwadd.vx v2, v1, x0  # [op649] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op650] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t1, t1, e64, m2, ta,ma  # [op651] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t1, 4  # [op652] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmul.vx v2, v2, t1  # [op653] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t1, 6464  # [op654] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld s1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld s1, 16(s1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
add t1, s1, t1  # [op655] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li s1, 32  # [op656] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli s1, s1, e32, m1, ta,ma  # [op657] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsuxei64.v v4, (t1), v2  # [op658] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t1, 32  # [op659] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
addw t0, t0, t1  # [op660] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
j .Lstg13_head  # [op661] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
.Lstg13_exit:  # block stg13_exit
li t0, 0  # [op662] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
j .Lstg14_head  # [op663] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
.Lstg14_head:  # block stg14_head
li t1, 512  # [op664] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
slt t1, t0, t1  # [op665] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
bne t1, zero, .Lbrc666_true  # [op666] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
j .Lstg14_exit  # [op666] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
.Lbrc666_true:  # [op666] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
j .Lstg14_body  # [op666] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
.Lstg14_body:  # block stg14_body
li t1, 32  # [op667] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t1, t1, e32, m1, ta,ma  # [op668] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vid.v v1  # [op669] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vadd.vx v1, v1, t0  # [op670] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t1, 16  # [op671] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv.v.x v2, t1  # [op672] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vdiv.vv v2, v1, v2  # [op673] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t1, 32  # [op674] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv.v.x v3, t1  # [op675] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vrem.vv v2, v2, v3  # [op676] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t1, 16  # [op677] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv.v.x v2, t1  # [op678] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vrem.vv v2, v1, v2  # [op679] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t1, 32  # [op680] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vwadd.vx v4, v2, x0  # [op682] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
    # [peephole-li] [op683] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t1, t1, e64, m2, ta,ma  # [op684] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t1, 4  # [op685] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmul.vx v2, v4, t1  # [op686] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t1, 21824  # [op687] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld s1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld s1, 16(s1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
add t1, s1, t1  # [op688] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li s1, 32  # [op689] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli s1, s1, e32, m1, ta,ma  # [op690] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vluxei64.v v4, (t1), v2  # [op691] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t1, 32  # [op692] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vwadd.vx v2, v1, x0  # [op694] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
    # [peephole-li] [op695] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t1, t1, e64, m2, ta,ma  # [op696] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t1, 4  # [op697] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmul.vx v2, v2, t1  # [op698] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t1, 23936  # [op699] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld s1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld s1, 16(s1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
add t1, s1, t1  # [op700] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li s1, 32  # [op701] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli s1, s1, e32, m1, ta,ma  # [op702] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsuxei64.v v4, (t1), v2  # [op703] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t1, 32  # [op704] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
addw t0, t0, t1  # [op705] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
j .Lstg14_head  # [op706] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
.Lstg14_exit:  # block stg14_exit
li t0, 0  # [op707] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
li s7, 32  # [op708] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
mv a1, t0  # [op709] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
j .Lmloop15.head  # [op709] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
.Lmloop15.head:  # block mloop15.head
ld t0, 136(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
slt t0, a1, t0  # [op710] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
bne t0, zero, .Lbrc711_true  # [op711] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
mv t0, a1  # [op711] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
j .Lmloop15.exit  # [op711] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
.Lbrc711_true:  # [op711] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
j .Lmloop15.body  # [op711] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
.Lmloop15.body:  # block mloop15.body
li t0, 0  # [op712] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, a4  # [op713] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk16_head  # [op713] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lmloop15.exit:  # block mloop15.exit
li t0, 0  # [op714] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, a4  # [op715] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk30_head  # [op715] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk16_head:  # block chunk16_head
li s1, 32  # [op716] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op717] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc718_true  # [op718] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op718] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op718] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk16_exit  # [op718] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc718_true:  # [op718] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk16_body  # [op718] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk16_exit:  # block chunk16_exit
li t1, 0  # [op719] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op720] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op720] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op720] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk17_head  # [op720] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk16_body:  # block chunk16_body
li s1, 32  # [op721] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op722] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op723] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vmv.v.x v1, a1  # [op725] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vid.v v2  # [op726] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vadd.vx v2, v2, t0  # [op727] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
    # [peephole-li] [op728] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vwadd.vx v4, v2, x0  # [op730] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
    # [peephole-li] [op731] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vsetvli s1, s1, e64, m2, ta,ma  # [op732] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
li s1, 4  # [op733] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vmul.vx v2, v4, s1  # [op734] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
li s1, 1280  # [op735] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
ld a3, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
ld a3, 16(a3)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
add s1, a3, s1  # [op736] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
li a3, 32  # [op737] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vsetvli a3, a3, e32, m1, ta,ma  # [op738] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vsuxei64.v v1, (s1), v2  # [op739] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
li s1, 32  # [op740] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vid.v v2  # [op742] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vadd.vx v2, v2, t0  # [op743] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
    # [peephole-li] [op744] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vwadd.vx v4, v2, x0  # [op746] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
    # [peephole-li] [op747] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vsetvli s1, s1, e64, m2, ta,ma  # [op748] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
li s1, 4  # [op749] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vmul.vx v2, v4, s1  # [op750] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
li s1, 128  # [op751] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
ld a3, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
ld a3, 16(a3)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
add s1, a3, s1  # [op752] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
li a3, 32  # [op753] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vsetvli a3, a3, e32, m1, ta,ma  # [op754] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vluxei64.v v4, (s1), v2  # [op755] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
li s1, 32  # [op756] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vadd.vv v1, v1, v4  # [op758] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vid.v v2  # [op759] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vadd.vx v2, v2, t0  # [op760] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
    # [peephole-li] [op761] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vwadd.vx v4, v2, x0  # [op763] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
    # [peephole-li] [op764] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vsetvli s1, s1, e64, m2, ta,ma  # [op765] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
li s1, 4  # [op766] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vmul.vx v2, v4, s1  # [op767] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
li s1, 1408  # [op768] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
ld a3, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
ld a3, 16(a3)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
add s1, a3, s1  # [op769] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
li a3, 32  # [op770] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vsetvli a3, a3, e32, m1, ta,ma  # [op771] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vsuxei64.v v1, (s1), v2  # [op772] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
li s1, 32  # [op773] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
    # [peephole-li] [op775] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op776] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op777] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op778] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op779] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk16_head  # [op781] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk17_head:  # block chunk17_head
li s1, 512  # [op782] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op783] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc784_true  # [op784] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op784] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op784] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk17_exit  # [op784] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc784_true:  # [op784] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk17_body  # [op784] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk17_exit:  # block chunk17_exit
li t1, 0  # [op785] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op786] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op786] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op786] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk18_head  # [op786] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk17_body:  # block chunk17_body
li s1, 32  # [op787] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op788] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op789] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
vid.v v1  # [op791] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
vadd.vx v1, v1, t0  # [op792] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
    # [peephole-li] [op793] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
vmv.v.x v2, s1  # [op794] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
vdiv.vv v1, v1, v2  # [op795] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
    # [peephole-li] [op796] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
vwadd.vx v2, v1, x0  # [op798] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
    # [peephole-li] [op799] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
vsetvli s1, s1, e64, m2, ta,ma  # [op800] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
li s1, 8  # [op801] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
vmul.vx v2, v2, s1  # [op802] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
li s1, 1728  # [op803] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
ld a3, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
ld a3, 16(a3)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
add s1, a3, s1  # [op804] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
li a3, 32  # [op805] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
vluxei64.v v4, (s1), v2  # [op807] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
li s1, 32  # [op808] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
vsetvli s1, s1, e32, m1, ta,ma  # [op809] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
li s1, 32  # [op810] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op811] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op812] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op813] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op814] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk17_head  # [op816] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk18_head:  # block chunk18_head
li s1, 32  # [op817] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op818] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc819_true  # [op819] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t2  # [op819] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk18_exit  # [op819] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc819_true:  # [op819] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk18_body  # [op819] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk18_exit:  # block chunk18_exit
li t0, 0  # [op820] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
j .Lstg19_head  # [op821] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
.Lchunk18_body:  # block chunk18_body
li s1, 32  # [op822] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op823] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op824] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vid.v v1  # [op826] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vadd.vx v1, v1, t0  # [op827] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
    # [peephole-li] [op828] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vwadd.vx v2, v1, x0  # [op830] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
    # [peephole-li] [op831] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vsetvli s1, s1, e64, m2, ta,ma  # [op832] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li s1, 4  # [op833] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vmul.vx v2, v2, s1  # [op834] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li s1, 1408  # [op835] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
ld a3, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
ld a3, 16(a3)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
add s1, a3, s1  # [op836] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li a3, 32  # [op837] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vsetvli a3, a3, e32, m1, ta,ma  # [op838] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vluxei64.v v1, (s1), v2  # [op839] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li s1, 32  # [op840] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vid.v v2  # [op842] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vadd.vx v2, v2, t0  # [op843] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
    # [peephole-li] [op844] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vwadd.vx v4, v2, x0  # [op846] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
    # [peephole-li] [op847] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vsetvli s1, s1, e64, m2, ta,ma  # [op848] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li s1, 4  # [op849] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vmul.vx v2, v4, s1  # [op850] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li s1, 6208  # [op851] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
ld a3, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
ld a3, 16(a3)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
add s1, a3, s1  # [op852] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li a3, 32  # [op853] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vsetvli a3, a3, e32, m1, ta,ma  # [op854] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vluxei64.v v4, (s1), v2  # [op855] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li s1, 32  # [op856] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vmslt.vv v1, v1, v4  # [op858] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vid.v v2  # [op859] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vadd.vx v2, v2, t0  # [op860] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
    # [peephole-li] [op861] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vwadd.vx v4, v2, x0  # [op863] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
    # [peephole-li] [op864] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vsetvli s1, s1, e64, m2, ta,ma  # [op865] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li s1, 4  # [op866] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vmul.vx v2, v4, s1  # [op867] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li s1, 6336  # [op868] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
ld a3, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
ld a3, 16(a3)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
add s1, a3, s1  # [op869] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li a3, 32  # [op870] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vsetvli a3, a3, e32, m1, ta,ma  # [op871] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li a3, 1  # [op872] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vmv.v.x v4, a3  # [op873] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li a3, 0  # [op874] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vmv.v.x v5, a3  # [op875] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vmv1r.v v0, v1  # [op876] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vmerge.vvm v1, v5, v4, v0  # [op877] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vsuxei64.v v1, (s1), v2  # [op878] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li s1, 32  # [op879] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op880] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op881] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op882] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op883] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk18_head  # [op885] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lstg19_head:  # block stg19_head
li s1, 512  # [op886] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
slt s1, t0, s1  # [op887] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
bne s1, zero, .Lbrc888_true  # [op888] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
j .Lstg19_exit  # [op888] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
.Lbrc888_true:  # [op888] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
j .Lstg19_body  # [op888] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
.Lstg19_body:  # block stg19_body
li s1, 32  # [op889] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli s1, s1, e32, m1, ta,ma  # [op890] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vid.v v1  # [op891] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vadd.vx v1, v1, t0  # [op892] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li s1, 32  # [op893] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv.v.x v2, s1  # [op894] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vdiv.vv v2, v1, v2  # [op895] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li s1, 16  # [op896] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv.v.x v3, s1  # [op897] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vrem.vv v2, v2, v3  # [op898] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li s1, 32  # [op899] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv.v.x v2, s1  # [op900] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vrem.vv v2, v1, v2  # [op901] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op902] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vwadd.vx v4, v2, x0  # [op904] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op905] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli s1, s1, e64, m2, ta,ma  # [op906] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li s1, 4  # [op907] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmul.vx v2, v4, s1  # [op908] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li s1, 6336  # [op909] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld a3, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld a3, 16(a3)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
add s1, a3, s1  # [op910] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li a3, 32  # [op911] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli a3, a3, e32, m1, ta,ma  # [op912] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vluxei64.v v4, (s1), v2  # [op913] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li s1, 32  # [op914] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vwadd.vx v2, v1, x0  # [op916] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op917] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli s1, s1, e64, m2, ta,ma  # [op918] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li s1, 4  # [op919] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmul.vx v2, v2, s1  # [op920] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li s1, 8512  # [op921] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld a3, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld a3, 16(a3)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
add s1, a3, s1  # [op922] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li a3, 32  # [op923] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli a3, a3, e32, m1, ta,ma  # [op924] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsuxei64.v v4, (s1), v2  # [op925] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li s1, 32  # [op926] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
addw t0, t0, s1  # [op927] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
j .Lstg19_head  # [op928] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
.Lstg19_exit:  # block stg19_exit
li t0, 0  # [op929] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv s1, t0  # [op930] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv a3, t1  # [op930] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk20_head  # [op930] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk20_head:  # block chunk20_head
li t0, 512  # [op931] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt t0, s1, t0  # [op932] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne t0, zero, .Lbrc933_true  # [op933] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op933] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, a3  # [op933] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk20_exit  # [op933] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc933_true:  # [op933] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk20_body  # [op933] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk20_exit:  # block chunk20_exit
li t1, 0  # [op934] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op935] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op935] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op935] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk21_head  # [op935] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk20_body:  # block chunk20_body
li t0, 32  # [op936] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli t0, t0, e16, m1, ta,ma  # [op937] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li t0, 32  # [op938] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t0, t0, e32, m1, ta,ma  # [op939] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vid.v v1  # [op940] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vadd.vx v1, v1, s1  # [op941] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 32  # [op942] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vwadd.vx v2, v1, x0  # [op944] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op945] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t0, t0, e64, m2, ta,ma  # [op946] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 4  # [op947] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmul.vx v2, v2, t0  # [op948] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 6464  # [op949] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld t1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld t1, 16(t1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
add t0, t1, t0  # [op950] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t1, 32  # [op951] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t1, t1, e32, m1, ta,ma  # [op952] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vluxei64.v v1, (t0), v2  # [op953] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 0  # [op954] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv.v.x v2, t0  # [op955] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmsne.vv v1, v1, v2  # [op956] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 32  # [op957] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t0, t0, e16, m1, ta,ma  # [op958] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 32  # [op959] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t0, t0, e32, m1, ta,ma  # [op960] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vid.v v2  # [op961] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vadd.vx v2, v2, s1  # [op962] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 32  # [op963] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vwadd.vx v4, v2, x0  # [op965] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op966] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t0, t0, e64, m2, ta,ma  # [op967] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 4  # [op968] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmul.vx v2, v4, t0  # [op969] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 8512  # [op970] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld t1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld t1, 16(t1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
add t0, t1, t0  # [op971] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t1, 32  # [op972] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t1, t1, e32, m1, ta,ma  # [op973] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vluxei64.v v4, (t0), v2  # [op974] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 0  # [op975] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv.v.x v2, t0  # [op976] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmsne.vv v2, v4, v2  # [op977] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 32  # [op978] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t0, t0, e16, m1, ta,ma  # [op979] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmand.mm v1, v1, v2  # [op980] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 32  # [op981] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t0, t0, e32, m1, ta,ma  # [op982] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vid.v v2  # [op983] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vadd.vx v2, v2, s1  # [op984] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 32  # [op985] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vwadd.vx v4, v2, x0  # [op987] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op988] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t0, t0, e64, m2, ta,ma  # [op989] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 4  # [op990] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmul.vx v2, v4, t0  # [op991] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 10560  # [op992] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld t1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld t1, 16(t1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
add t0, t1, t0  # [op993] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t1, 32  # [op994] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t1, t1, e32, m1, ta,ma  # [op995] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t1, 1  # [op996] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv.v.x v4, t1  # [op997] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t1, 0  # [op998] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv.v.x v5, t1  # [op999] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv1r.v v0, v1  # [op1000] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmerge.vvm v4, v5, v4, v0  # [op1001] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsuxei64.v v4, (t0), v2  # [op1002] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 32  # [op1003] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t0, t0, e16, m1, ta,ma  # [op1004] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 32  # [op1005] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t0, t0, e32, m1, ta,ma  # [op1006] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vid.v v2  # [op1007] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vadd.vx v2, v2, s1  # [op1008] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 32  # [op1009] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vwadd.vx v4, v2, x0  # [op1011] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op1012] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t0, t0, e64, m2, ta,ma  # [op1013] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 4  # [op1014] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmul.vx v2, v4, t0  # [op1015] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 10560  # [op1016] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld t1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld t1, 16(t1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
add t0, t1, t0  # [op1017] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t1, 32  # [op1018] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t1, t1, e32, m1, ta,ma  # [op1019] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t1, 1  # [op1020] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv.v.x v4, t1  # [op1021] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t1, 0  # [op1022] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv.v.x v5, t1  # [op1023] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv1r.v v0, v1  # [op1024] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmerge.vvm v4, v5, v4, v0  # [op1025] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsuxei64.v v4, (t0), v2  # [op1026] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 32  # [op1027] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t0, t0, e16, m1, ta,ma  # [op1028] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 32  # [op1029] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e32, m1, ta,ma  # [op1030] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vid.v v2  # [op1031] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vadd.vx v2, v2, s1  # [op1032] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1033] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.x v3, t0  # [op1034] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vdiv.vv v2, v2, v3  # [op1035] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op1036] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vwadd.vx v4, v2, x0  # [op1038] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op1039] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e64, m2, ta,ma  # [op1040] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 4  # [op1041] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmul.vx v2, v4, t0  # [op1042] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 1664  # [op1043] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
ld t1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
ld t1, 16(t1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add t0, t1, t0  # [op1044] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t1, 32  # [op1045] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t1, t1, e32, m1, ta,ma  # [op1046] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vluxei64.v v4, (t0), v2  # [op1047] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1048] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e16, m1, ta,ma  # [op1049] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1050] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e32, m1, ta,ma  # [op1051] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vid.v v2  # [op1052] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vadd.vx v2, v2, s1  # [op1053] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1054] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.x v3, t0  # [op1055] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vrem.vv v2, v2, v3  # [op1056] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op1057] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vwadd.vx v6, v2, x0  # [op1059] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op1060] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e64, m2, ta,ma  # [op1061] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 4  # [op1062] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmul.vx v2, v6, t0  # [op1063] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 1408  # [op1064] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
ld t1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
ld t1, 16(t1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add t0, t1, t0  # [op1065] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t1, 32  # [op1066] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t1, t1, e32, m1, ta,ma  # [op1067] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vluxei64.v v5, (t0), v2  # [op1068] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1069] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e16, m1, ta,ma  # [op1070] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1071] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e32, m1, ta,ma  # [op1072] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vadd.vv v2, v4, v5  # [op1073] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1074] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e16, m1, ta,ma  # [op1075] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1076] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e32, m1, ta,ma  # [op1077] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vwadd.vx v4, v2, x0  # [op1078] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1079] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e64, m2, ta,ma  # [op1080] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 2  # [op1081] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmul.vx v2, v4, t0  # [op1082] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1083] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e16, m1, ta,ma  # [op1084] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 37440  # [op1085] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
ld t1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
ld t1, 16(t1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add t0, t1, t0  # [op1086] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t1, 128  # [op1087] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add t1, t0, t1  # [op1088] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1089] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e32, m1, ta,ma  # [op1090] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 0  # [op1091] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.x v4, a5  # [op1092] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 1  # [op1093] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.x v5, a5  # [op1094] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv1r.v v0, v1  # [op1095] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmerge.vvm v4, v4, v5, v0  # [op1096] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vid.v v1  # [op1097] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vadd.vx v1, v1, s1  # [op1098] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1099] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vwadd.vx v6, v1, x0  # [op1101] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op1102] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e64, m2, ta,ma  # [op1103] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 4  # [op1104] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmul.vx v6, v6, a5  # [op1105] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 12608  # [op1106] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
ld s8, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
ld s8, 16(s8)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a5, s8, a5  # [op1107] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s8, 32  # [op1108] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli s8, s8, e32, m1, ta,ma  # [op1109] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vluxei64.v v5, (a5), v6  # [op1110] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1111] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.v v1, v5  # [op1113] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32767  # [op1114] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.x v5, a5  # [op1115] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 16  # [op1116] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.x v6, a5  # [op1117] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 1  # [op1118] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.x v7, a5  # [op1119] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vadd.vv v5, v1, v5  # [op1120] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsrl.vv v6, v1, v6  # [op1121] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vand.vv v6, v6, v7  # [op1122] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vadd.vv v5, v5, v6  # [op1123] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 2139095040  # [op1124] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.x v6, a5  # [op1125] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op1126] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.x v7, a5  # [op1127] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 8388607  # [op1128] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.x v8, a5  # [op1129] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 0  # [op1130] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.x v9, a5  # [op1131] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vand.vv v6, v1, v6  # [op1132] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmseq.vv v6, v6, v7  # [op1133] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vand.vv v7, v1, v8  # [op1134] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmsne.vv v7, v7, v9  # [op1135] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmand.mm v6, v6, v7  # [op1136] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 4194304  # [op1137] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.x v7, a5  # [op1138] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vor.vv v1, v1, v7  # [op1139] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv1r.v v0, v6  # [op1140] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmerge.vvm v1, v5, v1, v0  # [op1141] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 16  # [op1142] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.x v5, a5  # [op1143] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsrl.vv v1, v1, v5  # [op1144] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.v v5, v1  # [op1145] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1146] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e16, m1, ta,ma  # [op1147] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vid.v v1  # [op1148] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 2  # [op1149] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.x v6, a5  # [op1150] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmul.vv v1, v1, v6  # [op1151] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vrgather.vv v6, v5, v1  # [op1152] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.v v1, v6  # [op1153] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1154] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e64, m2, ta,ma  # [op1155] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vadd.vx v6, v2, s2  # [op1156] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1157] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e32, m1, ta,ma  # [op1158] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 0  # [op1159] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.x v2, a5  # [op1160] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmsne.vv v2, v4, v2  # [op1161] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv1r.v v0, v2  # [op1162] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1163] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e64, m2, ta,ma  # [op1164] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 0  # [op1165] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.x v4, a5  # [op1166] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.x v2, t1  # [op1167] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsub.vv v6, v6, v2  # [op1168] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmerge.vvm v4, v4, v6, v0  # [op1169] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vadd.vv v2, v2, v4  # [op1170] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1171] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e16, m1, ta,ma  # [op1172] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1173] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e64, m2, ta,ma  # [op1174] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a5, v2  # [op1175] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s8, 0  # [op1176] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add s8, t0, s8  # [op1177] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s9, 32  # [op1178] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli s9, s9, e16, m1, ta,ma  # [op1179] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s s9, v1  # [op1180] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh s9, 0(t1)  # [op1181] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1182] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a5, 0(a5)  # [op1183] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a5, 0(s8)  # [op1184] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1185] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e64, m2, ta,ma  # [op1186] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1187] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a5, v2  # [op1188] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s8, 2  # [op1189] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add s8, t0, s8  # [op1190] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s9, 32  # [op1191] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli s9, s9, e16, m1, ta,ma  # [op1192] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s s9, v1  # [op1193] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh s9, 0(t1)  # [op1194] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1195] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a5, 0(a5)  # [op1196] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a5, 0(s8)  # [op1197] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1198] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e64, m2, ta,ma  # [op1199] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1200] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a5, v2  # [op1201] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s8, 4  # [op1202] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add s8, t0, s8  # [op1203] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s9, 32  # [op1204] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli s9, s9, e16, m1, ta,ma  # [op1205] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s s9, v1  # [op1206] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh s9, 0(t1)  # [op1207] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1208] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a5, 0(a5)  # [op1209] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a5, 0(s8)  # [op1210] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1211] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e64, m2, ta,ma  # [op1212] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1213] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a5, v2  # [op1214] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s8, 6  # [op1215] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add s8, t0, s8  # [op1216] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s9, 32  # [op1217] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli s9, s9, e16, m1, ta,ma  # [op1218] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s s9, v1  # [op1219] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh s9, 0(t1)  # [op1220] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1221] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a5, 0(a5)  # [op1222] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a5, 0(s8)  # [op1223] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1224] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e64, m2, ta,ma  # [op1225] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1226] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a5, v2  # [op1227] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s8, 8  # [op1228] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add s8, t0, s8  # [op1229] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s9, 32  # [op1230] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli s9, s9, e16, m1, ta,ma  # [op1231] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s s9, v1  # [op1232] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh s9, 0(t1)  # [op1233] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1234] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a5, 0(a5)  # [op1235] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a5, 0(s8)  # [op1236] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1237] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e64, m2, ta,ma  # [op1238] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1239] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a5, v2  # [op1240] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s8, 10  # [op1241] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add s8, t0, s8  # [op1242] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s9, 32  # [op1243] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli s9, s9, e16, m1, ta,ma  # [op1244] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s s9, v1  # [op1245] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh s9, 0(t1)  # [op1246] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1247] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a5, 0(a5)  # [op1248] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a5, 0(s8)  # [op1249] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1250] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e64, m2, ta,ma  # [op1251] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1252] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a5, v2  # [op1253] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s8, 12  # [op1254] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add s8, t0, s8  # [op1255] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s9, 32  # [op1256] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli s9, s9, e16, m1, ta,ma  # [op1257] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s s9, v1  # [op1258] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh s9, 0(t1)  # [op1259] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1260] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a5, 0(a5)  # [op1261] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a5, 0(s8)  # [op1262] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1263] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e64, m2, ta,ma  # [op1264] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1265] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a5, v2  # [op1266] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s8, 14  # [op1267] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add s8, t0, s8  # [op1268] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s9, 32  # [op1269] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli s9, s9, e16, m1, ta,ma  # [op1270] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s s9, v1  # [op1271] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh s9, 0(t1)  # [op1272] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1273] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a5, 0(a5)  # [op1274] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a5, 0(s8)  # [op1275] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1276] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e64, m2, ta,ma  # [op1277] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1278] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a5, v2  # [op1279] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s8, 16  # [op1280] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add s8, t0, s8  # [op1281] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s9, 32  # [op1282] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli s9, s9, e16, m1, ta,ma  # [op1283] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s s9, v1  # [op1284] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh s9, 0(t1)  # [op1285] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1286] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a5, 0(a5)  # [op1287] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a5, 0(s8)  # [op1288] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1289] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e64, m2, ta,ma  # [op1290] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1291] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a5, v2  # [op1292] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s8, 18  # [op1293] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add s8, t0, s8  # [op1294] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s9, 32  # [op1295] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli s9, s9, e16, m1, ta,ma  # [op1296] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s s9, v1  # [op1297] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh s9, 0(t1)  # [op1298] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1299] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a5, 0(a5)  # [op1300] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a5, 0(s8)  # [op1301] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1302] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e64, m2, ta,ma  # [op1303] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1304] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a5, v2  # [op1305] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s8, 20  # [op1306] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add s8, t0, s8  # [op1307] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s9, 32  # [op1308] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli s9, s9, e16, m1, ta,ma  # [op1309] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s s9, v1  # [op1310] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh s9, 0(t1)  # [op1311] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1312] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a5, 0(a5)  # [op1313] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a5, 0(s8)  # [op1314] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1315] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e64, m2, ta,ma  # [op1316] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1317] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a5, v2  # [op1318] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s8, 22  # [op1319] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add s8, t0, s8  # [op1320] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s9, 32  # [op1321] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli s9, s9, e16, m1, ta,ma  # [op1322] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s s9, v1  # [op1323] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh s9, 0(t1)  # [op1324] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1325] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a5, 0(a5)  # [op1326] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a5, 0(s8)  # [op1327] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1328] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e64, m2, ta,ma  # [op1329] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1330] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a5, v2  # [op1331] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s8, 24  # [op1332] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add s8, t0, s8  # [op1333] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s9, 32  # [op1334] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli s9, s9, e16, m1, ta,ma  # [op1335] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s s9, v1  # [op1336] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh s9, 0(t1)  # [op1337] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1338] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a5, 0(a5)  # [op1339] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a5, 0(s8)  # [op1340] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1341] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e64, m2, ta,ma  # [op1342] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1343] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a5, v2  # [op1344] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s8, 26  # [op1345] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add s8, t0, s8  # [op1346] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s9, 32  # [op1347] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli s9, s9, e16, m1, ta,ma  # [op1348] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s s9, v1  # [op1349] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh s9, 0(t1)  # [op1350] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1351] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a5, 0(a5)  # [op1352] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a5, 0(s8)  # [op1353] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1354] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e64, m2, ta,ma  # [op1355] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1356] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a5, v2  # [op1357] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s8, 28  # [op1358] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add s8, t0, s8  # [op1359] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s9, 32  # [op1360] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli s9, s9, e16, m1, ta,ma  # [op1361] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s s9, v1  # [op1362] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh s9, 0(t1)  # [op1363] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1364] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a5, 0(a5)  # [op1365] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a5, 0(s8)  # [op1366] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1367] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e64, m2, ta,ma  # [op1368] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1369] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a5, v2  # [op1370] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s8, 30  # [op1371] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add s8, t0, s8  # [op1372] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s9, 32  # [op1373] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli s9, s9, e16, m1, ta,ma  # [op1374] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s s9, v1  # [op1375] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh s9, 0(t1)  # [op1376] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1377] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a5, 0(a5)  # [op1378] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a5, 0(s8)  # [op1379] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1380] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e64, m2, ta,ma  # [op1381] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1382] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a5, v2  # [op1383] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s8, 32  # [op1384] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add s8, t0, s8  # [op1385] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s9, 32  # [op1386] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli s9, s9, e16, m1, ta,ma  # [op1387] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s s9, v1  # [op1388] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh s9, 0(t1)  # [op1389] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1390] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a5, 0(a5)  # [op1391] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a5, 0(s8)  # [op1392] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1393] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e64, m2, ta,ma  # [op1394] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1395] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a5, v2  # [op1396] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s8, 34  # [op1397] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add s8, t0, s8  # [op1398] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s9, 32  # [op1399] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli s9, s9, e16, m1, ta,ma  # [op1400] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s s9, v1  # [op1401] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh s9, 0(t1)  # [op1402] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1403] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a5, 0(a5)  # [op1404] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a5, 0(s8)  # [op1405] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1406] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e64, m2, ta,ma  # [op1407] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1408] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a5, v2  # [op1409] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s8, 36  # [op1410] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add s8, t0, s8  # [op1411] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s9, 32  # [op1412] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli s9, s9, e16, m1, ta,ma  # [op1413] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s s9, v1  # [op1414] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh s9, 0(t1)  # [op1415] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1416] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a5, 0(a5)  # [op1417] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a5, 0(s8)  # [op1418] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1419] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e64, m2, ta,ma  # [op1420] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1421] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a5, v2  # [op1422] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s8, 38  # [op1423] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add s8, t0, s8  # [op1424] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s9, 32  # [op1425] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli s9, s9, e16, m1, ta,ma  # [op1426] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s s9, v1  # [op1427] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh s9, 0(t1)  # [op1428] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1429] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a5, 0(a5)  # [op1430] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a5, 0(s8)  # [op1431] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1432] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e64, m2, ta,ma  # [op1433] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1434] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a5, v2  # [op1435] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s8, 40  # [op1436] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add s8, t0, s8  # [op1437] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s9, 32  # [op1438] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli s9, s9, e16, m1, ta,ma  # [op1439] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s s9, v1  # [op1440] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh s9, 0(t1)  # [op1441] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1442] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a5, 0(a5)  # [op1443] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a5, 0(s8)  # [op1444] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1445] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e64, m2, ta,ma  # [op1446] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1447] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a5, v2  # [op1448] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s8, 42  # [op1449] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add s8, t0, s8  # [op1450] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s9, 32  # [op1451] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli s9, s9, e16, m1, ta,ma  # [op1452] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s s9, v1  # [op1453] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh s9, 0(t1)  # [op1454] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1455] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a5, 0(a5)  # [op1456] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a5, 0(s8)  # [op1457] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1458] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e64, m2, ta,ma  # [op1459] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1460] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a5, v2  # [op1461] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s8, 44  # [op1462] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add s8, t0, s8  # [op1463] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s9, 32  # [op1464] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli s9, s9, e16, m1, ta,ma  # [op1465] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s s9, v1  # [op1466] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh s9, 0(t1)  # [op1467] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1468] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a5, 0(a5)  # [op1469] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a5, 0(s8)  # [op1470] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1471] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e64, m2, ta,ma  # [op1472] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1473] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a5, v2  # [op1474] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s8, 46  # [op1475] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add s8, t0, s8  # [op1476] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s9, 32  # [op1477] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli s9, s9, e16, m1, ta,ma  # [op1478] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s s9, v1  # [op1479] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh s9, 0(t1)  # [op1480] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1481] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a5, 0(a5)  # [op1482] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a5, 0(s8)  # [op1483] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1484] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e64, m2, ta,ma  # [op1485] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1486] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a5, v2  # [op1487] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s8, 48  # [op1488] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add s8, t0, s8  # [op1489] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s9, 32  # [op1490] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli s9, s9, e16, m1, ta,ma  # [op1491] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s s9, v1  # [op1492] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh s9, 0(t1)  # [op1493] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1494] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a5, 0(a5)  # [op1495] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a5, 0(s8)  # [op1496] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1497] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e64, m2, ta,ma  # [op1498] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1499] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a5, v2  # [op1500] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s8, 50  # [op1501] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add s8, t0, s8  # [op1502] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s9, 32  # [op1503] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli s9, s9, e16, m1, ta,ma  # [op1504] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s s9, v1  # [op1505] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh s9, 0(t1)  # [op1506] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1507] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a5, 0(a5)  # [op1508] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a5, 0(s8)  # [op1509] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1510] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e64, m2, ta,ma  # [op1511] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1512] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a5, v2  # [op1513] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s8, 52  # [op1514] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add s8, t0, s8  # [op1515] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s9, 32  # [op1516] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli s9, s9, e16, m1, ta,ma  # [op1517] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s s9, v1  # [op1518] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh s9, 0(t1)  # [op1519] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1520] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a5, 0(a5)  # [op1521] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a5, 0(s8)  # [op1522] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1523] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e64, m2, ta,ma  # [op1524] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1525] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a5, v2  # [op1526] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s8, 54  # [op1527] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add s8, t0, s8  # [op1528] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s9, 32  # [op1529] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli s9, s9, e16, m1, ta,ma  # [op1530] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s s9, v1  # [op1531] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh s9, 0(t1)  # [op1532] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1533] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a5, 0(a5)  # [op1534] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a5, 0(s8)  # [op1535] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1536] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e64, m2, ta,ma  # [op1537] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1538] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a5, v2  # [op1539] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s8, 56  # [op1540] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add s8, t0, s8  # [op1541] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s9, 32  # [op1542] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli s9, s9, e16, m1, ta,ma  # [op1543] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s s9, v1  # [op1544] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh s9, 0(t1)  # [op1545] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1546] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a5, 0(a5)  # [op1547] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a5, 0(s8)  # [op1548] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1549] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e64, m2, ta,ma  # [op1550] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1551] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a5, v2  # [op1552] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s8, 58  # [op1553] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add s8, t0, s8  # [op1554] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s9, 32  # [op1555] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli s9, s9, e16, m1, ta,ma  # [op1556] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s s9, v1  # [op1557] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh s9, 0(t1)  # [op1558] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1559] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a5, 0(a5)  # [op1560] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a5, 0(s8)  # [op1561] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1562] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e64, m2, ta,ma  # [op1563] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1564] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a5, v2  # [op1565] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s8, 60  # [op1566] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add s8, t0, s8  # [op1567] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s9, 32  # [op1568] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli s9, s9, e16, m1, ta,ma  # [op1569] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s s9, v1  # [op1570] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh s9, 0(t1)  # [op1571] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1572] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a5, 0(a5)  # [op1573] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a5, 0(s8)  # [op1574] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a5, 32  # [op1575] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a5, a5, e64, m2, ta,ma  # [op1576] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1577] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a5, v2  # [op1578] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s8, 62  # [op1579] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add s8, t0, s8  # [op1580] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s9, 32  # [op1581] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli s9, s9, e16, m1, ta,ma  # [op1582] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s s9, v1  # [op1583] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh s9, 0(t1)  # [op1584] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1585] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu t1, 0(a5)  # [op1586] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh t1, 0(s8)  # [op1587] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t1, 32  # [op1588] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t1, t1, e64, m2, ta,ma  # [op1589] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1590] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t1, 32  # [op1591] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t1, t1, e16, m1, ta,ma  # [op1592] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vle16.v v1, 0(t0)  # [op1593] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1594] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e32, m1, ta,ma  # [op1595] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vid.v v2  # [op1596] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vadd.vx v2, v2, s1  # [op1597] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1598] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vwadd.vx v4, v2, x0  # [op1600] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op1601] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e64, m2, ta,ma  # [op1602] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 4  # [op1603] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmul.vx v2, v4, t0  # [op1604] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 14656  # [op1605] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
ld t1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
ld t1, 16(t1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add t0, t1, t0  # [op1606] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t1, 32  # [op1607] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t1, t1, e16, m1, ta,ma  # [op1608] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.v v4, v1  # [op1609] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vwaddu.vx v6, v4, x0  # [op1610] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t1, 32  # [op1611] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t1, t1, e32, m1, ta,ma  # [op1612] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.v v1, v6  # [op1613] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t1, 65536  # [op1614] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmul.vx v1, v1, t1  # [op1615] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.v v4, v1  # [op1616] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t1, 32  # [op1617] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t1, t1, e16, m1, ta,ma  # [op1618] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t1, 32  # [op1619] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t1, t1, e32, m1, ta,ma  # [op1620] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsuxei64.v v4, (t0), v2  # [op1621] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1622] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e16, m1, ta,ma  # [op1623] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1624] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t0, a3, t0  # [op1625] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li t1, 32  # [op1626] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t1, s1, t1  # [op1627] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op1628] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv s1, t1  # [op1630] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv a3, t0  # [op1630] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk20_head  # [op1630] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk21_head:  # block chunk21_head
li s1, 32  # [op1631] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op1632] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc1633_true  # [op1633] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op1633] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op1633] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk21_exit  # [op1633] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc1633_true:  # [op1633] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk21_body  # [op1633] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk21_exit:  # block chunk21_exit
li t1, 0  # [op1634] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op1635] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op1635] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op1635] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk22_head  # [op1635] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk21_body:  # block chunk21_body
li s1, 32  # [op1636] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op1637] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op1638] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vid.v v1  # [op1640] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vadd.vx v1, v1, t0  # [op1641] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
    # [peephole-li] [op1642] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vwadd.vx v2, v1, x0  # [op1644] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
    # [peephole-li] [op1645] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vsetvli s1, s1, e64, m2, ta,ma  # [op1646] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li s1, 4  # [op1647] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vmul.vx v2, v2, s1  # [op1648] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li s1, 1408  # [op1649] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
ld a3, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
ld a3, 16(a3)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
add s1, a3, s1  # [op1650] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li a3, 32  # [op1651] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vsetvli a3, a3, e32, m1, ta,ma  # [op1652] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vluxei64.v v1, (s1), v2  # [op1653] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li s1, 32  # [op1654] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vid.v v2  # [op1656] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vadd.vx v2, v2, t0  # [op1657] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
    # [peephole-li] [op1658] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vwadd.vx v4, v2, x0  # [op1660] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
    # [peephole-li] [op1661] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vsetvli s1, s1, e64, m2, ta,ma  # [op1662] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li s1, 4  # [op1663] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vmul.vx v2, v4, s1  # [op1664] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li s1, 16832  # [op1665] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
ld a3, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
ld a3, 16(a3)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
add s1, a3, s1  # [op1666] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li a3, 32  # [op1667] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vsetvli a3, a3, e32, m1, ta,ma  # [op1668] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vluxei64.v v4, (s1), v2  # [op1669] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li s1, 32  # [op1670] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vmul.vv v1, v1, v4  # [op1672] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vid.v v2  # [op1673] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vadd.vx v2, v2, t0  # [op1674] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
    # [peephole-li] [op1675] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vwadd.vx v4, v2, x0  # [op1677] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
    # [peephole-li] [op1678] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vsetvli s1, s1, e64, m2, ta,ma  # [op1679] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li s1, 4  # [op1680] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vmul.vx v2, v4, s1  # [op1681] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li s1, 16960  # [op1682] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
ld a3, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
ld a3, 16(a3)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
add s1, a3, s1  # [op1683] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li a3, 32  # [op1684] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vsetvli a3, a3, e32, m1, ta,ma  # [op1685] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vsuxei64.v v1, (s1), v2  # [op1686] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li s1, 32  # [op1687] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
    # [peephole-li] [op1689] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op1690] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op1691] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op1692] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op1693] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk21_head  # [op1695] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk22_head:  # block chunk22_head
li s1, 512  # [op1696] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op1697] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc1698_true  # [op1698] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op1698] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op1698] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk22_exit  # [op1698] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc1698_true:  # [op1698] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk22_body  # [op1698] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk22_exit:  # block chunk22_exit
li t1, 0  # [op1699] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op1700] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op1700] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op1700] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk23_head  # [op1700] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk22_body:  # block chunk22_body
li s1, 32  # [op1701] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op1702] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op1703] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
vid.v v1  # [op1705] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
vadd.vx v1, v1, t0  # [op1706] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
li s1, 16  # [op1707] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
vmv.v.x v2, s1  # [op1708] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
vdiv.vv v1, v1, v2  # [op1709] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
li s1, 32  # [op1710] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
vwadd.vx v2, v1, x0  # [op1712] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
    # [peephole-li] [op1713] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
vsetvli s1, s1, e64, m2, ta,ma  # [op1714] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
li s1, 8  # [op1715] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
vmul.vx v2, v2, s1  # [op1716] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
li s1, 17088  # [op1717] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
ld a3, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
ld a3, 16(a3)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
add s1, a3, s1  # [op1718] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
li a3, 32  # [op1719] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
vluxei64.v v4, (s1), v2  # [op1721] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
li s1, 32  # [op1722] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
vsetvli s1, s1, e32, m1, ta,ma  # [op1723] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
li s1, 32  # [op1724] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op1725] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op1726] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op1727] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op1728] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk22_head  # [op1730] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk23_head:  # block chunk23_head
li s1, 32  # [op1731] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op1732] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc1733_true  # [op1733] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t2  # [op1733] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk23_exit  # [op1733] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc1733_true:  # [op1733] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk23_body  # [op1733] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk23_exit:  # block chunk23_exit
li t0, 0  # [op1734] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
j .Lstg24_head  # [op1735] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
.Lchunk23_body:  # block chunk23_body
li s1, 32  # [op1736] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op1737] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op1738] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vid.v v1  # [op1740] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vadd.vx v1, v1, t0  # [op1741] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
    # [peephole-li] [op1742] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vwadd.vx v2, v1, x0  # [op1744] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
    # [peephole-li] [op1745] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vsetvli s1, s1, e64, m2, ta,ma  # [op1746] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li s1, 4  # [op1747] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vmul.vx v2, v2, s1  # [op1748] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li s1, 1408  # [op1749] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
ld a3, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
ld a3, 16(a3)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
add s1, a3, s1  # [op1750] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li a3, 32  # [op1751] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vsetvli a3, a3, e32, m1, ta,ma  # [op1752] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vluxei64.v v1, (s1), v2  # [op1753] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li s1, 32  # [op1754] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vid.v v2  # [op1756] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vadd.vx v2, v2, t0  # [op1757] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
    # [peephole-li] [op1758] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vwadd.vx v4, v2, x0  # [op1760] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
    # [peephole-li] [op1761] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vsetvli s1, s1, e64, m2, ta,ma  # [op1762] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li s1, 4  # [op1763] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vmul.vx v2, v4, s1  # [op1764] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li s1, 21504  # [op1765] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
ld a3, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
ld a3, 16(a3)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
add s1, a3, s1  # [op1766] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li a3, 32  # [op1767] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vsetvli a3, a3, e32, m1, ta,ma  # [op1768] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vluxei64.v v4, (s1), v2  # [op1769] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li s1, 32  # [op1770] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vmslt.vv v1, v1, v4  # [op1772] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vid.v v2  # [op1773] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vadd.vx v2, v2, t0  # [op1774] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
    # [peephole-li] [op1775] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vwadd.vx v4, v2, x0  # [op1777] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
    # [peephole-li] [op1778] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vsetvli s1, s1, e64, m2, ta,ma  # [op1779] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li s1, 4  # [op1780] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vmul.vx v2, v4, s1  # [op1781] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li s1, 21632  # [op1782] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
ld a3, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
ld a3, 16(a3)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
add s1, a3, s1  # [op1783] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li a3, 32  # [op1784] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vsetvli a3, a3, e32, m1, ta,ma  # [op1785] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li a3, 1  # [op1786] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vmv.v.x v4, a3  # [op1787] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li a3, 0  # [op1788] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vmv.v.x v5, a3  # [op1789] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vmv1r.v v0, v1  # [op1790] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vmerge.vvm v1, v5, v4, v0  # [op1791] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vsuxei64.v v1, (s1), v2  # [op1792] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li s1, 32  # [op1793] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op1794] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op1795] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op1796] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op1797] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk23_head  # [op1799] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lstg24_head:  # block stg24_head
li s1, 512  # [op1800] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
slt s1, t0, s1  # [op1801] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
bne s1, zero, .Lbrc1802_true  # [op1802] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
j .Lstg24_exit  # [op1802] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
.Lbrc1802_true:  # [op1802] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
j .Lstg24_body  # [op1802] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
.Lstg24_body:  # block stg24_body
li s1, 32  # [op1803] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli s1, s1, e32, m1, ta,ma  # [op1804] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vid.v v1  # [op1805] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vadd.vx v1, v1, t0  # [op1806] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li s1, 16  # [op1807] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv.v.x v2, s1  # [op1808] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vdiv.vv v2, v1, v2  # [op1809] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li s1, 32  # [op1810] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv.v.x v3, s1  # [op1811] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vrem.vv v2, v2, v3  # [op1812] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li s1, 16  # [op1813] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv.v.x v3, s1  # [op1814] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vrem.vv v3, v1, v3  # [op1815] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li s1, 32  # [op1816] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vwadd.vx v4, v2, x0  # [op1818] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
    # [peephole-li] [op1819] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli s1, s1, e64, m2, ta,ma  # [op1820] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li s1, 4  # [op1821] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmul.vx v2, v4, s1  # [op1822] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li s1, 21632  # [op1823] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld a3, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld a3, 16(a3)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
add s1, a3, s1  # [op1824] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a3, 32  # [op1825] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli a3, a3, e32, m1, ta,ma  # [op1826] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vluxei64.v v4, (s1), v2  # [op1827] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li s1, 32  # [op1828] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vwadd.vx v2, v1, x0  # [op1830] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
    # [peephole-li] [op1831] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli s1, s1, e64, m2, ta,ma  # [op1832] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li s1, 4  # [op1833] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmul.vx v2, v2, s1  # [op1834] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li s1, 21888  # [op1835] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld a3, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld a3, 16(a3)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
add s1, a3, s1  # [op1836] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a3, 32  # [op1837] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli a3, a3, e32, m1, ta,ma  # [op1838] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsuxei64.v v4, (s1), v2  # [op1839] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li s1, 32  # [op1840] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
addw t0, t0, s1  # [op1841] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
j .Lstg24_head  # [op1842] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
.Lstg24_exit:  # block stg24_exit
li t0, 0  # [op1843] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv s1, t0  # [op1844] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv a3, t1  # [op1844] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk25_head  # [op1844] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk25_head:  # block chunk25_head
li t0, 512  # [op1845] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt t0, s1, t0  # [op1846] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne t0, zero, .Lbrc1847_true  # [op1847] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t2  # [op1847] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, a3  # [op1847] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk25_exit  # [op1847] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc1847_true:  # [op1847] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk25_body  # [op1847] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk25_exit:  # block chunk25_exit
li t0, 14656  # [op1848] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t1, 16(t1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s8, t1, t0  # [op1849] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t0, 30080  # [op1850] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t1, 16(t1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s9, t1, t0  # [op1851] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t0, 32128  # [op1852] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t1, 16(t1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s10, t1, t0  # [op1853] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t0, 256  # [op1854] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t1, 16(t1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a3, t1, t0  # [op1855] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t0, 0  # [op1856] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s11, 16  # [op1857] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lvrm26.head  # [op1858] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lchunk25_body:  # block chunk25_body
li t0, 32  # [op1859] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli t0, t0, e16, m1, ta,ma  # [op1860] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li t0, 32  # [op1861] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t0, t0, e32, m1, ta,ma  # [op1862] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vid.v v1  # [op1863] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vadd.vx v1, v1, s1  # [op1864] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 32  # [op1865] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vwadd.vx v2, v1, x0  # [op1867] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
    # [peephole-li] [op1868] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t0, t0, e64, m2, ta,ma  # [op1869] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 4  # [op1870] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmul.vx v2, v2, t0  # [op1871] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 21888  # [op1872] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld t1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld t1, 16(t1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
add t0, t1, t0  # [op1873] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t1, 32  # [op1874] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t1, t1, e32, m1, ta,ma  # [op1875] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vluxei64.v v1, (t0), v2  # [op1876] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 0  # [op1877] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv.v.x v2, t0  # [op1878] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmsne.vv v1, v1, v2  # [op1879] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 32  # [op1880] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t0, t0, e16, m1, ta,ma  # [op1881] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 32  # [op1882] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t0, t0, e32, m1, ta,ma  # [op1883] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vid.v v2  # [op1884] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vadd.vx v2, v2, s1  # [op1885] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 32  # [op1886] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vwadd.vx v4, v2, x0  # [op1888] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
    # [peephole-li] [op1889] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t0, t0, e64, m2, ta,ma  # [op1890] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 4  # [op1891] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmul.vx v2, v4, t0  # [op1892] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 23936  # [op1893] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld t1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld t1, 16(t1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
add t0, t1, t0  # [op1894] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t1, 32  # [op1895] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t1, t1, e32, m1, ta,ma  # [op1896] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vluxei64.v v4, (t0), v2  # [op1897] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 0  # [op1898] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv.v.x v2, t0  # [op1899] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmsne.vv v2, v4, v2  # [op1900] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 32  # [op1901] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t0, t0, e16, m1, ta,ma  # [op1902] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmand.mm v1, v1, v2  # [op1903] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 32  # [op1904] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t0, t0, e32, m1, ta,ma  # [op1905] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vid.v v2  # [op1906] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vadd.vx v2, v2, s1  # [op1907] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 32  # [op1908] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vwadd.vx v4, v2, x0  # [op1910] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
    # [peephole-li] [op1911] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t0, t0, e64, m2, ta,ma  # [op1912] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 4  # [op1913] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmul.vx v2, v4, t0  # [op1914] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 25984  # [op1915] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld t1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld t1, 16(t1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
add t0, t1, t0  # [op1916] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t1, 32  # [op1917] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t1, t1, e32, m1, ta,ma  # [op1918] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t1, 1  # [op1919] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv.v.x v4, t1  # [op1920] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t1, 0  # [op1921] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv.v.x v5, t1  # [op1922] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv1r.v v0, v1  # [op1923] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmerge.vvm v4, v5, v4, v0  # [op1924] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsuxei64.v v4, (t0), v2  # [op1925] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 32  # [op1926] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t0, t0, e16, m1, ta,ma  # [op1927] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 32  # [op1928] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t0, t0, e32, m1, ta,ma  # [op1929] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vid.v v2  # [op1930] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vadd.vx v2, v2, s1  # [op1931] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 32  # [op1932] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vwadd.vx v4, v2, x0  # [op1934] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
    # [peephole-li] [op1935] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t0, t0, e64, m2, ta,ma  # [op1936] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 4  # [op1937] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmul.vx v2, v4, t0  # [op1938] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 25984  # [op1939] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld t1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld t1, 16(t1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
add t0, t1, t0  # [op1940] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t1, 32  # [op1941] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t1, t1, e32, m1, ta,ma  # [op1942] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t1, 1  # [op1943] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv.v.x v4, t1  # [op1944] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t1, 0  # [op1945] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv.v.x v5, t1  # [op1946] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv1r.v v0, v1  # [op1947] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmerge.vvm v4, v5, v4, v0  # [op1948] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsuxei64.v v4, (t0), v2  # [op1949] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 32  # [op1950] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t0, t0, e16, m1, ta,ma  # [op1951] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 32  # [op1952] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e32, m1, ta,ma  # [op1953] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vid.v v2  # [op1954] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vadd.vx v2, v2, s1  # [op1955] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 16  # [op1956] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.x v3, t0  # [op1957] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vdiv.vv v2, v2, v3  # [op1958] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op1959] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vwadd.vx v4, v2, x0  # [op1961] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
    # [peephole-li] [op1962] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e64, m2, ta,ma  # [op1963] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 4  # [op1964] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmul.vx v2, v4, t0  # [op1965] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 16960  # [op1966] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
ld t1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
ld t1, 16(t1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add t0, t1, t0  # [op1967] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t1, 32  # [op1968] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t1, t1, e32, m1, ta,ma  # [op1969] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vluxei64.v v4, (t0), v2  # [op1970] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op1971] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e16, m1, ta,ma  # [op1972] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op1973] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e32, m1, ta,ma  # [op1974] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vid.v v2  # [op1975] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vadd.vx v2, v2, s1  # [op1976] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 16  # [op1977] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.x v3, t0  # [op1978] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vrem.vv v2, v2, v3  # [op1979] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op1980] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vwadd.vx v6, v2, x0  # [op1982] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
    # [peephole-li] [op1983] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e64, m2, ta,ma  # [op1984] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 4  # [op1985] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmul.vx v2, v6, t0  # [op1986] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 64  # [op1987] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
ld t1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
ld t1, 16(t1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add t0, t1, t0  # [op1988] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t1, 32  # [op1989] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t1, t1, e32, m1, ta,ma  # [op1990] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vluxei64.v v5, (t0), v2  # [op1991] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op1992] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e16, m1, ta,ma  # [op1993] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op1994] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e32, m1, ta,ma  # [op1995] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vadd.vv v2, v4, v5  # [op1996] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op1997] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e16, m1, ta,ma  # [op1998] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op1999] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e32, m1, ta,ma  # [op2000] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vwadd.vx v4, v2, x0  # [op2001] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op2002] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e64, m2, ta,ma  # [op2003] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 2  # [op2004] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmul.vx v2, v4, t0  # [op2005] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op2006] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e16, m1, ta,ma  # [op2007] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 37440  # [op2008] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
ld t1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
ld t1, 16(t1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add t0, t1, t0  # [op2009] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t1, 128  # [op2010] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add t1, t0, t1  # [op2011] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2012] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e32, m1, ta,ma  # [op2013] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 0  # [op2014] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.x v4, a5  # [op2015] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 1  # [op2016] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.x v5, a5  # [op2017] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv1r.v v0, v1  # [op2018] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmerge.vvm v4, v4, v5, v0  # [op2019] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vid.v v1  # [op2020] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vadd.vx v1, v1, s1  # [op2021] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2022] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vwadd.vx v6, v1, x0  # [op2024] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
    # [peephole-li] [op2025] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e64, m2, ta,ma  # [op2026] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 4  # [op2027] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmul.vx v6, v6, a5  # [op2028] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 28032  # [op2029] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
ld s8, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
ld s8, 16(s8)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a5, s8, a5  # [op2030] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s8, 32  # [op2031] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s8, s8, e32, m1, ta,ma  # [op2032] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vluxei64.v v5, (a5), v6  # [op2033] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2034] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.v v1, v5  # [op2036] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32767  # [op2037] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.x v5, a5  # [op2038] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 16  # [op2039] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.x v6, a5  # [op2040] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 1  # [op2041] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.x v7, a5  # [op2042] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vadd.vv v5, v1, v5  # [op2043] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsrl.vv v6, v1, v6  # [op2044] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vand.vv v6, v6, v7  # [op2045] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vadd.vv v5, v5, v6  # [op2046] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 2139095040  # [op2047] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.x v6, a5  # [op2048] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
    # [peephole-li] [op2049] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.x v7, a5  # [op2050] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 8388607  # [op2051] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.x v8, a5  # [op2052] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 0  # [op2053] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.x v9, a5  # [op2054] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vand.vv v6, v1, v6  # [op2055] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmseq.vv v6, v6, v7  # [op2056] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vand.vv v7, v1, v8  # [op2057] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmsne.vv v7, v7, v9  # [op2058] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmand.mm v6, v6, v7  # [op2059] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 4194304  # [op2060] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.x v7, a5  # [op2061] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vor.vv v1, v1, v7  # [op2062] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv1r.v v0, v6  # [op2063] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmerge.vvm v1, v5, v1, v0  # [op2064] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 16  # [op2065] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.x v5, a5  # [op2066] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsrl.vv v1, v1, v5  # [op2067] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.v v5, v1  # [op2068] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2069] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e16, m1, ta,ma  # [op2070] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vid.v v1  # [op2071] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 2  # [op2072] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.x v6, a5  # [op2073] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmul.vv v1, v1, v6  # [op2074] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vrgather.vv v6, v5, v1  # [op2075] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.v v1, v6  # [op2076] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2077] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e64, m2, ta,ma  # [op2078] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vadd.vx v6, v2, s3  # [op2079] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2080] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e32, m1, ta,ma  # [op2081] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 0  # [op2082] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.x v2, a5  # [op2083] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmsne.vv v2, v4, v2  # [op2084] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv1r.v v0, v2  # [op2085] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2086] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e64, m2, ta,ma  # [op2087] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 0  # [op2088] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.x v4, a5  # [op2089] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.x v2, t1  # [op2090] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsub.vv v6, v6, v2  # [op2091] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmerge.vvm v4, v4, v6, v0  # [op2092] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vadd.vv v2, v2, v4  # [op2093] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2094] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e16, m1, ta,ma  # [op2095] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2096] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e64, m2, ta,ma  # [op2097] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a5, v2  # [op2098] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s8, 0  # [op2099] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add s8, t0, s8  # [op2100] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s9, 32  # [op2101] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s9, s9, e16, m1, ta,ma  # [op2102] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s s9, v1  # [op2103] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh s9, 0(t1)  # [op2104] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2105] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a5, 0(a5)  # [op2106] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a5, 0(s8)  # [op2107] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2108] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e64, m2, ta,ma  # [op2109] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2110] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a5, v2  # [op2111] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s8, 2  # [op2112] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add s8, t0, s8  # [op2113] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s9, 32  # [op2114] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s9, s9, e16, m1, ta,ma  # [op2115] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s s9, v1  # [op2116] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh s9, 0(t1)  # [op2117] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2118] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a5, 0(a5)  # [op2119] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a5, 0(s8)  # [op2120] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2121] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e64, m2, ta,ma  # [op2122] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2123] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a5, v2  # [op2124] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s8, 4  # [op2125] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add s8, t0, s8  # [op2126] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s9, 32  # [op2127] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s9, s9, e16, m1, ta,ma  # [op2128] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s s9, v1  # [op2129] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh s9, 0(t1)  # [op2130] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2131] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a5, 0(a5)  # [op2132] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a5, 0(s8)  # [op2133] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2134] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e64, m2, ta,ma  # [op2135] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2136] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a5, v2  # [op2137] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s8, 6  # [op2138] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add s8, t0, s8  # [op2139] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s9, 32  # [op2140] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s9, s9, e16, m1, ta,ma  # [op2141] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s s9, v1  # [op2142] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh s9, 0(t1)  # [op2143] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2144] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a5, 0(a5)  # [op2145] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a5, 0(s8)  # [op2146] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2147] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e64, m2, ta,ma  # [op2148] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2149] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a5, v2  # [op2150] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s8, 8  # [op2151] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add s8, t0, s8  # [op2152] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s9, 32  # [op2153] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s9, s9, e16, m1, ta,ma  # [op2154] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s s9, v1  # [op2155] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh s9, 0(t1)  # [op2156] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2157] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a5, 0(a5)  # [op2158] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a5, 0(s8)  # [op2159] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2160] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e64, m2, ta,ma  # [op2161] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2162] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a5, v2  # [op2163] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s8, 10  # [op2164] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add s8, t0, s8  # [op2165] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s9, 32  # [op2166] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s9, s9, e16, m1, ta,ma  # [op2167] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s s9, v1  # [op2168] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh s9, 0(t1)  # [op2169] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2170] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a5, 0(a5)  # [op2171] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a5, 0(s8)  # [op2172] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2173] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e64, m2, ta,ma  # [op2174] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2175] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a5, v2  # [op2176] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s8, 12  # [op2177] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add s8, t0, s8  # [op2178] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s9, 32  # [op2179] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s9, s9, e16, m1, ta,ma  # [op2180] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s s9, v1  # [op2181] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh s9, 0(t1)  # [op2182] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2183] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a5, 0(a5)  # [op2184] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a5, 0(s8)  # [op2185] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2186] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e64, m2, ta,ma  # [op2187] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2188] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a5, v2  # [op2189] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s8, 14  # [op2190] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add s8, t0, s8  # [op2191] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s9, 32  # [op2192] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s9, s9, e16, m1, ta,ma  # [op2193] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s s9, v1  # [op2194] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh s9, 0(t1)  # [op2195] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2196] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a5, 0(a5)  # [op2197] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a5, 0(s8)  # [op2198] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2199] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e64, m2, ta,ma  # [op2200] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2201] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a5, v2  # [op2202] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s8, 16  # [op2203] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add s8, t0, s8  # [op2204] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s9, 32  # [op2205] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s9, s9, e16, m1, ta,ma  # [op2206] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s s9, v1  # [op2207] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh s9, 0(t1)  # [op2208] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2209] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a5, 0(a5)  # [op2210] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a5, 0(s8)  # [op2211] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2212] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e64, m2, ta,ma  # [op2213] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2214] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a5, v2  # [op2215] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s8, 18  # [op2216] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add s8, t0, s8  # [op2217] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s9, 32  # [op2218] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s9, s9, e16, m1, ta,ma  # [op2219] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s s9, v1  # [op2220] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh s9, 0(t1)  # [op2221] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2222] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a5, 0(a5)  # [op2223] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a5, 0(s8)  # [op2224] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2225] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e64, m2, ta,ma  # [op2226] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2227] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a5, v2  # [op2228] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s8, 20  # [op2229] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add s8, t0, s8  # [op2230] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s9, 32  # [op2231] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s9, s9, e16, m1, ta,ma  # [op2232] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s s9, v1  # [op2233] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh s9, 0(t1)  # [op2234] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2235] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a5, 0(a5)  # [op2236] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a5, 0(s8)  # [op2237] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2238] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e64, m2, ta,ma  # [op2239] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2240] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a5, v2  # [op2241] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s8, 22  # [op2242] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add s8, t0, s8  # [op2243] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s9, 32  # [op2244] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s9, s9, e16, m1, ta,ma  # [op2245] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s s9, v1  # [op2246] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh s9, 0(t1)  # [op2247] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2248] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a5, 0(a5)  # [op2249] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a5, 0(s8)  # [op2250] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2251] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e64, m2, ta,ma  # [op2252] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2253] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a5, v2  # [op2254] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s8, 24  # [op2255] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add s8, t0, s8  # [op2256] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s9, 32  # [op2257] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s9, s9, e16, m1, ta,ma  # [op2258] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s s9, v1  # [op2259] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh s9, 0(t1)  # [op2260] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2261] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a5, 0(a5)  # [op2262] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a5, 0(s8)  # [op2263] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2264] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e64, m2, ta,ma  # [op2265] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2266] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a5, v2  # [op2267] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s8, 26  # [op2268] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add s8, t0, s8  # [op2269] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s9, 32  # [op2270] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s9, s9, e16, m1, ta,ma  # [op2271] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s s9, v1  # [op2272] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh s9, 0(t1)  # [op2273] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2274] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a5, 0(a5)  # [op2275] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a5, 0(s8)  # [op2276] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2277] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e64, m2, ta,ma  # [op2278] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2279] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a5, v2  # [op2280] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s8, 28  # [op2281] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add s8, t0, s8  # [op2282] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s9, 32  # [op2283] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s9, s9, e16, m1, ta,ma  # [op2284] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s s9, v1  # [op2285] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh s9, 0(t1)  # [op2286] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2287] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a5, 0(a5)  # [op2288] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a5, 0(s8)  # [op2289] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2290] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e64, m2, ta,ma  # [op2291] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2292] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a5, v2  # [op2293] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s8, 30  # [op2294] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add s8, t0, s8  # [op2295] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s9, 32  # [op2296] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s9, s9, e16, m1, ta,ma  # [op2297] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s s9, v1  # [op2298] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh s9, 0(t1)  # [op2299] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2300] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a5, 0(a5)  # [op2301] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a5, 0(s8)  # [op2302] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2303] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e64, m2, ta,ma  # [op2304] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2305] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a5, v2  # [op2306] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s8, 32  # [op2307] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add s8, t0, s8  # [op2308] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s9, 32  # [op2309] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s9, s9, e16, m1, ta,ma  # [op2310] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s s9, v1  # [op2311] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh s9, 0(t1)  # [op2312] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2313] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a5, 0(a5)  # [op2314] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a5, 0(s8)  # [op2315] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2316] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e64, m2, ta,ma  # [op2317] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2318] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a5, v2  # [op2319] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s8, 34  # [op2320] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add s8, t0, s8  # [op2321] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s9, 32  # [op2322] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s9, s9, e16, m1, ta,ma  # [op2323] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s s9, v1  # [op2324] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh s9, 0(t1)  # [op2325] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2326] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a5, 0(a5)  # [op2327] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a5, 0(s8)  # [op2328] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2329] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e64, m2, ta,ma  # [op2330] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2331] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a5, v2  # [op2332] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s8, 36  # [op2333] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add s8, t0, s8  # [op2334] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s9, 32  # [op2335] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s9, s9, e16, m1, ta,ma  # [op2336] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s s9, v1  # [op2337] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh s9, 0(t1)  # [op2338] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2339] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a5, 0(a5)  # [op2340] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a5, 0(s8)  # [op2341] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2342] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e64, m2, ta,ma  # [op2343] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2344] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a5, v2  # [op2345] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s8, 38  # [op2346] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add s8, t0, s8  # [op2347] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s9, 32  # [op2348] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s9, s9, e16, m1, ta,ma  # [op2349] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s s9, v1  # [op2350] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh s9, 0(t1)  # [op2351] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2352] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a5, 0(a5)  # [op2353] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a5, 0(s8)  # [op2354] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2355] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e64, m2, ta,ma  # [op2356] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2357] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a5, v2  # [op2358] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s8, 40  # [op2359] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add s8, t0, s8  # [op2360] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s9, 32  # [op2361] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s9, s9, e16, m1, ta,ma  # [op2362] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s s9, v1  # [op2363] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh s9, 0(t1)  # [op2364] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2365] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a5, 0(a5)  # [op2366] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a5, 0(s8)  # [op2367] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2368] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e64, m2, ta,ma  # [op2369] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2370] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a5, v2  # [op2371] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s8, 42  # [op2372] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add s8, t0, s8  # [op2373] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s9, 32  # [op2374] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s9, s9, e16, m1, ta,ma  # [op2375] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s s9, v1  # [op2376] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh s9, 0(t1)  # [op2377] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2378] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a5, 0(a5)  # [op2379] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a5, 0(s8)  # [op2380] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2381] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e64, m2, ta,ma  # [op2382] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2383] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a5, v2  # [op2384] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s8, 44  # [op2385] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add s8, t0, s8  # [op2386] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s9, 32  # [op2387] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s9, s9, e16, m1, ta,ma  # [op2388] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s s9, v1  # [op2389] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh s9, 0(t1)  # [op2390] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2391] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a5, 0(a5)  # [op2392] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a5, 0(s8)  # [op2393] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2394] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e64, m2, ta,ma  # [op2395] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2396] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a5, v2  # [op2397] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s8, 46  # [op2398] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add s8, t0, s8  # [op2399] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s9, 32  # [op2400] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s9, s9, e16, m1, ta,ma  # [op2401] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s s9, v1  # [op2402] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh s9, 0(t1)  # [op2403] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2404] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a5, 0(a5)  # [op2405] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a5, 0(s8)  # [op2406] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2407] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e64, m2, ta,ma  # [op2408] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2409] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a5, v2  # [op2410] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s8, 48  # [op2411] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add s8, t0, s8  # [op2412] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s9, 32  # [op2413] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s9, s9, e16, m1, ta,ma  # [op2414] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s s9, v1  # [op2415] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh s9, 0(t1)  # [op2416] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2417] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a5, 0(a5)  # [op2418] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a5, 0(s8)  # [op2419] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2420] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e64, m2, ta,ma  # [op2421] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2422] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a5, v2  # [op2423] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s8, 50  # [op2424] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add s8, t0, s8  # [op2425] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s9, 32  # [op2426] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s9, s9, e16, m1, ta,ma  # [op2427] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s s9, v1  # [op2428] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh s9, 0(t1)  # [op2429] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2430] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a5, 0(a5)  # [op2431] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a5, 0(s8)  # [op2432] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2433] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e64, m2, ta,ma  # [op2434] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2435] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a5, v2  # [op2436] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s8, 52  # [op2437] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add s8, t0, s8  # [op2438] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s9, 32  # [op2439] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s9, s9, e16, m1, ta,ma  # [op2440] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s s9, v1  # [op2441] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh s9, 0(t1)  # [op2442] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2443] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a5, 0(a5)  # [op2444] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a5, 0(s8)  # [op2445] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2446] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e64, m2, ta,ma  # [op2447] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2448] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a5, v2  # [op2449] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s8, 54  # [op2450] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add s8, t0, s8  # [op2451] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s9, 32  # [op2452] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s9, s9, e16, m1, ta,ma  # [op2453] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s s9, v1  # [op2454] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh s9, 0(t1)  # [op2455] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2456] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a5, 0(a5)  # [op2457] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a5, 0(s8)  # [op2458] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2459] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e64, m2, ta,ma  # [op2460] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2461] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a5, v2  # [op2462] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s8, 56  # [op2463] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add s8, t0, s8  # [op2464] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s9, 32  # [op2465] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s9, s9, e16, m1, ta,ma  # [op2466] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s s9, v1  # [op2467] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh s9, 0(t1)  # [op2468] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2469] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a5, 0(a5)  # [op2470] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a5, 0(s8)  # [op2471] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2472] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e64, m2, ta,ma  # [op2473] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2474] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a5, v2  # [op2475] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s8, 58  # [op2476] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add s8, t0, s8  # [op2477] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s9, 32  # [op2478] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s9, s9, e16, m1, ta,ma  # [op2479] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s s9, v1  # [op2480] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh s9, 0(t1)  # [op2481] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2482] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a5, 0(a5)  # [op2483] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a5, 0(s8)  # [op2484] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2485] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e64, m2, ta,ma  # [op2486] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2487] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a5, v2  # [op2488] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s8, 60  # [op2489] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add s8, t0, s8  # [op2490] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s9, 32  # [op2491] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s9, s9, e16, m1, ta,ma  # [op2492] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s s9, v1  # [op2493] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh s9, 0(t1)  # [op2494] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2495] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a5, 0(a5)  # [op2496] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a5, 0(s8)  # [op2497] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a5, 32  # [op2498] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a5, a5, e64, m2, ta,ma  # [op2499] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2500] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a5, v2  # [op2501] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s8, 62  # [op2502] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add s8, t0, s8  # [op2503] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s9, 32  # [op2504] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s9, s9, e16, m1, ta,ma  # [op2505] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s s9, v1  # [op2506] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh s9, 0(t1)  # [op2507] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2508] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu t1, 0(a5)  # [op2509] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh t1, 0(s8)  # [op2510] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t1, 32  # [op2511] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t1, t1, e64, m2, ta,ma  # [op2512] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2513] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t1, 32  # [op2514] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t1, t1, e16, m1, ta,ma  # [op2515] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vle16.v v1, 0(t0)  # [op2516] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op2517] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e32, m1, ta,ma  # [op2518] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vid.v v2  # [op2519] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vadd.vx v2, v2, s1  # [op2520] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op2521] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vwadd.vx v4, v2, x0  # [op2523] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
    # [peephole-li] [op2524] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e64, m2, ta,ma  # [op2525] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 4  # [op2526] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmul.vx v2, v4, t0  # [op2527] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 30080  # [op2528] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
ld t1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
ld t1, 16(t1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add t0, t1, t0  # [op2529] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t1, 32  # [op2530] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t1, t1, e16, m1, ta,ma  # [op2531] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.v v4, v1  # [op2532] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vwaddu.vx v6, v4, x0  # [op2533] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t1, 32  # [op2534] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t1, t1, e32, m1, ta,ma  # [op2535] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.v v1, v6  # [op2536] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t1, 65536  # [op2537] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmul.vx v1, v1, t1  # [op2538] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.v v4, v1  # [op2539] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t1, 32  # [op2540] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t1, t1, e16, m1, ta,ma  # [op2541] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t1, 32  # [op2542] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t1, t1, e32, m1, ta,ma  # [op2543] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsuxei64.v v4, (t0), v2  # [op2544] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op2545] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e16, m1, ta,ma  # [op2546] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op2547] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t0, a3, t0  # [op2548] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li t1, 32  # [op2549] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t1, s1, t1  # [op2550] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op2551] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv s1, t1  # [op2553] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv a3, t0  # [op2553] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk25_head  # [op2553] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lvrm26.head:  # block vrm26.head
sd t0, 144(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t0, 144(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt t1, t0, s11  # [op2554] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t0, 144(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
bne t1, zero, .Lbrc2555_true  # [op2555] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lvrm26.exit  # [op2555] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lbrc2555_true:  # [op2555] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lvrm26.body  # [op2555] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lvrm26.body:  # block vrm26.body
sd t0, 144(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t0, 0  # [op2556] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t3, 16  # [op2557] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lvrc27.head  # [op2558] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lvrm26.exit:  # block vrm26.exit
addw t1, a1, s7  # [op2559] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
li s1, 32128  # [op2560] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
li a1, 256  # [op2561] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
li t0, 0  # [op2562] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
li a3, 256  # [op2563] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
li a5, 32  # [op2564] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
j .Lmcarry29.head  # [op2565] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
.Lvrc27.head:  # block vrc27.head
sd t0, 152(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t0, 152(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt t1, t0, t3  # [op2566] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t0, 152(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
bne t1, zero, .Lbrc2567_true  # [op2567] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lvrc27.exit  # [op2567] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lbrc2567_true:  # [op2567] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lvrc27.body  # [op2567] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lvrc27.body:  # block vrc27.body
sd t0, 152(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t0, 128  # [op2568] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t1, 144(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul t0, t1, t0  # [op2569] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s1, s8, t0  # [op2570] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t0, 4  # [op2571] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t1, 152(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul t1, t1, t0  # [op2572] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t4, s9, t1  # [op2573] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t1, 64  # [op2574] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a5, 144(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul a5, a5, t1  # [op2575] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t5, 152(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul t0, t5, t0  # [op2576] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t0, a5, t0  # [op2577] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a5, s10, t0  # [op2578] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t5, 16  # [op2579] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vsetvli t5, t5, e32, m1, ta,ma  # [op2580] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t5, 0  # [op2581] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv.v.x v1, t5  # [op2582] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t5, a3, t0  # [op2583] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t6, 16  # [op2584] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle32.v v1, 0(t5)  # [op2586] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t0, a3, t0  # [op2587] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t0, t0, t1  # [op2588] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t1, 16  # [op2589] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle32.v v2, 0(t0)  # [op2591] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t0, 0  # [op2592] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t5, 32  # [op2593] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mv t1, t0  # [op2594] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mv t0, s1  # [op2594] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mv s1, t4  # [op2594] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lvrk28.head  # [op2594] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lvrc27.exit:  # block vrc27.exit
li t0, 2  # [op2595] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t1, 144(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t0, t1, t0  # [op2596] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lvrm26.head  # [op2597] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lvrk28.head:  # block vrk28.head
slt t4, t1, t5  # [op2598] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
bne t4, zero, .Lbrc2599_true  # [op2599] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sd t0, 96(sp)  # [op2599] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mv t0, t1  # [op2599] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t1, 96(sp)  # [op2599] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lvrk28.exit  # [op2599] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lbrc2599_true:  # [op2599] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lvrk28.body  # [op2599] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lvrk28.body:  # block vrk28.body
li t4, 16  # [op2600] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vsetvli t4, t4, e32, m1, ta,ma  # [op2601] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle32.v v3, 0(s1)  # [op2602] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
lw t4, 0(t0)  # [op2603] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t6, 16  # [op2604] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv.v.x v4, t4  # [op2606] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vfmacc.vv v1, v3, v4  # [op2607] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t4, 128  # [op2608] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t4, t0, t4  # [op2609] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
lw t4, 0(t4)  # [op2610] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
    # [peephole-li] [op2611] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv.v.x v4, t4  # [op2613] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vfmacc.vv v2, v3, v4  # [op2614] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t4, 1  # [op2615] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t1, t1, t4  # [op2616] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t4, 4  # [op2617] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t0, t0, t4  # [op2618] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t4, 64  # [op2619] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s1, s1, t4  # [op2620] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lvrk28.head  # [op2621] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lvrk28.exit:  # block vrk28.exit
li t0, 16  # [op2622] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vsetvli t0, t0, e32, m1, ta,ma  # [op2623] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse32.v v1, 0(a5)  # [op2624] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t0, 64  # [op2625] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t0, a5, t0  # [op2626] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t1, 16  # [op2627] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse32.v v2, 0(t0)  # [op2629] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t0, 16  # [op2630] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t1, 152(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t0, t1, t0  # [op2631] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lvrc27.head  # [op2632] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lmcarry29.head:  # block mcarry29.head
slt s8, t0, a3  # [op2633] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
bne s8, zero, .Lbrc2634_true  # [op2634] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
j .Lmcarry29.exit  # [op2634] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
.Lbrc2634_true:  # [op2634] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
j .Lmcarry29.body  # [op2634] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
.Lmcarry29.body:  # block mcarry29.body
ld s8, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
ld s8, 16(s8)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
add s8, s8, s1  # [op2635] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
ld s9, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
ld s9, 16(s9)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
add s9, s9, a1  # [op2636] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
li s10, 32  # [op2637] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
vsetvli s10, s10, e32, m1, ta,ma  # [op2638] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
vid.v v1  # [op2639] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
vadd.vx v1, v1, t0  # [op2640] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
li s10, 32  # [op2641] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
vwadd.vx v2, v1, x0  # [op2643] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
    # [peephole-li] [op2644] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
vsetvli s10, s10, e64, m2, ta,ma  # [op2645] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
li s10, 4  # [op2646] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
vmul.vx v2, v2, s10  # [op2647] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
li s10, 32  # [op2648] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
vsetvli s10, s10, e32, m1, ta,ma  # [op2649] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
vluxei64.v v1, (s8), v2  # [op2650] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
vsuxei64.v v1, (s9), v2  # [op2651] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
li s8, 16  # [op2652] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
vsetvli s8, s8, e32, m1, ta,ma  # [op2653] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
addw t0, t0, a5  # [op2654] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
j .Lmcarry29.head  # [op2655] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
.Lmcarry29.exit:  # block mcarry29.exit
mv a1, t1  # [op2656] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
j .Lmloop15.head  # [op2656] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
.Lchunk30_head:  # block chunk30_head
li s1, 16  # [op2657] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op2658] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc2659_true  # [op2659] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op2659] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op2659] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk30_exit  # [op2659] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc2659_true:  # [op2659] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk30_body  # [op2659] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk30_exit:  # block chunk30_exit
li t1, 0  # [op2660] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op2661] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op2661] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op2661] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk31_head  # [op2661] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk30_body:  # block chunk30_body
li s1, 16  # [op2662] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op2663] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 16  # [op2664] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vmv.v.x v1, a2  # [op2666] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vid.v v2  # [op2667] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vadd.vx v2, v2, t0  # [op2668] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
    # [peephole-li] [op2669] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vwadd.vx v4, v2, x0  # [op2671] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
    # [peephole-li] [op2672] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vsetvli s1, s1, e64, m2, ta,ma  # [op2673] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
li s1, 4  # [op2674] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vmul.vx v2, v4, s1  # [op2675] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
li s1, 0  # [op2676] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
add s1, a1, s1  # [op2677] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
li a1, 16  # [op2678] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vsetvli a1, a1, e32, m1, ta,ma  # [op2679] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vluxei64.v v4, (s1), v2  # [op2680] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
li s1, 16  # [op2681] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vmul.vv v1, v4, v1  # [op2683] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vid.v v2  # [op2684] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vadd.vx v2, v2, t0  # [op2685] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
    # [peephole-li] [op2686] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vwadd.vx v4, v2, x0  # [op2688] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
    # [peephole-li] [op2689] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vsetvli s1, s1, e64, m2, ta,ma  # [op2690] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
li s1, 4  # [op2691] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vmul.vx v2, v4, s1  # [op2692] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
li s1, 33152  # [op2693] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
add s1, a1, s1  # [op2694] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
li a1, 16  # [op2695] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vsetvli a1, a1, e32, m1, ta,ma  # [op2696] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vsuxei64.v v1, (s1), v2  # [op2697] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
li s1, 16  # [op2698] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
    # [peephole-li] [op2700] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op2701] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op2702] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op2703] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op2704] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk30_head  # [op2706] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk31_head:  # block chunk31_head
li s1, 256  # [op2707] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op2708] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc2709_true  # [op2709] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t2  # [op2709] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk31_exit  # [op2709] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc2709_true:  # [op2709] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk31_body  # [op2709] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk31_exit:  # block chunk31_exit
li t0, 0  # [op2710] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
j .Lstg32_head  # [op2711] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
.Lchunk31_body:  # block chunk31_body
li s1, 32  # [op2712] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op2713] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op2714] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
vid.v v1  # [op2716] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
vadd.vx v1, v1, t0  # [op2717] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
li s1, 16  # [op2718] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
vmv.v.x v2, s1  # [op2719] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
vdiv.vv v1, v1, v2  # [op2720] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
li s1, 32  # [op2721] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
vwadd.vx v2, v1, x0  # [op2723] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
    # [peephole-li] [op2724] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
vsetvli s1, s1, e64, m2, ta,ma  # [op2725] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
li s1, 8  # [op2726] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
vmul.vx v2, v2, s1  # [op2727] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
li s1, 33216  # [op2728] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
add s1, a1, s1  # [op2729] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
li a1, 32  # [op2730] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
vluxei64.v v4, (s1), v2  # [op2732] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
li s1, 32  # [op2733] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
vsetvli s1, s1, e32, m1, ta,ma  # [op2734] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
li s1, 32  # [op2735] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op2736] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op2737] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op2738] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op2739] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk31_head  # [op2741] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lstg32_head:  # block stg32_head
li s1, 256  # [op2742] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
slt s1, t0, s1  # [op2743] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
bne s1, zero, .Lbrc2744_true  # [op2744] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
j .Lstg32_exit  # [op2744] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
.Lbrc2744_true:  # [op2744] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
j .Lstg32_body  # [op2744] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
.Lstg32_body:  # block stg32_body
li s1, 32  # [op2745] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli s1, s1, e32, m1, ta,ma  # [op2746] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vid.v v1  # [op2747] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vadd.vx v1, v1, t0  # [op2748] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 16  # [op2749] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmv.v.x v2, s1  # [op2750] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vdiv.vv v2, v1, v2  # [op2751] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op2752] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmv.v.x v3, s1  # [op2753] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vrem.vv v2, v2, v3  # [op2754] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op2755] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmv.v.x v3, s1  # [op2756] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vrem.vv v3, v1, v3  # [op2757] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 32  # [op2758] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vwadd.vx v4, v2, x0  # [op2760] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op2761] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli s1, s1, e64, m2, ta,ma  # [op2762] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 4  # [op2763] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmul.vx v2, v4, s1  # [op2764] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 6144  # [op2765] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
add s1, a1, s1  # [op2766] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li a1, 32  # [op2767] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli a1, a1, e32, m1, ta,ma  # [op2768] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vluxei64.v v4, (s1), v2  # [op2769] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 32  # [op2770] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vwadd.vx v2, v1, x0  # [op2772] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op2773] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli s1, s1, e64, m2, ta,ma  # [op2774] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 4  # [op2775] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmul.vx v2, v2, s1  # [op2776] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 35392  # [op2777] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
add s1, a1, s1  # [op2778] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li a1, 32  # [op2779] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli a1, a1, e32, m1, ta,ma  # [op2780] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsuxei64.v v4, (s1), v2  # [op2781] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 32  # [op2782] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
addw t0, t0, s1  # [op2783] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
j .Lstg32_head  # [op2784] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
.Lstg32_exit:  # block stg32_exit
li t0, 0  # [op2785] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
j .Lstg33_head  # [op2786] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
.Lstg33_head:  # block stg33_head
li s1, 256  # [op2787] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
slt s1, t0, s1  # [op2788] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
bne s1, zero, .Lbrc2789_true  # [op2789] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
j .Lstg33_exit  # [op2789] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
.Lbrc2789_true:  # [op2789] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
j .Lstg33_body  # [op2789] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
.Lstg33_body:  # block stg33_body
li s1, 32  # [op2790] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli s1, s1, e32, m1, ta,ma  # [op2791] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vid.v v1  # [op2792] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vadd.vx v1, v1, t0  # [op2793] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 16  # [op2794] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmv.v.x v2, s1  # [op2795] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vdiv.vv v2, v1, v2  # [op2796] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op2797] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmv.v.x v3, s1  # [op2798] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vrem.vv v2, v2, v3  # [op2799] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op2800] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmv.v.x v2, s1  # [op2801] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vrem.vv v2, v1, v2  # [op2802] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 32  # [op2803] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vwadd.vx v4, v2, x0  # [op2805] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op2806] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli s1, s1, e64, m2, ta,ma  # [op2807] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 4  # [op2808] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmul.vx v2, v4, s1  # [op2809] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 21824  # [op2810] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
add s1, a1, s1  # [op2811] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li a1, 32  # [op2812] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli a1, a1, e32, m1, ta,ma  # [op2813] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vluxei64.v v4, (s1), v2  # [op2814] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 32  # [op2815] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vwadd.vx v2, v1, x0  # [op2817] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op2818] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli s1, s1, e64, m2, ta,ma  # [op2819] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 4  # [op2820] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmul.vx v2, v2, s1  # [op2821] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 36416  # [op2822] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
add s1, a1, s1  # [op2823] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li a1, 32  # [op2824] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli a1, a1, e32, m1, ta,ma  # [op2825] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsuxei64.v v4, (s1), v2  # [op2826] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 32  # [op2827] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
addw t0, t0, s1  # [op2828] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
j .Lstg33_head  # [op2829] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
.Lstg33_exit:  # block stg33_exit
li t0, 0  # [op2830] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv s1, t1  # [op2831] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t0  # [op2831] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk34_head  # [op2831] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk34_head:  # block chunk34_head
li t0, 256  # [op2832] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt t0, t1, t0  # [op2833] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne t0, zero, .Lbrc2834_true  # [op2834] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op2834] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, s1  # [op2834] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk34_exit  # [op2834] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc2834_true:  # [op2834] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk34_body  # [op2834] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk34_exit:  # block chunk34_exit
mv t1, t0  # [op2835] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t2  # [op2835] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lprog_next  # [op2835] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk34_body:  # block chunk34_body
li t0, 32  # [op2836] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli t0, t0, e16, m1, ta,ma  # [op2837] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li t0, 32  # [op2838] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli t0, t0, e32, m1, ta,ma  # [op2839] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vid.v v1  # [op2840] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vadd.vx v1, v1, t1  # [op2841] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li t0, 32  # [op2842] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vwadd.vx v2, v1, x0  # [op2844] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op2845] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli t0, t0, e64, m2, ta,ma  # [op2846] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li t0, 4  # [op2847] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmul.vx v2, v2, t0  # [op2848] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li t0, 35392  # [op2849] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
add t0, a1, t0  # [op2850] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li a1, 32  # [op2851] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli a1, a1, e32, m1, ta,ma  # [op2852] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vluxei64.v v1, (t0), v2  # [op2853] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li t0, 0  # [op2854] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmv.v.x v2, t0  # [op2855] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmsne.vv v1, v1, v2  # [op2856] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li t0, 32  # [op2857] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli t0, t0, e16, m1, ta,ma  # [op2858] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li t0, 32  # [op2859] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli t0, t0, e32, m1, ta,ma  # [op2860] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vid.v v2  # [op2861] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vadd.vx v2, v2, t1  # [op2862] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li t0, 32  # [op2863] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vwadd.vx v4, v2, x0  # [op2865] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op2866] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli t0, t0, e64, m2, ta,ma  # [op2867] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li t0, 4  # [op2868] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmul.vx v2, v4, t0  # [op2869] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li t0, 36416  # [op2870] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
add t0, a1, t0  # [op2871] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li a1, 32  # [op2872] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli a1, a1, e32, m1, ta,ma  # [op2873] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vluxei64.v v4, (t0), v2  # [op2874] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li t0, 0  # [op2875] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmv.v.x v2, t0  # [op2876] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmsne.vv v2, v4, v2  # [op2877] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li t0, 32  # [op2878] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli t0, t0, e16, m1, ta,ma  # [op2879] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmand.mm v2, v1, v2  # [op2880] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li t0, 32  # [op2881] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e32, m1, ta,ma  # [op2882] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vid.v v1  # [op2883] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vadd.vx v1, v1, t1  # [op2884] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op2885] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vwadd.vx v4, v1, x0  # [op2887] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
    # [peephole-li] [op2888] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e64, m2, ta,ma  # [op2889] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 4  # [op2890] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmul.vx v4, v4, t0  # [op2891] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 256  # [op2892] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add t0, a1, t0  # [op2893] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a1, 32  # [op2894] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli a1, a1, e32, m1, ta,ma  # [op2895] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vluxei64.v v3, (t0), v4  # [op2896] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op2897] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e16, m1, ta,ma  # [op2898] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op2899] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e32, m1, ta,ma  # [op2900] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.v.v v1, v3  # [op2901] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 32767  # [op2902] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.v.x v3, t0  # [op2903] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 16  # [op2904] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.v.x v4, t0  # [op2905] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 1  # [op2906] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.v.x v5, t0  # [op2907] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vadd.vv v3, v1, v3  # [op2908] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsrl.vv v4, v1, v4  # [op2909] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vand.vv v4, v4, v5  # [op2910] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vadd.vv v3, v3, v4  # [op2911] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 2139095040  # [op2912] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.v.x v4, t0  # [op2913] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
    # [peephole-li] [op2914] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.v.x v5, t0  # [op2915] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 8388607  # [op2916] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.v.x v6, t0  # [op2917] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 0  # [op2918] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.v.x v7, t0  # [op2919] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vand.vv v4, v1, v4  # [op2920] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmseq.vv v4, v4, v5  # [op2921] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vand.vv v5, v1, v6  # [op2922] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmsne.vv v5, v5, v7  # [op2923] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmand.mm v4, v4, v5  # [op2924] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 4194304  # [op2925] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.v.x v5, t0  # [op2926] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vor.vv v1, v1, v5  # [op2927] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv1r.v v0, v4  # [op2928] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmerge.vvm v1, v3, v1, v0  # [op2929] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 16  # [op2930] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.v.x v3, t0  # [op2931] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsrl.vv v1, v1, v3  # [op2932] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.v.v v3, v1  # [op2933] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op2934] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e16, m1, ta,ma  # [op2935] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vid.v v1  # [op2936] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 2  # [op2937] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.v.x v4, t0  # [op2938] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmul.vv v1, v1, v4  # [op2939] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vrgather.vv v4, v3, v1  # [op2940] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.v.v v1, v4  # [op2941] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op2942] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e32, m1, ta,ma  # [op2943] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vid.v v3  # [op2944] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vadd.vx v3, v3, t1  # [op2945] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 16  # [op2946] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.v.x v4, t0  # [op2947] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vdiv.vv v3, v3, v4  # [op2948] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op2949] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vwadd.vx v4, v3, x0  # [op2951] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
    # [peephole-li] [op2952] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e64, m2, ta,ma  # [op2953] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 4  # [op2954] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmul.vx v4, v4, t0  # [op2955] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 33152  # [op2956] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add t0, a1, t0  # [op2957] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a1, 32  # [op2958] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli a1, a1, e32, m1, ta,ma  # [op2959] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vluxei64.v v3, (t0), v4  # [op2960] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op2961] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e16, m1, ta,ma  # [op2962] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op2963] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e32, m1, ta,ma  # [op2964] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vid.v v4  # [op2965] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vadd.vx v4, v4, t1  # [op2966] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 16  # [op2967] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.v.x v5, t0  # [op2968] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vrem.vv v4, v4, v5  # [op2969] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op2970] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vwadd.vx v6, v4, x0  # [op2972] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
    # [peephole-li] [op2973] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e64, m2, ta,ma  # [op2974] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 4  # [op2975] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmul.vx v4, v6, t0  # [op2976] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 64  # [op2977] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add t0, a1, t0  # [op2978] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a1, 32  # [op2979] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli a1, a1, e32, m1, ta,ma  # [op2980] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vluxei64.v v6, (t0), v4  # [op2981] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op2982] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e16, m1, ta,ma  # [op2983] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op2984] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e32, m1, ta,ma  # [op2985] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vadd.vv v3, v3, v6  # [op2986] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op2987] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e16, m1, ta,ma  # [op2988] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op2989] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e32, m1, ta,ma  # [op2990] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vwadd.vx v4, v3, x0  # [op2991] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op2992] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e64, m2, ta,ma  # [op2993] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 2  # [op2994] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmul.vx v4, v4, t0  # [op2995] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op2996] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e16, m1, ta,ma  # [op2997] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 37440  # [op2998] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add t0, a1, t0  # [op2999] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a1, 128  # [op3000] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a1, t0, a1  # [op3001] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 32  # [op3002] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vse16.v v1, 0(t0)  # [op3004] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
    # [peephole-li] [op3005] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli a3, a3, e32, m1, ta,ma  # [op3006] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 0  # [op3007] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.v.x v1, a3  # [op3008] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 1  # [op3009] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.v.x v3, a3  # [op3010] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv1r.v v0, v2  # [op3011] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmerge.vvm v1, v1, v3, v0  # [op3012] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 32  # [op3013] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli a3, a3, e64, m2, ta,ma  # [op3014] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vadd.vx v6, v4, s4  # [op3015] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 32  # [op3016] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli a3, a3, e32, m1, ta,ma  # [op3017] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 0  # [op3018] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.v.x v3, a3  # [op3019] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmsne.vv v1, v1, v3  # [op3020] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv1r.v v0, v1  # [op3021] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 32  # [op3022] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli a3, a3, e64, m2, ta,ma  # [op3023] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 0  # [op3024] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.v.x v8, a3  # [op3025] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.v.x v4, a1  # [op3026] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsub.vv v6, v6, v4  # [op3027] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmerge.vvm v6, v8, v6, v0  # [op3028] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vadd.vv v4, v4, v6  # [op3029] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a1, 32  # [op3030] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli a1, a1, e16, m1, ta,ma  # [op3031] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a1, 32  # [op3032] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli a1, a1, e64, m2, ta,ma  # [op3033] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v4  # [op3034] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
    # [peephole-li] [op3035] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a3, t0, a3  # [op3036] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a3, 0(a3)  # [op3037] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a3, 0(a1)  # [op3038] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v4, v4, 1  # [op3039] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v4  # [op3040] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 2  # [op3041] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a3, t0, a3  # [op3042] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a3, 0(a3)  # [op3043] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a3, 0(a1)  # [op3044] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v4, v4, 1  # [op3045] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v4  # [op3046] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 4  # [op3047] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a3, t0, a3  # [op3048] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a3, 0(a3)  # [op3049] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a3, 0(a1)  # [op3050] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v4, v4, 1  # [op3051] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v4  # [op3052] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 6  # [op3053] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a3, t0, a3  # [op3054] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a3, 0(a3)  # [op3055] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a3, 0(a1)  # [op3056] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v4, v4, 1  # [op3057] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v4  # [op3058] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 8  # [op3059] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a3, t0, a3  # [op3060] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a3, 0(a3)  # [op3061] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a3, 0(a1)  # [op3062] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v4, v4, 1  # [op3063] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v4  # [op3064] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 10  # [op3065] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a3, t0, a3  # [op3066] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a3, 0(a3)  # [op3067] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a3, 0(a1)  # [op3068] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v4, v4, 1  # [op3069] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v4  # [op3070] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 12  # [op3071] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a3, t0, a3  # [op3072] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a3, 0(a3)  # [op3073] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a3, 0(a1)  # [op3074] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v4, v4, 1  # [op3075] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v4  # [op3076] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 14  # [op3077] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a3, t0, a3  # [op3078] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a3, 0(a3)  # [op3079] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a3, 0(a1)  # [op3080] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v4, v4, 1  # [op3081] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v4  # [op3082] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 16  # [op3083] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a3, t0, a3  # [op3084] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a3, 0(a3)  # [op3085] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a3, 0(a1)  # [op3086] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v4, v4, 1  # [op3087] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v4  # [op3088] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 18  # [op3089] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a3, t0, a3  # [op3090] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a3, 0(a3)  # [op3091] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a3, 0(a1)  # [op3092] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v4, v4, 1  # [op3093] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v4  # [op3094] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 20  # [op3095] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a3, t0, a3  # [op3096] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a3, 0(a3)  # [op3097] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a3, 0(a1)  # [op3098] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v4, v4, 1  # [op3099] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v4  # [op3100] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 22  # [op3101] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a3, t0, a3  # [op3102] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a3, 0(a3)  # [op3103] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a3, 0(a1)  # [op3104] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v4, v4, 1  # [op3105] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v4  # [op3106] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 24  # [op3107] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a3, t0, a3  # [op3108] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a3, 0(a3)  # [op3109] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a3, 0(a1)  # [op3110] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v4, v4, 1  # [op3111] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v4  # [op3112] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 26  # [op3113] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a3, t0, a3  # [op3114] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a3, 0(a3)  # [op3115] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a3, 0(a1)  # [op3116] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v4, v4, 1  # [op3117] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v4  # [op3118] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 28  # [op3119] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a3, t0, a3  # [op3120] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a3, 0(a3)  # [op3121] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a3, 0(a1)  # [op3122] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v4, v4, 1  # [op3123] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v4  # [op3124] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 30  # [op3125] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a3, t0, a3  # [op3126] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a3, 0(a3)  # [op3127] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a3, 0(a1)  # [op3128] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v4, v4, 1  # [op3129] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v4  # [op3130] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 32  # [op3131] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a3, t0, a3  # [op3132] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a3, 0(a3)  # [op3133] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a3, 0(a1)  # [op3134] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v4, v4, 1  # [op3135] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v4  # [op3136] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 34  # [op3137] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a3, t0, a3  # [op3138] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a3, 0(a3)  # [op3139] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a3, 0(a1)  # [op3140] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v4, v4, 1  # [op3141] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v4  # [op3142] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 36  # [op3143] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a3, t0, a3  # [op3144] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a3, 0(a3)  # [op3145] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a3, 0(a1)  # [op3146] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v4, v4, 1  # [op3147] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v4  # [op3148] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 38  # [op3149] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a3, t0, a3  # [op3150] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a3, 0(a3)  # [op3151] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a3, 0(a1)  # [op3152] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v4, v4, 1  # [op3153] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v4  # [op3154] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 40  # [op3155] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a3, t0, a3  # [op3156] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a3, 0(a3)  # [op3157] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a3, 0(a1)  # [op3158] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v4, v4, 1  # [op3159] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v4  # [op3160] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 42  # [op3161] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a3, t0, a3  # [op3162] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a3, 0(a3)  # [op3163] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a3, 0(a1)  # [op3164] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v4, v4, 1  # [op3165] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v4  # [op3166] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 44  # [op3167] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a3, t0, a3  # [op3168] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a3, 0(a3)  # [op3169] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a3, 0(a1)  # [op3170] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v4, v4, 1  # [op3171] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v4  # [op3172] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 46  # [op3173] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a3, t0, a3  # [op3174] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a3, 0(a3)  # [op3175] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a3, 0(a1)  # [op3176] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v4, v4, 1  # [op3177] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v4  # [op3178] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 48  # [op3179] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a3, t0, a3  # [op3180] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a3, 0(a3)  # [op3181] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a3, 0(a1)  # [op3182] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v4, v4, 1  # [op3183] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v4  # [op3184] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 50  # [op3185] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a3, t0, a3  # [op3186] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a3, 0(a3)  # [op3187] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a3, 0(a1)  # [op3188] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v4, v4, 1  # [op3189] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v4  # [op3190] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 52  # [op3191] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a3, t0, a3  # [op3192] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a3, 0(a3)  # [op3193] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a3, 0(a1)  # [op3194] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v4, v4, 1  # [op3195] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v4  # [op3196] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 54  # [op3197] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a3, t0, a3  # [op3198] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a3, 0(a3)  # [op3199] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a3, 0(a1)  # [op3200] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v4, v4, 1  # [op3201] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v4  # [op3202] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 56  # [op3203] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a3, t0, a3  # [op3204] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a3, 0(a3)  # [op3205] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a3, 0(a1)  # [op3206] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v4, v4, 1  # [op3207] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v4  # [op3208] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 58  # [op3209] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a3, t0, a3  # [op3210] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a3, 0(a3)  # [op3211] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a3, 0(a1)  # [op3212] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v4, v4, 1  # [op3213] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v4  # [op3214] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 60  # [op3215] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a3, t0, a3  # [op3216] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a3, 0(a3)  # [op3217] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a3, 0(a1)  # [op3218] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v4, v4, 1  # [op3219] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v4  # [op3220] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a3, 62  # [op3221] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add t0, t0, a3  # [op3222] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu t0, 0(t0)  # [op3223] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh t0, 0(a1)  # [op3224] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v4, v4, 1  # [op3225] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vcpop.m t0, v2  # [op3226] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add t0, s1, t0  # [op3227] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op3228] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t1, t1, s1  # [op3229] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op3230] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e16, m1, ta,ma  # [op3231] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv s1, t0  # [op3232] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk34_head  # [op3232] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lprog_next:  # block prog_next
add t0, t0, s6  # [op3233] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lprog_head  # [op3234] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lprog_exit:  # block prog_exit
sd t0, 0(a6)  # [op3235] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld ra, 0(sp)  # [op3236] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s1, 8(sp)  # [op3236] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s2, 16(sp)  # [op3236] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s3, 24(sp)  # [op3236] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s4, 32(sp)  # [op3236] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s5, 40(sp)  # [op3236] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s6, 48(sp)  # [op3236] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s7, 56(sp)  # [op3236] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s8, 64(sp)  # [op3236] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s9, 72(sp)  # [op3236] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s10, 80(sp)  # [op3236] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s11, 88(sp)  # [op3236] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addi sp, sp, 160  # [op3236] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ret  # [op3236] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    .size operator_entry, .-operator_entry
    .section .note.GNU-stack,"",@progbits
