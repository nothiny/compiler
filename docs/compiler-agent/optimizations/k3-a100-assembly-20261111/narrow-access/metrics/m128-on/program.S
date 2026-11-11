# a100c emitted program: matmul_kernel
# source: home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py
# specialization identity: 3ab9bd6fdfd1aee1
# compiler revision: 1a7d104811605803
# target model: a100-rvv1-vlen1024/1 (VLEN=1024, file=4096B)
# options: no-elementwise-width
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
    # [peephole] removed 0 redundant vsetvli, 173 redundant li
operator_entry:  # fn operator_entry
addi sp, sp, -208
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
ld t0, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t0, 0(t0)  # [op0] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t1, 0(t0)  # [op1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
sd t1, 128(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t0, 8(t0)  # [op2] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
sd t0, 136(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t0, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t0, 24(t0)  # [op3] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
sd t0, 144(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t0, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
lwu t2, 40(t0)  # [op4] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t0, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
lwu s1, 44(t0)  # [op5] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t0, 136(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t0, 8(t0)  # [op6] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
addiw t0, t0, 0  # [op7] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
sd t0, 152(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t0, 136(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t0, 24(t0)  # [op8] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
addiw s8, t0, 0  # [op9] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t1, 136(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t1, 40(t1)  # [op10] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
addiw a1, t1, 0  # [op11] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
sd a1, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld a1, 128(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld s2, 0(a1)  # [op12] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld a1, 128(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld s3, 56(a1)  # [op13] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld a1, 128(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld s4, 112(a1)  # [op14] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
li a1, 15  # [op15] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
add t0, t0, a1  # [op16] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
li a1, 16  # [op17] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
divu t0, t0, a1  # [op18] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
sd t0, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
li t0, 15  # [op19] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
add t0, t1, t0  # [op20] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
li t1, 16  # [op21] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
divu t0, t0, t1  # [op22] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
sd t0, 168(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
li t0, 1  # [op23] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t1, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mul t0, t0, t1  # [op24] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t1, 168(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mul s9, t0, t1  # [op25] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t2  # [op26] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv s10, s1  # [op27] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
li t1, 0  # [op28] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lprog_head  # [op29] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lprog_head:  # block prog_head
slt t2, t0, s9  # [op30] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
bne t2, zero, .Lbrc31_true  # [op31] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
sd t1, 96(sp)  # [op31] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t1, t0  # [op31] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t0, 96(sp)  # [op31] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lprog_exit  # [op31] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lbrc31_true:  # [op31] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t2, t0  # [op31] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv a1, t1  # [op31] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lprog_body  # [op31] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lprog_body:  # block prog_body
li t0, 1  # [op32] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t1, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
divu t1, t2, t1  # [op33] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld s1, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mul t1, t1, s1  # [op34] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
sub s1, t2, t1  # [op35] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t1, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mul t0, t0, t1  # [op36] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
divu t1, t2, t0  # [op37] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld a2, 168(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
divu a2, t1, a2  # [op38] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld a3, 168(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mul a2, a2, a3  # [op39] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
sub t1, t1, a2  # [op40] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld a2, 168(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mul t0, t0, a2  # [op41] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
addiw t0, s1, 0  # [op42] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
addiw a2, t1, 0  # [op43] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t1, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
addiw t1, t1, 0  # [op44] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t1, 168(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
addiw t1, t1, 0  # [op45] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t1, 8(t1)  # [op47] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
li s1, 4  # [op48] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:25:14
sllw a3, t0, s1  # [op49] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:25:14
li t0, 0  # [op50] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t1, a1  # [op51] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk1_head  # [op51] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk1_head:  # block chunk1_head
li a1, 16  # [op52] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
slt a1, t0, a1  # [op53] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
bne a1, zero, .Lbrc54_true  # [op54] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op54] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op54] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk1_exit  # [op54] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lbrc54_true:  # [op54] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk1_body  # [op54] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk1_exit:  # block chunk1_exit
li t1, 0  # [op55] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op56] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op56] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op56] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk2_head  # [op56] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk1_body:  # block chunk1_body
li a1, 16  # [op57] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
vsetvli a1, a1, e32, m1, ta,ma  # [op58] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
li a1, 16  # [op59] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:25:27
vid.v v1  # [op61] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:25:27
vadd.vx v1, v1, t0  # [op62] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:25:27
vmv.v.x v2, a3  # [op63] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:25:14
vadd.vv v2, v2, v1  # [op64] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:25:14
vid.v v3  # [op65] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:25:14
vadd.vx v3, v3, t0  # [op66] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:25:14
    # [peephole-li] [op67] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:25:14
vwadd.vx v4, v3, x0  # [op69] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:25:14
    # [peephole-li] [op70] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:25:14
vsetvli a1, a1, e64, m2, ta,ma  # [op71] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:25:14
li a1, 4  # [op72] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:25:14
vmul.vx v4, v4, a1  # [op73] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:25:14
li a1, 0  # [op74] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:25:14
ld a4, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:25:14
ld a4, 16(a4)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:25:14
add a1, a4, a1  # [op75] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:25:14
li a4, 16  # [op76] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:25:14
vsetvli a4, a4, e32, m1, ta,ma  # [op77] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:25:14
vsuxei64.v v2, (a1), v4  # [op78] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:25:14
li a1, 16  # [op79] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:25:14
sllw a1, a2, s1  # [op81] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:26:14
vmv.v.x v2, a1  # [op82] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:26:14
vadd.vv v1, v2, v1  # [op83] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:26:14
vid.v v2  # [op84] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:26:14
vadd.vx v2, v2, t0  # [op85] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:26:14
li a1, 16  # [op86] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:26:14
vwadd.vx v4, v2, x0  # [op88] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:26:14
    # [peephole-li] [op89] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:26:14
vsetvli a1, a1, e64, m2, ta,ma  # [op90] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:26:14
li a1, 4  # [op91] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:26:14
vmul.vx v2, v4, a1  # [op92] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:26:14
li a1, 64  # [op93] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:26:14
ld a4, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:26:14
ld a4, 16(a4)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:26:14
add a1, a4, a1  # [op94] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:26:14
li a4, 16  # [op95] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:26:14
vsetvli a4, a4, e32, m1, ta,ma  # [op96] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:26:14
vsuxei64.v v1, (a1), v2  # [op97] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:26:14
li a1, 16  # [op98] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:26:14
    # [peephole-li] [op100] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
add t1, t1, a1  # [op101] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op102] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
addw t0, t0, a1  # [op103] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op104] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk1_head  # [op106] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk2_head:  # block chunk2_head
li s1, 32  # [op107] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op108] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc109_true  # [op109] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op109] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op109] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk2_exit  # [op109] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lbrc109_true:  # [op109] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk2_body  # [op109] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk2_exit:  # block chunk2_exit
li t1, 0  # [op110] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op111] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op111] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op111] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk3_head  # [op111] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk2_body:  # block chunk2_body
li s1, 32  # [op112] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op113] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op114] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:27:14
vid.v v1  # [op116] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:27:14
vadd.vx v1, v1, t0  # [op117] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:27:14
vid.v v2  # [op118] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:27:14
vadd.vx v2, v2, t0  # [op119] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:27:14
    # [peephole-li] [op120] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:27:14
vwadd.vx v4, v2, x0  # [op122] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:27:14
    # [peephole-li] [op123] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:27:14
vsetvli s1, s1, e64, m2, ta,ma  # [op124] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:27:14
li s1, 4  # [op125] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:27:14
vmul.vx v2, v4, s1  # [op126] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:27:14
li s1, 128  # [op127] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:27:14
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:27:14
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:27:14
add s1, a1, s1  # [op128] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:27:14
li a1, 32  # [op129] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:27:14
vsetvli a1, a1, e32, m1, ta,ma  # [op130] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:27:14
vsuxei64.v v1, (s1), v2  # [op131] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:27:14
li s1, 32  # [op132] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:27:14
    # [peephole-li] [op134] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op135] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op136] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op137] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op138] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk2_head  # [op140] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk3_head:  # block chunk3_head
li s1, 256  # [op141] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op142] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc143_true  # [op143] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op143] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op143] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk3_exit  # [op143] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lbrc143_true:  # [op143] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk3_body  # [op143] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk3_exit:  # block chunk3_exit
li t1, 0  # [op144] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op145] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op145] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op145] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk4_head  # [op145] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk3_body:  # block chunk3_body
li s1, 32  # [op146] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op147] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
li s1, 0  # [op148] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:28:11
li a1, 32  # [op149] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:28:11
vmv.v.x v1, s1  # [op151] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:28:11
vid.v v2  # [op152] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:28:11
vadd.vx v2, v2, t0  # [op153] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:28:11
li s1, 32  # [op154] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:28:11
vwadd.vx v4, v2, x0  # [op156] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:28:11
    # [peephole-li] [op157] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:28:11
vsetvli s1, s1, e64, m2, ta,ma  # [op158] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:28:11
li s1, 4  # [op159] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:28:11
vmul.vx v2, v4, s1  # [op160] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:28:11
li s1, 256  # [op161] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:28:11
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:28:11
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:28:11
add s1, a1, s1  # [op162] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:28:11
li a1, 32  # [op163] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:28:11
vsetvli a1, a1, e32, m1, ta,ma  # [op164] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:28:11
vsuxei64.v v1, (s1), v2  # [op165] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:28:11
li s1, 32  # [op166] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:28:11
li s1, 0  # [op168] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
li s1, 32  # [op169] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
    # [peephole-li] [op170] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op171] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op172] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op173] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op174] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk3_head  # [op176] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk4_head:  # block chunk4_head
li s1, 16  # [op177] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op178] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc179_true  # [op179] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op179] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op179] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk4_exit  # [op179] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lbrc179_true:  # [op179] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk4_body  # [op179] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk4_exit:  # block chunk4_exit
li t1, 0  # [op180] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op181] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op181] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op181] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk5_head  # [op181] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk4_body:  # block chunk4_body
li s1, 16  # [op182] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op183] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
li s1, 16  # [op184] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
ld s1, 152(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
vmv.v.x v1, s1  # [op186] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
vid.v v2  # [op187] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
vadd.vx v2, v2, t0  # [op188] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
li s1, 16  # [op189] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
vwadd.vx v4, v2, x0  # [op191] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
    # [peephole-li] [op192] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
vsetvli s1, s1, e64, m2, ta,ma  # [op193] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
li s1, 4  # [op194] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
vmul.vx v2, v4, s1  # [op195] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
li s1, 1600  # [op196] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
add s1, a1, s1  # [op197] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
li a1, 16  # [op198] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
vsetvli a1, a1, e32, m1, ta,ma  # [op199] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
vsuxei64.v v1, (s1), v2  # [op200] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
li s1, 16  # [op201] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
vmv.v.x v1, s8  # [op203] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
vid.v v2  # [op204] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
vadd.vx v2, v2, t0  # [op205] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
    # [peephole-li] [op206] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
vwadd.vx v4, v2, x0  # [op208] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
    # [peephole-li] [op209] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
vsetvli s1, s1, e64, m2, ta,ma  # [op210] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
li s1, 4  # [op211] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
vmul.vx v2, v4, s1  # [op212] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
li s1, 6080  # [op213] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
add s1, a1, s1  # [op214] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
li a1, 16  # [op215] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
vsetvli a1, a1, e32, m1, ta,ma  # [op216] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
vsuxei64.v v1, (s1), v2  # [op217] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
li s1, 16  # [op218] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
    # [peephole-li] [op220] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op221] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op222] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op223] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op224] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk4_head  # [op226] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk5_head:  # block chunk5_head
li s1, 32  # [op227] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op228] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc229_true  # [op229] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op229] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op229] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk5_exit  # [op229] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lbrc229_true:  # [op229] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk5_body  # [op229] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk5_exit:  # block chunk5_exit
li t1, 0  # [op230] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op231] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op231] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op231] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk6_head  # [op231] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk5_body:  # block chunk5_body
li s1, 32  # [op232] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op233] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op234] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
ld s1, 152(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
vmv.v.x v1, s1  # [op236] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
vid.v v2  # [op237] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
vadd.vx v2, v2, t0  # [op238] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
li s1, 32  # [op239] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
vwadd.vx v4, v2, x0  # [op241] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
    # [peephole-li] [op242] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
vsetvli s1, s1, e64, m2, ta,ma  # [op243] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
li s1, 4  # [op244] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
vmul.vx v2, v4, s1  # [op245] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
li s1, 6208  # [op246] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
add s1, a1, s1  # [op247] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
li a1, 32  # [op248] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
vsetvli a1, a1, e32, m1, ta,ma  # [op249] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
vsuxei64.v v1, (s1), v2  # [op250] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
li s1, 32  # [op251] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
li s1, 0  # [op253] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
ld s1, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
vmv.v.x v1, s1  # [op254] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
vid.v v2  # [op255] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
vadd.vx v2, v2, t0  # [op256] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
li s1, 32  # [op257] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
vwadd.vx v4, v2, x0  # [op259] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
    # [peephole-li] [op260] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
vsetvli s1, s1, e64, m2, ta,ma  # [op261] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
li s1, 4  # [op262] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
vmul.vx v2, v4, s1  # [op263] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
li s1, 15808  # [op264] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
add s1, a1, s1  # [op265] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
li a1, 32  # [op266] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
vsetvli a1, a1, e32, m1, ta,ma  # [op267] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
vsuxei64.v v1, (s1), v2  # [op268] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
li s1, 32  # [op269] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
    # [peephole-li] [op271] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op272] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op273] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op274] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op275] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk5_head  # [op277] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk6_head:  # block chunk6_head
li s1, 16  # [op278] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op279] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc280_true  # [op280] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op280] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op280] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk6_exit  # [op280] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lbrc280_true:  # [op280] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk6_body  # [op280] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk6_exit:  # block chunk6_exit
li t1, 0  # [op281] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op282] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op282] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op282] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk7_head  # [op282] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk6_body:  # block chunk6_body
li s1, 16  # [op283] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op284] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
li s1, 16  # [op285] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op286] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op287] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op288] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op289] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk6_head  # [op291] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk7_head:  # block chunk7_head
li s1, 32  # [op292] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op293] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc294_true  # [op294] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op294] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op294] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk7_exit  # [op294] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lbrc294_true:  # [op294] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk7_body  # [op294] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk7_exit:  # block chunk7_exit
li t1, 0  # [op295] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op296] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op296] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op296] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk8_head  # [op296] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk7_body:  # block chunk7_body
li s1, 32  # [op297] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op298] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op299] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
ld s1, 152(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
vmv.v.x v1, s1  # [op301] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
vid.v v2  # [op302] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
vadd.vx v2, v2, t0  # [op303] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
li s1, 32  # [op304] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
vwadd.vx v4, v2, x0  # [op306] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
    # [peephole-li] [op307] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
vsetvli s1, s1, e64, m2, ta,ma  # [op308] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
li s1, 4  # [op309] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
vmul.vx v2, v4, s1  # [op310] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
li s1, 20480  # [op311] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
add s1, a1, s1  # [op312] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
li a1, 32  # [op313] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
vsetvli a1, a1, e32, m1, ta,ma  # [op314] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
vsuxei64.v v1, (s1), v2  # [op315] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
li s1, 32  # [op316] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
    # [peephole-li] [op318] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op319] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op320] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op321] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op322] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk7_head  # [op324] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk8_head:  # block chunk8_head
li s1, 16  # [op325] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op326] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc327_true  # [op327] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op327] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op327] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk8_exit  # [op327] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lbrc327_true:  # [op327] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk8_body  # [op327] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk8_exit:  # block chunk8_exit
li t1, 0  # [op328] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op329] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op329] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op329] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk9_head  # [op329] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk8_body:  # block chunk8_body
li s1, 16  # [op330] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op331] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
li s1, 16  # [op332] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
ld s1, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
vmv.v.x v1, s1  # [op334] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
vid.v v2  # [op335] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
vadd.vx v2, v2, t0  # [op336] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
li s1, 16  # [op337] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
vwadd.vx v4, v2, x0  # [op339] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
    # [peephole-li] [op340] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
vsetvli s1, s1, e64, m2, ta,ma  # [op341] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
li s1, 4  # [op342] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
vmul.vx v2, v4, s1  # [op343] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
li s1, 20736  # [op344] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
add s1, a1, s1  # [op345] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
li a1, 16  # [op346] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
vsetvli a1, a1, e32, m1, ta,ma  # [op347] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
vsuxei64.v v1, (s1), v2  # [op348] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
li s1, 16  # [op349] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
vid.v v1  # [op351] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
vadd.vx v1, v1, t0  # [op352] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
    # [peephole-li] [op353] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
vwadd.vx v2, v1, x0  # [op355] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
    # [peephole-li] [op356] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
vsetvli s1, s1, e64, m2, ta,ma  # [op357] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
li s1, 4  # [op358] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
vmul.vx v2, v2, s1  # [op359] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
li s1, 0  # [op360] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
add s1, a1, s1  # [op361] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
li a1, 16  # [op362] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
vsetvli a1, a1, e32, m1, ta,ma  # [op363] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
vluxei64.v v1, (s1), v2  # [op364] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
li s1, 16  # [op365] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
vid.v v2  # [op367] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
vadd.vx v2, v2, t0  # [op368] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
    # [peephole-li] [op369] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
vwadd.vx v4, v2, x0  # [op371] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
    # [peephole-li] [op372] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
vsetvli s1, s1, e64, m2, ta,ma  # [op373] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
li s1, 4  # [op374] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
vmul.vx v2, v4, s1  # [op375] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
li s1, 1600  # [op376] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
add s1, a1, s1  # [op377] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
li a1, 16  # [op378] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
vsetvli a1, a1, e32, m1, ta,ma  # [op379] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
vluxei64.v v4, (s1), v2  # [op380] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
li s1, 16  # [op381] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
vmul.vv v2, v1, v4  # [op383] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
vid.v v3  # [op384] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
vadd.vx v3, v3, t0  # [op385] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
    # [peephole-li] [op386] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
vwadd.vx v4, v3, x0  # [op388] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
    # [peephole-li] [op389] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
vsetvli s1, s1, e64, m2, ta,ma  # [op390] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
li s1, 4  # [op391] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
vmul.vx v4, v4, s1  # [op392] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
li s1, 1664  # [op393] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
add s1, a1, s1  # [op394] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
li a1, 16  # [op395] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
vsetvli a1, a1, e32, m1, ta,ma  # [op396] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
vsuxei64.v v2, (s1), v4  # [op397] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
li s1, 16  # [op398] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:29
vid.v v2  # [op400] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
vadd.vx v2, v2, t0  # [op401] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
    # [peephole-li] [op402] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
vwadd.vx v4, v2, x0  # [op404] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
    # [peephole-li] [op405] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
vsetvli s1, s1, e64, m2, ta,ma  # [op406] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
li s1, 4  # [op407] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
vmul.vx v2, v4, s1  # [op408] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
li s1, 6080  # [op409] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
add s1, a1, s1  # [op410] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
li a1, 16  # [op411] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
vsetvli a1, a1, e32, m1, ta,ma  # [op412] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
vluxei64.v v4, (s1), v2  # [op413] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
li s1, 16  # [op414] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
vmslt.vv v1, v1, v4  # [op416] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
vid.v v2  # [op417] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
vadd.vx v2, v2, t0  # [op418] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
    # [peephole-li] [op419] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
vwadd.vx v4, v2, x0  # [op421] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
    # [peephole-li] [op422] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
vsetvli s1, s1, e64, m2, ta,ma  # [op423] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
li s1, 4  # [op424] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
vmul.vx v2, v4, s1  # [op425] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
li s1, 6144  # [op426] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
add s1, a1, s1  # [op427] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
li a1, 16  # [op428] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
vsetvli a1, a1, e32, m1, ta,ma  # [op429] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
li a1, 1  # [op430] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
vmv.v.x v4, a1  # [op431] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
li a1, 0  # [op432] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
vmv.v.x v5, a1  # [op433] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
vmv1r.v v0, v1  # [op434] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
vmerge.vvm v1, v5, v4, v0  # [op435] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
vsuxei64.v v1, (s1), v2  # [op436] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:27
li s1, 16  # [op437] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op438] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op439] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op440] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op441] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk8_head  # [op443] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk9_head:  # block chunk9_head
li s1, 512  # [op444] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op445] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc446_true  # [op446] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op446] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op446] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk9_exit  # [op446] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lbrc446_true:  # [op446] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk9_body  # [op446] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk9_exit:  # block chunk9_exit
li t1, 0  # [op447] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op448] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op448] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op448] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk10_head  # [op448] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk9_body:  # block chunk9_body
li s1, 32  # [op449] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op450] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
li s1, 0  # [op451] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a1, 32  # [op452] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a1, a1, e16, m1, ta,ma  # [op453] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.v.x v1, s1  # [op454] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li s1, 32  # [op455] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli s1, s1, e32, m1, ta,ma  # [op456] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vid.v v2  # [op457] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vadd.vx v2, v2, t0  # [op458] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li s1, 32  # [op459] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vwadd.vx v4, v2, x0  # [op461] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op462] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli s1, s1, e64, m2, ta,ma  # [op463] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li s1, 4  # [op464] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmul.vx v2, v4, s1  # [op465] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li s1, 12608  # [op466] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add s1, a1, s1  # [op467] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a1, 32  # [op468] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a1, a1, e16, m1, ta,ma  # [op469] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vfwcvt.f.f.v v4, v1  # [op470] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a1, 32  # [op471] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a1, a1, e32, m1, ta,ma  # [op472] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.v.v v1, v4  # [op473] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a1, 32  # [op474] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsuxei64.v v1, (s1), v2  # [op476] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li s1, 32  # [op477] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op479] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op480] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op481] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op482] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op483] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk9_head  # [op485] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk10_head:  # block chunk10_head
li s1, 16  # [op486] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op487] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc488_true  # [op488] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op488] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op488] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk10_exit  # [op488] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lbrc488_true:  # [op488] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk10_body  # [op488] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk10_exit:  # block chunk10_exit
li t1, 0  # [op489] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op490] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op490] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op490] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk11_head  # [op490] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk10_body:  # block chunk10_body
li s1, 16  # [op491] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op492] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
li s1, 16  # [op493] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
vid.v v1  # [op495] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
vadd.vx v1, v1, t0  # [op496] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
    # [peephole-li] [op497] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
vwadd.vx v2, v1, x0  # [op499] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
    # [peephole-li] [op500] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
vsetvli s1, s1, e64, m2, ta,ma  # [op501] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
li s1, 4  # [op502] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
vmul.vx v2, v2, s1  # [op503] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
li s1, 64  # [op504] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
add s1, a1, s1  # [op505] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
li a1, 16  # [op506] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
vsetvli a1, a1, e32, m1, ta,ma  # [op507] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
vluxei64.v v1, (s1), v2  # [op508] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
li s1, 16  # [op509] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
vid.v v2  # [op511] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
vadd.vx v2, v2, t0  # [op512] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
    # [peephole-li] [op513] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
vwadd.vx v4, v2, x0  # [op515] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
    # [peephole-li] [op516] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
vsetvli s1, s1, e64, m2, ta,ma  # [op517] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
li s1, 4  # [op518] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
vmul.vx v2, v4, s1  # [op519] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
li s1, 20736  # [op520] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
add s1, a1, s1  # [op521] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
li a1, 16  # [op522] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
vsetvli a1, a1, e32, m1, ta,ma  # [op523] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
vluxei64.v v4, (s1), v2  # [op524] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
li s1, 16  # [op525] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
vmslt.vv v1, v1, v4  # [op527] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
vid.v v2  # [op528] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
vadd.vx v2, v2, t0  # [op529] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
    # [peephole-li] [op530] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
vwadd.vx v4, v2, x0  # [op532] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
    # [peephole-li] [op533] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
vsetvli s1, s1, e64, m2, ta,ma  # [op534] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
li s1, 4  # [op535] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
vmul.vx v2, v4, s1  # [op536] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
li s1, 20800  # [op537] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
add s1, a1, s1  # [op538] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
li a1, 16  # [op539] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
vsetvli a1, a1, e32, m1, ta,ma  # [op540] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
li a1, 1  # [op541] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
vmv.v.x v4, a1  # [op542] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
li a1, 0  # [op543] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
vmv.v.x v5, a1  # [op544] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
vmv1r.v v0, v1  # [op545] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
vmerge.vvm v1, v5, v4, v0  # [op546] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
vsuxei64.v v1, (s1), v2  # [op547] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:47
li s1, 16  # [op548] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op549] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op550] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op551] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op552] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk10_head  # [op554] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk11_head:  # block chunk11_head
li s1, 512  # [op555] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op556] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc557_true  # [op557] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op557] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op557] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk11_exit  # [op557] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lbrc557_true:  # [op557] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk11_body  # [op557] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk11_exit:  # block chunk11_exit
li t1, 0  # [op558] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op559] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op559] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op559] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk12_head  # [op559] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk11_body:  # block chunk11_body
li s1, 32  # [op560] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op561] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
li s1, 0  # [op562] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a1, 32  # [op563] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a1, a1, e16, m1, ta,ma  # [op564] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.v.x v1, s1  # [op565] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li s1, 32  # [op566] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli s1, s1, e32, m1, ta,ma  # [op567] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vid.v v2  # [op568] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vadd.vx v2, v2, t0  # [op569] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li s1, 32  # [op570] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vwadd.vx v4, v2, x0  # [op572] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
    # [peephole-li] [op573] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli s1, s1, e64, m2, ta,ma  # [op574] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li s1, 4  # [op575] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmul.vx v2, v4, s1  # [op576] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li s1, 27008  # [op577] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add s1, a1, s1  # [op578] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a1, 32  # [op579] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a1, a1, e16, m1, ta,ma  # [op580] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vfwcvt.f.f.v v4, v1  # [op581] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a1, 32  # [op582] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a1, a1, e32, m1, ta,ma  # [op583] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.v.v v1, v4  # [op584] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a1, 32  # [op585] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsuxei64.v v1, (s1), v2  # [op587] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li s1, 32  # [op588] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
    # [peephole-li] [op590] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op591] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op592] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op593] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op594] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk11_head  # [op596] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk12_head:  # block chunk12_head
li s1, 16  # [op597] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op598] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc599_true  # [op599] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t2  # [op599] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv s5, t1  # [op599] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk12_exit  # [op599] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lbrc599_true:  # [op599] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk12_body  # [op599] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk12_exit:  # block chunk12_exit
li t0, 0  # [op600] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
j .Lstg13_head  # [op601] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
.Lchunk12_body:  # block chunk12_body
li s1, 16  # [op602] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op603] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
li s1, 16  # [op604] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op605] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op606] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op607] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op608] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk12_head  # [op610] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lstg13_head:  # block stg13_head
li t1, 512  # [op611] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
slt t1, t0, t1  # [op612] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
bne t1, zero, .Lbrc613_true  # [op613] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
j .Lstg13_exit  # [op613] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
.Lbrc613_true:  # [op613] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
j .Lstg13_body  # [op613] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
.Lstg13_body:  # block stg13_body
li t1, 32  # [op614] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vsetvli t1, t1, e32, m1, ta,ma  # [op615] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vid.v v1  # [op616] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vadd.vx v1, v1, t0  # [op617] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t1, 32  # [op618] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vmv.v.x v2, t1  # [op619] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vdiv.vv v2, v1, v2  # [op620] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t1, 16  # [op621] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vmv.v.x v3, t1  # [op622] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vrem.vv v2, v2, v3  # [op623] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t1, 32  # [op624] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vmv.v.x v3, t1  # [op625] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vrem.vv v3, v1, v3  # [op626] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op627] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vwadd.vx v4, v2, x0  # [op629] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op630] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vsetvli t1, t1, e64, m2, ta,ma  # [op631] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t1, 4  # [op632] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vmul.vx v2, v4, t1  # [op633] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t1, 6144  # [op634] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
add t1, s1, t1  # [op635] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li s1, 32  # [op636] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vsetvli s1, s1, e32, m1, ta,ma  # [op637] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vluxei64.v v4, (t1), v2  # [op638] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t1, 32  # [op639] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vwadd.vx v2, v1, x0  # [op641] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op642] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vsetvli t1, t1, e64, m2, ta,ma  # [op643] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t1, 4  # [op644] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vmul.vx v2, v2, t1  # [op645] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t1, 6464  # [op646] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
add t1, s1, t1  # [op647] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li s1, 32  # [op648] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vsetvli s1, s1, e32, m1, ta,ma  # [op649] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vsuxei64.v v4, (t1), v2  # [op650] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t1, 32  # [op651] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
addw t0, t0, t1  # [op652] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
j .Lstg13_head  # [op653] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
.Lstg13_exit:  # block stg13_exit
li t0, 0  # [op654] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
j .Lstg14_head  # [op655] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
.Lstg14_head:  # block stg14_head
li t1, 512  # [op656] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
slt t1, t0, t1  # [op657] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
bne t1, zero, .Lbrc658_true  # [op658] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
j .Lstg14_exit  # [op658] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
.Lbrc658_true:  # [op658] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
j .Lstg14_body  # [op658] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
.Lstg14_body:  # block stg14_body
li t1, 32  # [op659] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vsetvli t1, t1, e32, m1, ta,ma  # [op660] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vid.v v1  # [op661] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vadd.vx v1, v1, t0  # [op662] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t1, 16  # [op663] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vmv.v.x v2, t1  # [op664] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vdiv.vv v2, v1, v2  # [op665] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t1, 32  # [op666] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vmv.v.x v3, t1  # [op667] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vrem.vv v2, v2, v3  # [op668] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t1, 16  # [op669] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vmv.v.x v2, t1  # [op670] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vrem.vv v2, v1, v2  # [op671] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t1, 32  # [op672] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vwadd.vx v4, v2, x0  # [op674] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
    # [peephole-li] [op675] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vsetvli t1, t1, e64, m2, ta,ma  # [op676] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t1, 4  # [op677] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vmul.vx v2, v4, t1  # [op678] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t1, 20800  # [op679] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
add t1, s1, t1  # [op680] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li s1, 32  # [op681] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vsetvli s1, s1, e32, m1, ta,ma  # [op682] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vluxei64.v v4, (t1), v2  # [op683] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t1, 32  # [op684] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vwadd.vx v2, v1, x0  # [op686] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
    # [peephole-li] [op687] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vsetvli t1, t1, e64, m2, ta,ma  # [op688] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t1, 4  # [op689] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vmul.vx v2, v2, t1  # [op690] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t1, 22912  # [op691] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
add t1, s1, t1  # [op692] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li s1, 32  # [op693] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vsetvli s1, s1, e32, m1, ta,ma  # [op694] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vsuxei64.v v4, (t1), v2  # [op695] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t1, 32  # [op696] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
addw t0, t0, t1  # [op697] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
j .Lstg14_head  # [op698] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
.Lstg14_exit:  # block stg14_exit
li t0, 0  # [op699] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
li s11, 32  # [op700] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
mv a7, t0  # [op701] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
j .Lmloop15.head  # [op701] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
.Lmloop15.head:  # block mloop15.head
ld t0, 152(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
slt t0, a7, t0  # [op702] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
bne t0, zero, .Lbrc703_true  # [op703] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
mv t0, a7  # [op703] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
j .Lmloop15.exit  # [op703] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
.Lbrc703_true:  # [op703] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
j .Lmloop15.body  # [op703] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
.Lmloop15.body:  # block mloop15.body
li t0, 0  # [op704] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t1, s5  # [op705] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk16_head  # [op705] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lmloop15.exit:  # block mloop15.exit
li t0, 0  # [op706] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t1, s5  # [op707] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk32_head  # [op707] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk16_head:  # block chunk16_head
li s1, 32  # [op708] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op709] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc710_true  # [op710] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op710] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op710] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk16_exit  # [op710] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lbrc710_true:  # [op710] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk16_body  # [op710] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk16_exit:  # block chunk16_exit
li t1, 0  # [op711] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op712] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op712] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op712] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk17_head  # [op712] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk16_body:  # block chunk16_body
li s1, 32  # [op713] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op714] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op715] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
vmv.v.x v1, a7  # [op717] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
vid.v v2  # [op718] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
vadd.vx v2, v2, t0  # [op719] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
    # [peephole-li] [op720] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
vwadd.vx v4, v2, x0  # [op722] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
    # [peephole-li] [op723] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
vsetvli s1, s1, e64, m2, ta,ma  # [op724] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
li s1, 4  # [op725] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
vmul.vx v2, v4, s1  # [op726] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
li s1, 1280  # [op727] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
add s1, a1, s1  # [op728] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
li a1, 32  # [op729] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
vsetvli a1, a1, e32, m1, ta,ma  # [op730] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
vsuxei64.v v1, (s1), v2  # [op731] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
li s1, 32  # [op732] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
vid.v v2  # [op734] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
vadd.vx v2, v2, t0  # [op735] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
    # [peephole-li] [op736] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
vwadd.vx v4, v2, x0  # [op738] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
    # [peephole-li] [op739] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
vsetvli s1, s1, e64, m2, ta,ma  # [op740] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
li s1, 4  # [op741] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
vmul.vx v2, v4, s1  # [op742] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
li s1, 128  # [op743] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
add s1, a1, s1  # [op744] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
li a1, 32  # [op745] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
vsetvli a1, a1, e32, m1, ta,ma  # [op746] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
vluxei64.v v4, (s1), v2  # [op747] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
li s1, 32  # [op748] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
vadd.vv v1, v1, v4  # [op750] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
vid.v v2  # [op751] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
vadd.vx v2, v2, t0  # [op752] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
    # [peephole-li] [op753] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
vwadd.vx v4, v2, x0  # [op755] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
    # [peephole-li] [op756] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
vsetvli s1, s1, e64, m2, ta,ma  # [op757] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
li s1, 4  # [op758] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
vmul.vx v2, v4, s1  # [op759] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
li s1, 1408  # [op760] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
add s1, a1, s1  # [op761] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
li a1, 32  # [op762] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
vsetvli a1, a1, e32, m1, ta,ma  # [op763] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
vsuxei64.v v1, (s1), v2  # [op764] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
li s1, 32  # [op765] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:30:14
    # [peephole-li] [op767] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op768] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op769] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op770] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op771] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk16_head  # [op773] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk17_head:  # block chunk17_head
li s1, 512  # [op774] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op775] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc776_true  # [op776] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op776] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op776] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk17_exit  # [op776] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lbrc776_true:  # [op776] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk17_body  # [op776] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk17_exit:  # block chunk17_exit
li t1, 0  # [op777] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op778] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op778] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op778] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk18_head  # [op778] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk17_body:  # block chunk17_body
li s1, 32  # [op779] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op780] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op781] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:21
vid.v v1  # [op783] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:21
vadd.vx v1, v1, t0  # [op784] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:21
    # [peephole-li] [op785] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:21
vmv.v.x v2, s1  # [op786] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:21
vdiv.vv v1, v1, v2  # [op787] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:21
    # [peephole-li] [op788] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:21
vwadd.vx v2, v1, x0  # [op790] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:21
    # [peephole-li] [op791] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:21
vsetvli s1, s1, e64, m2, ta,ma  # [op792] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:21
li s1, 8  # [op793] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:21
vmul.vx v2, v2, s1  # [op794] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:21
li s1, 1728  # [op795] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:21
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:21
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:21
add s1, a1, s1  # [op796] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:21
li a1, 32  # [op797] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:21
vluxei64.v v4, (s1), v2  # [op799] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:21
li s1, 32  # [op800] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:21
vsetvli s1, s1, e32, m1, ta,ma  # [op801] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:21
li s1, 32  # [op802] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op803] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op804] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op805] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op806] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk17_head  # [op808] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk18_head:  # block chunk18_head
li s1, 32  # [op809] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op810] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc811_true  # [op811] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t2  # [op811] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk18_exit  # [op811] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lbrc811_true:  # [op811] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk18_body  # [op811] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk18_exit:  # block chunk18_exit
li t0, 0  # [op812] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
j .Lstg19_head  # [op813] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
.Lchunk18_body:  # block chunk18_body
li s1, 32  # [op814] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op815] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op816] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
vid.v v1  # [op818] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
vadd.vx v1, v1, t0  # [op819] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
    # [peephole-li] [op820] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
vwadd.vx v2, v1, x0  # [op822] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
    # [peephole-li] [op823] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
vsetvli s1, s1, e64, m2, ta,ma  # [op824] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
li s1, 4  # [op825] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
vmul.vx v2, v2, s1  # [op826] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
li s1, 1408  # [op827] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
add s1, a1, s1  # [op828] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
li a1, 32  # [op829] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
vsetvli a1, a1, e32, m1, ta,ma  # [op830] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
vluxei64.v v1, (s1), v2  # [op831] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
li s1, 32  # [op832] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
vid.v v2  # [op834] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
vadd.vx v2, v2, t0  # [op835] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
    # [peephole-li] [op836] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
vwadd.vx v4, v2, x0  # [op838] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
    # [peephole-li] [op839] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
vsetvli s1, s1, e64, m2, ta,ma  # [op840] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
li s1, 4  # [op841] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
vmul.vx v2, v4, s1  # [op842] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
li s1, 6208  # [op843] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
add s1, a1, s1  # [op844] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
li a1, 32  # [op845] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
vsetvli a1, a1, e32, m1, ta,ma  # [op846] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
vluxei64.v v4, (s1), v2  # [op847] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
li s1, 32  # [op848] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
vmslt.vv v1, v1, v4  # [op850] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
vid.v v2  # [op851] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
vadd.vx v2, v2, t0  # [op852] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
    # [peephole-li] [op853] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
vwadd.vx v4, v2, x0  # [op855] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
    # [peephole-li] [op856] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
vsetvli s1, s1, e64, m2, ta,ma  # [op857] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
li s1, 4  # [op858] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
vmul.vx v2, v4, s1  # [op859] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
li s1, 6336  # [op860] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
add s1, a1, s1  # [op861] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
li a1, 32  # [op862] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
vsetvli a1, a1, e32, m1, ta,ma  # [op863] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
li a1, 1  # [op864] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
vmv.v.x v4, a1  # [op865] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
li a1, 0  # [op866] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
vmv.v.x v5, a1  # [op867] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
vmv1r.v v0, v1  # [op868] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
vmerge.vvm v1, v5, v4, v0  # [op869] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
vsuxei64.v v1, (s1), v2  # [op870] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:51
li s1, 32  # [op871] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op872] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op873] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op874] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op875] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk18_head  # [op877] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lstg19_head:  # block stg19_head
li s1, 512  # [op878] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
slt s1, t0, s1  # [op879] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
bne s1, zero, .Lbrc880_true  # [op880] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
j .Lstg19_exit  # [op880] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
.Lbrc880_true:  # [op880] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
j .Lstg19_body  # [op880] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
.Lstg19_body:  # block stg19_body
li s1, 32  # [op881] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vsetvli s1, s1, e32, m1, ta,ma  # [op882] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vid.v v1  # [op883] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vadd.vx v1, v1, t0  # [op884] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li s1, 32  # [op885] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vmv.v.x v2, s1  # [op886] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vdiv.vv v2, v1, v2  # [op887] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li s1, 16  # [op888] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vmv.v.x v3, s1  # [op889] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vrem.vv v2, v2, v3  # [op890] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li s1, 32  # [op891] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vmv.v.x v2, s1  # [op892] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vrem.vv v2, v1, v2  # [op893] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op894] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vwadd.vx v4, v2, x0  # [op896] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op897] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vsetvli s1, s1, e64, m2, ta,ma  # [op898] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li s1, 4  # [op899] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vmul.vx v2, v4, s1  # [op900] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li s1, 6336  # [op901] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
add s1, a1, s1  # [op902] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li a1, 32  # [op903] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vsetvli a1, a1, e32, m1, ta,ma  # [op904] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vluxei64.v v4, (s1), v2  # [op905] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li s1, 32  # [op906] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vwadd.vx v2, v1, x0  # [op908] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op909] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vsetvli s1, s1, e64, m2, ta,ma  # [op910] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li s1, 4  # [op911] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vmul.vx v2, v2, s1  # [op912] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li s1, 8512  # [op913] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
add s1, a1, s1  # [op914] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li a1, 32  # [op915] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vsetvli a1, a1, e32, m1, ta,ma  # [op916] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vsuxei64.v v4, (s1), v2  # [op917] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li s1, 32  # [op918] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
addw t0, t0, s1  # [op919] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
j .Lstg19_head  # [op920] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
.Lstg19_exit:  # block stg19_exit
li t0, 0  # [op921] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv s1, t0  # [op922] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv a1, t1  # [op922] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk20_head  # [op922] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk20_head:  # block chunk20_head
li t0, 512  # [op923] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
slt t0, s1, t0  # [op924] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
bne t0, zero, .Lbrc925_true  # [op925] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op925] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, a1  # [op925] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk20_exit  # [op925] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lbrc925_true:  # [op925] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk20_body  # [op925] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk20_exit:  # block chunk20_exit
li t1, 0  # [op926] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op927] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op927] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op927] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk21_head  # [op927] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk20_body:  # block chunk20_body
li t0, 32  # [op928] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
vsetvli t0, t0, e16, m1, ta,ma  # [op929] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
li t0, 32  # [op930] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vsetvli t0, t0, e32, m1, ta,ma  # [op931] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vid.v v1  # [op932] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vadd.vx v1, v1, s1  # [op933] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t0, 32  # [op934] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vwadd.vx v2, v1, x0  # [op936] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op937] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vsetvli t0, t0, e64, m2, ta,ma  # [op938] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t0, 4  # [op939] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vmul.vx v2, v2, t0  # [op940] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t0, 6464  # [op941] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
add t0, t1, t0  # [op942] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t1, 32  # [op943] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vsetvli t1, t1, e32, m1, ta,ma  # [op944] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vluxei64.v v1, (t0), v2  # [op945] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t0, 0  # [op946] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vmv.v.x v2, t0  # [op947] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vmsne.vv v1, v1, v2  # [op948] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t0, 32  # [op949] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vsetvli t0, t0, e16, m1, ta,ma  # [op950] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t0, 32  # [op951] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vsetvli t0, t0, e32, m1, ta,ma  # [op952] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vid.v v2  # [op953] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vadd.vx v2, v2, s1  # [op954] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t0, 32  # [op955] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vwadd.vx v4, v2, x0  # [op957] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op958] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vsetvli t0, t0, e64, m2, ta,ma  # [op959] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t0, 4  # [op960] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vmul.vx v2, v4, t0  # [op961] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t0, 8512  # [op962] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
add t0, t1, t0  # [op963] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t1, 32  # [op964] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vsetvli t1, t1, e32, m1, ta,ma  # [op965] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vluxei64.v v4, (t0), v2  # [op966] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t0, 0  # [op967] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vmv.v.x v2, t0  # [op968] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vmsne.vv v2, v4, v2  # [op969] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t0, 32  # [op970] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vsetvli t0, t0, e16, m1, ta,ma  # [op971] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vmand.mm v1, v1, v2  # [op972] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t0, 32  # [op973] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vsetvli t0, t0, e32, m1, ta,ma  # [op974] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vid.v v2  # [op975] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vadd.vx v2, v2, s1  # [op976] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t0, 32  # [op977] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vwadd.vx v4, v2, x0  # [op979] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op980] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vsetvli t0, t0, e64, m2, ta,ma  # [op981] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t0, 4  # [op982] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vmul.vx v2, v4, t0  # [op983] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t0, 10560  # [op984] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
add t0, t1, t0  # [op985] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t1, 32  # [op986] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vsetvli t1, t1, e32, m1, ta,ma  # [op987] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t1, 1  # [op988] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vmv.v.x v4, t1  # [op989] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t1, 0  # [op990] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vmv.v.x v5, t1  # [op991] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vmv1r.v v0, v1  # [op992] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vmerge.vvm v4, v5, v4, v0  # [op993] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vsuxei64.v v4, (t0), v2  # [op994] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t0, 32  # [op995] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vsetvli t0, t0, e16, m1, ta,ma  # [op996] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t0, 32  # [op997] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vsetvli t0, t0, e32, m1, ta,ma  # [op998] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vid.v v2  # [op999] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vadd.vx v2, v2, s1  # [op1000] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t0, 32  # [op1001] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vwadd.vx v4, v2, x0  # [op1003] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
    # [peephole-li] [op1004] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vsetvli t0, t0, e64, m2, ta,ma  # [op1005] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t0, 4  # [op1006] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vmul.vx v2, v4, t0  # [op1007] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t0, 10560  # [op1008] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
add t0, t1, t0  # [op1009] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t1, 32  # [op1010] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vsetvli t1, t1, e32, m1, ta,ma  # [op1011] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t1, 1  # [op1012] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vmv.v.x v4, t1  # [op1013] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t1, 0  # [op1014] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vmv.v.x v5, t1  # [op1015] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vmv1r.v v0, v1  # [op1016] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vmerge.vvm v4, v5, v4, v0  # [op1017] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vsuxei64.v v4, (t0), v2  # [op1018] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t0, 32  # [op1019] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
vsetvli t0, t0, e16, m1, ta,ma  # [op1020] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:32:26
li t0, 32  # [op1021] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e32, m1, ta,ma  # [op1022] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vid.v v2  # [op1023] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vadd.vx v2, v2, s1  # [op1024] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1025] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.v.x v3, t0  # [op1026] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vdiv.vv v2, v2, v3  # [op1027] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op1028] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vwadd.vx v4, v2, x0  # [op1030] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op1031] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e64, m2, ta,ma  # [op1032] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t0, 4  # [op1033] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmul.vx v2, v4, t0  # [op1034] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t0, 1664  # [op1035] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add t0, t1, t0  # [op1036] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t1, 32  # [op1037] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli t1, t1, e32, m1, ta,ma  # [op1038] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vluxei64.v v4, (t0), v2  # [op1039] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1040] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e16, m1, ta,ma  # [op1041] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1042] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e32, m1, ta,ma  # [op1043] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vid.v v2  # [op1044] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vadd.vx v2, v2, s1  # [op1045] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1046] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.v.x v3, t0  # [op1047] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vrem.vv v2, v2, v3  # [op1048] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op1049] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vwadd.vx v6, v2, x0  # [op1051] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op1052] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e64, m2, ta,ma  # [op1053] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t0, 4  # [op1054] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmul.vx v2, v6, t0  # [op1055] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t0, 1408  # [op1056] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add t0, t1, t0  # [op1057] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t1, 32  # [op1058] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli t1, t1, e32, m1, ta,ma  # [op1059] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vluxei64.v v5, (t0), v2  # [op1060] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1061] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e16, m1, ta,ma  # [op1062] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1063] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e32, m1, ta,ma  # [op1064] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vadd.vv v6, v4, v5  # [op1065] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1066] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e16, m1, ta,ma  # [op1067] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1068] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e32, m1, ta,ma  # [op1069] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vid.v v2  # [op1070] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vadd.vx v2, v2, s1  # [op1071] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1072] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vwadd.vx v4, v2, x0  # [op1074] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op1075] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e64, m2, ta,ma  # [op1076] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t0, 4  # [op1077] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmul.vx v2, v4, t0  # [op1078] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t0, 12608  # [op1079] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add t0, t1, t0  # [op1080] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t1, 32  # [op1081] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli t1, t1, e32, m1, ta,ma  # [op1082] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vluxei64.v v4, (t0), v2  # [op1083] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1084] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.v.v v8, v4  # [op1086] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op1087] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e16, m1, ta,ma  # [op1088] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vfncvt.f.f.w v2, v8  # [op1089] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1090] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e32, m1, ta,ma  # [op1091] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t0, 0  # [op1092] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.v.x v3, t0  # [op1093] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t0, 1  # [op1094] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.v.x v4, t0  # [op1095] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv1r.v v0, v1  # [op1096] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmerge.vvm v3, v3, v4, v0  # [op1097] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1098] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vwadd.vx v4, v6, x0  # [op1100] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
    # [peephole-li] [op1101] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e64, m2, ta,ma  # [op1102] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t0, 2  # [op1103] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmul.vx v4, v4, t0  # [op1104] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1105] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e16, m1, ta,ma  # [op1106] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t1, 0  # [op1107] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t0, 16  # [op1108] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e64, m2, ta,ma  # [op1109] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s t0, v4  # [op1110] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vid.v v8  # [op1111] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 2  # [op1112] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmul.vx v8, v8, a2  # [op1113] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vadd.vx v8, v8, t0  # [op1114] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmsne.vv v7, v4, v8  # [op1115] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 16  # [op1116] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e32, m1, ta,ma  # [op1117] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 0  # [op1118] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.v.x v8, a2  # [op1119] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmsne.vv v8, v3, v8  # [op1120] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmand.mm v7, v7, v8  # [op1121] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vcpop.m a2, v7  # [op1122] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add t1, t1, a2  # [op1123] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add a2, s2, t0  # [op1124] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t0, 16  # [op1125] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e64, m2, ta,ma  # [op1126] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vid.v v8  # [op1127] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t0, 16  # [op1128] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vadd.vx v10, v8, t0  # [op1129] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vrgather.vv v8, v4, v10  # [op1130] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s t0, v8  # [op1131] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vid.v v4  # [op1132] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a3, 2  # [op1133] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmul.vx v4, v4, a3  # [op1134] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vadd.vx v4, v4, t0  # [op1135] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmsne.vv v4, v8, v4  # [op1136] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a3, 16  # [op1137] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a3, a3, e32, m1, ta,ma  # [op1138] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vid.v v5  # [op1139] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a3, 16  # [op1140] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vadd.vx v5, v5, a3  # [op1141] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vrgather.vv v7, v3, v5  # [op1142] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a3, 0  # [op1143] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.v.x v5, a3  # [op1144] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmsne.vv v5, v7, v5  # [op1145] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmand.mm v4, v4, v5  # [op1146] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vcpop.m a3, v4  # [op1147] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add t1, t1, a3  # [op1148] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add a3, s2, t0  # [op1149] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
bne t1, zero, .Lbrc1150_true  # [op1150] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
j .Lngl.t1  # [op1150] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
.Lbrc1150_true:  # [op1150] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
j .Lngl.e1  # [op1150] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
.Lngl.t1:  # block ngl.t1
li t0, 35904  # [op1151] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add t0, t1, t0  # [op1152] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t1, 16  # [op1153] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli t1, t1, e32, m1, ta,ma  # [op1154] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t1, 0  # [op1155] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.v.x v1, t1  # [op1156] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmsne.vv v1, v3, v1  # [op1157] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t1, 16  # [op1158] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli t1, t1, e16, m1, ta,ma  # [op1159] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv1r.v v0, v1  # [op1160] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vle16.v v4, 0(a2), v0.t  # [op1161] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv1r.v v0, v1  # [op1162] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmerge.vvm v1, v2, v4, v0  # [op1163] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t1, 0  # [op1164] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add t1, t0, t1  # [op1165] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vse16.v v1, 0(t1)  # [op1166] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t1, 16  # [op1167] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli t1, t1, e32, m1, ta,ma  # [op1168] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vid.v v1  # [op1169] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t1, 16  # [op1170] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vadd.vx v1, v1, t1  # [op1171] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vrgather.vv v4, v3, v1  # [op1172] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t1, 0  # [op1173] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.v.x v1, t1  # [op1174] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmsne.vv v1, v4, v1  # [op1175] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t1, 16  # [op1176] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli t1, t1, e16, m1, ta,ma  # [op1177] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv1r.v v0, v1  # [op1178] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vle16.v v3, 0(a3), v0.t  # [op1179] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vid.v v4  # [op1180] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t1, 16  # [op1181] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vadd.vx v4, v4, t1  # [op1182] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vrgather.vv v5, v2, v4  # [op1183] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv1r.v v0, v1  # [op1184] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmerge.vvm v1, v5, v3, v0  # [op1185] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t1, 32  # [op1186] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add t1, t0, t1  # [op1187] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vse16.v v1, 0(t1)  # [op1188] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t1, 32  # [op1189] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli t1, t1, e16, m1, ta,ma  # [op1190] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vle16.v v1, 0(t0)  # [op1191] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
j .Lngl.j1  # [op1192] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
.Lngl.e1:  # block ngl.e1
li t0, 32  # [op1193] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e32, m1, ta,ma  # [op1194] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vwadd.vx v4, v6, x0  # [op1195] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1196] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e64, m2, ta,ma  # [op1197] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t0, 2  # [op1198] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmul.vx v4, v4, t0  # [op1199] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1200] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e16, m1, ta,ma  # [op1201] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t0, 35904  # [op1202] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add t0, t1, t0  # [op1203] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t1, 128  # [op1204] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add t1, t0, t1  # [op1205] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1206] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e32, m1, ta,ma  # [op1207] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 0  # [op1208] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.v.x v3, a2  # [op1209] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 1  # [op1210] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.v.x v6, a2  # [op1211] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv1r.v v0, v1  # [op1212] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmerge.vvm v1, v3, v6, v0  # [op1213] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1214] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1215] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vadd.vx v6, v4, s2  # [op1216] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1217] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e32, m1, ta,ma  # [op1218] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 0  # [op1219] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.v.x v3, a2  # [op1220] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmsne.vv v1, v1, v3  # [op1221] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv1r.v v0, v1  # [op1222] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1223] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1224] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 0  # [op1225] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.v.x v8, a2  # [op1226] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.v.x v4, t1  # [op1227] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsub.vv v6, v6, v4  # [op1228] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmerge.vvm v6, v8, v6, v0  # [op1229] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vadd.vv v4, v4, v6  # [op1230] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1231] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e16, m1, ta,ma  # [op1232] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1233] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1234] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v4  # [op1235] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a3, 0  # [op1236] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1237] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1238] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1239] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v2  # [op1240] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1241] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v2, 1  # [op1242] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1243] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1244] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1245] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1246] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v4, 1  # [op1247] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1248] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a3, 2  # [op1249] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1250] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1251] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1252] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1253] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1254] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1255] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1256] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1257] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1258] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1259] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1260] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1261] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a3, 4  # [op1262] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1263] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1264] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1265] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1266] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1267] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1268] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1269] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1270] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1271] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1272] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1273] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1274] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a3, 6  # [op1275] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1276] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1277] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1278] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1279] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1280] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1281] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1282] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1283] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1284] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1285] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1286] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1287] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a3, 8  # [op1288] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1289] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1290] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1291] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1292] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1293] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1294] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1295] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1296] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1297] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1298] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1299] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1300] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a3, 10  # [op1301] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1302] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1303] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1304] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1305] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1306] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1307] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1308] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1309] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1310] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1311] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1312] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1313] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a3, 12  # [op1314] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1315] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1316] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1317] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1318] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1319] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1320] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1321] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1322] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1323] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1324] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1325] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1326] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a3, 14  # [op1327] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1328] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1329] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1330] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1331] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1332] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1333] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1334] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1335] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1336] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1337] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1338] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1339] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a3, 16  # [op1340] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1341] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1342] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1343] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1344] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1345] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1346] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1347] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1348] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1349] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1350] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1351] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1352] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a3, 18  # [op1353] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1354] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1355] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1356] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1357] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1358] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1359] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1360] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1361] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1362] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1363] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1364] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1365] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a3, 20  # [op1366] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1367] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1368] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1369] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1370] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1371] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1372] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1373] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1374] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1375] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1376] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1377] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1378] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a3, 22  # [op1379] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1380] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1381] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1382] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1383] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1384] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1385] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1386] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1387] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1388] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1389] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1390] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1391] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a3, 24  # [op1392] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1393] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1394] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1395] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1396] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1397] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1398] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1399] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1400] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1401] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1402] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1403] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1404] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a3, 26  # [op1405] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1406] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1407] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1408] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1409] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1410] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1411] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1412] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1413] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1414] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1415] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1416] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1417] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a3, 28  # [op1418] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1419] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1420] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1421] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1422] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1423] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1424] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1425] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1426] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1427] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1428] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1429] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1430] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a3, 30  # [op1431] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1432] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1433] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1434] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1435] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1436] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1437] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1438] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1439] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1440] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1441] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1442] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1443] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a3, 32  # [op1444] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1445] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1446] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1447] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1448] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1449] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1450] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1451] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1452] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1453] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1454] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1455] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1456] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a3, 34  # [op1457] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1458] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1459] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1460] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1461] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1462] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1463] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1464] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1465] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1466] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1467] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1468] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1469] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a3, 36  # [op1470] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1471] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1472] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1473] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1474] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1475] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1476] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1477] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1478] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1479] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1480] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1481] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1482] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a3, 38  # [op1483] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1484] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1485] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1486] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1487] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1488] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1489] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1490] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1491] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1492] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1493] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1494] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1495] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a3, 40  # [op1496] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1497] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1498] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1499] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1500] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1501] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1502] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1503] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1504] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1505] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1506] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1507] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1508] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a3, 42  # [op1509] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1510] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1511] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1512] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1513] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1514] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1515] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1516] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1517] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1518] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1519] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1520] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1521] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a3, 44  # [op1522] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1523] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1524] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1525] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1526] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1527] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1528] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1529] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1530] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1531] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1532] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1533] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1534] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a3, 46  # [op1535] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1536] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1537] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1538] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1539] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1540] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1541] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1542] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1543] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1544] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1545] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1546] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1547] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a3, 48  # [op1548] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1549] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1550] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1551] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1552] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1553] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1554] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1555] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1556] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1557] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1558] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1559] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1560] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a3, 50  # [op1561] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1562] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1563] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1564] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1565] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1566] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1567] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1568] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1569] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1570] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1571] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1572] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1573] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a3, 52  # [op1574] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1575] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1576] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1577] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1578] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1579] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1580] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1581] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1582] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1583] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1584] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1585] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1586] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a3, 54  # [op1587] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1588] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1589] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1590] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1591] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1592] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1593] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1594] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1595] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1596] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1597] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1598] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1599] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a3, 56  # [op1600] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1601] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1602] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1603] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1604] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1605] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1606] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1607] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1608] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1609] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1610] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1611] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1612] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a3, 58  # [op1613] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1614] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1615] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1616] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1617] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1618] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1619] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1620] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1621] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1622] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1623] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1624] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1625] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a3, 60  # [op1626] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1627] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1628] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1629] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1630] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1631] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1632] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
lhu a2, 0(a2)  # [op1633] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a2, 0(a3)  # [op1634] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 32  # [op1635] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a2, a2, e64, m2, ta,ma  # [op1636] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1637] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a2, v2  # [op1638] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a3, 62  # [op1639] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add a3, t0, a3  # [op1640] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a4, 32  # [op1641] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli a4, a4, e16, m1, ta,ma  # [op1642] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vmv.x.s a4, v1  # [op1643] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh a4, 0(t1)  # [op1644] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v1, v1, 1  # [op1645] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
lhu t1, 0(a2)  # [op1646] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
sh t1, 0(a3)  # [op1647] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t1, 32  # [op1648] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli t1, t1, e64, m2, ta,ma  # [op1649] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vslidedown.vi v2, v2, 1  # [op1650] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t1, 32  # [op1651] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli t1, t1, e16, m1, ta,ma  # [op1652] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vle16.v v1, 0(t0)  # [op1653] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
j .Lngl.j1  # [op1654] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
.Lngl.j1:  # block ngl.j1
li t0, 32  # [op1655] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vsetvli t0, t0, e16, m1, ta,ma  # [op1656] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t0, 14656  # [op1657] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add t0, t1, t0  # [op1658] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
mv t1, s1  # [op1659] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li a2, 2  # [op1660] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
mul t1, t1, a2  # [op1661] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
add t0, t0, t1  # [op1662] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
vse16.v v1, 0(t0)  # [op1663] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:31:13
li t0, 32  # [op1664] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
add t0, a1, t0  # [op1665] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
li t1, 32  # [op1666] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
addw t1, s1, t1  # [op1667] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op1668] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv s1, t1  # [op1670] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv a1, t0  # [op1670] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk20_head  # [op1670] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk21_head:  # block chunk21_head
li s1, 32  # [op1671] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op1672] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc1673_true  # [op1673] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op1673] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op1673] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk21_exit  # [op1673] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lbrc1673_true:  # [op1673] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk21_body  # [op1673] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk21_exit:  # block chunk21_exit
li t1, 0  # [op1674] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op1675] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op1675] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op1675] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk22_head  # [op1675] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk21_body:  # block chunk21_body
li s1, 32  # [op1676] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op1677] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op1678] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
vid.v v1  # [op1680] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
vadd.vx v1, v1, t0  # [op1681] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
    # [peephole-li] [op1682] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
vwadd.vx v2, v1, x0  # [op1684] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
    # [peephole-li] [op1685] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
vsetvli s1, s1, e64, m2, ta,ma  # [op1686] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
li s1, 4  # [op1687] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
vmul.vx v2, v2, s1  # [op1688] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
li s1, 1408  # [op1689] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
add s1, a1, s1  # [op1690] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
li a1, 32  # [op1691] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
vsetvli a1, a1, e32, m1, ta,ma  # [op1692] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
vluxei64.v v1, (s1), v2  # [op1693] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
li s1, 32  # [op1694] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
vid.v v2  # [op1696] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
vadd.vx v2, v2, t0  # [op1697] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
    # [peephole-li] [op1698] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
vwadd.vx v4, v2, x0  # [op1700] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
    # [peephole-li] [op1701] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
vsetvli s1, s1, e64, m2, ta,ma  # [op1702] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
li s1, 4  # [op1703] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
vmul.vx v2, v4, s1  # [op1704] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
li s1, 15808  # [op1705] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
add s1, a1, s1  # [op1706] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
li a1, 32  # [op1707] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
vsetvli a1, a1, e32, m1, ta,ma  # [op1708] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
vluxei64.v v4, (s1), v2  # [op1709] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
li s1, 32  # [op1710] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
vmul.vv v1, v1, v4  # [op1712] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
vid.v v2  # [op1713] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
vadd.vx v2, v2, t0  # [op1714] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
    # [peephole-li] [op1715] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
vwadd.vx v4, v2, x0  # [op1717] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
    # [peephole-li] [op1718] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
vsetvli s1, s1, e64, m2, ta,ma  # [op1719] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
li s1, 4  # [op1720] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
vmul.vx v2, v4, s1  # [op1721] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
li s1, 15936  # [op1722] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
add s1, a1, s1  # [op1723] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
li a1, 32  # [op1724] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
vsetvli a1, a1, e32, m1, ta,ma  # [op1725] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
vsuxei64.v v1, (s1), v2  # [op1726] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
li s1, 32  # [op1727] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:29
    # [peephole-li] [op1729] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op1730] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op1731] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op1732] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op1733] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk21_head  # [op1735] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk22_head:  # block chunk22_head
li s1, 512  # [op1736] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op1737] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc1738_true  # [op1738] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op1738] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op1738] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk22_exit  # [op1738] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lbrc1738_true:  # [op1738] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk22_body  # [op1738] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk22_exit:  # block chunk22_exit
li t1, 0  # [op1739] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op1740] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op1740] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op1740] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk23_head  # [op1740] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk22_body:  # block chunk22_body
li s1, 32  # [op1741] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op1742] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op1743] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:21
vid.v v1  # [op1745] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:21
vadd.vx v1, v1, t0  # [op1746] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:21
li s1, 16  # [op1747] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:21
vmv.v.x v2, s1  # [op1748] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:21
vdiv.vv v1, v1, v2  # [op1749] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:21
li s1, 32  # [op1750] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:21
vwadd.vx v2, v1, x0  # [op1752] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:21
    # [peephole-li] [op1753] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:21
vsetvli s1, s1, e64, m2, ta,ma  # [op1754] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:21
li s1, 8  # [op1755] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:21
vmul.vx v2, v2, s1  # [op1756] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:21
li s1, 16064  # [op1757] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:21
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:21
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:21
add s1, a1, s1  # [op1758] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:21
li a1, 32  # [op1759] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:21
vluxei64.v v4, (s1), v2  # [op1761] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:21
li s1, 32  # [op1762] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:21
vsetvli s1, s1, e32, m1, ta,ma  # [op1763] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:21
li s1, 32  # [op1764] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op1765] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op1766] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op1767] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op1768] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk22_head  # [op1770] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk23_head:  # block chunk23_head
li s1, 32  # [op1771] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op1772] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc1773_true  # [op1773] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t2  # [op1773] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk23_exit  # [op1773] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lbrc1773_true:  # [op1773] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk23_body  # [op1773] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk23_exit:  # block chunk23_exit
li t0, 0  # [op1774] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
j .Lstg24_head  # [op1775] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
.Lchunk23_body:  # block chunk23_body
li s1, 32  # [op1776] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op1777] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op1778] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
vid.v v1  # [op1780] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
vadd.vx v1, v1, t0  # [op1781] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
    # [peephole-li] [op1782] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
vwadd.vx v2, v1, x0  # [op1784] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
    # [peephole-li] [op1785] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
vsetvli s1, s1, e64, m2, ta,ma  # [op1786] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
li s1, 4  # [op1787] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
vmul.vx v2, v2, s1  # [op1788] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
li s1, 1408  # [op1789] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
add s1, a1, s1  # [op1790] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
li a1, 32  # [op1791] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
vsetvli a1, a1, e32, m1, ta,ma  # [op1792] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
vluxei64.v v1, (s1), v2  # [op1793] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
li s1, 32  # [op1794] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
vid.v v2  # [op1796] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
vadd.vx v2, v2, t0  # [op1797] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
    # [peephole-li] [op1798] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
vwadd.vx v4, v2, x0  # [op1800] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
    # [peephole-li] [op1801] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
vsetvli s1, s1, e64, m2, ta,ma  # [op1802] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
li s1, 4  # [op1803] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
vmul.vx v2, v4, s1  # [op1804] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
li s1, 20480  # [op1805] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
add s1, a1, s1  # [op1806] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
li a1, 32  # [op1807] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
vsetvli a1, a1, e32, m1, ta,ma  # [op1808] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
vluxei64.v v4, (s1), v2  # [op1809] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
li s1, 32  # [op1810] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
vmslt.vv v1, v1, v4  # [op1812] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
vid.v v2  # [op1813] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
vadd.vx v2, v2, t0  # [op1814] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
    # [peephole-li] [op1815] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
vwadd.vx v4, v2, x0  # [op1817] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
    # [peephole-li] [op1818] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
vsetvli s1, s1, e64, m2, ta,ma  # [op1819] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
li s1, 4  # [op1820] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
vmul.vx v2, v4, s1  # [op1821] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
li s1, 20608  # [op1822] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
add s1, a1, s1  # [op1823] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
li a1, 32  # [op1824] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
vsetvli a1, a1, e32, m1, ta,ma  # [op1825] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
li a1, 1  # [op1826] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
vmv.v.x v4, a1  # [op1827] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
li a1, 0  # [op1828] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
vmv.v.x v5, a1  # [op1829] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
vmv1r.v v0, v1  # [op1830] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
vmerge.vvm v1, v5, v4, v0  # [op1831] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
vsuxei64.v v1, (s1), v2  # [op1832] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:27
li s1, 32  # [op1833] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op1834] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op1835] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op1836] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op1837] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk23_head  # [op1839] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lstg24_head:  # block stg24_head
li s1, 512  # [op1840] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
slt s1, t0, s1  # [op1841] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
bne s1, zero, .Lbrc1842_true  # [op1842] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
j .Lstg24_exit  # [op1842] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
.Lbrc1842_true:  # [op1842] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
j .Lstg24_body  # [op1842] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
.Lstg24_body:  # block stg24_body
li s1, 32  # [op1843] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vsetvli s1, s1, e32, m1, ta,ma  # [op1844] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vid.v v1  # [op1845] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vadd.vx v1, v1, t0  # [op1846] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li s1, 16  # [op1847] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vmv.v.x v2, s1  # [op1848] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vdiv.vv v2, v1, v2  # [op1849] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li s1, 32  # [op1850] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vmv.v.x v3, s1  # [op1851] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vrem.vv v2, v2, v3  # [op1852] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li s1, 16  # [op1853] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vmv.v.x v3, s1  # [op1854] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vrem.vv v3, v1, v3  # [op1855] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li s1, 32  # [op1856] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vwadd.vx v4, v2, x0  # [op1858] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
    # [peephole-li] [op1859] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vsetvli s1, s1, e64, m2, ta,ma  # [op1860] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li s1, 4  # [op1861] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vmul.vx v2, v4, s1  # [op1862] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li s1, 20608  # [op1863] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
add s1, a1, s1  # [op1864] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li a1, 32  # [op1865] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vsetvli a1, a1, e32, m1, ta,ma  # [op1866] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vluxei64.v v4, (s1), v2  # [op1867] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li s1, 32  # [op1868] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vwadd.vx v2, v1, x0  # [op1870] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
    # [peephole-li] [op1871] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vsetvli s1, s1, e64, m2, ta,ma  # [op1872] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li s1, 4  # [op1873] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vmul.vx v2, v2, s1  # [op1874] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li s1, 20864  # [op1875] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
add s1, a1, s1  # [op1876] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li a1, 32  # [op1877] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vsetvli a1, a1, e32, m1, ta,ma  # [op1878] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vsuxei64.v v4, (s1), v2  # [op1879] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li s1, 32  # [op1880] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
addw t0, t0, s1  # [op1881] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
j .Lstg24_head  # [op1882] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
.Lstg24_exit:  # block stg24_exit
li t0, 0  # [op1883] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv s1, t0  # [op1884] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv a1, t1  # [op1884] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk25_head  # [op1884] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk25_head:  # block chunk25_head
li t0, 512  # [op1885] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
slt t0, s1, t0  # [op1886] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
bne t0, zero, .Lbrc1887_true  # [op1887] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t2  # [op1887] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t1, a1  # [op1887] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk25_exit  # [op1887] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lbrc1887_true:  # [op1887] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk25_body  # [op1887] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk25_exit:  # block chunk25_exit
li t0, 35392  # [op1888] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s1, t1, t0  # [op1889] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t0, 128  # [op1890] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a1, s1, t0  # [op1891] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t0, 256  # [op1892] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add t0, s1, t0  # [op1893] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sd t0, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t0, 8  # [op1894] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vsetvli t0, t0, e32, m1, ta,ma  # [op1895] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vid.v v2  # [op1896] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t0, 8  # [op1897] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vid.v v1  # [op1899] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t0, 64  # [op1900] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vsetvli t0, t0, e16, m1, ta,ma  # [op1901] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t0, 0  # [op1902] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv.v.x v3, t0  # [op1903] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv.v.x v4, t0  # [op1904] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
    # [peephole-li] [op1905] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t3, 4  # [op1906] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mv a6, t0  # [op1907] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
j .Lmtile26.head  # [op1907] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
.Lchunk25_body:  # block chunk25_body
li t0, 32  # [op1908] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
vsetvli t0, t0, e16, m1, ta,ma  # [op1909] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
li t0, 32  # [op1910] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vsetvli t0, t0, e32, m1, ta,ma  # [op1911] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vid.v v1  # [op1912] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vadd.vx v1, v1, s1  # [op1913] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t0, 32  # [op1914] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vwadd.vx v2, v1, x0  # [op1916] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
    # [peephole-li] [op1917] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vsetvli t0, t0, e64, m2, ta,ma  # [op1918] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t0, 4  # [op1919] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vmul.vx v2, v2, t0  # [op1920] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t0, 20864  # [op1921] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
add t0, t1, t0  # [op1922] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t1, 32  # [op1923] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vsetvli t1, t1, e32, m1, ta,ma  # [op1924] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vluxei64.v v1, (t0), v2  # [op1925] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t0, 0  # [op1926] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vmv.v.x v2, t0  # [op1927] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vmsne.vv v1, v1, v2  # [op1928] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t0, 32  # [op1929] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vsetvli t0, t0, e16, m1, ta,ma  # [op1930] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t0, 32  # [op1931] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vsetvli t0, t0, e32, m1, ta,ma  # [op1932] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vid.v v2  # [op1933] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vadd.vx v2, v2, s1  # [op1934] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t0, 32  # [op1935] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vwadd.vx v4, v2, x0  # [op1937] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
    # [peephole-li] [op1938] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vsetvli t0, t0, e64, m2, ta,ma  # [op1939] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t0, 4  # [op1940] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vmul.vx v2, v4, t0  # [op1941] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t0, 22912  # [op1942] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
add t0, t1, t0  # [op1943] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t1, 32  # [op1944] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vsetvli t1, t1, e32, m1, ta,ma  # [op1945] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vluxei64.v v4, (t0), v2  # [op1946] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t0, 0  # [op1947] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vmv.v.x v2, t0  # [op1948] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vmsne.vv v2, v4, v2  # [op1949] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t0, 32  # [op1950] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vsetvli t0, t0, e16, m1, ta,ma  # [op1951] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vmand.mm v1, v1, v2  # [op1952] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t0, 32  # [op1953] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vsetvli t0, t0, e32, m1, ta,ma  # [op1954] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vid.v v2  # [op1955] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vadd.vx v2, v2, s1  # [op1956] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t0, 32  # [op1957] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vwadd.vx v4, v2, x0  # [op1959] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
    # [peephole-li] [op1960] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vsetvli t0, t0, e64, m2, ta,ma  # [op1961] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t0, 4  # [op1962] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vmul.vx v2, v4, t0  # [op1963] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t0, 24960  # [op1964] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
add t0, t1, t0  # [op1965] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t1, 32  # [op1966] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vsetvli t1, t1, e32, m1, ta,ma  # [op1967] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t1, 1  # [op1968] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vmv.v.x v4, t1  # [op1969] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t1, 0  # [op1970] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vmv.v.x v5, t1  # [op1971] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vmv1r.v v0, v1  # [op1972] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vmerge.vvm v4, v5, v4, v0  # [op1973] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vsuxei64.v v4, (t0), v2  # [op1974] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t0, 32  # [op1975] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vsetvli t0, t0, e16, m1, ta,ma  # [op1976] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t0, 32  # [op1977] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vsetvli t0, t0, e32, m1, ta,ma  # [op1978] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vid.v v2  # [op1979] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vadd.vx v2, v2, s1  # [op1980] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t0, 32  # [op1981] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vwadd.vx v4, v2, x0  # [op1983] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
    # [peephole-li] [op1984] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vsetvli t0, t0, e64, m2, ta,ma  # [op1985] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t0, 4  # [op1986] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vmul.vx v2, v4, t0  # [op1987] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t0, 24960  # [op1988] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
add t0, t1, t0  # [op1989] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t1, 32  # [op1990] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vsetvli t1, t1, e32, m1, ta,ma  # [op1991] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t1, 1  # [op1992] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vmv.v.x v4, t1  # [op1993] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t1, 0  # [op1994] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vmv.v.x v5, t1  # [op1995] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vmv1r.v v0, v1  # [op1996] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vmerge.vvm v4, v5, v4, v0  # [op1997] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vsuxei64.v v4, (t0), v2  # [op1998] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t0, 32  # [op1999] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
vsetvli t0, t0, e16, m1, ta,ma  # [op2000] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:34:26
li t0, 32  # [op2001] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e32, m1, ta,ma  # [op2002] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vid.v v2  # [op2003] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vadd.vx v2, v2, s1  # [op2004] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t0, 16  # [op2005] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.v.x v3, t0  # [op2006] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vdiv.vv v2, v2, v3  # [op2007] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op2008] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vwadd.vx v4, v2, x0  # [op2010] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
    # [peephole-li] [op2011] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e64, m2, ta,ma  # [op2012] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t0, 4  # [op2013] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmul.vx v2, v4, t0  # [op2014] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t0, 15936  # [op2015] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add t0, t1, t0  # [op2016] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t1, 32  # [op2017] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli t1, t1, e32, m1, ta,ma  # [op2018] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vluxei64.v v4, (t0), v2  # [op2019] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op2020] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e16, m1, ta,ma  # [op2021] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op2022] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e32, m1, ta,ma  # [op2023] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vid.v v2  # [op2024] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vadd.vx v2, v2, s1  # [op2025] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t0, 16  # [op2026] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.v.x v3, t0  # [op2027] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vrem.vv v2, v2, v3  # [op2028] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op2029] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vwadd.vx v6, v2, x0  # [op2031] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
    # [peephole-li] [op2032] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e64, m2, ta,ma  # [op2033] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t0, 4  # [op2034] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmul.vx v2, v6, t0  # [op2035] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t0, 64  # [op2036] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add t0, t1, t0  # [op2037] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t1, 32  # [op2038] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli t1, t1, e32, m1, ta,ma  # [op2039] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vluxei64.v v5, (t0), v2  # [op2040] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op2041] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e16, m1, ta,ma  # [op2042] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op2043] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e32, m1, ta,ma  # [op2044] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vadd.vv v6, v4, v5  # [op2045] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op2046] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e16, m1, ta,ma  # [op2047] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op2048] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e32, m1, ta,ma  # [op2049] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vid.v v2  # [op2050] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vadd.vx v2, v2, s1  # [op2051] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op2052] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vwadd.vx v4, v2, x0  # [op2054] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
    # [peephole-li] [op2055] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e64, m2, ta,ma  # [op2056] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t0, 4  # [op2057] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmul.vx v2, v4, t0  # [op2058] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t0, 27008  # [op2059] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add t0, t1, t0  # [op2060] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t1, 32  # [op2061] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli t1, t1, e32, m1, ta,ma  # [op2062] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vluxei64.v v4, (t0), v2  # [op2063] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op2064] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.v.v v8, v4  # [op2066] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
    # [peephole-li] [op2067] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e16, m1, ta,ma  # [op2068] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vfncvt.f.f.w v2, v8  # [op2069] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op2070] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e32, m1, ta,ma  # [op2071] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t0, 0  # [op2072] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.v.x v3, t0  # [op2073] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t0, 1  # [op2074] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.v.x v4, t0  # [op2075] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv1r.v v0, v1  # [op2076] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmerge.vvm v3, v3, v4, v0  # [op2077] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op2078] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vwadd.vx v4, v6, x0  # [op2080] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
    # [peephole-li] [op2081] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e64, m2, ta,ma  # [op2082] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t0, 2  # [op2083] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmul.vx v4, v4, t0  # [op2084] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op2085] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e16, m1, ta,ma  # [op2086] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t1, 0  # [op2087] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t0, 16  # [op2088] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e64, m2, ta,ma  # [op2089] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s t0, v4  # [op2090] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vid.v v8  # [op2091] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 2  # [op2092] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmul.vx v8, v8, a2  # [op2093] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vadd.vx v8, v8, t0  # [op2094] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmsne.vv v7, v4, v8  # [op2095] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 16  # [op2096] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e32, m1, ta,ma  # [op2097] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 0  # [op2098] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.v.x v8, a2  # [op2099] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmsne.vv v8, v3, v8  # [op2100] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmand.mm v7, v7, v8  # [op2101] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vcpop.m a2, v7  # [op2102] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add t1, t1, a2  # [op2103] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add a2, s3, t0  # [op2104] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t0, 16  # [op2105] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e64, m2, ta,ma  # [op2106] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vid.v v8  # [op2107] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t0, 16  # [op2108] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vadd.vx v10, v8, t0  # [op2109] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vrgather.vv v8, v4, v10  # [op2110] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s t0, v8  # [op2111] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vid.v v4  # [op2112] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a3, 2  # [op2113] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmul.vx v4, v4, a3  # [op2114] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vadd.vx v4, v4, t0  # [op2115] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmsne.vv v4, v8, v4  # [op2116] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a3, 16  # [op2117] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a3, a3, e32, m1, ta,ma  # [op2118] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vid.v v5  # [op2119] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a3, 16  # [op2120] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vadd.vx v5, v5, a3  # [op2121] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vrgather.vv v7, v3, v5  # [op2122] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a3, 0  # [op2123] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.v.x v5, a3  # [op2124] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmsne.vv v5, v7, v5  # [op2125] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmand.mm v4, v4, v5  # [op2126] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vcpop.m a3, v4  # [op2127] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add t1, t1, a3  # [op2128] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add a3, s3, t0  # [op2129] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
bne t1, zero, .Lbrc2130_true  # [op2130] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
j .Lngl.t2  # [op2130] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
.Lbrc2130_true:  # [op2130] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
j .Lngl.e2  # [op2130] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
.Lngl.t2:  # block ngl.t2
li t0, 35904  # [op2131] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add t0, t1, t0  # [op2132] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t1, 16  # [op2133] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli t1, t1, e32, m1, ta,ma  # [op2134] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t1, 0  # [op2135] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.v.x v1, t1  # [op2136] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmsne.vv v1, v3, v1  # [op2137] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t1, 16  # [op2138] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli t1, t1, e16, m1, ta,ma  # [op2139] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv1r.v v0, v1  # [op2140] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vle16.v v4, 0(a2), v0.t  # [op2141] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv1r.v v0, v1  # [op2142] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmerge.vvm v1, v2, v4, v0  # [op2143] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t1, 0  # [op2144] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add t1, t0, t1  # [op2145] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vse16.v v1, 0(t1)  # [op2146] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t1, 16  # [op2147] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli t1, t1, e32, m1, ta,ma  # [op2148] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vid.v v1  # [op2149] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t1, 16  # [op2150] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vadd.vx v1, v1, t1  # [op2151] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vrgather.vv v4, v3, v1  # [op2152] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t1, 0  # [op2153] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.v.x v1, t1  # [op2154] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmsne.vv v1, v4, v1  # [op2155] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t1, 16  # [op2156] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli t1, t1, e16, m1, ta,ma  # [op2157] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv1r.v v0, v1  # [op2158] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vle16.v v3, 0(a3), v0.t  # [op2159] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vid.v v4  # [op2160] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t1, 16  # [op2161] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vadd.vx v4, v4, t1  # [op2162] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vrgather.vv v5, v2, v4  # [op2163] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv1r.v v0, v1  # [op2164] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmerge.vvm v1, v5, v3, v0  # [op2165] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t1, 32  # [op2166] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add t1, t0, t1  # [op2167] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vse16.v v1, 0(t1)  # [op2168] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t1, 32  # [op2169] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli t1, t1, e16, m1, ta,ma  # [op2170] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vle16.v v1, 0(t0)  # [op2171] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
j .Lngl.j2  # [op2172] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
.Lngl.e2:  # block ngl.e2
li t0, 32  # [op2173] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e32, m1, ta,ma  # [op2174] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vwadd.vx v4, v6, x0  # [op2175] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op2176] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e64, m2, ta,ma  # [op2177] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t0, 2  # [op2178] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmul.vx v4, v4, t0  # [op2179] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op2180] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e16, m1, ta,ma  # [op2181] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t0, 35904  # [op2182] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add t0, t1, t0  # [op2183] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t1, 128  # [op2184] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add t1, t0, t1  # [op2185] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2186] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e32, m1, ta,ma  # [op2187] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 0  # [op2188] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.v.x v3, a2  # [op2189] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 1  # [op2190] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.v.x v6, a2  # [op2191] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv1r.v v0, v1  # [op2192] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmerge.vvm v1, v3, v6, v0  # [op2193] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2194] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2195] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vadd.vx v6, v4, s3  # [op2196] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2197] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e32, m1, ta,ma  # [op2198] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 0  # [op2199] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.v.x v3, a2  # [op2200] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmsne.vv v1, v1, v3  # [op2201] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv1r.v v0, v1  # [op2202] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2203] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2204] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 0  # [op2205] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.v.x v8, a2  # [op2206] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.v.x v4, t1  # [op2207] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsub.vv v6, v6, v4  # [op2208] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmerge.vvm v6, v8, v6, v0  # [op2209] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vadd.vv v4, v4, v6  # [op2210] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2211] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e16, m1, ta,ma  # [op2212] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2213] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2214] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v4  # [op2215] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a3, 0  # [op2216] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2217] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2218] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2219] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v2  # [op2220] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2221] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v2, 1  # [op2222] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2223] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2224] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2225] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2226] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v4, 1  # [op2227] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2228] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a3, 2  # [op2229] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2230] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2231] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2232] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2233] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2234] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2235] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2236] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2237] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2238] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2239] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2240] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2241] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a3, 4  # [op2242] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2243] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2244] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2245] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2246] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2247] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2248] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2249] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2250] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2251] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2252] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2253] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2254] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a3, 6  # [op2255] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2256] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2257] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2258] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2259] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2260] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2261] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2262] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2263] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2264] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2265] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2266] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2267] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a3, 8  # [op2268] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2269] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2270] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2271] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2272] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2273] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2274] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2275] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2276] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2277] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2278] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2279] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2280] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a3, 10  # [op2281] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2282] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2283] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2284] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2285] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2286] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2287] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2288] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2289] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2290] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2291] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2292] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2293] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a3, 12  # [op2294] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2295] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2296] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2297] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2298] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2299] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2300] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2301] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2302] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2303] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2304] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2305] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2306] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a3, 14  # [op2307] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2308] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2309] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2310] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2311] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2312] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2313] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2314] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2315] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2316] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2317] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2318] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2319] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a3, 16  # [op2320] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2321] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2322] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2323] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2324] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2325] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2326] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2327] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2328] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2329] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2330] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2331] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2332] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a3, 18  # [op2333] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2334] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2335] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2336] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2337] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2338] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2339] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2340] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2341] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2342] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2343] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2344] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2345] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a3, 20  # [op2346] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2347] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2348] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2349] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2350] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2351] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2352] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2353] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2354] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2355] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2356] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2357] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2358] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a3, 22  # [op2359] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2360] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2361] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2362] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2363] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2364] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2365] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2366] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2367] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2368] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2369] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2370] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2371] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a3, 24  # [op2372] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2373] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2374] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2375] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2376] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2377] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2378] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2379] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2380] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2381] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2382] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2383] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2384] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a3, 26  # [op2385] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2386] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2387] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2388] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2389] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2390] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2391] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2392] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2393] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2394] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2395] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2396] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2397] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a3, 28  # [op2398] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2399] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2400] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2401] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2402] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2403] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2404] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2405] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2406] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2407] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2408] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2409] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2410] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a3, 30  # [op2411] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2412] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2413] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2414] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2415] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2416] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2417] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2418] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2419] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2420] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2421] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2422] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2423] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a3, 32  # [op2424] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2425] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2426] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2427] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2428] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2429] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2430] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2431] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2432] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2433] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2434] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2435] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2436] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a3, 34  # [op2437] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2438] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2439] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2440] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2441] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2442] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2443] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2444] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2445] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2446] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2447] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2448] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2449] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a3, 36  # [op2450] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2451] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2452] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2453] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2454] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2455] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2456] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2457] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2458] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2459] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2460] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2461] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2462] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a3, 38  # [op2463] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2464] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2465] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2466] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2467] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2468] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2469] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2470] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2471] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2472] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2473] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2474] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2475] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a3, 40  # [op2476] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2477] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2478] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2479] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2480] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2481] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2482] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2483] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2484] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2485] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2486] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2487] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2488] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a3, 42  # [op2489] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2490] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2491] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2492] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2493] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2494] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2495] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2496] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2497] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2498] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2499] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2500] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2501] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a3, 44  # [op2502] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2503] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2504] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2505] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2506] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2507] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2508] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2509] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2510] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2511] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2512] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2513] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2514] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a3, 46  # [op2515] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2516] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2517] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2518] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2519] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2520] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2521] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2522] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2523] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2524] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2525] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2526] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2527] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a3, 48  # [op2528] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2529] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2530] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2531] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2532] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2533] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2534] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2535] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2536] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2537] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2538] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2539] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2540] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a3, 50  # [op2541] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2542] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2543] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2544] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2545] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2546] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2547] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2548] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2549] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2550] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2551] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2552] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2553] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a3, 52  # [op2554] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2555] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2556] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2557] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2558] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2559] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2560] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2561] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2562] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2563] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2564] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2565] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2566] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a3, 54  # [op2567] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2568] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2569] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2570] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2571] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2572] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2573] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2574] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2575] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2576] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2577] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2578] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2579] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a3, 56  # [op2580] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2581] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2582] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2583] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2584] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2585] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2586] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2587] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2588] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2589] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2590] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2591] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2592] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a3, 58  # [op2593] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2594] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2595] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2596] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2597] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2598] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2599] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2600] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2601] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2602] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2603] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2604] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2605] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a3, 60  # [op2606] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2607] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2608] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2609] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2610] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2611] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2612] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
lhu a2, 0(a2)  # [op2613] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a2, 0(a3)  # [op2614] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 32  # [op2615] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a2, a2, e64, m2, ta,ma  # [op2616] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2617] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a2, v2  # [op2618] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a3, 62  # [op2619] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add a3, t0, a3  # [op2620] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a4, 32  # [op2621] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli a4, a4, e16, m1, ta,ma  # [op2622] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vmv.x.s a4, v1  # [op2623] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh a4, 0(t1)  # [op2624] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v1, v1, 1  # [op2625] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
lhu t1, 0(a2)  # [op2626] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
sh t1, 0(a3)  # [op2627] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t1, 32  # [op2628] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli t1, t1, e64, m2, ta,ma  # [op2629] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vslidedown.vi v2, v2, 1  # [op2630] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t1, 32  # [op2631] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli t1, t1, e16, m1, ta,ma  # [op2632] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vle16.v v1, 0(t0)  # [op2633] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
j .Lngl.j2  # [op2634] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
.Lngl.j2:  # block ngl.j2
li t0, 32  # [op2635] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vsetvli t0, t0, e16, m1, ta,ma  # [op2636] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t0, 29056  # [op2637] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add t0, t1, t0  # [op2638] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
mv t1, s1  # [op2639] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li a2, 2  # [op2640] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
mul t1, t1, a2  # [op2641] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
add t0, t0, t1  # [op2642] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
vse16.v v1, 0(t0)  # [op2643] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:33:13
li t0, 32  # [op2644] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
add t0, a1, t0  # [op2645] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
li t1, 32  # [op2646] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
addw t1, s1, t1  # [op2647] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op2648] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv s1, t1  # [op2650] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv a1, t0  # [op2650] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk25_head  # [op2650] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lmtile26.head:  # block mtile26.head
slt t0, a6, t3  # [op2651] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
bne t0, zero, .Lbrc2652_true  # [op2652] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mv t0, a6  # [op2652] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
j .Lmtile26.exit  # [op2652] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
.Lbrc2652_true:  # [op2652] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
j .Lmtile26.body  # [op2652] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
.Lmtile26.body:  # block mtile26.body
li a5, 2  # [op2653] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
divu t0, a6, a5  # [op2654] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul t1, t0, a5  # [op2655] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub a2, a6, t1  # [op2656] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t1, 8  # [op2657] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul t0, t0, t1  # [op2658] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sd t0, 200(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul t0, a2, t1  # [op2659] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sd t0, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t0, 8  # [op2660] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vsetvli t0, t0, e32, m1, ta,ma  # [op2661] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t0, 0  # [op2662] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv.v.x v5, t0  # [op2663] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t1, 0  # [op2664] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t0, 200(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a3, t0, t1  # [op2665] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t0, 16  # [op2666] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt a2, a3, t0  # [op2667] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld a4, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub a4, t0, a4  # [op2668] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub a2, t1, a2  # [op2669] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
and a2, a4, a2  # [op2670] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
addiw a2, a2, 0  # [op2671] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a4, 8  # [op2672] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv.v.x v6, a2  # [op2674] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmslt.vv v6, v1, v6  # [op2675] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v6  # [op2676] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a4, 256  # [op2677] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld a2, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld a2, 16(a2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s6, a2, a4  # [op2678] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a2, 64  # [op2679] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul a3, a3, a2  # [op2680] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s6, s6, a3  # [op2681] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a3, 4  # [op2682] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul s7, s7, a3  # [op2683] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s6, s6, s7  # [op2684] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 8  # [op2685] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vle32.v v6, 0(s6), v0.t  # [op2687] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmerge.vvm v6, v5, v6, v0  # [op2688] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s6, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s6, s6, t1  # [op2689] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
    # [peephole-li] [op2690] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse32.v v6, 0(s6)  # [op2692] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s6, 1  # [op2693] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 200(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s6, s7, s6  # [op2694] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt s7, s6, t0  # [op2695] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t4, t0, t4  # [op2696] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub s7, t1, s7  # [op2697] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
and s7, t4, s7  # [op2698] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
addiw s7, s7, 0  # [op2699] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op2700] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv.v.x v6, s7  # [op2702] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmslt.vv v6, v1, v6  # [op2703] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v6  # [op2704] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 16(s7)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, s7, a4  # [op2705] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul s6, s6, a2  # [op2706] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s6, s7, s6  # [op2707] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul s7, s7, a3  # [op2708] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s6, s6, s7  # [op2709] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 8  # [op2710] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vle32.v v6, 0(s6), v0.t  # [op2712] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmerge.vvm v6, v5, v6, v0  # [op2713] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s6, 32  # [op2714] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, s7, s6  # [op2715] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
    # [peephole-li] [op2716] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse32.v v6, 0(s7)  # [op2718] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 200(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a5, s7, a5  # [op2719] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt s7, a5, t0  # [op2720] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t4, t0, t4  # [op2721] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub s7, t1, s7  # [op2722] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
and s7, t4, s7  # [op2723] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
addiw s7, s7, 0  # [op2724] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op2725] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv.v.x v6, s7  # [op2727] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmslt.vv v6, v1, v6  # [op2728] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v6  # [op2729] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 16(s7)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, s7, a4  # [op2730] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul a5, a5, a2  # [op2731] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a5, s7, a5  # [op2732] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul s7, s7, a3  # [op2733] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a5, a5, s7  # [op2734] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 8  # [op2735] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vle32.v v6, 0(a5), v0.t  # [op2737] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmerge.vvm v6, v5, v6, v0  # [op2738] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld a5, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a5, a5, a2  # [op2739] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
    # [peephole-li] [op2740] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse32.v v6, 0(a5)  # [op2742] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a5, 3  # [op2743] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 200(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a5, s7, a5  # [op2744] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt s7, a5, t0  # [op2745] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t4, t0, t4  # [op2746] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub s7, t1, s7  # [op2747] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
and s7, t4, s7  # [op2748] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
addiw s7, s7, 0  # [op2749] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op2750] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv.v.x v6, s7  # [op2752] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmslt.vv v6, v1, v6  # [op2753] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v6  # [op2754] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 16(s7)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, s7, a4  # [op2755] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul a5, a5, a2  # [op2756] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a5, s7, a5  # [op2757] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul s7, s7, a3  # [op2758] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a5, a5, s7  # [op2759] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 8  # [op2760] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vle32.v v6, 0(a5), v0.t  # [op2762] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmerge.vvm v6, v5, v6, v0  # [op2763] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a5, 96  # [op2764] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a5, s7, a5  # [op2765] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 8  # [op2766] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse32.v v6, 0(a5)  # [op2768] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld a5, 200(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a5, a5, a3  # [op2769] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt s7, a5, t0  # [op2770] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t4, t0, t4  # [op2771] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub s7, t1, s7  # [op2772] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
and s7, t4, s7  # [op2773] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
addiw s7, s7, 0  # [op2774] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op2775] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv.v.x v6, s7  # [op2777] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmslt.vv v6, v1, v6  # [op2778] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v6  # [op2779] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 16(s7)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, s7, a4  # [op2780] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul a5, a5, a2  # [op2781] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a5, s7, a5  # [op2782] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul s7, s7, a3  # [op2783] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a5, a5, s7  # [op2784] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 8  # [op2785] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vle32.v v6, 0(a5), v0.t  # [op2787] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmerge.vvm v6, v5, v6, v0  # [op2788] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a5, 128  # [op2789] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a5, s7, a5  # [op2790] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 8  # [op2791] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse32.v v6, 0(a5)  # [op2793] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a5, 5  # [op2794] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 200(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a5, s7, a5  # [op2795] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt s7, a5, t0  # [op2796] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t4, t0, t4  # [op2797] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub s7, t1, s7  # [op2798] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
and s7, t4, s7  # [op2799] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
addiw s7, s7, 0  # [op2800] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op2801] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv.v.x v6, s7  # [op2803] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmslt.vv v6, v1, v6  # [op2804] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v6  # [op2805] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 16(s7)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, s7, a4  # [op2806] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul a5, a5, a2  # [op2807] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a5, s7, a5  # [op2808] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul s7, s7, a3  # [op2809] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a5, a5, s7  # [op2810] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 8  # [op2811] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vle32.v v6, 0(a5), v0.t  # [op2813] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmerge.vvm v6, v5, v6, v0  # [op2814] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a5, 160  # [op2815] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a5, s7, a5  # [op2816] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 8  # [op2817] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse32.v v6, 0(a5)  # [op2819] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a5, 6  # [op2820] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 200(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a5, s7, a5  # [op2821] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt s7, a5, t0  # [op2822] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t4, t0, t4  # [op2823] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub s7, t1, s7  # [op2824] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
and s7, t4, s7  # [op2825] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
addiw s7, s7, 0  # [op2826] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op2827] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv.v.x v6, s7  # [op2829] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmslt.vv v6, v1, v6  # [op2830] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v6  # [op2831] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 16(s7)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, s7, a4  # [op2832] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul a5, a5, a2  # [op2833] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a5, s7, a5  # [op2834] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul s7, s7, a3  # [op2835] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a5, a5, s7  # [op2836] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 8  # [op2837] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vle32.v v6, 0(a5), v0.t  # [op2839] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmerge.vvm v6, v5, v6, v0  # [op2840] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a5, 192  # [op2841] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a5, s7, a5  # [op2842] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 8  # [op2843] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse32.v v6, 0(a5)  # [op2845] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a5, 7  # [op2846] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 200(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a5, s7, a5  # [op2847] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt s7, a5, t0  # [op2848] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t0, t0, t4  # [op2849] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub s7, t1, s7  # [op2850] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
and t0, t0, s7  # [op2851] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
addiw t0, t0, 0  # [op2852] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 8  # [op2853] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv.v.x v6, t0  # [op2855] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmslt.vv v6, v1, v6  # [op2856] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v6  # [op2857] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t0, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t0, 16(t0)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add t0, t0, a4  # [op2858] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul a2, a5, a2  # [op2859] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add t0, t0, a2  # [op2860] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld a2, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul a2, a2, a3  # [op2861] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add t0, t0, a2  # [op2862] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a2, 8  # [op2863] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vle32.v v6, 0(t0), v0.t  # [op2865] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmerge.vvm v5, v5, v6, v0  # [op2866] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t0, 224  # [op2867] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld a2, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add t0, a2, t0  # [op2868] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a2, 8  # [op2869] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse32.v v5, 0(t0)  # [op2871] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t0, 64  # [op2872] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vsetvli t0, t0, e32, m2, ta,ma  # [op2873] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t0, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vle32.v v6, 0(t0)  # [op2874] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mv t0, t1  # [op2875] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
j .Lmk27.head  # [op2875] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
.Lmtile26.exit:  # block mtile26.exit
addw t1, a7, s11  # [op2876] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
li s1, 30080  # [op2877] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
li a1, 256  # [op2878] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
li t0, 0  # [op2879] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
li a2, 256  # [op2880] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
li a3, 32  # [op2881] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
j .Lmcarry31.head  # [op2882] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
.Lmk27.head:  # block mk27.head
slt t1, t0, s6  # [op2883] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
bne t1, zero, .Lbrc2884_true  # [op2884] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
j .Lmk27.exit  # [op2884] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
.Lbrc2884_true:  # [op2884] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
j .Lmk27.body  # [op2884] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
.Lmk27.body:  # block mk27.body
li t1, 32  # [op2885] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t1, t1, t0  # [op2886] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sd t1, 192(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t1, 8  # [op2887] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld a2, 200(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a2, a2, t1  # [op2888] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a3, 17  # [op2889] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt a2, a2, a3  # [op2890] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a3, 1  # [op2891] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld a4, 192(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a3, a4, a3  # [op2892] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt t1, t1, a3  # [op2893] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
and t1, a2, t1  # [op2894] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
bne t1, zero, .Lbrc2895_true  # [op2895] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
j .Ltaf28.else  # [op2895] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
.Lbrc2895_true:  # [op2895] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
j .Ltaf28.then  # [op2895] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
.Lmk27.exit:  # block mk27.exit
li t0, 64  # [op2896] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vsetvli t0, t0, e32, m2, ta,ma  # [op2897] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t0, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse32.v v6, 0(t0)  # [op2898] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t1, 0  # [op2899] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t0, 200(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a3, t0, t1  # [op2900] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t0, 16  # [op2901] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt a2, a3, t0  # [op2902] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld a4, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub a4, t0, a4  # [op2903] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub a2, t1, a2  # [op2904] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
and a2, a4, a2  # [op2905] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
addiw a2, a2, 0  # [op2906] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a4, 8  # [op2907] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vsetvli a4, a4, e32, m1, ta,ma  # [op2908] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv.v.x v5, a2  # [op2909] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmslt.vv v5, v1, v5  # [op2910] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v5  # [op2911] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld a2, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a2, a2, t1  # [op2912] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a4, 8  # [op2913] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vle32.v v5, 0(a2)  # [op2915] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a4, 30080  # [op2916] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld a2, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld a2, 16(a2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a5, a2, a4  # [op2917] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a2, 64  # [op2918] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul a3, a3, a2  # [op2919] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a5, a5, a3  # [op2920] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a3, 4  # [op2921] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s6, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul s6, s6, a3  # [op2922] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a5, a5, s6  # [op2923] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s6, 8  # [op2924] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse32.v v5, 0(a5), v0.t  # [op2926] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a5, 1  # [op2927] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s6, 200(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s6, s6, a5  # [op2928] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt s7, s6, t0  # [op2929] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t4, t0, t4  # [op2930] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub s7, t1, s7  # [op2931] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
and s7, t4, s7  # [op2932] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
addiw s7, s7, 0  # [op2933] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op2934] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv.v.x v5, s7  # [op2936] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmslt.vv v5, v1, v5  # [op2937] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v5  # [op2938] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 32  # [op2939] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, t4, s7  # [op2940] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op2941] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vle32.v v5, 0(s7)  # [op2943] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 16(s7)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, s7, a4  # [op2944] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul s6, s6, a2  # [op2945] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s6, s7, s6  # [op2946] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul s7, s7, a3  # [op2947] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s6, s6, s7  # [op2948] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 8  # [op2949] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse32.v v5, 0(s6), v0.t  # [op2951] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s6, 2  # [op2952] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 200(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s6, s7, s6  # [op2953] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt s7, s6, t0  # [op2954] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t4, t0, t4  # [op2955] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub s7, t1, s7  # [op2956] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
and s7, t4, s7  # [op2957] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
addiw s7, s7, 0  # [op2958] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op2959] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv.v.x v5, s7  # [op2961] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmslt.vv v5, v1, v5  # [op2962] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v5  # [op2963] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, s7, a2  # [op2964] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
    # [peephole-li] [op2965] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vle32.v v5, 0(s7)  # [op2967] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 16(s7)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, s7, a4  # [op2968] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul s6, s6, a2  # [op2969] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s6, s7, s6  # [op2970] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul s7, s7, a3  # [op2971] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s6, s6, s7  # [op2972] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 8  # [op2973] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse32.v v5, 0(s6), v0.t  # [op2975] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s6, 3  # [op2976] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 200(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s6, s7, s6  # [op2977] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt s7, s6, t0  # [op2978] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t4, t0, t4  # [op2979] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub s7, t1, s7  # [op2980] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
and s7, t4, s7  # [op2981] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
addiw s7, s7, 0  # [op2982] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op2983] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv.v.x v5, s7  # [op2985] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmslt.vv v5, v1, v5  # [op2986] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v5  # [op2987] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 96  # [op2988] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, t4, s7  # [op2989] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op2990] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vle32.v v5, 0(s7)  # [op2992] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 16(s7)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, s7, a4  # [op2993] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul s6, s6, a2  # [op2994] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s6, s7, s6  # [op2995] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul s7, s7, a3  # [op2996] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s6, s6, s7  # [op2997] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 8  # [op2998] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse32.v v5, 0(s6), v0.t  # [op3000] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s6, 200(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s6, s6, a3  # [op3001] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt s7, s6, t0  # [op3002] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t4, t0, t4  # [op3003] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub s7, t1, s7  # [op3004] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
and s7, t4, s7  # [op3005] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
addiw s7, s7, 0  # [op3006] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op3007] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv.v.x v5, s7  # [op3009] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmslt.vv v5, v1, v5  # [op3010] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v5  # [op3011] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 128  # [op3012] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, t4, s7  # [op3013] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op3014] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vle32.v v5, 0(s7)  # [op3016] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 16(s7)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, s7, a4  # [op3017] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul s6, s6, a2  # [op3018] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s6, s7, s6  # [op3019] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul s7, s7, a3  # [op3020] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s6, s6, s7  # [op3021] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 8  # [op3022] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse32.v v5, 0(s6), v0.t  # [op3024] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s6, 5  # [op3025] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 200(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s6, s7, s6  # [op3026] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt s7, s6, t0  # [op3027] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t4, t0, t4  # [op3028] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub s7, t1, s7  # [op3029] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
and s7, t4, s7  # [op3030] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
addiw s7, s7, 0  # [op3031] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op3032] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv.v.x v5, s7  # [op3034] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmslt.vv v5, v1, v5  # [op3035] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v5  # [op3036] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 160  # [op3037] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, t4, s7  # [op3038] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op3039] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vle32.v v5, 0(s7)  # [op3041] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 16(s7)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, s7, a4  # [op3042] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul s6, s6, a2  # [op3043] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s6, s7, s6  # [op3044] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul s7, s7, a3  # [op3045] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s6, s6, s7  # [op3046] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 8  # [op3047] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse32.v v5, 0(s6), v0.t  # [op3049] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s6, 6  # [op3050] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 200(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s6, s7, s6  # [op3051] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt s7, s6, t0  # [op3052] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t4, t0, t4  # [op3053] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub s7, t1, s7  # [op3054] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
and s7, t4, s7  # [op3055] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
addiw s7, s7, 0  # [op3056] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op3057] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv.v.x v5, s7  # [op3059] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmslt.vv v5, v1, v5  # [op3060] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v5  # [op3061] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 192  # [op3062] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, t4, s7  # [op3063] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op3064] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vle32.v v5, 0(s7)  # [op3066] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 16(s7)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, s7, a4  # [op3067] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul s6, s6, a2  # [op3068] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s6, s7, s6  # [op3069] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul s7, s7, a3  # [op3070] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s6, s6, s7  # [op3071] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 8  # [op3072] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse32.v v5, 0(s6), v0.t  # [op3074] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s6, 7  # [op3075] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 200(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s6, s7, s6  # [op3076] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt s7, s6, t0  # [op3077] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t0, t0, t4  # [op3078] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t1, t1, s7  # [op3079] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
and t0, t0, t1  # [op3080] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
addiw t0, t0, 0  # [op3081] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t1, 8  # [op3082] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv.v.x v5, t0  # [op3084] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmslt.vv v5, v1, v5  # [op3085] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v5  # [op3086] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t0, 224  # [op3087] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t1, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add t0, t1, t0  # [op3088] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t1, 8  # [op3089] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vle32.v v5, 0(t0)  # [op3091] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t0, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t0, 16(t0)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add t0, t0, a4  # [op3092] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul t1, s6, a2  # [op3093] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add t0, t0, t1  # [op3094] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t1, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul t1, t1, a3  # [op3095] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add t0, t0, t1  # [op3096] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t1, 8  # [op3097] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse32.v v5, 0(t0), v0.t  # [op3099] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add t0, a6, a5  # [op3100] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mv a6, t0  # [op3101] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
j .Lmtile26.head  # [op3101] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
.Ltaf28.then:  # block taf28.then
li t1, 8  # [op3102] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vsetvli t1, t1, e16, m1, ta,ma  # [op3103] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t1, 14656  # [op3104] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld a2, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld a2, 16(a2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a2, a2, t1  # [op3105] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t1, 64  # [op3106] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld a3, 200(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul a3, a3, t1  # [op3107] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a2, a2, a3  # [op3108] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a3, 2  # [op3109] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul a3, t0, a3  # [op3110] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a2, a2, a3  # [op3111] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vle16.v v5, 0(a2)  # [op3112] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(s1)  # [op3113] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a3, a2, t1  # [op3114] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a2, 16  # [op3115] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a4, s1, a2  # [op3116] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vle16.v v5, 0(a3)  # [op3117] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(a4)  # [op3118] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a3, a3, t1  # [op3119] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a4, a4, a2  # [op3120] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vle16.v v5, 0(a3)  # [op3121] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(a4)  # [op3122] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a3, a3, t1  # [op3123] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a4, a4, a2  # [op3124] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vle16.v v5, 0(a3)  # [op3125] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(a4)  # [op3126] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a3, a3, t1  # [op3127] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a4, a4, a2  # [op3128] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vle16.v v5, 0(a3)  # [op3129] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(a4)  # [op3130] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a3, a3, t1  # [op3131] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a4, a4, a2  # [op3132] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vle16.v v5, 0(a3)  # [op3133] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(a4)  # [op3134] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a3, a3, t1  # [op3135] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a4, a4, a2  # [op3136] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vle16.v v5, 0(a3)  # [op3137] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(a4)  # [op3138] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add t1, a3, t1  # [op3139] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a2, a4, a2  # [op3140] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vle16.v v5, 0(t1)  # [op3141] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(a2)  # [op3142] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
j .Ltaf28.join  # [op3143] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
.Ltaf28.else:  # block taf28.else
ld t1, 200(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a2, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a4, t1, a2  # [op3145] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a2, 16  # [op3146] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt a3, a4, a2  # [op3147] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t1, 8  # [op3148] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld a5, 192(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt a5, a5, t1  # [op3149] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub a5, s7, a5  # [op3150] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 192(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub s7, t1, s7  # [op3151] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
and a5, s7, a5  # [op3152] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 192(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a5, s7, a5  # [op3153] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub a3, s7, a3  # [op3154] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
and a3, a5, a3  # [op3155] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
addiw a3, a3, 0  # [op3156] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a5, 8  # [op3157] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vsetvli a5, a5, e32, m1, ta,ma  # [op3158] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv.v.x v5, a3  # [op3159] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmslt.vv v5, v2, v5  # [op3160] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v5  # [op3161] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a5, 14656  # [op3162] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld a3, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld a3, 16(a3)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, a3, a5  # [op3163] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a3, 64  # [op3164] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul a4, a4, a3  # [op3165] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, s7, a4  # [op3166] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a4, 2  # [op3167] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul t4, t0, a4  # [op3168] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, s7, t4  # [op3169] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op3170] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vsetvli t4, t4, e16, m1, ta,ma  # [op3171] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vle16.v v5, 0(s7), v0.t  # [op3172] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmerge.vvm v5, v3, v5, v0  # [op3173] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, s1, s7  # [op3174] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op3175] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(s7)  # [op3177] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 1  # [op3178] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 200(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, t4, s7  # [op3179] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt t4, s7, a2  # [op3180] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t5, 192(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt t5, t5, t1  # [op3181] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t6, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t5, t6, t5  # [op3182] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t6, 192(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t6, t1, t6  # [op3183] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
and t5, t6, t5  # [op3184] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t6, 192(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add t5, t6, t5  # [op3185] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t6, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t4, t6, t4  # [op3186] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
and t4, t5, t4  # [op3187] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
addiw t4, t4, 0  # [op3188] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t5, 8  # [op3189] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vsetvli t5, t5, e32, m1, ta,ma  # [op3190] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv.v.x v5, t4  # [op3191] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmslt.vv v5, v2, v5  # [op3192] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v5  # [op3193] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 16(t4)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add t4, t4, a5  # [op3194] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul s7, s7, a3  # [op3195] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, t4, s7  # [op3196] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul t4, t0, a4  # [op3197] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, s7, t4  # [op3198] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op3199] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vsetvli t4, t4, e16, m1, ta,ma  # [op3200] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vle16.v v5, 0(s7), v0.t  # [op3201] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmerge.vvm v5, v3, v5, v0  # [op3202] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, s1, a2  # [op3203] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op3204] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(s7)  # [op3206] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld s7, 200(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, s7, a4  # [op3207] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt t4, s7, a2  # [op3208] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t5, 192(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt t5, t5, t1  # [op3209] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
    # [peephole-li] [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t5, t6, t5  # [op3210] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t6, 192(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t6, t1, t6  # [op3211] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
and t5, t6, t5  # [op3212] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t6, 192(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add t5, t6, t5  # [op3213] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t6, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t4, t6, t4  # [op3214] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
and t4, t5, t4  # [op3215] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
addiw t4, t4, 0  # [op3216] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t5, 8  # [op3217] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vsetvli t5, t5, e32, m1, ta,ma  # [op3218] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv.v.x v5, t4  # [op3219] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmslt.vv v5, v2, v5  # [op3220] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v5  # [op3221] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 16(t4)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add t4, t4, a5  # [op3222] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul s7, s7, a3  # [op3223] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, t4, s7  # [op3224] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul t4, t0, a4  # [op3225] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, s7, t4  # [op3226] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op3227] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vsetvli t4, t4, e16, m1, ta,ma  # [op3228] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vle16.v v5, 0(s7), v0.t  # [op3229] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmerge.vvm v5, v3, v5, v0  # [op3230] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 32  # [op3231] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, s1, s7  # [op3232] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op3233] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(s7)  # [op3235] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 3  # [op3236] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 200(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, t4, s7  # [op3237] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt t4, s7, a2  # [op3238] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t5, 192(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt t5, t5, t1  # [op3239] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
    # [peephole-li] [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t5, t6, t5  # [op3240] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t6, 192(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t6, t1, t6  # [op3241] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
and t5, t6, t5  # [op3242] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t6, 192(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add t5, t6, t5  # [op3243] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t6, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t4, t6, t4  # [op3244] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
and t4, t5, t4  # [op3245] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
addiw t4, t4, 0  # [op3246] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t5, 8  # [op3247] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vsetvli t5, t5, e32, m1, ta,ma  # [op3248] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv.v.x v5, t4  # [op3249] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmslt.vv v5, v2, v5  # [op3250] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v5  # [op3251] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 16(t4)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add t4, t4, a5  # [op3252] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul s7, s7, a3  # [op3253] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, t4, s7  # [op3254] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul t4, t0, a4  # [op3255] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, s7, t4  # [op3256] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op3257] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vsetvli t4, t4, e16, m1, ta,ma  # [op3258] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vle16.v v5, 0(s7), v0.t  # [op3259] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmerge.vvm v5, v3, v5, v0  # [op3260] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 48  # [op3261] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, s1, s7  # [op3262] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op3263] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(s7)  # [op3265] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 4  # [op3266] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 200(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, t4, s7  # [op3267] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt t4, s7, a2  # [op3268] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t5, 192(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt t5, t5, t1  # [op3269] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
    # [peephole-li] [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t5, t6, t5  # [op3270] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t6, 192(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t6, t1, t6  # [op3271] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
and t5, t6, t5  # [op3272] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t6, 192(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add t5, t6, t5  # [op3273] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t6, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t4, t6, t4  # [op3274] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
and t4, t5, t4  # [op3275] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
addiw t4, t4, 0  # [op3276] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t5, 8  # [op3277] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vsetvli t5, t5, e32, m1, ta,ma  # [op3278] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv.v.x v5, t4  # [op3279] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmslt.vv v5, v2, v5  # [op3280] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v5  # [op3281] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 16(t4)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add t4, t4, a5  # [op3282] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul s7, s7, a3  # [op3283] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, t4, s7  # [op3284] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul t4, t0, a4  # [op3285] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, s7, t4  # [op3286] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op3287] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vsetvli t4, t4, e16, m1, ta,ma  # [op3288] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vle16.v v5, 0(s7), v0.t  # [op3289] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmerge.vvm v5, v3, v5, v0  # [op3290] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, s1, a3  # [op3291] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op3292] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(s7)  # [op3294] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 5  # [op3295] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 200(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, t4, s7  # [op3296] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt t4, s7, a2  # [op3297] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t5, 192(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt t5, t5, t1  # [op3298] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
    # [peephole-li] [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t5, t6, t5  # [op3299] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t6, 192(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t6, t1, t6  # [op3300] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
and t5, t6, t5  # [op3301] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t6, 192(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add t5, t6, t5  # [op3302] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t6, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t4, t6, t4  # [op3303] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
and t4, t5, t4  # [op3304] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
addiw t4, t4, 0  # [op3305] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t5, 8  # [op3306] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vsetvli t5, t5, e32, m1, ta,ma  # [op3307] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv.v.x v5, t4  # [op3308] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmslt.vv v5, v2, v5  # [op3309] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v5  # [op3310] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 16(t4)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add t4, t4, a5  # [op3311] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul s7, s7, a3  # [op3312] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, t4, s7  # [op3313] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul t4, t0, a4  # [op3314] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, s7, t4  # [op3315] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op3316] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vsetvli t4, t4, e16, m1, ta,ma  # [op3317] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vle16.v v5, 0(s7), v0.t  # [op3318] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmerge.vvm v5, v3, v5, v0  # [op3319] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 80  # [op3320] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, s1, s7  # [op3321] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op3322] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(s7)  # [op3324] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 6  # [op3325] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 200(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, t4, s7  # [op3326] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt t4, s7, a2  # [op3327] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t5, 192(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt t5, t5, t1  # [op3328] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
    # [peephole-li] [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t5, t6, t5  # [op3329] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t6, 192(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t6, t1, t6  # [op3330] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
and t5, t6, t5  # [op3331] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t6, 192(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add t5, t6, t5  # [op3332] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t6, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t4, t6, t4  # [op3333] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
and t4, t5, t4  # [op3334] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
addiw t4, t4, 0  # [op3335] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t5, 8  # [op3336] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vsetvli t5, t5, e32, m1, ta,ma  # [op3337] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv.v.x v5, t4  # [op3338] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmslt.vv v5, v2, v5  # [op3339] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v5  # [op3340] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 16(t4)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add t4, t4, a5  # [op3341] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul s7, s7, a3  # [op3342] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, t4, s7  # [op3343] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul t4, t0, a4  # [op3344] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, s7, t4  # [op3345] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op3346] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vsetvli t4, t4, e16, m1, ta,ma  # [op3347] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vle16.v v5, 0(s7), v0.t  # [op3348] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmerge.vvm v5, v3, v5, v0  # [op3349] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 96  # [op3350] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, s1, s7  # [op3351] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t4, 8  # [op3352] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(s7)  # [op3354] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 7  # [op3355] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 200(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add s7, t4, s7  # [op3356] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt a2, s7, a2  # [op3357] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 192(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt t4, t4, t1  # [op3358] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t5, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t4, t5, t4  # [op3359] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t5, 192(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t1, t1, t5  # [op3360] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
and t1, t1, t4  # [op3361] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 192(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add t1, t4, t1  # [op3362] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t4, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub a2, t4, a2  # [op3363] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
and t1, t1, a2  # [op3364] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
addiw t1, t1, 0  # [op3365] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a2, 8  # [op3366] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vsetvli a2, a2, e32, m1, ta,ma  # [op3367] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv.v.x v5, t1  # [op3368] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmslt.vv v5, v2, v5  # [op3369] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmv1r.v v0, v5  # [op3370] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add t1, t1, a5  # [op3371] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul a2, s7, a3  # [op3372] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add t1, t1, a2  # [op3373] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul a2, t0, a4  # [op3374] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add t1, t1, a2  # [op3375] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a2, 8  # [op3376] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vsetvli a2, a2, e16, m1, ta,ma  # [op3377] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vle16.v v5, 0(t1), v0.t  # [op3378] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vmerge.vvm v5, v3, v5, v0  # [op3379] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t1, 112  # [op3380] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add t1, s1, t1  # [op3381] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a2, 8  # [op3382] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(t1)  # [op3384] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
j .Ltaf28.join  # [op3385] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
.Ltaf28.join:  # block taf28.join
li t1, 8  # [op3386] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld a2, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a2, a2, t1  # [op3387] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a3, 17  # [op3388] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt a2, a2, a3  # [op3389] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a3, 1  # [op3390] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld a4, 192(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a3, a4, a3  # [op3391] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt t1, t1, a3  # [op3392] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
and t1, a2, t1  # [op3393] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
bne t1, zero, .Lbrc3394_true  # [op3394] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
j .Lpbf29.else  # [op3394] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
.Lbrc3394_true:  # [op3394] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
j .Lpbf29.then  # [op3394] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
.Lpbf29.then:  # block pbf29.then
li t1, 8  # [op3395] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vsetvli t1, t1, e16, m1, ta,ma  # [op3396] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t1, 32  # [op3397] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a2, 29056  # [op3398] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld a3, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld a3, 16(a3)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a2, a3, a2  # [op3399] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul a3, t0, t1  # [op3400] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a3, a2, a3  # [op3401] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a2, 2  # [op3402] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld a4, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul a4, a4, a2  # [op3403] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a3, a3, a4  # [op3404] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vlse16.v v5, 0(a3), t1  # [op3405] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(a1)  # [op3406] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a4, a3, a2  # [op3407] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a3, 16  # [op3408] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a5, a1, a3  # [op3409] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vlse16.v v5, 0(a4), t1  # [op3410] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(a5)  # [op3411] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a4, a4, a2  # [op3412] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a5, a5, a3  # [op3413] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vlse16.v v5, 0(a4), t1  # [op3414] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(a5)  # [op3415] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a4, a4, a2  # [op3416] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a5, a5, a3  # [op3417] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vlse16.v v5, 0(a4), t1  # [op3418] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(a5)  # [op3419] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a4, a4, a2  # [op3420] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a5, a5, a3  # [op3421] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vlse16.v v5, 0(a4), t1  # [op3422] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(a5)  # [op3423] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a4, a4, a2  # [op3424] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a5, a5, a3  # [op3425] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vlse16.v v5, 0(a4), t1  # [op3426] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(a5)  # [op3427] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a4, a4, a2  # [op3428] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a5, a5, a3  # [op3429] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vlse16.v v5, 0(a4), t1  # [op3430] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(a5)  # [op3431] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a2, a4, a2  # [op3432] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a3, a5, a3  # [op3433] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vlse16.v v5, 0(a2), t1  # [op3434] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(a3)  # [op3435] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
j .Lpbf29.join  # [op3436] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
.Lpbf29.else:  # block pbf29.else
li t1, 8  # [op3437] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vsetvli t1, t1, e16, m1, ta,ma  # [op3438] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t1, 0  # [op3439] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a2, a1, t1  # [op3440] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse16.v v4, 0(a2)  # [op3441] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a2, 16  # [op3442] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a2, a1, a2  # [op3443] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse16.v v4, 0(a2)  # [op3444] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a2, 32  # [op3445] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a2, a1, a2  # [op3446] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse16.v v4, 0(a2)  # [op3447] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a2, 48  # [op3448] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a2, a1, a2  # [op3449] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse16.v v4, 0(a2)  # [op3450] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a2, 64  # [op3451] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a2, a1, a2  # [op3452] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse16.v v4, 0(a2)  # [op3453] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a2, 80  # [op3454] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a2, a1, a2  # [op3455] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse16.v v4, 0(a2)  # [op3456] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a2, 96  # [op3457] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a2, a1, a2  # [op3458] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse16.v v4, 0(a2)  # [op3459] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a2, 112  # [op3460] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a2, a1, a2  # [op3461] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse16.v v4, 0(a2)  # [op3462] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li s7, 8  # [op3463] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
j .Lpb30.head  # [op3464] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
.Lpb30.head:  # block pb30.head
slt a2, t1, s7  # [op3465] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
bne a2, zero, .Lbrc3466_true  # [op3466] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
j .Lpb30.exit  # [op3466] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
.Lbrc3466_true:  # [op3466] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
j .Lpb30.body  # [op3466] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
.Lpb30.body:  # block pb30.body
ld a2, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a2, a2, t1  # [op3467] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a3, 16  # [op3468] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt t4, a2, a3  # [op3469] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a4, 8  # [op3470] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld a5, 192(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
slt t5, a5, a4  # [op3471] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a5, 0  # [op3472] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub t5, a5, t5  # [op3473] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t6, 192(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub a4, a4, t6  # [op3474] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
and a4, a4, t5  # [op3475] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t5, 192(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a4, t5, a4  # [op3476] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
sub a5, a5, t4  # [op3477] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
and a5, a4, a5  # [op3478] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a4, 29056  # [op3479] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
ld t4, 16(t4)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add t4, t4, a4  # [op3480] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a4, 32  # [op3481] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul t5, t0, a4  # [op3482] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add t4, t4, t5  # [op3483] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t5, 2  # [op3484] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul a2, a2, t5  # [op3485] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a2, t4, a2  # [op3486] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
mul a3, t1, a3  # [op3487] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add a3, a1, a3  # [op3488] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
addiw a5, a5, 0  # [op3489] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vsetvli a5, a5, e16, m1, ta,ma  # [op3490] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vlse16.v v5, 0(a2), a4  # [op3491] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vse16.v v5, 0(a3)  # [op3492] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li a2, 1  # [op3493] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add t1, t1, a2  # [op3494] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
j .Lpb30.head  # [op3495] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
.Lpb30.exit:  # block pb30.exit
j .Lpbf29.join  # [op3496] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
.Lpbf29.join:  # block pbf29.join
li t1, 64  # [op3497] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vsetvli t1, t1, e16, m1, ta,ma  # [op3498] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vle16.v v5, 0(s1)  # [op3499] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vle16.v v8, 0(a1)  # [op3500] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
vsetvli x0, zero, e16, m1, ta, ma
    smt.vfwmadot v6, v5, v8  # [op3501] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
li t1, 8  # [op3502] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
add t0, t0, t1  # [op3503] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
j .Lmk27.head  # [op3504] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:35:15
.Lmcarry31.head:  # block mcarry31.head
slt a4, t0, a2  # [op3505] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
bne a4, zero, .Lbrc3506_true  # [op3506] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
j .Lmcarry31.exit  # [op3506] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
.Lbrc3506_true:  # [op3506] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
j .Lmcarry31.body  # [op3506] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
.Lmcarry31.body:  # block mcarry31.body
ld a4, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
ld a4, 16(a4)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
add a4, a4, s1  # [op3507] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
ld a5, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
ld a5, 16(a5)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
add a5, a5, a1  # [op3508] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
li a6, 32  # [op3509] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
vsetvli a6, a6, e32, m1, ta,ma  # [op3510] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
vid.v v1  # [op3511] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
vadd.vx v1, v1, t0  # [op3512] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
li a6, 32  # [op3513] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
vwadd.vx v2, v1, x0  # [op3515] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
    # [peephole-li] [op3516] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
vsetvli a6, a6, e64, m2, ta,ma  # [op3517] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
li a6, 4  # [op3518] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
vmul.vx v2, v2, a6  # [op3519] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
li a6, 32  # [op3520] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
vsetvli a6, a6, e32, m1, ta,ma  # [op3521] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
vluxei64.v v1, (a4), v2  # [op3522] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
vsuxei64.v v1, (a5), v2  # [op3523] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
li a4, 16  # [op3524] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
vsetvli a4, a4, e32, m1, ta,ma  # [op3525] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
addw t0, t0, a3  # [op3526] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
j .Lmcarry31.head  # [op3527] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
.Lmcarry31.exit:  # block mcarry31.exit
mv a7, t1  # [op3528] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
j .Lmloop15.head  # [op3528] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:29:5
.Lchunk32_head:  # block chunk32_head
li s1, 16  # [op3529] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op3530] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc3531_true  # [op3531] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op3531] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op3531] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk32_exit  # [op3531] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lbrc3531_true:  # [op3531] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk32_body  # [op3531] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk32_exit:  # block chunk32_exit
li t1, 0  # [op3532] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
sd t0, 96(sp)  # [op3533] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t1  # [op3533] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld t1, 96(sp)  # [op3533] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk33_head  # [op3533] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk32_body:  # block chunk32_body
li s1, 16  # [op3534] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op3535] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
li s1, 16  # [op3536] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:22
ld s1, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:22
vmv.v.x v1, s1  # [op3538] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:22
vid.v v2  # [op3539] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:22
vadd.vx v2, v2, t0  # [op3540] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:22
li s1, 16  # [op3541] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:22
vwadd.vx v4, v2, x0  # [op3543] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:22
    # [peephole-li] [op3544] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:22
vsetvli s1, s1, e64, m2, ta,ma  # [op3545] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:22
li s1, 4  # [op3546] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:22
vmul.vx v2, v4, s1  # [op3547] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:22
li s1, 0  # [op3548] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:22
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:22
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:22
add s1, a1, s1  # [op3549] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:22
li a1, 16  # [op3550] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:22
vsetvli a1, a1, e32, m1, ta,ma  # [op3551] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:22
vluxei64.v v4, (s1), v2  # [op3552] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:22
li s1, 16  # [op3553] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:22
vmul.vv v1, v4, v1  # [op3555] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:22
vid.v v2  # [op3556] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:22
vadd.vx v2, v2, t0  # [op3557] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:22
    # [peephole-li] [op3558] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:22
vwadd.vx v4, v2, x0  # [op3560] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:22
    # [peephole-li] [op3561] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:22
vsetvli s1, s1, e64, m2, ta,ma  # [op3562] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:22
li s1, 4  # [op3563] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:22
vmul.vx v2, v4, s1  # [op3564] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:22
li s1, 31104  # [op3565] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:22
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:22
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:22
add s1, a1, s1  # [op3566] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:22
li a1, 16  # [op3567] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:22
vsetvli a1, a1, e32, m1, ta,ma  # [op3568] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:22
vsuxei64.v v1, (s1), v2  # [op3569] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:22
li s1, 16  # [op3570] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:22
    # [peephole-li] [op3572] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op3573] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op3574] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op3575] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op3576] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk32_head  # [op3578] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk33_head:  # block chunk33_head
li s1, 256  # [op3579] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
slt s1, t0, s1  # [op3580] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
bne s1, zero, .Lbrc3581_true  # [op3581] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t2  # [op3581] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk33_exit  # [op3581] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lbrc3581_true:  # [op3581] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk33_body  # [op3581] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk33_exit:  # block chunk33_exit
li t0, 0  # [op3582] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
j .Lstg34_head  # [op3583] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
.Lchunk33_body:  # block chunk33_body
li s1, 32  # [op3584] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
vsetvli s1, s1, e32, m1, ta,ma  # [op3585] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op3586] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:14
vid.v v1  # [op3588] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:14
vadd.vx v1, v1, t0  # [op3589] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:14
li s1, 16  # [op3590] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:14
vmv.v.x v2, s1  # [op3591] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:14
vdiv.vv v1, v1, v2  # [op3592] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:14
li s1, 32  # [op3593] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:14
vwadd.vx v2, v1, x0  # [op3595] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:14
    # [peephole-li] [op3596] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:14
vsetvli s1, s1, e64, m2, ta,ma  # [op3597] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:14
li s1, 8  # [op3598] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:14
vmul.vx v2, v2, s1  # [op3599] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:14
li s1, 31168  # [op3600] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:14
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:14
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:14
add s1, a1, s1  # [op3601] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:14
li a1, 32  # [op3602] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:14
vluxei64.v v4, (s1), v2  # [op3604] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:14
li s1, 32  # [op3605] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:14
vsetvli s1, s1, e32, m1, ta,ma  # [op3606] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:14
li s1, 32  # [op3607] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
add t1, t1, s1  # [op3608] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op3609] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
addw t0, t0, s1  # [op3610] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op3611] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk33_head  # [op3613] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lstg34_head:  # block stg34_head
li s1, 256  # [op3614] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
slt s1, t0, s1  # [op3615] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
bne s1, zero, .Lbrc3616_true  # [op3616] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
j .Lstg34_exit  # [op3616] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
.Lbrc3616_true:  # [op3616] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
j .Lstg34_body  # [op3616] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
.Lstg34_body:  # block stg34_body
li s1, 32  # [op3617] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vsetvli s1, s1, e32, m1, ta,ma  # [op3618] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vid.v v1  # [op3619] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vadd.vx v1, v1, t0  # [op3620] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
li s1, 16  # [op3621] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vmv.v.x v2, s1  # [op3622] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vdiv.vv v2, v1, v2  # [op3623] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op3624] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vmv.v.x v3, s1  # [op3625] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vrem.vv v2, v2, v3  # [op3626] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op3627] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vmv.v.x v3, s1  # [op3628] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vrem.vv v3, v1, v3  # [op3629] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
li s1, 32  # [op3630] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vwadd.vx v4, v2, x0  # [op3632] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op3633] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vsetvli s1, s1, e64, m2, ta,ma  # [op3634] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
li s1, 4  # [op3635] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vmul.vx v2, v4, s1  # [op3636] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
li s1, 6144  # [op3637] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
add s1, a1, s1  # [op3638] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
li a1, 32  # [op3639] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vsetvli a1, a1, e32, m1, ta,ma  # [op3640] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vluxei64.v v4, (s1), v2  # [op3641] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
li s1, 32  # [op3642] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vwadd.vx v2, v1, x0  # [op3644] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op3645] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vsetvli s1, s1, e64, m2, ta,ma  # [op3646] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
li s1, 4  # [op3647] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vmul.vx v2, v2, s1  # [op3648] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
li s1, 33344  # [op3649] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
add s1, a1, s1  # [op3650] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
li a1, 32  # [op3651] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vsetvli a1, a1, e32, m1, ta,ma  # [op3652] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vsuxei64.v v4, (s1), v2  # [op3653] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
li s1, 32  # [op3654] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
addw t0, t0, s1  # [op3655] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
j .Lstg34_head  # [op3656] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
.Lstg34_exit:  # block stg34_exit
li t0, 0  # [op3657] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
j .Lstg35_head  # [op3658] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
.Lstg35_head:  # block stg35_head
li s1, 256  # [op3659] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
slt s1, t0, s1  # [op3660] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
bne s1, zero, .Lbrc3661_true  # [op3661] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
j .Lstg35_exit  # [op3661] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
.Lbrc3661_true:  # [op3661] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
j .Lstg35_body  # [op3661] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
.Lstg35_body:  # block stg35_body
li s1, 32  # [op3662] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vsetvli s1, s1, e32, m1, ta,ma  # [op3663] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vid.v v1  # [op3664] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vadd.vx v1, v1, t0  # [op3665] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
li s1, 16  # [op3666] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vmv.v.x v2, s1  # [op3667] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vdiv.vv v2, v1, v2  # [op3668] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op3669] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vmv.v.x v3, s1  # [op3670] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vrem.vv v2, v2, v3  # [op3671] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op3672] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vmv.v.x v2, s1  # [op3673] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vrem.vv v2, v1, v2  # [op3674] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
li s1, 32  # [op3675] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vwadd.vx v4, v2, x0  # [op3677] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op3678] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vsetvli s1, s1, e64, m2, ta,ma  # [op3679] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
li s1, 4  # [op3680] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vmul.vx v2, v4, s1  # [op3681] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
li s1, 20800  # [op3682] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
add s1, a1, s1  # [op3683] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
li a1, 32  # [op3684] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vsetvli a1, a1, e32, m1, ta,ma  # [op3685] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vluxei64.v v4, (s1), v2  # [op3686] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
li s1, 32  # [op3687] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vwadd.vx v2, v1, x0  # [op3689] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op3690] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vsetvli s1, s1, e64, m2, ta,ma  # [op3691] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
li s1, 4  # [op3692] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vmul.vx v2, v2, s1  # [op3693] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
li s1, 34368  # [op3694] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
add s1, a1, s1  # [op3695] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
li a1, 32  # [op3696] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vsetvli a1, a1, e32, m1, ta,ma  # [op3697] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vsuxei64.v v4, (s1), v2  # [op3698] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
li s1, 32  # [op3699] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
addw t0, t0, s1  # [op3700] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
j .Lstg35_head  # [op3701] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
.Lstg35_exit:  # block stg35_exit
li t0, 0  # [op3702] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv s1, t1  # [op3703] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t1, t0  # [op3703] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk36_head  # [op3703] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk36_head:  # block chunk36_head
li t0, 256  # [op3704] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
slt t0, t1, t0  # [op3705] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
bne t0, zero, .Lbrc3706_true  # [op3706] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t1, t2  # [op3706] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, s1  # [op3706] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk36_exit  # [op3706] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lbrc3706_true:  # [op3706] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk36_body  # [op3706] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk36_exit:  # block chunk36_exit
mv t1, t0  # [op3707] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv t0, t2  # [op3707] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lprog_next  # [op3707] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lchunk36_body:  # block chunk36_body
li t0, 32  # [op3708] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
vsetvli t0, t0, e16, m1, ta,ma  # [op3709] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
li t0, 32  # [op3710] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vsetvli t0, t0, e32, m1, ta,ma  # [op3711] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vid.v v1  # [op3712] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vadd.vx v1, v1, t1  # [op3713] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
li t0, 32  # [op3714] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vwadd.vx v2, v1, x0  # [op3716] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op3717] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vsetvli t0, t0, e64, m2, ta,ma  # [op3718] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
li t0, 4  # [op3719] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vmul.vx v2, v2, t0  # [op3720] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
li t0, 33344  # [op3721] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
add t0, a1, t0  # [op3722] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
li a1, 32  # [op3723] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vsetvli a1, a1, e32, m1, ta,ma  # [op3724] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vluxei64.v v1, (t0), v2  # [op3725] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
li t0, 0  # [op3726] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vmv.v.x v2, t0  # [op3727] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vmsne.vv v1, v1, v2  # [op3728] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
li t0, 32  # [op3729] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vsetvli t0, t0, e16, m1, ta,ma  # [op3730] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
li t0, 32  # [op3731] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vsetvli t0, t0, e32, m1, ta,ma  # [op3732] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vid.v v2  # [op3733] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vadd.vx v2, v2, t1  # [op3734] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
li t0, 32  # [op3735] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vwadd.vx v4, v2, x0  # [op3737] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
    # [peephole-li] [op3738] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vsetvli t0, t0, e64, m2, ta,ma  # [op3739] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
li t0, 4  # [op3740] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vmul.vx v2, v4, t0  # [op3741] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
li t0, 34368  # [op3742] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
add t0, a1, t0  # [op3743] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
li a1, 32  # [op3744] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vsetvli a1, a1, e32, m1, ta,ma  # [op3745] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vluxei64.v v4, (t0), v2  # [op3746] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
li t0, 0  # [op3747] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vmv.v.x v2, t0  # [op3748] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vmsne.vv v2, v4, v2  # [op3749] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
li t0, 32  # [op3750] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vsetvli t0, t0, e16, m1, ta,ma  # [op3751] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
vmand.mm v3, v1, v2  # [op3752] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:37:19
li t0, 32  # [op3753] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e32, m1, ta,ma  # [op3754] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vid.v v1  # [op3755] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vadd.vx v1, v1, t1  # [op3756] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op3757] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vwadd.vx v4, v1, x0  # [op3759] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
    # [peephole-li] [op3760] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e64, m2, ta,ma  # [op3761] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li t0, 4  # [op3762] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmul.vx v4, v4, t0  # [op3763] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li t0, 256  # [op3764] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add t0, a1, t0  # [op3765] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a1, 32  # [op3766] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli a1, a1, e32, m1, ta,ma  # [op3767] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vluxei64.v v1, (t0), v4  # [op3768] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op3769] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e16, m1, ta,ma  # [op3770] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op3771] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e32, m1, ta,ma  # [op3772] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.v.v v4, v1  # [op3773] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op3774] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e16, m1, ta,ma  # [op3775] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vfncvt.f.f.w v2, v4  # [op3776] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op3777] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e32, m1, ta,ma  # [op3778] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vid.v v1  # [op3779] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vadd.vx v1, v1, t1  # [op3780] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li t0, 16  # [op3781] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.v.x v4, t0  # [op3782] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vdiv.vv v1, v1, v4  # [op3783] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op3784] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vwadd.vx v4, v1, x0  # [op3786] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
    # [peephole-li] [op3787] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e64, m2, ta,ma  # [op3788] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li t0, 4  # [op3789] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmul.vx v4, v4, t0  # [op3790] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li t0, 31104  # [op3791] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add t0, a1, t0  # [op3792] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a1, 32  # [op3793] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli a1, a1, e32, m1, ta,ma  # [op3794] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vluxei64.v v1, (t0), v4  # [op3795] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op3796] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e16, m1, ta,ma  # [op3797] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op3798] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e32, m1, ta,ma  # [op3799] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vid.v v4  # [op3800] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vadd.vx v4, v4, t1  # [op3801] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li t0, 16  # [op3802] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.v.x v5, t0  # [op3803] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vrem.vv v4, v4, v5  # [op3804] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op3805] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vwadd.vx v6, v4, x0  # [op3807] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
    # [peephole-li] [op3808] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e64, m2, ta,ma  # [op3809] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li t0, 4  # [op3810] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmul.vx v4, v6, t0  # [op3811] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li t0, 64  # [op3812] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add t0, a1, t0  # [op3813] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a1, 32  # [op3814] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli a1, a1, e32, m1, ta,ma  # [op3815] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vluxei64.v v6, (t0), v4  # [op3816] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op3817] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e16, m1, ta,ma  # [op3818] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op3819] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e32, m1, ta,ma  # [op3820] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vadd.vv v6, v1, v6  # [op3821] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op3822] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e16, m1, ta,ma  # [op3823] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op3824] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e32, m1, ta,ma  # [op3825] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li t0, 0  # [op3826] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.v.x v1, t0  # [op3827] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li t0, 1  # [op3828] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.v.x v4, t0  # [op3829] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv1r.v v0, v3  # [op3830] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmerge.vvm v1, v1, v4, v0  # [op3831] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op3832] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vwadd.vx v4, v6, x0  # [op3834] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
    # [peephole-li] [op3835] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e64, m2, ta,ma  # [op3836] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li t0, 2  # [op3837] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmul.vx v4, v4, t0  # [op3838] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op3839] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e16, m1, ta,ma  # [op3840] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a1, 0  # [op3841] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li t0, 16  # [op3842] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e64, m2, ta,ma  # [op3843] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.x.s t0, v4  # [op3844] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vid.v v8  # [op3845] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 2  # [op3846] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmul.vx v8, v8, a2  # [op3847] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vadd.vx v8, v8, t0  # [op3848] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmsne.vv v7, v4, v8  # [op3849] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 16  # [op3850] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli a2, a2, e32, m1, ta,ma  # [op3851] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 0  # [op3852] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.v.x v8, a2  # [op3853] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmsne.vv v8, v1, v8  # [op3854] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmand.mm v7, v7, v8  # [op3855] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vcpop.m a2, v7  # [op3856] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add a1, a1, a2  # [op3857] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add a2, s4, t0  # [op3858] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li t0, 16  # [op3859] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e64, m2, ta,ma  # [op3860] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vid.v v8  # [op3861] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li t0, 16  # [op3862] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vadd.vx v10, v8, t0  # [op3863] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vrgather.vv v8, v4, v10  # [op3864] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.x.s t0, v8  # [op3865] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vid.v v4  # [op3866] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a3, 2  # [op3867] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmul.vx v4, v4, a3  # [op3868] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vadd.vx v4, v4, t0  # [op3869] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmsne.vv v4, v8, v4  # [op3870] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a3, 16  # [op3871] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli a3, a3, e32, m1, ta,ma  # [op3872] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vid.v v5  # [op3873] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a3, 16  # [op3874] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vadd.vx v5, v5, a3  # [op3875] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vrgather.vv v7, v1, v5  # [op3876] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a3, 0  # [op3877] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.v.x v5, a3  # [op3878] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmsne.vv v5, v7, v5  # [op3879] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmand.mm v4, v4, v5  # [op3880] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vcpop.m a3, v4  # [op3881] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add a1, a1, a3  # [op3882] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add t0, s4, t0  # [op3883] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
bne a1, zero, .Lbrc3884_true  # [op3884] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
j .Lngs.t3  # [op3884] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
.Lbrc3884_true:  # [op3884] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
j .Lngs.e3  # [op3884] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
.Lngs.t3:  # block ngs.t3
li a1, 16  # [op3885] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli a1, a1, e16, m1, ta,ma  # [op3886] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a1, 16  # [op3887] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli a1, a1, e32, m1, ta,ma  # [op3888] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a1, 0  # [op3889] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.v.x v3, a1  # [op3890] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmsne.vv v3, v1, v3  # [op3891] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a1, 16  # [op3892] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli a1, a1, e16, m1, ta,ma  # [op3893] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv1r.v v0, v3  # [op3894] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vse16.v v2, 0(a2), v0.t  # [op3895] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vid.v v3  # [op3896] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a1, 16  # [op3897] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vadd.vx v3, v3, a1  # [op3898] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vrgather.vv v4, v2, v3  # [op3899] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
    # [peephole-li] [op3900] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli a1, a1, e32, m1, ta,ma  # [op3901] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vid.v v2  # [op3902] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a1, 16  # [op3903] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vadd.vx v2, v2, a1  # [op3904] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vrgather.vv v3, v1, v2  # [op3905] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a1, 0  # [op3906] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.v.x v1, a1  # [op3907] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmsne.vv v1, v3, v1  # [op3908] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a1, 16  # [op3909] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli a1, a1, e16, m1, ta,ma  # [op3910] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv1r.v v0, v1  # [op3911] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vse16.v v4, 0(t0), v0.t  # [op3912] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
j .Lngs.j3  # [op3913] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
.Lngs.e3:  # block ngs.e3
li t0, 32  # [op3914] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e32, m1, ta,ma  # [op3915] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vwadd.vx v4, v6, x0  # [op3916] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op3917] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e64, m2, ta,ma  # [op3918] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li t0, 2  # [op3919] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmul.vx v4, v4, t0  # [op3920] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op3921] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e16, m1, ta,ma  # [op3922] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li t0, 35904  # [op3923] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add t0, a1, t0  # [op3924] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a1, 128  # [op3925] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add a1, t0, a1  # [op3926] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 32  # [op3927] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vse16.v v2, 0(t0)  # [op3929] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
    # [peephole-li] [op3930] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli a2, a2, e32, m1, ta,ma  # [op3931] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 0  # [op3932] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.v.x v1, a2  # [op3933] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 1  # [op3934] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.v.x v2, a2  # [op3935] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv1r.v v0, v3  # [op3936] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmerge.vvm v1, v1, v2, v0  # [op3937] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 32  # [op3938] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli a2, a2, e64, m2, ta,ma  # [op3939] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vadd.vx v4, v4, s4  # [op3940] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 32  # [op3941] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli a2, a2, e32, m1, ta,ma  # [op3942] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 0  # [op3943] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.v.x v2, a2  # [op3944] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmsne.vv v1, v1, v2  # [op3945] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv1r.v v0, v1  # [op3946] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 32  # [op3947] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli a2, a2, e64, m2, ta,ma  # [op3948] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 0  # [op3949] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.v.x v6, a2  # [op3950] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.v.x v2, a1  # [op3951] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsub.vv v4, v4, v2  # [op3952] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmerge.vvm v4, v6, v4, v0  # [op3953] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vadd.vv v2, v2, v4  # [op3954] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a1, 32  # [op3955] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli a1, a1, e16, m1, ta,ma  # [op3956] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a1, 32  # [op3957] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli a1, a1, e64, m2, ta,ma  # [op3958] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3959] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
    # [peephole-li] [op3960] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3961] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3962] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3963] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3964] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3965] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 2  # [op3966] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3967] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3968] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3969] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3970] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3971] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 4  # [op3972] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3973] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3974] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3975] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3976] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3977] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 6  # [op3978] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3979] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3980] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3981] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3982] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3983] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 8  # [op3984] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3985] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3986] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3987] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3988] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3989] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 10  # [op3990] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3991] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3992] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3993] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op3994] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op3995] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 12  # [op3996] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op3997] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op3998] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op3999] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op4000] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op4001] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 14  # [op4002] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op4003] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op4004] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op4005] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op4006] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op4007] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 16  # [op4008] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op4009] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op4010] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op4011] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op4012] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op4013] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 18  # [op4014] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op4015] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op4016] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op4017] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op4018] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op4019] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 20  # [op4020] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op4021] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op4022] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op4023] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op4024] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op4025] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 22  # [op4026] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op4027] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op4028] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op4029] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op4030] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op4031] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 24  # [op4032] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op4033] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op4034] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op4035] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op4036] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op4037] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 26  # [op4038] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op4039] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op4040] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op4041] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op4042] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op4043] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 28  # [op4044] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op4045] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op4046] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op4047] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op4048] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op4049] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 30  # [op4050] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op4051] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op4052] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op4053] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op4054] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op4055] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 32  # [op4056] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op4057] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op4058] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op4059] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op4060] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op4061] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 34  # [op4062] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op4063] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op4064] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op4065] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op4066] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op4067] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 36  # [op4068] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op4069] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op4070] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op4071] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op4072] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op4073] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 38  # [op4074] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op4075] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op4076] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op4077] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op4078] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op4079] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 40  # [op4080] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op4081] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op4082] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op4083] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op4084] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op4085] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 42  # [op4086] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op4087] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op4088] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op4089] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op4090] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op4091] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 44  # [op4092] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op4093] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op4094] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op4095] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op4096] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op4097] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 46  # [op4098] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op4099] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op4100] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op4101] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op4102] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op4103] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 48  # [op4104] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op4105] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op4106] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op4107] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op4108] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op4109] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 50  # [op4110] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op4111] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op4112] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op4113] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op4114] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op4115] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 52  # [op4116] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op4117] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op4118] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op4119] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op4120] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op4121] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 54  # [op4122] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op4123] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op4124] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op4125] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op4126] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op4127] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 56  # [op4128] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op4129] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op4130] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op4131] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op4132] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op4133] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 58  # [op4134] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op4135] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op4136] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op4137] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op4138] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op4139] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 60  # [op4140] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add a2, t0, a2  # [op4141] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
lhu a2, 0(a2)  # [op4142] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
sh a2, 0(a1)  # [op4143] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op4144] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vmv.x.s a1, v2  # [op4145] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li a2, 62  # [op4146] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
add t0, t0, a2  # [op4147] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
lhu t0, 0(t0)  # [op4148] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
sh t0, 0(a1)  # [op4149] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vslidedown.vi v2, v2, 1  # [op4150] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
j .Lngs.j3  # [op4151] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
.Lngs.j3:  # block ngs.j3
li t0, 32  # [op4152] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
vsetvli t0, t0, e16, m1, ta,ma  # [op4153] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:36:5
li t0, 32  # [op4154] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
add t0, s1, t0  # [op4155] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
li s1, 32  # [op4156] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
addw t1, t1, s1  # [op4157] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    # [peephole-li] [op4158] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
mv s1, t0  # [op4160] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lchunk36_head  # [op4160] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lprog_next:  # block prog_next
add t0, t0, s10  # [op4161] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
j .Lprog_head  # [op4162] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
.Lprog_exit:  # block prog_exit
ld t1, 144(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
sd t0, 0(t1)  # [op4163] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld ra, 0(sp)  # [op4164] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld s1, 8(sp)  # [op4164] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld s2, 16(sp)  # [op4164] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld s3, 24(sp)  # [op4164] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld s4, 32(sp)  # [op4164] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld s5, 40(sp)  # [op4164] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld s6, 48(sp)  # [op4164] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld s7, 56(sp)  # [op4164] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld s8, 64(sp)  # [op4164] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld s9, 72(sp)  # [op4164] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld s10, 80(sp)  # [op4164] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ld s11, 88(sp)  # [op4164] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
addi sp, sp, 208  # [op4164] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
ret  # [op4164] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/matmul.py:21:1
    .size operator_entry, .-operator_entry
    .section .note.GNU-stack,"",@progbits
