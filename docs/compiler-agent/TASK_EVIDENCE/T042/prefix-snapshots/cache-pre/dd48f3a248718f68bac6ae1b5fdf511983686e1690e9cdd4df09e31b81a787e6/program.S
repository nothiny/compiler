# a100c emitted program: amax_kernel_1
# source: home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py
# specialization identity: af5e9f0cad748288
# compiler revision: bb81f4c49150cef9
# target model: a100-rvv1-vlen1024/1 (VLEN=1024, file=4096B)
# options: default
# argument layout: 168cdead92f45432
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
    li a0, 64
    ret
    .size operator_workspace_shared, .-operator_workspace_shared
    .globl operator_entry
    .type operator_entry, @function
operator_entry:  # fn operator_entry
addi sp, sp, -96
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
mv t0, a0
.Lentry:  # block entry
ld t1, 0(t0)  # [op0] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
ld t2, 0(t1)  # [op1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
ld s1, 8(t1)  # [op2] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
ld s9, 24(t0)  # [op3] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
lwu t1, 40(t0)  # [op4] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
lwu s3, 44(t0)  # [op5] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
ld s1, 8(s1)  # [op6] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
addiw a3, s1, 0  # [op7] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
ld a4, 0(t2)  # [op8] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
ld s4, 56(t2)  # [op9] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
ld t2, 64(t2)  # [op10] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
ld t2, 0(t2)  # [op11] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
li s1, 1  # [op12] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
mul a5, s1, t2  # [op13] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
mv s1, t1  # [op14] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
mv s1, s3  # [op15] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
li a1, 0  # [op16] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
li a1, 1  # [op17] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
li a2, 2  # [op18] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
slt a1, a1, s1  # [op19] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
slt a2, a5, a2  # [op20] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
and a1, a1, a2  # [op21] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
mv a2, t1  # [op22] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
li a6, 0  # [op23] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
bne a1, zero, .Lbrc24_true  # [op24] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
mv t1, a2  # [op24] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
mv a1, a6  # [op24] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
j .Lprog_head  # [op24] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
.Lbrc24_true:  # [op24] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
j .Lsplit_entry  # [op24] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
.Lprog_head:  # block prog_head
slt a2, t1, a5  # [op25] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
bne a2, zero, .Lbrc26_true  # [op26] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
mv t0, a1  # [op26] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
j .Lprog_exit  # [op26] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
.Lbrc26_true:  # [op26] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
sd a1, 80(sp)  # [op26] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
mv a1, t1  # [op26] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
ld t1, 80(sp)  # [op26] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
j .Lprog_body  # [op26] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
.Lsplit_entry:  # block split_entry
mv s2, t1  # [op27] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
li a1, 0  # [op28] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
li a2, 0  # [op29] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
addiw t2, t2, 0  # [op30] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
ld t2, 16(t0)  # [op31] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
ld s5, 8(t0)  # [op32] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
mv s6, a2  # [op33] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:12:11
li t2, 7  # [op34] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:13:14
sll a2, s6, t2  # [op35] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:13:14
mv t2, t1  # [op36] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
li a5, 32  # [op37] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
mul a5, s1, a5  # [op38] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
li s1, 32  # [op39] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
mul t2, t2, s1  # [op40] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
addiw t2, t2, 0  # [op41] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
li s1, 32  # [op42] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
vsetvli s1, s1, e32, m1, ta,ma  # [op43] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
li s1, 4286578688  # [op44] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
vmv.v.x v1, s1  # [op45] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
mv s1, a1  # [op46] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
j .Lschunk2_head  # [op46] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
.Lprog_body:  # block prog_body
addiw a2, a1, 0  # [op47] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
addiw a6, t2, 0  # [op48] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
ld a6, 16(t0)  # [op49] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
ld a6, 8(t0)  # [op50] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
mv a6, a2  # [op51] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:12:11
li a2, 7  # [op52] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:13:14
sll a7, a6, a2  # [op53] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:13:14
li a2, 0  # [op54] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
li s2, 32  # [op55] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
vsetvli s2, s2, e32, m1, ta,ma  # [op56] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
li s2, 4286578688  # [op57] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
vmv.v.x v1, s2  # [op58] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
sd t1, 80(sp)  # [op59] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
mv t1, a2  # [op59] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
ld a2, 80(sp)  # [op59] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
j .Lchunk1_head  # [op59] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
.Lchunk1_head:  # block chunk1_head
li s2, 128  # [op60] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
slt s2, t1, s2  # [op61] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
bne s2, zero, .Lbrc62_true  # [op62] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
mv t1, a2  # [op62] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
mv a2, a1  # [op62] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
j .Lchunk1_exit  # [op62] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
.Lbrc62_true:  # [op62] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
j .Lchunk1_body  # [op62] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
.Lchunk1_exit:  # block chunk1_exit
li a2, 32  # [op63] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
vsetvli a2, a2, e32, m1, ta,ma  # [op64] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
vmv.x.s a2, v1  # [op65] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
li a7, 4  # [op66] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:34:5
mul a6, a6, a7  # [op67] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:34:5
add a6, s4, a6  # [op68] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:34:5
sw a2, 0(a6)  # [op69] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:34:5
sd t1, 80(sp)  # [op70] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
mv t1, a1  # [op70] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
ld a1, 80(sp)  # [op70] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
j .Lprog_next  # [op70] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
.Lchunk1_body:  # block chunk1_body
li s2, 32  # [op71] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
vsetvli s2, s2, e32, m1, ta,ma  # [op72] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
li s2, 32  # [op73] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:13:33
vsetvli s2, s2, e32, m1, ta,ma  # [op74] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:13:33
vid.v v2  # [op75] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:13:33
vadd.vx v2, v2, t1  # [op76] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:13:33
vwadd.vx v4, v2, x0  # [op77] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:13:14
li s2, 32  # [op78] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:13:14
vsetvli s2, s2, e64, m2, ta,ma  # [op79] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:13:14
vmv.v.x v2, a7  # [op80] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:13:14
li s2, 32  # [op81] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:13:14
vsetvli s2, s2, e32, m1, ta,ma  # [op82] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:13:14
li s2, 32  # [op83] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:13:14
vsetvli s2, s2, e64, m2, ta,ma  # [op84] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:13:14
vadd.vv v2, v2, v4  # [op85] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:13:14
li s2, 32  # [op86] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:13:14
vsetvli s2, s2, e32, m1, ta,ma  # [op87] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:13:14
mv s2, a3  # [op88] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:15:12
li s3, 32  # [op89] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:15:12
vsetvli s3, s3, e64, m2, ta,ma  # [op90] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:15:12
vmv.v.x v4, s2  # [op91] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:15:12
li s2, 32  # [op92] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:15:12
vsetvli s2, s2, e32, m1, ta,ma  # [op93] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:15:12
li s2, 32  # [op94] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:15:12
vsetvli s2, s2, e64, m2, ta,ma  # [op95] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:15:12
vmslt.vv v4, v2, v4  # [op96] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:15:12
li s2, 32  # [op97] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:15:12
vsetvli s2, s2, e32, m1, ta,ma  # [op98] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:15:12
li s2, 4286578688  # [op99] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:31:15
vmv.v.x v5, s2  # [op100] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:31:15
li s2, 32  # [op101] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:31:15
vsetvli s2, s2, e64, m2, ta,ma  # [op102] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:31:15
li s2, 4  # [op103] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:31:15
vmul.vx v2, v2, s2  # [op104] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:31:15
li s2, 32  # [op105] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:31:15
vsetvli s2, s2, e32, m1, ta,ma  # [op106] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:31:15
vmv1r.v v0, v4  # [op107] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:31:15
vluxei64.v v6, (a4), v2, v0.t  # [op108] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:31:15
vmv1r.v v0, v4  # [op109] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:31:15
vmerge.vvm v2, v5, v6, v0  # [op110] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:31:15
li s2, 32  # [op111] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:32:16
vsetvli s2, s2, e32, m1, ta,ma  # [op112] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:32:16
li s2, 4286578688  # [op113] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:32:16
vmv.v.x v3, s2  # [op114] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:32:16
vfredmax.vs v2, v2, v3  # [op115] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:32:16
vmv.x.s s2, v2  # [op116] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:32:16
li s3, 32  # [op117] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
add a2, a2, s3  # [op118] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
li s3, 32  # [op119] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
addw t1, t1, s3  # [op120] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
li s3, 32  # [op121] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
vsetvli s3, s3, e32, m1, ta,ma  # [op122] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
li s3, 32  # [op123] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
vsetvli s3, s3, e32, m1, ta,ma  # [op124] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
vmv.v.x v2, s2  # [op125] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
vmflt.vv v3, v1, v2  # [op126] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
vmv1r.v v0, v3  # [op127] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
vmerge.vvm v1, v1, v2, v0  # [op128] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
j .Lchunk1_head  # [op129] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
.Lprog_next:  # block prog_next
add t1, t1, s1  # [op130] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
j .Lprog_head  # [op131] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
.Lschunk2_head:  # block schunk2_head
li a1, 128  # [op132] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
slt a1, t2, a1  # [op133] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
bne a1, zero, .Lbrc134_true  # [op134] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
mv t2, s2  # [op134] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
j .Lschunk2_exit  # [op134] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
.Lbrc134_true:  # [op134] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
j .Lschunk2_body  # [op134] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
.Lschunk2_exit:  # block schunk2_exit
li t2, 32  # [op135] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
vsetvli t2, t2, e32, m1, ta,ma  # [op136] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
vmv.x.s t2, v1  # [op137] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
li s7, 8  # [op138] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
mv s8, t1  # [op139] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
mul t1, s8, s7  # [op140] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
add t1, s5, t1  # [op141] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
sw t2, 0(t1)  # [op142] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
mv a0, t0  # [op143] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
call a100rt_stage_barrier  # [op143] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
li t0, 0  # [op144] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
sltu t0, t0, s8  # [op145] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
bne t0, zero, .Lbrc146_true  # [op146] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
j .Lsplit_merge  # [op146] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
.Lbrc146_true:  # [op146] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
j .Lsplit_skip  # [op146] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
.Lschunk2_body:  # block schunk2_body
li a1, 32  # [op147] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
vsetvli a1, a1, e32, m1, ta,ma  # [op148] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
li a1, 32  # [op149] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:13:33
vsetvli a1, a1, e32, m1, ta,ma  # [op150] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:13:33
vid.v v2  # [op151] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:13:33
vadd.vx v2, v2, t2  # [op152] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:13:33
vwadd.vx v4, v2, x0  # [op153] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:13:14
li a1, 32  # [op154] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:13:14
vsetvli a1, a1, e64, m2, ta,ma  # [op155] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:13:14
vmv.v.x v2, a2  # [op156] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:13:14
li a1, 32  # [op157] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:13:14
vsetvli a1, a1, e32, m1, ta,ma  # [op158] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:13:14
li a1, 32  # [op159] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:13:14
vsetvli a1, a1, e64, m2, ta,ma  # [op160] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:13:14
vadd.vv v2, v2, v4  # [op161] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:13:14
li a1, 32  # [op162] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:13:14
vsetvli a1, a1, e32, m1, ta,ma  # [op163] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:13:14
mv a1, a3  # [op164] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:15:12
li a6, 32  # [op165] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:15:12
vsetvli a6, a6, e64, m2, ta,ma  # [op166] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:15:12
vmv.v.x v4, a1  # [op167] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:15:12
li a1, 32  # [op168] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:15:12
vsetvli a1, a1, e32, m1, ta,ma  # [op169] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:15:12
li a1, 32  # [op170] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:15:12
vsetvli a1, a1, e64, m2, ta,ma  # [op171] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:15:12
vmslt.vv v4, v2, v4  # [op172] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:15:12
li a1, 32  # [op173] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:15:12
vsetvli a1, a1, e32, m1, ta,ma  # [op174] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:15:12
li a1, 4286578688  # [op175] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:31:15
vmv.v.x v5, a1  # [op176] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:31:15
li a1, 32  # [op177] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:31:15
vsetvli a1, a1, e64, m2, ta,ma  # [op178] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:31:15
li a1, 4  # [op179] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:31:15
vmul.vx v2, v2, a1  # [op180] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:31:15
li a1, 32  # [op181] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:31:15
vsetvli a1, a1, e32, m1, ta,ma  # [op182] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:31:15
vmv1r.v v0, v4  # [op183] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:31:15
vluxei64.v v6, (a4), v2, v0.t  # [op184] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:31:15
vmv1r.v v0, v4  # [op185] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:31:15
vmerge.vvm v2, v5, v6, v0  # [op186] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:31:15
li a1, 32  # [op187] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:32:16
vsetvli a1, a1, e32, m1, ta,ma  # [op188] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:32:16
li a1, 4286578688  # [op189] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:32:16
vmv.v.x v3, a1  # [op190] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:32:16
vfredmax.vs v2, v2, v3  # [op191] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:32:16
vmv.x.s a1, v2  # [op192] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:32:16
li a6, 32  # [op193] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
add s1, s1, a6  # [op194] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
addiw a6, a5, 0  # [op195] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
addw t2, t2, a6  # [op196] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
li a6, 32  # [op197] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
vsetvli a6, a6, e32, m1, ta,ma  # [op198] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
li a6, 32  # [op199] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
vsetvli a6, a6, e32, m1, ta,ma  # [op200] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
vmv.v.x v2, a1  # [op201] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
vmflt.vv v3, v1, v2  # [op202] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
vmv1r.v v0, v3  # [op203] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
vmerge.vvm v1, v1, v2, v0  # [op204] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
j .Lschunk2_head  # [op205] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
.Lsplit_merge:  # block split_merge
li t0, 32  # [op206] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
vsetvli t0, t0, e32, m1, ta,ma  # [op207] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
li t0, 4286578688  # [op208] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
vmv.v.x v1, t0  # [op209] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
li t0, 0  # [op210] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
mv t1, s3  # [op211] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
j .Lmerge.head  # [op212] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
.Lsplit_skip:  # block split_skip
mv t1, s2  # [op213] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
mv t0, s1  # [op213] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
j .Lprog_exit  # [op213] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
.Lmerge.head:  # block merge.head
slt t2, t0, t1  # [op214] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
bne t2, zero, .Lbrc215_true  # [op215] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
j .Lmerge.exit  # [op215] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
.Lbrc215_true:  # [op215] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
j .Lmerge.body  # [op215] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
.Lmerge.body:  # block merge.body
mul t2, t0, s7  # [op216] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
add t2, s5, t2  # [op217] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
li a1, 32  # [op218] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
vsetvli a1, a1, e32, m1, ta,ma  # [op219] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
li a1, 1  # [op220] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
add t0, t0, a1  # [op221] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
lw t2, 0(t2)  # [op222] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
li a1, 32  # [op223] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
vsetvli a1, a1, e32, m1, ta,ma  # [op224] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
vmv.v.x v2, t2  # [op225] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
vmflt.vv v3, v1, v2  # [op226] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
vmv1r.v v0, v3  # [op227] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
vmerge.vvm v1, v1, v2, v0  # [op228] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
j .Lmerge.head  # [op229] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
.Lmerge.exit:  # block merge.exit
li t0, 32  # [op230] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
vsetvli t0, t0, e32, m1, ta,ma  # [op231] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
vmv.x.s t0, v1  # [op232] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
li t1, 4  # [op233] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:34:5
mul t1, s6, t1  # [op234] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:34:5
add t1, s4, t1  # [op235] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:34:5
sw t0, 0(t1)  # [op236] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:34:5
mv t1, s2  # [op237] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
mv t0, s1  # [op237] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
j .Lprog_exit  # [op237] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
.Lprog_exit:  # block prog_exit
sd t0, 0(s9)  # [op238] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
ld ra, 0(sp)  # [op239] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
ld s1, 8(sp)  # [op239] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
ld s2, 16(sp)  # [op239] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
ld s3, 24(sp)  # [op239] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
ld s4, 32(sp)  # [op239] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
ld s5, 40(sp)  # [op239] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
ld s6, 48(sp)  # [op239] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
ld s7, 56(sp)  # [op239] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
ld s8, 64(sp)  # [op239] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
ld s9, 72(sp)  # [op239] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
addi sp, sp, 96  # [op239] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
ret  # [op239] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/amax_kernel_1.py:11:1
    .size operator_entry, .-operator_entry
    .section .note.GNU-stack,"",@progbits
