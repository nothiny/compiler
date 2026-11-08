# a100c emitted program: batched_vecmat_kernel
# source: home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py
# specialization identity: 23341e70a9a83bee
# compiler revision: bb81f4c49150cef9
# target model: a100-rvv1-vlen1024/1 (VLEN=1024, file=4096B)
# options: default
# argument layout: 67ccddd41ac8ead9
# every instruction below traces to a selected MIR op: [opN] carries the source location
# passes: passes=default
    .text
    .globl operator_workspace_private
    .type operator_workspace_private, @function
operator_workspace_private:
    li a0, 77712
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
addi sp, sp, -256
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
ld t0, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t0, 0(t0)  # [op0] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t1, 0(t0)  # [op1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
sd t1, 128(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t0, 8(t0)  # [op2] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
sd t0, 136(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t0, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t0, 24(t0)  # [op3] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
sd t0, 144(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t0, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
lwu t0, 40(t0)  # [op4] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
lwu t1, 44(t1)  # [op5] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t2, 136(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t2, 8(t2)  # [op6] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
addiw t2, t2, 0  # [op7] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
sd t2, 152(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t2, 136(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t2, 24(t2)  # [op8] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
sd t2, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t2, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
addiw t2, t2, 0  # [op9] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
sd t2, 168(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t2, 136(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t2, 40(t2)  # [op10] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
sd t2, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t2, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
addiw t2, t2, 0  # [op11] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
sd t2, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t2, 128(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld s3, 0(t2)  # [op12] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t2, 128(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld s4, 56(t2)  # [op13] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t2, 128(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld s5, 112(t2)  # [op14] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 32  # [op15] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li s1, 1  # [op16] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
sub t2, t2, s1  # [op17] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld s1, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
add t2, s1, t2  # [op18] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li s1, 32  # [op19] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
divu t2, t2, s1  # [op20] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
sd t2, 192(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 32  # [op21] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li s1, 1  # [op22] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
sub t2, t2, s1  # [op23] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld s1, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
add t2, s1, t2  # [op24] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li s1, 32  # [op25] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
divu t2, t2, s1  # [op26] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
sd t2, 200(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 1  # [op27] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld s1, 192(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mul t2, t2, s1  # [op28] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld s1, 200(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mul s6, t2, s1  # [op29] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t0, t0  # [op30] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv s7, t1  # [op31] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t1, 0  # [op32] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lprog_head  # [op33] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lprog_head:  # block prog_head
slt t2, t0, s6  # [op34] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
bne t2, zero, .Lbrc35_true  # [op35] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
sd t1, 96(sp)  # [op35] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t1, t0  # [op35] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t0, 96(sp)  # [op35] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lprog_exit  # [op35] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lbrc35_true:  # [op35] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t2, t1  # [op35] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lprog_body  # [op35] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lprog_body:  # block prog_body
sd t0, 208(sp)  # [op-1]
li t0, 1  # [op36] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t1, 192(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld s1, 208(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
divu t1, s1, t1  # [op37] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld s1, 192(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mul t1, t1, s1  # [op38] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld s1, 208(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
sub s1, s1, t1  # [op39] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t1, 192(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mul t0, t0, t1  # [op40] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t1, 208(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
divu t1, t1, t0  # [op41] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld a1, 200(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
divu a1, t1, a1  # [op42] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld a2, 200(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mul a1, a1, a2  # [op43] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
sub t1, t1, a1  # [op44] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld a1, 200(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mul t0, t0, a1  # [op45] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
addiw t0, s1, 0  # [op46] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
addiw s1, t1, 0  # [op47] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t1, 192(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
addiw t1, t1, 0  # [op48] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t1, 200(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
addiw t1, t1, 0  # [op49] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t1, 8(t1)  # [op51] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t1, 5  # [op53] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:14
sllw a1, t0, t1  # [op54] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:14
li t0, 0  # [op55] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk1_head  # [op56] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk1_head:  # block chunk1_head
li a2, 32  # [op57] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
slt a2, t0, a2  # [op58] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld a3, 208(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
bne a2, zero, .Lbrc59_true  # [op59] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t0, t2  # [op59] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t2, a3  # [op59] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk1_exit  # [op59] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lbrc59_true:  # [op59] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk1_body  # [op59] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk1_exit:  # block chunk1_exit
li t2, 0  # [op60] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
sd t0, 96(sp)  # [op61] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t0, t2  # [op61] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t2, 96(sp)  # [op61] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk2_head  # [op61] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk1_body:  # block chunk1_body
li a2, 32  # [op62] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
vsetvli a2, a2, e32, m1, ta,ma  # [op63] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li a2, 32  # [op64] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:27
vsetvli a2, a2, e32, m1, ta,ma  # [op65] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:27
vid.v v1  # [op66] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:27
vadd.vx v1, v1, t0  # [op67] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:27
vid.v v2  # [op68] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:27
vadd.vx v2, v2, t0  # [op69] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:27
li a2, 32  # [op70] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:27
vsetvli a2, a2, e32, m1, ta,ma  # [op71] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:27
vwadd.vx v4, v2, x0  # [op72] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:27
li a2, 32  # [op73] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:27
vsetvli a2, a2, e64, m2, ta,ma  # [op74] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:27
li a2, 4  # [op75] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:27
vmul.vx v2, v4, a2  # [op76] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:27
li a2, 0  # [op77] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:27
ld a3, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:27
ld a3, 16(a3)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:27
add a2, a3, a2  # [op78] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:27
li a3, 32  # [op79] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:27
vsetvli a3, a3, e32, m1, ta,ma  # [op80] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:27
vsuxei64.v v1, (a2), v2  # [op81] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:27
li a2, 32  # [op82] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:27
vsetvli a2, a2, e32, m1, ta,ma  # [op83] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:27
vmv.v.x v2, a1  # [op84] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:14
vadd.vv v2, v2, v1  # [op85] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:14
vid.v v3  # [op86] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:14
vadd.vx v3, v3, t0  # [op87] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:14
li a2, 32  # [op88] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:14
vsetvli a2, a2, e32, m1, ta,ma  # [op89] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:14
vwadd.vx v4, v3, x0  # [op90] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:14
li a2, 32  # [op91] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:14
vsetvli a2, a2, e64, m2, ta,ma  # [op92] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:14
li a2, 4  # [op93] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:14
vmul.vx v4, v4, a2  # [op94] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:14
li a2, 128  # [op95] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:14
ld a3, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:14
ld a3, 16(a3)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:14
add a2, a3, a2  # [op96] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:14
li a3, 32  # [op97] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:14
vsetvli a3, a3, e32, m1, ta,ma  # [op98] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:14
vsuxei64.v v2, (a2), v4  # [op99] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:14
li a2, 32  # [op100] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:14
vsetvli a2, a2, e32, m1, ta,ma  # [op101] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:24:14
sllw a2, s1, t1  # [op102] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:25:14
vmv.v.x v2, a2  # [op103] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:25:14
vadd.vv v1, v2, v1  # [op104] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:25:14
vid.v v2  # [op105] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:25:14
vadd.vx v2, v2, t0  # [op106] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:25:14
li a2, 32  # [op107] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:25:14
vsetvli a2, a2, e32, m1, ta,ma  # [op108] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:25:14
vwadd.vx v4, v2, x0  # [op109] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:25:14
li a2, 32  # [op110] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:25:14
vsetvli a2, a2, e64, m2, ta,ma  # [op111] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:25:14
li a2, 4  # [op112] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:25:14
vmul.vx v2, v4, a2  # [op113] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:25:14
li a2, 256  # [op114] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:25:14
ld a3, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:25:14
ld a3, 16(a3)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:25:14
add a2, a3, a2  # [op115] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:25:14
li a3, 32  # [op116] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:25:14
vsetvli a3, a3, e32, m1, ta,ma  # [op117] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:25:14
vsuxei64.v v1, (a2), v2  # [op118] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:25:14
li a2, 32  # [op119] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:25:14
vsetvli a2, a2, e32, m1, ta,ma  # [op120] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:25:14
li a2, 32  # [op121] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
add t2, t2, a2  # [op122] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li a2, 32  # [op123] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
addw t0, t0, a2  # [op124] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li a2, 32  # [op125] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
vsetvli a2, a2, e32, m1, ta,ma  # [op126] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk1_head  # [op127] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk2_head:  # block chunk2_head
li s1, 1024  # [op128] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
slt s1, t0, s1  # [op129] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld a1, 208(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
bne s1, zero, .Lbrc130_true  # [op130] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t1, a1  # [op130] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t0, t2  # [op130] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk2_exit  # [op130] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lbrc130_true:  # [op130] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk2_body  # [op130] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk2_exit:  # block chunk2_exit
li t1, 77704  # [op131] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t2, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t2, 16(t2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
add t1, t2, t1  # [op132] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
lw s8, 0(t1)  # [op133] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t1, 0  # [op134] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
sd t0, 96(sp)  # [op135] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t0, t1  # [op135] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t1, 96(sp)  # [op135] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk3_head  # [op135] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk2_body:  # block chunk2_body
li s1, 32  # [op136] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
vsetvli s1, s1, e32, m1, ta,ma  # [op137] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li s1, 0  # [op138] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:26:11
li a1, 32  # [op139] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:26:11
vsetvli a1, a1, e32, m1, ta,ma  # [op140] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:26:11
vmv.v.x v1, s1  # [op141] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:26:11
vid.v v2  # [op142] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:26:11
vadd.vx v2, v2, t0  # [op143] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:26:11
li s1, 32  # [op144] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:26:11
vsetvli s1, s1, e32, m1, ta,ma  # [op145] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:26:11
vwadd.vx v4, v2, x0  # [op146] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:26:11
li s1, 32  # [op147] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:26:11
vsetvli s1, s1, e64, m2, ta,ma  # [op148] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:26:11
li s1, 4  # [op149] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:26:11
vmul.vx v2, v4, s1  # [op150] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:26:11
li s1, 384  # [op151] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:26:11
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:26:11
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:26:11
add s1, a1, s1  # [op152] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:26:11
li a1, 32  # [op153] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:26:11
vsetvli a1, a1, e32, m1, ta,ma  # [op154] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:26:11
vsuxei64.v v1, (s1), v2  # [op155] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:26:11
li s1, 32  # [op156] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:26:11
vsetvli s1, s1, e32, m1, ta,ma  # [op157] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:26:11
li s1, 31  # [op158] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:23
ld a1, 152(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:23
addw a1, s1, a1  # [op159] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:23
sraw a2, a1, s1  # [op160] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:23
and s1, a2, s1  # [op161] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:23
addw s1, a1, s1  # [op162] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:23
sraw s1, s1, t1  # [op163] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:23
li a1, 0  # [op164] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
li a1, 1  # [op165] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
li a1, 32  # [op166] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
add t2, t2, a1  # [op167] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li a1, 32  # [op168] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
addw t0, t0, a1  # [op169] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li a1, 32  # [op170] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
vsetvli a1, a1, e32, m1, ta,ma  # [op171] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li a1, 77704  # [op172] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld a2, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld a2, 16(a2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
add a1, a2, a1  # [op173] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
sw s1, 0(a1)  # [op174] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk2_head  # [op175] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk3_head:  # block chunk3_head
li t2, 32  # [op176] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
slt t2, t0, t2  # [op177] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld s1, 208(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
bne t2, zero, .Lbrc178_true  # [op178] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t0, t1  # [op178] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t1, s1  # [op178] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk3_exit  # [op178] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lbrc178_true:  # [op178] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk3_body  # [op178] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk3_exit:  # block chunk3_exit
li t1, 0  # [op179] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
sd t0, 96(sp)  # [op180] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t0, t1  # [op180] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t1, 96(sp)  # [op180] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk4_head  # [op180] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk3_body:  # block chunk3_body
li t2, 32  # [op181] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
vsetvli t2, t2, e32, m1, ta,ma  # [op182] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 32  # [op183] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vsetvli t2, t2, e32, m1, ta,ma  # [op184] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
ld t2, 168(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vmv.v.x v1, t2  # [op185] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vid.v v2  # [op186] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vadd.vx v2, v2, t0  # [op187] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
li t2, 32  # [op188] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vsetvli t2, t2, e32, m1, ta,ma  # [op189] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vwadd.vx v4, v2, x0  # [op190] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
li t2, 32  # [op191] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vsetvli t2, t2, e64, m2, ta,ma  # [op192] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
li t2, 4  # [op193] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vmul.vx v2, v4, t2  # [op194] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
li t2, 4864  # [op195] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
add t2, s1, t2  # [op196] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
li s1, 32  # [op197] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vsetvli s1, s1, e32, m1, ta,ma  # [op198] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vsuxei64.v v1, (t2), v2  # [op199] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
li t2, 32  # [op200] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vsetvli t2, t2, e32, m1, ta,ma  # [op201] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
ld t2, 152(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vmv.v.x v1, t2  # [op202] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vid.v v2  # [op203] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vadd.vx v2, v2, t0  # [op204] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
li t2, 32  # [op205] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vsetvli t2, t2, e32, m1, ta,ma  # [op206] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vwadd.vx v4, v2, x0  # [op207] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
li t2, 32  # [op208] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vsetvli t2, t2, e64, m2, ta,ma  # [op209] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
li t2, 4  # [op210] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vmul.vx v2, v4, t2  # [op211] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
li t2, 13696  # [op212] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
add t2, s1, t2  # [op213] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
li s1, 32  # [op214] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vsetvli s1, s1, e32, m1, ta,ma  # [op215] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vsuxei64.v v1, (t2), v2  # [op216] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
li t2, 32  # [op217] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vsetvli t2, t2, e32, m1, ta,ma  # [op218] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
ld t2, 168(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
vmv.v.x v1, t2  # [op219] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
li t2, 0  # [op220] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
ld t2, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vmv.v.x v2, t2  # [op221] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vid.v v3  # [op222] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vadd.vx v3, v3, t0  # [op223] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
li t2, 32  # [op224] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vsetvli t2, t2, e32, m1, ta,ma  # [op225] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vwadd.vx v4, v3, x0  # [op226] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
li t2, 32  # [op227] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vsetvli t2, t2, e64, m2, ta,ma  # [op228] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
li t2, 4  # [op229] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vmul.vx v4, v4, t2  # [op230] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
li t2, 34560  # [op231] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
add t2, s1, t2  # [op232] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
li s1, 32  # [op233] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vsetvli s1, s1, e32, m1, ta,ma  # [op234] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vsuxei64.v v2, (t2), v4  # [op235] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
li t2, 32  # [op236] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vsetvli t2, t2, e32, m1, ta,ma  # [op237] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
ld t2, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vmv.v.x v2, t2  # [op238] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vid.v v3  # [op239] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vadd.vx v3, v3, t0  # [op240] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
li t2, 32  # [op241] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vsetvli t2, t2, e32, m1, ta,ma  # [op242] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vwadd.vx v4, v3, x0  # [op243] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
li t2, 32  # [op244] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vsetvli t2, t2, e64, m2, ta,ma  # [op245] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
li t2, 4  # [op246] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vmul.vx v4, v4, t2  # [op247] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
li t2, 43392  # [op248] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
add t2, s1, t2  # [op249] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
li s1, 32  # [op250] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vsetvli s1, s1, e32, m1, ta,ma  # [op251] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vsuxei64.v v2, (t2), v4  # [op252] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
li t2, 32  # [op253] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vsetvli t2, t2, e32, m1, ta,ma  # [op254] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vid.v v2  # [op255] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
vadd.vx v2, v2, t0  # [op256] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
li t2, 32  # [op257] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
vsetvli t2, t2, e32, m1, ta,ma  # [op258] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
vwadd.vx v4, v2, x0  # [op259] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
li t2, 32  # [op260] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
vsetvli t2, t2, e64, m2, ta,ma  # [op261] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
li t2, 4  # [op262] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
vmul.vx v2, v4, t2  # [op263] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
li t2, 128  # [op264] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
add t2, s1, t2  # [op265] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
li s1, 32  # [op266] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
vsetvli s1, s1, e32, m1, ta,ma  # [op267] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
vluxei64.v v4, (t2), v2  # [op268] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
li t2, 32  # [op269] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
vsetvli t2, t2, e32, m1, ta,ma  # [op270] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
vmslt.vv v1, v4, v1  # [op271] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
vid.v v2  # [op272] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
vadd.vx v2, v2, t0  # [op273] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
li t2, 32  # [op274] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
vsetvli t2, t2, e32, m1, ta,ma  # [op275] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
vwadd.vx v4, v2, x0  # [op276] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
li t2, 32  # [op277] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
vsetvli t2, t2, e64, m2, ta,ma  # [op278] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
li t2, 4  # [op279] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
vmul.vx v2, v4, t2  # [op280] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
li t2, 13952  # [op281] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
add t2, s1, t2  # [op282] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
li s1, 32  # [op283] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
vsetvli s1, s1, e32, m1, ta,ma  # [op284] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
li s1, 1  # [op285] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
vmv.v.x v4, s1  # [op286] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
li s1, 0  # [op287] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
vmv.v.x v5, s1  # [op288] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
vmv1r.v v0, v1  # [op289] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
vmerge.vvm v1, v5, v4, v0  # [op290] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
vsuxei64.v v1, (t2), v2  # [op291] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:47
li t2, 32  # [op292] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
add t1, t1, t2  # [op293] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 32  # [op294] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
addw t0, t0, t2  # [op295] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 32  # [op296] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
vsetvli t2, t2, e32, m1, ta,ma  # [op297] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk3_head  # [op298] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk4_head:  # block chunk4_head
li t2, 1024  # [op299] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
slt t2, t0, t2  # [op300] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld s1, 208(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
bne t2, zero, .Lbrc301_true  # [op301] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t0, t1  # [op301] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t1, s1  # [op301] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk4_exit  # [op301] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lbrc301_true:  # [op301] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk4_body  # [op301] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk4_exit:  # block chunk4_exit
li t1, 0  # [op302] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
sd t0, 96(sp)  # [op303] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t0, t1  # [op303] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t1, 96(sp)  # [op303] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk5_head  # [op303] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk4_body:  # block chunk4_body
li t2, 32  # [op304] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
vsetvli t2, t2, e32, m1, ta,ma  # [op305] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 0  # [op306] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li s1, 32  # [op307] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli s1, s1, e16, m1, ta,ma  # [op308] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.v.x v1, t2  # [op309] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t2, 32  # [op310] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli t2, t2, e32, m1, ta,ma  # [op311] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vid.v v2  # [op312] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vadd.vx v2, v2, t0  # [op313] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t2, 32  # [op314] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli t2, t2, e32, m1, ta,ma  # [op315] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vwadd.vx v4, v2, x0  # [op316] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t2, 32  # [op317] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli t2, t2, e64, m2, ta,ma  # [op318] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t2, 4  # [op319] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmul.vx v2, v4, t2  # [op320] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t2, 26368  # [op321] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add t2, s1, t2  # [op322] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li s1, 32  # [op323] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli s1, s1, e16, m1, ta,ma  # [op324] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vfwcvt.f.f.v v4, v1  # [op325] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li s1, 32  # [op326] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli s1, s1, e32, m1, ta,ma  # [op327] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.v.v v1, v4  # [op328] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li s1, 32  # [op329] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli s1, s1, e32, m1, ta,ma  # [op330] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsuxei64.v v1, (t2), v2  # [op331] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t2, 32  # [op332] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli t2, t2, e32, m1, ta,ma  # [op333] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t2, 32  # [op334] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
add t1, t1, t2  # [op335] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 32  # [op336] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
addw t0, t0, t2  # [op337] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 32  # [op338] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
vsetvli t2, t2, e32, m1, ta,ma  # [op339] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk4_head  # [op340] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk5_head:  # block chunk5_head
li t2, 32  # [op341] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
slt t2, t0, t2  # [op342] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld s1, 208(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
bne t2, zero, .Lbrc343_true  # [op343] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t0, s1  # [op343] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv a5, t1  # [op343] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk5_exit  # [op343] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lbrc343_true:  # [op343] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk5_body  # [op343] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk5_exit:  # block chunk5_exit
li t0, 0  # [op344] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
j .Lstg6_head  # [op345] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
.Lchunk5_body:  # block chunk5_body
li t2, 32  # [op346] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
vsetvli t2, t2, e32, m1, ta,ma  # [op347] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 32  # [op348] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vsetvli t2, t2, e32, m1, ta,ma  # [op349] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vid.v v1  # [op350] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vadd.vx v1, v1, t0  # [op351] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
li t2, 32  # [op352] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vsetvli t2, t2, e32, m1, ta,ma  # [op353] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vwadd.vx v2, v1, x0  # [op354] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
li t2, 32  # [op355] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vsetvli t2, t2, e64, m2, ta,ma  # [op356] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
li t2, 4  # [op357] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vmul.vx v2, v2, t2  # [op358] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
li t2, 256  # [op359] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
add t2, s1, t2  # [op360] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
li s1, 32  # [op361] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vsetvli s1, s1, e32, m1, ta,ma  # [op362] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vluxei64.v v1, (t2), v2  # [op363] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
li t2, 32  # [op364] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vsetvli t2, t2, e32, m1, ta,ma  # [op365] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vid.v v2  # [op366] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vadd.vx v2, v2, t0  # [op367] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
li t2, 32  # [op368] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vsetvli t2, t2, e32, m1, ta,ma  # [op369] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vwadd.vx v4, v2, x0  # [op370] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
li t2, 32  # [op371] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vsetvli t2, t2, e64, m2, ta,ma  # [op372] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
li t2, 4  # [op373] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vmul.vx v2, v4, t2  # [op374] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
li t2, 43392  # [op375] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
add t2, s1, t2  # [op376] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
li s1, 32  # [op377] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vsetvli s1, s1, e32, m1, ta,ma  # [op378] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vluxei64.v v4, (t2), v2  # [op379] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
li t2, 32  # [op380] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vsetvli t2, t2, e32, m1, ta,ma  # [op381] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vmslt.vv v1, v1, v4  # [op382] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vid.v v2  # [op383] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vadd.vx v2, v2, t0  # [op384] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
li t2, 32  # [op385] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vsetvli t2, t2, e32, m1, ta,ma  # [op386] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vwadd.vx v4, v2, x0  # [op387] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
li t2, 32  # [op388] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vsetvli t2, t2, e64, m2, ta,ma  # [op389] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
li t2, 4  # [op390] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vmul.vx v2, v4, t2  # [op391] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
li t2, 43520  # [op392] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
add t2, s1, t2  # [op393] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
li s1, 32  # [op394] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vsetvli s1, s1, e32, m1, ta,ma  # [op395] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
li s1, 1  # [op396] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vmv.v.x v4, s1  # [op397] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
li s1, 0  # [op398] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vmv.v.x v5, s1  # [op399] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vmv1r.v v0, v1  # [op400] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vmerge.vvm v1, v5, v4, v0  # [op401] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
vsuxei64.v v1, (t2), v2  # [op402] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:47
li t2, 32  # [op403] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
add t1, t1, t2  # [op404] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 32  # [op405] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
addw t0, t0, t2  # [op406] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 32  # [op407] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
vsetvli t2, t2, e32, m1, ta,ma  # [op408] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk5_head  # [op409] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lstg6_head:  # block stg6_head
li t1, 1024  # [op410] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
slt t1, t0, t1  # [op411] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
bne t1, zero, .Lbrc412_true  # [op412] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
j .Lstg6_exit  # [op412] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
.Lbrc412_true:  # [op412] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
j .Lstg6_body  # [op412] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
.Lstg6_body:  # block stg6_body
li t1, 32  # [op413] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsetvli t1, t1, e32, m1, ta,ma  # [op414] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vid.v v1  # [op415] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vadd.vx v1, v1, t0  # [op416] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t1, 32  # [op417] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vmv.v.x v2, t1  # [op418] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vdiv.vv v2, v1, v2  # [op419] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t1, 32  # [op420] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vmv.v.x v3, t1  # [op421] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vrem.vv v2, v2, v3  # [op422] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t1, 32  # [op423] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vmv.v.x v2, t1  # [op424] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vrem.vv v2, v1, v2  # [op425] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t1, 32  # [op426] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsetvli t1, t1, e32, m1, ta,ma  # [op427] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vwadd.vx v4, v2, x0  # [op428] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t1, 32  # [op429] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsetvli t1, t1, e64, m2, ta,ma  # [op430] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t1, 4  # [op431] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vmul.vx v2, v4, t1  # [op432] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t1, 13952  # [op433] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
ld t2, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
ld t2, 16(t2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
add t1, t2, t1  # [op434] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t2, 32  # [op435] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsetvli t2, t2, e32, m1, ta,ma  # [op436] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vluxei64.v v4, (t1), v2  # [op437] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t1, 32  # [op438] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsetvli t1, t1, e32, m1, ta,ma  # [op439] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vwadd.vx v2, v1, x0  # [op440] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t1, 32  # [op441] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsetvli t1, t1, e64, m2, ta,ma  # [op442] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t1, 4  # [op443] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vmul.vx v2, v2, t1  # [op444] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t1, 18176  # [op445] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
ld t2, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
ld t2, 16(t2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
add t1, t2, t1  # [op446] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t2, 32  # [op447] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsetvli t2, t2, e32, m1, ta,ma  # [op448] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsuxei64.v v4, (t1), v2  # [op449] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t1, 32  # [op450] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
addw t0, t0, t1  # [op451] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
j .Lstg6_head  # [op452] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
.Lstg6_exit:  # block stg6_exit
li t0, 0  # [op453] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
j .Lstg7_head  # [op454] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
.Lstg7_head:  # block stg7_head
li t1, 1024  # [op455] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
slt t1, t0, t1  # [op456] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
bne t1, zero, .Lbrc457_true  # [op457] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
j .Lstg7_exit  # [op457] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
.Lbrc457_true:  # [op457] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
j .Lstg7_body  # [op457] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
.Lstg7_body:  # block stg7_body
li t1, 32  # [op458] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vsetvli t1, t1, e32, m1, ta,ma  # [op459] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vid.v v1  # [op460] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vadd.vx v1, v1, t0  # [op461] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t1, 32  # [op462] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vmv.v.x v2, t1  # [op463] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vdiv.vv v2, v1, v2  # [op464] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t1, 32  # [op465] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vmv.v.x v3, t1  # [op466] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vrem.vv v2, v2, v3  # [op467] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t1, 32  # [op468] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vmv.v.x v2, t1  # [op469] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vrem.vv v2, v1, v2  # [op470] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t1, 32  # [op471] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vsetvli t1, t1, e32, m1, ta,ma  # [op472] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vwadd.vx v4, v2, x0  # [op473] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t1, 32  # [op474] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vsetvli t1, t1, e64, m2, ta,ma  # [op475] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t1, 4  # [op476] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vmul.vx v2, v4, t1  # [op477] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t1, 43520  # [op478] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
ld t2, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
ld t2, 16(t2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
add t1, t2, t1  # [op479] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t2, 32  # [op480] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vsetvli t2, t2, e32, m1, ta,ma  # [op481] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vluxei64.v v4, (t1), v2  # [op482] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t1, 32  # [op483] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vsetvli t1, t1, e32, m1, ta,ma  # [op484] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vwadd.vx v2, v1, x0  # [op485] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t1, 32  # [op486] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vsetvli t1, t1, e64, m2, ta,ma  # [op487] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t1, 4  # [op488] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vmul.vx v2, v2, t1  # [op489] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t1, 43648  # [op490] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
ld t2, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
ld t2, 16(t2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
add t1, t2, t1  # [op491] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t2, 32  # [op492] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vsetvli t2, t2, e32, m1, ta,ma  # [op493] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vsuxei64.v v4, (t1), v2  # [op494] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t1, 32  # [op495] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
addw t0, t0, t1  # [op496] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
j .Lstg7_head  # [op497] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
.Lstg7_exit:  # block stg7_exit
li t0, 0  # [op498] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
j .Lmloop8.head  # [op500] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
.Lmloop8.head:  # block mloop8.head
sd t0, 216(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
ld t0, 216(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
slt t1, t0, s8  # [op501] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
ld t0, 216(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
bne t1, zero, .Lbrc502_true  # [op502] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
j .Lmloop8.exit  # [op502] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
.Lbrc502_true:  # [op502] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
j .Lmloop8.body  # [op502] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
.Lmloop8.body:  # block mloop8.body
sd t0, 216(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
li t0, 32  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
ld t1, 216(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
mulw t2, t0, t1  # [op503] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
li t0, 0  # [op504] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t1, a5  # [op505] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk9_head  # [op505] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lmloop8.exit:  # block mloop8.exit
li t0, 0  # [op506] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t1, a5  # [op507] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk23_head  # [op507] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk9_head:  # block chunk9_head
li s1, 32  # [op508] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
slt s1, t0, s1  # [op509] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld a1, 208(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
bne s1, zero, .Lbrc510_true  # [op510] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t0, t1  # [op510] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t1, a1  # [op510] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk9_exit  # [op510] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lbrc510_true:  # [op510] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk9_body  # [op510] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk9_exit:  # block chunk9_exit
li t1, 0  # [op511] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
sd t0, 96(sp)  # [op512] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t0, t1  # [op512] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t1, 96(sp)  # [op512] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk10_head  # [op512] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk9_body:  # block chunk9_body
li s1, 32  # [op513] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
vsetvli s1, s1, e32, m1, ta,ma  # [op514] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li s1, 32  # [op515] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
vsetvli s1, s1, e32, m1, ta,ma  # [op516] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
vmv.v.x v1, t2  # [op517] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
vid.v v2  # [op518] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
vadd.vx v2, v2, t0  # [op519] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
li s1, 32  # [op520] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
vsetvli s1, s1, e32, m1, ta,ma  # [op521] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
vwadd.vx v4, v2, x0  # [op522] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
li s1, 32  # [op523] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
vsetvli s1, s1, e64, m2, ta,ma  # [op524] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
li s1, 4  # [op525] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
vmul.vx v2, v4, s1  # [op526] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
li s1, 4480  # [op527] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
add s1, a1, s1  # [op528] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
li a1, 32  # [op529] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
vsetvli a1, a1, e32, m1, ta,ma  # [op530] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
vsuxei64.v v1, (s1), v2  # [op531] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
li s1, 32  # [op532] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
vsetvli s1, s1, e32, m1, ta,ma  # [op533] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
vid.v v2  # [op534] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
vadd.vx v2, v2, t0  # [op535] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
li s1, 32  # [op536] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
vsetvli s1, s1, e32, m1, ta,ma  # [op537] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
vwadd.vx v4, v2, x0  # [op538] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
li s1, 32  # [op539] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
vsetvli s1, s1, e64, m2, ta,ma  # [op540] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
li s1, 4  # [op541] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
vmul.vx v2, v4, s1  # [op542] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
li s1, 0  # [op543] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
add s1, a1, s1  # [op544] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
li a1, 32  # [op545] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
vsetvli a1, a1, e32, m1, ta,ma  # [op546] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
vluxei64.v v4, (s1), v2  # [op547] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
li s1, 32  # [op548] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
vsetvli s1, s1, e32, m1, ta,ma  # [op549] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
vadd.vv v1, v1, v4  # [op550] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
vid.v v2  # [op551] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
vadd.vx v2, v2, t0  # [op552] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
li s1, 32  # [op553] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
vsetvli s1, s1, e32, m1, ta,ma  # [op554] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
vwadd.vx v4, v2, x0  # [op555] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
li s1, 32  # [op556] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
vsetvli s1, s1, e64, m2, ta,ma  # [op557] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
li s1, 4  # [op558] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
vmul.vx v2, v4, s1  # [op559] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
li s1, 4608  # [op560] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
add s1, a1, s1  # [op561] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
li a1, 32  # [op562] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
vsetvli a1, a1, e32, m1, ta,ma  # [op563] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
vsuxei64.v v1, (s1), v2  # [op564] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
li s1, 32  # [op565] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
vsetvli s1, s1, e32, m1, ta,ma  # [op566] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:28:14
vid.v v1  # [op567] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vadd.vx v1, v1, t0  # [op568] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
li s1, 32  # [op569] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vsetvli s1, s1, e32, m1, ta,ma  # [op570] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vwadd.vx v2, v1, x0  # [op571] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
li s1, 32  # [op572] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vsetvli s1, s1, e64, m2, ta,ma  # [op573] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
li s1, 4  # [op574] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vmul.vx v2, v2, s1  # [op575] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
li s1, 4608  # [op576] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
add s1, a1, s1  # [op577] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
li a1, 32  # [op578] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vsetvli a1, a1, e32, m1, ta,ma  # [op579] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vluxei64.v v1, (s1), v2  # [op580] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
li s1, 32  # [op581] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vsetvli s1, s1, e32, m1, ta,ma  # [op582] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vid.v v2  # [op583] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vadd.vx v2, v2, t0  # [op584] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
li s1, 32  # [op585] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vsetvli s1, s1, e32, m1, ta,ma  # [op586] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vwadd.vx v4, v2, x0  # [op587] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
li s1, 32  # [op588] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vsetvli s1, s1, e64, m2, ta,ma  # [op589] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
li s1, 4  # [op590] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vmul.vx v2, v4, s1  # [op591] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
li s1, 4864  # [op592] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
add s1, a1, s1  # [op593] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
li a1, 32  # [op594] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vsetvli a1, a1, e32, m1, ta,ma  # [op595] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vluxei64.v v4, (s1), v2  # [op596] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
li s1, 32  # [op597] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vsetvli s1, s1, e32, m1, ta,ma  # [op598] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vmul.vv v1, v1, v4  # [op599] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vid.v v2  # [op600] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vadd.vx v2, v2, t0  # [op601] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
li s1, 32  # [op602] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vsetvli s1, s1, e32, m1, ta,ma  # [op603] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vwadd.vx v4, v2, x0  # [op604] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
li s1, 32  # [op605] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vsetvli s1, s1, e64, m2, ta,ma  # [op606] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
li s1, 4  # [op607] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vmul.vx v2, v4, s1  # [op608] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
li s1, 4992  # [op609] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
add s1, a1, s1  # [op610] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
li a1, 32  # [op611] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vsetvli a1, a1, e32, m1, ta,ma  # [op612] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vsuxei64.v v1, (s1), v2  # [op613] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
li s1, 32  # [op614] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
vsetvli s1, s1, e32, m1, ta,ma  # [op615] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:25
li s1, 32  # [op616] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
add t1, t1, s1  # [op617] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li s1, 32  # [op618] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
addw t0, t0, s1  # [op619] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li s1, 32  # [op620] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
vsetvli s1, s1, e32, m1, ta,ma  # [op621] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk9_head  # [op622] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk10_head:  # block chunk10_head
li t2, 1024  # [op623] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
slt t2, t0, t2  # [op624] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld s1, 208(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
bne t2, zero, .Lbrc625_true  # [op625] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t0, t1  # [op625] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t1, s1  # [op625] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk10_exit  # [op625] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lbrc625_true:  # [op625] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk10_body  # [op625] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk10_exit:  # block chunk10_exit
li t1, 0  # [op626] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
sd t0, 96(sp)  # [op627] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t0, t1  # [op627] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t1, 96(sp)  # [op627] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk11_head  # [op627] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk10_body:  # block chunk10_body
li t2, 32  # [op628] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
vsetvli t2, t2, e32, m1, ta,ma  # [op629] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 32  # [op630] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:21
vsetvli t2, t2, e32, m1, ta,ma  # [op631] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:21
vid.v v1  # [op632] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:21
vadd.vx v1, v1, t0  # [op633] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:21
li t2, 32  # [op634] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:21
vmv.v.x v2, t2  # [op635] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:21
vdiv.vv v1, v1, v2  # [op636] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:21
li t2, 32  # [op637] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:21
vsetvli t2, t2, e32, m1, ta,ma  # [op638] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:21
vwadd.vx v2, v1, x0  # [op639] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:21
li t2, 32  # [op640] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:21
vsetvli t2, t2, e64, m2, ta,ma  # [op641] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:21
li t2, 8  # [op642] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:21
vmul.vx v2, v2, t2  # [op643] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:21
li t2, 5120  # [op644] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:21
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:21
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:21
add t2, s1, t2  # [op645] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:21
li s1, 32  # [op646] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:21
vsetvli s1, s1, e64, m2, ta,ma  # [op647] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:21
vluxei64.v v4, (t2), v2  # [op648] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:21
li t2, 32  # [op649] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:21
vsetvli t2, t2, e32, m1, ta,ma  # [op650] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:21
li t2, 32  # [op651] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
add t1, t1, t2  # [op652] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 32  # [op653] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
addw t0, t0, t2  # [op654] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 32  # [op655] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
vsetvli t2, t2, e32, m1, ta,ma  # [op656] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk10_head  # [op657] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk11_head:  # block chunk11_head
li t2, 32  # [op658] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
slt t2, t0, t2  # [op659] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld s1, 208(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
bne t2, zero, .Lbrc660_true  # [op660] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t0, s1  # [op660] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk11_exit  # [op660] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lbrc660_true:  # [op660] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk11_body  # [op660] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk11_exit:  # block chunk11_exit
li t0, 0  # [op661] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
j .Lstg12_head  # [op662] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
.Lchunk11_body:  # block chunk11_body
li t2, 32  # [op663] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
vsetvli t2, t2, e32, m1, ta,ma  # [op664] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 32  # [op665] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vsetvli t2, t2, e32, m1, ta,ma  # [op666] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vid.v v1  # [op667] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vadd.vx v1, v1, t0  # [op668] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
li t2, 32  # [op669] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vsetvli t2, t2, e32, m1, ta,ma  # [op670] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vwadd.vx v2, v1, x0  # [op671] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
li t2, 32  # [op672] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vsetvli t2, t2, e64, m2, ta,ma  # [op673] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
li t2, 4  # [op674] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vmul.vx v2, v2, t2  # [op675] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
li t2, 4608  # [op676] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
add t2, s1, t2  # [op677] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
li s1, 32  # [op678] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vsetvli s1, s1, e32, m1, ta,ma  # [op679] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vluxei64.v v1, (t2), v2  # [op680] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
li t2, 32  # [op681] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vsetvli t2, t2, e32, m1, ta,ma  # [op682] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vid.v v2  # [op683] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vadd.vx v2, v2, t0  # [op684] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
li t2, 32  # [op685] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vsetvli t2, t2, e32, m1, ta,ma  # [op686] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vwadd.vx v4, v2, x0  # [op687] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
li t2, 32  # [op688] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vsetvli t2, t2, e64, m2, ta,ma  # [op689] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
li t2, 4  # [op690] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vmul.vx v2, v4, t2  # [op691] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
li t2, 13696  # [op692] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
add t2, s1, t2  # [op693] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
li s1, 32  # [op694] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vsetvli s1, s1, e32, m1, ta,ma  # [op695] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vluxei64.v v4, (t2), v2  # [op696] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
li t2, 32  # [op697] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vsetvli t2, t2, e32, m1, ta,ma  # [op698] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vmslt.vv v1, v1, v4  # [op699] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vid.v v2  # [op700] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vadd.vx v2, v2, t0  # [op701] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
li t2, 32  # [op702] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vsetvli t2, t2, e32, m1, ta,ma  # [op703] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vwadd.vx v4, v2, x0  # [op704] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
li t2, 32  # [op705] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vsetvli t2, t2, e64, m2, ta,ma  # [op706] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
li t2, 4  # [op707] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vmul.vx v2, v4, t2  # [op708] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
li t2, 13824  # [op709] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
add t2, s1, t2  # [op710] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
li s1, 32  # [op711] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vsetvli s1, s1, e32, m1, ta,ma  # [op712] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
li s1, 1  # [op713] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vmv.v.x v4, s1  # [op714] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
li s1, 0  # [op715] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vmv.v.x v5, s1  # [op716] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vmv1r.v v0, v1  # [op717] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vmerge.vvm v1, v5, v4, v0  # [op718] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
vsuxei64.v v1, (t2), v2  # [op719] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:27
li t2, 32  # [op720] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
add t1, t1, t2  # [op721] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 32  # [op722] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
addw t0, t0, t2  # [op723] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 32  # [op724] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
vsetvli t2, t2, e32, m1, ta,ma  # [op725] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk11_head  # [op726] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lstg12_head:  # block stg12_head
li t2, 1024  # [op727] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
slt t2, t0, t2  # [op728] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
bne t2, zero, .Lbrc729_true  # [op729] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
j .Lstg12_exit  # [op729] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
.Lbrc729_true:  # [op729] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
j .Lstg12_body  # [op729] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
.Lstg12_body:  # block stg12_body
li t2, 32  # [op730] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsetvli t2, t2, e32, m1, ta,ma  # [op731] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vid.v v1  # [op732] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vadd.vx v1, v1, t0  # [op733] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t2, 32  # [op734] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vmv.v.x v2, t2  # [op735] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vdiv.vv v2, v1, v2  # [op736] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t2, 32  # [op737] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vmv.v.x v3, t2  # [op738] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vrem.vv v2, v2, v3  # [op739] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t2, 32  # [op740] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vmv.v.x v3, t2  # [op741] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vrem.vv v3, v1, v3  # [op742] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t2, 32  # [op743] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsetvli t2, t2, e32, m1, ta,ma  # [op744] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vwadd.vx v4, v2, x0  # [op745] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t2, 32  # [op746] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsetvli t2, t2, e64, m2, ta,ma  # [op747] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t2, 4  # [op748] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vmul.vx v2, v4, t2  # [op749] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t2, 13824  # [op750] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
add t2, s1, t2  # [op751] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li s1, 32  # [op752] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsetvli s1, s1, e32, m1, ta,ma  # [op753] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vluxei64.v v4, (t2), v2  # [op754] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t2, 32  # [op755] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsetvli t2, t2, e32, m1, ta,ma  # [op756] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vwadd.vx v2, v1, x0  # [op757] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t2, 32  # [op758] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsetvli t2, t2, e64, m2, ta,ma  # [op759] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t2, 4  # [op760] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vmul.vx v2, v2, t2  # [op761] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t2, 14080  # [op762] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
add t2, s1, t2  # [op763] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li s1, 32  # [op764] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsetvli s1, s1, e32, m1, ta,ma  # [op765] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsuxei64.v v4, (t2), v2  # [op766] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t2, 32  # [op767] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
addw t0, t0, t2  # [op768] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
j .Lstg12_head  # [op769] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
.Lstg12_exit:  # block stg12_exit
li t0, 0  # [op770] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t2, t0  # [op771] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv s1, t1  # [op771] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk13_head  # [op771] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk13_head:  # block chunk13_head
li t0, 1024  # [op772] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
slt t0, t2, t0  # [op773] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t1, 208(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
bne t0, zero, .Lbrc774_true  # [op774] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t0, s1  # [op774] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk13_exit  # [op774] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lbrc774_true:  # [op774] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk13_body  # [op774] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk13_exit:  # block chunk13_exit
li t1, 0  # [op775] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
sd t0, 96(sp)  # [op776] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t0, t1  # [op776] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t1, 96(sp)  # [op776] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk14_head  # [op776] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk13_body:  # block chunk13_body
li t0, 32  # [op777] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
vsetvli t0, t0, e16, m1, ta,ma  # [op778] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t0, 32  # [op779] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsetvli t0, t0, e32, m1, ta,ma  # [op780] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vid.v v1  # [op781] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vadd.vx v1, v1, t2  # [op782] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t0, 32  # [op783] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsetvli t0, t0, e32, m1, ta,ma  # [op784] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vwadd.vx v2, v1, x0  # [op785] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t0, 32  # [op786] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsetvli t0, t0, e64, m2, ta,ma  # [op787] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t0, 4  # [op788] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vmul.vx v2, v2, t0  # [op789] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t0, 14080  # [op790] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
add t0, t1, t0  # [op791] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t1, 32  # [op792] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsetvli t1, t1, e32, m1, ta,ma  # [op793] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vluxei64.v v1, (t0), v2  # [op794] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t0, 0  # [op795] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vmv.v.x v2, t0  # [op796] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vmsne.vv v1, v1, v2  # [op797] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t0, 32  # [op798] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsetvli t0, t0, e16, m1, ta,ma  # [op799] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t0, 32  # [op800] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsetvli t0, t0, e32, m1, ta,ma  # [op801] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vid.v v2  # [op802] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vadd.vx v2, v2, t2  # [op803] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t0, 32  # [op804] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsetvli t0, t0, e32, m1, ta,ma  # [op805] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vwadd.vx v4, v2, x0  # [op806] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t0, 32  # [op807] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsetvli t0, t0, e64, m2, ta,ma  # [op808] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t0, 4  # [op809] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vmul.vx v2, v4, t0  # [op810] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t0, 18176  # [op811] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
add t0, t1, t0  # [op812] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t1, 32  # [op813] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsetvli t1, t1, e32, m1, ta,ma  # [op814] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vluxei64.v v4, (t0), v2  # [op815] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t0, 0  # [op816] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vmv.v.x v2, t0  # [op817] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vmsne.vv v2, v4, v2  # [op818] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t0, 32  # [op819] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsetvli t0, t0, e16, m1, ta,ma  # [op820] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vmand.mm v1, v1, v2  # [op821] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t0, 32  # [op822] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsetvli t0, t0, e32, m1, ta,ma  # [op823] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vid.v v2  # [op824] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vadd.vx v2, v2, t2  # [op825] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t0, 32  # [op826] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsetvli t0, t0, e32, m1, ta,ma  # [op827] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vwadd.vx v4, v2, x0  # [op828] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t0, 32  # [op829] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsetvli t0, t0, e64, m2, ta,ma  # [op830] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t0, 4  # [op831] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vmul.vx v2, v4, t0  # [op832] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t0, 22272  # [op833] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
add t0, t1, t0  # [op834] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t1, 32  # [op835] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsetvli t1, t1, e32, m1, ta,ma  # [op836] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t1, 1  # [op837] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vmv.v.x v4, t1  # [op838] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t1, 0  # [op839] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vmv.v.x v5, t1  # [op840] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vmv1r.v v0, v1  # [op841] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vmerge.vvm v4, v5, v4, v0  # [op842] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsuxei64.v v4, (t0), v2  # [op843] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t0, 32  # [op844] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsetvli t0, t0, e16, m1, ta,ma  # [op845] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t0, 32  # [op846] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsetvli t0, t0, e32, m1, ta,ma  # [op847] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vid.v v2  # [op848] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vadd.vx v2, v2, t2  # [op849] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t0, 32  # [op850] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsetvli t0, t0, e32, m1, ta,ma  # [op851] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vwadd.vx v4, v2, x0  # [op852] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t0, 32  # [op853] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsetvli t0, t0, e64, m2, ta,ma  # [op854] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t0, 4  # [op855] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vmul.vx v2, v4, t0  # [op856] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t0, 22272  # [op857] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
add t0, t1, t0  # [op858] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t1, 32  # [op859] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsetvli t1, t1, e32, m1, ta,ma  # [op860] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t1, 1  # [op861] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vmv.v.x v4, t1  # [op862] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t1, 0  # [op863] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vmv.v.x v5, t1  # [op864] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vmv1r.v v0, v1  # [op865] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vmerge.vvm v4, v5, v4, v0  # [op866] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsuxei64.v v4, (t0), v2  # [op867] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t0, 32  # [op868] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
vsetvli t0, t0, e16, m1, ta,ma  # [op869] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:30:26
li t0, 32  # [op870] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli t0, t0, e32, m1, ta,ma  # [op871] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vid.v v2  # [op872] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vadd.vx v2, v2, t2  # [op873] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t0, 32  # [op874] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.v.x v3, t0  # [op875] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vdiv.vv v2, v2, v3  # [op876] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t0, 32  # [op877] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli t0, t0, e32, m1, ta,ma  # [op878] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vwadd.vx v4, v2, x0  # [op879] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t0, 32  # [op880] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli t0, t0, e64, m2, ta,ma  # [op881] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t0, 4  # [op882] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmul.vx v2, v4, t0  # [op883] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t0, 4992  # [op884] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add t0, t1, t0  # [op885] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t1, 32  # [op886] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli t1, t1, e32, m1, ta,ma  # [op887] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vluxei64.v v4, (t0), v2  # [op888] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t0, 32  # [op889] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli t0, t0, e16, m1, ta,ma  # [op890] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t0, 32  # [op891] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli t0, t0, e32, m1, ta,ma  # [op892] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vid.v v2  # [op893] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vadd.vx v2, v2, t2  # [op894] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t0, 32  # [op895] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.v.x v3, t0  # [op896] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vrem.vv v2, v2, v3  # [op897] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t0, 32  # [op898] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli t0, t0, e32, m1, ta,ma  # [op899] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vwadd.vx v6, v2, x0  # [op900] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t0, 32  # [op901] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli t0, t0, e64, m2, ta,ma  # [op902] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t0, 4  # [op903] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmul.vx v2, v6, t0  # [op904] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t0, 128  # [op905] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add t0, t1, t0  # [op906] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t1, 32  # [op907] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli t1, t1, e32, m1, ta,ma  # [op908] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vluxei64.v v5, (t0), v2  # [op909] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t0, 32  # [op910] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli t0, t0, e16, m1, ta,ma  # [op911] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t0, 32  # [op912] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli t0, t0, e32, m1, ta,ma  # [op913] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vadd.vv v2, v4, v5  # [op914] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t0, 32  # [op915] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli t0, t0, e16, m1, ta,ma  # [op916] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t0, 32  # [op917] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli t0, t0, e32, m1, ta,ma  # [op918] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vwadd.vx v4, v2, x0  # [op919] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t0, 32  # [op920] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli t0, t0, e64, m2, ta,ma  # [op921] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t0, 2  # [op922] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmul.vx v2, v4, t0  # [op923] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t0, 32  # [op924] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli t0, t0, e16, m1, ta,ma  # [op925] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t0, 77568  # [op926] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add t0, t1, t0  # [op927] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t1, 128  # [op928] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add t1, t0, t1  # [op929] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op930] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e32, m1, ta,ma  # [op931] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 0  # [op932] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.v.x v4, a1  # [op933] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 1  # [op934] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.v.x v5, a1  # [op935] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv1r.v v0, v1  # [op936] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmerge.vvm v4, v4, v5, v0  # [op937] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vid.v v1  # [op938] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vadd.vx v1, v1, t2  # [op939] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op940] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e32, m1, ta,ma  # [op941] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vwadd.vx v6, v1, x0  # [op942] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op943] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e64, m2, ta,ma  # [op944] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 4  # [op945] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmul.vx v6, v6, a1  # [op946] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 26368  # [op947] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
ld a2, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
ld a2, 16(a2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add a1, a2, a1  # [op948] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a2, 32  # [op949] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a2, a2, e32, m1, ta,ma  # [op950] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vluxei64.v v1, (a1), v6  # [op951] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op952] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e32, m1, ta,ma  # [op953] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.v.v v6, v1  # [op954] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op955] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e16, m1, ta,ma  # [op956] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vfncvt.f.f.w v1, v6  # [op957] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op958] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e64, m2, ta,ma  # [op959] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vadd.vx v6, v2, s3  # [op960] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op961] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e32, m1, ta,ma  # [op962] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 0  # [op963] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.v.x v2, a1  # [op964] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmsne.vv v2, v4, v2  # [op965] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv1r.v v0, v2  # [op966] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op967] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e64, m2, ta,ma  # [op968] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 0  # [op969] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.v.x v4, a1  # [op970] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.v.x v2, t1  # [op971] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsub.vv v6, v6, v2  # [op972] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmerge.vvm v4, v4, v6, v0  # [op973] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vadd.vv v2, v2, v4  # [op974] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op975] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e16, m1, ta,ma  # [op976] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op977] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e64, m2, ta,ma  # [op978] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a1, v2  # [op979] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a2, 0  # [op980] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add a2, t0, a2  # [op981] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a3, 32  # [op982] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a3, a3, e16, m1, ta,ma  # [op983] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a3, v1  # [op984] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a3, 0(t1)  # [op985] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v1, v1, 1  # [op986] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
lhu a1, 0(a1)  # [op987] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a1, 0(a2)  # [op988] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op989] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e64, m2, ta,ma  # [op990] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v2, v2, 1  # [op991] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a1, v2  # [op992] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a2, 2  # [op993] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add a2, t0, a2  # [op994] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a3, 32  # [op995] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a3, a3, e16, m1, ta,ma  # [op996] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a3, v1  # [op997] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a3, 0(t1)  # [op998] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v1, v1, 1  # [op999] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
lhu a1, 0(a1)  # [op1000] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a1, 0(a2)  # [op1001] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op1002] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1003] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v2, v2, 1  # [op1004] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a1, v2  # [op1005] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a2, 4  # [op1006] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add a2, t0, a2  # [op1007] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a3, 32  # [op1008] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1009] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a3, v1  # [op1010] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a3, 0(t1)  # [op1011] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v1, v1, 1  # [op1012] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
lhu a1, 0(a1)  # [op1013] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a1, 0(a2)  # [op1014] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op1015] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1016] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v2, v2, 1  # [op1017] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a1, v2  # [op1018] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a2, 6  # [op1019] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add a2, t0, a2  # [op1020] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a3, 32  # [op1021] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1022] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a3, v1  # [op1023] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a3, 0(t1)  # [op1024] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v1, v1, 1  # [op1025] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
lhu a1, 0(a1)  # [op1026] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a1, 0(a2)  # [op1027] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op1028] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1029] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v2, v2, 1  # [op1030] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a1, v2  # [op1031] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a2, 8  # [op1032] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add a2, t0, a2  # [op1033] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a3, 32  # [op1034] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1035] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a3, v1  # [op1036] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a3, 0(t1)  # [op1037] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v1, v1, 1  # [op1038] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
lhu a1, 0(a1)  # [op1039] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a1, 0(a2)  # [op1040] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op1041] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1042] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v2, v2, 1  # [op1043] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a1, v2  # [op1044] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a2, 10  # [op1045] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add a2, t0, a2  # [op1046] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a3, 32  # [op1047] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1048] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a3, v1  # [op1049] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a3, 0(t1)  # [op1050] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v1, v1, 1  # [op1051] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
lhu a1, 0(a1)  # [op1052] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a1, 0(a2)  # [op1053] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op1054] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1055] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v2, v2, 1  # [op1056] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a1, v2  # [op1057] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a2, 12  # [op1058] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add a2, t0, a2  # [op1059] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a3, 32  # [op1060] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1061] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a3, v1  # [op1062] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a3, 0(t1)  # [op1063] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v1, v1, 1  # [op1064] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
lhu a1, 0(a1)  # [op1065] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a1, 0(a2)  # [op1066] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op1067] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1068] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v2, v2, 1  # [op1069] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a1, v2  # [op1070] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a2, 14  # [op1071] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add a2, t0, a2  # [op1072] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a3, 32  # [op1073] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1074] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a3, v1  # [op1075] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a3, 0(t1)  # [op1076] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v1, v1, 1  # [op1077] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
lhu a1, 0(a1)  # [op1078] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a1, 0(a2)  # [op1079] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op1080] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1081] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v2, v2, 1  # [op1082] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a1, v2  # [op1083] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a2, 16  # [op1084] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add a2, t0, a2  # [op1085] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a3, 32  # [op1086] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1087] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a3, v1  # [op1088] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a3, 0(t1)  # [op1089] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v1, v1, 1  # [op1090] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
lhu a1, 0(a1)  # [op1091] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a1, 0(a2)  # [op1092] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op1093] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1094] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v2, v2, 1  # [op1095] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a1, v2  # [op1096] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a2, 18  # [op1097] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add a2, t0, a2  # [op1098] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a3, 32  # [op1099] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1100] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a3, v1  # [op1101] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a3, 0(t1)  # [op1102] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v1, v1, 1  # [op1103] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
lhu a1, 0(a1)  # [op1104] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a1, 0(a2)  # [op1105] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op1106] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1107] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v2, v2, 1  # [op1108] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a1, v2  # [op1109] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a2, 20  # [op1110] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add a2, t0, a2  # [op1111] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a3, 32  # [op1112] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1113] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a3, v1  # [op1114] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a3, 0(t1)  # [op1115] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v1, v1, 1  # [op1116] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
lhu a1, 0(a1)  # [op1117] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a1, 0(a2)  # [op1118] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op1119] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1120] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v2, v2, 1  # [op1121] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a1, v2  # [op1122] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a2, 22  # [op1123] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add a2, t0, a2  # [op1124] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a3, 32  # [op1125] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1126] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a3, v1  # [op1127] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a3, 0(t1)  # [op1128] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v1, v1, 1  # [op1129] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
lhu a1, 0(a1)  # [op1130] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a1, 0(a2)  # [op1131] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op1132] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1133] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v2, v2, 1  # [op1134] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a1, v2  # [op1135] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a2, 24  # [op1136] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add a2, t0, a2  # [op1137] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a3, 32  # [op1138] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1139] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a3, v1  # [op1140] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a3, 0(t1)  # [op1141] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v1, v1, 1  # [op1142] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
lhu a1, 0(a1)  # [op1143] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a1, 0(a2)  # [op1144] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op1145] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1146] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v2, v2, 1  # [op1147] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a1, v2  # [op1148] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a2, 26  # [op1149] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add a2, t0, a2  # [op1150] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a3, 32  # [op1151] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1152] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a3, v1  # [op1153] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a3, 0(t1)  # [op1154] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v1, v1, 1  # [op1155] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
lhu a1, 0(a1)  # [op1156] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a1, 0(a2)  # [op1157] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op1158] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1159] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v2, v2, 1  # [op1160] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a1, v2  # [op1161] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a2, 28  # [op1162] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add a2, t0, a2  # [op1163] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a3, 32  # [op1164] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1165] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a3, v1  # [op1166] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a3, 0(t1)  # [op1167] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v1, v1, 1  # [op1168] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
lhu a1, 0(a1)  # [op1169] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a1, 0(a2)  # [op1170] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op1171] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1172] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v2, v2, 1  # [op1173] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a1, v2  # [op1174] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a2, 30  # [op1175] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add a2, t0, a2  # [op1176] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a3, 32  # [op1177] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1178] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a3, v1  # [op1179] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a3, 0(t1)  # [op1180] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v1, v1, 1  # [op1181] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
lhu a1, 0(a1)  # [op1182] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a1, 0(a2)  # [op1183] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op1184] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1185] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v2, v2, 1  # [op1186] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a1, v2  # [op1187] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a2, 32  # [op1188] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add a2, t0, a2  # [op1189] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a3, 32  # [op1190] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1191] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a3, v1  # [op1192] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a3, 0(t1)  # [op1193] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v1, v1, 1  # [op1194] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
lhu a1, 0(a1)  # [op1195] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a1, 0(a2)  # [op1196] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op1197] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1198] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v2, v2, 1  # [op1199] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a1, v2  # [op1200] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a2, 34  # [op1201] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add a2, t0, a2  # [op1202] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a3, 32  # [op1203] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1204] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a3, v1  # [op1205] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a3, 0(t1)  # [op1206] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v1, v1, 1  # [op1207] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
lhu a1, 0(a1)  # [op1208] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a1, 0(a2)  # [op1209] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op1210] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1211] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v2, v2, 1  # [op1212] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a1, v2  # [op1213] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a2, 36  # [op1214] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add a2, t0, a2  # [op1215] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a3, 32  # [op1216] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1217] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a3, v1  # [op1218] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a3, 0(t1)  # [op1219] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v1, v1, 1  # [op1220] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
lhu a1, 0(a1)  # [op1221] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a1, 0(a2)  # [op1222] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op1223] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1224] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v2, v2, 1  # [op1225] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a1, v2  # [op1226] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a2, 38  # [op1227] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add a2, t0, a2  # [op1228] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a3, 32  # [op1229] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1230] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a3, v1  # [op1231] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a3, 0(t1)  # [op1232] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v1, v1, 1  # [op1233] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
lhu a1, 0(a1)  # [op1234] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a1, 0(a2)  # [op1235] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op1236] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1237] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v2, v2, 1  # [op1238] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a1, v2  # [op1239] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a2, 40  # [op1240] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add a2, t0, a2  # [op1241] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a3, 32  # [op1242] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1243] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a3, v1  # [op1244] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a3, 0(t1)  # [op1245] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v1, v1, 1  # [op1246] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
lhu a1, 0(a1)  # [op1247] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a1, 0(a2)  # [op1248] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op1249] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1250] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v2, v2, 1  # [op1251] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a1, v2  # [op1252] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a2, 42  # [op1253] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add a2, t0, a2  # [op1254] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a3, 32  # [op1255] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1256] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a3, v1  # [op1257] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a3, 0(t1)  # [op1258] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v1, v1, 1  # [op1259] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
lhu a1, 0(a1)  # [op1260] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a1, 0(a2)  # [op1261] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op1262] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1263] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v2, v2, 1  # [op1264] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a1, v2  # [op1265] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a2, 44  # [op1266] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add a2, t0, a2  # [op1267] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a3, 32  # [op1268] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1269] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a3, v1  # [op1270] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a3, 0(t1)  # [op1271] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v1, v1, 1  # [op1272] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
lhu a1, 0(a1)  # [op1273] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a1, 0(a2)  # [op1274] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op1275] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1276] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v2, v2, 1  # [op1277] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a1, v2  # [op1278] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a2, 46  # [op1279] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add a2, t0, a2  # [op1280] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a3, 32  # [op1281] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1282] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a3, v1  # [op1283] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a3, 0(t1)  # [op1284] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v1, v1, 1  # [op1285] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
lhu a1, 0(a1)  # [op1286] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a1, 0(a2)  # [op1287] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op1288] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1289] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v2, v2, 1  # [op1290] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a1, v2  # [op1291] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a2, 48  # [op1292] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add a2, t0, a2  # [op1293] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a3, 32  # [op1294] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1295] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a3, v1  # [op1296] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a3, 0(t1)  # [op1297] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v1, v1, 1  # [op1298] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
lhu a1, 0(a1)  # [op1299] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a1, 0(a2)  # [op1300] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op1301] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1302] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v2, v2, 1  # [op1303] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a1, v2  # [op1304] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a2, 50  # [op1305] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add a2, t0, a2  # [op1306] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a3, 32  # [op1307] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1308] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a3, v1  # [op1309] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a3, 0(t1)  # [op1310] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v1, v1, 1  # [op1311] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
lhu a1, 0(a1)  # [op1312] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a1, 0(a2)  # [op1313] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op1314] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1315] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v2, v2, 1  # [op1316] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a1, v2  # [op1317] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a2, 52  # [op1318] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add a2, t0, a2  # [op1319] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a3, 32  # [op1320] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1321] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a3, v1  # [op1322] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a3, 0(t1)  # [op1323] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v1, v1, 1  # [op1324] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
lhu a1, 0(a1)  # [op1325] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a1, 0(a2)  # [op1326] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op1327] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1328] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v2, v2, 1  # [op1329] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a1, v2  # [op1330] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a2, 54  # [op1331] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add a2, t0, a2  # [op1332] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a3, 32  # [op1333] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1334] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a3, v1  # [op1335] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a3, 0(t1)  # [op1336] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v1, v1, 1  # [op1337] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
lhu a1, 0(a1)  # [op1338] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a1, 0(a2)  # [op1339] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op1340] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1341] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v2, v2, 1  # [op1342] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a1, v2  # [op1343] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a2, 56  # [op1344] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add a2, t0, a2  # [op1345] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a3, 32  # [op1346] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1347] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a3, v1  # [op1348] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a3, 0(t1)  # [op1349] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v1, v1, 1  # [op1350] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
lhu a1, 0(a1)  # [op1351] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a1, 0(a2)  # [op1352] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op1353] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1354] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v2, v2, 1  # [op1355] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a1, v2  # [op1356] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a2, 58  # [op1357] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add a2, t0, a2  # [op1358] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a3, 32  # [op1359] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1360] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a3, v1  # [op1361] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a3, 0(t1)  # [op1362] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v1, v1, 1  # [op1363] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
lhu a1, 0(a1)  # [op1364] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a1, 0(a2)  # [op1365] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op1366] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1367] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v2, v2, 1  # [op1368] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a1, v2  # [op1369] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a2, 60  # [op1370] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add a2, t0, a2  # [op1371] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a3, 32  # [op1372] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1373] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a3, v1  # [op1374] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a3, 0(t1)  # [op1375] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v1, v1, 1  # [op1376] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
lhu a1, 0(a1)  # [op1377] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a1, 0(a2)  # [op1378] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a1, 32  # [op1379] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1380] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v2, v2, 1  # [op1381] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a1, v2  # [op1382] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a2, 62  # [op1383] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add a2, t0, a2  # [op1384] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li a3, 32  # [op1385] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1386] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.x.s a3, v1  # [op1387] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh a3, 0(t1)  # [op1388] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v1, v1, 1  # [op1389] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
lhu t1, 0(a1)  # [op1390] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
sh t1, 0(a2)  # [op1391] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t1, 32  # [op1392] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli t1, t1, e64, m2, ta,ma  # [op1393] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vslidedown.vi v2, v2, 1  # [op1394] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t1, 32  # [op1395] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli t1, t1, e16, m1, ta,ma  # [op1396] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vle16.v v1, 0(t0)  # [op1397] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t0, 32  # [op1398] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli t0, t0, e32, m1, ta,ma  # [op1399] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vid.v v2  # [op1400] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vadd.vx v2, v2, t2  # [op1401] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t0, 32  # [op1402] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli t0, t0, e32, m1, ta,ma  # [op1403] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vwadd.vx v4, v2, x0  # [op1404] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t0, 32  # [op1405] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli t0, t0, e64, m2, ta,ma  # [op1406] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t0, 4  # [op1407] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmul.vx v2, v4, t0  # [op1408] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t0, 30464  # [op1409] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
add t0, t1, t0  # [op1410] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t1, 32  # [op1411] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli t1, t1, e16, m1, ta,ma  # [op1412] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vfwcvt.f.f.v v4, v1  # [op1413] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t1, 32  # [op1414] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli t1, t1, e32, m1, ta,ma  # [op1415] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vmv.v.v v1, v4  # [op1416] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t1, 32  # [op1417] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli t1, t1, e16, m1, ta,ma  # [op1418] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t1, 32  # [op1419] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli t1, t1, e32, m1, ta,ma  # [op1420] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsuxei64.v v1, (t0), v2  # [op1421] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t0, 32  # [op1422] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
vsetvli t0, t0, e16, m1, ta,ma  # [op1423] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:29:13
li t0, 32  # [op1424] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
add t0, s1, t0  # [op1425] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t1, 32  # [op1426] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
addw t1, t2, t1  # [op1427] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 32  # [op1428] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
vsetvli t2, t2, e16, m1, ta,ma  # [op1429] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t2, t1  # [op1430] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv s1, t0  # [op1430] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk13_head  # [op1430] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk14_head:  # block chunk14_head
li t2, 32  # [op1431] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
slt t2, t0, t2  # [op1432] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld s1, 208(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
bne t2, zero, .Lbrc1433_true  # [op1433] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t0, t1  # [op1433] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t1, s1  # [op1433] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk14_exit  # [op1433] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lbrc1433_true:  # [op1433] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk14_body  # [op1433] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk14_exit:  # block chunk14_exit
li t1, 0  # [op1434] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t2, t1  # [op1435] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv s1, t0  # [op1435] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk15_head  # [op1435] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk14_body:  # block chunk14_body
li t2, 32  # [op1436] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
vsetvli t2, t2, e32, m1, ta,ma  # [op1437] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 32  # [op1438] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vsetvli t2, t2, e32, m1, ta,ma  # [op1439] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vid.v v1  # [op1440] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vadd.vx v1, v1, t0  # [op1441] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
li t2, 32  # [op1442] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vsetvli t2, t2, e32, m1, ta,ma  # [op1443] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vwadd.vx v2, v1, x0  # [op1444] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
li t2, 32  # [op1445] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vsetvli t2, t2, e64, m2, ta,ma  # [op1446] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
li t2, 4  # [op1447] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vmul.vx v2, v2, t2  # [op1448] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
li t2, 4608  # [op1449] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
add t2, s1, t2  # [op1450] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
li s1, 32  # [op1451] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vsetvli s1, s1, e32, m1, ta,ma  # [op1452] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vluxei64.v v1, (t2), v2  # [op1453] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
li t2, 32  # [op1454] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vsetvli t2, t2, e32, m1, ta,ma  # [op1455] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vid.v v2  # [op1456] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vadd.vx v2, v2, t0  # [op1457] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
li t2, 32  # [op1458] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vsetvli t2, t2, e32, m1, ta,ma  # [op1459] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vwadd.vx v4, v2, x0  # [op1460] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
li t2, 32  # [op1461] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vsetvli t2, t2, e64, m2, ta,ma  # [op1462] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
li t2, 4  # [op1463] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vmul.vx v2, v4, t2  # [op1464] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
li t2, 34560  # [op1465] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
add t2, s1, t2  # [op1466] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
li s1, 32  # [op1467] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vsetvli s1, s1, e32, m1, ta,ma  # [op1468] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vluxei64.v v4, (t2), v2  # [op1469] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
li t2, 32  # [op1470] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vsetvli t2, t2, e32, m1, ta,ma  # [op1471] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vmul.vv v1, v1, v4  # [op1472] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vid.v v2  # [op1473] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vadd.vx v2, v2, t0  # [op1474] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
li t2, 32  # [op1475] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vsetvli t2, t2, e32, m1, ta,ma  # [op1476] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vwadd.vx v4, v2, x0  # [op1477] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
li t2, 32  # [op1478] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vsetvli t2, t2, e64, m2, ta,ma  # [op1479] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
li t2, 4  # [op1480] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vmul.vx v2, v4, t2  # [op1481] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
li t2, 34688  # [op1482] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
add t2, s1, t2  # [op1483] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
li s1, 32  # [op1484] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vsetvli s1, s1, e32, m1, ta,ma  # [op1485] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vsuxei64.v v1, (t2), v2  # [op1486] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
li t2, 32  # [op1487] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
vsetvli t2, t2, e32, m1, ta,ma  # [op1488] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:25
li t2, 32  # [op1489] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
add t1, t1, t2  # [op1490] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 32  # [op1491] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
addw t0, t0, t2  # [op1492] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 32  # [op1493] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
vsetvli t2, t2, e32, m1, ta,ma  # [op1494] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk14_head  # [op1495] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk15_head:  # block chunk15_head
li t0, 1024  # [op1496] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
slt t0, t2, t0  # [op1497] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t1, 208(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
bne t0, zero, .Lbrc1498_true  # [op1498] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t0, t1  # [op1498] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv s9, s1  # [op1498] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk15_exit  # [op1498] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lbrc1498_true:  # [op1498] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk15_body  # [op1498] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk15_exit:  # block chunk15_exit
li t0, 0  # [op1499] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
j .Lstg16_head  # [op1500] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
.Lchunk15_body:  # block chunk15_body
li t0, 32  # [op1501] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
vsetvli t0, t0, e16, m1, ta,ma  # [op1502] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t0, 32  # [op1503] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:21
vsetvli t0, t0, e32, m1, ta,ma  # [op1504] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:21
vid.v v1  # [op1505] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:21
vadd.vx v1, v1, t2  # [op1506] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:21
li t0, 32  # [op1507] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:21
vmv.v.x v2, t0  # [op1508] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:21
vdiv.vv v1, v1, v2  # [op1509] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:21
li t0, 32  # [op1510] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:21
vsetvli t0, t0, e32, m1, ta,ma  # [op1511] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:21
vwadd.vx v2, v1, x0  # [op1512] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:21
li t0, 32  # [op1513] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:21
vsetvli t0, t0, e64, m2, ta,ma  # [op1514] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:21
li t0, 8  # [op1515] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:21
vmul.vx v2, v2, t0  # [op1516] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:21
li t0, 34816  # [op1517] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:21
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:21
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:21
add t0, t1, t0  # [op1518] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:21
li t1, 32  # [op1519] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:21
vsetvli t1, t1, e64, m2, ta,ma  # [op1520] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:21
vluxei64.v v4, (t0), v2  # [op1521] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:21
li t0, 32  # [op1522] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:21
vsetvli t0, t0, e16, m1, ta,ma  # [op1523] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:21
li t0, 32  # [op1524] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vsetvli t0, t0, e32, m1, ta,ma  # [op1525] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vid.v v1  # [op1526] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vadd.vx v1, v1, t2  # [op1527] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t0, 32  # [op1528] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vsetvli t0, t0, e32, m1, ta,ma  # [op1529] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vwadd.vx v2, v1, x0  # [op1530] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t0, 32  # [op1531] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vsetvli t0, t0, e64, m2, ta,ma  # [op1532] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t0, 4  # [op1533] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vmul.vx v2, v2, t0  # [op1534] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t0, 14080  # [op1535] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
add t0, t1, t0  # [op1536] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t1, 32  # [op1537] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vsetvli t1, t1, e32, m1, ta,ma  # [op1538] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vluxei64.v v1, (t0), v2  # [op1539] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t0, 0  # [op1540] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vmv.v.x v2, t0  # [op1541] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vmsne.vv v1, v1, v2  # [op1542] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t0, 32  # [op1543] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vsetvli t0, t0, e16, m1, ta,ma  # [op1544] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t0, 32  # [op1545] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vsetvli t0, t0, e32, m1, ta,ma  # [op1546] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vid.v v2  # [op1547] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vadd.vx v2, v2, t2  # [op1548] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t0, 32  # [op1549] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vsetvli t0, t0, e32, m1, ta,ma  # [op1550] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vwadd.vx v4, v2, x0  # [op1551] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t0, 32  # [op1552] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vsetvli t0, t0, e64, m2, ta,ma  # [op1553] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t0, 4  # [op1554] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vmul.vx v2, v4, t0  # [op1555] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t0, 43648  # [op1556] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
add t0, t1, t0  # [op1557] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t1, 32  # [op1558] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vsetvli t1, t1, e32, m1, ta,ma  # [op1559] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vluxei64.v v4, (t0), v2  # [op1560] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t0, 0  # [op1561] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vmv.v.x v2, t0  # [op1562] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vmsne.vv v2, v4, v2  # [op1563] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t0, 32  # [op1564] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vsetvli t0, t0, e16, m1, ta,ma  # [op1565] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vmand.mm v1, v1, v2  # [op1566] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t0, 32  # [op1567] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vsetvli t0, t0, e32, m1, ta,ma  # [op1568] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vid.v v2  # [op1569] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vadd.vx v2, v2, t2  # [op1570] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t0, 32  # [op1571] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vsetvli t0, t0, e32, m1, ta,ma  # [op1572] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vwadd.vx v4, v2, x0  # [op1573] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t0, 32  # [op1574] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vsetvli t0, t0, e64, m2, ta,ma  # [op1575] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t0, 4  # [op1576] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vmul.vx v2, v4, t0  # [op1577] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t0, 47744  # [op1578] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
add t0, t1, t0  # [op1579] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t1, 32  # [op1580] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vsetvli t1, t1, e32, m1, ta,ma  # [op1581] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t1, 1  # [op1582] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vmv.v.x v4, t1  # [op1583] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t1, 0  # [op1584] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vmv.v.x v5, t1  # [op1585] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vmv1r.v v0, v1  # [op1586] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vmerge.vvm v4, v5, v4, v0  # [op1587] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vsuxei64.v v4, (t0), v2  # [op1588] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t0, 32  # [op1589] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vsetvli t0, t0, e16, m1, ta,ma  # [op1590] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t0, 32  # [op1591] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vsetvli t0, t0, e32, m1, ta,ma  # [op1592] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vid.v v2  # [op1593] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vadd.vx v2, v2, t2  # [op1594] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t0, 32  # [op1595] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vsetvli t0, t0, e32, m1, ta,ma  # [op1596] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vwadd.vx v4, v2, x0  # [op1597] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t0, 32  # [op1598] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vsetvli t0, t0, e64, m2, ta,ma  # [op1599] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t0, 4  # [op1600] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vmul.vx v2, v4, t0  # [op1601] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t0, 47744  # [op1602] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
add t0, t1, t0  # [op1603] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t1, 32  # [op1604] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vsetvli t1, t1, e32, m1, ta,ma  # [op1605] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t1, 1  # [op1606] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vmv.v.x v4, t1  # [op1607] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t1, 0  # [op1608] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vmv.v.x v5, t1  # [op1609] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vmv1r.v v0, v1  # [op1610] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vmerge.vvm v4, v5, v4, v0  # [op1611] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vsuxei64.v v4, (t0), v2  # [op1612] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t0, 32  # [op1613] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
vsetvli t0, t0, e16, m1, ta,ma  # [op1614] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:32:26
li t0, 32  # [op1615] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli t0, t0, e32, m1, ta,ma  # [op1616] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vid.v v2  # [op1617] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vadd.vx v2, v2, t2  # [op1618] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li t0, 32  # [op1619] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.v.x v3, t0  # [op1620] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vdiv.vv v2, v2, v3  # [op1621] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li t0, 32  # [op1622] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli t0, t0, e32, m1, ta,ma  # [op1623] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vwadd.vx v4, v2, x0  # [op1624] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li t0, 32  # [op1625] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli t0, t0, e64, m2, ta,ma  # [op1626] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li t0, 4  # [op1627] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmul.vx v2, v4, t0  # [op1628] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li t0, 34688  # [op1629] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add t0, t1, t0  # [op1630] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li t1, 32  # [op1631] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli t1, t1, e32, m1, ta,ma  # [op1632] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vluxei64.v v4, (t0), v2  # [op1633] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li t0, 32  # [op1634] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli t0, t0, e16, m1, ta,ma  # [op1635] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li t0, 32  # [op1636] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli t0, t0, e32, m1, ta,ma  # [op1637] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vid.v v2  # [op1638] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vadd.vx v2, v2, t2  # [op1639] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li t0, 32  # [op1640] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.v.x v3, t0  # [op1641] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vrem.vv v2, v2, v3  # [op1642] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li t0, 32  # [op1643] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli t0, t0, e32, m1, ta,ma  # [op1644] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vwadd.vx v6, v2, x0  # [op1645] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li t0, 32  # [op1646] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli t0, t0, e64, m2, ta,ma  # [op1647] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li t0, 4  # [op1648] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmul.vx v2, v6, t0  # [op1649] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li t0, 256  # [op1650] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add t0, t1, t0  # [op1651] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li t1, 32  # [op1652] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli t1, t1, e32, m1, ta,ma  # [op1653] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vluxei64.v v5, (t0), v2  # [op1654] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li t0, 32  # [op1655] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli t0, t0, e16, m1, ta,ma  # [op1656] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li t0, 32  # [op1657] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli t0, t0, e32, m1, ta,ma  # [op1658] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vadd.vv v2, v4, v5  # [op1659] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li t0, 32  # [op1660] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli t0, t0, e16, m1, ta,ma  # [op1661] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li t0, 32  # [op1662] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli t0, t0, e32, m1, ta,ma  # [op1663] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vwadd.vx v4, v2, x0  # [op1664] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li t0, 32  # [op1665] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli t0, t0, e64, m2, ta,ma  # [op1666] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li t0, 2  # [op1667] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmul.vx v2, v4, t0  # [op1668] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li t0, 32  # [op1669] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli t0, t0, e16, m1, ta,ma  # [op1670] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li t0, 77568  # [op1671] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add t0, t1, t0  # [op1672] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li t1, 128  # [op1673] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add t1, t0, t1  # [op1674] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op1675] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e32, m1, ta,ma  # [op1676] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 0  # [op1677] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.v.x v4, a1  # [op1678] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 1  # [op1679] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.v.x v5, a1  # [op1680] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv1r.v v0, v1  # [op1681] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmerge.vvm v4, v4, v5, v0  # [op1682] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vid.v v1  # [op1683] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vadd.vx v1, v1, t2  # [op1684] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op1685] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e32, m1, ta,ma  # [op1686] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vwadd.vx v6, v1, x0  # [op1687] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op1688] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1689] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 4  # [op1690] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmul.vx v6, v6, a1  # [op1691] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 26368  # [op1692] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
ld a2, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
ld a2, 16(a2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add a1, a2, a1  # [op1693] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a2, 32  # [op1694] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a2, a2, e32, m1, ta,ma  # [op1695] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vluxei64.v v1, (a1), v6  # [op1696] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op1697] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e32, m1, ta,ma  # [op1698] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.v.v v6, v1  # [op1699] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op1700] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e16, m1, ta,ma  # [op1701] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vfncvt.f.f.w v1, v6  # [op1702] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op1703] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1704] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vadd.vx v6, v2, s4  # [op1705] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op1706] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e32, m1, ta,ma  # [op1707] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 0  # [op1708] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.v.x v2, a1  # [op1709] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmsne.vv v2, v4, v2  # [op1710] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv1r.v v0, v2  # [op1711] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op1712] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1713] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 0  # [op1714] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.v.x v4, a1  # [op1715] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.v.x v2, t1  # [op1716] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsub.vv v6, v6, v2  # [op1717] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmerge.vvm v4, v4, v6, v0  # [op1718] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vadd.vv v2, v2, v4  # [op1719] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op1720] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e16, m1, ta,ma  # [op1721] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op1722] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1723] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a1, v2  # [op1724] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a2, 0  # [op1725] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add a2, t0, a2  # [op1726] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a3, 32  # [op1727] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1728] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a3, v1  # [op1729] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a3, 0(t1)  # [op1730] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v1, v1, 1  # [op1731] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
lhu a1, 0(a1)  # [op1732] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a1, 0(a2)  # [op1733] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op1734] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1735] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v2, v2, 1  # [op1736] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a1, v2  # [op1737] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a2, 2  # [op1738] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add a2, t0, a2  # [op1739] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a3, 32  # [op1740] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1741] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a3, v1  # [op1742] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a3, 0(t1)  # [op1743] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v1, v1, 1  # [op1744] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
lhu a1, 0(a1)  # [op1745] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a1, 0(a2)  # [op1746] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op1747] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1748] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v2, v2, 1  # [op1749] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a1, v2  # [op1750] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a2, 4  # [op1751] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add a2, t0, a2  # [op1752] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a3, 32  # [op1753] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1754] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a3, v1  # [op1755] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a3, 0(t1)  # [op1756] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v1, v1, 1  # [op1757] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
lhu a1, 0(a1)  # [op1758] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a1, 0(a2)  # [op1759] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op1760] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1761] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v2, v2, 1  # [op1762] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a1, v2  # [op1763] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a2, 6  # [op1764] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add a2, t0, a2  # [op1765] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a3, 32  # [op1766] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1767] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a3, v1  # [op1768] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a3, 0(t1)  # [op1769] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v1, v1, 1  # [op1770] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
lhu a1, 0(a1)  # [op1771] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a1, 0(a2)  # [op1772] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op1773] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1774] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v2, v2, 1  # [op1775] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a1, v2  # [op1776] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a2, 8  # [op1777] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add a2, t0, a2  # [op1778] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a3, 32  # [op1779] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1780] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a3, v1  # [op1781] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a3, 0(t1)  # [op1782] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v1, v1, 1  # [op1783] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
lhu a1, 0(a1)  # [op1784] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a1, 0(a2)  # [op1785] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op1786] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1787] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v2, v2, 1  # [op1788] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a1, v2  # [op1789] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a2, 10  # [op1790] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add a2, t0, a2  # [op1791] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a3, 32  # [op1792] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1793] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a3, v1  # [op1794] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a3, 0(t1)  # [op1795] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v1, v1, 1  # [op1796] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
lhu a1, 0(a1)  # [op1797] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a1, 0(a2)  # [op1798] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op1799] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1800] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v2, v2, 1  # [op1801] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a1, v2  # [op1802] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a2, 12  # [op1803] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add a2, t0, a2  # [op1804] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a3, 32  # [op1805] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1806] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a3, v1  # [op1807] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a3, 0(t1)  # [op1808] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v1, v1, 1  # [op1809] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
lhu a1, 0(a1)  # [op1810] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a1, 0(a2)  # [op1811] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op1812] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1813] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v2, v2, 1  # [op1814] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a1, v2  # [op1815] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a2, 14  # [op1816] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add a2, t0, a2  # [op1817] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a3, 32  # [op1818] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1819] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a3, v1  # [op1820] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a3, 0(t1)  # [op1821] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v1, v1, 1  # [op1822] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
lhu a1, 0(a1)  # [op1823] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a1, 0(a2)  # [op1824] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op1825] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1826] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v2, v2, 1  # [op1827] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a1, v2  # [op1828] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a2, 16  # [op1829] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add a2, t0, a2  # [op1830] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a3, 32  # [op1831] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1832] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a3, v1  # [op1833] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a3, 0(t1)  # [op1834] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v1, v1, 1  # [op1835] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
lhu a1, 0(a1)  # [op1836] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a1, 0(a2)  # [op1837] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op1838] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1839] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v2, v2, 1  # [op1840] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a1, v2  # [op1841] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a2, 18  # [op1842] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add a2, t0, a2  # [op1843] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a3, 32  # [op1844] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1845] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a3, v1  # [op1846] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a3, 0(t1)  # [op1847] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v1, v1, 1  # [op1848] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
lhu a1, 0(a1)  # [op1849] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a1, 0(a2)  # [op1850] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op1851] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1852] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v2, v2, 1  # [op1853] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a1, v2  # [op1854] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a2, 20  # [op1855] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add a2, t0, a2  # [op1856] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a3, 32  # [op1857] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1858] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a3, v1  # [op1859] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a3, 0(t1)  # [op1860] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v1, v1, 1  # [op1861] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
lhu a1, 0(a1)  # [op1862] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a1, 0(a2)  # [op1863] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op1864] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1865] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v2, v2, 1  # [op1866] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a1, v2  # [op1867] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a2, 22  # [op1868] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add a2, t0, a2  # [op1869] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a3, 32  # [op1870] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1871] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a3, v1  # [op1872] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a3, 0(t1)  # [op1873] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v1, v1, 1  # [op1874] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
lhu a1, 0(a1)  # [op1875] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a1, 0(a2)  # [op1876] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op1877] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1878] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v2, v2, 1  # [op1879] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a1, v2  # [op1880] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a2, 24  # [op1881] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add a2, t0, a2  # [op1882] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a3, 32  # [op1883] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1884] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a3, v1  # [op1885] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a3, 0(t1)  # [op1886] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v1, v1, 1  # [op1887] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
lhu a1, 0(a1)  # [op1888] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a1, 0(a2)  # [op1889] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op1890] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1891] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v2, v2, 1  # [op1892] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a1, v2  # [op1893] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a2, 26  # [op1894] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add a2, t0, a2  # [op1895] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a3, 32  # [op1896] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1897] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a3, v1  # [op1898] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a3, 0(t1)  # [op1899] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v1, v1, 1  # [op1900] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
lhu a1, 0(a1)  # [op1901] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a1, 0(a2)  # [op1902] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op1903] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1904] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v2, v2, 1  # [op1905] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a1, v2  # [op1906] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a2, 28  # [op1907] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add a2, t0, a2  # [op1908] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a3, 32  # [op1909] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1910] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a3, v1  # [op1911] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a3, 0(t1)  # [op1912] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v1, v1, 1  # [op1913] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
lhu a1, 0(a1)  # [op1914] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a1, 0(a2)  # [op1915] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op1916] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1917] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v2, v2, 1  # [op1918] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a1, v2  # [op1919] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a2, 30  # [op1920] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add a2, t0, a2  # [op1921] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a3, 32  # [op1922] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1923] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a3, v1  # [op1924] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a3, 0(t1)  # [op1925] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v1, v1, 1  # [op1926] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
lhu a1, 0(a1)  # [op1927] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a1, 0(a2)  # [op1928] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op1929] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1930] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v2, v2, 1  # [op1931] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a1, v2  # [op1932] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a2, 32  # [op1933] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add a2, t0, a2  # [op1934] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a3, 32  # [op1935] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1936] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a3, v1  # [op1937] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a3, 0(t1)  # [op1938] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v1, v1, 1  # [op1939] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
lhu a1, 0(a1)  # [op1940] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a1, 0(a2)  # [op1941] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op1942] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1943] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v2, v2, 1  # [op1944] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a1, v2  # [op1945] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a2, 34  # [op1946] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add a2, t0, a2  # [op1947] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a3, 32  # [op1948] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1949] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a3, v1  # [op1950] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a3, 0(t1)  # [op1951] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v1, v1, 1  # [op1952] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
lhu a1, 0(a1)  # [op1953] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a1, 0(a2)  # [op1954] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op1955] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1956] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v2, v2, 1  # [op1957] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a1, v2  # [op1958] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a2, 36  # [op1959] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add a2, t0, a2  # [op1960] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a3, 32  # [op1961] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1962] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a3, v1  # [op1963] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a3, 0(t1)  # [op1964] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v1, v1, 1  # [op1965] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
lhu a1, 0(a1)  # [op1966] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a1, 0(a2)  # [op1967] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op1968] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1969] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v2, v2, 1  # [op1970] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a1, v2  # [op1971] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a2, 38  # [op1972] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add a2, t0, a2  # [op1973] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a3, 32  # [op1974] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1975] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a3, v1  # [op1976] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a3, 0(t1)  # [op1977] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v1, v1, 1  # [op1978] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
lhu a1, 0(a1)  # [op1979] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a1, 0(a2)  # [op1980] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op1981] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1982] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v2, v2, 1  # [op1983] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a1, v2  # [op1984] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a2, 40  # [op1985] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add a2, t0, a2  # [op1986] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a3, 32  # [op1987] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a3, a3, e16, m1, ta,ma  # [op1988] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a3, v1  # [op1989] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a3, 0(t1)  # [op1990] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v1, v1, 1  # [op1991] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
lhu a1, 0(a1)  # [op1992] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a1, 0(a2)  # [op1993] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op1994] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op1995] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v2, v2, 1  # [op1996] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a1, v2  # [op1997] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a2, 42  # [op1998] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add a2, t0, a2  # [op1999] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a3, 32  # [op2000] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a3, a3, e16, m1, ta,ma  # [op2001] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a3, v1  # [op2002] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a3, 0(t1)  # [op2003] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v1, v1, 1  # [op2004] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
lhu a1, 0(a1)  # [op2005] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a1, 0(a2)  # [op2006] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op2007] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op2008] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v2, v2, 1  # [op2009] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a1, v2  # [op2010] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a2, 44  # [op2011] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add a2, t0, a2  # [op2012] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a3, 32  # [op2013] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a3, a3, e16, m1, ta,ma  # [op2014] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a3, v1  # [op2015] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a3, 0(t1)  # [op2016] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v1, v1, 1  # [op2017] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
lhu a1, 0(a1)  # [op2018] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a1, 0(a2)  # [op2019] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op2020] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op2021] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v2, v2, 1  # [op2022] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a1, v2  # [op2023] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a2, 46  # [op2024] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add a2, t0, a2  # [op2025] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a3, 32  # [op2026] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a3, a3, e16, m1, ta,ma  # [op2027] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a3, v1  # [op2028] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a3, 0(t1)  # [op2029] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v1, v1, 1  # [op2030] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
lhu a1, 0(a1)  # [op2031] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a1, 0(a2)  # [op2032] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op2033] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op2034] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v2, v2, 1  # [op2035] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a1, v2  # [op2036] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a2, 48  # [op2037] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add a2, t0, a2  # [op2038] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a3, 32  # [op2039] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a3, a3, e16, m1, ta,ma  # [op2040] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a3, v1  # [op2041] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a3, 0(t1)  # [op2042] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v1, v1, 1  # [op2043] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
lhu a1, 0(a1)  # [op2044] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a1, 0(a2)  # [op2045] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op2046] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op2047] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v2, v2, 1  # [op2048] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a1, v2  # [op2049] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a2, 50  # [op2050] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add a2, t0, a2  # [op2051] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a3, 32  # [op2052] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a3, a3, e16, m1, ta,ma  # [op2053] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a3, v1  # [op2054] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a3, 0(t1)  # [op2055] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v1, v1, 1  # [op2056] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
lhu a1, 0(a1)  # [op2057] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a1, 0(a2)  # [op2058] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op2059] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op2060] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v2, v2, 1  # [op2061] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a1, v2  # [op2062] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a2, 52  # [op2063] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add a2, t0, a2  # [op2064] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a3, 32  # [op2065] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a3, a3, e16, m1, ta,ma  # [op2066] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a3, v1  # [op2067] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a3, 0(t1)  # [op2068] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v1, v1, 1  # [op2069] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
lhu a1, 0(a1)  # [op2070] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a1, 0(a2)  # [op2071] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op2072] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op2073] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v2, v2, 1  # [op2074] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a1, v2  # [op2075] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a2, 54  # [op2076] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add a2, t0, a2  # [op2077] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a3, 32  # [op2078] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a3, a3, e16, m1, ta,ma  # [op2079] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a3, v1  # [op2080] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a3, 0(t1)  # [op2081] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v1, v1, 1  # [op2082] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
lhu a1, 0(a1)  # [op2083] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a1, 0(a2)  # [op2084] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op2085] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op2086] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v2, v2, 1  # [op2087] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a1, v2  # [op2088] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a2, 56  # [op2089] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add a2, t0, a2  # [op2090] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a3, 32  # [op2091] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a3, a3, e16, m1, ta,ma  # [op2092] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a3, v1  # [op2093] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a3, 0(t1)  # [op2094] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v1, v1, 1  # [op2095] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
lhu a1, 0(a1)  # [op2096] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a1, 0(a2)  # [op2097] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op2098] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op2099] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v2, v2, 1  # [op2100] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a1, v2  # [op2101] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a2, 58  # [op2102] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add a2, t0, a2  # [op2103] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a3, 32  # [op2104] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a3, a3, e16, m1, ta,ma  # [op2105] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a3, v1  # [op2106] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a3, 0(t1)  # [op2107] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v1, v1, 1  # [op2108] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
lhu a1, 0(a1)  # [op2109] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a1, 0(a2)  # [op2110] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op2111] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op2112] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v2, v2, 1  # [op2113] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a1, v2  # [op2114] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a2, 60  # [op2115] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add a2, t0, a2  # [op2116] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a3, 32  # [op2117] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a3, a3, e16, m1, ta,ma  # [op2118] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a3, v1  # [op2119] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a3, 0(t1)  # [op2120] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v1, v1, 1  # [op2121] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
lhu a1, 0(a1)  # [op2122] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a1, 0(a2)  # [op2123] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 32  # [op2124] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a1, a1, e64, m2, ta,ma  # [op2125] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v2, v2, 1  # [op2126] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a1, v2  # [op2127] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a2, 62  # [op2128] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add a2, t0, a2  # [op2129] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a3, 32  # [op2130] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli a3, a3, e16, m1, ta,ma  # [op2131] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vmv.x.s a3, v1  # [op2132] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh a3, 0(t1)  # [op2133] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v1, v1, 1  # [op2134] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
lhu t1, 0(a1)  # [op2135] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
sh t1, 0(a2)  # [op2136] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li t1, 32  # [op2137] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli t1, t1, e64, m2, ta,ma  # [op2138] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vslidedown.vi v2, v2, 1  # [op2139] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li t1, 32  # [op2140] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vsetvli t1, t1, e16, m1, ta,ma  # [op2141] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vle16.v v1, 0(t0)  # [op2142] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li t0, 51840  # [op2143] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add t0, t1, t0  # [op2144] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
mv t1, t2  # [op2145] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li a1, 2  # [op2146] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
mul t1, t1, a1  # [op2147] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
add t0, t0, t1  # [op2148] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
vse16.v v1, 0(t0)  # [op2149] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:31:13
li t0, 32  # [op2150] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
add t0, s1, t0  # [op2151] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t1, 32  # [op2152] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
addw t1, t2, t1  # [op2153] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 32  # [op2154] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
vsetvli t2, t2, e16, m1, ta,ma  # [op2155] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t2, t1  # [op2156] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv s1, t0  # [op2156] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk15_head  # [op2156] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lstg16_head:  # block stg16_head
li t1, 1024  # [op2157] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
slt t1, t0, t1  # [op2158] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
bne t1, zero, .Lbrc2159_true  # [op2159] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
j .Lstg16_exit  # [op2159] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
.Lbrc2159_true:  # [op2159] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
j .Lstg16_body  # [op2159] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
.Lstg16_body:  # block stg16_body
li t1, 32  # [op2160] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
vsetvli t1, t1, e32, m1, ta,ma  # [op2161] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
vid.v v1  # [op2162] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
vadd.vx v1, v1, t0  # [op2163] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
li t1, 32  # [op2164] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
vmv.v.x v2, t1  # [op2165] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
vdiv.vv v2, v1, v2  # [op2166] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
li t1, 32  # [op2167] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
vmv.v.x v3, t1  # [op2168] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
vrem.vv v2, v2, v3  # [op2169] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
li t1, 32  # [op2170] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
vmv.v.x v3, t1  # [op2171] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
vrem.vv v3, v1, v3  # [op2172] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
li t1, 32  # [op2173] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
vmv.v.x v4, t1  # [op2174] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
vmul.vv v3, v3, v4  # [op2175] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
vadd.vv v2, v2, v3  # [op2176] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
li t1, 32  # [op2177] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
vsetvli t1, t1, e32, m1, ta,ma  # [op2178] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
vwadd.vx v4, v2, x0  # [op2179] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
li t1, 32  # [op2180] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
vsetvli t1, t1, e64, m2, ta,ma  # [op2181] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
li t1, 4  # [op2182] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
vmul.vx v2, v4, t1  # [op2183] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
li t1, 30464  # [op2184] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
ld t2, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
ld t2, 16(t2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
add t1, t2, t1  # [op2185] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
li t2, 32  # [op2186] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
vsetvli t2, t2, e32, m1, ta,ma  # [op2187] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
vluxei64.v v4, (t1), v2  # [op2188] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
li t1, 32  # [op2189] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
vsetvli t1, t1, e32, m1, ta,ma  # [op2190] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
vwadd.vx v2, v1, x0  # [op2191] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
li t1, 32  # [op2192] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
vsetvli t1, t1, e64, m2, ta,ma  # [op2193] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
li t1, 2  # [op2194] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
vmul.vx v2, v2, t1  # [op2195] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
li t1, 53888  # [op2196] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
ld t2, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
ld t2, 16(t2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
add t1, t2, t1  # [op2197] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
li t2, 32  # [op2198] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
vsetvli t2, t2, e32, m1, ta,ma  # [op2199] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
vmv.v.v v2, v4  # [op2200] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
li t2, 32  # [op2201] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
vsetvli t2, t2, e16, m1, ta,ma  # [op2202] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
vfncvt.f.f.w v1, v2  # [op2203] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
mv t2, t0  # [op2204] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
li s1, 2  # [op2205] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
mul t2, t2, s1  # [op2206] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
add t1, t1, t2  # [op2207] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
vse16.v v1, 0(t1)  # [op2208] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
li t1, 32  # [op2209] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
addw t0, t0, t1  # [op2210] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
j .Lstg16_head  # [op2211] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:23
.Lstg16_exit:  # block stg16_exit
li t0, 77056  # [op2212] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld t1, 16(t1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add t0, t1, t0  # [op2213] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sd t0, 224(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t0, 128  # [op2214] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld t1, 224(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add t1, t1, t0  # [op2215] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t0, 256  # [op2216] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld t2, 224(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add s1, t2, t0  # [op2217] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t0, 8  # [op2218] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli t0, t0, e32, m1, ta,ma  # [op2219] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vid.v v1  # [op2220] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t0, 8  # [op2221] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli t0, t0, e32, m1, ta,ma  # [op2222] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vid.v v2  # [op2223] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t0, 64  # [op2224] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli t0, t0, e16, m1, ta,ma  # [op2225] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t0, 0  # [op2226] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmv.v.x v3, t0  # [op2227] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmv.v.x v4, t0  # [op2228] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t0, 0  # [op2229] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s10, 16  # [op2230] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mv a4, t0  # [op2231] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
j .Lmtile17.head  # [op2231] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
.Lmtile17.head:  # block mtile17.head
slt t0, a4, s10  # [op2232] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
bne t0, zero, .Lbrc2233_true  # [op2233] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mv t0, a4  # [op2233] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
j .Lmtile17.exit  # [op2233] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
.Lbrc2233_true:  # [op2233] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
j .Lmtile17.body  # [op2233] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
.Lmtile17.body:  # block mtile17.body
li t0, 4  # [op2234] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
divu t2, a4, t0  # [op2235] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul t0, t2, t0  # [op2236] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub a1, a4, t0  # [op2237] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t0, 8  # [op2238] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul t2, t2, t0  # [op2239] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sd t2, 240(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul t0, a1, t0  # [op2240] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sd t0, 232(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t0, 64  # [op2241] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli t0, t0, e32, m2, ta,ma  # [op2242] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t0, 0  # [op2243] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmv.v.x v6, t0  # [op2244] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t0, 0  # [op2245] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s11, 32  # [op2246] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
j .Lmk18.head  # [op2247] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
.Lmtile17.exit:  # block mtile17.exit
li t0, 0  # [op2248] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t1, s9  # [op2249] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk21_head  # [op2249] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lmk18.head:  # block mk18.head
sd t0, 248(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld t0, 248(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
slt t2, t0, s11  # [op2250] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld t0, 248(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
bne t2, zero, .Lbrc2251_true  # [op2251] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
j .Lmk18.exit  # [op2251] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
.Lbrc2251_true:  # [op2251] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
j .Lmk18.body  # [op2251] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
.Lmk18.body:  # block mk18.body
sd t0, 248(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld t0, 248(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t2, 32  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub t0, t2, t0  # [op2253] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sd t0, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t0, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld t2, 240(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add t2, t2, t0  # [op2255] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t0, 32  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
slt t0, t2, t0  # [op2256] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a1, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a2, 8  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
slt a1, a1, a2  # [op2258] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a2, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub a1, a2, a1  # [op2259] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a2, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a3, 8  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub a2, a3, a2  # [op2260] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
and a1, a2, a1  # [op2261] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a2, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a1, a2, a1  # [op2262] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a2, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub t0, a2, t0  # [op2263] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
and t0, a1, t0  # [op2264] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
addiw t0, t0, 0  # [op2265] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a1, 8  # [op2266] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli a1, a1, e32, m1, ta,ma  # [op2267] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmv.v.x v5, t0  # [op2268] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmslt.vv v5, v1, v5  # [op2269] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmv1r.v v0, v5  # [op2270] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a1, 53888  # [op2271] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld t0, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld t0, 16(t0)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a2, t0, a1  # [op2272] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t0, 64  # [op2273] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul t2, t2, t0  # [op2274] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a2, a2, t2  # [op2275] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t2, 2  # [op2276] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a3, 248(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul a3, a3, t2  # [op2277] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a2, a2, a3  # [op2278] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a3, 8  # [op2279] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli a3, a3, e16, m1, ta,ma  # [op2280] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vle16.v v5, 0(a2), v0.t  # [op2281] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmerge.vvm v5, v3, v5, v0  # [op2282] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a2, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a3, 224(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a2, a3, a2  # [op2283] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a3, 8  # [op2284] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli a3, a3, e16, m1, ta,ma  # [op2285] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vse16.v v5, 0(a2)  # [op2286] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a2, 1  # [op2287] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a3, 240(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a2, a3, a2  # [op2288] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a3, 32  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
slt a3, a2, a3  # [op2289] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a6, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a7, 8  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
slt a6, a6, a7  # [op2290] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a7, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub a6, a7, a6  # [op2291] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a7, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s2, 8  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub a7, s2, a7  # [op2292] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
and a6, a7, a6  # [op2293] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a7, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a6, a7, a6  # [op2294] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a7, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub a3, a7, a3  # [op2295] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
and a3, a6, a3  # [op2296] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
addiw a3, a3, 0  # [op2297] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a6, 8  # [op2298] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli a6, a6, e32, m1, ta,ma  # [op2299] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmv.v.x v5, a3  # [op2300] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmslt.vv v5, v1, v5  # [op2301] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmv1r.v v0, v5  # [op2302] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a3, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a3, 16(a3)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a3, a3, a1  # [op2303] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul a2, a2, t0  # [op2304] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a2, a3, a2  # [op2305] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a3, 248(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul a3, a3, t2  # [op2306] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a2, a2, a3  # [op2307] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a3, 8  # [op2308] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli a3, a3, e16, m1, ta,ma  # [op2309] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vle16.v v5, 0(a2), v0.t  # [op2310] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmerge.vvm v5, v3, v5, v0  # [op2311] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a2, 16  # [op2312] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a3, 224(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a3, a3, a2  # [op2313] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a6, 8  # [op2314] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli a6, a6, e16, m1, ta,ma  # [op2315] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vse16.v v5, 0(a3)  # [op2316] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a3, 240(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a3, a3, t2  # [op2317] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a6, 32  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
slt a6, a3, a6  # [op2318] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a7, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s2, 8  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
slt a7, a7, s2  # [op2319] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s2, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub a7, s2, a7  # [op2320] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s2, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t3, 8  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub s2, t3, s2  # [op2321] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
and a7, s2, a7  # [op2322] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s2, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a7, s2, a7  # [op2323] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s2, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub a6, s2, a6  # [op2324] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
and a6, a7, a6  # [op2325] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
addiw a6, a6, 0  # [op2326] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a7, 8  # [op2327] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli a7, a7, e32, m1, ta,ma  # [op2328] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmv.v.x v5, a6  # [op2329] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmslt.vv v5, v1, v5  # [op2330] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmv1r.v v0, v5  # [op2331] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a6, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a6, 16(a6)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a6, a6, a1  # [op2332] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul a3, a3, t0  # [op2333] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a3, a6, a3  # [op2334] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a6, 248(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul a6, a6, t2  # [op2335] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a3, a3, a6  # [op2336] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a6, 8  # [op2337] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli a6, a6, e16, m1, ta,ma  # [op2338] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vle16.v v5, 0(a3), v0.t  # [op2339] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmerge.vvm v5, v3, v5, v0  # [op2340] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a3, 224(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a6, 32  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a3, a3, a6  # [op2341] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a6, 8  # [op2342] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli a6, a6, e16, m1, ta,ma  # [op2343] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vse16.v v5, 0(a3)  # [op2344] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a3, 3  # [op2345] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a6, 240(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a3, a6, a3  # [op2346] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a6, 32  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
slt a6, a3, a6  # [op2347] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a7, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s2, 8  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
slt a7, a7, s2  # [op2348] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s2, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub a7, s2, a7  # [op2349] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s2, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t3, 8  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub s2, t3, s2  # [op2350] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
and a7, s2, a7  # [op2351] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s2, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a7, s2, a7  # [op2352] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s2, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub a6, s2, a6  # [op2353] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
and a6, a7, a6  # [op2354] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
addiw a6, a6, 0  # [op2355] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a7, 8  # [op2356] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli a7, a7, e32, m1, ta,ma  # [op2357] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmv.v.x v5, a6  # [op2358] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmslt.vv v5, v1, v5  # [op2359] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmv1r.v v0, v5  # [op2360] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a6, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a6, 16(a6)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a6, a6, a1  # [op2361] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul a3, a3, t0  # [op2362] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a3, a6, a3  # [op2363] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a6, 248(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul a6, a6, t2  # [op2364] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a3, a3, a6  # [op2365] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a6, 8  # [op2366] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli a6, a6, e16, m1, ta,ma  # [op2367] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vle16.v v5, 0(a3), v0.t  # [op2368] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmerge.vvm v5, v3, v5, v0  # [op2369] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a3, 48  # [op2370] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a6, 224(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a6, a6, a3  # [op2371] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a7, 8  # [op2372] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli a7, a7, e16, m1, ta,ma  # [op2373] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vse16.v v5, 0(a6)  # [op2374] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a6, 4  # [op2375] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a7, 240(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a6, a7, a6  # [op2376] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a7, 32  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
slt a7, a6, a7  # [op2377] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s2, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t3, 8  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
slt s2, s2, t3  # [op2378] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t3, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub s2, t3, s2  # [op2379] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld t3, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t4, 8  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub t3, t4, t3  # [op2380] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
and s2, t3, s2  # [op2381] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld t3, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add s2, t3, s2  # [op2382] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t3, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub a7, t3, a7  # [op2383] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
and a7, s2, a7  # [op2384] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
addiw a7, a7, 0  # [op2385] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s2, 8  # [op2386] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli s2, s2, e32, m1, ta,ma  # [op2387] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmv.v.x v5, a7  # [op2388] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmslt.vv v5, v1, v5  # [op2389] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmv1r.v v0, v5  # [op2390] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a7, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a7, 16(a7)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a7, a7, a1  # [op2391] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul a6, a6, t0  # [op2392] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a6, a7, a6  # [op2393] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a7, 248(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul a7, a7, t2  # [op2394] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a6, a6, a7  # [op2395] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a7, 8  # [op2396] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli a7, a7, e16, m1, ta,ma  # [op2397] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vle16.v v5, 0(a6), v0.t  # [op2398] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmerge.vvm v5, v3, v5, v0  # [op2399] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a6, 224(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a6, a6, t0  # [op2400] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a7, 8  # [op2401] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli a7, a7, e16, m1, ta,ma  # [op2402] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vse16.v v5, 0(a6)  # [op2403] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a6, 5  # [op2404] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a7, 240(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a6, a7, a6  # [op2405] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a7, 32  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
slt a7, a6, a7  # [op2406] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s2, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t3, 8  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
slt s2, s2, t3  # [op2407] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t3, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub s2, t3, s2  # [op2408] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld t3, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t4, 8  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub t3, t4, t3  # [op2409] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
and s2, t3, s2  # [op2410] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld t3, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add s2, t3, s2  # [op2411] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t3, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub a7, t3, a7  # [op2412] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
and a7, s2, a7  # [op2413] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
addiw a7, a7, 0  # [op2414] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s2, 8  # [op2415] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli s2, s2, e32, m1, ta,ma  # [op2416] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmv.v.x v5, a7  # [op2417] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmslt.vv v5, v1, v5  # [op2418] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmv1r.v v0, v5  # [op2419] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a7, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a7, 16(a7)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a7, a7, a1  # [op2420] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul a6, a6, t0  # [op2421] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a6, a7, a6  # [op2422] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a7, 248(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul a7, a7, t2  # [op2423] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a6, a6, a7  # [op2424] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a7, 8  # [op2425] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli a7, a7, e16, m1, ta,ma  # [op2426] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vle16.v v5, 0(a6), v0.t  # [op2427] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmerge.vvm v5, v3, v5, v0  # [op2428] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a6, 80  # [op2429] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a7, 224(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a7, a7, a6  # [op2430] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s2, 8  # [op2431] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli s2, s2, e16, m1, ta,ma  # [op2432] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vse16.v v5, 0(a7)  # [op2433] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a7, 6  # [op2434] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s2, 240(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a7, s2, a7  # [op2435] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s2, 32  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
slt s2, a7, s2  # [op2436] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld t3, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t4, 8  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
slt t3, t3, t4  # [op2437] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t4, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub t3, t4, t3  # [op2438] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld t4, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t5, 8  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub t4, t5, t4  # [op2439] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
and t3, t4, t3  # [op2440] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld t4, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add t3, t4, t3  # [op2441] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t4, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub s2, t4, s2  # [op2442] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
and s2, t3, s2  # [op2443] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
addiw s2, s2, 0  # [op2444] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t3, 8  # [op2445] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli t3, t3, e32, m1, ta,ma  # [op2446] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmv.v.x v5, s2  # [op2447] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmslt.vv v5, v1, v5  # [op2448] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmv1r.v v0, v5  # [op2449] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s2, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s2, 16(s2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add s2, s2, a1  # [op2450] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul a7, a7, t0  # [op2451] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a7, s2, a7  # [op2452] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s2, 248(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul s2, s2, t2  # [op2453] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a7, a7, s2  # [op2454] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s2, 8  # [op2455] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli s2, s2, e16, m1, ta,ma  # [op2456] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vle16.v v5, 0(a7), v0.t  # [op2457] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmerge.vvm v5, v3, v5, v0  # [op2458] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a7, 96  # [op2459] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s2, 224(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add s2, s2, a7  # [op2460] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t3, 8  # [op2461] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli t3, t3, e16, m1, ta,ma  # [op2462] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vse16.v v5, 0(s2)  # [op2463] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s2, 7  # [op2464] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld t3, 240(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add s2, t3, s2  # [op2465] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t3, 32  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
slt t3, s2, t3  # [op2466] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld t4, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t5, 8  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
slt t4, t4, t5  # [op2467] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t5, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub t4, t5, t4  # [op2468] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld t5, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t6, 8  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub t5, t6, t5  # [op2469] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
and t4, t5, t4  # [op2470] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld t5, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add t4, t5, t4  # [op2471] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t5, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub t3, t5, t3  # [op2472] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
and t3, t4, t3  # [op2473] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
addiw t3, t3, 0  # [op2474] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t4, 8  # [op2475] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli t4, t4, e32, m1, ta,ma  # [op2476] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmv.v.x v5, t3  # [op2477] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmslt.vv v5, v1, v5  # [op2478] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmv1r.v v0, v5  # [op2479] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld t3, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld t3, 16(t3)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a1, t3, a1  # [op2480] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul s2, s2, t0  # [op2481] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a1, a1, s2  # [op2482] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s2, 248(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul t2, s2, t2  # [op2483] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add t2, a1, t2  # [op2484] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a1, 8  # [op2485] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli a1, a1, e16, m1, ta,ma  # [op2486] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vle16.v v5, 0(t2), v0.t  # [op2487] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmerge.vvm v5, v3, v5, v0  # [op2488] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t2, 112  # [op2489] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a1, 224(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a1, a1, t2  # [op2490] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s2, 8  # [op2491] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli s2, s2, e16, m1, ta,ma  # [op2492] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vse16.v v5, 0(a1)  # [op2493] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a1, 8  # [op2494] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli a1, a1, e16, m1, ta,ma  # [op2495] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a1, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a1, t1, a1  # [op2496] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vse16.v v4, 0(a1)  # [op2497] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a1, t1, a2  # [op2498] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vse16.v v4, 0(a1)  # [op2499] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a1, 32  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a1, t1, a1  # [op2500] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vse16.v v4, 0(a1)  # [op2501] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a1, t1, a3  # [op2502] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vse16.v v4, 0(a1)  # [op2503] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add t0, t1, t0  # [op2504] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vse16.v v4, 0(t0)  # [op2505] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add t0, t1, a6  # [op2506] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vse16.v v4, 0(t0)  # [op2507] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add t0, t1, a7  # [op2508] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vse16.v v4, 0(t0)  # [op2509] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add t0, t1, t2  # [op2510] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vse16.v v4, 0(t0)  # [op2511] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t0, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
j .Lpb19.head  # [op2512] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
.Lmk18.exit:  # block mk18.exit
li t0, 64  # [op2513] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli t0, t0, e32, m2, ta,ma  # [op2514] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vse32.v v6, 0(s1)  # [op2515] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t2, 0  # [op2516] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld t0, 240(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a2, t0, t2  # [op2517] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t0, 32  # [op2518] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
slt a1, a2, t0  # [op2519] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a3, 232(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub a3, t0, a3  # [op2520] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub a1, t2, a1  # [op2521] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
and a1, a3, a1  # [op2522] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
addiw a1, a1, 0  # [op2523] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a3, 8  # [op2524] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli a3, a3, e32, m1, ta,ma  # [op2525] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmv.v.x v5, a1  # [op2526] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmslt.vv v5, v2, v5  # [op2527] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmv1r.v v0, v5  # [op2528] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a1, s1, t2  # [op2529] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a3, 8  # [op2530] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli a3, a3, e32, m1, ta,ma  # [op2531] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vle32.v v5, 0(a1)  # [op2532] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a3, 55936  # [op2533] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a1, 16(a1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a6, a1, a3  # [op2534] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a1, 128  # [op2535] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul a2, a2, a1  # [op2536] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a6, a6, a2  # [op2537] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a2, 4  # [op2538] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a7, 232(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul a7, a7, a2  # [op2539] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a6, a6, a7  # [op2540] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a7, 8  # [op2541] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli a7, a7, e32, m1, ta,ma  # [op2542] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vse32.v v5, 0(a6), v0.t  # [op2543] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a6, 1  # [op2544] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a7, 240(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a7, a7, a6  # [op2545] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
slt s2, a7, t0  # [op2546] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s11, 232(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub s11, t0, s11  # [op2547] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub s2, t2, s2  # [op2548] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
and s2, s11, s2  # [op2549] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
addiw s2, s2, 0  # [op2550] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s11, 8  # [op2551] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli s11, s11, e32, m1, ta,ma  # [op2552] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmv.v.x v5, s2  # [op2553] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmslt.vv v5, v2, v5  # [op2554] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmv1r.v v0, v5  # [op2555] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add s2, s1, t0  # [op2556] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s11, 8  # [op2557] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli s11, s11, e32, m1, ta,ma  # [op2558] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vle32.v v5, 0(s2)  # [op2559] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s2, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s2, 16(s2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add s2, s2, a3  # [op2560] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul a7, a7, a1  # [op2561] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a7, s2, a7  # [op2562] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s2, 232(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul s2, s2, a2  # [op2563] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a7, a7, s2  # [op2564] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s2, 8  # [op2565] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli s2, s2, e32, m1, ta,ma  # [op2566] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vse32.v v5, 0(a7), v0.t  # [op2567] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a7, 2  # [op2568] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s2, 240(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a7, s2, a7  # [op2569] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
slt s2, a7, t0  # [op2570] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s11, 232(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub s11, t0, s11  # [op2571] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub s2, t2, s2  # [op2572] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
and s2, s11, s2  # [op2573] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
addiw s2, s2, 0  # [op2574] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s11, 8  # [op2575] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli s11, s11, e32, m1, ta,ma  # [op2576] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmv.v.x v5, s2  # [op2577] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmslt.vv v5, v2, v5  # [op2578] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmv1r.v v0, v5  # [op2579] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s2, 64  # [op2580] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add s2, s1, s2  # [op2581] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s11, 8  # [op2582] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli s11, s11, e32, m1, ta,ma  # [op2583] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vle32.v v5, 0(s2)  # [op2584] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s2, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s2, 16(s2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add s2, s2, a3  # [op2585] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul a7, a7, a1  # [op2586] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a7, s2, a7  # [op2587] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s2, 232(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul s2, s2, a2  # [op2588] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a7, a7, s2  # [op2589] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s2, 8  # [op2590] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli s2, s2, e32, m1, ta,ma  # [op2591] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vse32.v v5, 0(a7), v0.t  # [op2592] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a7, 3  # [op2593] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s2, 240(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a7, s2, a7  # [op2594] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
slt s2, a7, t0  # [op2595] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s11, 232(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub s11, t0, s11  # [op2596] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub s2, t2, s2  # [op2597] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
and s2, s11, s2  # [op2598] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
addiw s2, s2, 0  # [op2599] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s11, 8  # [op2600] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli s11, s11, e32, m1, ta,ma  # [op2601] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmv.v.x v5, s2  # [op2602] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmslt.vv v5, v2, v5  # [op2603] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmv1r.v v0, v5  # [op2604] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s2, 96  # [op2605] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add s2, s1, s2  # [op2606] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s11, 8  # [op2607] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli s11, s11, e32, m1, ta,ma  # [op2608] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vle32.v v5, 0(s2)  # [op2609] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s2, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s2, 16(s2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add s2, s2, a3  # [op2610] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul a7, a7, a1  # [op2611] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a7, s2, a7  # [op2612] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s2, 232(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul s2, s2, a2  # [op2613] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a7, a7, s2  # [op2614] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s2, 8  # [op2615] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli s2, s2, e32, m1, ta,ma  # [op2616] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vse32.v v5, 0(a7), v0.t  # [op2617] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a7, 240(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a7, a7, a2  # [op2618] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
slt s2, a7, t0  # [op2619] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s11, 232(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub s11, t0, s11  # [op2620] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub s2, t2, s2  # [op2621] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
and s2, s11, s2  # [op2622] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
addiw s2, s2, 0  # [op2623] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s11, 8  # [op2624] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli s11, s11, e32, m1, ta,ma  # [op2625] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmv.v.x v5, s2  # [op2626] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmslt.vv v5, v2, v5  # [op2627] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmv1r.v v0, v5  # [op2628] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add s2, s1, a1  # [op2629] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s11, 8  # [op2630] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli s11, s11, e32, m1, ta,ma  # [op2631] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vle32.v v5, 0(s2)  # [op2632] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s2, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s2, 16(s2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add s2, s2, a3  # [op2633] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul a7, a7, a1  # [op2634] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a7, s2, a7  # [op2635] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s2, 232(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul s2, s2, a2  # [op2636] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a7, a7, s2  # [op2637] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s2, 8  # [op2638] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli s2, s2, e32, m1, ta,ma  # [op2639] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vse32.v v5, 0(a7), v0.t  # [op2640] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a7, 5  # [op2641] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s2, 240(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a7, s2, a7  # [op2642] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
slt s2, a7, t0  # [op2643] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s11, 232(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub s11, t0, s11  # [op2644] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub s2, t2, s2  # [op2645] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
and s2, s11, s2  # [op2646] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
addiw s2, s2, 0  # [op2647] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s11, 8  # [op2648] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli s11, s11, e32, m1, ta,ma  # [op2649] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmv.v.x v5, s2  # [op2650] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmslt.vv v5, v2, v5  # [op2651] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmv1r.v v0, v5  # [op2652] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s2, 160  # [op2653] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add s2, s1, s2  # [op2654] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s11, 8  # [op2655] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli s11, s11, e32, m1, ta,ma  # [op2656] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vle32.v v5, 0(s2)  # [op2657] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s2, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s2, 16(s2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add s2, s2, a3  # [op2658] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul a7, a7, a1  # [op2659] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a7, s2, a7  # [op2660] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s2, 232(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul s2, s2, a2  # [op2661] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a7, a7, s2  # [op2662] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s2, 8  # [op2663] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli s2, s2, e32, m1, ta,ma  # [op2664] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vse32.v v5, 0(a7), v0.t  # [op2665] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a7, 6  # [op2666] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s2, 240(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a7, s2, a7  # [op2667] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
slt s2, a7, t0  # [op2668] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s11, 232(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub s11, t0, s11  # [op2669] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub s2, t2, s2  # [op2670] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
and s2, s11, s2  # [op2671] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
addiw s2, s2, 0  # [op2672] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s11, 8  # [op2673] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli s11, s11, e32, m1, ta,ma  # [op2674] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmv.v.x v5, s2  # [op2675] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmslt.vv v5, v2, v5  # [op2676] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmv1r.v v0, v5  # [op2677] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s2, 192  # [op2678] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add s2, s1, s2  # [op2679] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s11, 8  # [op2680] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli s11, s11, e32, m1, ta,ma  # [op2681] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vle32.v v5, 0(s2)  # [op2682] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s2, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s2, 16(s2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add s2, s2, a3  # [op2683] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul a7, a7, a1  # [op2684] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a7, s2, a7  # [op2685] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s2, 232(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul s2, s2, a2  # [op2686] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a7, a7, s2  # [op2687] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li s2, 8  # [op2688] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli s2, s2, e32, m1, ta,ma  # [op2689] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vse32.v v5, 0(a7), v0.t  # [op2690] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a7, 7  # [op2691] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s2, 240(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a7, s2, a7  # [op2692] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
slt s2, a7, t0  # [op2693] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld s11, 232(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub t0, t0, s11  # [op2694] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub t2, t2, s2  # [op2695] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
and t0, t0, t2  # [op2696] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
addiw t0, t0, 0  # [op2697] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t2, 8  # [op2698] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli t2, t2, e32, m1, ta,ma  # [op2699] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmv.v.x v5, t0  # [op2700] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmslt.vv v5, v2, v5  # [op2701] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vmv1r.v v0, v5  # [op2702] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t0, 224  # [op2703] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add t0, s1, t0  # [op2704] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t2, 8  # [op2705] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli t2, t2, e32, m1, ta,ma  # [op2706] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vle32.v v5, 0(t0)  # [op2707] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld t0, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld t0, 16(t0)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add t0, t0, a3  # [op2708] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul t2, a7, a1  # [op2709] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add t0, t0, t2  # [op2710] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld t2, 232(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul t2, t2, a2  # [op2711] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add t0, t0, t2  # [op2712] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t2, 8  # [op2713] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli t2, t2, e32, m1, ta,ma  # [op2714] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vse32.v v5, 0(t0), v0.t  # [op2715] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add t0, a4, a6  # [op2716] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mv a4, t0  # [op2717] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
j .Lmtile17.head  # [op2717] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
.Lpb19.head:  # block pb19.head
li t2, 8  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
slt t2, t0, t2  # [op2718] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
bne t2, zero, .Lbrc2719_true  # [op2719] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
j .Lpb19.exit  # [op2719] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
.Lbrc2719_true:  # [op2719] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
j .Lpb19.body  # [op2719] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
.Lpb19.body:  # block pb19.body
ld t2, 232(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a1, t2, t0  # [op2720] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t2, 32  # [op2721] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
slt a3, a1, t2  # [op2722] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a2, 8  # [op2723] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld t2, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
slt a6, t2, a2  # [op2724] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t2, 0  # [op2725] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub a6, t2, a6  # [op2726] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a7, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub a2, a2, a7  # [op2727] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
and a2, a2, a6  # [op2728] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a6, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a2, a6, a2  # [op2729] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sub a3, t2, a3  # [op2730] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
and a2, a2, a3  # [op2731] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a3, 51840  # [op2732] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a6, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a6, 16(a6)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a3, a6, a3  # [op2733] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a6, 64  # [op2734] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld a7, 248(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul a6, a7, a6  # [op2735] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a3, a3, a6  # [op2736] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a6, 2  # [op2737] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul a1, a1, a6  # [op2738] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a1, a3, a1  # [op2739] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a3, 16  # [op2740] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul a3, t0, a3  # [op2741] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a3, t1, a3  # [op2742] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
j .Lpq20.head  # [op2743] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
.Lpb19.exit:  # block pb19.exit
li t0, 64  # [op2744] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli t0, t0, e16, m1, ta,ma  # [op2745] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld t0, 224(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vle16.v v5, 0(t0)  # [op2746] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vle16.v v8, 0(t1)  # [op2747] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
vsetvli x0, zero, e16, m1, ta, ma
    smt.vfwmadot v6, v5, v8  # [op2748] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li t0, 8  # [op2749] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
ld t2, 248(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add t0, t2, t0  # [op2750] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
j .Lmk18.head  # [op2751] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
.Lpq20.head:  # block pq20.head
slt a6, t2, a2  # [op2752] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
bne a6, zero, .Lbrc2753_true  # [op2753] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
j .Lpq20.exit  # [op2753] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
.Lbrc2753_true:  # [op2753] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
j .Lpq20.body  # [op2753] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
.Lpq20.body:  # block pq20.body
li a6, 64  # [op2754] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul a6, t2, a6  # [op2755] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a6, a1, a6  # [op2756] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a7, 2  # [op2757] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
mul a7, t2, a7  # [op2758] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add a7, a3, a7  # [op2759] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
lhu a6, 0(a6)  # [op2760] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
sh a6, 0(a7)  # [op2761] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
li a6, 1  # [op2762] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add t2, t2, a6  # [op2763] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
j .Lpq20.head  # [op2764] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
.Lpq20.exit:  # block pq20.exit
li t2, 1  # [op2765] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
add t0, t0, t2  # [op2766] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
j .Lpb19.head  # [op2767] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:16
.Lchunk21_head:  # block chunk21_head
li t2, 1024  # [op2768] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
slt t2, t0, t2  # [op2769] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld s1, 208(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
bne t2, zero, .Lbrc2770_true  # [op2770] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t0, s1  # [op2770] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk21_exit  # [op2770] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lbrc2770_true:  # [op2770] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk21_body  # [op2770] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk21_exit:  # block chunk21_exit
li t0, 1  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
ld t1, 216(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
addw t1, t1, t0  # [op2771] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
li t2, 60032  # [op2772] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
li s1, 384  # [op2773] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
li t0, 0  # [op2774] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
li a1, 1024  # [op2775] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
li a2, 32  # [op2776] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
j .Lmcarry22.head  # [op2777] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
.Lchunk21_body:  # block chunk21_body
li t2, 32  # [op2778] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
vsetvli t2, t2, e32, m1, ta,ma  # [op2779] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 32  # [op2780] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
vsetvli t2, t2, e32, m1, ta,ma  # [op2781] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
vid.v v1  # [op2782] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
vadd.vx v1, v1, t0  # [op2783] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
li t2, 32  # [op2784] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
vsetvli t2, t2, e32, m1, ta,ma  # [op2785] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
vwadd.vx v2, v1, x0  # [op2786] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
li t2, 32  # [op2787] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
vsetvli t2, t2, e64, m2, ta,ma  # [op2788] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
li t2, 4  # [op2789] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
vmul.vx v2, v2, t2  # [op2790] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
li t2, 384  # [op2791] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
add t2, s1, t2  # [op2792] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
li s1, 32  # [op2793] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
vsetvli s1, s1, e32, m1, ta,ma  # [op2794] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
vluxei64.v v1, (t2), v2  # [op2795] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
li t2, 32  # [op2796] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
vsetvli t2, t2, e32, m1, ta,ma  # [op2797] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
vid.v v2  # [op2798] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
vadd.vx v2, v2, t0  # [op2799] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
li t2, 32  # [op2800] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
vsetvli t2, t2, e32, m1, ta,ma  # [op2801] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
vwadd.vx v4, v2, x0  # [op2802] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
li t2, 32  # [op2803] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
vsetvli t2, t2, e64, m2, ta,ma  # [op2804] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
li t2, 4  # [op2805] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
vmul.vx v2, v4, t2  # [op2806] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
li t2, 55936  # [op2807] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
add t2, s1, t2  # [op2808] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
li s1, 32  # [op2809] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
vsetvli s1, s1, e32, m1, ta,ma  # [op2810] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
vluxei64.v v4, (t2), v2  # [op2811] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
li t2, 32  # [op2812] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
vsetvli t2, t2, e32, m1, ta,ma  # [op2813] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
vfadd.vv v1, v1, v4  # [op2814] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
vid.v v2  # [op2815] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
vadd.vx v2, v2, t0  # [op2816] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
li t2, 32  # [op2817] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
vsetvli t2, t2, e32, m1, ta,ma  # [op2818] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
vwadd.vx v4, v2, x0  # [op2819] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
li t2, 32  # [op2820] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
vsetvli t2, t2, e64, m2, ta,ma  # [op2821] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
li t2, 4  # [op2822] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
vmul.vx v2, v4, t2  # [op2823] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
li t2, 60032  # [op2824] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
add t2, s1, t2  # [op2825] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
li s1, 32  # [op2826] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
vsetvli s1, s1, e32, m1, ta,ma  # [op2827] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
vsuxei64.v v1, (t2), v2  # [op2828] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
li t2, 32  # [op2829] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
vsetvli t2, t2, e32, m1, ta,ma  # [op2830] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:33:9
li t2, 32  # [op2831] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
add t1, t1, t2  # [op2832] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 32  # [op2833] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
addw t0, t0, t2  # [op2834] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 32  # [op2835] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
vsetvli t2, t2, e32, m1, ta,ma  # [op2836] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk21_head  # [op2837] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lmcarry22.head:  # block mcarry22.head
slt a3, t0, a1  # [op2838] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
bne a3, zero, .Lbrc2839_true  # [op2839] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
j .Lmcarry22.exit  # [op2839] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
.Lbrc2839_true:  # [op2839] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
j .Lmcarry22.body  # [op2839] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
.Lmcarry22.body:  # block mcarry22.body
ld a3, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
ld a3, 16(a3)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
add a3, a3, t2  # [op2840] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
ld a4, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
ld a4, 16(a4)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
add a4, a4, s1  # [op2841] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
li a6, 32  # [op2842] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
vsetvli a6, a6, e32, m1, ta,ma  # [op2843] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
vid.v v1  # [op2844] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
vadd.vx v1, v1, t0  # [op2845] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
li a6, 32  # [op2846] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
vsetvli a6, a6, e32, m1, ta,ma  # [op2847] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
vwadd.vx v2, v1, x0  # [op2848] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
li a6, 32  # [op2849] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
vsetvli a6, a6, e64, m2, ta,ma  # [op2850] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
li a6, 4  # [op2851] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
vmul.vx v2, v2, a6  # [op2852] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
li a6, 32  # [op2853] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
vsetvli a6, a6, e32, m1, ta,ma  # [op2854] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
vluxei64.v v1, (a3), v2  # [op2855] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
vsuxei64.v v1, (a4), v2  # [op2856] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
addw t0, t0, a2  # [op2857] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
j .Lmcarry22.head  # [op2858] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
.Lmcarry22.exit:  # block mcarry22.exit
mv t0, t1  # [op2859] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
j .Lmloop8.head  # [op2859] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:27:5
.Lchunk23_head:  # block chunk23_head
li t2, 32  # [op2860] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
slt t2, t0, t2  # [op2861] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld s1, 208(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
bne t2, zero, .Lbrc2862_true  # [op2862] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t0, t1  # [op2862] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t1, s1  # [op2862] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk23_exit  # [op2862] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lbrc2862_true:  # [op2862] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk23_body  # [op2862] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk23_exit:  # block chunk23_exit
li t1, 0  # [op2863] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
sd t0, 96(sp)  # [op2864] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t0, t1  # [op2864] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t1, 96(sp)  # [op2864] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk24_head  # [op2864] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk23_body:  # block chunk23_body
li t2, 32  # [op2865] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
vsetvli t2, t2, e32, m1, ta,ma  # [op2866] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 32  # [op2867] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
vsetvli t2, t2, e32, m1, ta,ma  # [op2868] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
vid.v v1  # [op2869] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
vadd.vx v1, v1, t0  # [op2870] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
li t2, 32  # [op2871] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
vsetvli t2, t2, e32, m1, ta,ma  # [op2872] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
vwadd.vx v2, v1, x0  # [op2873] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
li t2, 32  # [op2874] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
vsetvli t2, t2, e64, m2, ta,ma  # [op2875] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
li t2, 4  # [op2876] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
vmul.vx v2, v2, t2  # [op2877] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
li t2, 128  # [op2878] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
add t2, s1, t2  # [op2879] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
li s1, 32  # [op2880] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
vsetvli s1, s1, e32, m1, ta,ma  # [op2881] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
vluxei64.v v1, (t2), v2  # [op2882] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
li t2, 32  # [op2883] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
vsetvli t2, t2, e32, m1, ta,ma  # [op2884] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
vid.v v2  # [op2885] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
vadd.vx v2, v2, t0  # [op2886] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
li t2, 32  # [op2887] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
vsetvli t2, t2, e32, m1, ta,ma  # [op2888] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
vwadd.vx v4, v2, x0  # [op2889] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
li t2, 32  # [op2890] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
vsetvli t2, t2, e64, m2, ta,ma  # [op2891] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
li t2, 4  # [op2892] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
vmul.vx v2, v4, t2  # [op2893] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
li t2, 34560  # [op2894] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
add t2, s1, t2  # [op2895] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
li s1, 32  # [op2896] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
vsetvli s1, s1, e32, m1, ta,ma  # [op2897] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
vluxei64.v v4, (t2), v2  # [op2898] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
li t2, 32  # [op2899] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
vsetvli t2, t2, e32, m1, ta,ma  # [op2900] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
vmul.vv v1, v1, v4  # [op2901] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
vid.v v2  # [op2902] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
vadd.vx v2, v2, t0  # [op2903] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
li t2, 32  # [op2904] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
vsetvli t2, t2, e32, m1, ta,ma  # [op2905] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
vwadd.vx v4, v2, x0  # [op2906] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
li t2, 32  # [op2907] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
vsetvli t2, t2, e64, m2, ta,ma  # [op2908] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
li t2, 4  # [op2909] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
vmul.vx v2, v4, t2  # [op2910] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
li t2, 64256  # [op2911] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
add t2, s1, t2  # [op2912] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
li s1, 32  # [op2913] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
vsetvli s1, s1, e32, m1, ta,ma  # [op2914] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
vsuxei64.v v1, (t2), v2  # [op2915] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
li t2, 32  # [op2916] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
vsetvli t2, t2, e32, m1, ta,ma  # [op2917] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:20
li t2, 32  # [op2918] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
add t1, t1, t2  # [op2919] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 32  # [op2920] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
addw t0, t0, t2  # [op2921] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 32  # [op2922] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
vsetvli t2, t2, e32, m1, ta,ma  # [op2923] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk23_head  # [op2924] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk24_head:  # block chunk24_head
li t2, 1024  # [op2925] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
slt t2, t0, t2  # [op2926] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld s1, 208(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
bne t2, zero, .Lbrc2927_true  # [op2927] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t0, t1  # [op2927] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t1, s1  # [op2927] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk24_exit  # [op2927] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lbrc2927_true:  # [op2927] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk24_body  # [op2927] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk24_exit:  # block chunk24_exit
li t1, 0  # [op2928] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
sd t0, 96(sp)  # [op2929] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t0, t1  # [op2929] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t1, 96(sp)  # [op2929] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk25_head  # [op2929] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk24_body:  # block chunk24_body
li t2, 32  # [op2930] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
vsetvli t2, t2, e32, m1, ta,ma  # [op2931] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 32  # [op2932] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:14
vsetvli t2, t2, e32, m1, ta,ma  # [op2933] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:14
vid.v v1  # [op2934] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:14
vadd.vx v1, v1, t0  # [op2935] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:14
li t2, 32  # [op2936] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:14
vmv.v.x v2, t2  # [op2937] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:14
vdiv.vv v1, v1, v2  # [op2938] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:14
li t2, 32  # [op2939] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:14
vsetvli t2, t2, e32, m1, ta,ma  # [op2940] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:14
vwadd.vx v2, v1, x0  # [op2941] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:14
li t2, 32  # [op2942] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:14
vsetvli t2, t2, e64, m2, ta,ma  # [op2943] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:14
li t2, 8  # [op2944] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:14
vmul.vx v2, v2, t2  # [op2945] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:14
li t2, 64384  # [op2946] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:14
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:14
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:14
add t2, s1, t2  # [op2947] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:14
li s1, 32  # [op2948] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:14
vsetvli s1, s1, e64, m2, ta,ma  # [op2949] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:14
vluxei64.v v4, (t2), v2  # [op2950] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:14
li t2, 32  # [op2951] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:14
vsetvli t2, t2, e32, m1, ta,ma  # [op2952] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:14
li t2, 32  # [op2953] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
add t1, t1, t2  # [op2954] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 32  # [op2955] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
addw t0, t0, t2  # [op2956] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 32  # [op2957] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
vsetvli t2, t2, e32, m1, ta,ma  # [op2958] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk24_head  # [op2959] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk25_head:  # block chunk25_head
li t2, 32  # [op2960] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
slt t2, t0, t2  # [op2961] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld s1, 208(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
bne t2, zero, .Lbrc2962_true  # [op2962] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t0, s1  # [op2962] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk25_exit  # [op2962] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lbrc2962_true:  # [op2962] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk25_body  # [op2962] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk25_exit:  # block chunk25_exit
li t0, 0  # [op2963] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
j .Lstg26_head  # [op2964] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
.Lchunk25_body:  # block chunk25_body
li t2, 32  # [op2965] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
vsetvli t2, t2, e32, m1, ta,ma  # [op2966] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 32  # [op2967] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
vsetvli t2, t2, e32, m1, ta,ma  # [op2968] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
vid.v v1  # [op2969] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
vadd.vx v1, v1, t0  # [op2970] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
li t2, 32  # [op2971] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
vsetvli t2, t2, e32, m1, ta,ma  # [op2972] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
vwadd.vx v2, v1, x0  # [op2973] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
li t2, 32  # [op2974] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
vsetvli t2, t2, e64, m2, ta,ma  # [op2975] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
li t2, 4  # [op2976] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
vmul.vx v2, v2, t2  # [op2977] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
li t2, 128  # [op2978] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
add t2, s1, t2  # [op2979] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
li s1, 32  # [op2980] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
vsetvli s1, s1, e32, m1, ta,ma  # [op2981] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
vluxei64.v v1, (t2), v2  # [op2982] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
li t2, 32  # [op2983] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
vsetvli t2, t2, e32, m1, ta,ma  # [op2984] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
vid.v v2  # [op2985] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
vadd.vx v2, v2, t0  # [op2986] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
li t2, 32  # [op2987] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
vsetvli t2, t2, e32, m1, ta,ma  # [op2988] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
vwadd.vx v4, v2, x0  # [op2989] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
li t2, 32  # [op2990] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
vsetvli t2, t2, e64, m2, ta,ma  # [op2991] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
li t2, 4  # [op2992] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
vmul.vx v2, v4, t2  # [op2993] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
li t2, 4864  # [op2994] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
add t2, s1, t2  # [op2995] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
li s1, 32  # [op2996] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
vsetvli s1, s1, e32, m1, ta,ma  # [op2997] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
vluxei64.v v4, (t2), v2  # [op2998] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
li t2, 32  # [op2999] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
vsetvli t2, t2, e32, m1, ta,ma  # [op3000] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
vmslt.vv v1, v1, v4  # [op3001] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
vid.v v2  # [op3002] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
vadd.vx v2, v2, t0  # [op3003] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
li t2, 32  # [op3004] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
vsetvli t2, t2, e32, m1, ta,ma  # [op3005] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
vwadd.vx v4, v2, x0  # [op3006] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
li t2, 32  # [op3007] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
vsetvli t2, t2, e64, m2, ta,ma  # [op3008] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
li t2, 4  # [op3009] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
vmul.vx v2, v4, t2  # [op3010] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
li t2, 72832  # [op3011] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
add t2, s1, t2  # [op3012] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
li s1, 32  # [op3013] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
vsetvli s1, s1, e32, m1, ta,ma  # [op3014] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
li s1, 1  # [op3015] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
vmv.v.x v4, s1  # [op3016] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
li s1, 0  # [op3017] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
vmv.v.x v5, s1  # [op3018] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
vmv1r.v v0, v1  # [op3019] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
vmerge.vvm v1, v5, v4, v0  # [op3020] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
vsuxei64.v v1, (t2), v2  # [op3021] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:20
li t2, 32  # [op3022] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
add t1, t1, t2  # [op3023] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 32  # [op3024] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
addw t0, t0, t2  # [op3025] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 32  # [op3026] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
vsetvli t2, t2, e32, m1, ta,ma  # [op3027] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk25_head  # [op3028] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lstg26_head:  # block stg26_head
li t2, 1024  # [op3029] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
slt t2, t0, t2  # [op3030] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
bne t2, zero, .Lbrc3031_true  # [op3031] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
j .Lstg26_exit  # [op3031] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
.Lbrc3031_true:  # [op3031] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
j .Lstg26_body  # [op3031] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
.Lstg26_body:  # block stg26_body
li t2, 32  # [op3032] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vsetvli t2, t2, e32, m1, ta,ma  # [op3033] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vid.v v1  # [op3034] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vadd.vx v1, v1, t0  # [op3035] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
li t2, 32  # [op3036] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vmv.v.x v2, t2  # [op3037] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vdiv.vv v2, v1, v2  # [op3038] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
li t2, 32  # [op3039] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vmv.v.x v3, t2  # [op3040] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vrem.vv v2, v2, v3  # [op3041] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
li t2, 32  # [op3042] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vmv.v.x v3, t2  # [op3043] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vrem.vv v3, v1, v3  # [op3044] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
li t2, 32  # [op3045] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vsetvli t2, t2, e32, m1, ta,ma  # [op3046] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vwadd.vx v4, v2, x0  # [op3047] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
li t2, 32  # [op3048] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vsetvli t2, t2, e64, m2, ta,ma  # [op3049] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
li t2, 4  # [op3050] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vmul.vx v2, v4, t2  # [op3051] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
li t2, 72832  # [op3052] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
add t2, s1, t2  # [op3053] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
li s1, 32  # [op3054] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vsetvli s1, s1, e32, m1, ta,ma  # [op3055] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vluxei64.v v4, (t2), v2  # [op3056] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
li t2, 32  # [op3057] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vsetvli t2, t2, e32, m1, ta,ma  # [op3058] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vwadd.vx v2, v1, x0  # [op3059] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
li t2, 32  # [op3060] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vsetvli t2, t2, e64, m2, ta,ma  # [op3061] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
li t2, 4  # [op3062] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vmul.vx v2, v2, t2  # [op3063] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
li t2, 72960  # [op3064] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
add t2, s1, t2  # [op3065] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
li s1, 32  # [op3066] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vsetvli s1, s1, e32, m1, ta,ma  # [op3067] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vsuxei64.v v4, (t2), v2  # [op3068] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
li t2, 32  # [op3069] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
addw t0, t0, t2  # [op3070] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
j .Lstg26_head  # [op3071] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
.Lstg26_exit:  # block stg26_exit
li t0, 0  # [op3072] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t2, t1  # [op3073] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t1, t0  # [op3073] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk27_head  # [op3073] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk27_head:  # block chunk27_head
li t0, 1024  # [op3074] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
slt t0, t1, t0  # [op3075] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld s1, 208(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
bne t0, zero, .Lbrc3076_true  # [op3076] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t1, s1  # [op3076] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t0, t2  # [op3076] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk27_exit  # [op3076] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lbrc3076_true:  # [op3076] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk27_body  # [op3076] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk27_exit:  # block chunk27_exit
ld t1, 208(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
sd t0, 96(sp)  # [op3077] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t0, t1  # [op3077] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld t1, 96(sp)  # [op3077] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lprog_next  # [op3077] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lchunk27_body:  # block chunk27_body
li t0, 32  # [op3078] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
vsetvli t0, t0, e16, m1, ta,ma  # [op3079] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t0, 32  # [op3080] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vsetvli t0, t0, e32, m1, ta,ma  # [op3081] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vid.v v1  # [op3082] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vadd.vx v1, v1, t1  # [op3083] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
li t0, 32  # [op3084] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vsetvli t0, t0, e32, m1, ta,ma  # [op3085] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vwadd.vx v2, v1, x0  # [op3086] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
li t0, 32  # [op3087] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vsetvli t0, t0, e64, m2, ta,ma  # [op3088] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
li t0, 4  # [op3089] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vmul.vx v2, v2, t0  # [op3090] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
li t0, 72960  # [op3091] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
add t0, s1, t0  # [op3092] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
li s1, 32  # [op3093] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vsetvli s1, s1, e32, m1, ta,ma  # [op3094] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vluxei64.v v1, (t0), v2  # [op3095] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
li t0, 0  # [op3096] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vmv.v.x v2, t0  # [op3097] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vmsne.vv v1, v1, v2  # [op3098] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
li t0, 32  # [op3099] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vsetvli t0, t0, e16, m1, ta,ma  # [op3100] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
li t0, 32  # [op3101] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vsetvli t0, t0, e32, m1, ta,ma  # [op3102] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vid.v v2  # [op3103] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vadd.vx v2, v2, t1  # [op3104] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
li t0, 32  # [op3105] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vsetvli t0, t0, e32, m1, ta,ma  # [op3106] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vwadd.vx v4, v2, x0  # [op3107] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
li t0, 32  # [op3108] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vsetvli t0, t0, e64, m2, ta,ma  # [op3109] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
li t0, 4  # [op3110] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vmul.vx v2, v4, t0  # [op3111] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
li t0, 43648  # [op3112] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
add t0, s1, t0  # [op3113] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
li s1, 32  # [op3114] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vsetvli s1, s1, e32, m1, ta,ma  # [op3115] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vluxei64.v v4, (t0), v2  # [op3116] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
li t0, 0  # [op3117] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vmv.v.x v2, t0  # [op3118] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vmsne.vv v2, v4, v2  # [op3119] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
li t0, 32  # [op3120] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vsetvli t0, t0, e16, m1, ta,ma  # [op3121] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
vmand.mm v1, v1, v2  # [op3122] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:35:19
li t0, 32  # [op3123] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vsetvli t0, t0, e32, m1, ta,ma  # [op3124] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vid.v v2  # [op3125] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vadd.vx v2, v2, t1  # [op3126] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li t0, 32  # [op3127] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vsetvli t0, t0, e32, m1, ta,ma  # [op3128] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vwadd.vx v4, v2, x0  # [op3129] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li t0, 32  # [op3130] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vsetvli t0, t0, e64, m2, ta,ma  # [op3131] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li t0, 4  # [op3132] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmul.vx v2, v4, t0  # [op3133] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li t0, 384  # [op3134] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add t0, s1, t0  # [op3135] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li s1, 32  # [op3136] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vsetvli s1, s1, e32, m1, ta,ma  # [op3137] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vluxei64.v v4, (t0), v2  # [op3138] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li t0, 32  # [op3139] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vsetvli t0, t0, e16, m1, ta,ma  # [op3140] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li t0, 32  # [op3141] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vsetvli t0, t0, e32, m1, ta,ma  # [op3142] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.v.v v2, v4  # [op3143] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li t0, 32  # [op3144] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vsetvli t0, t0, e16, m1, ta,ma  # [op3145] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vfncvt.f.f.w v4, v2  # [op3146] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li t0, 32  # [op3147] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vsetvli t0, t0, e32, m1, ta,ma  # [op3148] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vid.v v2  # [op3149] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vadd.vx v2, v2, t1  # [op3150] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li t0, 32  # [op3151] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.v.x v3, t0  # [op3152] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vdiv.vv v2, v2, v3  # [op3153] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li t0, 32  # [op3154] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vsetvli t0, t0, e32, m1, ta,ma  # [op3155] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vwadd.vx v6, v2, x0  # [op3156] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li t0, 32  # [op3157] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vsetvli t0, t0, e64, m2, ta,ma  # [op3158] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li t0, 4  # [op3159] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmul.vx v2, v6, t0  # [op3160] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li t0, 64256  # [op3161] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add t0, s1, t0  # [op3162] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li s1, 32  # [op3163] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vsetvli s1, s1, e32, m1, ta,ma  # [op3164] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vluxei64.v v5, (t0), v2  # [op3165] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li t0, 32  # [op3166] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vsetvli t0, t0, e16, m1, ta,ma  # [op3167] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li t0, 32  # [op3168] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vsetvli t0, t0, e32, m1, ta,ma  # [op3169] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vid.v v2  # [op3170] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vadd.vx v2, v2, t1  # [op3171] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li t0, 32  # [op3172] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.v.x v3, t0  # [op3173] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vrem.vv v2, v2, v3  # [op3174] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li t0, 32  # [op3175] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vsetvli t0, t0, e32, m1, ta,ma  # [op3176] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vwadd.vx v6, v2, x0  # [op3177] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li t0, 32  # [op3178] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vsetvli t0, t0, e64, m2, ta,ma  # [op3179] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li t0, 4  # [op3180] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmul.vx v2, v6, t0  # [op3181] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li t0, 256  # [op3182] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add t0, s1, t0  # [op3183] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li s1, 32  # [op3184] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vsetvli s1, s1, e32, m1, ta,ma  # [op3185] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vluxei64.v v6, (t0), v2  # [op3186] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li t0, 32  # [op3187] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vsetvli t0, t0, e16, m1, ta,ma  # [op3188] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li t0, 32  # [op3189] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vsetvli t0, t0, e32, m1, ta,ma  # [op3190] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vadd.vv v2, v5, v6  # [op3191] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li t0, 32  # [op3192] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vsetvli t0, t0, e16, m1, ta,ma  # [op3193] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li t0, 32  # [op3194] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vsetvli t0, t0, e32, m1, ta,ma  # [op3195] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vwadd.vx v6, v2, x0  # [op3196] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li t0, 32  # [op3197] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vsetvli t0, t0, e64, m2, ta,ma  # [op3198] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li t0, 2  # [op3199] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmul.vx v2, v6, t0  # [op3200] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li t0, 32  # [op3201] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vsetvli t0, t0, e16, m1, ta,ma  # [op3202] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li t0, 77568  # [op3203] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
ld s1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
ld s1, 16(s1)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add t0, s1, t0  # [op3204] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li s1, 128  # [op3205] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add s1, t0, s1  # [op3206] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 32  # [op3207] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vsetvli a1, a1, e16, m1, ta,ma  # [op3208] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vse16.v v4, 0(t0)  # [op3209] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 32  # [op3210] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vsetvli a1, a1, e32, m1, ta,ma  # [op3211] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 0  # [op3212] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.v.x v4, a1  # [op3213] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 1  # [op3214] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.v.x v5, a1  # [op3215] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv1r.v v0, v1  # [op3216] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmerge.vvm v4, v4, v5, v0  # [op3217] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 32  # [op3218] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vsetvli a1, a1, e64, m2, ta,ma  # [op3219] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vadd.vx v6, v2, s5  # [op3220] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 32  # [op3221] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vsetvli a1, a1, e32, m1, ta,ma  # [op3222] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 0  # [op3223] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.v.x v2, a1  # [op3224] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmsne.vv v2, v4, v2  # [op3225] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv1r.v v0, v2  # [op3226] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 32  # [op3227] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vsetvli a1, a1, e64, m2, ta,ma  # [op3228] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 0  # [op3229] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.v.x v4, a1  # [op3230] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.v.x v2, s1  # [op3231] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vsub.vv v6, v6, v2  # [op3232] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmerge.vvm v4, v4, v6, v0  # [op3233] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vadd.vv v2, v2, v4  # [op3234] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li s1, 32  # [op3235] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vsetvli s1, s1, e16, m1, ta,ma  # [op3236] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li s1, 32  # [op3237] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vsetvli s1, s1, e64, m2, ta,ma  # [op3238] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.x.s s1, v2  # [op3239] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 0  # [op3240] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add a1, t0, a1  # [op3241] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
lhu a1, 0(a1)  # [op3242] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
sh a1, 0(s1)  # [op3243] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vslidedown.vi v2, v2, 1  # [op3244] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.x.s s1, v2  # [op3245] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 2  # [op3246] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add a1, t0, a1  # [op3247] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
lhu a1, 0(a1)  # [op3248] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
sh a1, 0(s1)  # [op3249] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vslidedown.vi v2, v2, 1  # [op3250] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.x.s s1, v2  # [op3251] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 4  # [op3252] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add a1, t0, a1  # [op3253] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
lhu a1, 0(a1)  # [op3254] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
sh a1, 0(s1)  # [op3255] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vslidedown.vi v2, v2, 1  # [op3256] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.x.s s1, v2  # [op3257] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 6  # [op3258] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add a1, t0, a1  # [op3259] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
lhu a1, 0(a1)  # [op3260] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
sh a1, 0(s1)  # [op3261] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vslidedown.vi v2, v2, 1  # [op3262] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.x.s s1, v2  # [op3263] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 8  # [op3264] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add a1, t0, a1  # [op3265] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
lhu a1, 0(a1)  # [op3266] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
sh a1, 0(s1)  # [op3267] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vslidedown.vi v2, v2, 1  # [op3268] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.x.s s1, v2  # [op3269] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 10  # [op3270] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add a1, t0, a1  # [op3271] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
lhu a1, 0(a1)  # [op3272] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
sh a1, 0(s1)  # [op3273] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vslidedown.vi v2, v2, 1  # [op3274] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.x.s s1, v2  # [op3275] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 12  # [op3276] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add a1, t0, a1  # [op3277] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
lhu a1, 0(a1)  # [op3278] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
sh a1, 0(s1)  # [op3279] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vslidedown.vi v2, v2, 1  # [op3280] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.x.s s1, v2  # [op3281] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 14  # [op3282] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add a1, t0, a1  # [op3283] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
lhu a1, 0(a1)  # [op3284] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
sh a1, 0(s1)  # [op3285] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vslidedown.vi v2, v2, 1  # [op3286] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.x.s s1, v2  # [op3287] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 16  # [op3288] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add a1, t0, a1  # [op3289] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
lhu a1, 0(a1)  # [op3290] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
sh a1, 0(s1)  # [op3291] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vslidedown.vi v2, v2, 1  # [op3292] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.x.s s1, v2  # [op3293] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 18  # [op3294] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add a1, t0, a1  # [op3295] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
lhu a1, 0(a1)  # [op3296] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
sh a1, 0(s1)  # [op3297] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vslidedown.vi v2, v2, 1  # [op3298] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.x.s s1, v2  # [op3299] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 20  # [op3300] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add a1, t0, a1  # [op3301] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
lhu a1, 0(a1)  # [op3302] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
sh a1, 0(s1)  # [op3303] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vslidedown.vi v2, v2, 1  # [op3304] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.x.s s1, v2  # [op3305] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 22  # [op3306] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add a1, t0, a1  # [op3307] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
lhu a1, 0(a1)  # [op3308] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
sh a1, 0(s1)  # [op3309] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vslidedown.vi v2, v2, 1  # [op3310] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.x.s s1, v2  # [op3311] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 24  # [op3312] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add a1, t0, a1  # [op3313] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
lhu a1, 0(a1)  # [op3314] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
sh a1, 0(s1)  # [op3315] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vslidedown.vi v2, v2, 1  # [op3316] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.x.s s1, v2  # [op3317] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 26  # [op3318] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add a1, t0, a1  # [op3319] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
lhu a1, 0(a1)  # [op3320] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
sh a1, 0(s1)  # [op3321] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vslidedown.vi v2, v2, 1  # [op3322] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.x.s s1, v2  # [op3323] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 28  # [op3324] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add a1, t0, a1  # [op3325] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
lhu a1, 0(a1)  # [op3326] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
sh a1, 0(s1)  # [op3327] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vslidedown.vi v2, v2, 1  # [op3328] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.x.s s1, v2  # [op3329] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 30  # [op3330] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add a1, t0, a1  # [op3331] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
lhu a1, 0(a1)  # [op3332] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
sh a1, 0(s1)  # [op3333] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vslidedown.vi v2, v2, 1  # [op3334] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.x.s s1, v2  # [op3335] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 32  # [op3336] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add a1, t0, a1  # [op3337] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
lhu a1, 0(a1)  # [op3338] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
sh a1, 0(s1)  # [op3339] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vslidedown.vi v2, v2, 1  # [op3340] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.x.s s1, v2  # [op3341] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 34  # [op3342] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add a1, t0, a1  # [op3343] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
lhu a1, 0(a1)  # [op3344] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
sh a1, 0(s1)  # [op3345] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vslidedown.vi v2, v2, 1  # [op3346] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.x.s s1, v2  # [op3347] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 36  # [op3348] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add a1, t0, a1  # [op3349] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
lhu a1, 0(a1)  # [op3350] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
sh a1, 0(s1)  # [op3351] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vslidedown.vi v2, v2, 1  # [op3352] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.x.s s1, v2  # [op3353] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 38  # [op3354] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add a1, t0, a1  # [op3355] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
lhu a1, 0(a1)  # [op3356] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
sh a1, 0(s1)  # [op3357] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vslidedown.vi v2, v2, 1  # [op3358] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.x.s s1, v2  # [op3359] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 40  # [op3360] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add a1, t0, a1  # [op3361] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
lhu a1, 0(a1)  # [op3362] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
sh a1, 0(s1)  # [op3363] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vslidedown.vi v2, v2, 1  # [op3364] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.x.s s1, v2  # [op3365] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 42  # [op3366] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add a1, t0, a1  # [op3367] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
lhu a1, 0(a1)  # [op3368] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
sh a1, 0(s1)  # [op3369] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vslidedown.vi v2, v2, 1  # [op3370] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.x.s s1, v2  # [op3371] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 44  # [op3372] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add a1, t0, a1  # [op3373] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
lhu a1, 0(a1)  # [op3374] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
sh a1, 0(s1)  # [op3375] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vslidedown.vi v2, v2, 1  # [op3376] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.x.s s1, v2  # [op3377] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 46  # [op3378] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add a1, t0, a1  # [op3379] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
lhu a1, 0(a1)  # [op3380] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
sh a1, 0(s1)  # [op3381] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vslidedown.vi v2, v2, 1  # [op3382] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.x.s s1, v2  # [op3383] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 48  # [op3384] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add a1, t0, a1  # [op3385] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
lhu a1, 0(a1)  # [op3386] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
sh a1, 0(s1)  # [op3387] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vslidedown.vi v2, v2, 1  # [op3388] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.x.s s1, v2  # [op3389] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 50  # [op3390] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add a1, t0, a1  # [op3391] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
lhu a1, 0(a1)  # [op3392] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
sh a1, 0(s1)  # [op3393] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vslidedown.vi v2, v2, 1  # [op3394] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.x.s s1, v2  # [op3395] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 52  # [op3396] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add a1, t0, a1  # [op3397] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
lhu a1, 0(a1)  # [op3398] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
sh a1, 0(s1)  # [op3399] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vslidedown.vi v2, v2, 1  # [op3400] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.x.s s1, v2  # [op3401] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 54  # [op3402] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add a1, t0, a1  # [op3403] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
lhu a1, 0(a1)  # [op3404] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
sh a1, 0(s1)  # [op3405] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vslidedown.vi v2, v2, 1  # [op3406] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.x.s s1, v2  # [op3407] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 56  # [op3408] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add a1, t0, a1  # [op3409] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
lhu a1, 0(a1)  # [op3410] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
sh a1, 0(s1)  # [op3411] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vslidedown.vi v2, v2, 1  # [op3412] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.x.s s1, v2  # [op3413] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 58  # [op3414] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add a1, t0, a1  # [op3415] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
lhu a1, 0(a1)  # [op3416] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
sh a1, 0(s1)  # [op3417] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vslidedown.vi v2, v2, 1  # [op3418] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.x.s s1, v2  # [op3419] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 60  # [op3420] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add a1, t0, a1  # [op3421] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
lhu a1, 0(a1)  # [op3422] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
sh a1, 0(s1)  # [op3423] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vslidedown.vi v2, v2, 1  # [op3424] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vmv.x.s s1, v2  # [op3425] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
li a1, 62  # [op3426] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add t0, t0, a1  # [op3427] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
lhu t0, 0(t0)  # [op3428] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
sh t0, 0(s1)  # [op3429] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vslidedown.vi v2, v2, 1  # [op3430] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
vcpop.m t0, v1  # [op3431] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:34:5
add t0, t2, t0  # [op3432] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 32  # [op3433] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
addw t1, t1, t2  # [op3434] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
li t2, 32  # [op3435] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
vsetvli t2, t2, e16, m1, ta,ma  # [op3436] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
mv t2, t0  # [op3437] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lchunk27_head  # [op3437] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lprog_next:  # block prog_next
add t0, t0, s7  # [op3438] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
j .Lprog_head  # [op3439] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
.Lprog_exit:  # block prog_exit
ld t1, 144(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
sd t0, 0(t1)  # [op3440] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld ra, 0(sp)  # [op3441] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld s1, 8(sp)  # [op3441] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld s2, 16(sp)  # [op3441] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld s3, 24(sp)  # [op3441] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld s4, 32(sp)  # [op3441] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld s5, 40(sp)  # [op3441] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld s6, 48(sp)  # [op3441] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld s7, 56(sp)  # [op3441] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld s8, 64(sp)  # [op3441] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld s9, 72(sp)  # [op3441] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld s10, 80(sp)  # [op3441] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ld s11, 88(sp)  # [op3441] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
addi sp, sp, 256  # [op3441] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
ret  # [op3441] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/perf/batched_vecmat_mult.py:20:1
    .size operator_entry, .-operator_entry
    .section .note.GNU-stack,"",@progbits
