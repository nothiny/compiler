# a100c emitted program: matmul_kernel
# source: tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py
# specialization identity: 2645ca7f8d56a638
# compiler revision: b5c42fbb75a242a8
# target model: a100-rvv1-vlen1024/1 (VLEN=1024, file=4096B)
# options: default
# argument layout: d915c0c98980c5e6
# every instruction below traces to a selected MIR op: [opN] carries the source location
# passes: passes=default
    .text
    .globl operator_workspace_private
    .type operator_workspace_private, @function
operator_workspace_private:
    li a0, 36040
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
    # [peephole] removed 0 redundant vsetvli, 164 redundant li
operator_entry:  # fn operator_entry
addi sp, sp, -240
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
ld t0, 0(t0)  # [op0] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 0(t0)  # [op1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t1, 128(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t0, 8(t0)  # [op2] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s6, 24(t1)  # [op3] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
lwu t1, 40(t1)  # [op4] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t2, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
lwu t2, 44(t2)  # [op5] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s1, 8(t0)  # [op6] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addiw s1, s1, 0  # [op7] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd s1, 120(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s1, 24(t0)  # [op8] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd s1, 144(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s1, 144(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addiw s7, s1, 0  # [op9] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t0, 40(t0)  # [op10] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t0, 152(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t0, 152(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addiw t0, t0, 0  # [op11] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t0, 136(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t0, 128(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s8, 0(t0)  # [op12] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t0, 128(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t0, 56(t0)  # [op13] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t0, 160(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t0, 128(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t0, 112(t0)  # [op14] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t0, 168(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li t0, 15  # [op15] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s1, 144(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t0, s1, t0  # [op16] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 16  # [op17] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
divu t0, t0, s1  # [op18] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t0, 176(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li t0, 15  # [op19] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s1, 152(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t0, s1, t0  # [op20] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 16  # [op21] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
divu t0, t0, s1  # [op22] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t0, 184(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li t0, 1  # [op23] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s1, 176(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mul t0, t0, s1  # [op24] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s1, 184(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mul s9, t0, s1  # [op25] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op26] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv s10, t2  # [op27] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li t1, 0  # [op28] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lprog_head  # [op29] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lprog_head:  # block prog_head
slt t2, t0, s9  # [op30] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
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
ld t1, 176(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
divu t1, t2, t1  # [op33] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s1, 176(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mul t1, t1, s1  # [op34] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sub s1, t2, t1  # [op35] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 176(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mul t0, t0, t1  # [op36] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
divu t1, t2, t0  # [op37] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld a2, 184(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
divu a2, t1, a2  # [op38] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld a3, 184(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mul a2, a2, a3  # [op39] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sub t1, t1, a2  # [op40] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld a2, 184(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mul t0, t0, a2  # [op41] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addiw t0, s1, 0  # [op42] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addiw a2, t1, 0  # [op43] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 176(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addiw t1, t1, 0  # [op44] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 184(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addiw t1, t1, 0  # [op45] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 16(t1)  # [op46] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 8(t1)  # [op47] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 4  # [op48] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:14
sllw a3, t0, s1  # [op49] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:14
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
vmv.v.x v2, a3  # [op63] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:14
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
ld a4, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:14
add a1, a4, a1  # [op75] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:14
li a4, 16  # [op76] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:14
vsetvli a4, a4, e32, m1, ta,ma  # [op77] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:14
vsuxei64.v v2, (a1), v4  # [op78] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:14
li a1, 16  # [op79] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:25:14
sllw a1, a2, s1  # [op81] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:26:14
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
ld a4, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:26:14
add a1, a4, a1  # [op94] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:26:14
li a4, 16  # [op95] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:26:14
vsetvli a4, a4, e32, m1, ta,ma  # [op96] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:26:14
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
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:27:14
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
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:28:11
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
ld s1, 120(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
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
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
add s1, a1, s1  # [op197] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
li a1, 16  # [op198] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vsetvli a1, a1, e32, m1, ta,ma  # [op199] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vsuxei64.v v1, (s1), v2  # [op200] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
li s1, 16  # [op201] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
vmv.v.x v1, s7  # [op203] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
vid.v v2  # [op204] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
vadd.vx v2, v2, t0  # [op205] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
    # [peephole-li] [op206] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
vwadd.vx v4, v2, x0  # [op208] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
    # [peephole-li] [op209] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
vsetvli s1, s1, e64, m2, ta,ma  # [op210] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
li s1, 4  # [op211] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
vmul.vx v2, v4, s1  # [op212] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
li s1, 6080  # [op213] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
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
ld s1, 120(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
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
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
add s1, a1, s1  # [op247] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li a1, 32  # [op248] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vsetvli a1, a1, e32, m1, ta,ma  # [op249] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vsuxei64.v v1, (s1), v2  # [op250] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li s1, 32  # [op251] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li s1, 0  # [op253] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
ld s1, 136(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vmv.v.x v1, s1  # [op254] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vid.v v2  # [op255] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vadd.vx v2, v2, t0  # [op256] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li s1, 32  # [op257] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vwadd.vx v4, v2, x0  # [op259] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
    # [peephole-li] [op260] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vsetvli s1, s1, e64, m2, ta,ma  # [op261] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li s1, 4  # [op262] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vmul.vx v2, v4, s1  # [op263] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li s1, 15808  # [op264] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
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
ld s1, 120(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vmv.v.x v1, s1  # [op301] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vid.v v2  # [op302] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vadd.vx v2, v2, t0  # [op303] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li s1, 32  # [op304] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vwadd.vx v4, v2, x0  # [op306] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
    # [peephole-li] [op307] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vsetvli s1, s1, e64, m2, ta,ma  # [op308] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li s1, 4  # [op309] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vmul.vx v2, v4, s1  # [op310] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li s1, 20480  # [op311] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
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
ld s1, 136(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vmv.v.x v1, s1  # [op334] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vid.v v2  # [op335] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vadd.vx v2, v2, t0  # [op336] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li s1, 16  # [op337] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vwadd.vx v4, v2, x0  # [op339] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
    # [peephole-li] [op340] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vsetvli s1, s1, e64, m2, ta,ma  # [op341] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li s1, 4  # [op342] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vmul.vx v2, v4, s1  # [op343] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li s1, 20736  # [op344] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
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
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
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
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
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
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:29
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
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
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
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:27
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
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add s1, a1, s1  # [op467] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a1, 32  # [op468] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a1, a1, e16, m1, ta,ma  # [op469] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vfwcvt.f.f.v v4, v1  # [op470] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a1, 32  # [op471] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a1, a1, e32, m1, ta,ma  # [op472] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.v v1, v4  # [op473] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a1, 32  # [op474] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsuxei64.v v1, (s1), v2  # [op476] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li s1, 32  # [op477] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op479] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op480] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op481] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op482] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op483] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk9_head  # [op485] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk10_head:  # block chunk10_head
li s1, 16  # [op486] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op487] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc488_true  # [op488] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op488] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op488] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk10_exit  # [op488] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc488_true:  # [op488] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk10_body  # [op488] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk10_exit:  # block chunk10_exit
li t1, 0  # [op489] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op490] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op490] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op490] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk11_head  # [op490] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk10_body:  # block chunk10_body
li s1, 16  # [op491] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op492] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 16  # [op493] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vid.v v1  # [op495] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vadd.vx v1, v1, t0  # [op496] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
    # [peephole-li] [op497] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vwadd.vx v2, v1, x0  # [op499] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
    # [peephole-li] [op500] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vsetvli s1, s1, e64, m2, ta,ma  # [op501] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li s1, 4  # [op502] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vmul.vx v2, v2, s1  # [op503] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li s1, 64  # [op504] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
add s1, a1, s1  # [op505] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li a1, 16  # [op506] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vsetvli a1, a1, e32, m1, ta,ma  # [op507] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vluxei64.v v1, (s1), v2  # [op508] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li s1, 16  # [op509] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vid.v v2  # [op511] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vadd.vx v2, v2, t0  # [op512] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
    # [peephole-li] [op513] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vwadd.vx v4, v2, x0  # [op515] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
    # [peephole-li] [op516] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vsetvli s1, s1, e64, m2, ta,ma  # [op517] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li s1, 4  # [op518] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vmul.vx v2, v4, s1  # [op519] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li s1, 20736  # [op520] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
add s1, a1, s1  # [op521] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li a1, 16  # [op522] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vsetvli a1, a1, e32, m1, ta,ma  # [op523] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vluxei64.v v4, (s1), v2  # [op524] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li s1, 16  # [op525] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vmslt.vv v1, v1, v4  # [op527] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vid.v v2  # [op528] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vadd.vx v2, v2, t0  # [op529] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
    # [peephole-li] [op530] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vwadd.vx v4, v2, x0  # [op532] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
    # [peephole-li] [op533] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vsetvli s1, s1, e64, m2, ta,ma  # [op534] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li s1, 4  # [op535] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vmul.vx v2, v4, s1  # [op536] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li s1, 20800  # [op537] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
add s1, a1, s1  # [op538] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li a1, 16  # [op539] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vsetvli a1, a1, e32, m1, ta,ma  # [op540] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li a1, 1  # [op541] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vmv.v.x v4, a1  # [op542] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li a1, 0  # [op543] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vmv.v.x v5, a1  # [op544] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vmv1r.v v0, v1  # [op545] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vmerge.vvm v1, v5, v4, v0  # [op546] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
vsuxei64.v v1, (s1), v2  # [op547] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:47
li s1, 16  # [op548] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op549] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op550] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op551] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op552] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk10_head  # [op554] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk11_head:  # block chunk11_head
li s1, 512  # [op555] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op556] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc557_true  # [op557] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op557] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op557] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk11_exit  # [op557] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc557_true:  # [op557] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk11_body  # [op557] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk11_exit:  # block chunk11_exit
li t1, 0  # [op558] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op559] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op559] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op559] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk12_head  # [op559] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk11_body:  # block chunk11_body
li s1, 32  # [op560] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op561] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 0  # [op562] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a1, 32  # [op563] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a1, a1, e16, m1, ta,ma  # [op564] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.x v1, s1  # [op565] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s1, 32  # [op566] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s1, s1, e32, m1, ta,ma  # [op567] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vid.v v2  # [op568] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vadd.vx v2, v2, t0  # [op569] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s1, 32  # [op570] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vwadd.vx v4, v2, x0  # [op572] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
    # [peephole-li] [op573] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli s1, s1, e64, m2, ta,ma  # [op574] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s1, 4  # [op575] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmul.vx v2, v4, s1  # [op576] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s1, 27008  # [op577] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add s1, a1, s1  # [op578] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a1, 32  # [op579] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a1, a1, e16, m1, ta,ma  # [op580] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vfwcvt.f.f.v v4, v1  # [op581] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a1, 32  # [op582] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a1, a1, e32, m1, ta,ma  # [op583] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.v v1, v4  # [op584] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a1, 32  # [op585] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsuxei64.v v1, (s1), v2  # [op587] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li s1, 32  # [op588] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
    # [peephole-li] [op590] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op591] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op592] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op593] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op594] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk11_head  # [op596] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk12_head:  # block chunk12_head
li s1, 16  # [op597] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op598] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc599_true  # [op599] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t2  # [op599] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv s3, t1  # [op599] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk12_exit  # [op599] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc599_true:  # [op599] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk12_body  # [op599] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk12_exit:  # block chunk12_exit
li t0, 0  # [op600] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
j .Lstg13_head  # [op601] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
.Lchunk12_body:  # block chunk12_body
li s1, 16  # [op602] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op603] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 16  # [op604] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op605] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op606] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op607] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op608] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk12_head  # [op610] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lstg13_head:  # block stg13_head
li t1, 512  # [op611] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
slt t1, t0, t1  # [op612] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
bne t1, zero, .Lbrc613_true  # [op613] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
j .Lstg13_exit  # [op613] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
.Lbrc613_true:  # [op613] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
j .Lstg13_body  # [op613] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
.Lstg13_body:  # block stg13_body
li t1, 32  # [op614] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t1, t1, e32, m1, ta,ma  # [op615] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vid.v v1  # [op616] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vadd.vx v1, v1, t0  # [op617] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t1, 32  # [op618] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv.v.x v2, t1  # [op619] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vdiv.vv v2, v1, v2  # [op620] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t1, 16  # [op621] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv.v.x v3, t1  # [op622] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vrem.vv v2, v2, v3  # [op623] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t1, 32  # [op624] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv.v.x v3, t1  # [op625] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vrem.vv v3, v1, v3  # [op626] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op627] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vwadd.vx v4, v2, x0  # [op629] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op630] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t1, t1, e64, m2, ta,ma  # [op631] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t1, 4  # [op632] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmul.vx v2, v4, t1  # [op633] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t1, 6144  # [op634] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld s1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
add t1, s1, t1  # [op635] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li s1, 32  # [op636] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli s1, s1, e32, m1, ta,ma  # [op637] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vluxei64.v v4, (t1), v2  # [op638] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t1, 32  # [op639] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vwadd.vx v2, v1, x0  # [op641] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op642] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t1, t1, e64, m2, ta,ma  # [op643] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t1, 4  # [op644] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmul.vx v2, v2, t1  # [op645] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t1, 6464  # [op646] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld s1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
add t1, s1, t1  # [op647] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li s1, 32  # [op648] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli s1, s1, e32, m1, ta,ma  # [op649] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsuxei64.v v4, (t1), v2  # [op650] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t1, 32  # [op651] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
addw t0, t0, t1  # [op652] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
j .Lstg13_head  # [op653] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
.Lstg13_exit:  # block stg13_exit
li t0, 0  # [op654] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
j .Lstg14_head  # [op655] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
.Lstg14_head:  # block stg14_head
li t1, 512  # [op656] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
slt t1, t0, t1  # [op657] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
bne t1, zero, .Lbrc658_true  # [op658] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
j .Lstg14_exit  # [op658] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
.Lbrc658_true:  # [op658] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
j .Lstg14_body  # [op658] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
.Lstg14_body:  # block stg14_body
li t1, 32  # [op659] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t1, t1, e32, m1, ta,ma  # [op660] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vid.v v1  # [op661] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vadd.vx v1, v1, t0  # [op662] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t1, 16  # [op663] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv.v.x v2, t1  # [op664] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vdiv.vv v2, v1, v2  # [op665] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t1, 32  # [op666] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv.v.x v3, t1  # [op667] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vrem.vv v2, v2, v3  # [op668] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t1, 16  # [op669] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv.v.x v2, t1  # [op670] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vrem.vv v2, v1, v2  # [op671] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t1, 32  # [op672] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vwadd.vx v4, v2, x0  # [op674] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
    # [peephole-li] [op675] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t1, t1, e64, m2, ta,ma  # [op676] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t1, 4  # [op677] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmul.vx v2, v4, t1  # [op678] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t1, 20800  # [op679] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld s1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
add t1, s1, t1  # [op680] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li s1, 32  # [op681] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli s1, s1, e32, m1, ta,ma  # [op682] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vluxei64.v v4, (t1), v2  # [op683] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t1, 32  # [op684] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vwadd.vx v2, v1, x0  # [op686] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
    # [peephole-li] [op687] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t1, t1, e64, m2, ta,ma  # [op688] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t1, 4  # [op689] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmul.vx v2, v2, t1  # [op690] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t1, 22912  # [op691] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld s1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
add t1, s1, t1  # [op692] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li s1, 32  # [op693] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli s1, s1, e32, m1, ta,ma  # [op694] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsuxei64.v v4, (t1), v2  # [op695] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t1, 32  # [op696] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
addw t0, t0, t1  # [op697] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
j .Lstg14_head  # [op698] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
.Lstg14_exit:  # block stg14_exit
li t0, 0  # [op699] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
li s11, 32  # [op700] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
mv s2, t0  # [op701] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
j .Lmloop15.head  # [op701] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
.Lmloop15.head:  # block mloop15.head
ld t0, 120(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
slt t0, s2, t0  # [op702] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
bne t0, zero, .Lbrc703_true  # [op703] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
mv t0, s2  # [op703] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
j .Lmloop15.exit  # [op703] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
.Lbrc703_true:  # [op703] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
j .Lmloop15.body  # [op703] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
.Lmloop15.body:  # block mloop15.body
li t0, 0  # [op704] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, s3  # [op705] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk16_head  # [op705] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lmloop15.exit:  # block mloop15.exit
li t0, 0  # [op706] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, s3  # [op707] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk32_head  # [op707] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk16_head:  # block chunk16_head
li s1, 32  # [op708] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op709] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc710_true  # [op710] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op710] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op710] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk16_exit  # [op710] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc710_true:  # [op710] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk16_body  # [op710] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk16_exit:  # block chunk16_exit
li t1, 0  # [op711] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op712] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op712] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op712] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk17_head  # [op712] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk16_body:  # block chunk16_body
li s1, 32  # [op713] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op714] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op715] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vmv.v.x v1, s2  # [op717] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vid.v v2  # [op718] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vadd.vx v2, v2, t0  # [op719] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
    # [peephole-li] [op720] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vwadd.vx v4, v2, x0  # [op722] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
    # [peephole-li] [op723] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vsetvli s1, s1, e64, m2, ta,ma  # [op724] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
li s1, 4  # [op725] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vmul.vx v2, v4, s1  # [op726] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
li s1, 1280  # [op727] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
add s1, a1, s1  # [op728] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
li a1, 32  # [op729] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vsetvli a1, a1, e32, m1, ta,ma  # [op730] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vsuxei64.v v1, (s1), v2  # [op731] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
li s1, 32  # [op732] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vid.v v2  # [op734] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vadd.vx v2, v2, t0  # [op735] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
    # [peephole-li] [op736] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vwadd.vx v4, v2, x0  # [op738] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
    # [peephole-li] [op739] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vsetvli s1, s1, e64, m2, ta,ma  # [op740] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
li s1, 4  # [op741] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vmul.vx v2, v4, s1  # [op742] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
li s1, 128  # [op743] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
add s1, a1, s1  # [op744] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
li a1, 32  # [op745] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vsetvli a1, a1, e32, m1, ta,ma  # [op746] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vluxei64.v v4, (s1), v2  # [op747] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
li s1, 32  # [op748] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vadd.vv v1, v1, v4  # [op750] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vid.v v2  # [op751] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vadd.vx v2, v2, t0  # [op752] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
    # [peephole-li] [op753] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vwadd.vx v4, v2, x0  # [op755] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
    # [peephole-li] [op756] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vsetvli s1, s1, e64, m2, ta,ma  # [op757] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
li s1, 4  # [op758] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vmul.vx v2, v4, s1  # [op759] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
li s1, 1408  # [op760] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
add s1, a1, s1  # [op761] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
li a1, 32  # [op762] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vsetvli a1, a1, e32, m1, ta,ma  # [op763] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
vsuxei64.v v1, (s1), v2  # [op764] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
li s1, 32  # [op765] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:30:14
    # [peephole-li] [op767] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op768] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op769] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op770] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op771] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk16_head  # [op773] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk17_head:  # block chunk17_head
li s1, 512  # [op774] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op775] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc776_true  # [op776] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op776] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op776] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk17_exit  # [op776] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc776_true:  # [op776] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk17_body  # [op776] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk17_exit:  # block chunk17_exit
li t1, 0  # [op777] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op778] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op778] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op778] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk18_head  # [op778] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk17_body:  # block chunk17_body
li s1, 32  # [op779] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op780] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op781] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
vid.v v1  # [op783] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
vadd.vx v1, v1, t0  # [op784] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
    # [peephole-li] [op785] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
vmv.v.x v2, s1  # [op786] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
vdiv.vv v1, v1, v2  # [op787] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
    # [peephole-li] [op788] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
vwadd.vx v2, v1, x0  # [op790] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
    # [peephole-li] [op791] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
vsetvli s1, s1, e64, m2, ta,ma  # [op792] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
li s1, 8  # [op793] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
vmul.vx v2, v2, s1  # [op794] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
li s1, 1728  # [op795] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
add s1, a1, s1  # [op796] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
li a1, 32  # [op797] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
vluxei64.v v4, (s1), v2  # [op799] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
li s1, 32  # [op800] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
vsetvli s1, s1, e32, m1, ta,ma  # [op801] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:21
li s1, 32  # [op802] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op803] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op804] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op805] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op806] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk17_head  # [op808] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk18_head:  # block chunk18_head
li s1, 32  # [op809] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op810] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc811_true  # [op811] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t2  # [op811] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk18_exit  # [op811] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc811_true:  # [op811] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk18_body  # [op811] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk18_exit:  # block chunk18_exit
li t0, 0  # [op812] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
j .Lstg19_head  # [op813] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
.Lchunk18_body:  # block chunk18_body
li s1, 32  # [op814] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op815] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op816] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vid.v v1  # [op818] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vadd.vx v1, v1, t0  # [op819] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
    # [peephole-li] [op820] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vwadd.vx v2, v1, x0  # [op822] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
    # [peephole-li] [op823] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vsetvli s1, s1, e64, m2, ta,ma  # [op824] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li s1, 4  # [op825] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vmul.vx v2, v2, s1  # [op826] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li s1, 1408  # [op827] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
add s1, a1, s1  # [op828] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li a1, 32  # [op829] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vsetvli a1, a1, e32, m1, ta,ma  # [op830] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vluxei64.v v1, (s1), v2  # [op831] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li s1, 32  # [op832] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vid.v v2  # [op834] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vadd.vx v2, v2, t0  # [op835] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
    # [peephole-li] [op836] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vwadd.vx v4, v2, x0  # [op838] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
    # [peephole-li] [op839] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vsetvli s1, s1, e64, m2, ta,ma  # [op840] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li s1, 4  # [op841] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vmul.vx v2, v4, s1  # [op842] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li s1, 6208  # [op843] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
add s1, a1, s1  # [op844] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li a1, 32  # [op845] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vsetvli a1, a1, e32, m1, ta,ma  # [op846] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vluxei64.v v4, (s1), v2  # [op847] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li s1, 32  # [op848] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vmslt.vv v1, v1, v4  # [op850] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vid.v v2  # [op851] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vadd.vx v2, v2, t0  # [op852] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
    # [peephole-li] [op853] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vwadd.vx v4, v2, x0  # [op855] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
    # [peephole-li] [op856] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vsetvli s1, s1, e64, m2, ta,ma  # [op857] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li s1, 4  # [op858] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vmul.vx v2, v4, s1  # [op859] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li s1, 6336  # [op860] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
add s1, a1, s1  # [op861] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li a1, 32  # [op862] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vsetvli a1, a1, e32, m1, ta,ma  # [op863] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li a1, 1  # [op864] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vmv.v.x v4, a1  # [op865] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li a1, 0  # [op866] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vmv.v.x v5, a1  # [op867] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vmv1r.v v0, v1  # [op868] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vmerge.vvm v1, v5, v4, v0  # [op869] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
vsuxei64.v v1, (s1), v2  # [op870] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:51
li s1, 32  # [op871] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op872] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op873] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op874] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op875] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk18_head  # [op877] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lstg19_head:  # block stg19_head
li s1, 512  # [op878] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
slt s1, t0, s1  # [op879] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
bne s1, zero, .Lbrc880_true  # [op880] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
j .Lstg19_exit  # [op880] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
.Lbrc880_true:  # [op880] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
j .Lstg19_body  # [op880] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
.Lstg19_body:  # block stg19_body
li s1, 32  # [op881] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli s1, s1, e32, m1, ta,ma  # [op882] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vid.v v1  # [op883] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vadd.vx v1, v1, t0  # [op884] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li s1, 32  # [op885] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv.v.x v2, s1  # [op886] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vdiv.vv v2, v1, v2  # [op887] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li s1, 16  # [op888] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv.v.x v3, s1  # [op889] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vrem.vv v2, v2, v3  # [op890] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li s1, 32  # [op891] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv.v.x v2, s1  # [op892] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vrem.vv v2, v1, v2  # [op893] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op894] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vwadd.vx v4, v2, x0  # [op896] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op897] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli s1, s1, e64, m2, ta,ma  # [op898] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li s1, 4  # [op899] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmul.vx v2, v4, s1  # [op900] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li s1, 6336  # [op901] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
add s1, a1, s1  # [op902] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li a1, 32  # [op903] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli a1, a1, e32, m1, ta,ma  # [op904] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vluxei64.v v4, (s1), v2  # [op905] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li s1, 32  # [op906] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vwadd.vx v2, v1, x0  # [op908] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op909] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli s1, s1, e64, m2, ta,ma  # [op910] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li s1, 4  # [op911] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmul.vx v2, v2, s1  # [op912] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li s1, 8512  # [op913] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
add s1, a1, s1  # [op914] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li a1, 32  # [op915] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli a1, a1, e32, m1, ta,ma  # [op916] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsuxei64.v v4, (s1), v2  # [op917] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li s1, 32  # [op918] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
addw t0, t0, s1  # [op919] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
j .Lstg19_head  # [op920] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
.Lstg19_exit:  # block stg19_exit
li t0, 0  # [op921] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv s1, t0  # [op922] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv a1, t1  # [op922] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk20_head  # [op922] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk20_head:  # block chunk20_head
li t0, 512  # [op923] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt t0, s1, t0  # [op924] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne t0, zero, .Lbrc925_true  # [op925] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op925] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, a1  # [op925] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk20_exit  # [op925] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc925_true:  # [op925] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk20_body  # [op925] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk20_exit:  # block chunk20_exit
li t1, 0  # [op926] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op927] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op927] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op927] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk21_head  # [op927] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk20_body:  # block chunk20_body
li t0, 32  # [op928] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli t0, t0, e16, m1, ta,ma  # [op929] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li t0, 32  # [op930] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t0, t0, e32, m1, ta,ma  # [op931] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vid.v v1  # [op932] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vadd.vx v1, v1, s1  # [op933] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 32  # [op934] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vwadd.vx v2, v1, x0  # [op936] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op937] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t0, t0, e64, m2, ta,ma  # [op938] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 4  # [op939] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmul.vx v2, v2, t0  # [op940] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 6464  # [op941] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld t1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
add t0, t1, t0  # [op942] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t1, 32  # [op943] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t1, t1, e32, m1, ta,ma  # [op944] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vluxei64.v v1, (t0), v2  # [op945] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 0  # [op946] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv.v.x v2, t0  # [op947] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmsne.vv v1, v1, v2  # [op948] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 32  # [op949] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t0, t0, e16, m1, ta,ma  # [op950] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 32  # [op951] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t0, t0, e32, m1, ta,ma  # [op952] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vid.v v2  # [op953] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vadd.vx v2, v2, s1  # [op954] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 32  # [op955] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vwadd.vx v4, v2, x0  # [op957] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op958] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t0, t0, e64, m2, ta,ma  # [op959] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 4  # [op960] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmul.vx v2, v4, t0  # [op961] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 8512  # [op962] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld t1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
add t0, t1, t0  # [op963] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t1, 32  # [op964] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t1, t1, e32, m1, ta,ma  # [op965] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vluxei64.v v4, (t0), v2  # [op966] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 0  # [op967] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv.v.x v2, t0  # [op968] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmsne.vv v2, v4, v2  # [op969] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 32  # [op970] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t0, t0, e16, m1, ta,ma  # [op971] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmand.mm v1, v1, v2  # [op972] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 32  # [op973] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t0, t0, e32, m1, ta,ma  # [op974] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vid.v v2  # [op975] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vadd.vx v2, v2, s1  # [op976] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 32  # [op977] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vwadd.vx v4, v2, x0  # [op979] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op980] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t0, t0, e64, m2, ta,ma  # [op981] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 4  # [op982] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmul.vx v2, v4, t0  # [op983] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 10560  # [op984] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld t1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
add t0, t1, t0  # [op985] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t1, 32  # [op986] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t1, t1, e32, m1, ta,ma  # [op987] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t1, 1  # [op988] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv.v.x v4, t1  # [op989] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t1, 0  # [op990] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv.v.x v5, t1  # [op991] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv1r.v v0, v1  # [op992] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmerge.vvm v4, v5, v4, v0  # [op993] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsuxei64.v v4, (t0), v2  # [op994] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 32  # [op995] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t0, t0, e16, m1, ta,ma  # [op996] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 32  # [op997] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t0, t0, e32, m1, ta,ma  # [op998] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vid.v v2  # [op999] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vadd.vx v2, v2, s1  # [op1000] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 32  # [op1001] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vwadd.vx v4, v2, x0  # [op1003] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op1004] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t0, t0, e64, m2, ta,ma  # [op1005] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 4  # [op1006] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmul.vx v2, v4, t0  # [op1007] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 10560  # [op1008] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
ld t1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
add t0, t1, t0  # [op1009] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t1, 32  # [op1010] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t1, t1, e32, m1, ta,ma  # [op1011] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t1, 1  # [op1012] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv.v.x v4, t1  # [op1013] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t1, 0  # [op1014] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv.v.x v5, t1  # [op1015] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmv1r.v v0, v1  # [op1016] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vmerge.vvm v4, v5, v4, v0  # [op1017] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsuxei64.v v4, (t0), v2  # [op1018] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 32  # [op1019] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
vsetvli t0, t0, e16, m1, ta,ma  # [op1020] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:32:26
li t0, 32  # [op1021] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e32, m1, ta,ma  # [op1022] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vid.v v2  # [op1023] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vadd.vx v2, v2, s1  # [op1024] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1025] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.x v3, t0  # [op1026] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vdiv.vv v2, v2, v3  # [op1027] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op1028] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vwadd.vx v4, v2, x0  # [op1030] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op1031] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e64, m2, ta,ma  # [op1032] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 4  # [op1033] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmul.vx v2, v4, t0  # [op1034] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 1664  # [op1035] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
ld t1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add t0, t1, t0  # [op1036] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t1, 32  # [op1037] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t1, t1, e32, m1, ta,ma  # [op1038] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vluxei64.v v4, (t0), v2  # [op1039] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1040] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e16, m1, ta,ma  # [op1041] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1042] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e32, m1, ta,ma  # [op1043] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vid.v v2  # [op1044] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vadd.vx v2, v2, s1  # [op1045] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1046] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.x v3, t0  # [op1047] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vrem.vv v2, v2, v3  # [op1048] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op1049] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vwadd.vx v6, v2, x0  # [op1051] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op1052] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e64, m2, ta,ma  # [op1053] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 4  # [op1054] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmul.vx v2, v6, t0  # [op1055] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 1408  # [op1056] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
ld t1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add t0, t1, t0  # [op1057] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t1, 32  # [op1058] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t1, t1, e32, m1, ta,ma  # [op1059] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vluxei64.v v5, (t0), v2  # [op1060] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1061] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e16, m1, ta,ma  # [op1062] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1063] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e32, m1, ta,ma  # [op1064] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vadd.vv v2, v4, v5  # [op1065] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1066] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e16, m1, ta,ma  # [op1067] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1068] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e32, m1, ta,ma  # [op1069] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vwadd.vx v4, v2, x0  # [op1070] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1071] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e64, m2, ta,ma  # [op1072] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 2  # [op1073] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmul.vx v2, v4, t0  # [op1074] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1075] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e16, m1, ta,ma  # [op1076] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 35904  # [op1077] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
ld t1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add t0, t1, t0  # [op1078] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t1, 128  # [op1079] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add t1, t0, t1  # [op1080] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1081] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e32, m1, ta,ma  # [op1082] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 0  # [op1083] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.x v4, a2  # [op1084] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 1  # [op1085] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.x v5, a2  # [op1086] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv1r.v v0, v1  # [op1087] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmerge.vvm v4, v4, v5, v0  # [op1088] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vid.v v1  # [op1089] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vadd.vx v1, v1, s1  # [op1090] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1091] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vwadd.vx v6, v1, x0  # [op1093] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op1094] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1095] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 4  # [op1096] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmul.vx v6, v6, a2  # [op1097] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 12608  # [op1098] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
ld a3, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a2, a3, a2  # [op1099] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a3, 32  # [op1100] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a3, a3, e32, m1, ta,ma  # [op1101] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vluxei64.v v1, (a2), v6  # [op1102] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1103] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.v v6, v1  # [op1105] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op1106] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e16, m1, ta,ma  # [op1107] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vfncvt.f.f.w v1, v6  # [op1108] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1109] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1110] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vadd.vx v6, v2, s8  # [op1111] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1112] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e32, m1, ta,ma  # [op1113] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 0  # [op1114] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.x v2, a2  # [op1115] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmsne.vv v2, v4, v2  # [op1116] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv1r.v v0, v2  # [op1117] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1118] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1119] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 0  # [op1120] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.x v4, a2  # [op1121] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.v.x v2, t1  # [op1122] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsub.vv v6, v6, v2  # [op1123] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmerge.vvm v4, v4, v6, v0  # [op1124] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vadd.vv v2, v2, v4  # [op1125] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1126] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e16, m1, ta,ma  # [op1127] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1128] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1129] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1130] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a3, 0  # [op1131] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1132] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1133] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1134] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1135] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1136] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1137] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1138] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1139] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1140] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1141] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1142] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1143] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a3, 2  # [op1144] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1145] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1146] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1147] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1148] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1149] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1150] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1151] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1152] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1153] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1154] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1155] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1156] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a3, 4  # [op1157] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1158] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1159] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1160] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1161] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1162] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1163] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1164] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1165] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1166] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1167] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1168] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1169] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a3, 6  # [op1170] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1171] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1172] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1173] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1174] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1175] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1176] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1177] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1178] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1179] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1180] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1181] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1182] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a3, 8  # [op1183] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1184] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1185] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1186] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1187] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1188] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1189] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1190] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1191] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1192] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1193] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1194] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1195] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a3, 10  # [op1196] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1197] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1198] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1199] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1200] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1201] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1202] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1203] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1204] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1205] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1206] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1207] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1208] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a3, 12  # [op1209] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1210] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1211] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1212] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1213] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1214] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1215] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1216] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1217] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1218] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1219] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1220] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1221] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a3, 14  # [op1222] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1223] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1224] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1225] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1226] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1227] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1228] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1229] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1230] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1231] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1232] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1233] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1234] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a3, 16  # [op1235] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1236] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1237] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1238] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1239] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1240] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1241] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1242] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1243] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1244] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1245] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1246] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1247] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a3, 18  # [op1248] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1249] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1250] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1251] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1252] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1253] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1254] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1255] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1256] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1257] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1258] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1259] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1260] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a3, 20  # [op1261] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1262] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1263] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1264] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1265] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1266] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1267] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1268] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1269] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1270] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1271] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1272] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1273] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a3, 22  # [op1274] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1275] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1276] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1277] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1278] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1279] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1280] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1281] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1282] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1283] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1284] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1285] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1286] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a3, 24  # [op1287] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1288] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1289] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1290] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1291] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1292] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1293] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1294] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1295] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1296] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1297] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1298] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1299] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a3, 26  # [op1300] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1301] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1302] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1303] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1304] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1305] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1306] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1307] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1308] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1309] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1310] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1311] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1312] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a3, 28  # [op1313] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1314] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1315] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1316] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1317] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1318] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1319] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1320] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1321] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1322] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1323] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1324] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1325] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a3, 30  # [op1326] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1327] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1328] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1329] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1330] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1331] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1332] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1333] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1334] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1335] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1336] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1337] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1338] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a3, 32  # [op1339] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1340] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1341] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1342] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1343] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1344] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1345] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1346] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1347] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1348] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1349] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1350] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1351] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a3, 34  # [op1352] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1353] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1354] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1355] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1356] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1357] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1358] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1359] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1360] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1361] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1362] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1363] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1364] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a3, 36  # [op1365] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1366] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1367] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1368] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1369] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1370] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1371] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1372] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1373] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1374] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1375] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1376] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1377] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a3, 38  # [op1378] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1379] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1380] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1381] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1382] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1383] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1384] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1385] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1386] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1387] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1388] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1389] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1390] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a3, 40  # [op1391] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1392] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1393] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1394] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1395] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1396] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1397] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1398] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1399] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1400] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1401] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1402] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1403] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a3, 42  # [op1404] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1405] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1406] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1407] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1408] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1409] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1410] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1411] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1412] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1413] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1414] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1415] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1416] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a3, 44  # [op1417] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1418] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1419] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1420] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1421] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1422] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1423] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1424] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1425] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1426] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1427] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1428] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1429] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a3, 46  # [op1430] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1431] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1432] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1433] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1434] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1435] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1436] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1437] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1438] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1439] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1440] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1441] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1442] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a3, 48  # [op1443] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1444] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1445] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1446] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1447] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1448] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1449] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1450] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1451] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1452] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1453] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1454] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1455] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a3, 50  # [op1456] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1457] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1458] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1459] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1460] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1461] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1462] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1463] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1464] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1465] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1466] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1467] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1468] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a3, 52  # [op1469] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1470] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1471] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1472] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1473] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1474] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1475] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1476] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1477] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1478] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1479] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1480] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1481] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a3, 54  # [op1482] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1483] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1484] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1485] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1486] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1487] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1488] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1489] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1490] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1491] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1492] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1493] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1494] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a3, 56  # [op1495] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1496] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1497] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1498] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1499] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1500] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1501] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1502] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1503] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1504] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1505] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1506] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1507] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a3, 58  # [op1508] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1509] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1510] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1511] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1512] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1513] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1514] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1515] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1516] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1517] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1518] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1519] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1520] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a3, 60  # [op1521] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1522] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1523] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1524] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1525] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1526] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1527] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1528] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1529] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1530] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1531] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1532] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1533] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a3, 62  # [op1534] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1535] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1536] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1537] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1538] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1539] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1540] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
lhu t1, 0(a2)  # [op1541] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
sh t1, 0(a3)  # [op1542] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t1, 32  # [op1543] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t1, t1, e64, m2, ta,ma  # [op1544] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1545] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t1, 32  # [op1546] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vsetvli t1, t1, e16, m1, ta,ma  # [op1547] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vle16.v v1, 0(t0)  # [op1548] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 14656  # [op1549] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
ld t1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add t0, t1, t0  # [op1550] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
mv t1, s1  # [op1551] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li a2, 2  # [op1552] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
mul t1, t1, a2  # [op1553] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
add t0, t0, t1  # [op1554] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
vse16.v v1, 0(t0)  # [op1555] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1556] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t0, a1, t0  # [op1557] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li t1, 32  # [op1558] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t1, s1, t1  # [op1559] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op1560] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv s1, t1  # [op1562] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv a1, t0  # [op1562] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk20_head  # [op1562] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk21_head:  # block chunk21_head
li s1, 32  # [op1563] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op1564] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc1565_true  # [op1565] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op1565] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op1565] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk21_exit  # [op1565] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc1565_true:  # [op1565] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk21_body  # [op1565] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk21_exit:  # block chunk21_exit
li t1, 0  # [op1566] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op1567] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op1567] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op1567] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk22_head  # [op1567] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk21_body:  # block chunk21_body
li s1, 32  # [op1568] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op1569] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op1570] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vid.v v1  # [op1572] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vadd.vx v1, v1, t0  # [op1573] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
    # [peephole-li] [op1574] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vwadd.vx v2, v1, x0  # [op1576] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
    # [peephole-li] [op1577] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vsetvli s1, s1, e64, m2, ta,ma  # [op1578] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li s1, 4  # [op1579] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vmul.vx v2, v2, s1  # [op1580] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li s1, 1408  # [op1581] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
add s1, a1, s1  # [op1582] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li a1, 32  # [op1583] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vsetvli a1, a1, e32, m1, ta,ma  # [op1584] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vluxei64.v v1, (s1), v2  # [op1585] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li s1, 32  # [op1586] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vid.v v2  # [op1588] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vadd.vx v2, v2, t0  # [op1589] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
    # [peephole-li] [op1590] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vwadd.vx v4, v2, x0  # [op1592] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
    # [peephole-li] [op1593] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vsetvli s1, s1, e64, m2, ta,ma  # [op1594] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li s1, 4  # [op1595] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vmul.vx v2, v4, s1  # [op1596] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li s1, 15808  # [op1597] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
add s1, a1, s1  # [op1598] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li a1, 32  # [op1599] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vsetvli a1, a1, e32, m1, ta,ma  # [op1600] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vluxei64.v v4, (s1), v2  # [op1601] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li s1, 32  # [op1602] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vmul.vv v1, v1, v4  # [op1604] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vid.v v2  # [op1605] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vadd.vx v2, v2, t0  # [op1606] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
    # [peephole-li] [op1607] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vwadd.vx v4, v2, x0  # [op1609] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
    # [peephole-li] [op1610] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vsetvli s1, s1, e64, m2, ta,ma  # [op1611] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li s1, 4  # [op1612] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vmul.vx v2, v4, s1  # [op1613] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li s1, 15936  # [op1614] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
add s1, a1, s1  # [op1615] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li a1, 32  # [op1616] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vsetvli a1, a1, e32, m1, ta,ma  # [op1617] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
vsuxei64.v v1, (s1), v2  # [op1618] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
li s1, 32  # [op1619] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:29
    # [peephole-li] [op1621] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op1622] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op1623] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op1624] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op1625] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk21_head  # [op1627] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk22_head:  # block chunk22_head
li s1, 512  # [op1628] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op1629] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc1630_true  # [op1630] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op1630] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op1630] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk22_exit  # [op1630] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc1630_true:  # [op1630] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk22_body  # [op1630] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk22_exit:  # block chunk22_exit
li t1, 0  # [op1631] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op1632] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op1632] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op1632] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk23_head  # [op1632] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk22_body:  # block chunk22_body
li s1, 32  # [op1633] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op1634] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op1635] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
vid.v v1  # [op1637] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
vadd.vx v1, v1, t0  # [op1638] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
li s1, 16  # [op1639] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
vmv.v.x v2, s1  # [op1640] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
vdiv.vv v1, v1, v2  # [op1641] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
li s1, 32  # [op1642] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
vwadd.vx v2, v1, x0  # [op1644] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
    # [peephole-li] [op1645] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
vsetvli s1, s1, e64, m2, ta,ma  # [op1646] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
li s1, 8  # [op1647] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
vmul.vx v2, v2, s1  # [op1648] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
li s1, 16064  # [op1649] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
add s1, a1, s1  # [op1650] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
li a1, 32  # [op1651] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
vluxei64.v v4, (s1), v2  # [op1653] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
li s1, 32  # [op1654] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
vsetvli s1, s1, e32, m1, ta,ma  # [op1655] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:21
li s1, 32  # [op1656] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op1657] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op1658] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op1659] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op1660] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk22_head  # [op1662] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk23_head:  # block chunk23_head
li s1, 32  # [op1663] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op1664] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc1665_true  # [op1665] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t2  # [op1665] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk23_exit  # [op1665] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc1665_true:  # [op1665] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk23_body  # [op1665] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk23_exit:  # block chunk23_exit
li t0, 0  # [op1666] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
j .Lstg24_head  # [op1667] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
.Lchunk23_body:  # block chunk23_body
li s1, 32  # [op1668] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op1669] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op1670] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vid.v v1  # [op1672] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vadd.vx v1, v1, t0  # [op1673] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
    # [peephole-li] [op1674] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vwadd.vx v2, v1, x0  # [op1676] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
    # [peephole-li] [op1677] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vsetvli s1, s1, e64, m2, ta,ma  # [op1678] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li s1, 4  # [op1679] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vmul.vx v2, v2, s1  # [op1680] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li s1, 1408  # [op1681] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
add s1, a1, s1  # [op1682] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li a1, 32  # [op1683] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vsetvli a1, a1, e32, m1, ta,ma  # [op1684] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vluxei64.v v1, (s1), v2  # [op1685] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li s1, 32  # [op1686] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vid.v v2  # [op1688] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vadd.vx v2, v2, t0  # [op1689] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
    # [peephole-li] [op1690] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vwadd.vx v4, v2, x0  # [op1692] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
    # [peephole-li] [op1693] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vsetvli s1, s1, e64, m2, ta,ma  # [op1694] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li s1, 4  # [op1695] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vmul.vx v2, v4, s1  # [op1696] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li s1, 20480  # [op1697] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
add s1, a1, s1  # [op1698] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li a1, 32  # [op1699] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vsetvli a1, a1, e32, m1, ta,ma  # [op1700] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vluxei64.v v4, (s1), v2  # [op1701] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li s1, 32  # [op1702] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vmslt.vv v1, v1, v4  # [op1704] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vid.v v2  # [op1705] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vadd.vx v2, v2, t0  # [op1706] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
    # [peephole-li] [op1707] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vwadd.vx v4, v2, x0  # [op1709] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
    # [peephole-li] [op1710] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vsetvli s1, s1, e64, m2, ta,ma  # [op1711] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li s1, 4  # [op1712] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vmul.vx v2, v4, s1  # [op1713] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li s1, 20608  # [op1714] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
add s1, a1, s1  # [op1715] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li a1, 32  # [op1716] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vsetvli a1, a1, e32, m1, ta,ma  # [op1717] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li a1, 1  # [op1718] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vmv.v.x v4, a1  # [op1719] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li a1, 0  # [op1720] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vmv.v.x v5, a1  # [op1721] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vmv1r.v v0, v1  # [op1722] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vmerge.vvm v1, v5, v4, v0  # [op1723] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
vsuxei64.v v1, (s1), v2  # [op1724] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:27
li s1, 32  # [op1725] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op1726] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op1727] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op1728] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op1729] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk23_head  # [op1731] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lstg24_head:  # block stg24_head
li s1, 512  # [op1732] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
slt s1, t0, s1  # [op1733] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
bne s1, zero, .Lbrc1734_true  # [op1734] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
j .Lstg24_exit  # [op1734] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
.Lbrc1734_true:  # [op1734] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
j .Lstg24_body  # [op1734] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
.Lstg24_body:  # block stg24_body
li s1, 32  # [op1735] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli s1, s1, e32, m1, ta,ma  # [op1736] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vid.v v1  # [op1737] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vadd.vx v1, v1, t0  # [op1738] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li s1, 16  # [op1739] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv.v.x v2, s1  # [op1740] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vdiv.vv v2, v1, v2  # [op1741] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li s1, 32  # [op1742] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv.v.x v3, s1  # [op1743] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vrem.vv v2, v2, v3  # [op1744] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li s1, 16  # [op1745] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv.v.x v3, s1  # [op1746] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vrem.vv v3, v1, v3  # [op1747] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li s1, 32  # [op1748] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vwadd.vx v4, v2, x0  # [op1750] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
    # [peephole-li] [op1751] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli s1, s1, e64, m2, ta,ma  # [op1752] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li s1, 4  # [op1753] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmul.vx v2, v4, s1  # [op1754] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li s1, 20608  # [op1755] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
add s1, a1, s1  # [op1756] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a1, 32  # [op1757] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli a1, a1, e32, m1, ta,ma  # [op1758] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vluxei64.v v4, (s1), v2  # [op1759] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li s1, 32  # [op1760] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vwadd.vx v2, v1, x0  # [op1762] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
    # [peephole-li] [op1763] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli s1, s1, e64, m2, ta,ma  # [op1764] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li s1, 4  # [op1765] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmul.vx v2, v2, s1  # [op1766] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li s1, 20864  # [op1767] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
add s1, a1, s1  # [op1768] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li a1, 32  # [op1769] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli a1, a1, e32, m1, ta,ma  # [op1770] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsuxei64.v v4, (s1), v2  # [op1771] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li s1, 32  # [op1772] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
addw t0, t0, s1  # [op1773] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
j .Lstg24_head  # [op1774] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
.Lstg24_exit:  # block stg24_exit
li t0, 0  # [op1775] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv s1, t0  # [op1776] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv a1, t1  # [op1776] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk25_head  # [op1776] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk25_head:  # block chunk25_head
li t0, 512  # [op1777] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt t0, s1, t0  # [op1778] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne t0, zero, .Lbrc1779_true  # [op1779] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t2  # [op1779] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, a1  # [op1779] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk25_exit  # [op1779] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc1779_true:  # [op1779] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk25_body  # [op1779] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk25_exit:  # block chunk25_exit
li t0, 35392  # [op1780] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a1, t1, t0  # [op1781] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t0, 128  # [op1782] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a2, a1, t0  # [op1783] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t0, 256  # [op1784] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t0, a1, t0  # [op1785] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sd t0, 200(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t0, 8  # [op1786] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vsetvli t0, t0, e32, m1, ta,ma  # [op1787] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vid.v v2  # [op1788] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t0, 8  # [op1789] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vid.v v1  # [op1791] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t0, 64  # [op1792] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vsetvli t0, t0, e16, m1, ta,ma  # [op1793] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t0, 0  # [op1794] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv.v.x v3, t0  # [op1795] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv.v.x v4, t0  # [op1796] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
    # [peephole-li] [op1797] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t3, 4  # [op1798] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mv a7, t0  # [op1799] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lmtile26.head  # [op1799] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lchunk25_body:  # block chunk25_body
li t0, 32  # [op1800] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli t0, t0, e16, m1, ta,ma  # [op1801] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li t0, 32  # [op1802] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t0, t0, e32, m1, ta,ma  # [op1803] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vid.v v1  # [op1804] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vadd.vx v1, v1, s1  # [op1805] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 32  # [op1806] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vwadd.vx v2, v1, x0  # [op1808] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
    # [peephole-li] [op1809] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t0, t0, e64, m2, ta,ma  # [op1810] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 4  # [op1811] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmul.vx v2, v2, t0  # [op1812] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 20864  # [op1813] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld t1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
add t0, t1, t0  # [op1814] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t1, 32  # [op1815] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t1, t1, e32, m1, ta,ma  # [op1816] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vluxei64.v v1, (t0), v2  # [op1817] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 0  # [op1818] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv.v.x v2, t0  # [op1819] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmsne.vv v1, v1, v2  # [op1820] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 32  # [op1821] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t0, t0, e16, m1, ta,ma  # [op1822] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 32  # [op1823] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t0, t0, e32, m1, ta,ma  # [op1824] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vid.v v2  # [op1825] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vadd.vx v2, v2, s1  # [op1826] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 32  # [op1827] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vwadd.vx v4, v2, x0  # [op1829] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
    # [peephole-li] [op1830] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t0, t0, e64, m2, ta,ma  # [op1831] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 4  # [op1832] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmul.vx v2, v4, t0  # [op1833] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 22912  # [op1834] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld t1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
add t0, t1, t0  # [op1835] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t1, 32  # [op1836] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t1, t1, e32, m1, ta,ma  # [op1837] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vluxei64.v v4, (t0), v2  # [op1838] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 0  # [op1839] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv.v.x v2, t0  # [op1840] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmsne.vv v2, v4, v2  # [op1841] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 32  # [op1842] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t0, t0, e16, m1, ta,ma  # [op1843] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmand.mm v1, v1, v2  # [op1844] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 32  # [op1845] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t0, t0, e32, m1, ta,ma  # [op1846] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vid.v v2  # [op1847] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vadd.vx v2, v2, s1  # [op1848] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 32  # [op1849] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vwadd.vx v4, v2, x0  # [op1851] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
    # [peephole-li] [op1852] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t0, t0, e64, m2, ta,ma  # [op1853] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 4  # [op1854] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmul.vx v2, v4, t0  # [op1855] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 24960  # [op1856] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld t1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
add t0, t1, t0  # [op1857] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t1, 32  # [op1858] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t1, t1, e32, m1, ta,ma  # [op1859] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t1, 1  # [op1860] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv.v.x v4, t1  # [op1861] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t1, 0  # [op1862] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv.v.x v5, t1  # [op1863] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv1r.v v0, v1  # [op1864] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmerge.vvm v4, v5, v4, v0  # [op1865] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsuxei64.v v4, (t0), v2  # [op1866] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 32  # [op1867] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t0, t0, e16, m1, ta,ma  # [op1868] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 32  # [op1869] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t0, t0, e32, m1, ta,ma  # [op1870] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vid.v v2  # [op1871] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vadd.vx v2, v2, s1  # [op1872] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 32  # [op1873] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vwadd.vx v4, v2, x0  # [op1875] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
    # [peephole-li] [op1876] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t0, t0, e64, m2, ta,ma  # [op1877] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 4  # [op1878] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmul.vx v2, v4, t0  # [op1879] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 24960  # [op1880] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
ld t1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
add t0, t1, t0  # [op1881] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t1, 32  # [op1882] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t1, t1, e32, m1, ta,ma  # [op1883] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t1, 1  # [op1884] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv.v.x v4, t1  # [op1885] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t1, 0  # [op1886] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv.v.x v5, t1  # [op1887] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmv1r.v v0, v1  # [op1888] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vmerge.vvm v4, v5, v4, v0  # [op1889] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsuxei64.v v4, (t0), v2  # [op1890] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 32  # [op1891] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
vsetvli t0, t0, e16, m1, ta,ma  # [op1892] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:34:26
li t0, 32  # [op1893] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e32, m1, ta,ma  # [op1894] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vid.v v2  # [op1895] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vadd.vx v2, v2, s1  # [op1896] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 16  # [op1897] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.x v3, t0  # [op1898] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vdiv.vv v2, v2, v3  # [op1899] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op1900] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vwadd.vx v4, v2, x0  # [op1902] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
    # [peephole-li] [op1903] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e64, m2, ta,ma  # [op1904] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 4  # [op1905] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmul.vx v2, v4, t0  # [op1906] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 15936  # [op1907] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
ld t1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add t0, t1, t0  # [op1908] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t1, 32  # [op1909] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t1, t1, e32, m1, ta,ma  # [op1910] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vluxei64.v v4, (t0), v2  # [op1911] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op1912] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e16, m1, ta,ma  # [op1913] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op1914] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e32, m1, ta,ma  # [op1915] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vid.v v2  # [op1916] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vadd.vx v2, v2, s1  # [op1917] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 16  # [op1918] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.x v3, t0  # [op1919] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vrem.vv v2, v2, v3  # [op1920] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op1921] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vwadd.vx v6, v2, x0  # [op1923] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
    # [peephole-li] [op1924] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e64, m2, ta,ma  # [op1925] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 4  # [op1926] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmul.vx v2, v6, t0  # [op1927] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 64  # [op1928] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
ld t1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add t0, t1, t0  # [op1929] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t1, 32  # [op1930] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t1, t1, e32, m1, ta,ma  # [op1931] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vluxei64.v v5, (t0), v2  # [op1932] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op1933] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e16, m1, ta,ma  # [op1934] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op1935] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e32, m1, ta,ma  # [op1936] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vadd.vv v2, v4, v5  # [op1937] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op1938] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e16, m1, ta,ma  # [op1939] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op1940] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e32, m1, ta,ma  # [op1941] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vwadd.vx v4, v2, x0  # [op1942] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op1943] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e64, m2, ta,ma  # [op1944] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 2  # [op1945] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmul.vx v2, v4, t0  # [op1946] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op1947] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e16, m1, ta,ma  # [op1948] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 35904  # [op1949] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
ld t1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add t0, t1, t0  # [op1950] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t1, 128  # [op1951] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add t1, t0, t1  # [op1952] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op1953] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e32, m1, ta,ma  # [op1954] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 0  # [op1955] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.x v4, a2  # [op1956] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 1  # [op1957] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.x v5, a2  # [op1958] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv1r.v v0, v1  # [op1959] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmerge.vvm v4, v4, v5, v0  # [op1960] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vid.v v1  # [op1961] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vadd.vx v1, v1, s1  # [op1962] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op1963] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vwadd.vx v6, v1, x0  # [op1965] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
    # [peephole-li] [op1966] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1967] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 4  # [op1968] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmul.vx v6, v6, a2  # [op1969] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 27008  # [op1970] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
ld a3, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a2, a3, a2  # [op1971] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a3, 32  # [op1972] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a3, a3, e32, m1, ta,ma  # [op1973] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vluxei64.v v1, (a2), v6  # [op1974] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op1975] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.v v6, v1  # [op1977] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
    # [peephole-li] [op1978] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e16, m1, ta,ma  # [op1979] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vfncvt.f.f.w v1, v6  # [op1980] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op1981] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1982] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
ld a2, 160(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vadd.vx v6, v2, a2  # [op1983] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op1984] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e32, m1, ta,ma  # [op1985] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 0  # [op1986] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.x v2, a2  # [op1987] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmsne.vv v2, v4, v2  # [op1988] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv1r.v v0, v2  # [op1989] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op1990] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1991] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 0  # [op1992] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.x v4, a2  # [op1993] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.v.x v2, t1  # [op1994] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsub.vv v6, v6, v2  # [op1995] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmerge.vvm v4, v4, v6, v0  # [op1996] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vadd.vv v2, v2, v4  # [op1997] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op1998] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e16, m1, ta,ma  # [op1999] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2000] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2001] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2002] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a3, 0  # [op2003] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2004] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2005] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2006] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2007] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2008] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2009] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2010] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2011] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2012] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2013] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2014] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2015] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a3, 2  # [op2016] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2017] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2018] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2019] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2020] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2021] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2022] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2023] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2024] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2025] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2026] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2027] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2028] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a3, 4  # [op2029] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2030] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2031] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2032] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2033] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2034] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2035] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2036] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2037] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2038] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2039] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2040] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2041] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a3, 6  # [op2042] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2043] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2044] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2045] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2046] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2047] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2048] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2049] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2050] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2051] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2052] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2053] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2054] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a3, 8  # [op2055] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2056] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2057] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2058] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2059] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2060] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2061] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2062] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2063] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2064] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2065] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2066] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2067] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a3, 10  # [op2068] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2069] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2070] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2071] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2072] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2073] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2074] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2075] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2076] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2077] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2078] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2079] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2080] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a3, 12  # [op2081] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2082] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2083] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2084] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2085] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2086] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2087] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2088] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2089] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2090] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2091] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2092] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2093] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a3, 14  # [op2094] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2095] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2096] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2097] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2098] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2099] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2100] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2101] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2102] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2103] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2104] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2105] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2106] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a3, 16  # [op2107] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2108] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2109] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2110] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2111] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2112] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2113] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2114] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2115] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2116] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2117] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2118] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2119] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a3, 18  # [op2120] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2121] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2122] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2123] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2124] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2125] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2126] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2127] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2128] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2129] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2130] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2131] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2132] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a3, 20  # [op2133] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2134] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2135] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2136] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2137] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2138] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2139] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2140] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2141] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2142] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2143] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2144] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2145] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a3, 22  # [op2146] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2147] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2148] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2149] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2150] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2151] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2152] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2153] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2154] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2155] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2156] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2157] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2158] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a3, 24  # [op2159] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2160] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2161] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2162] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2163] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2164] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2165] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2166] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2167] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2168] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2169] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2170] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2171] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a3, 26  # [op2172] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2173] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2174] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2175] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2176] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2177] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2178] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2179] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2180] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2181] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2182] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2183] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2184] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a3, 28  # [op2185] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2186] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2187] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2188] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2189] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2190] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2191] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2192] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2193] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2194] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2195] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2196] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2197] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a3, 30  # [op2198] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2199] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2200] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2201] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2202] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2203] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2204] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2205] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2206] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2207] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2208] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2209] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2210] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a3, 32  # [op2211] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2212] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2213] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2214] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2215] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2216] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2217] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2218] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2219] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2220] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2221] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2222] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2223] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a3, 34  # [op2224] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2225] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2226] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2227] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2228] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2229] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2230] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2231] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2232] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2233] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2234] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2235] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2236] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a3, 36  # [op2237] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2238] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2239] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2240] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2241] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2242] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2243] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2244] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2245] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2246] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2247] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2248] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2249] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a3, 38  # [op2250] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2251] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2252] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2253] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2254] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2255] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2256] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2257] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2258] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2259] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2260] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2261] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2262] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a3, 40  # [op2263] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2264] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2265] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2266] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2267] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2268] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2269] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2270] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2271] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2272] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2273] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2274] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2275] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a3, 42  # [op2276] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2277] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2278] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2279] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2280] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2281] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2282] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2283] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2284] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2285] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2286] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2287] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2288] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a3, 44  # [op2289] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2290] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2291] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2292] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2293] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2294] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2295] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2296] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2297] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2298] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2299] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2300] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2301] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a3, 46  # [op2302] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2303] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2304] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2305] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2306] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2307] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2308] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2309] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2310] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2311] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2312] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2313] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2314] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a3, 48  # [op2315] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2316] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2317] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2318] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2319] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2320] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2321] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2322] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2323] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2324] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2325] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2326] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2327] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a3, 50  # [op2328] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2329] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2330] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2331] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2332] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2333] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2334] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2335] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2336] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2337] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2338] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2339] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2340] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a3, 52  # [op2341] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2342] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2343] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2344] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2345] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2346] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2347] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2348] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2349] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2350] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2351] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2352] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2353] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a3, 54  # [op2354] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2355] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2356] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2357] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2358] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2359] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2360] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2361] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2362] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2363] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2364] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2365] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2366] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a3, 56  # [op2367] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2368] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2369] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2370] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2371] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2372] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2373] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2374] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2375] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2376] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2377] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2378] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2379] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a3, 58  # [op2380] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2381] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2382] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2383] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2384] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2385] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2386] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2387] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2388] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2389] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2390] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2391] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2392] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a3, 60  # [op2393] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2394] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2395] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2396] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2397] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2398] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2399] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2400] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2401] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2402] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2403] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2404] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2405] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a3, 62  # [op2406] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2407] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2408] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2409] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2410] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2411] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2412] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
lhu t1, 0(a2)  # [op2413] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
sh t1, 0(a3)  # [op2414] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t1, 32  # [op2415] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t1, t1, e64, m2, ta,ma  # [op2416] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2417] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t1, 32  # [op2418] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vsetvli t1, t1, e16, m1, ta,ma  # [op2419] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vle16.v v1, 0(t0)  # [op2420] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 29056  # [op2421] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
ld t1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add t0, t1, t0  # [op2422] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
mv t1, s1  # [op2423] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li a2, 2  # [op2424] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
mul t1, t1, a2  # [op2425] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
add t0, t0, t1  # [op2426] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
vse16.v v1, 0(t0)  # [op2427] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op2428] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t0, a1, t0  # [op2429] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li t1, 32  # [op2430] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t1, s1, t1  # [op2431] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op2432] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv s1, t1  # [op2434] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv a1, t0  # [op2434] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk25_head  # [op2434] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lmtile26.head:  # block mtile26.head
slt t0, a7, t3  # [op2435] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
bne t0, zero, .Lbrc2436_true  # [op2436] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mv t0, a7  # [op2436] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lmtile26.exit  # [op2436] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lbrc2436_true:  # [op2436] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lmtile26.body  # [op2436] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lmtile26.body:  # block mtile26.body
li a5, 2  # [op2437] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
divu t0, a7, a5  # [op2438] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul t1, t0, a5  # [op2439] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub s1, a7, t1  # [op2440] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t1, 8  # [op2441] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul t0, t0, t1  # [op2442] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sd t0, 224(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul t0, s1, t1  # [op2443] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sd t0, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t0, 8  # [op2444] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vsetvli t0, t0, e32, m1, ta,ma  # [op2445] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t0, 0  # [op2446] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv.v.x v5, t0  # [op2447] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t1, 0  # [op2448] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t0, 224(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a3, t0, t1  # [op2449] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t0, 16  # [op2450] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt s1, a3, t0  # [op2451] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a4, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub a4, t0, a4  # [op2452] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub s1, t1, s1  # [op2453] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
and s1, a4, s1  # [op2454] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
addiw s1, s1, 0  # [op2455] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a4, 8  # [op2456] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv.v.x v6, s1  # [op2458] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmslt.vv v6, v1, v6  # [op2459] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v6  # [op2460] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a4, 256  # [op2461] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a6, s1, a4  # [op2462] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s1, 64  # [op2463] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul a3, a3, s1  # [op2464] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a6, a6, a3  # [op2465] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a3, 4  # [op2466] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s4, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul s4, s4, a3  # [op2467] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a6, a6, s4  # [op2468] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s4, 8  # [op2469] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle32.v v6, 0(a6), v0.t  # [op2471] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmerge.vvm v6, v5, v6, v0  # [op2472] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a6, 200(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a6, a6, t1  # [op2473] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
    # [peephole-li] [op2474] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse32.v v6, 0(a6)  # [op2476] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a6, 1  # [op2477] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s4, 224(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a6, s4, a6  # [op2478] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt s4, a6, t0  # [op2479] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s5, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub s5, t0, s5  # [op2480] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub s4, t1, s4  # [op2481] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
and s4, s5, s4  # [op2482] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
addiw s4, s4, 0  # [op2483] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s5, 8  # [op2484] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv.v.x v6, s4  # [op2486] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmslt.vv v6, v1, v6  # [op2487] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v6  # [op2488] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s4, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s4, s4, a4  # [op2489] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul a6, a6, s1  # [op2490] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a6, s4, a6  # [op2491] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s4, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul s4, s4, a3  # [op2492] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a6, a6, s4  # [op2493] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s4, 8  # [op2494] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle32.v v6, 0(a6), v0.t  # [op2496] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmerge.vvm v6, v5, v6, v0  # [op2497] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s4, 32  # [op2498] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a6, 200(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a6, a6, s4  # [op2499] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
    # [peephole-li] [op2500] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse32.v v6, 0(a6)  # [op2502] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a6, 224(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a5, a6, a5  # [op2503] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt a6, a5, t0  # [op2504] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s5, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub s5, t0, s5  # [op2505] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub a6, t1, a6  # [op2506] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
and a6, s5, a6  # [op2507] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
addiw a6, a6, 0  # [op2508] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s5, 8  # [op2509] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv.v.x v6, a6  # [op2511] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmslt.vv v6, v1, v6  # [op2512] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v6  # [op2513] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a6, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a6, a6, a4  # [op2514] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul a5, a5, s1  # [op2515] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a5, a6, a5  # [op2516] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a6, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul a6, a6, a3  # [op2517] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a5, a5, a6  # [op2518] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a6, 8  # [op2519] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle32.v v6, 0(a5), v0.t  # [op2521] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmerge.vvm v6, v5, v6, v0  # [op2522] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a5, 200(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a5, a5, s1  # [op2523] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
    # [peephole-li] [op2524] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse32.v v6, 0(a5)  # [op2526] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a5, 3  # [op2527] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a6, 224(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a5, a6, a5  # [op2528] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt a6, a5, t0  # [op2529] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s5, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub s5, t0, s5  # [op2530] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub a6, t1, a6  # [op2531] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
and a6, s5, a6  # [op2532] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
addiw a6, a6, 0  # [op2533] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s5, 8  # [op2534] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv.v.x v6, a6  # [op2536] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmslt.vv v6, v1, v6  # [op2537] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v6  # [op2538] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a6, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a6, a6, a4  # [op2539] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul a5, a5, s1  # [op2540] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a5, a6, a5  # [op2541] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a6, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul a6, a6, a3  # [op2542] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a5, a5, a6  # [op2543] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a6, 8  # [op2544] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle32.v v6, 0(a5), v0.t  # [op2546] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmerge.vvm v6, v5, v6, v0  # [op2547] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a5, 96  # [op2548] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a6, 200(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a5, a6, a5  # [op2549] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a6, 8  # [op2550] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse32.v v6, 0(a5)  # [op2552] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a5, 224(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a5, a5, a3  # [op2553] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt a6, a5, t0  # [op2554] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s5, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub s5, t0, s5  # [op2555] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub a6, t1, a6  # [op2556] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
and a6, s5, a6  # [op2557] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
addiw a6, a6, 0  # [op2558] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s5, 8  # [op2559] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv.v.x v6, a6  # [op2561] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmslt.vv v6, v1, v6  # [op2562] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v6  # [op2563] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a6, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a6, a6, a4  # [op2564] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul a5, a5, s1  # [op2565] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a5, a6, a5  # [op2566] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a6, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul a6, a6, a3  # [op2567] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a5, a5, a6  # [op2568] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a6, 8  # [op2569] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle32.v v6, 0(a5), v0.t  # [op2571] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmerge.vvm v6, v5, v6, v0  # [op2572] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a5, 128  # [op2573] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a6, 200(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a5, a6, a5  # [op2574] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a6, 8  # [op2575] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse32.v v6, 0(a5)  # [op2577] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a5, 5  # [op2578] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a6, 224(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a5, a6, a5  # [op2579] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt a6, a5, t0  # [op2580] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s5, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub s5, t0, s5  # [op2581] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub a6, t1, a6  # [op2582] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
and a6, s5, a6  # [op2583] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
addiw a6, a6, 0  # [op2584] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s5, 8  # [op2585] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv.v.x v6, a6  # [op2587] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmslt.vv v6, v1, v6  # [op2588] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v6  # [op2589] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a6, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a6, a6, a4  # [op2590] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul a5, a5, s1  # [op2591] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a5, a6, a5  # [op2592] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a6, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul a6, a6, a3  # [op2593] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a5, a5, a6  # [op2594] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a6, 8  # [op2595] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle32.v v6, 0(a5), v0.t  # [op2597] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmerge.vvm v6, v5, v6, v0  # [op2598] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a5, 160  # [op2599] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a6, 200(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a5, a6, a5  # [op2600] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a6, 8  # [op2601] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse32.v v6, 0(a5)  # [op2603] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a5, 6  # [op2604] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a6, 224(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a5, a6, a5  # [op2605] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt a6, a5, t0  # [op2606] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s5, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub s5, t0, s5  # [op2607] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub a6, t1, a6  # [op2608] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
and a6, s5, a6  # [op2609] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
addiw a6, a6, 0  # [op2610] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s5, 8  # [op2611] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv.v.x v6, a6  # [op2613] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmslt.vv v6, v1, v6  # [op2614] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v6  # [op2615] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a6, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a6, a6, a4  # [op2616] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul a5, a5, s1  # [op2617] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a5, a6, a5  # [op2618] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a6, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul a6, a6, a3  # [op2619] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a5, a5, a6  # [op2620] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a6, 8  # [op2621] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle32.v v6, 0(a5), v0.t  # [op2623] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmerge.vvm v6, v5, v6, v0  # [op2624] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a5, 192  # [op2625] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a6, 200(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a5, a6, a5  # [op2626] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a6, 8  # [op2627] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse32.v v6, 0(a5)  # [op2629] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a5, 7  # [op2630] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a6, 224(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a5, a6, a5  # [op2631] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt a6, a5, t0  # [op2632] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s5, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub t0, t0, s5  # [op2633] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub a6, t1, a6  # [op2634] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
and t0, t0, a6  # [op2635] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
addiw t0, t0, 0  # [op2636] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a6, 8  # [op2637] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv.v.x v6, t0  # [op2639] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmslt.vv v6, v1, v6  # [op2640] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v6  # [op2641] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t0, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t0, t0, a4  # [op2642] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul s1, a5, s1  # [op2643] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t0, t0, s1  # [op2644] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s1, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul s1, s1, a3  # [op2645] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t0, t0, s1  # [op2646] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s1, 8  # [op2647] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle32.v v6, 0(t0), v0.t  # [op2649] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmerge.vvm v5, v5, v6, v0  # [op2650] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t0, 224  # [op2651] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s1, 200(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t0, s1, t0  # [op2652] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s1, 8  # [op2653] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse32.v v5, 0(t0)  # [op2655] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t0, 64  # [op2656] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vsetvli t0, t0, e32, m2, ta,ma  # [op2657] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t0, 200(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle32.v v6, 0(t0)  # [op2658] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lmk27.head  # [op2659] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lmtile26.exit:  # block mtile26.exit
addw t1, s2, s11  # [op2660] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
li s1, 30080  # [op2661] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
li a1, 256  # [op2662] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
li t0, 0  # [op2663] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
li a2, 256  # [op2664] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
li a3, 32  # [op2665] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
j .Lmcarry31.head  # [op2666] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
.Lmk27.head:  # block mk27.head
slt t0, t1, s4  # [op2667] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
bne t0, zero, .Lbrc2668_true  # [op2668] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mv t0, t1  # [op2668] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lmk27.exit  # [op2668] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lbrc2668_true:  # [op2668] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lmk27.body  # [op2668] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lmk27.body:  # block mk27.body
li t0, 32  # [op2669] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub t0, t0, t1  # [op2670] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sd t0, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t0, 8  # [op2671] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s1, 224(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s1, s1, t0  # [op2672] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a3, 17  # [op2673] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt s1, s1, a3  # [op2674] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a3, 1  # [op2675] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a4, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a3, a4, a3  # [op2676] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt t0, t0, a3  # [op2677] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
and t0, s1, t0  # [op2678] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
bne t0, zero, .Lbrc2679_true  # [op2679] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Ltaf28.else  # [op2679] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lbrc2679_true:  # [op2679] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Ltaf28.then  # [op2679] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lmk27.exit:  # block mk27.exit
li t0, 64  # [op2680] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vsetvli t0, t0, e32, m2, ta,ma  # [op2681] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t0, 200(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse32.v v6, 0(t0)  # [op2682] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t1, 0  # [op2683] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t0, 224(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a3, t0, t1  # [op2684] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t0, 16  # [op2685] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt s1, a3, t0  # [op2686] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a4, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub a4, t0, a4  # [op2687] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub s1, t1, s1  # [op2688] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
and s1, a4, s1  # [op2689] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
addiw s1, s1, 0  # [op2690] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a4, 8  # [op2691] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vsetvli a4, a4, e32, m1, ta,ma  # [op2692] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv.v.x v5, s1  # [op2693] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmslt.vv v5, v1, v5  # [op2694] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v5  # [op2695] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s1, 200(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s1, s1, t1  # [op2696] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a4, 8  # [op2697] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle32.v v5, 0(s1)  # [op2699] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a4, 30080  # [op2700] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a5, s1, a4  # [op2701] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s1, 64  # [op2702] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul a3, a3, s1  # [op2703] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a5, a5, a3  # [op2704] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a3, 4  # [op2705] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a6, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul a6, a6, a3  # [op2706] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a5, a5, a6  # [op2707] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a6, 8  # [op2708] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse32.v v5, 0(a5), v0.t  # [op2710] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a5, 1  # [op2711] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a6, 224(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a6, a6, a5  # [op2712] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt s4, a6, t0  # [op2713] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s5, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub s5, t0, s5  # [op2714] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub s4, t1, s4  # [op2715] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
and s4, s5, s4  # [op2716] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
addiw s4, s4, 0  # [op2717] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s5, 8  # [op2718] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv.v.x v5, s4  # [op2720] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmslt.vv v5, v1, v5  # [op2721] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v5  # [op2722] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s4, 32  # [op2723] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s5, 200(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s4, s5, s4  # [op2724] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s5, 8  # [op2725] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle32.v v5, 0(s4)  # [op2727] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s4, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s4, s4, a4  # [op2728] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul a6, a6, s1  # [op2729] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a6, s4, a6  # [op2730] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s4, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul s4, s4, a3  # [op2731] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a6, a6, s4  # [op2732] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s4, 8  # [op2733] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse32.v v5, 0(a6), v0.t  # [op2735] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a6, 2  # [op2736] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s4, 224(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a6, s4, a6  # [op2737] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt s4, a6, t0  # [op2738] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s5, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub s5, t0, s5  # [op2739] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub s4, t1, s4  # [op2740] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
and s4, s5, s4  # [op2741] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
addiw s4, s4, 0  # [op2742] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s5, 8  # [op2743] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv.v.x v5, s4  # [op2745] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmslt.vv v5, v1, v5  # [op2746] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v5  # [op2747] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s4, 200(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s4, s4, s1  # [op2748] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
    # [peephole-li] [op2749] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle32.v v5, 0(s4)  # [op2751] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s4, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s4, s4, a4  # [op2752] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul a6, a6, s1  # [op2753] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a6, s4, a6  # [op2754] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s4, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul s4, s4, a3  # [op2755] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a6, a6, s4  # [op2756] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s4, 8  # [op2757] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse32.v v5, 0(a6), v0.t  # [op2759] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a6, 3  # [op2760] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s4, 224(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a6, s4, a6  # [op2761] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt s4, a6, t0  # [op2762] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s5, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub s5, t0, s5  # [op2763] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub s4, t1, s4  # [op2764] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
and s4, s5, s4  # [op2765] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
addiw s4, s4, 0  # [op2766] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s5, 8  # [op2767] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv.v.x v5, s4  # [op2769] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmslt.vv v5, v1, v5  # [op2770] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v5  # [op2771] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s4, 96  # [op2772] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s5, 200(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s4, s5, s4  # [op2773] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s5, 8  # [op2774] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle32.v v5, 0(s4)  # [op2776] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s4, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s4, s4, a4  # [op2777] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul a6, a6, s1  # [op2778] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a6, s4, a6  # [op2779] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s4, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul s4, s4, a3  # [op2780] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a6, a6, s4  # [op2781] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s4, 8  # [op2782] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse32.v v5, 0(a6), v0.t  # [op2784] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a6, 224(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a6, a6, a3  # [op2785] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt s4, a6, t0  # [op2786] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s5, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub s5, t0, s5  # [op2787] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub s4, t1, s4  # [op2788] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
and s4, s5, s4  # [op2789] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
addiw s4, s4, 0  # [op2790] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s5, 8  # [op2791] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv.v.x v5, s4  # [op2793] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmslt.vv v5, v1, v5  # [op2794] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v5  # [op2795] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s4, 128  # [op2796] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s5, 200(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s4, s5, s4  # [op2797] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s5, 8  # [op2798] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle32.v v5, 0(s4)  # [op2800] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s4, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s4, s4, a4  # [op2801] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul a6, a6, s1  # [op2802] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a6, s4, a6  # [op2803] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s4, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul s4, s4, a3  # [op2804] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a6, a6, s4  # [op2805] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s4, 8  # [op2806] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse32.v v5, 0(a6), v0.t  # [op2808] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a6, 5  # [op2809] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s4, 224(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a6, s4, a6  # [op2810] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt s4, a6, t0  # [op2811] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s5, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub s5, t0, s5  # [op2812] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub s4, t1, s4  # [op2813] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
and s4, s5, s4  # [op2814] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
addiw s4, s4, 0  # [op2815] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s5, 8  # [op2816] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv.v.x v5, s4  # [op2818] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmslt.vv v5, v1, v5  # [op2819] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v5  # [op2820] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s4, 160  # [op2821] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s5, 200(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s4, s5, s4  # [op2822] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s5, 8  # [op2823] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle32.v v5, 0(s4)  # [op2825] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s4, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s4, s4, a4  # [op2826] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul a6, a6, s1  # [op2827] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a6, s4, a6  # [op2828] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s4, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul s4, s4, a3  # [op2829] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a6, a6, s4  # [op2830] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s4, 8  # [op2831] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse32.v v5, 0(a6), v0.t  # [op2833] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a6, 6  # [op2834] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s4, 224(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a6, s4, a6  # [op2835] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt s4, a6, t0  # [op2836] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s5, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub s5, t0, s5  # [op2837] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub s4, t1, s4  # [op2838] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
and s4, s5, s4  # [op2839] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
addiw s4, s4, 0  # [op2840] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s5, 8  # [op2841] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv.v.x v5, s4  # [op2843] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmslt.vv v5, v1, v5  # [op2844] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v5  # [op2845] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s4, 192  # [op2846] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s5, 200(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s4, s5, s4  # [op2847] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s5, 8  # [op2848] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle32.v v5, 0(s4)  # [op2850] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s4, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s4, s4, a4  # [op2851] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul a6, a6, s1  # [op2852] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a6, s4, a6  # [op2853] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s4, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul s4, s4, a3  # [op2854] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a6, a6, s4  # [op2855] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s4, 8  # [op2856] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse32.v v5, 0(a6), v0.t  # [op2858] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a6, 7  # [op2859] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s4, 224(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a6, s4, a6  # [op2860] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt s4, a6, t0  # [op2861] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s5, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub t0, t0, s5  # [op2862] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub t1, t1, s4  # [op2863] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
and t0, t0, t1  # [op2864] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
addiw t0, t0, 0  # [op2865] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t1, 8  # [op2866] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv.v.x v5, t0  # [op2868] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmslt.vv v5, v1, v5  # [op2869] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v5  # [op2870] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t0, 224  # [op2871] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t1, 200(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t0, t1, t0  # [op2872] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t1, 8  # [op2873] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle32.v v5, 0(t0)  # [op2875] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t0, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t0, t0, a4  # [op2876] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul t1, a6, s1  # [op2877] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t0, t0, t1  # [op2878] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t1, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul t1, t1, a3  # [op2879] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t0, t0, t1  # [op2880] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t1, 8  # [op2881] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse32.v v5, 0(t0), v0.t  # [op2883] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t0, a7, a5  # [op2884] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mv a7, t0  # [op2885] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lmtile26.head  # [op2885] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Ltaf28.then:  # block taf28.then
li t0, 8  # [op2886] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vsetvli t0, t0, e16, m1, ta,ma  # [op2887] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t0, 14656  # [op2888] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s1, s1, t0  # [op2889] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t0, 64  # [op2890] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a3, 224(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul a3, a3, t0  # [op2891] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s1, s1, a3  # [op2892] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a3, 2  # [op2893] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul a3, t1, a3  # [op2894] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s1, s1, a3  # [op2895] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle16.v v5, 0(s1)  # [op2896] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(a1)  # [op2897] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a3, s1, t0  # [op2898] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s1, 16  # [op2899] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a4, a1, s1  # [op2900] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle16.v v5, 0(a3)  # [op2901] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(a4)  # [op2902] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a3, a3, t0  # [op2903] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a4, a4, s1  # [op2904] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle16.v v5, 0(a3)  # [op2905] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(a4)  # [op2906] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a3, a3, t0  # [op2907] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a4, a4, s1  # [op2908] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle16.v v5, 0(a3)  # [op2909] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(a4)  # [op2910] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a3, a3, t0  # [op2911] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a4, a4, s1  # [op2912] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle16.v v5, 0(a3)  # [op2913] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(a4)  # [op2914] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a3, a3, t0  # [op2915] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a4, a4, s1  # [op2916] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle16.v v5, 0(a3)  # [op2917] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(a4)  # [op2918] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a3, a3, t0  # [op2919] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a4, a4, s1  # [op2920] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle16.v v5, 0(a3)  # [op2921] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(a4)  # [op2922] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t0, a3, t0  # [op2923] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s1, a4, s1  # [op2924] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle16.v v5, 0(t0)  # [op2925] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(s1)  # [op2926] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Ltaf28.join  # [op2927] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Ltaf28.else:  # block taf28.else
li t0, 0  # [op2928] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s1, 224(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a5, s1, t0  # [op2929] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a3, 16  # [op2930] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt a4, a5, a3  # [op2931] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s1, 8  # [op2932] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a6, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt a6, a6, s1  # [op2933] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub a6, t0, a6  # [op2934] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s5, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub s5, s1, s5  # [op2935] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
and a6, s5, a6  # [op2936] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s5, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a6, s5, a6  # [op2937] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub a4, t0, a4  # [op2938] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
and a4, a6, a4  # [op2939] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
addiw a4, a4, 0  # [op2940] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a6, 8  # [op2941] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vsetvli a6, a6, e32, m1, ta,ma  # [op2942] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv.v.x v5, a4  # [op2943] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmslt.vv v5, v2, v5  # [op2944] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v5  # [op2945] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a6, 14656  # [op2946] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a4, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s5, a4, a6  # [op2947] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a4, 64  # [op2948] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul a5, a5, a4  # [op2949] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s5, s5, a5  # [op2950] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a5, 2  # [op2951] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul t4, t1, a5  # [op2952] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s5, s5, t4  # [op2953] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op2954] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vsetvli t4, t4, e16, m1, ta,ma  # [op2955] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle16.v v5, 0(s5), v0.t  # [op2956] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmerge.vvm v5, v3, v5, v0  # [op2957] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s5, a1, t0  # [op2958] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op2959] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(s5)  # [op2961] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s5, 1  # [op2962] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t4, 224(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s5, t4, s5  # [op2963] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt t4, s5, a3  # [op2964] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t5, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt t5, t5, s1  # [op2965] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub t5, t0, t5  # [op2966] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t6, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub t6, s1, t6  # [op2967] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
and t5, t6, t5  # [op2968] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t6, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t5, t6, t5  # [op2969] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub t4, t0, t4  # [op2970] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
and t4, t5, t4  # [op2971] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
addiw t4, t4, 0  # [op2972] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t5, 8  # [op2973] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vsetvli t5, t5, e32, m1, ta,ma  # [op2974] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv.v.x v5, t4  # [op2975] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmslt.vv v5, v2, v5  # [op2976] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v5  # [op2977] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t4, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t4, t4, a6  # [op2978] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul s5, s5, a4  # [op2979] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s5, t4, s5  # [op2980] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul t4, t1, a5  # [op2981] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s5, s5, t4  # [op2982] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op2983] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vsetvli t4, t4, e16, m1, ta,ma  # [op2984] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle16.v v5, 0(s5), v0.t  # [op2985] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmerge.vvm v5, v3, v5, v0  # [op2986] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s5, a1, a3  # [op2987] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op2988] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(s5)  # [op2990] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s5, 224(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s5, s5, a5  # [op2991] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt t4, s5, a3  # [op2992] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t5, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt t5, t5, s1  # [op2993] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub t5, t0, t5  # [op2994] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t6, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub t6, s1, t6  # [op2995] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
and t5, t6, t5  # [op2996] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t6, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t5, t6, t5  # [op2997] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub t4, t0, t4  # [op2998] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
and t4, t5, t4  # [op2999] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
addiw t4, t4, 0  # [op3000] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t5, 8  # [op3001] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vsetvli t5, t5, e32, m1, ta,ma  # [op3002] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv.v.x v5, t4  # [op3003] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmslt.vv v5, v2, v5  # [op3004] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v5  # [op3005] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t4, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t4, t4, a6  # [op3006] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul s5, s5, a4  # [op3007] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s5, t4, s5  # [op3008] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul t4, t1, a5  # [op3009] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s5, s5, t4  # [op3010] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op3011] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vsetvli t4, t4, e16, m1, ta,ma  # [op3012] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle16.v v5, 0(s5), v0.t  # [op3013] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmerge.vvm v5, v3, v5, v0  # [op3014] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s5, 32  # [op3015] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s5, a1, s5  # [op3016] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op3017] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(s5)  # [op3019] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s5, 3  # [op3020] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t4, 224(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s5, t4, s5  # [op3021] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt t4, s5, a3  # [op3022] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t5, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt t5, t5, s1  # [op3023] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub t5, t0, t5  # [op3024] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t6, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub t6, s1, t6  # [op3025] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
and t5, t6, t5  # [op3026] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t6, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t5, t6, t5  # [op3027] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub t4, t0, t4  # [op3028] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
and t4, t5, t4  # [op3029] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
addiw t4, t4, 0  # [op3030] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t5, 8  # [op3031] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vsetvli t5, t5, e32, m1, ta,ma  # [op3032] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv.v.x v5, t4  # [op3033] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmslt.vv v5, v2, v5  # [op3034] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v5  # [op3035] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t4, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t4, t4, a6  # [op3036] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul s5, s5, a4  # [op3037] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s5, t4, s5  # [op3038] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul t4, t1, a5  # [op3039] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s5, s5, t4  # [op3040] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op3041] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vsetvli t4, t4, e16, m1, ta,ma  # [op3042] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle16.v v5, 0(s5), v0.t  # [op3043] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmerge.vvm v5, v3, v5, v0  # [op3044] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s5, 48  # [op3045] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s5, a1, s5  # [op3046] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op3047] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(s5)  # [op3049] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s5, 4  # [op3050] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t4, 224(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s5, t4, s5  # [op3051] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt t4, s5, a3  # [op3052] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t5, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt t5, t5, s1  # [op3053] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub t5, t0, t5  # [op3054] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t6, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub t6, s1, t6  # [op3055] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
and t5, t6, t5  # [op3056] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t6, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t5, t6, t5  # [op3057] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub t4, t0, t4  # [op3058] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
and t4, t5, t4  # [op3059] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
addiw t4, t4, 0  # [op3060] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t5, 8  # [op3061] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vsetvli t5, t5, e32, m1, ta,ma  # [op3062] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv.v.x v5, t4  # [op3063] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmslt.vv v5, v2, v5  # [op3064] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v5  # [op3065] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t4, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t4, t4, a6  # [op3066] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul s5, s5, a4  # [op3067] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s5, t4, s5  # [op3068] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul t4, t1, a5  # [op3069] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s5, s5, t4  # [op3070] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op3071] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vsetvli t4, t4, e16, m1, ta,ma  # [op3072] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle16.v v5, 0(s5), v0.t  # [op3073] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmerge.vvm v5, v3, v5, v0  # [op3074] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s5, a1, a4  # [op3075] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op3076] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(s5)  # [op3078] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s5, 5  # [op3079] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t4, 224(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s5, t4, s5  # [op3080] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt t4, s5, a3  # [op3081] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t5, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt t5, t5, s1  # [op3082] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub t5, t0, t5  # [op3083] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t6, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub t6, s1, t6  # [op3084] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
and t5, t6, t5  # [op3085] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t6, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t5, t6, t5  # [op3086] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub t4, t0, t4  # [op3087] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
and t4, t5, t4  # [op3088] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
addiw t4, t4, 0  # [op3089] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t5, 8  # [op3090] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vsetvli t5, t5, e32, m1, ta,ma  # [op3091] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv.v.x v5, t4  # [op3092] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmslt.vv v5, v2, v5  # [op3093] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v5  # [op3094] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t4, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t4, t4, a6  # [op3095] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul s5, s5, a4  # [op3096] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s5, t4, s5  # [op3097] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul t4, t1, a5  # [op3098] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s5, s5, t4  # [op3099] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op3100] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vsetvli t4, t4, e16, m1, ta,ma  # [op3101] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle16.v v5, 0(s5), v0.t  # [op3102] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmerge.vvm v5, v3, v5, v0  # [op3103] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s5, 80  # [op3104] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s5, a1, s5  # [op3105] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op3106] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(s5)  # [op3108] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s5, 6  # [op3109] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t4, 224(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s5, t4, s5  # [op3110] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt t4, s5, a3  # [op3111] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t5, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt t5, t5, s1  # [op3112] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub t5, t0, t5  # [op3113] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t6, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub t6, s1, t6  # [op3114] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
and t5, t6, t5  # [op3115] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t6, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t5, t6, t5  # [op3116] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub t4, t0, t4  # [op3117] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
and t4, t5, t4  # [op3118] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
addiw t4, t4, 0  # [op3119] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t5, 8  # [op3120] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vsetvli t5, t5, e32, m1, ta,ma  # [op3121] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv.v.x v5, t4  # [op3122] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmslt.vv v5, v2, v5  # [op3123] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v5  # [op3124] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t4, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t4, t4, a6  # [op3125] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul s5, s5, a4  # [op3126] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s5, t4, s5  # [op3127] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul t4, t1, a5  # [op3128] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s5, s5, t4  # [op3129] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op3130] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vsetvli t4, t4, e16, m1, ta,ma  # [op3131] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle16.v v5, 0(s5), v0.t  # [op3132] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmerge.vvm v5, v3, v5, v0  # [op3133] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s5, 96  # [op3134] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s5, a1, s5  # [op3135] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op3136] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(s5)  # [op3138] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s5, 7  # [op3139] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t4, 224(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s5, t4, s5  # [op3140] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt a3, s5, a3  # [op3141] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t4, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt t4, t4, s1  # [op3142] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub t4, t0, t4  # [op3143] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t5, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub s1, s1, t5  # [op3144] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
and s1, s1, t4  # [op3145] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t4, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s1, t4, s1  # [op3146] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub t0, t0, a3  # [op3147] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
and t0, s1, t0  # [op3148] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
addiw t0, t0, 0  # [op3149] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s1, 8  # [op3150] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vsetvli s1, s1, e32, m1, ta,ma  # [op3151] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv.v.x v5, t0  # [op3152] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmslt.vv v5, v2, v5  # [op3153] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v5  # [op3154] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t0, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t0, t0, a6  # [op3155] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul s1, s5, a4  # [op3156] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t0, t0, s1  # [op3157] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul s1, t1, a5  # [op3158] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t0, t0, s1  # [op3159] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s1, 8  # [op3160] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vsetvli s1, s1, e16, m1, ta,ma  # [op3161] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle16.v v5, 0(t0), v0.t  # [op3162] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vmerge.vvm v5, v3, v5, v0  # [op3163] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t0, 112  # [op3164] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t0, a1, t0  # [op3165] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s1, 8  # [op3166] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(t0)  # [op3168] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Ltaf28.join  # [op3169] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Ltaf28.join:  # block taf28.join
li t0, 8  # [op3170] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s1, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s1, s1, t0  # [op3171] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a3, 17  # [op3172] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt s1, s1, a3  # [op3173] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a3, 1  # [op3174] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a4, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a3, a4, a3  # [op3175] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt t0, t0, a3  # [op3176] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
and t0, s1, t0  # [op3177] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
bne t0, zero, .Lbrc3178_true  # [op3178] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lpbf29.else  # [op3178] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lbrc3178_true:  # [op3178] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lpbf29.then  # [op3178] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lpbf29.then:  # block pbf29.then
li t0, 8  # [op3179] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vsetvli t0, t0, e16, m1, ta,ma  # [op3180] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t0, 32  # [op3181] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s1, 29056  # [op3182] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a3, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s1, a3, s1  # [op3183] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul a3, t1, t0  # [op3184] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a3, s1, a3  # [op3185] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s1, 2  # [op3186] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a4, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul a4, a4, s1  # [op3187] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a3, a3, a4  # [op3188] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vlse16.v v5, 0(a3), t0  # [op3189] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(a2)  # [op3190] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a4, a3, s1  # [op3191] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a3, 16  # [op3192] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a5, a2, a3  # [op3193] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vlse16.v v5, 0(a4), t0  # [op3194] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(a5)  # [op3195] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a4, a4, s1  # [op3196] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a5, a5, a3  # [op3197] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vlse16.v v5, 0(a4), t0  # [op3198] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(a5)  # [op3199] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a4, a4, s1  # [op3200] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a5, a5, a3  # [op3201] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vlse16.v v5, 0(a4), t0  # [op3202] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(a5)  # [op3203] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a4, a4, s1  # [op3204] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a5, a5, a3  # [op3205] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vlse16.v v5, 0(a4), t0  # [op3206] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(a5)  # [op3207] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a4, a4, s1  # [op3208] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a5, a5, a3  # [op3209] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vlse16.v v5, 0(a4), t0  # [op3210] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(a5)  # [op3211] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a4, a4, s1  # [op3212] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a5, a5, a3  # [op3213] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vlse16.v v5, 0(a4), t0  # [op3214] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(a5)  # [op3215] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s1, a4, s1  # [op3216] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a3, a5, a3  # [op3217] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vlse16.v v5, 0(s1), t0  # [op3218] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(a3)  # [op3219] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lpbf29.join  # [op3220] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lpbf29.else:  # block pbf29.else
li t0, 8  # [op3221] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vsetvli t0, t0, e16, m1, ta,ma  # [op3222] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t0, 0  # [op3223] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s1, a2, t0  # [op3224] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse16.v v4, 0(s1)  # [op3225] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s1, 16  # [op3226] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s1, a2, s1  # [op3227] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse16.v v4, 0(s1)  # [op3228] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s1, 32  # [op3229] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s1, a2, s1  # [op3230] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse16.v v4, 0(s1)  # [op3231] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s1, 48  # [op3232] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s1, a2, s1  # [op3233] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse16.v v4, 0(s1)  # [op3234] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s1, 64  # [op3235] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s1, a2, s1  # [op3236] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse16.v v4, 0(s1)  # [op3237] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s1, 80  # [op3238] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s1, a2, s1  # [op3239] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse16.v v4, 0(s1)  # [op3240] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s1, 96  # [op3241] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s1, a2, s1  # [op3242] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse16.v v4, 0(s1)  # [op3243] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s1, 112  # [op3244] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s1, a2, s1  # [op3245] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse16.v v4, 0(s1)  # [op3246] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a6, 8  # [op3247] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lpb30.head  # [op3248] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lpb30.head:  # block pb30.head
slt s1, t0, a6  # [op3249] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
bne s1, zero, .Lbrc3250_true  # [op3250] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lpb30.exit  # [op3250] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lbrc3250_true:  # [op3250] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lpb30.body  # [op3250] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lpb30.body:  # block pb30.body
ld s1, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s1, s1, t0  # [op3251] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a3, 16  # [op3252] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt s5, s1, a3  # [op3253] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a4, 8  # [op3254] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld a5, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
slt t4, a5, a4  # [op3255] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a5, 0  # [op3256] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub t4, a5, t4  # [op3257] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t5, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub a4, a4, t5  # [op3258] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
and a4, a4, t4  # [op3259] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld t4, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a4, t4, a4  # [op3260] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
sub a5, a5, s5  # [op3261] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
and a5, a4, a5  # [op3262] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a4, 29056  # [op3263] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
ld s5, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s5, s5, a4  # [op3264] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li a4, 32  # [op3265] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul t4, t1, a4  # [op3266] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s5, s5, t4  # [op3267] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t4, 2  # [op3268] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul s1, s1, t4  # [op3269] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add s1, s5, s1  # [op3270] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mul a3, t0, a3  # [op3271] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add a3, a2, a3  # [op3272] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
addiw a5, a5, 0  # [op3273] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vsetvli a5, a5, e16, m1, ta,ma  # [op3274] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vlse16.v v5, 0(s1), a4  # [op3275] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(a3)  # [op3276] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li s1, 1  # [op3277] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t0, t0, s1  # [op3278] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lpb30.head  # [op3279] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lpb30.exit:  # block pb30.exit
j .Lpbf29.join  # [op3280] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lpbf29.join:  # block pbf29.join
li t0, 64  # [op3281] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vsetvli t0, t0, e16, m1, ta,ma  # [op3282] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle16.v v5, 0(a1)  # [op3283] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vle16.v v8, 0(a2)  # [op3284] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
vsetvli x0, zero, e16, m1, ta, ma
    smt.vfwmadot v6, v5, v8  # [op3285] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
li t0, 8  # [op3286] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
add t0, t1, t0  # [op3287] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
mv t1, t0  # [op3288] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
j .Lmk27.head  # [op3288] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:35:15
.Lmcarry31.head:  # block mcarry31.head
slt a4, t0, a2  # [op3289] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
bne a4, zero, .Lbrc3290_true  # [op3290] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
j .Lmcarry31.exit  # [op3290] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
.Lbrc3290_true:  # [op3290] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
j .Lmcarry31.body  # [op3290] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
.Lmcarry31.body:  # block mcarry31.body
ld a4, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
add a4, a4, s1  # [op3291] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
ld a5, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
add a5, a5, a1  # [op3292] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
li a6, 32  # [op3293] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
vsetvli a6, a6, e32, m1, ta,ma  # [op3294] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
vid.v v1  # [op3295] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
vadd.vx v1, v1, t0  # [op3296] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
li a6, 32  # [op3297] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
vwadd.vx v2, v1, x0  # [op3299] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
    # [peephole-li] [op3300] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
vsetvli a6, a6, e64, m2, ta,ma  # [op3301] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
li a6, 4  # [op3302] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
vmul.vx v2, v2, a6  # [op3303] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
li a6, 32  # [op3304] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
vsetvli a6, a6, e32, m1, ta,ma  # [op3305] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
vluxei64.v v1, (a4), v2  # [op3306] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
vsuxei64.v v1, (a5), v2  # [op3307] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
li a4, 16  # [op3308] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
vsetvli a4, a4, e32, m1, ta,ma  # [op3309] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
addw t0, t0, a3  # [op3310] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
j .Lmcarry31.head  # [op3311] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
.Lmcarry31.exit:  # block mcarry31.exit
mv s2, t1  # [op3312] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
j .Lmloop15.head  # [op3312] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:29:5
.Lchunk32_head:  # block chunk32_head
li s1, 16  # [op3313] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op3314] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc3315_true  # [op3315] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op3315] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op3315] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk32_exit  # [op3315] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc3315_true:  # [op3315] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk32_body  # [op3315] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk32_exit:  # block chunk32_exit
li t1, 0  # [op3316] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op3317] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op3317] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op3317] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk33_head  # [op3317] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk32_body:  # block chunk32_body
li s1, 16  # [op3318] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op3319] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 16  # [op3320] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
ld s1, 136(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vmv.v.x v1, s1  # [op3322] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vid.v v2  # [op3323] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vadd.vx v2, v2, t0  # [op3324] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
li s1, 16  # [op3325] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vwadd.vx v4, v2, x0  # [op3327] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
    # [peephole-li] [op3328] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vsetvli s1, s1, e64, m2, ta,ma  # [op3329] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
li s1, 4  # [op3330] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vmul.vx v2, v4, s1  # [op3331] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
li s1, 0  # [op3332] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
add s1, a1, s1  # [op3333] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
li a1, 16  # [op3334] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vsetvli a1, a1, e32, m1, ta,ma  # [op3335] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vluxei64.v v4, (s1), v2  # [op3336] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
li s1, 16  # [op3337] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vmul.vv v1, v4, v1  # [op3339] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vid.v v2  # [op3340] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vadd.vx v2, v2, t0  # [op3341] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
    # [peephole-li] [op3342] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vwadd.vx v4, v2, x0  # [op3344] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
    # [peephole-li] [op3345] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vsetvli s1, s1, e64, m2, ta,ma  # [op3346] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
li s1, 4  # [op3347] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vmul.vx v2, v4, s1  # [op3348] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
li s1, 31104  # [op3349] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
add s1, a1, s1  # [op3350] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
li a1, 16  # [op3351] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vsetvli a1, a1, e32, m1, ta,ma  # [op3352] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
vsuxei64.v v1, (s1), v2  # [op3353] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
li s1, 16  # [op3354] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:22
    # [peephole-li] [op3356] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op3357] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op3358] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op3359] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op3360] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk32_head  # [op3362] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk33_head:  # block chunk33_head
li s1, 256  # [op3363] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op3364] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc3365_true  # [op3365] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t2  # [op3365] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk33_exit  # [op3365] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc3365_true:  # [op3365] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk33_body  # [op3365] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk33_exit:  # block chunk33_exit
li t0, 0  # [op3366] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
j .Lstg34_head  # [op3367] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
.Lchunk33_body:  # block chunk33_body
li s1, 32  # [op3368] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op3369] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op3370] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
vid.v v1  # [op3372] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
vadd.vx v1, v1, t0  # [op3373] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
li s1, 16  # [op3374] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
vmv.v.x v2, s1  # [op3375] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
vdiv.vv v1, v1, v2  # [op3376] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
li s1, 32  # [op3377] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
vwadd.vx v2, v1, x0  # [op3379] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
    # [peephole-li] [op3380] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
vsetvli s1, s1, e64, m2, ta,ma  # [op3381] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
li s1, 8  # [op3382] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
vmul.vx v2, v2, s1  # [op3383] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
li s1, 31168  # [op3384] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
add s1, a1, s1  # [op3385] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
li a1, 32  # [op3386] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
vluxei64.v v4, (s1), v2  # [op3388] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
li s1, 32  # [op3389] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
vsetvli s1, s1, e32, m1, ta,ma  # [op3390] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:14
li s1, 32  # [op3391] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op3392] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op3393] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op3394] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op3395] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk33_head  # [op3397] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lstg34_head:  # block stg34_head
li s1, 256  # [op3398] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
slt s1, t0, s1  # [op3399] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
bne s1, zero, .Lbrc3400_true  # [op3400] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
j .Lstg34_exit  # [op3400] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
.Lbrc3400_true:  # [op3400] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
j .Lstg34_body  # [op3400] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
.Lstg34_body:  # block stg34_body
li s1, 32  # [op3401] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli s1, s1, e32, m1, ta,ma  # [op3402] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vid.v v1  # [op3403] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vadd.vx v1, v1, t0  # [op3404] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 16  # [op3405] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmv.v.x v2, s1  # [op3406] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vdiv.vv v2, v1, v2  # [op3407] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op3408] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmv.v.x v3, s1  # [op3409] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vrem.vv v2, v2, v3  # [op3410] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op3411] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmv.v.x v3, s1  # [op3412] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vrem.vv v3, v1, v3  # [op3413] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 32  # [op3414] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vwadd.vx v4, v2, x0  # [op3416] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op3417] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli s1, s1, e64, m2, ta,ma  # [op3418] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 4  # [op3419] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmul.vx v2, v4, s1  # [op3420] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 6144  # [op3421] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
add s1, a1, s1  # [op3422] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li a1, 32  # [op3423] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli a1, a1, e32, m1, ta,ma  # [op3424] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vluxei64.v v4, (s1), v2  # [op3425] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 32  # [op3426] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vwadd.vx v2, v1, x0  # [op3428] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op3429] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli s1, s1, e64, m2, ta,ma  # [op3430] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 4  # [op3431] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmul.vx v2, v2, s1  # [op3432] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 33344  # [op3433] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
add s1, a1, s1  # [op3434] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li a1, 32  # [op3435] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli a1, a1, e32, m1, ta,ma  # [op3436] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsuxei64.v v4, (s1), v2  # [op3437] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 32  # [op3438] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
addw t0, t0, s1  # [op3439] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
j .Lstg34_head  # [op3440] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
.Lstg34_exit:  # block stg34_exit
li t0, 0  # [op3441] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
j .Lstg35_head  # [op3442] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
.Lstg35_head:  # block stg35_head
li s1, 256  # [op3443] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
slt s1, t0, s1  # [op3444] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
bne s1, zero, .Lbrc3445_true  # [op3445] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
j .Lstg35_exit  # [op3445] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
.Lbrc3445_true:  # [op3445] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
j .Lstg35_body  # [op3445] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
.Lstg35_body:  # block stg35_body
li s1, 32  # [op3446] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli s1, s1, e32, m1, ta,ma  # [op3447] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vid.v v1  # [op3448] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vadd.vx v1, v1, t0  # [op3449] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 16  # [op3450] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmv.v.x v2, s1  # [op3451] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vdiv.vv v2, v1, v2  # [op3452] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op3453] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmv.v.x v3, s1  # [op3454] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vrem.vv v2, v2, v3  # [op3455] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op3456] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmv.v.x v2, s1  # [op3457] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vrem.vv v2, v1, v2  # [op3458] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 32  # [op3459] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vwadd.vx v4, v2, x0  # [op3461] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op3462] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli s1, s1, e64, m2, ta,ma  # [op3463] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 4  # [op3464] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmul.vx v2, v4, s1  # [op3465] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 20800  # [op3466] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
add s1, a1, s1  # [op3467] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li a1, 32  # [op3468] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli a1, a1, e32, m1, ta,ma  # [op3469] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vluxei64.v v4, (s1), v2  # [op3470] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 32  # [op3471] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vwadd.vx v2, v1, x0  # [op3473] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op3474] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli s1, s1, e64, m2, ta,ma  # [op3475] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 4  # [op3476] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmul.vx v2, v2, s1  # [op3477] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 34368  # [op3478] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
add s1, a1, s1  # [op3479] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li a1, 32  # [op3480] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli a1, a1, e32, m1, ta,ma  # [op3481] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsuxei64.v v4, (s1), v2  # [op3482] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li s1, 32  # [op3483] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
addw t0, t0, s1  # [op3484] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
j .Lstg35_head  # [op3485] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
.Lstg35_exit:  # block stg35_exit
li t0, 0  # [op3486] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv s1, t1  # [op3487] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t0  # [op3487] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk36_head  # [op3487] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk36_head:  # block chunk36_head
li t0, 256  # [op3488] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
slt t0, t1, t0  # [op3489] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
bne t0, zero, .Lbrc3490_true  # [op3490] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op3490] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, s1  # [op3490] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk36_exit  # [op3490] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lbrc3490_true:  # [op3490] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk36_body  # [op3490] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk36_exit:  # block chunk36_exit
mv t1, t0  # [op3491] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv t0, t2  # [op3491] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lprog_next  # [op3491] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lchunk36_body:  # block chunk36_body
li t0, 32  # [op3492] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli t0, t0, e16, m1, ta,ma  # [op3493] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li t0, 32  # [op3494] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli t0, t0, e32, m1, ta,ma  # [op3495] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vid.v v1  # [op3496] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vadd.vx v1, v1, t1  # [op3497] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li t0, 32  # [op3498] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vwadd.vx v2, v1, x0  # [op3500] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op3501] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli t0, t0, e64, m2, ta,ma  # [op3502] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li t0, 4  # [op3503] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmul.vx v2, v2, t0  # [op3504] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li t0, 33344  # [op3505] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
add t0, a1, t0  # [op3506] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li a1, 32  # [op3507] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli a1, a1, e32, m1, ta,ma  # [op3508] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vluxei64.v v1, (t0), v2  # [op3509] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li t0, 0  # [op3510] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmv.v.x v2, t0  # [op3511] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmsne.vv v1, v1, v2  # [op3512] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li t0, 32  # [op3513] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli t0, t0, e16, m1, ta,ma  # [op3514] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li t0, 32  # [op3515] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli t0, t0, e32, m1, ta,ma  # [op3516] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vid.v v2  # [op3517] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vadd.vx v2, v2, t1  # [op3518] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li t0, 32  # [op3519] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vwadd.vx v4, v2, x0  # [op3521] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op3522] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli t0, t0, e64, m2, ta,ma  # [op3523] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li t0, 4  # [op3524] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmul.vx v2, v4, t0  # [op3525] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li t0, 34368  # [op3526] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
add t0, a1, t0  # [op3527] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li a1, 32  # [op3528] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli a1, a1, e32, m1, ta,ma  # [op3529] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vluxei64.v v4, (t0), v2  # [op3530] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li t0, 0  # [op3531] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmv.v.x v2, t0  # [op3532] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmsne.vv v2, v4, v2  # [op3533] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li t0, 32  # [op3534] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vsetvli t0, t0, e16, m1, ta,ma  # [op3535] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
vmand.mm v1, v1, v2  # [op3536] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:37:19
li t0, 32  # [op3537] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e32, m1, ta,ma  # [op3538] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vid.v v2  # [op3539] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vadd.vx v2, v2, t1  # [op3540] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op3541] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vwadd.vx v4, v2, x0  # [op3543] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
    # [peephole-li] [op3544] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e64, m2, ta,ma  # [op3545] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 4  # [op3546] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmul.vx v2, v4, t0  # [op3547] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 256  # [op3548] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add t0, a1, t0  # [op3549] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a1, 32  # [op3550] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli a1, a1, e32, m1, ta,ma  # [op3551] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vluxei64.v v4, (t0), v2  # [op3552] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op3553] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e16, m1, ta,ma  # [op3554] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op3555] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e32, m1, ta,ma  # [op3556] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.v.v v2, v4  # [op3557] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op3558] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e16, m1, ta,ma  # [op3559] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vfncvt.f.f.w v4, v2  # [op3560] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op3561] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e32, m1, ta,ma  # [op3562] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vid.v v2  # [op3563] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vadd.vx v2, v2, t1  # [op3564] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 16  # [op3565] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.v.x v3, t0  # [op3566] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vdiv.vv v2, v2, v3  # [op3567] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op3568] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vwadd.vx v6, v2, x0  # [op3570] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
    # [peephole-li] [op3571] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e64, m2, ta,ma  # [op3572] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 4  # [op3573] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmul.vx v2, v6, t0  # [op3574] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 31104  # [op3575] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add t0, a1, t0  # [op3576] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a1, 32  # [op3577] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli a1, a1, e32, m1, ta,ma  # [op3578] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vluxei64.v v5, (t0), v2  # [op3579] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op3580] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e16, m1, ta,ma  # [op3581] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op3582] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e32, m1, ta,ma  # [op3583] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vid.v v2  # [op3584] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vadd.vx v2, v2, t1  # [op3585] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 16  # [op3586] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.v.x v3, t0  # [op3587] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vrem.vv v2, v2, v3  # [op3588] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op3589] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vwadd.vx v6, v2, x0  # [op3591] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
    # [peephole-li] [op3592] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e64, m2, ta,ma  # [op3593] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 4  # [op3594] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmul.vx v2, v6, t0  # [op3595] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 64  # [op3596] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add t0, a1, t0  # [op3597] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a1, 32  # [op3598] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli a1, a1, e32, m1, ta,ma  # [op3599] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vluxei64.v v6, (t0), v2  # [op3600] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op3601] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e16, m1, ta,ma  # [op3602] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op3603] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e32, m1, ta,ma  # [op3604] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vadd.vv v2, v5, v6  # [op3605] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op3606] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e16, m1, ta,ma  # [op3607] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op3608] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e32, m1, ta,ma  # [op3609] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vwadd.vx v6, v2, x0  # [op3610] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op3611] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e64, m2, ta,ma  # [op3612] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 2  # [op3613] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmul.vx v2, v6, t0  # [op3614] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op3615] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e16, m1, ta,ma  # [op3616] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li t0, 35904  # [op3617] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
ld a1, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add t0, a1, t0  # [op3618] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a1, 128  # [op3619] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a1, t0, a1  # [op3620] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 32  # [op3621] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vse16.v v4, 0(t0)  # [op3623] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
    # [peephole-li] [op3624] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli a2, a2, e32, m1, ta,ma  # [op3625] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 0  # [op3626] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.v.x v4, a2  # [op3627] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 1  # [op3628] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.v.x v5, a2  # [op3629] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv1r.v v0, v1  # [op3630] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmerge.vvm v4, v4, v5, v0  # [op3631] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 32  # [op3632] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli a2, a2, e64, m2, ta,ma  # [op3633] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
ld a2, 168(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vadd.vx v6, v2, a2  # [op3634] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 32  # [op3635] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli a2, a2, e32, m1, ta,ma  # [op3636] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 0  # [op3637] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.v.x v2, a2  # [op3638] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmsne.vv v2, v4, v2  # [op3639] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv1r.v v0, v2  # [op3640] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 32  # [op3641] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli a2, a2, e64, m2, ta,ma  # [op3642] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 0  # [op3643] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.v.x v4, a2  # [op3644] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.v.x v2, a1  # [op3645] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsub.vv v6, v6, v2  # [op3646] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmerge.vvm v4, v4, v6, v0  # [op3647] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vadd.vv v2, v2, v4  # [op3648] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a1, 32  # [op3649] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli a1, a1, e16, m1, ta,ma  # [op3650] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a1, 32  # [op3651] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vsetvli a1, a1, e64, m2, ta,ma  # [op3652] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3653] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
    # [peephole-li] [op3654] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3655] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3656] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3657] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3658] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3659] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 2  # [op3660] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3661] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3662] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3663] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3664] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3665] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 4  # [op3666] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3667] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3668] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3669] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3670] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3671] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 6  # [op3672] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3673] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3674] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3675] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3676] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3677] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 8  # [op3678] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3679] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3680] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3681] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3682] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3683] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 10  # [op3684] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3685] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3686] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3687] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3688] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3689] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 12  # [op3690] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3691] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3692] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3693] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3694] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3695] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 14  # [op3696] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3697] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3698] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3699] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3700] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3701] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 16  # [op3702] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3703] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3704] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3705] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3706] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3707] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 18  # [op3708] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3709] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3710] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3711] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3712] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3713] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 20  # [op3714] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3715] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3716] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3717] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3718] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3719] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 22  # [op3720] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3721] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3722] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3723] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3724] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3725] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 24  # [op3726] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3727] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3728] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3729] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3730] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3731] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 26  # [op3732] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3733] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3734] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3735] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3736] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3737] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 28  # [op3738] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3739] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3740] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3741] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3742] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3743] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 30  # [op3744] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3745] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3746] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3747] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3748] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3749] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 32  # [op3750] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3751] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3752] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3753] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3754] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3755] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 34  # [op3756] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3757] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3758] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3759] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3760] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3761] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 36  # [op3762] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3763] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3764] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3765] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3766] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3767] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 38  # [op3768] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3769] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3770] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3771] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3772] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3773] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 40  # [op3774] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3775] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3776] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3777] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3778] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3779] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 42  # [op3780] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3781] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3782] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3783] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3784] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3785] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 44  # [op3786] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3787] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3788] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3789] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3790] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3791] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 46  # [op3792] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3793] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3794] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3795] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3796] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3797] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 48  # [op3798] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3799] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3800] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3801] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3802] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3803] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 50  # [op3804] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3805] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3806] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3807] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3808] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3809] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 52  # [op3810] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3811] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3812] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3813] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3814] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3815] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 54  # [op3816] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3817] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3818] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3819] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3820] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3821] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 56  # [op3822] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3823] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3824] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3825] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3826] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3827] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 58  # [op3828] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3829] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3830] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3831] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3832] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3833] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 60  # [op3834] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3835] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3836] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3837] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3838] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3839] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
li a2, 62  # [op3840] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add t0, t0, a2  # [op3841] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
lhu t0, 0(t0)  # [op3842] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
sh t0, 0(a1)  # [op3843] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3844] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
vcpop.m t0, v1  # [op3845] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:36:5
add t0, s1, t0  # [op3846] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op3847] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addw t1, t1, s1  # [op3848] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op3849] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e16, m1, ta,ma  # [op3850] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
mv s1, t0  # [op3851] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lchunk36_head  # [op3851] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lprog_next:  # block prog_next
add t0, t0, s10  # [op3852] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
j .Lprog_head  # [op3853] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
.Lprog_exit:  # block prog_exit
sd t0, 0(s6)  # [op3854] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld ra, 0(sp)  # [op3855] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s1, 8(sp)  # [op3855] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s2, 16(sp)  # [op3855] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s3, 24(sp)  # [op3855] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s4, 32(sp)  # [op3855] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s5, 40(sp)  # [op3855] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s6, 48(sp)  # [op3855] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s7, 56(sp)  # [op3855] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s8, 64(sp)  # [op3855] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s9, 72(sp)  # [op3855] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s10, 80(sp)  # [op3855] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ld s11, 88(sp)  # [op3855] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
addi sp, sp, 240  # [op3855] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
ret  # [op3855] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/matmul.py:21:1
    .size operator_entry, .-operator_entry
    .section .note.GNU-stack,"",@progbits
