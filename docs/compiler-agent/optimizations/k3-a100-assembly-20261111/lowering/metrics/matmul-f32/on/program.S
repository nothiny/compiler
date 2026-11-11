# a100c emitted program: matmul_kernel
# source: tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py
# specialization identity: 216f8cb4fe10a59a
# compiler revision: b5c42fbb75a242a8
# target model: a100-rvv1-vlen1024/1 (VLEN=1024, file=4096B)
# options: default
# argument layout: d04f8df25eab1dc2
# every instruction below traces to a selected MIR op: [opN] carries the source location
# passes: passes=default
    .text
    .globl operator_workspace_private
    .type operator_workspace_private, @function
operator_workspace_private:
    li a0, 37440
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
    # [peephole] removed 0 redundant vsetvli, 186 redundant li
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
mv a1, t1  # [op31] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lprog_body  # [op31] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lprog_body:  # block prog_body
li t1, 1  # [op32] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t2, 120(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
divu t2, t0, t2  # [op33] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s1, 120(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mul t2, t2, s1  # [op34] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sub s1, t0, t2  # [op35] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t2, 120(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mul t1, t1, t2  # [op36] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
divu t2, t0, t1  # [op37] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld a3, 128(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
divu a3, t2, a3  # [op38] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld a4, 128(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mul a3, a3, a4  # [op39] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sub t2, t2, a3  # [op40] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld a3, 128(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mul t1, t1, a3  # [op41] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addiw t1, s1, 0  # [op42] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addiw a3, t2, 0  # [op43] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t2, 120(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addiw t2, t2, 0  # [op44] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t2, 128(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addiw t2, t2, 0  # [op45] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t2, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t2, 8(t2)  # [op47] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 4  # [op48] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:14
sllw a4, t1, s1  # [op49] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:14
li t1, 0  # [op50] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t2, a1  # [op51] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk1_head  # [op51] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk1_head:  # block chunk1_head
li a1, 16  # [op52] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt a1, t1, a1  # [op53] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne a1, zero, .Lbrc54_true  # [op54] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op54] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t2, t0  # [op54] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk1_exit  # [op54] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc54_true:  # [op54] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk1_body  # [op54] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk1_exit:  # block chunk1_exit
li t2, 0  # [op55] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t1, 96(sp)  # [op56] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op56] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t2, 96(sp)  # [op56] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk2_head  # [op56] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk1_body:  # block chunk1_body
li a1, 16  # [op57] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli a1, a1, e32, m1, ta,ma  # [op58] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li a1, 16  # [op59] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:27
vid.v v1  # [op61] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:27
vadd.vx v1, v1, t1  # [op62] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:27
vmv.v.x v2, a4  # [op63] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:14
vadd.vv v2, v2, v1  # [op64] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:14
vid.v v3  # [op65] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:14
vadd.vx v3, v3, t1  # [op66] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:14
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
vadd.vx v2, v2, t1  # [op85] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:26:14
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
add t2, t2, a1  # [op101] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op102] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t1, t1, a1  # [op103] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op104] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk1_head  # [op106] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk2_head:  # block chunk2_head
li s1, 32  # [op107] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t1, s1  # [op108] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc109_true  # [op109] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op109] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t2, t0  # [op109] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk2_exit  # [op109] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc109_true:  # [op109] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk2_body  # [op109] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk2_exit:  # block chunk2_exit
li t2, 0  # [op110] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t1, 96(sp)  # [op111] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op111] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t2, 96(sp)  # [op111] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk3_head  # [op111] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk2_body:  # block chunk2_body
li s1, 32  # [op112] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op113] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op114] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:27:14
vid.v v1  # [op116] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:27:14
vadd.vx v1, v1, t1  # [op117] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:27:14
vid.v v2  # [op118] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:27:14
vadd.vx v2, v2, t1  # [op119] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:27:14
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
add t2, t2, s1  # [op135] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op136] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t1, t1, s1  # [op137] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op138] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk2_head  # [op140] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk3_head:  # block chunk3_head
li s1, 256  # [op141] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t1, s1  # [op142] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc143_true  # [op143] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op143] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t2, t0  # [op143] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk3_exit  # [op143] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc143_true:  # [op143] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk3_body  # [op143] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk3_exit:  # block chunk3_exit
li t2, 0  # [op144] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t1, 96(sp)  # [op145] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op145] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t2, 96(sp)  # [op145] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk4_head  # [op145] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk3_body:  # block chunk3_body
li s1, 32  # [op146] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op147] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 0  # [op148] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:28:11
li a1, 32  # [op149] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:28:11
vmv.v.x v1, s1  # [op151] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:28:11
vid.v v2  # [op152] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:28:11
vadd.vx v2, v2, t1  # [op153] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:28:11
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
add t2, t2, s1  # [op171] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op172] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t1, t1, s1  # [op173] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op174] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk3_head  # [op176] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk4_head:  # block chunk4_head
li s1, 16  # [op177] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t1, s1  # [op178] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc179_true  # [op179] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op179] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t2, t0  # [op179] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk4_exit  # [op179] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc179_true:  # [op179] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk4_body  # [op179] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk4_exit:  # block chunk4_exit
li t2, 0  # [op180] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t1, 96(sp)  # [op181] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op181] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t2, 96(sp)  # [op181] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk5_head  # [op181] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk4_body:  # block chunk4_body
li s1, 16  # [op182] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op183] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 16  # [op184] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
ld s1, 136(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vmv.v.x v1, s1  # [op186] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vid.v v2  # [op187] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vadd.vx v2, v2, t1  # [op188] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
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
vadd.vx v2, v2, t1  # [op205] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
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
add t2, t2, s1  # [op221] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op222] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t1, t1, s1  # [op223] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op224] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk4_head  # [op226] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk5_head:  # block chunk5_head
li s1, 32  # [op227] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t1, s1  # [op228] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc229_true  # [op229] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op229] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t2, t0  # [op229] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk5_exit  # [op229] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc229_true:  # [op229] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk5_body  # [op229] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk5_exit:  # block chunk5_exit
li t2, 0  # [op230] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t1, 96(sp)  # [op231] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op231] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t2, 96(sp)  # [op231] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk6_head  # [op231] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk5_body:  # block chunk5_body
li s1, 32  # [op232] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op233] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op234] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
ld s1, 136(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vmv.v.x v1, s1  # [op236] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vid.v v2  # [op237] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vadd.vx v2, v2, t1  # [op238] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
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
vadd.vx v2, v2, t1  # [op256] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
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
add t2, t2, s1  # [op272] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op273] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t1, t1, s1  # [op274] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op275] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk5_head  # [op277] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk6_head:  # block chunk6_head
li s1, 16  # [op278] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t1, s1  # [op279] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc280_true  # [op280] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op280] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t2, t0  # [op280] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk6_exit  # [op280] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc280_true:  # [op280] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk6_body  # [op280] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk6_exit:  # block chunk6_exit
li t2, 0  # [op281] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t1, 96(sp)  # [op282] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op282] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t2, 96(sp)  # [op282] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk7_head  # [op282] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk6_body:  # block chunk6_body
li s1, 16  # [op283] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op284] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 16  # [op285] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t2, t2, s1  # [op286] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op287] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t1, t1, s1  # [op288] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op289] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk6_head  # [op291] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk7_head:  # block chunk7_head
li s1, 32  # [op292] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t1, s1  # [op293] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc294_true  # [op294] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op294] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t2, t0  # [op294] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk7_exit  # [op294] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc294_true:  # [op294] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk7_body  # [op294] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk7_exit:  # block chunk7_exit
li t2, 0  # [op295] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t1, 96(sp)  # [op296] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op296] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t2, 96(sp)  # [op296] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk8_head  # [op296] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk7_body:  # block chunk7_body
li s1, 32  # [op297] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op298] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op299] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
ld s1, 136(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vmv.v.x v1, s1  # [op301] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vid.v v2  # [op302] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vadd.vx v2, v2, t1  # [op303] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
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
add t2, t2, s1  # [op319] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op320] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t1, t1, s1  # [op321] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op322] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk7_head  # [op324] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk8_head:  # block chunk8_head
li s1, 16  # [op325] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t1, s1  # [op326] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc327_true  # [op327] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op327] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t2, t0  # [op327] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk8_exit  # [op327] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc327_true:  # [op327] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk8_body  # [op327] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk8_exit:  # block chunk8_exit
li t2, 0  # [op328] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t1, 96(sp)  # [op329] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op329] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t2, 96(sp)  # [op329] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk9_head  # [op329] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk8_body:  # block chunk8_body
li s1, 16  # [op330] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op331] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 16  # [op332] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vmv.v.x v1, a2  # [op334] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vid.v v2  # [op335] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vadd.vx v2, v2, t1  # [op336] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
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
vadd.vx v1, v1, t1  # [op352] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
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
vadd.vx v2, v2, t1  # [op368] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
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
vadd.vx v3, v3, t1  # [op385] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
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
vadd.vx v2, v2, t1  # [op401] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
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
vadd.vx v2, v2, t1  # [op418] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
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
add t2, t2, s1  # [op438] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op439] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t1, t1, s1  # [op440] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op441] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk8_head  # [op443] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk9_head:  # block chunk9_head
li s1, 512  # [op444] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t1, s1  # [op445] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc446_true  # [op446] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op446] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t2, t0  # [op446] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk9_exit  # [op446] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc446_true:  # [op446] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk9_body  # [op446] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk9_exit:  # block chunk9_exit
li t2, 0  # [op447] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t1, 96(sp)  # [op448] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op448] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t2, 96(sp)  # [op448] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk10_head  # [op448] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk9_body:  # block chunk9_body
li s1, 32  # [op449] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op450] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 0  # [op451] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a1, 32  # [op452] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.x v1, s1  # [op454] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vid.v v2  # [op455] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vadd.vx v2, v2, t1  # [op456] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s1, 32  # [op457] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vwadd.vx v4, v2, x0  # [op459] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op460] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli s1, s1, e64, m2, ta,ma  # [op461] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s1, 4  # [op462] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmul.vx v2, v4, s1  # [op463] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s1, 12608  # [op464] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add s1, a1, s1  # [op465] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a1, 32  # [op466] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a1, a1, e32, m1, ta,ma  # [op467] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsuxei64.v v1, (s1), v2  # [op468] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s1, 32  # [op469] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op471] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t2, t2, s1  # [op472] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op473] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t1, t1, s1  # [op474] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op475] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk9_head  # [op477] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk10_head:  # block chunk10_head
li s1, 16  # [op478] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t1, s1  # [op479] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc480_true  # [op480] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op480] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t2, t0  # [op480] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk10_exit  # [op480] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc480_true:  # [op480] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk10_body  # [op480] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk10_exit:  # block chunk10_exit
li t2, 0  # [op481] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t1, 96(sp)  # [op482] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op482] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t2, 96(sp)  # [op482] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk11_head  # [op482] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk10_body:  # block chunk10_body
li s1, 16  # [op483] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op484] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 16  # [op485] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vid.v v1  # [op487] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vadd.vx v1, v1, t1  # [op488] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
    # [peephole-li] [op489] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vwadd.vx v2, v1, x0  # [op491] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
    # [peephole-li] [op492] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vsetvli s1, s1, e64, m2, ta,ma  # [op493] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li s1, 4  # [op494] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vmul.vx v2, v2, s1  # [op495] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li s1, 64  # [op496] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
add s1, a1, s1  # [op497] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li a1, 16  # [op498] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vsetvli a1, a1, e32, m1, ta,ma  # [op499] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vluxei64.v v1, (s1), v2  # [op500] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li s1, 16  # [op501] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vid.v v2  # [op503] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vadd.vx v2, v2, t1  # [op504] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
    # [peephole-li] [op505] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vwadd.vx v4, v2, x0  # [op507] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
    # [peephole-li] [op508] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vsetvli s1, s1, e64, m2, ta,ma  # [op509] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li s1, 4  # [op510] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vmul.vx v2, v4, s1  # [op511] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li s1, 21760  # [op512] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
add s1, a1, s1  # [op513] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li a1, 16  # [op514] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vsetvli a1, a1, e32, m1, ta,ma  # [op515] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vluxei64.v v4, (s1), v2  # [op516] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li s1, 16  # [op517] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vmslt.vv v1, v1, v4  # [op519] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vid.v v2  # [op520] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vadd.vx v2, v2, t1  # [op521] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
    # [peephole-li] [op522] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vwadd.vx v4, v2, x0  # [op524] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
    # [peephole-li] [op525] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vsetvli s1, s1, e64, m2, ta,ma  # [op526] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li s1, 4  # [op527] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vmul.vx v2, v4, s1  # [op528] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li s1, 21824  # [op529] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
add s1, a1, s1  # [op530] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li a1, 16  # [op531] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vsetvli a1, a1, e32, m1, ta,ma  # [op532] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li a1, 1  # [op533] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vmv.v.x v4, a1  # [op534] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li a1, 0  # [op535] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vmv.v.x v5, a1  # [op536] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vmv1r.v v0, v1  # [op537] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vmerge.vvm v1, v5, v4, v0  # [op538] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vsuxei64.v v1, (s1), v2  # [op539] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li s1, 16  # [op540] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t2, t2, s1  # [op541] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op542] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t1, t1, s1  # [op543] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op544] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk10_head  # [op546] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk11_head:  # block chunk11_head
li s1, 512  # [op547] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t1, s1  # [op548] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc549_true  # [op549] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op549] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t2, t0  # [op549] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk11_exit  # [op549] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc549_true:  # [op549] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk11_body  # [op549] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk11_exit:  # block chunk11_exit
li t2, 0  # [op550] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t1, 96(sp)  # [op551] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op551] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t2, 96(sp)  # [op551] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk12_head  # [op551] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk11_body:  # block chunk11_body
li s1, 32  # [op552] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op553] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 0  # [op554] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a1, 32  # [op555] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.x v1, s1  # [op557] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vid.v v2  # [op558] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vadd.vx v2, v2, t1  # [op559] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s1, 32  # [op560] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vwadd.vx v4, v2, x0  # [op562] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
    # [peephole-li] [op563] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s1, s1, e64, m2, ta,ma  # [op564] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s1, 4  # [op565] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmul.vx v2, v4, s1  # [op566] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s1, 28032  # [op567] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add s1, a1, s1  # [op568] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a1, 32  # [op569] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a1, a1, e32, m1, ta,ma  # [op570] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsuxei64.v v1, (s1), v2  # [op571] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s1, 32  # [op572] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
    # [peephole-li] [op574] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t2, t2, s1  # [op575] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op576] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t1, t1, s1  # [op577] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op578] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk11_head  # [op580] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk12_head:  # block chunk12_head
li s1, 16  # [op581] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t1, s1  # [op582] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc583_true  # [op583] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t0  # [op583] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv a3, t2  # [op583] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk12_exit  # [op583] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc583_true:  # [op583] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk12_body  # [op583] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk12_exit:  # block chunk12_exit
li t1, 0  # [op584] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
j .Lstg13_head  # [op585] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
.Lchunk12_body:  # block chunk12_body
li s1, 16  # [op586] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op587] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 16  # [op588] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t2, t2, s1  # [op589] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op590] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t1, t1, s1  # [op591] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op592] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk12_head  # [op594] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lstg13_head:  # block stg13_head
li t2, 512  # [op595] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
slt t2, t1, t2  # [op596] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
bne t2, zero, .Lbrc597_true  # [op597] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
j .Lstg13_exit  # [op597] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
.Lbrc597_true:  # [op597] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
j .Lstg13_body  # [op597] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
.Lstg13_body:  # block stg13_body
li t2, 32  # [op598] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t2, t2, e32, m1, ta,ma  # [op599] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vid.v v1  # [op600] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vadd.vx v1, v1, t1  # [op601] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t2, 32  # [op602] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv.v.x v2, t2  # [op603] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vdiv.vv v2, v1, v2  # [op604] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t2, 16  # [op605] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv.v.x v3, t2  # [op606] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vrem.vv v2, v2, v3  # [op607] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t2, 32  # [op608] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv.v.x v3, t2  # [op609] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vrem.vv v3, v1, v3  # [op610] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op611] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vwadd.vx v4, v2, x0  # [op613] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op614] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t2, t2, e64, m2, ta,ma  # [op615] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t2, 4  # [op616] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmul.vx v2, v4, t2  # [op617] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t2, 6144  # [op618] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld s1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld s1, 16(s1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
add t2, s1, t2  # [op619] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li s1, 32  # [op620] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli s1, s1, e32, m1, ta,ma  # [op621] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vluxei64.v v4, (t2), v2  # [op622] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t2, 32  # [op623] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vwadd.vx v2, v1, x0  # [op625] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op626] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t2, t2, e64, m2, ta,ma  # [op627] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t2, 4  # [op628] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmul.vx v2, v2, t2  # [op629] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t2, 6464  # [op630] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld s1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld s1, 16(s1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
add t2, s1, t2  # [op631] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li s1, 32  # [op632] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli s1, s1, e32, m1, ta,ma  # [op633] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsuxei64.v v4, (t2), v2  # [op634] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t2, 32  # [op635] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
addw t1, t1, t2  # [op636] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
j .Lstg13_head  # [op637] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
.Lstg13_exit:  # block stg13_exit
li t1, 0  # [op638] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
j .Lstg14_head  # [op639] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
.Lstg14_head:  # block stg14_head
li t2, 512  # [op640] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
slt t2, t1, t2  # [op641] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
bne t2, zero, .Lbrc642_true  # [op642] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
j .Lstg14_exit  # [op642] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
.Lbrc642_true:  # [op642] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
j .Lstg14_body  # [op642] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
.Lstg14_body:  # block stg14_body
li t2, 32  # [op643] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t2, t2, e32, m1, ta,ma  # [op644] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vid.v v1  # [op645] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vadd.vx v1, v1, t1  # [op646] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t2, 16  # [op647] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv.v.x v2, t2  # [op648] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vdiv.vv v2, v1, v2  # [op649] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t2, 32  # [op650] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv.v.x v3, t2  # [op651] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vrem.vv v2, v2, v3  # [op652] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t2, 16  # [op653] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv.v.x v2, t2  # [op654] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vrem.vv v2, v1, v2  # [op655] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t2, 32  # [op656] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vwadd.vx v4, v2, x0  # [op658] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
    # [peephole-li] [op659] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t2, t2, e64, m2, ta,ma  # [op660] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t2, 4  # [op661] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmul.vx v2, v4, t2  # [op662] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t2, 21824  # [op663] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld s1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld s1, 16(s1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
add t2, s1, t2  # [op664] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li s1, 32  # [op665] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli s1, s1, e32, m1, ta,ma  # [op666] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vluxei64.v v4, (t2), v2  # [op667] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t2, 32  # [op668] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vwadd.vx v2, v1, x0  # [op670] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
    # [peephole-li] [op671] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t2, t2, e64, m2, ta,ma  # [op672] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t2, 4  # [op673] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmul.vx v2, v2, t2  # [op674] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t2, 23936  # [op675] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld s1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld s1, 16(s1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
add t2, s1, t2  # [op676] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li s1, 32  # [op677] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli s1, s1, e32, m1, ta,ma  # [op678] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsuxei64.v v4, (t2), v2  # [op679] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t2, 32  # [op680] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
addw t1, t1, t2  # [op681] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
j .Lstg14_head  # [op682] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
.Lstg14_exit:  # block stg14_exit
li t1, 0  # [op683] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
li s7, 32  # [op684] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
mv t2, t1  # [op685] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
j .Lmloop15.head  # [op685] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
.Lmloop15.head:  # block mloop15.head
ld t1, 136(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
slt t1, t2, t1  # [op686] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
bne t1, zero, .Lbrc687_true  # [op687] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
mv t1, t2  # [op687] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
j .Lmloop15.exit  # [op687] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
.Lbrc687_true:  # [op687] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
j .Lmloop15.body  # [op687] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
.Lmloop15.body:  # block mloop15.body
li t1, 0  # [op688] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv s1, a3  # [op689] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk16_head  # [op689] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lmloop15.exit:  # block mloop15.exit
li t1, 0  # [op690] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t2, a3  # [op691] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk30_head  # [op691] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk16_head:  # block chunk16_head
li a1, 32  # [op692] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt a1, t1, a1  # [op693] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne a1, zero, .Lbrc694_true  # [op694] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, s1  # [op694] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv s1, t0  # [op694] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk16_exit  # [op694] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc694_true:  # [op694] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk16_body  # [op694] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk16_exit:  # block chunk16_exit
li s1, 0  # [op695] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t1, 96(sp)  # [op696] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, s1  # [op696] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s1, 96(sp)  # [op696] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk17_head  # [op696] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk16_body:  # block chunk16_body
li a1, 32  # [op697] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli a1, a1, e32, m1, ta,ma  # [op698] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li a1, 32  # [op699] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vmv.v.x v1, t2  # [op701] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vid.v v2  # [op702] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vadd.vx v2, v2, t1  # [op703] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
    # [peephole-li] [op704] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vwadd.vx v4, v2, x0  # [op706] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
    # [peephole-li] [op707] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vsetvli a1, a1, e64, m2, ta,ma  # [op708] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
li a1, 4  # [op709] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vmul.vx v2, v4, a1  # [op710] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
li a1, 1280  # [op711] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
ld a4, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
ld a4, 16(a4)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
add a1, a4, a1  # [op712] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
li a4, 32  # [op713] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vsetvli a4, a4, e32, m1, ta,ma  # [op714] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vsuxei64.v v1, (a1), v2  # [op715] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
li a1, 32  # [op716] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vid.v v2  # [op718] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vadd.vx v2, v2, t1  # [op719] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
    # [peephole-li] [op720] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vwadd.vx v4, v2, x0  # [op722] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
    # [peephole-li] [op723] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vsetvli a1, a1, e64, m2, ta,ma  # [op724] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
li a1, 4  # [op725] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vmul.vx v2, v4, a1  # [op726] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
li a1, 128  # [op727] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
ld a4, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
ld a4, 16(a4)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
add a1, a4, a1  # [op728] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
li a4, 32  # [op729] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vsetvli a4, a4, e32, m1, ta,ma  # [op730] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vluxei64.v v4, (a1), v2  # [op731] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
li a1, 32  # [op732] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vadd.vv v1, v1, v4  # [op734] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vid.v v2  # [op735] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vadd.vx v2, v2, t1  # [op736] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
    # [peephole-li] [op737] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vwadd.vx v4, v2, x0  # [op739] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
    # [peephole-li] [op740] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vsetvli a1, a1, e64, m2, ta,ma  # [op741] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
li a1, 4  # [op742] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vmul.vx v2, v4, a1  # [op743] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
li a1, 1408  # [op744] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
ld a4, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
ld a4, 16(a4)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
add a1, a4, a1  # [op745] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
li a4, 32  # [op746] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vsetvli a4, a4, e32, m1, ta,ma  # [op747] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vsuxei64.v v1, (a1), v2  # [op748] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
li a1, 32  # [op749] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
    # [peephole-li] [op751] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add s1, s1, a1  # [op752] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op753] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t1, t1, a1  # [op754] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op755] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk16_head  # [op757] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk17_head:  # block chunk17_head
li a1, 512  # [op758] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt a1, t1, a1  # [op759] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne a1, zero, .Lbrc760_true  # [op760] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, s1  # [op760] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv s1, t0  # [op760] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk17_exit  # [op760] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc760_true:  # [op760] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk17_body  # [op760] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk17_exit:  # block chunk17_exit
li s1, 0  # [op761] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t1, 96(sp)  # [op762] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, s1  # [op762] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s1, 96(sp)  # [op762] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk18_head  # [op762] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk17_body:  # block chunk17_body
li a1, 32  # [op763] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli a1, a1, e32, m1, ta,ma  # [op764] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li a1, 32  # [op765] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
vid.v v1  # [op767] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
vadd.vx v1, v1, t1  # [op768] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
    # [peephole-li] [op769] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
vmv.v.x v2, a1  # [op770] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
vdiv.vv v1, v1, v2  # [op771] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
    # [peephole-li] [op772] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
vwadd.vx v2, v1, x0  # [op774] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
    # [peephole-li] [op775] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
vsetvli a1, a1, e64, m2, ta,ma  # [op776] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
li a1, 8  # [op777] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
vmul.vx v2, v2, a1  # [op778] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
li a1, 1728  # [op779] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
ld a4, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
ld a4, 16(a4)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
add a1, a4, a1  # [op780] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
li a4, 32  # [op781] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
vluxei64.v v4, (a1), v2  # [op783] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
li a1, 32  # [op784] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
vsetvli a1, a1, e32, m1, ta,ma  # [op785] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
li a1, 32  # [op786] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add s1, s1, a1  # [op787] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op788] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t1, t1, a1  # [op789] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op790] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk17_head  # [op792] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk18_head:  # block chunk18_head
li a1, 32  # [op793] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt a1, t1, a1  # [op794] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne a1, zero, .Lbrc795_true  # [op795] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t0  # [op795] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk18_exit  # [op795] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc795_true:  # [op795] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk18_body  # [op795] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk18_exit:  # block chunk18_exit
li t1, 0  # [op796] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
j .Lstg19_head  # [op797] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
.Lchunk18_body:  # block chunk18_body
li a1, 32  # [op798] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli a1, a1, e32, m1, ta,ma  # [op799] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li a1, 32  # [op800] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vid.v v1  # [op802] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vadd.vx v1, v1, t1  # [op803] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
    # [peephole-li] [op804] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vwadd.vx v2, v1, x0  # [op806] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
    # [peephole-li] [op807] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vsetvli a1, a1, e64, m2, ta,ma  # [op808] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li a1, 4  # [op809] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vmul.vx v2, v2, a1  # [op810] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li a1, 1408  # [op811] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
ld a4, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
ld a4, 16(a4)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
add a1, a4, a1  # [op812] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li a4, 32  # [op813] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vsetvli a4, a4, e32, m1, ta,ma  # [op814] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vluxei64.v v1, (a1), v2  # [op815] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li a1, 32  # [op816] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vid.v v2  # [op818] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vadd.vx v2, v2, t1  # [op819] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
    # [peephole-li] [op820] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vwadd.vx v4, v2, x0  # [op822] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
    # [peephole-li] [op823] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vsetvli a1, a1, e64, m2, ta,ma  # [op824] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li a1, 4  # [op825] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vmul.vx v2, v4, a1  # [op826] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li a1, 6208  # [op827] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
ld a4, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
ld a4, 16(a4)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
add a1, a4, a1  # [op828] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li a4, 32  # [op829] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vsetvli a4, a4, e32, m1, ta,ma  # [op830] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vluxei64.v v4, (a1), v2  # [op831] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li a1, 32  # [op832] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vmslt.vv v1, v1, v4  # [op834] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vid.v v2  # [op835] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vadd.vx v2, v2, t1  # [op836] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
    # [peephole-li] [op837] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vwadd.vx v4, v2, x0  # [op839] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
    # [peephole-li] [op840] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vsetvli a1, a1, e64, m2, ta,ma  # [op841] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li a1, 4  # [op842] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vmul.vx v2, v4, a1  # [op843] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li a1, 6336  # [op844] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
ld a4, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
ld a4, 16(a4)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
add a1, a4, a1  # [op845] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li a4, 32  # [op846] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vsetvli a4, a4, e32, m1, ta,ma  # [op847] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li a4, 1  # [op848] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vmv.v.x v4, a4  # [op849] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li a4, 0  # [op850] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vmv.v.x v5, a4  # [op851] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vmv1r.v v0, v1  # [op852] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vmerge.vvm v1, v5, v4, v0  # [op853] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vsuxei64.v v1, (a1), v2  # [op854] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li a1, 32  # [op855] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add s1, s1, a1  # [op856] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op857] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t1, t1, a1  # [op858] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op859] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk18_head  # [op861] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lstg19_head:  # block stg19_head
li a1, 512  # [op862] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
slt a1, t1, a1  # [op863] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
bne a1, zero, .Lbrc864_true  # [op864] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
j .Lstg19_exit  # [op864] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
.Lbrc864_true:  # [op864] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
j .Lstg19_body  # [op864] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
.Lstg19_body:  # block stg19_body
li a1, 32  # [op865] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli a1, a1, e32, m1, ta,ma  # [op866] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vid.v v1  # [op867] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vadd.vx v1, v1, t1  # [op868] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li a1, 32  # [op869] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv.v.x v2, a1  # [op870] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vdiv.vv v2, v1, v2  # [op871] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li a1, 16  # [op872] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv.v.x v3, a1  # [op873] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vrem.vv v2, v2, v3  # [op874] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li a1, 32  # [op875] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv.v.x v2, a1  # [op876] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vrem.vv v2, v1, v2  # [op877] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op878] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vwadd.vx v4, v2, x0  # [op880] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op881] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli a1, a1, e64, m2, ta,ma  # [op882] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li a1, 4  # [op883] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmul.vx v2, v4, a1  # [op884] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li a1, 6336  # [op885] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld a4, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld a4, 16(a4)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
add a1, a4, a1  # [op886] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li a4, 32  # [op887] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli a4, a4, e32, m1, ta,ma  # [op888] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vluxei64.v v4, (a1), v2  # [op889] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li a1, 32  # [op890] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vwadd.vx v2, v1, x0  # [op892] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op893] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli a1, a1, e64, m2, ta,ma  # [op894] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li a1, 4  # [op895] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmul.vx v2, v2, a1  # [op896] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li a1, 8512  # [op897] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld a4, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld a4, 16(a4)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
add a1, a4, a1  # [op898] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li a4, 32  # [op899] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli a4, a4, e32, m1, ta,ma  # [op900] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsuxei64.v v4, (a1), v2  # [op901] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li a1, 32  # [op902] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
addw t1, t1, a1  # [op903] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
j .Lstg19_head  # [op904] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
.Lstg19_exit:  # block stg19_exit
li t1, 0  # [op905] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk20_head  # [op906] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk20_head:  # block chunk20_head
li a1, 512  # [op907] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt a1, t1, a1  # [op908] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne a1, zero, .Lbrc909_true  # [op909] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, s1  # [op909] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv s1, t0  # [op909] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk20_exit  # [op909] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc909_true:  # [op909] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk20_body  # [op909] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk20_exit:  # block chunk20_exit
li s1, 0  # [op910] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t1, 96(sp)  # [op911] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, s1  # [op911] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s1, 96(sp)  # [op911] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk21_head  # [op911] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk20_body:  # block chunk20_body
li a1, 32  # [op912] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli a1, a1, e32, m1, ta,ma  # [op913] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li a1, 32  # [op914] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vid.v v1  # [op916] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vadd.vx v1, v1, t1  # [op917] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op918] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vwadd.vx v2, v1, x0  # [op920] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op921] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli a1, a1, e64, m2, ta,ma  # [op922] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li a1, 4  # [op923] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmul.vx v2, v2, a1  # [op924] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li a1, 6464  # [op925] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld a4, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld a4, 16(a4)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
add a1, a4, a1  # [op926] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li a4, 32  # [op927] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli a4, a4, e32, m1, ta,ma  # [op928] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vluxei64.v v1, (a1), v2  # [op929] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li a1, 0  # [op930] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv.v.x v2, a1  # [op931] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmsne.vv v1, v1, v2  # [op932] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li a1, 32  # [op933] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vid.v v2  # [op935] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vadd.vx v2, v2, t1  # [op936] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op937] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vwadd.vx v4, v2, x0  # [op939] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op940] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli a1, a1, e64, m2, ta,ma  # [op941] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li a1, 4  # [op942] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmul.vx v2, v4, a1  # [op943] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li a1, 8512  # [op944] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld a4, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld a4, 16(a4)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
add a1, a4, a1  # [op945] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li a4, 32  # [op946] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli a4, a4, e32, m1, ta,ma  # [op947] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vluxei64.v v4, (a1), v2  # [op948] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li a1, 0  # [op949] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv.v.x v2, a1  # [op950] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmsne.vv v2, v4, v2  # [op951] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li a1, 32  # [op952] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmand.mm v1, v1, v2  # [op954] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vid.v v2  # [op955] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vadd.vx v2, v2, t1  # [op956] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op957] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vwadd.vx v4, v2, x0  # [op959] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op960] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli a1, a1, e64, m2, ta,ma  # [op961] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li a1, 4  # [op962] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmul.vx v2, v4, a1  # [op963] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li a1, 10560  # [op964] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld a4, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld a4, 16(a4)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
add a1, a4, a1  # [op965] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li a4, 32  # [op966] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli a4, a4, e32, m1, ta,ma  # [op967] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li a4, 1  # [op968] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv.v.x v4, a4  # [op969] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li a4, 0  # [op970] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv.v.x v5, a4  # [op971] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv1r.v v0, v1  # [op972] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmerge.vvm v4, v5, v4, v0  # [op973] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsuxei64.v v4, (a1), v2  # [op974] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vid.v v2  # [op975] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vadd.vx v2, v2, t1  # [op976] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li a1, 32  # [op977] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vwadd.vx v4, v2, x0  # [op979] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op980] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli a1, a1, e64, m2, ta,ma  # [op981] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li a1, 4  # [op982] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmul.vx v2, v4, a1  # [op983] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li a1, 10560  # [op984] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld a4, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld a4, 16(a4)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
add a1, a4, a1  # [op985] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li a4, 32  # [op986] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli a4, a4, e32, m1, ta,ma  # [op987] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li a4, 1  # [op988] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv.v.x v4, a4  # [op989] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li a4, 0  # [op990] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv.v.x v5, a4  # [op991] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv1r.v v0, v1  # [op992] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmerge.vvm v4, v5, v4, v0  # [op993] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsuxei64.v v4, (a1), v2  # [op994] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vid.v v2  # [op995] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vadd.vx v2, v2, t1  # [op996] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a1, 32  # [op997] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.x v3, a1  # [op998] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vdiv.vv v2, v2, v3  # [op999] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op1000] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vwadd.vx v4, v2, x0  # [op1002] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op1003] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1004] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a1, 4  # [op1005] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmul.vx v2, v4, a1  # [op1006] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a1, 1664  # [op1007] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
ld a4, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
ld a4, 16(a4)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a1, a4, a1  # [op1008] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1009] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e32, m1, ta,ma  # [op1010] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vluxei64.v v4, (a1), v2  # [op1011] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a1, 32  # [op1012] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vid.v v2  # [op1014] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vadd.vx v2, v2, t1  # [op1015] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op1016] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.x v3, a1  # [op1017] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vrem.vv v2, v2, v3  # [op1018] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op1019] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vwadd.vx v6, v2, x0  # [op1021] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op1022] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1023] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a1, 4  # [op1024] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmul.vx v2, v6, a1  # [op1025] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a1, 1408  # [op1026] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
ld a4, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
ld a4, 16(a4)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a1, a4, a1  # [op1027] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1028] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e32, m1, ta,ma  # [op1029] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vluxei64.v v5, (a1), v2  # [op1030] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a1, 32  # [op1031] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vadd.vv v2, v4, v5  # [op1033] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op1034] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vwadd.vx v4, v2, x0  # [op1036] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op1037] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1038] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a1, 4  # [op1039] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmul.vx v2, v4, a1  # [op1040] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a1, 32  # [op1041] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a1, a1, e32, m1, ta,ma  # [op1042] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv1r.v v0, v1  # [op1043] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vluxei64.v v4, (s2), v2, v0.t  # [op1044] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a1, 32  # [op1045] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vid.v v2  # [op1047] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vadd.vx v2, v2, t1  # [op1048] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op1049] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vwadd.vx v6, v2, x0  # [op1051] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op1052] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1053] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a1, 4  # [op1054] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmul.vx v2, v6, a1  # [op1055] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a1, 12608  # [op1056] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
ld a4, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
ld a4, 16(a4)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a1, a4, a1  # [op1057] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1058] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e32, m1, ta,ma  # [op1059] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vluxei64.v v5, (a1), v2  # [op1060] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a1, 32  # [op1061] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv1r.v v0, v1  # [op1063] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmerge.vvm v1, v5, v4, v0  # [op1064] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vid.v v2  # [op1065] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vadd.vx v2, v2, t1  # [op1066] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op1067] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vwadd.vx v4, v2, x0  # [op1069] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op1070] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1071] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a1, 4  # [op1072] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmul.vx v2, v4, a1  # [op1073] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a1, 14656  # [op1074] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
ld a4, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
ld a4, 16(a4)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a1, a4, a1  # [op1075] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1076] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e32, m1, ta,ma  # [op1077] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsuxei64.v v1, (a1), v2  # [op1078] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a1, 32  # [op1079] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op1081] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add s1, s1, a1  # [op1082] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op1083] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t1, t1, a1  # [op1084] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op1085] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk20_head  # [op1087] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk21_head:  # block chunk21_head
li a1, 32  # [op1088] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt a1, t1, a1  # [op1089] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne a1, zero, .Lbrc1090_true  # [op1090] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, s1  # [op1090] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv s1, t0  # [op1090] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk21_exit  # [op1090] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc1090_true:  # [op1090] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk21_body  # [op1090] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk21_exit:  # block chunk21_exit
li s1, 0  # [op1091] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t1, 96(sp)  # [op1092] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, s1  # [op1092] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s1, 96(sp)  # [op1092] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk22_head  # [op1092] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk21_body:  # block chunk21_body
li a1, 32  # [op1093] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli a1, a1, e32, m1, ta,ma  # [op1094] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li a1, 32  # [op1095] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vid.v v1  # [op1097] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vadd.vx v1, v1, t1  # [op1098] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
    # [peephole-li] [op1099] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vwadd.vx v2, v1, x0  # [op1101] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
    # [peephole-li] [op1102] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vsetvli a1, a1, e64, m2, ta,ma  # [op1103] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li a1, 4  # [op1104] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vmul.vx v2, v2, a1  # [op1105] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li a1, 1408  # [op1106] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
ld a4, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
ld a4, 16(a4)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
add a1, a4, a1  # [op1107] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li a4, 32  # [op1108] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vsetvli a4, a4, e32, m1, ta,ma  # [op1109] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vluxei64.v v1, (a1), v2  # [op1110] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li a1, 32  # [op1111] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vid.v v2  # [op1113] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vadd.vx v2, v2, t1  # [op1114] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
    # [peephole-li] [op1115] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vwadd.vx v4, v2, x0  # [op1117] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
    # [peephole-li] [op1118] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vsetvli a1, a1, e64, m2, ta,ma  # [op1119] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li a1, 4  # [op1120] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vmul.vx v2, v4, a1  # [op1121] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li a1, 16832  # [op1122] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
ld a4, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
ld a4, 16(a4)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
add a1, a4, a1  # [op1123] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li a4, 32  # [op1124] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vsetvli a4, a4, e32, m1, ta,ma  # [op1125] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vluxei64.v v4, (a1), v2  # [op1126] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li a1, 32  # [op1127] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vmul.vv v1, v1, v4  # [op1129] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vid.v v2  # [op1130] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vadd.vx v2, v2, t1  # [op1131] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
    # [peephole-li] [op1132] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vwadd.vx v4, v2, x0  # [op1134] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
    # [peephole-li] [op1135] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vsetvli a1, a1, e64, m2, ta,ma  # [op1136] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li a1, 4  # [op1137] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vmul.vx v2, v4, a1  # [op1138] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li a1, 16960  # [op1139] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
ld a4, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
ld a4, 16(a4)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
add a1, a4, a1  # [op1140] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li a4, 32  # [op1141] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vsetvli a4, a4, e32, m1, ta,ma  # [op1142] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vsuxei64.v v1, (a1), v2  # [op1143] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li a1, 32  # [op1144] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
    # [peephole-li] [op1146] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add s1, s1, a1  # [op1147] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op1148] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t1, t1, a1  # [op1149] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op1150] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk21_head  # [op1152] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk22_head:  # block chunk22_head
li a1, 512  # [op1153] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt a1, t1, a1  # [op1154] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne a1, zero, .Lbrc1155_true  # [op1155] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, s1  # [op1155] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv s1, t0  # [op1155] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk22_exit  # [op1155] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc1155_true:  # [op1155] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk22_body  # [op1155] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk22_exit:  # block chunk22_exit
li s1, 0  # [op1156] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t1, 96(sp)  # [op1157] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, s1  # [op1157] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s1, 96(sp)  # [op1157] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk23_head  # [op1157] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk22_body:  # block chunk22_body
li a1, 32  # [op1158] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli a1, a1, e32, m1, ta,ma  # [op1159] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li a1, 32  # [op1160] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
vid.v v1  # [op1162] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
vadd.vx v1, v1, t1  # [op1163] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
li a1, 16  # [op1164] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
vmv.v.x v2, a1  # [op1165] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
vdiv.vv v1, v1, v2  # [op1166] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
li a1, 32  # [op1167] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
vwadd.vx v2, v1, x0  # [op1169] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
    # [peephole-li] [op1170] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
vsetvli a1, a1, e64, m2, ta,ma  # [op1171] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
li a1, 8  # [op1172] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
vmul.vx v2, v2, a1  # [op1173] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
li a1, 17088  # [op1174] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
ld a4, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
ld a4, 16(a4)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
add a1, a4, a1  # [op1175] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
li a4, 32  # [op1176] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
vluxei64.v v4, (a1), v2  # [op1178] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
li a1, 32  # [op1179] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
vsetvli a1, a1, e32, m1, ta,ma  # [op1180] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
li a1, 32  # [op1181] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add s1, s1, a1  # [op1182] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op1183] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t1, t1, a1  # [op1184] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op1185] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk22_head  # [op1187] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk23_head:  # block chunk23_head
li a1, 32  # [op1188] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt a1, t1, a1  # [op1189] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne a1, zero, .Lbrc1190_true  # [op1190] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t0  # [op1190] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk23_exit  # [op1190] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc1190_true:  # [op1190] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk23_body  # [op1190] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk23_exit:  # block chunk23_exit
li t1, 0  # [op1191] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
j .Lstg24_head  # [op1192] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
.Lchunk23_body:  # block chunk23_body
li a1, 32  # [op1193] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli a1, a1, e32, m1, ta,ma  # [op1194] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li a1, 32  # [op1195] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vid.v v1  # [op1197] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vadd.vx v1, v1, t1  # [op1198] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
    # [peephole-li] [op1199] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vwadd.vx v2, v1, x0  # [op1201] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
    # [peephole-li] [op1202] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vsetvli a1, a1, e64, m2, ta,ma  # [op1203] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li a1, 4  # [op1204] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vmul.vx v2, v2, a1  # [op1205] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li a1, 1408  # [op1206] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
ld a4, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
ld a4, 16(a4)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
add a1, a4, a1  # [op1207] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li a4, 32  # [op1208] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vsetvli a4, a4, e32, m1, ta,ma  # [op1209] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vluxei64.v v1, (a1), v2  # [op1210] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li a1, 32  # [op1211] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vid.v v2  # [op1213] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vadd.vx v2, v2, t1  # [op1214] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
    # [peephole-li] [op1215] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vwadd.vx v4, v2, x0  # [op1217] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
    # [peephole-li] [op1218] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vsetvli a1, a1, e64, m2, ta,ma  # [op1219] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li a1, 4  # [op1220] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vmul.vx v2, v4, a1  # [op1221] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li a1, 21504  # [op1222] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
ld a4, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
ld a4, 16(a4)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
add a1, a4, a1  # [op1223] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li a4, 32  # [op1224] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vsetvli a4, a4, e32, m1, ta,ma  # [op1225] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vluxei64.v v4, (a1), v2  # [op1226] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li a1, 32  # [op1227] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vmslt.vv v1, v1, v4  # [op1229] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vid.v v2  # [op1230] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vadd.vx v2, v2, t1  # [op1231] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
    # [peephole-li] [op1232] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vwadd.vx v4, v2, x0  # [op1234] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
    # [peephole-li] [op1235] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vsetvli a1, a1, e64, m2, ta,ma  # [op1236] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li a1, 4  # [op1237] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vmul.vx v2, v4, a1  # [op1238] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li a1, 21632  # [op1239] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
ld a4, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
ld a4, 16(a4)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
add a1, a4, a1  # [op1240] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li a4, 32  # [op1241] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vsetvli a4, a4, e32, m1, ta,ma  # [op1242] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li a4, 1  # [op1243] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vmv.v.x v4, a4  # [op1244] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li a4, 0  # [op1245] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vmv.v.x v5, a4  # [op1246] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vmv1r.v v0, v1  # [op1247] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vmerge.vvm v1, v5, v4, v0  # [op1248] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vsuxei64.v v1, (a1), v2  # [op1249] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li a1, 32  # [op1250] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add s1, s1, a1  # [op1251] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op1252] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t1, t1, a1  # [op1253] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op1254] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk23_head  # [op1256] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lstg24_head:  # block stg24_head
li a1, 512  # [op1257] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
slt a1, t1, a1  # [op1258] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
bne a1, zero, .Lbrc1259_true  # [op1259] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
j .Lstg24_exit  # [op1259] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
.Lbrc1259_true:  # [op1259] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
j .Lstg24_body  # [op1259] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
.Lstg24_body:  # block stg24_body
li a1, 32  # [op1260] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli a1, a1, e32, m1, ta,ma  # [op1261] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vid.v v1  # [op1262] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vadd.vx v1, v1, t1  # [op1263] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a1, 16  # [op1264] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv.v.x v2, a1  # [op1265] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vdiv.vv v2, v1, v2  # [op1266] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a1, 32  # [op1267] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv.v.x v3, a1  # [op1268] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vrem.vv v2, v2, v3  # [op1269] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a1, 16  # [op1270] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv.v.x v3, a1  # [op1271] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vrem.vv v3, v1, v3  # [op1272] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a1, 32  # [op1273] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vwadd.vx v4, v2, x0  # [op1275] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
    # [peephole-li] [op1276] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli a1, a1, e64, m2, ta,ma  # [op1277] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a1, 4  # [op1278] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmul.vx v2, v4, a1  # [op1279] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a1, 21632  # [op1280] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld a4, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld a4, 16(a4)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
add a1, a4, a1  # [op1281] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a4, 32  # [op1282] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli a4, a4, e32, m1, ta,ma  # [op1283] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vluxei64.v v4, (a1), v2  # [op1284] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a1, 32  # [op1285] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vwadd.vx v2, v1, x0  # [op1287] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
    # [peephole-li] [op1288] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli a1, a1, e64, m2, ta,ma  # [op1289] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a1, 4  # [op1290] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmul.vx v2, v2, a1  # [op1291] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a1, 21888  # [op1292] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld a4, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld a4, 16(a4)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
add a1, a4, a1  # [op1293] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a4, 32  # [op1294] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli a4, a4, e32, m1, ta,ma  # [op1295] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsuxei64.v v4, (a1), v2  # [op1296] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a1, 32  # [op1297] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
addw t1, t1, a1  # [op1298] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
j .Lstg24_head  # [op1299] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
.Lstg24_exit:  # block stg24_exit
li t1, 0  # [op1300] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk25_head  # [op1301] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk25_head:  # block chunk25_head
li a1, 512  # [op1302] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt a1, t1, a1  # [op1303] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne a1, zero, .Lbrc1304_true  # [op1304] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t0  # [op1304] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk25_exit  # [op1304] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc1304_true:  # [op1304] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk25_body  # [op1304] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk25_exit:  # block chunk25_exit
li t1, 14656  # [op1305] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s1, 16(s1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s8, s1, t1  # [op1306] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t1, 30080  # [op1307] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s1, 16(s1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s9, s1, t1  # [op1308] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t1, 32128  # [op1309] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s1, 16(s1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s10, s1, t1  # [op1310] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t1, 256  # [op1311] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s1, 16(s1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a4, s1, t1  # [op1312] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t1, 0  # [op1313] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s11, 16  # [op1314] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lvrm26.head  # [op1315] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lchunk25_body:  # block chunk25_body
li a1, 32  # [op1316] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli a1, a1, e32, m1, ta,ma  # [op1317] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li a1, 32  # [op1318] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vid.v v1  # [op1320] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vadd.vx v1, v1, t1  # [op1321] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
    # [peephole-li] [op1322] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vwadd.vx v2, v1, x0  # [op1324] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
    # [peephole-li] [op1325] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli a1, a1, e64, m2, ta,ma  # [op1326] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a1, 4  # [op1327] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmul.vx v2, v2, a1  # [op1328] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a1, 21888  # [op1329] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld a4, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld a4, 16(a4)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
add a1, a4, a1  # [op1330] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a4, 32  # [op1331] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli a4, a4, e32, m1, ta,ma  # [op1332] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vluxei64.v v1, (a1), v2  # [op1333] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a1, 0  # [op1334] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv.v.x v2, a1  # [op1335] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmsne.vv v1, v1, v2  # [op1336] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a1, 32  # [op1337] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vid.v v2  # [op1339] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vadd.vx v2, v2, t1  # [op1340] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
    # [peephole-li] [op1341] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vwadd.vx v4, v2, x0  # [op1343] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
    # [peephole-li] [op1344] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli a1, a1, e64, m2, ta,ma  # [op1345] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a1, 4  # [op1346] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmul.vx v2, v4, a1  # [op1347] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a1, 23936  # [op1348] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld a4, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld a4, 16(a4)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
add a1, a4, a1  # [op1349] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a4, 32  # [op1350] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli a4, a4, e32, m1, ta,ma  # [op1351] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vluxei64.v v4, (a1), v2  # [op1352] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a1, 0  # [op1353] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv.v.x v2, a1  # [op1354] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmsne.vv v2, v4, v2  # [op1355] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a1, 32  # [op1356] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmand.mm v1, v1, v2  # [op1358] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vid.v v2  # [op1359] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vadd.vx v2, v2, t1  # [op1360] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
    # [peephole-li] [op1361] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vwadd.vx v4, v2, x0  # [op1363] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
    # [peephole-li] [op1364] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli a1, a1, e64, m2, ta,ma  # [op1365] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a1, 4  # [op1366] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmul.vx v2, v4, a1  # [op1367] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a1, 25984  # [op1368] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld a4, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld a4, 16(a4)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
add a1, a4, a1  # [op1369] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a4, 32  # [op1370] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli a4, a4, e32, m1, ta,ma  # [op1371] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a4, 1  # [op1372] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv.v.x v4, a4  # [op1373] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a4, 0  # [op1374] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv.v.x v5, a4  # [op1375] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv1r.v v0, v1  # [op1376] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmerge.vvm v4, v5, v4, v0  # [op1377] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsuxei64.v v4, (a1), v2  # [op1378] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vid.v v2  # [op1379] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vadd.vx v2, v2, t1  # [op1380] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a1, 32  # [op1381] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vwadd.vx v4, v2, x0  # [op1383] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
    # [peephole-li] [op1384] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli a1, a1, e64, m2, ta,ma  # [op1385] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a1, 4  # [op1386] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmul.vx v2, v4, a1  # [op1387] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a1, 25984  # [op1388] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld a4, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld a4, 16(a4)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
add a1, a4, a1  # [op1389] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a4, 32  # [op1390] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli a4, a4, e32, m1, ta,ma  # [op1391] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a4, 1  # [op1392] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv.v.x v4, a4  # [op1393] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a4, 0  # [op1394] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv.v.x v5, a4  # [op1395] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv1r.v v0, v1  # [op1396] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmerge.vvm v4, v5, v4, v0  # [op1397] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsuxei64.v v4, (a1), v2  # [op1398] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vid.v v2  # [op1399] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vadd.vx v2, v2, t1  # [op1400] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a1, 16  # [op1401] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.x v3, a1  # [op1402] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vdiv.vv v2, v2, v3  # [op1403] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a1, 32  # [op1404] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vwadd.vx v4, v2, x0  # [op1406] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
    # [peephole-li] [op1407] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1408] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a1, 4  # [op1409] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmul.vx v2, v4, a1  # [op1410] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a1, 16960  # [op1411] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
ld a4, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
ld a4, 16(a4)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a1, a4, a1  # [op1412] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op1413] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e32, m1, ta,ma  # [op1414] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vluxei64.v v4, (a1), v2  # [op1415] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a1, 32  # [op1416] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vid.v v2  # [op1418] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vadd.vx v2, v2, t1  # [op1419] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a1, 16  # [op1420] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.x v3, a1  # [op1421] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vrem.vv v2, v2, v3  # [op1422] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a1, 32  # [op1423] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vwadd.vx v6, v2, x0  # [op1425] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
    # [peephole-li] [op1426] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1427] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a1, 4  # [op1428] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmul.vx v2, v6, a1  # [op1429] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a1, 64  # [op1430] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
ld a4, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
ld a4, 16(a4)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a1, a4, a1  # [op1431] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op1432] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e32, m1, ta,ma  # [op1433] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vluxei64.v v5, (a1), v2  # [op1434] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a1, 32  # [op1435] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vadd.vv v2, v4, v5  # [op1437] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
    # [peephole-li] [op1438] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vwadd.vx v4, v2, x0  # [op1440] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
    # [peephole-li] [op1441] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1442] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a1, 4  # [op1443] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmul.vx v2, v4, a1  # [op1444] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a1, 32  # [op1445] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a1, a1, e32, m1, ta,ma  # [op1446] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv1r.v v0, v1  # [op1447] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vluxei64.v v4, (s3), v2, v0.t  # [op1448] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a1, 32  # [op1449] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vid.v v2  # [op1451] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vadd.vx v2, v2, t1  # [op1452] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
    # [peephole-li] [op1453] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vwadd.vx v6, v2, x0  # [op1455] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
    # [peephole-li] [op1456] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1457] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a1, 4  # [op1458] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmul.vx v2, v6, a1  # [op1459] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a1, 28032  # [op1460] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
ld a4, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
ld a4, 16(a4)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a1, a4, a1  # [op1461] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op1462] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e32, m1, ta,ma  # [op1463] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vluxei64.v v5, (a1), v2  # [op1464] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a1, 32  # [op1465] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv1r.v v0, v1  # [op1467] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmerge.vvm v1, v5, v4, v0  # [op1468] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vid.v v2  # [op1469] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vadd.vx v2, v2, t1  # [op1470] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
    # [peephole-li] [op1471] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vwadd.vx v4, v2, x0  # [op1473] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
    # [peephole-li] [op1474] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1475] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a1, 4  # [op1476] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmul.vx v2, v4, a1  # [op1477] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a1, 30080  # [op1478] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
ld a4, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
ld a4, 16(a4)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a1, a4, a1  # [op1479] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op1480] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e32, m1, ta,ma  # [op1481] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsuxei64.v v1, (a1), v2  # [op1482] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a1, 32  # [op1483] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
    # [peephole-li] [op1485] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add s1, s1, a1  # [op1486] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op1487] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t1, t1, a1  # [op1488] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op1489] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk25_head  # [op1491] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lvrm26.head:  # block vrm26.head
sd t1, 144(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t1, 144(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt s1, t1, s11  # [op1492] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t1, 144(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
bne s1, zero, .Lbrc1493_true  # [op1493] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lvrm26.exit  # [op1493] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lbrc1493_true:  # [op1493] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lvrm26.body  # [op1493] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lvrm26.body:  # block vrm26.body
sd t1, 144(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t1, 0  # [op1494] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t3, 16  # [op1495] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lvrc27.head  # [op1496] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lvrm26.exit:  # block vrm26.exit
addw t2, t2, s7  # [op1497] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
li s1, 32128  # [op1498] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
li a1, 256  # [op1499] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
li t1, 0  # [op1500] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
li a4, 256  # [op1501] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
li a5, 32  # [op1502] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
j .Lmcarry29.head  # [op1503] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
.Lvrc27.head:  # block vrc27.head
sd t1, 152(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t1, 152(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt s1, t1, t3  # [op1504] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t1, 152(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
bne s1, zero, .Lbrc1505_true  # [op1505] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lvrc27.exit  # [op1505] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lbrc1505_true:  # [op1505] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lvrc27.body  # [op1505] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lvrc27.body:  # block vrc27.body
sd t1, 152(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t1, 128  # [op1506] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s1, 144(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul t1, s1, t1  # [op1507] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a1, s8, t1  # [op1508] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t1, 4  # [op1509] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s1, 152(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul s1, s1, t1  # [op1510] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t4, s9, s1  # [op1511] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s1, 64  # [op1512] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a5, 144(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul a5, a5, s1  # [op1513] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t5, 152(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul t1, t5, t1  # [op1514] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t1, a5, t1  # [op1515] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a5, s10, t1  # [op1516] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t5, 16  # [op1517] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vsetvli t5, t5, e32, m1, ta,ma  # [op1518] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t5, 0  # [op1519] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv.v.x v1, t5  # [op1520] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t5, a4, t1  # [op1521] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t6, 16  # [op1522] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle32.v v1, 0(t5)  # [op1524] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t1, a4, t1  # [op1525] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t1, t1, s1  # [op1526] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s1, 16  # [op1527] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle32.v v2, 0(t1)  # [op1529] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t1, 0  # [op1530] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t5, 32  # [op1531] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mv s1, t1  # [op1532] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mv t1, a1  # [op1532] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mv a1, t4  # [op1532] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lvrk28.head  # [op1532] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lvrc27.exit:  # block vrc27.exit
li t1, 2  # [op1533] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s1, 144(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t1, s1, t1  # [op1534] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lvrm26.head  # [op1535] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lvrk28.head:  # block vrk28.head
slt t4, s1, t5  # [op1536] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
bne t4, zero, .Lbrc1537_true  # [op1537] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sd t1, 96(sp)  # [op1537] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mv t1, s1  # [op1537] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s1, 96(sp)  # [op1537] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lvrk28.exit  # [op1537] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lbrc1537_true:  # [op1537] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lvrk28.body  # [op1537] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lvrk28.body:  # block vrk28.body
li t4, 16  # [op1538] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vsetvli t4, t4, e32, m1, ta,ma  # [op1539] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle32.v v3, 0(a1)  # [op1540] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
lw t4, 0(t1)  # [op1541] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t6, 16  # [op1542] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv.v.x v4, t4  # [op1544] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vfmacc.vv v1, v3, v4  # [op1545] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t4, 128  # [op1546] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t4, t1, t4  # [op1547] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
lw t4, 0(t4)  # [op1548] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
    # [peephole-li] [op1549] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv.v.x v4, t4  # [op1551] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vfmacc.vv v2, v3, v4  # [op1552] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t4, 1  # [op1553] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s1, s1, t4  # [op1554] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t4, 4  # [op1555] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t1, t1, t4  # [op1556] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t4, 64  # [op1557] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a1, a1, t4  # [op1558] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lvrk28.head  # [op1559] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lvrk28.exit:  # block vrk28.exit
li t1, 16  # [op1560] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vsetvli t1, t1, e32, m1, ta,ma  # [op1561] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse32.v v1, 0(a5)  # [op1562] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t1, 64  # [op1563] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t1, a5, t1  # [op1564] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s1, 16  # [op1565] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse32.v v2, 0(t1)  # [op1567] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t1, 16  # [op1568] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s1, 152(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t1, s1, t1  # [op1569] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lvrc27.head  # [op1570] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lmcarry29.head:  # block mcarry29.head
slt s8, t1, a4  # [op1571] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
bne s8, zero, .Lbrc1572_true  # [op1572] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
j .Lmcarry29.exit  # [op1572] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
.Lbrc1572_true:  # [op1572] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
j .Lmcarry29.body  # [op1572] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
.Lmcarry29.body:  # block mcarry29.body
ld s8, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
ld s8, 16(s8)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
add s8, s8, s1  # [op1573] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
ld s9, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
ld s9, 16(s9)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
add s9, s9, a1  # [op1574] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
li s10, 32  # [op1575] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
vsetvli s10, s10, e32, m1, ta,ma  # [op1576] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
vid.v v1  # [op1577] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
vadd.vx v1, v1, t1  # [op1578] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
li s10, 32  # [op1579] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
vwadd.vx v2, v1, x0  # [op1581] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
    # [peephole-li] [op1582] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
vsetvli s10, s10, e64, m2, ta,ma  # [op1583] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
li s10, 4  # [op1584] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
vmul.vx v2, v2, s10  # [op1585] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
li s10, 32  # [op1586] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
vsetvli s10, s10, e32, m1, ta,ma  # [op1587] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
vluxei64.v v1, (s8), v2  # [op1588] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
vsuxei64.v v1, (s9), v2  # [op1589] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
li s8, 16  # [op1590] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
vsetvli s8, s8, e32, m1, ta,ma  # [op1591] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
addw t1, t1, a5  # [op1592] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
j .Lmcarry29.head  # [op1593] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
.Lmcarry29.exit:  # block mcarry29.exit
j .Lmloop15.head  # [op1594] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
.Lchunk30_head:  # block chunk30_head
li s1, 16  # [op1595] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t1, s1  # [op1596] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc1597_true  # [op1597] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op1597] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t2, t0  # [op1597] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk30_exit  # [op1597] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc1597_true:  # [op1597] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk30_body  # [op1597] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk30_exit:  # block chunk30_exit
li t2, 0  # [op1598] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t1, 96(sp)  # [op1599] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op1599] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t2, 96(sp)  # [op1599] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk31_head  # [op1599] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk30_body:  # block chunk30_body
li s1, 16  # [op1600] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op1601] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 16  # [op1602] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vmv.v.x v1, a2  # [op1604] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vid.v v2  # [op1605] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vadd.vx v2, v2, t1  # [op1606] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
    # [peephole-li] [op1607] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vwadd.vx v4, v2, x0  # [op1609] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
    # [peephole-li] [op1610] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vsetvli s1, s1, e64, m2, ta,ma  # [op1611] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
li s1, 4  # [op1612] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vmul.vx v2, v4, s1  # [op1613] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
li s1, 0  # [op1614] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
add s1, a1, s1  # [op1615] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
li a1, 16  # [op1616] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vsetvli a1, a1, e32, m1, ta,ma  # [op1617] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vluxei64.v v4, (s1), v2  # [op1618] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
li s1, 16  # [op1619] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vmul.vv v1, v4, v1  # [op1621] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vid.v v2  # [op1622] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vadd.vx v2, v2, t1  # [op1623] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
    # [peephole-li] [op1624] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vwadd.vx v4, v2, x0  # [op1626] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
    # [peephole-li] [op1627] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vsetvli s1, s1, e64, m2, ta,ma  # [op1628] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
li s1, 4  # [op1629] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vmul.vx v2, v4, s1  # [op1630] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
li s1, 33152  # [op1631] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
add s1, a1, s1  # [op1632] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
li a1, 16  # [op1633] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vsetvli a1, a1, e32, m1, ta,ma  # [op1634] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vsuxei64.v v1, (s1), v2  # [op1635] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
li s1, 16  # [op1636] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
    # [peephole-li] [op1638] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t2, t2, s1  # [op1639] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op1640] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t1, t1, s1  # [op1641] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op1642] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk30_head  # [op1644] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk31_head:  # block chunk31_head
li s1, 256  # [op1645] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t1, s1  # [op1646] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc1647_true  # [op1647] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t0  # [op1647] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk31_exit  # [op1647] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc1647_true:  # [op1647] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk31_body  # [op1647] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk31_exit:  # block chunk31_exit
li t1, 0  # [op1648] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
j .Lstg32_head  # [op1649] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
.Lchunk31_body:  # block chunk31_body
li s1, 32  # [op1650] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op1651] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op1652] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
vid.v v1  # [op1654] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
vadd.vx v1, v1, t1  # [op1655] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
li s1, 16  # [op1656] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
vmv.v.x v2, s1  # [op1657] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
vdiv.vv v1, v1, v2  # [op1658] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
li s1, 32  # [op1659] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
vwadd.vx v2, v1, x0  # [op1661] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
    # [peephole-li] [op1662] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
vsetvli s1, s1, e64, m2, ta,ma  # [op1663] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
li s1, 8  # [op1664] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
vmul.vx v2, v2, s1  # [op1665] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
li s1, 33216  # [op1666] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
add s1, a1, s1  # [op1667] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
li a1, 32  # [op1668] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
vluxei64.v v4, (s1), v2  # [op1670] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
li s1, 32  # [op1671] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
vsetvli s1, s1, e32, m1, ta,ma  # [op1672] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
li s1, 32  # [op1673] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t2, t2, s1  # [op1674] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op1675] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t1, t1, s1  # [op1676] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op1677] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk31_head  # [op1679] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lstg32_head:  # block stg32_head
li s1, 256  # [op1680] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
slt s1, t1, s1  # [op1681] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
bne s1, zero, .Lbrc1682_true  # [op1682] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
j .Lstg32_exit  # [op1682] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
.Lbrc1682_true:  # [op1682] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
j .Lstg32_body  # [op1682] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
.Lstg32_body:  # block stg32_body
li s1, 32  # [op1683] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli s1, s1, e32, m1, ta,ma  # [op1684] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vid.v v1  # [op1685] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vadd.vx v1, v1, t1  # [op1686] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 16  # [op1687] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmv.v.x v2, s1  # [op1688] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vdiv.vv v2, v1, v2  # [op1689] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op1690] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmv.v.x v3, s1  # [op1691] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vrem.vv v2, v2, v3  # [op1692] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op1693] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmv.v.x v3, s1  # [op1694] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vrem.vv v3, v1, v3  # [op1695] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 32  # [op1696] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vwadd.vx v4, v2, x0  # [op1698] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op1699] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli s1, s1, e64, m2, ta,ma  # [op1700] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 4  # [op1701] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmul.vx v2, v4, s1  # [op1702] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 6144  # [op1703] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
add s1, a1, s1  # [op1704] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li a1, 32  # [op1705] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli a1, a1, e32, m1, ta,ma  # [op1706] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vluxei64.v v4, (s1), v2  # [op1707] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 32  # [op1708] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vwadd.vx v2, v1, x0  # [op1710] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op1711] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli s1, s1, e64, m2, ta,ma  # [op1712] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 4  # [op1713] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmul.vx v2, v2, s1  # [op1714] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 35392  # [op1715] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
add s1, a1, s1  # [op1716] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li a1, 32  # [op1717] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli a1, a1, e32, m1, ta,ma  # [op1718] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsuxei64.v v4, (s1), v2  # [op1719] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 32  # [op1720] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
addw t1, t1, s1  # [op1721] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
j .Lstg32_head  # [op1722] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
.Lstg32_exit:  # block stg32_exit
li t1, 0  # [op1723] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
j .Lstg33_head  # [op1724] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
.Lstg33_head:  # block stg33_head
li s1, 256  # [op1725] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
slt s1, t1, s1  # [op1726] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
bne s1, zero, .Lbrc1727_true  # [op1727] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
j .Lstg33_exit  # [op1727] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
.Lbrc1727_true:  # [op1727] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
j .Lstg33_body  # [op1727] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
.Lstg33_body:  # block stg33_body
li s1, 32  # [op1728] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli s1, s1, e32, m1, ta,ma  # [op1729] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vid.v v1  # [op1730] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vadd.vx v1, v1, t1  # [op1731] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 16  # [op1732] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmv.v.x v2, s1  # [op1733] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vdiv.vv v2, v1, v2  # [op1734] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op1735] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmv.v.x v3, s1  # [op1736] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vrem.vv v2, v2, v3  # [op1737] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op1738] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmv.v.x v2, s1  # [op1739] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vrem.vv v2, v1, v2  # [op1740] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 32  # [op1741] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vwadd.vx v4, v2, x0  # [op1743] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op1744] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli s1, s1, e64, m2, ta,ma  # [op1745] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 4  # [op1746] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmul.vx v2, v4, s1  # [op1747] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 21824  # [op1748] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
add s1, a1, s1  # [op1749] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li a1, 32  # [op1750] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli a1, a1, e32, m1, ta,ma  # [op1751] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vluxei64.v v4, (s1), v2  # [op1752] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 32  # [op1753] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vwadd.vx v2, v1, x0  # [op1755] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op1756] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli s1, s1, e64, m2, ta,ma  # [op1757] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 4  # [op1758] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmul.vx v2, v2, s1  # [op1759] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 36416  # [op1760] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
add s1, a1, s1  # [op1761] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li a1, 32  # [op1762] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli a1, a1, e32, m1, ta,ma  # [op1763] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsuxei64.v v4, (s1), v2  # [op1764] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 32  # [op1765] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
addw t1, t1, s1  # [op1766] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
j .Lstg33_head  # [op1767] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
.Lstg33_exit:  # block stg33_exit
li t1, 0  # [op1768] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk34_head  # [op1769] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk34_head:  # block chunk34_head
li s1, 256  # [op1770] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t1, s1  # [op1771] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc1772_true  # [op1772] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op1772] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t2, t0  # [op1772] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk34_exit  # [op1772] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc1772_true:  # [op1772] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk34_body  # [op1772] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk34_exit:  # block chunk34_exit
j .Lprog_next  # [op1773] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk34_body:  # block chunk34_body
li s1, 32  # [op1774] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op1775] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op1776] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vid.v v1  # [op1778] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vadd.vx v1, v1, t1  # [op1779] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op1780] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vwadd.vx v2, v1, x0  # [op1782] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op1783] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli s1, s1, e64, m2, ta,ma  # [op1784] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 4  # [op1785] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmul.vx v2, v2, s1  # [op1786] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 35392  # [op1787] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
add s1, a1, s1  # [op1788] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li a1, 32  # [op1789] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli a1, a1, e32, m1, ta,ma  # [op1790] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vluxei64.v v1, (s1), v2  # [op1791] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 0  # [op1792] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmv.v.x v2, s1  # [op1793] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmsne.vv v1, v1, v2  # [op1794] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 32  # [op1795] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vid.v v2  # [op1797] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vadd.vx v2, v2, t1  # [op1798] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op1799] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vwadd.vx v4, v2, x0  # [op1801] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op1802] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli s1, s1, e64, m2, ta,ma  # [op1803] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 4  # [op1804] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmul.vx v2, v4, s1  # [op1805] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 36416  # [op1806] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
add s1, a1, s1  # [op1807] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li a1, 32  # [op1808] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli a1, a1, e32, m1, ta,ma  # [op1809] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vluxei64.v v4, (s1), v2  # [op1810] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 0  # [op1811] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmv.v.x v2, s1  # [op1812] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmsne.vv v2, v4, v2  # [op1813] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 32  # [op1814] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmand.mm v1, v1, v2  # [op1816] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vid.v v2  # [op1817] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vadd.vx v2, v2, t1  # [op1818] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li s1, 16  # [op1819] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.v.x v3, s1  # [op1820] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vdiv.vv v2, v2, v3  # [op1821] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li s1, 32  # [op1822] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vwadd.vx v4, v2, x0  # [op1824] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
    # [peephole-li] [op1825] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli s1, s1, e64, m2, ta,ma  # [op1826] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li s1, 4  # [op1827] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmul.vx v2, v4, s1  # [op1828] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li s1, 33152  # [op1829] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add s1, a1, s1  # [op1830] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a1, 32  # [op1831] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli a1, a1, e32, m1, ta,ma  # [op1832] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vluxei64.v v4, (s1), v2  # [op1833] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li s1, 32  # [op1834] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vid.v v2  # [op1836] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vadd.vx v2, v2, t1  # [op1837] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li s1, 16  # [op1838] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.v.x v3, s1  # [op1839] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vrem.vv v2, v2, v3  # [op1840] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li s1, 32  # [op1841] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vwadd.vx v6, v2, x0  # [op1843] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
    # [peephole-li] [op1844] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli s1, s1, e64, m2, ta,ma  # [op1845] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li s1, 4  # [op1846] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmul.vx v2, v6, s1  # [op1847] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li s1, 64  # [op1848] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add s1, a1, s1  # [op1849] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a1, 32  # [op1850] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli a1, a1, e32, m1, ta,ma  # [op1851] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vluxei64.v v5, (s1), v2  # [op1852] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li s1, 32  # [op1853] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vadd.vv v2, v4, v5  # [op1855] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vid.v v3  # [op1856] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vadd.vx v3, v3, t1  # [op1857] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
    # [peephole-li] [op1858] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vwadd.vx v4, v3, x0  # [op1860] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
    # [peephole-li] [op1861] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli s1, s1, e64, m2, ta,ma  # [op1862] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li s1, 4  # [op1863] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmul.vx v4, v4, s1  # [op1864] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li s1, 256  # [op1865] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
ld a1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
ld a1, 16(a1)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add s1, a1, s1  # [op1866] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a1, 32  # [op1867] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli a1, a1, e32, m1, ta,ma  # [op1868] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vluxei64.v v3, (s1), v4  # [op1869] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li s1, 32  # [op1870] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
    # [peephole-li] [op1872] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vwadd.vx v4, v2, x0  # [op1874] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
    # [peephole-li] [op1875] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli s1, s1, e64, m2, ta,ma  # [op1876] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li s1, 4  # [op1877] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmul.vx v4, v4, s1  # [op1878] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li s1, 32  # [op1879] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli s1, s1, e32, m1, ta,ma  # [op1880] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li s1, 32  # [op1881] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv1r.v v0, v1  # [op1883] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsuxei64.v v3, (s4), v4, v0.t  # [op1884] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vcpop.m s1, v1  # [op1885] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add t2, t2, s1  # [op1886] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op1887] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t1, t1, s1  # [op1888] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op1889] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk34_head  # [op1891] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lprog_next:  # block prog_next
add t0, t0, s6  # [op1892] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lprog_head  # [op1893] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lprog_exit:  # block prog_exit
sd t0, 0(a6)  # [op1894] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld ra, 0(sp)  # [op1895] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s1, 8(sp)  # [op1895] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s2, 16(sp)  # [op1895] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s3, 24(sp)  # [op1895] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s4, 32(sp)  # [op1895] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s5, 40(sp)  # [op1895] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s6, 48(sp)  # [op1895] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s7, 56(sp)  # [op1895] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s8, 64(sp)  # [op1895] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s9, 72(sp)  # [op1895] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s10, 80(sp)  # [op1895] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s11, 88(sp)  # [op1895] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addi sp, sp, 160  # [op1895] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ret  # [op1895] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    .size operator_entry, .-operator_entry
    .section .note.GNU-stack,"",@progbits
