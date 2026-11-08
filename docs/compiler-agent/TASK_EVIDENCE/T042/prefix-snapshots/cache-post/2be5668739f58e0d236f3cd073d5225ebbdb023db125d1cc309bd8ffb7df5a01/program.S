# a100c emitted program: nanmedian_ascend_histogram_count_kernel
# source: home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py
# specialization identity: 9f77a7e1f4cf2351
# compiler revision: 676724339831a98d
# target model: a100-rvv1-vlen1024/1 (VLEN=1024, file=4096B)
# options: default
# argument layout: 09a73a5467bcb88f
# every instruction below traces to a selected MIR op: [opN] carries the source location
# passes: passes=default
    .text
    .globl operator_workspace_private
    .type operator_workspace_private, @function
operator_workspace_private:
    li a0, 4232
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
addi sp, sp, -112
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
mv a1, a0
.Lentry:  # block entry
ld t0, 0(a1)  # [op0] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
ld t1, 0(t0)  # [op1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
ld t0, 8(t0)  # [op2] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
ld s2, 24(a1)  # [op3] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
lwu t2, 40(a1)  # [op4] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
lwu s1, 44(a1)  # [op5] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
ld t0, 8(t0)  # [op6] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
addiw t0, t0, 0  # [op7] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
ld s3, 0(t1)  # [op8] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
ld s4, 56(t1)  # [op9] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
li a3, 3  # [op10] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
li a4, 1  # [op11] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
li t0, 1  # [op12] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
mul t0, t0, a3  # [op13] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
mul s5, t0, a4  # [op14] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
mv t0, t2  # [op15] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
mv s6, s1  # [op16] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
li t1, 0  # [op17] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
j .Lprog_head  # [op18] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
.Lprog_head:  # block prog_head
slt t2, t0, s5  # [op19] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
bne t2, zero, .Lbrc20_true  # [op20] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
sd t1, 96(sp)  # [op20] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
mv t1, t0  # [op20] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
ld t0, 96(sp)  # [op20] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
j .Lprog_exit  # [op20] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
.Lbrc20_true:  # [op20] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
mv s1, t0  # [op20] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
mv a2, t1  # [op20] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
j .Lprog_body  # [op20] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
.Lprog_body:  # block prog_body
li t0, 1  # [op21] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
divu t1, s1, a3  # [op22] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
mul t1, t1, a3  # [op23] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
sub t2, s1, t1  # [op24] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
mul t0, t0, a3  # [op25] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
divu t1, s1, t0  # [op26] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
divu a5, t1, a4  # [op27] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
mul a5, a5, a4  # [op28] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
sub t1, t1, a5  # [op29] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
mul t0, t0, a4  # [op30] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
addiw t0, t2, 0  # [op31] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
addiw t1, t1, 0  # [op32] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
addiw t2, a3, 0  # [op33] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
addiw t2, a4, 0  # [op34] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
ld t2, 16(a1)  # [op35] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
ld a5, 8(a1)  # [op36] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
mv a5, t0  # [op37] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:23:13
mv a7, t1  # [op38] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:24:17
li t0, 7  # [op39] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:25:15
sll a6, a7, t0  # [op40] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:25:15
li t0, 0  # [op41] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
mv t1, a2  # [op42] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
j .Lchunk1_head  # [op42] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
.Lchunk1_head:  # block chunk1_head
li a2, 128  # [op43] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
slt a2, t0, a2  # [op44] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
bne a2, zero, .Lbrc45_true  # [op45] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
mv t0, t1  # [op45] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
mv t1, s1  # [op45] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
j .Lchunk1_exit  # [op45] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
.Lbrc45_true:  # [op45] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
j .Lchunk1_body  # [op45] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
.Lchunk1_exit:  # block chunk1_exit
li t1, 0  # [op46] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
sd t0, 96(sp)  # [op47] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
mv t0, t1  # [op47] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
ld t1, 96(sp)  # [op47] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
j .Lchunk2_head  # [op47] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
.Lchunk1_body:  # block chunk1_body
li a2, 32  # [op48] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
vsetvli a2, a2, e32, m1, ta,ma  # [op49] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
li a2, 32  # [op50] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:25:37
vsetvli a2, a2, e32, m1, ta,ma  # [op51] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:25:37
vid.v v1  # [op52] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:25:37
vadd.vx v1, v1, t0  # [op53] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:25:37
vwadd.vx v2, v1, x0  # [op54] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:25:15
li a2, 32  # [op55] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:25:15
vsetvli a2, a2, e64, m2, ta,ma  # [op56] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:25:15
vmv.v.x v4, a6  # [op57] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:25:15
li a2, 32  # [op58] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:25:15
vsetvli a2, a2, e32, m1, ta,ma  # [op59] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:25:15
li a2, 32  # [op60] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:25:15
vsetvli a2, a2, e64, m2, ta,ma  # [op61] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:25:15
vadd.vv v2, v4, v2  # [op62] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:25:15
li a2, 32  # [op63] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:25:15
vsetvli a2, a2, e32, m1, ta,ma  # [op64] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:25:15
vid.v v1  # [op65] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:25:15
vadd.vx v1, v1, t0  # [op66] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:25:15
li a2, 32  # [op67] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:25:15
vsetvli a2, a2, e32, m1, ta,ma  # [op68] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:25:15
vwadd.vx v4, v1, x0  # [op69] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:25:15
li a2, 32  # [op70] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:25:15
vsetvli a2, a2, e64, m2, ta,ma  # [op71] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:25:15
li a2, 8  # [op72] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:25:15
vmul.vx v4, v4, a2  # [op73] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:25:15
li a2, 0  # [op74] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:25:15
add a2, t2, a2  # [op75] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:25:15
li s7, 32  # [op76] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:25:15
vsetvli s7, s7, e64, m2, ta,ma  # [op77] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:25:15
vsuxei64.v v2, (a2), v4  # [op78] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:25:15
li a2, 32  # [op79] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:25:15
vsetvli a2, a2, e32, m1, ta,ma  # [op80] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:25:15
li a2, 32  # [op81] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
add t1, t1, a2  # [op82] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
li a2, 32  # [op83] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
addw t0, t0, a2  # [op84] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
li a2, 32  # [op85] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
vsetvli a2, a2, e32, m1, ta,ma  # [op86] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
j .Lchunk1_head  # [op87] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
.Lchunk2_head:  # block chunk2_head
li a2, 256  # [op88] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
slt a2, t0, a2  # [op89] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
bne a2, zero, .Lbrc90_true  # [op90] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
mv t0, t1  # [op90] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
mv t1, s1  # [op90] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
j .Lchunk2_exit  # [op90] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
.Lbrc90_true:  # [op90] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
j .Lchunk2_body  # [op90] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
.Lchunk2_exit:  # block chunk2_exit
li t1, 0  # [op91] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
mv a2, t1  # [op92] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
mv a6, t0  # [op92] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
j .Lchunk3_head  # [op92] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
.Lchunk2_body:  # block chunk2_body
li a2, 32  # [op93] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
vsetvli a2, a2, e32, m1, ta,ma  # [op94] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
li a2, 32  # [op95] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:26:12
vsetvli a2, a2, e32, m1, ta,ma  # [op96] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:26:12
vid.v v1  # [op97] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:26:12
vadd.vx v1, v1, t0  # [op98] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:26:12
vid.v v2  # [op99] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:26:12
vadd.vx v2, v2, t0  # [op100] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:26:12
li a2, 32  # [op101] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:26:12
vsetvli a2, a2, e32, m1, ta,ma  # [op102] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:26:12
vwadd.vx v4, v2, x0  # [op103] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:26:12
li a2, 32  # [op104] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:26:12
vsetvli a2, a2, e64, m2, ta,ma  # [op105] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:26:12
li a2, 4  # [op106] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:26:12
vmul.vx v2, v4, a2  # [op107] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:26:12
li a2, 1024  # [op108] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:26:12
add a2, t2, a2  # [op109] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:26:12
li a6, 32  # [op110] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:26:12
vsetvli a6, a6, e32, m1, ta,ma  # [op111] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:26:12
vsuxei64.v v1, (a2), v2  # [op112] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:26:12
li a2, 32  # [op113] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:26:12
vsetvli a2, a2, e32, m1, ta,ma  # [op114] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:26:12
li a2, 17  # [op115] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
li a2, 32  # [op116] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
add t1, t1, a2  # [op117] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
li a2, 32  # [op118] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
addw t0, t0, a2  # [op119] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
li a2, 32  # [op120] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
vsetvli a2, a2, e32, m1, ta,ma  # [op121] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
j .Lchunk2_head  # [op122] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
.Lchunk3_head:  # block chunk3_head
li t0, 128  # [op123] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
slt t0, a2, t0  # [op124] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
bne t0, zero, .Lbrc125_true  # [op125] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
mv t0, s1  # [op125] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
j .Lchunk3_exit  # [op125] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
.Lbrc125_true:  # [op125] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
j .Lchunk3_body  # [op125] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
.Lchunk3_exit:  # block chunk3_exit
li t0, 2560  # [op126] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
add s7, t2, t0  # [op127] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
li t0, 3072  # [op128] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
add s8, t2, t0  # [op129] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
li t0, 0  # [op130] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
li s9, 256  # [op131] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
j .Lrhb4.head  # [op132] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
.Lchunk3_body:  # block chunk3_body
li t0, 32  # [op133] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
vsetvli t0, t0, e8, m1, ta,ma  # [op134] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
li t0, 17  # [op135] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
li t1, 32  # [op136] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
vsetvli t1, t1, e64, m2, ta,ma  # [op137] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
vmv.v.x v4, t0  # [op138] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
li t0, 32  # [op139] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
vsetvli t0, t0, e8, m1, ta,ma  # [op140] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
li t0, 32  # [op141] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
vsetvli t0, t0, e32, m1, ta,ma  # [op142] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
vid.v v1  # [op143] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
vadd.vx v1, v1, a2  # [op144] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
li t0, 32  # [op145] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
vsetvli t0, t0, e32, m1, ta,ma  # [op146] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
vwadd.vx v2, v1, x0  # [op147] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
li t0, 32  # [op148] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
vsetvli t0, t0, e64, m2, ta,ma  # [op149] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
li t0, 8  # [op150] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
vmul.vx v6, v2, t0  # [op151] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
li t0, 0  # [op152] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
add t0, t2, t0  # [op153] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
li t1, 32  # [op154] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
vsetvli t1, t1, e64, m2, ta,ma  # [op155] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
vluxei64.v v2, (t0), v6  # [op156] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
li t0, 32  # [op157] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
vsetvli t0, t0, e8, m1, ta,ma  # [op158] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
li t0, 32  # [op159] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
vsetvli t0, t0, e64, m2, ta,ma  # [op160] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
vmslt.vv v1, v2, v4  # [op161] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
li t0, 32  # [op162] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
vsetvli t0, t0, e8, m1, ta,ma  # [op163] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
li t0, 32  # [op164] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
vsetvli t0, t0, e32, m1, ta,ma  # [op165] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
vid.v v4  # [op166] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
vadd.vx v4, v4, a2  # [op167] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
li t0, 32  # [op168] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
vsetvli t0, t0, e32, m1, ta,ma  # [op169] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
vwadd.vx v6, v4, x0  # [op170] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
li t0, 32  # [op171] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
vsetvli t0, t0, e64, m2, ta,ma  # [op172] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
li t0, 4  # [op173] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
vmul.vx v4, v6, t0  # [op174] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
li t0, 2048  # [op175] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
add t0, t2, t0  # [op176] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
li t1, 32  # [op177] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
vsetvli t1, t1, e32, m1, ta,ma  # [op178] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
li t1, 1  # [op179] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
vmv.v.x v6, t1  # [op180] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
li t1, 0  # [op181] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
vmv.v.x v7, t1  # [op182] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
vmv1r.v v0, v1  # [op183] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
vmerge.vvm v6, v7, v6, v0  # [op184] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
vsuxei64.v v6, (t0), v4  # [op185] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
li t0, 32  # [op186] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
vsetvli t0, t0, e8, m1, ta,ma  # [op187] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:27:12
li t0, 4  # [op188] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:26
sll t0, a5, t0  # [op189] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:26
add t0, a5, t0  # [op190] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:26
li s7, 0  # [op191] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li t1, 0  # [op192] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.v.x v4, t1  # [op193] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li t1, 32  # [op194] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli t1, t1, e64, m2, ta,ma  # [op195] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vadd.vx v2, v2, t0  # [op196] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li t0, 32  # [op197] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli t0, t0, e8, m1, ta,ma  # [op198] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li t0, 32  # [op199] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli t0, t0, e64, m2, ta,ma  # [op200] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li t0, 1  # [op201] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmul.vx v2, v2, t0  # [op202] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li t0, 32  # [op203] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli t0, t0, e8, m1, ta,ma  # [op204] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li t0, 4096  # [op205] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
add t0, t2, t0  # [op206] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li t1, 128  # [op207] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
add t1, t0, t1  # [op208] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op209] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e32, m1, ta,ma  # [op210] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 0  # [op211] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.v.x v5, s8  # [op212] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 1  # [op213] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.v.x v6, s8  # [op214] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv1r.v v0, v1  # [op215] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmerge.vvm v5, v5, v6, v0  # [op216] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op217] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e64, m2, ta,ma  # [op218] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vadd.vx v6, v2, s3  # [op219] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op220] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e32, m1, ta,ma  # [op221] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 0  # [op222] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.v.x v2, s8  # [op223] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmsne.vv v2, v5, v2  # [op224] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv1r.v v0, v2  # [op225] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op226] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e64, m2, ta,ma  # [op227] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 0  # [op228] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.v.x v8, s8  # [op229] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.v.x v2, t1  # [op230] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsub.vv v6, v6, v2  # [op231] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmerge.vvm v6, v8, v6, v0  # [op232] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vadd.vv v2, v2, v6  # [op233] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op234] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e8, m1, ta,ma  # [op235] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op236] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e64, m2, ta,ma  # [op237] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s8, v2  # [op238] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s9, 0  # [op239] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
add s9, t0, s9  # [op240] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s10, 32  # [op241] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s10, s10, e8, m1, ta,ma  # [op242] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s10, v4  # [op243] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s10, 0(t1)  # [op244] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v4, v4, 1  # [op245] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
lbu s8, 0(s8)  # [op246] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s8, 0(s9)  # [op247] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op248] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e64, m2, ta,ma  # [op249] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v2, v2, 1  # [op250] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s8, v2  # [op251] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s9, 1  # [op252] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
add s9, t0, s9  # [op253] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s10, 32  # [op254] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s10, s10, e8, m1, ta,ma  # [op255] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s10, v4  # [op256] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s10, 0(t1)  # [op257] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v4, v4, 1  # [op258] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
lbu s8, 0(s8)  # [op259] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s8, 0(s9)  # [op260] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op261] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e64, m2, ta,ma  # [op262] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v2, v2, 1  # [op263] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s8, v2  # [op264] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s9, 2  # [op265] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
add s9, t0, s9  # [op266] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s10, 32  # [op267] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s10, s10, e8, m1, ta,ma  # [op268] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s10, v4  # [op269] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s10, 0(t1)  # [op270] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v4, v4, 1  # [op271] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
lbu s8, 0(s8)  # [op272] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s8, 0(s9)  # [op273] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op274] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e64, m2, ta,ma  # [op275] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v2, v2, 1  # [op276] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s8, v2  # [op277] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s9, 3  # [op278] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
add s9, t0, s9  # [op279] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s10, 32  # [op280] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s10, s10, e8, m1, ta,ma  # [op281] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s10, v4  # [op282] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s10, 0(t1)  # [op283] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v4, v4, 1  # [op284] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
lbu s8, 0(s8)  # [op285] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s8, 0(s9)  # [op286] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op287] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e64, m2, ta,ma  # [op288] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v2, v2, 1  # [op289] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s8, v2  # [op290] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s9, 4  # [op291] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
add s9, t0, s9  # [op292] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s10, 32  # [op293] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s10, s10, e8, m1, ta,ma  # [op294] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s10, v4  # [op295] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s10, 0(t1)  # [op296] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v4, v4, 1  # [op297] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
lbu s8, 0(s8)  # [op298] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s8, 0(s9)  # [op299] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op300] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e64, m2, ta,ma  # [op301] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v2, v2, 1  # [op302] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s8, v2  # [op303] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s9, 5  # [op304] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
add s9, t0, s9  # [op305] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s10, 32  # [op306] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s10, s10, e8, m1, ta,ma  # [op307] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s10, v4  # [op308] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s10, 0(t1)  # [op309] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v4, v4, 1  # [op310] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
lbu s8, 0(s8)  # [op311] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s8, 0(s9)  # [op312] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op313] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e64, m2, ta,ma  # [op314] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v2, v2, 1  # [op315] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s8, v2  # [op316] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s9, 6  # [op317] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
add s9, t0, s9  # [op318] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s10, 32  # [op319] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s10, s10, e8, m1, ta,ma  # [op320] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s10, v4  # [op321] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s10, 0(t1)  # [op322] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v4, v4, 1  # [op323] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
lbu s8, 0(s8)  # [op324] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s8, 0(s9)  # [op325] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op326] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e64, m2, ta,ma  # [op327] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v2, v2, 1  # [op328] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s8, v2  # [op329] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s9, 7  # [op330] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
add s9, t0, s9  # [op331] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s10, 32  # [op332] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s10, s10, e8, m1, ta,ma  # [op333] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s10, v4  # [op334] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s10, 0(t1)  # [op335] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v4, v4, 1  # [op336] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
lbu s8, 0(s8)  # [op337] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s8, 0(s9)  # [op338] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op339] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e64, m2, ta,ma  # [op340] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v2, v2, 1  # [op341] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s8, v2  # [op342] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s9, 8  # [op343] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
add s9, t0, s9  # [op344] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s10, 32  # [op345] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s10, s10, e8, m1, ta,ma  # [op346] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s10, v4  # [op347] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s10, 0(t1)  # [op348] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v4, v4, 1  # [op349] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
lbu s8, 0(s8)  # [op350] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s8, 0(s9)  # [op351] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op352] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e64, m2, ta,ma  # [op353] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v2, v2, 1  # [op354] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s8, v2  # [op355] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s9, 9  # [op356] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
add s9, t0, s9  # [op357] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s10, 32  # [op358] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s10, s10, e8, m1, ta,ma  # [op359] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s10, v4  # [op360] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s10, 0(t1)  # [op361] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v4, v4, 1  # [op362] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
lbu s8, 0(s8)  # [op363] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s8, 0(s9)  # [op364] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op365] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e64, m2, ta,ma  # [op366] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v2, v2, 1  # [op367] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s8, v2  # [op368] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s9, 10  # [op369] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
add s9, t0, s9  # [op370] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s10, 32  # [op371] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s10, s10, e8, m1, ta,ma  # [op372] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s10, v4  # [op373] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s10, 0(t1)  # [op374] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v4, v4, 1  # [op375] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
lbu s8, 0(s8)  # [op376] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s8, 0(s9)  # [op377] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op378] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e64, m2, ta,ma  # [op379] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v2, v2, 1  # [op380] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s8, v2  # [op381] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s9, 11  # [op382] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
add s9, t0, s9  # [op383] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s10, 32  # [op384] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s10, s10, e8, m1, ta,ma  # [op385] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s10, v4  # [op386] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s10, 0(t1)  # [op387] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v4, v4, 1  # [op388] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
lbu s8, 0(s8)  # [op389] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s8, 0(s9)  # [op390] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op391] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e64, m2, ta,ma  # [op392] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v2, v2, 1  # [op393] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s8, v2  # [op394] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s9, 12  # [op395] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
add s9, t0, s9  # [op396] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s10, 32  # [op397] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s10, s10, e8, m1, ta,ma  # [op398] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s10, v4  # [op399] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s10, 0(t1)  # [op400] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v4, v4, 1  # [op401] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
lbu s8, 0(s8)  # [op402] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s8, 0(s9)  # [op403] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op404] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e64, m2, ta,ma  # [op405] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v2, v2, 1  # [op406] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s8, v2  # [op407] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s9, 13  # [op408] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
add s9, t0, s9  # [op409] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s10, 32  # [op410] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s10, s10, e8, m1, ta,ma  # [op411] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s10, v4  # [op412] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s10, 0(t1)  # [op413] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v4, v4, 1  # [op414] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
lbu s8, 0(s8)  # [op415] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s8, 0(s9)  # [op416] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op417] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e64, m2, ta,ma  # [op418] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v2, v2, 1  # [op419] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s8, v2  # [op420] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s9, 14  # [op421] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
add s9, t0, s9  # [op422] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s10, 32  # [op423] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s10, s10, e8, m1, ta,ma  # [op424] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s10, v4  # [op425] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s10, 0(t1)  # [op426] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v4, v4, 1  # [op427] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
lbu s8, 0(s8)  # [op428] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s8, 0(s9)  # [op429] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op430] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e64, m2, ta,ma  # [op431] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v2, v2, 1  # [op432] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s8, v2  # [op433] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s9, 15  # [op434] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
add s9, t0, s9  # [op435] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s10, 32  # [op436] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s10, s10, e8, m1, ta,ma  # [op437] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s10, v4  # [op438] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s10, 0(t1)  # [op439] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v4, v4, 1  # [op440] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
lbu s8, 0(s8)  # [op441] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s8, 0(s9)  # [op442] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op443] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e64, m2, ta,ma  # [op444] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v2, v2, 1  # [op445] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s8, v2  # [op446] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s9, 16  # [op447] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
add s9, t0, s9  # [op448] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s10, 32  # [op449] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s10, s10, e8, m1, ta,ma  # [op450] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s10, v4  # [op451] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s10, 0(t1)  # [op452] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v4, v4, 1  # [op453] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
lbu s8, 0(s8)  # [op454] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s8, 0(s9)  # [op455] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op456] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e64, m2, ta,ma  # [op457] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v2, v2, 1  # [op458] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s8, v2  # [op459] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s9, 17  # [op460] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
add s9, t0, s9  # [op461] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s10, 32  # [op462] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s10, s10, e8, m1, ta,ma  # [op463] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s10, v4  # [op464] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s10, 0(t1)  # [op465] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v4, v4, 1  # [op466] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
lbu s8, 0(s8)  # [op467] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s8, 0(s9)  # [op468] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op469] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e64, m2, ta,ma  # [op470] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v2, v2, 1  # [op471] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s8, v2  # [op472] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s9, 18  # [op473] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
add s9, t0, s9  # [op474] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s10, 32  # [op475] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s10, s10, e8, m1, ta,ma  # [op476] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s10, v4  # [op477] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s10, 0(t1)  # [op478] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v4, v4, 1  # [op479] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
lbu s8, 0(s8)  # [op480] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s8, 0(s9)  # [op481] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op482] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e64, m2, ta,ma  # [op483] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v2, v2, 1  # [op484] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s8, v2  # [op485] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s9, 19  # [op486] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
add s9, t0, s9  # [op487] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s10, 32  # [op488] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s10, s10, e8, m1, ta,ma  # [op489] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s10, v4  # [op490] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s10, 0(t1)  # [op491] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v4, v4, 1  # [op492] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
lbu s8, 0(s8)  # [op493] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s8, 0(s9)  # [op494] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op495] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e64, m2, ta,ma  # [op496] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v2, v2, 1  # [op497] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s8, v2  # [op498] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s9, 20  # [op499] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
add s9, t0, s9  # [op500] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s10, 32  # [op501] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s10, s10, e8, m1, ta,ma  # [op502] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s10, v4  # [op503] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s10, 0(t1)  # [op504] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v4, v4, 1  # [op505] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
lbu s8, 0(s8)  # [op506] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s8, 0(s9)  # [op507] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op508] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e64, m2, ta,ma  # [op509] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v2, v2, 1  # [op510] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s8, v2  # [op511] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s9, 21  # [op512] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
add s9, t0, s9  # [op513] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s10, 32  # [op514] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s10, s10, e8, m1, ta,ma  # [op515] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s10, v4  # [op516] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s10, 0(t1)  # [op517] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v4, v4, 1  # [op518] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
lbu s8, 0(s8)  # [op519] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s8, 0(s9)  # [op520] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op521] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e64, m2, ta,ma  # [op522] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v2, v2, 1  # [op523] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s8, v2  # [op524] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s9, 22  # [op525] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
add s9, t0, s9  # [op526] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s10, 32  # [op527] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s10, s10, e8, m1, ta,ma  # [op528] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s10, v4  # [op529] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s10, 0(t1)  # [op530] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v4, v4, 1  # [op531] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
lbu s8, 0(s8)  # [op532] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s8, 0(s9)  # [op533] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op534] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e64, m2, ta,ma  # [op535] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v2, v2, 1  # [op536] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s8, v2  # [op537] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s9, 23  # [op538] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
add s9, t0, s9  # [op539] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s10, 32  # [op540] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s10, s10, e8, m1, ta,ma  # [op541] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s10, v4  # [op542] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s10, 0(t1)  # [op543] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v4, v4, 1  # [op544] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
lbu s8, 0(s8)  # [op545] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s8, 0(s9)  # [op546] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op547] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e64, m2, ta,ma  # [op548] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v2, v2, 1  # [op549] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s8, v2  # [op550] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s9, 24  # [op551] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
add s9, t0, s9  # [op552] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s10, 32  # [op553] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s10, s10, e8, m1, ta,ma  # [op554] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s10, v4  # [op555] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s10, 0(t1)  # [op556] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v4, v4, 1  # [op557] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
lbu s8, 0(s8)  # [op558] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s8, 0(s9)  # [op559] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op560] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e64, m2, ta,ma  # [op561] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v2, v2, 1  # [op562] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s8, v2  # [op563] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s9, 25  # [op564] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
add s9, t0, s9  # [op565] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s10, 32  # [op566] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s10, s10, e8, m1, ta,ma  # [op567] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s10, v4  # [op568] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s10, 0(t1)  # [op569] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v4, v4, 1  # [op570] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
lbu s8, 0(s8)  # [op571] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s8, 0(s9)  # [op572] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op573] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e64, m2, ta,ma  # [op574] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v2, v2, 1  # [op575] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s8, v2  # [op576] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s9, 26  # [op577] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
add s9, t0, s9  # [op578] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s10, 32  # [op579] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s10, s10, e8, m1, ta,ma  # [op580] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s10, v4  # [op581] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s10, 0(t1)  # [op582] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v4, v4, 1  # [op583] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
lbu s8, 0(s8)  # [op584] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s8, 0(s9)  # [op585] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op586] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e64, m2, ta,ma  # [op587] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v2, v2, 1  # [op588] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s8, v2  # [op589] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s9, 27  # [op590] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
add s9, t0, s9  # [op591] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s10, 32  # [op592] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s10, s10, e8, m1, ta,ma  # [op593] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s10, v4  # [op594] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s10, 0(t1)  # [op595] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v4, v4, 1  # [op596] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
lbu s8, 0(s8)  # [op597] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s8, 0(s9)  # [op598] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op599] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e64, m2, ta,ma  # [op600] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v2, v2, 1  # [op601] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s8, v2  # [op602] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s9, 28  # [op603] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
add s9, t0, s9  # [op604] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s10, 32  # [op605] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s10, s10, e8, m1, ta,ma  # [op606] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s10, v4  # [op607] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s10, 0(t1)  # [op608] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v4, v4, 1  # [op609] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
lbu s8, 0(s8)  # [op610] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s8, 0(s9)  # [op611] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op612] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e64, m2, ta,ma  # [op613] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v2, v2, 1  # [op614] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s8, v2  # [op615] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s9, 29  # [op616] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
add s9, t0, s9  # [op617] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s10, 32  # [op618] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s10, s10, e8, m1, ta,ma  # [op619] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s10, v4  # [op620] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s10, 0(t1)  # [op621] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v4, v4, 1  # [op622] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
lbu s8, 0(s8)  # [op623] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s8, 0(s9)  # [op624] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op625] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e64, m2, ta,ma  # [op626] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v2, v2, 1  # [op627] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s8, v2  # [op628] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s9, 30  # [op629] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
add s9, t0, s9  # [op630] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s10, 32  # [op631] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s10, s10, e8, m1, ta,ma  # [op632] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s10, v4  # [op633] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s10, 0(t1)  # [op634] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v4, v4, 1  # [op635] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
lbu s8, 0(s8)  # [op636] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s8, 0(s9)  # [op637] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s8, 32  # [op638] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s8, s8, e64, m2, ta,ma  # [op639] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v2, v2, 1  # [op640] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s8, v2  # [op641] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s9, 31  # [op642] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
add s9, t0, s9  # [op643] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li s10, 32  # [op644] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli s10, s10, e8, m1, ta,ma  # [op645] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vmv.x.s s10, v4  # [op646] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb s10, 0(t1)  # [op647] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v4, v4, 1  # [op648] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
lbu t1, 0(s8)  # [op649] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
sb t1, 0(s9)  # [op650] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li t1, 32  # [op651] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli t1, t1, e64, m2, ta,ma  # [op652] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vslidedown.vi v2, v2, 1  # [op653] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li t1, 32  # [op654] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vsetvli t1, t1, e8, m1, ta,ma  # [op655] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
vle8.v v2, 0(t0)  # [op656] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:28:12
li t0, 255  # [op657] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:36:32
vmv.v.x v3, t0  # [op658] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:36:32
vmv.v.v v4, v2  # [op659] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:42:36
li t0, 128  # [op660] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:43:35
vmv.v.x v2, t0  # [op661] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:43:35
vxor.vv v2, v2, v4  # [op662] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:43:35
vmv1r.v v0, v1  # [op663] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:46:34
vmerge.vvm v2, v3, v2, v0  # [op664] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:46:34
vwaddu.vx v4, v2, x0  # [op665] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:47:12
li t0, 32  # [op666] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:47:12
vsetvli t0, t0, e16, m1, ta,ma  # [op667] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:47:12
vmv.v.v v2, v4  # [op668] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:47:12
vwaddu.vx v4, v2, x0  # [op669] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:47:12
li t0, 32  # [op670] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:47:12
vsetvli t0, t0, e32, m1, ta,ma  # [op671] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:47:12
vmv.v.v v2, v4  # [op672] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:47:12
li t0, 32  # [op673] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:47:12
vsetvli t0, t0, e8, m1, ta,ma  # [op674] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:47:12
li t0, 32  # [op675] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:48:12
vsetvli t0, t0, e32, m1, ta,ma  # [op676] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:48:12
vmv.v.x v3, s7  # [op677] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:48:12
li t0, 32  # [op678] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:48:12
vsetvli t0, t0, e8, m1, ta,ma  # [op679] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:48:12
vmv1r.v v0, v1  # [op680] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:48:12
li t0, 32  # [op681] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:48:12
vsetvli t0, t0, e32, m1, ta,ma  # [op682] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:48:12
vmerge.vvm v1, v3, v2, v0  # [op683] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:48:12
li t0, 32  # [op684] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:48:12
vsetvli t0, t0, e8, m1, ta,ma  # [op685] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:48:12
li t0, 32  # [op686] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:48:12
vsetvli t0, t0, e32, m1, ta,ma  # [op687] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:48:12
vid.v v2  # [op688] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:48:12
vadd.vx v2, v2, a2  # [op689] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:48:12
li t0, 32  # [op690] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:48:12
vsetvli t0, t0, e32, m1, ta,ma  # [op691] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:48:12
vwadd.vx v4, v2, x0  # [op692] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:48:12
li t0, 32  # [op693] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:48:12
vsetvli t0, t0, e64, m2, ta,ma  # [op694] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:48:12
li t0, 4  # [op695] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:48:12
vmul.vx v2, v4, t0  # [op696] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:48:12
li t0, 2560  # [op697] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:48:12
add t0, t2, t0  # [op698] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:48:12
li t1, 32  # [op699] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:48:12
vsetvli t1, t1, e32, m1, ta,ma  # [op700] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:48:12
vsuxei64.v v1, (t0), v2  # [op701] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:48:12
li t0, 32  # [op702] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:48:12
vsetvli t0, t0, e8, m1, ta,ma  # [op703] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:48:12
li t0, 32  # [op704] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
add t0, a6, t0  # [op705] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
li t1, 32  # [op706] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
addw t1, a2, t1  # [op707] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
li a2, 32  # [op708] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
vsetvli a2, a2, e8, m1, ta,ma  # [op709] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
mv a2, t1  # [op710] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
mv a6, t0  # [op710] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
j .Lchunk3_head  # [op710] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
.Lrhb4.head:  # block rhb4.head
slt t1, t0, s9  # [op711] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
bne t1, zero, .Lbrc712_true  # [op712] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
j .Lrhb4.exit  # [op712] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
.Lbrc712_true:  # [op712] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
j .Lrhb4.body  # [op712] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
.Lrhb4.body:  # block rhb4.body
addiw s10, t0, 0  # [op713] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
li t1, 0  # [op714] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
li s11, 128  # [op715] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
li a2, 0  # [op716] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
j .Lrhj5.head  # [op717] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
.Lrhb4.exit:  # block rhb4.exit
li t0, 0  # [op718] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
li t1, 32  # [op719] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
vsetvli t1, t1, e32, m1, ta,ma  # [op720] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
li t1, 0  # [op721] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
vmv.v.x v1, t1  # [op722] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
mv t1, a6  # [op723] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
j .Lchunk6_head  # [op723] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
.Lrhj5.head:  # block rhj5.head
slt t3, t1, s11  # [op724] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
bne t3, zero, .Lbrc725_true  # [op725] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
sd a2, 96(sp)  # [op725] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
mv a2, t1  # [op725] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
ld t1, 96(sp)  # [op725] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
j .Lrhj5.exit  # [op725] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
.Lbrc725_true:  # [op725] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
j .Lrhj5.body  # [op725] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
.Lrhj5.body:  # block rhj5.body
li t3, 4  # [op726] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
mul t3, t1, t3  # [op727] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
add t3, s7, t3  # [op728] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
lw t3, 0(t3)  # [op729] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
li t4, 32  # [op730] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
vsetvli t4, t4, e32, m1, ta,ma  # [op731] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
vmv.v.x v1, t3  # [op732] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
vmv.v.x v2, s10  # [op733] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
vmseq.vv v1, v1, v2  # [op734] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
vcpop.m t3, v1  # [op735] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
li t4, 0  # [op736] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
sltu t3, t4, t3  # [op737] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
add a2, a2, t3  # [op738] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
li t3, 1  # [op739] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
add t1, t1, t3  # [op740] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
j .Lrhj5.head  # [op741] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
.Lrhj5.exit:  # block rhj5.exit
addiw t1, t1, 0  # [op742] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
li a2, 4  # [op743] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
mul a2, t0, a2  # [op744] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
add a2, s8, a2  # [op745] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
sw t1, 0(a2)  # [op746] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
li t1, 1  # [op747] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
add t0, t0, t1  # [op748] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
j .Lrhb4.head  # [op749] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:49:14
.Lchunk6_head:  # block chunk6_head
li a2, 128  # [op750] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
slt a2, t0, a2  # [op751] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
bne a2, zero, .Lbrc752_true  # [op752] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
mv t0, t1  # [op752] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
mv t1, s1  # [op752] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
j .Lchunk6_exit  # [op752] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
.Lbrc752_true:  # [op752] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
j .Lchunk6_body  # [op752] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
.Lchunk6_exit:  # block chunk6_exit
li t1, 32  # [op753] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
vsetvli t1, t1, e32, m1, ta,ma  # [op754] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
vmv.x.s a2, v1  # [op755] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
li t1, 0  # [op756] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
sd t0, 96(sp)  # [op757] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
mv t0, t1  # [op757] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
ld t1, 96(sp)  # [op757] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
j .Lchunk7_head  # [op757] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
.Lchunk6_body:  # block chunk6_body
li a2, 32  # [op758] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
vsetvli a2, a2, e32, m1, ta,ma  # [op759] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
li a2, 32  # [op760] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:50:29
vsetvli a2, a2, e32, m1, ta,ma  # [op761] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:50:29
vid.v v2  # [op762] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:50:29
vadd.vx v2, v2, t0  # [op763] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:50:29
li a2, 32  # [op764] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:50:29
vsetvli a2, a2, e32, m1, ta,ma  # [op765] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:50:29
vwadd.vx v4, v2, x0  # [op766] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:50:29
li a2, 32  # [op767] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:50:29
vsetvli a2, a2, e64, m2, ta,ma  # [op768] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:50:29
li a2, 4  # [op769] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:50:29
vmul.vx v2, v4, a2  # [op770] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:50:29
li a2, 2048  # [op771] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:50:29
add a2, t2, a2  # [op772] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:50:29
li a6, 32  # [op773] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:50:29
vsetvli a6, a6, e32, m1, ta,ma  # [op774] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:50:29
vluxei64.v v4, (a2), v2  # [op775] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:50:29
li a2, 0  # [op776] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:50:29
vmv.v.x v2, a2  # [op777] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:50:29
vmsne.vv v2, v4, v2  # [op778] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:50:29
li a2, 32  # [op779] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:50:29
vsetvli a2, a2, e32, m1, ta,ma  # [op780] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:50:29
vmnand.mm v2, v2, v2  # [op781] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:50:29
li a2, 1  # [op782] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:50:28
vmv.v.x v3, a2  # [op783] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:50:28
li a2, 0  # [op784] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:50:28
vmv.v.x v4, a2  # [op785] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:50:28
vmv1r.v v0, v2  # [op786] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:50:28
vmerge.vvm v2, v4, v3, v0  # [op787] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:50:28
li a2, 0  # [op788] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:50:21
vmv.v.x v3, a2  # [op789] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:50:21
vredsum.vs v2, v2, v3  # [op790] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:50:21
vmv.x.s a2, v2  # [op791] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:50:21
li a6, 32  # [op792] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
add t1, t1, a6  # [op793] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
li a6, 32  # [op794] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
addw t0, t0, a6  # [op795] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
li a6, 32  # [op796] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
vsetvli a6, a6, e32, m1, ta,ma  # [op797] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
li a6, 32  # [op798] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
vsetvli a6, a6, e32, m1, ta,ma  # [op799] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
vmv.v.x v2, a2  # [op800] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
vadd.vv v1, v1, v2  # [op801] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
j .Lchunk6_head  # [op802] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
.Lchunk7_head:  # block chunk7_head
li a6, 256  # [op803] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
slt a6, t0, a6  # [op804] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
bne a6, zero, .Lbrc805_true  # [op805] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
mv t0, t1  # [op805] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
mv t1, s1  # [op805] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
j .Lchunk7_exit  # [op805] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
.Lbrc805_true:  # [op805] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
j .Lchunk7_body  # [op805] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
.Lchunk7_exit:  # block chunk7_exit
mv t1, t0  # [op806] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
mv t0, s1  # [op806] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
j .Lprog_next  # [op806] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
.Lchunk7_body:  # block chunk7_body
li a6, 32  # [op807] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
vsetvli a6, a6, e32, m1, ta,ma  # [op808] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
li a6, 0  # [op809] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:32
li s7, 32  # [op810] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:32
vsetvli s7, s7, e32, m1, ta,ma  # [op811] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:32
vmv.v.x v1, a6  # [op812] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:32
vid.v v2  # [op813] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:32
vadd.vx v2, v2, t0  # [op814] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:32
li a6, 32  # [op815] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:32
vsetvli a6, a6, e32, m1, ta,ma  # [op816] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:32
vwadd.vx v4, v2, x0  # [op817] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:32
li a6, 32  # [op818] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:32
vsetvli a6, a6, e64, m2, ta,ma  # [op819] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:32
li a6, 4  # [op820] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:32
vmul.vx v4, v4, a6  # [op821] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:32
li a6, 1024  # [op822] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:32
add a6, t2, a6  # [op823] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:32
li s7, 32  # [op824] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:32
vsetvli s7, s7, e32, m1, ta,ma  # [op825] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:32
vluxei64.v v2, (a6), v4  # [op826] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:32
li a6, 32  # [op827] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:32
vsetvli a6, a6, e32, m1, ta,ma  # [op828] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:32
vmseq.vv v3, v2, v1  # [op829] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:32
vmv.v.x v4, a2  # [op830] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:23
vmv1r.v v0, v3  # [op831] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:23
vmerge.vvm v1, v1, v4, v0  # [op832] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:23
vid.v v3  # [op833] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:14
vadd.vx v3, v3, t0  # [op834] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:14
li a6, 32  # [op835] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:14
vsetvli a6, a6, e32, m1, ta,ma  # [op836] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:14
vwadd.vx v4, v3, x0  # [op837] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:14
li a6, 32  # [op838] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:14
vsetvli a6, a6, e64, m2, ta,ma  # [op839] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:14
li a6, 4  # [op840] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:14
vmul.vx v4, v4, a6  # [op841] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:14
li a6, 3072  # [op842] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:14
add a6, t2, a6  # [op843] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:14
li s7, 32  # [op844] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:14
vsetvli s7, s7, e32, m1, ta,ma  # [op845] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:14
vluxei64.v v3, (a6), v4  # [op846] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:14
li a6, 32  # [op847] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:14
vsetvli a6, a6, e32, m1, ta,ma  # [op848] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:14
vsub.vv v1, v3, v1  # [op849] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:51:14
add a6, a5, a7  # [op850] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:52:22
li s7, 8  # [op851] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:52:21
sll a6, a6, s7  # [op852] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:52:21
vwadd.vx v4, v2, x0  # [op853] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:52:21
li s7, 32  # [op854] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:52:21
vsetvli s7, s7, e64, m2, ta,ma  # [op855] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:52:21
vmv.v.x v2, a6  # [op856] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:52:21
li a6, 32  # [op857] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:52:21
vsetvli a6, a6, e32, m1, ta,ma  # [op858] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:52:21
li a6, 32  # [op859] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:52:21
vsetvli a6, a6, e64, m2, ta,ma  # [op860] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:52:21
vadd.vv v2, v2, v4  # [op861] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:52:21
li a6, 32  # [op862] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:52:21
vsetvli a6, a6, e32, m1, ta,ma  # [op863] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:52:21
li a6, 32  # [op864] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:53:5
vsetvli a6, a6, e64, m2, ta,ma  # [op865] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:53:5
li a6, 4  # [op866] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:53:5
vmul.vx v2, v2, a6  # [op867] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:53:5
li a6, 32  # [op868] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:53:5
vsetvli a6, a6, e32, m1, ta,ma  # [op869] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:53:5
li a6, 32  # [op870] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:53:5
vsetvli a6, a6, e32, m1, ta,ma  # [op871] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:53:5
vsuxei64.v v1, (s4), v2  # [op872] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:53:5
li a6, 32  # [op873] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
add t1, t1, a6  # [op874] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
li a6, 32  # [op875] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
addw t0, t0, a6  # [op876] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
li a6, 32  # [op877] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
vsetvli a6, a6, e32, m1, ta,ma  # [op878] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
j .Lchunk7_head  # [op879] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
.Lprog_next:  # block prog_next
add t0, t0, s6  # [op880] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
j .Lprog_head  # [op881] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
.Lprog_exit:  # block prog_exit
sd t0, 0(s2)  # [op882] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
ld ra, 0(sp)  # [op883] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
ld s1, 8(sp)  # [op883] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
ld s2, 16(sp)  # [op883] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
ld s3, 24(sp)  # [op883] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
ld s4, 32(sp)  # [op883] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
ld s5, 40(sp)  # [op883] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
ld s6, 48(sp)  # [op883] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
ld s7, 56(sp)  # [op883] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
ld s8, 64(sp)  # [op883] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
ld s9, 72(sp)  # [op883] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
ld s10, 80(sp)  # [op883] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
ld s11, 88(sp)  # [op883] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
addi sp, sp, 112  # [op883] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
ret  # [op883] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/nanmedian_ascend_histogram_count_kernel.py:22:1
    .size operator_entry, .-operator_entry
    .section .note.GNU-stack,"",@progbits
