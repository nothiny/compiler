# a100c emitted program: matmul_k32_fast_kernel
# source: home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py
# specialization identity: 5b9701b642fc9e77
# compiler revision: 92fa8b4b706f0a76
# target model: a100-rvv1-vlen1024/1 (VLEN=1024, file=4096B)
# options: default
# argument layout: 264913e9333fb7df
# every instruction below traces to a selected MIR op: [opN] carries the source location
# passes: passes=default
    .text
    .globl operator_workspace_private
    .type operator_workspace_private, @function
operator_workspace_private:
    li a0, 523536
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
    # [peephole] removed 0 redundant vsetvli, 86 redundant li
operator_entry:  # fn operator_entry
addi sp, sp, -192
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
ld t0, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t0, 0(t0)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t0, 0(t0)  # [op1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd t0, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t0, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s7, 24(t0)  # [op3] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t0, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
lwu t0, 40(t0)  # [op4] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t1, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
lwu t1, 44(t1)  # [op5] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 0(t2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 8(t2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 8(t2)  # [op6] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw t2, t2, 0  # [op7] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 0(t2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 8(t2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 24(t2)  # [op8] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd t2, 128(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 128(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw t2, t2, 0  # [op9] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 0(t2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 8(t2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 40(t2)  # [op10] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw t2, t2, 0  # [op11] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 0(t2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 8(t2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 56(t2)  # [op12] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw t2, t2, 0  # [op13] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 0(t2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 8(t2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 72(t2)  # [op14] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw s8, t2, 0  # [op15] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 0(t2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 8(t2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 88(t2)  # [op16] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw t2, t2, 0  # [op17] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd t2, 136(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 0(t2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 8(t2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 104(t2)  # [op18] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw t2, t2, 0  # [op19] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 0(t2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 8(t2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 120(t2)  # [op20] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw t2, t2, 0  # [op21] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd t2, 144(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 0(t2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 8(t2)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 136(t2)  # [op22] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw t2, t2, 0  # [op23] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s2, 0(t2)  # [op24] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s3, 56(t2)  # [op25] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 120(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s4, 112(t2)  # [op26] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t2, 128  # [op27] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 128(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
divu t2, s1, t2  # [op28] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd t2, 152(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t2, 1  # [op30] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 152(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mul t2, t2, s1  # [op31] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li s1, 2  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mul s9, t2, s1  # [op32] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t0  # [op33] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv s10, t1  # [op34] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t1, 0  # [op35] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lprog_head  # [op36] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lprog_head:  # block prog_head
slt t2, t0, s9  # [op37] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
bne t2, zero, .Lbrc38_true  # [op38] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd t1, 96(sp)  # [op38] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t1, t0  # [op38] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t0, 96(sp)  # [op38] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lprog_exit  # [op38] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lbrc38_true:  # [op38] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv s1, t1  # [op38] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t1, t0  # [op38] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lprog_body  # [op38] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lprog_body:  # block prog_body
li t0, 1  # [op39] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 152(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
divu t2, t1, t2  # [op40] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld a1, 152(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mul t2, t2, a1  # [op41] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sub a1, t1, t2  # [op42] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 152(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mul t0, t0, t2  # [op43] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
divu t2, t1, t0  # [op44] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li a2, 2  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
divu a2, t2, a2  # [op45] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li a3, 2  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mul a2, a2, a3  # [op46] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sub t2, t2, a2  # [op47] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li a2, 2  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mul t0, t0, a2  # [op48] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw t0, a1, 0  # [op49] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw a1, t2, 0  # [op50] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 152(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw t2, t2, 0  # [op51] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t2, 2  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw t2, t2, 0  # [op52] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 16(t2)  # [op53] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd t2, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 112(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 8(t2)  # [op54] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t2, 7  # [op55] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
sllw a2, t0, t2  # [op56] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
li t0, 0  # [op57] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, s1  # [op58] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk1_head  # [op58] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk1_head:  # block chunk1_head
li s1, 128  # [op59] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
slt s1, t0, s1  # [op60] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
bne s1, zero, .Lbrc61_true  # [op61] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op61] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op61] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk1_exit  # [op61] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lbrc61_true:  # [op61] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk1_body  # [op61] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk1_exit:  # block chunk1_exit
li t2, 523528  # [op62] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add t2, s1, t2  # [op63] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
lw s1, 0(t2)  # [op64] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t2, 0  # [op65] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd t0, 96(sp)  # [op66] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op66] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 96(sp)  # [op66] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk2_head  # [op66] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk1_body:  # block chunk1_body
li s1, 32  # [op67] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli s1, s1, e32, m1, ta,ma  # [op68] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li s1, 32  # [op69] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:32
vid.v v1  # [op71] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:32
vadd.vx v1, v1, t0  # [op72] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:32
vmv.v.x v2, a2  # [op73] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
vadd.vv v1, v2, v1  # [op74] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
vid.v v2  # [op75] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
vadd.vx v2, v2, t0  # [op76] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
    # [peephole-li] [op77] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
vwadd.vx v4, v2, x0  # [op79] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
    # [peephole-li] [op80] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
vsetvli s1, s1, e64, m2, ta,ma  # [op81] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
li s1, 4  # [op82] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
vmul.vx v2, v4, s1  # [op83] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
li s1, 0  # [op84] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
ld a3, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
add s1, a3, s1  # [op85] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
li a3, 32  # [op86] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
vsetvli a3, a3, e32, m1, ta,ma  # [op87] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
vsuxei64.v v1, (s1), v2  # [op88] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
li s1, 32  # [op89] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
li s1, 8  # [op91] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
sllw s1, a1, s1  # [op92] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
li a3, 32  # [op93] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add t2, t2, a3  # [op94] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-li] [op95] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t0, a3  # [op96] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-li] [op97] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li a3, 523528  # [op99] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld a4, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add a3, a4, a3  # [op100] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sw s1, 0(a3)  # [op101] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk1_head  # [op102] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk2_head:  # block chunk2_head
li a1, 256  # [op103] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
slt a1, t0, a1  # [op104] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
bne a1, zero, .Lbrc105_true  # [op105] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op105] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op105] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk2_exit  # [op105] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lbrc105_true:  # [op105] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk2_body  # [op105] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk2_exit:  # block chunk2_exit
li t2, 0  # [op106] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd t0, 96(sp)  # [op107] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op107] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 96(sp)  # [op107] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk3_head  # [op107] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk2_body:  # block chunk2_body
li a1, 32  # [op108] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli a1, a1, e32, m1, ta,ma  # [op109] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li a1, 32  # [op110] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:32
vid.v v1  # [op112] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:32
vadd.vx v1, v1, t0  # [op113] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:32
vmv.v.x v2, s1  # [op114] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
vadd.vv v1, v2, v1  # [op115] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
vid.v v2  # [op116] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
vadd.vx v2, v2, t0  # [op117] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
    # [peephole-li] [op118] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
vwadd.vx v4, v2, x0  # [op120] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
    # [peephole-li] [op121] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
vsetvli a1, a1, e64, m2, ta,ma  # [op122] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
li a1, 4  # [op123] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
vmul.vx v2, v4, a1  # [op124] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
li a1, 512  # [op125] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
ld a2, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
add a1, a2, a1  # [op126] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
li a2, 32  # [op127] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
vsetvli a2, a2, e32, m1, ta,ma  # [op128] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
vsuxei64.v v1, (a1), v2  # [op129] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
li a1, 32  # [op130] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
    # [peephole-li] [op132] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add t2, t2, a1  # [op133] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-li] [op134] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t0, a1  # [op135] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-li] [op136] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk2_head  # [op138] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk3_head:  # block chunk3_head
li s1, 32  # [op139] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
slt s1, t0, s1  # [op140] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
bne s1, zero, .Lbrc141_true  # [op141] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op141] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op141] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk3_exit  # [op141] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lbrc141_true:  # [op141] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk3_body  # [op141] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk3_exit:  # block chunk3_exit
li t2, 0  # [op142] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd t0, 96(sp)  # [op143] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op143] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 96(sp)  # [op143] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk4_head  # [op143] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk3_body:  # block chunk3_body
li s1, 32  # [op144] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli s1, s1, e32, m1, ta,ma  # [op145] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li s1, 32  # [op146] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
vid.v v1  # [op148] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
vadd.vx v1, v1, t0  # [op149] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
vid.v v2  # [op150] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
vadd.vx v2, v2, t0  # [op151] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
    # [peephole-li] [op152] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
vwadd.vx v4, v2, x0  # [op154] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
    # [peephole-li] [op155] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
vsetvli s1, s1, e64, m2, ta,ma  # [op156] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
li s1, 4  # [op157] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
vmul.vx v2, v4, s1  # [op158] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
li s1, 1536  # [op159] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
ld a1, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
add s1, a1, s1  # [op160] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
li a1, 32  # [op161] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
vsetvli a1, a1, e32, m1, ta,ma  # [op162] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
vsuxei64.v v1, (s1), v2  # [op163] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
li s1, 32  # [op164] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
    # [peephole-li] [op166] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add t2, t2, s1  # [op167] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-li] [op168] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t0, s1  # [op169] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-li] [op170] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk3_head  # [op172] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk4_head:  # block chunk4_head
li s1, 128  # [op173] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
slt s1, t0, s1  # [op174] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
bne s1, zero, .Lbrc175_true  # [op175] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op175] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op175] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk4_exit  # [op175] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lbrc175_true:  # [op175] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk4_body  # [op175] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk4_exit:  # block chunk4_exit
li t2, 0  # [op176] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd t0, 96(sp)  # [op177] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op177] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 96(sp)  # [op177] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk5_head  # [op177] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk4_body:  # block chunk4_body
li s1, 32  # [op178] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli s1, s1, e32, m1, ta,ma  # [op179] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li s1, 32  # [op180] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vmv.v.x v1, s8  # [op182] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vid.v v2  # [op183] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vadd.vx v2, v2, t0  # [op184] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
    # [peephole-li] [op185] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vwadd.vx v4, v2, x0  # [op187] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
    # [peephole-li] [op188] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vsetvli s1, s1, e64, m2, ta,ma  # [op189] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
li s1, 4  # [op190] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vmul.vx v2, v4, s1  # [op191] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
li s1, 0  # [op192] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
ld a1, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
add s1, a1, s1  # [op193] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
li a1, 32  # [op194] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vsetvli a1, a1, e32, m1, ta,ma  # [op195] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vluxei64.v v4, (s1), v2  # [op196] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
li s1, 32  # [op197] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vmul.vv v1, v4, v1  # [op199] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vid.v v2  # [op200] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vadd.vx v2, v2, t0  # [op201] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
    # [peephole-li] [op202] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vwadd.vx v4, v2, x0  # [op204] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
    # [peephole-li] [op205] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vsetvli s1, s1, e64, m2, ta,ma  # [op206] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
li s1, 4  # [op207] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vmul.vx v2, v4, s1  # [op208] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
li s1, 2176  # [op209] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
ld a1, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
add s1, a1, s1  # [op210] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
li a1, 32  # [op211] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vsetvli a1, a1, e32, m1, ta,ma  # [op212] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vsuxei64.v v1, (s1), v2  # [op213] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
li s1, 32  # [op214] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
    # [peephole-li] [op216] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add t2, t2, s1  # [op217] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-li] [op218] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t0, s1  # [op219] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-li] [op220] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk4_head  # [op222] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk5_head:  # block chunk5_head
li s1, 32  # [op223] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
slt s1, t0, s1  # [op224] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
bne s1, zero, .Lbrc225_true  # [op225] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op225] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op225] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk5_exit  # [op225] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lbrc225_true:  # [op225] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk5_body  # [op225] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk5_exit:  # block chunk5_exit
li t2, 0  # [op226] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd t0, 96(sp)  # [op227] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op227] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 96(sp)  # [op227] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk6_head  # [op227] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk5_body:  # block chunk5_body
li s1, 32  # [op228] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli s1, s1, e32, m1, ta,ma  # [op229] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li s1, 32  # [op230] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add t2, t2, s1  # [op231] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-li] [op232] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t0, s1  # [op233] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-li] [op234] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk5_head  # [op236] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk6_head:  # block chunk6_head
li s1, 4096  # [op237] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
slt s1, t0, s1  # [op238] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
bne s1, zero, .Lbrc239_true  # [op239] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op239] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op239] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk6_exit  # [op239] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lbrc239_true:  # [op239] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk6_body  # [op239] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk6_exit:  # block chunk6_exit
li t2, 0  # [op240] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd t0, 96(sp)  # [op241] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op241] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 96(sp)  # [op241] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk7_head  # [op241] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk6_body:  # block chunk6_body
li s1, 32  # [op242] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli s1, s1, e32, m1, ta,ma  # [op243] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li s1, 32  # [op244] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
vid.v v1  # [op246] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
vadd.vx v1, v1, t0  # [op247] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
    # [peephole-li] [op248] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
vmv.v.x v2, s1  # [op249] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
vdiv.vv v1, v1, v2  # [op250] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
    # [peephole-li] [op251] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
vwadd.vx v2, v1, x0  # [op253] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
    # [peephole-li] [op254] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
vsetvli s1, s1, e64, m2, ta,ma  # [op255] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
li s1, 8  # [op256] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
vmul.vx v2, v2, s1  # [op257] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
li s1, 2688  # [op258] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
ld a1, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
add s1, a1, s1  # [op259] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
li a1, 32  # [op260] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
vluxei64.v v4, (s1), v2  # [op262] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
li s1, 32  # [op263] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
vsetvli s1, s1, e32, m1, ta,ma  # [op264] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
li s1, 32  # [op265] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add t2, t2, s1  # [op266] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-li] [op267] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t0, s1  # [op268] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-li] [op269] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk6_head  # [op271] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk7_head:  # block chunk7_head
li s1, 32  # [op272] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
slt s1, t0, s1  # [op273] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
bne s1, zero, .Lbrc274_true  # [op274] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op274] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op274] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk7_exit  # [op274] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lbrc274_true:  # [op274] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk7_body  # [op274] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk7_exit:  # block chunk7_exit
li t2, 0  # [op275] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd t0, 96(sp)  # [op276] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op276] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 96(sp)  # [op276] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk8_head  # [op276] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk7_body:  # block chunk7_body
li s1, 32  # [op277] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli s1, s1, e32, m1, ta,ma  # [op278] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li s1, 32  # [op279] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
ld s1, 136(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vmv.v.x v1, s1  # [op281] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vid.v v2  # [op282] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vadd.vx v2, v2, t0  # [op283] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
li s1, 32  # [op284] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vwadd.vx v4, v2, x0  # [op286] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
    # [peephole-li] [op287] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vsetvli s1, s1, e64, m2, ta,ma  # [op288] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
li s1, 4  # [op289] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vmul.vx v2, v4, s1  # [op290] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
li s1, 1536  # [op291] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
ld a1, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
add s1, a1, s1  # [op292] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
li a1, 32  # [op293] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vsetvli a1, a1, e32, m1, ta,ma  # [op294] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vluxei64.v v4, (s1), v2  # [op295] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
li s1, 32  # [op296] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vmul.vv v1, v4, v1  # [op298] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vid.v v2  # [op299] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vadd.vx v2, v2, t0  # [op300] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
    # [peephole-li] [op301] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vwadd.vx v4, v2, x0  # [op303] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
    # [peephole-li] [op304] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vsetvli s1, s1, e64, m2, ta,ma  # [op305] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
li s1, 4  # [op306] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vmul.vx v2, v4, s1  # [op307] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
li s1, 36608  # [op308] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
ld a1, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
add s1, a1, s1  # [op309] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
li a1, 32  # [op310] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vsetvli a1, a1, e32, m1, ta,ma  # [op311] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vsuxei64.v v1, (s1), v2  # [op312] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
li s1, 32  # [op313] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
    # [peephole-li] [op315] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add t2, t2, s1  # [op316] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-li] [op317] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t0, s1  # [op318] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-li] [op319] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk7_head  # [op321] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk8_head:  # block chunk8_head
li s1, 256  # [op322] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
slt s1, t0, s1  # [op323] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
bne s1, zero, .Lbrc324_true  # [op324] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op324] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op324] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk8_exit  # [op324] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lbrc324_true:  # [op324] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk8_body  # [op324] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk8_exit:  # block chunk8_exit
li t2, 0  # [op325] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd t0, 96(sp)  # [op326] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op326] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 96(sp)  # [op326] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk9_head  # [op326] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk8_body:  # block chunk8_body
li s1, 32  # [op327] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli s1, s1, e32, m1, ta,ma  # [op328] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li s1, 32  # [op329] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add t2, t2, s1  # [op330] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-li] [op331] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t0, s1  # [op332] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-li] [op333] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk8_head  # [op335] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk9_head:  # block chunk9_head
li s1, 8192  # [op336] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
slt s1, t0, s1  # [op337] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
bne s1, zero, .Lbrc338_true  # [op338] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op338] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op338] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk9_exit  # [op338] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lbrc338_true:  # [op338] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk9_body  # [op338] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk9_exit:  # block chunk9_exit
li t2, 0  # [op339] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv s1, t0  # [op340] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk10_head  # [op340] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk9_body:  # block chunk9_body
li s1, 32  # [op341] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli s1, s1, e32, m1, ta,ma  # [op342] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li s1, 32  # [op343] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
vid.v v1  # [op345] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
vadd.vx v1, v1, t0  # [op346] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
li s1, 256  # [op347] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
vmv.v.x v2, s1  # [op348] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
vdiv.vv v1, v1, v2  # [op349] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
li s1, 32  # [op350] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
vwadd.vx v2, v1, x0  # [op352] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
    # [peephole-li] [op353] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
vsetvli s1, s1, e64, m2, ta,ma  # [op354] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
li s1, 8  # [op355] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
vmul.vx v2, v2, s1  # [op356] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
li s1, 36736  # [op357] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
ld a1, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
add s1, a1, s1  # [op358] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
li a1, 32  # [op359] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
vluxei64.v v4, (s1), v2  # [op361] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
li s1, 32  # [op362] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
vsetvli s1, s1, e32, m1, ta,ma  # [op363] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
li s1, 32  # [op364] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add t2, t2, s1  # [op365] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-li] [op366] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t0, s1  # [op367] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-li] [op368] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk9_head  # [op370] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk10_head:  # block chunk10_head
li t0, 4096  # [op371] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
slt t0, t2, t0  # [op372] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
bne t0, zero, .Lbrc373_true  # [op373] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op373] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, s1  # [op373] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk10_exit  # [op373] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lbrc373_true:  # [op373] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk10_body  # [op373] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk10_exit:  # block chunk10_exit
li t2, 0  # [op374] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv s1, t0  # [op375] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk11_head  # [op375] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk10_body:  # block chunk10_body
li t0, 32  # [op376] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli t0, t0, e16, m1, ta,ma  # [op377] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t0, 32  # [op378] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli t0, t0, e32, m1, ta,ma  # [op379] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vid.v v1  # [op380] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vadd.vx v1, v1, t2  # [op381] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li t0, 32  # [op382] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.v.x v2, t0  # [op383] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vdiv.vv v1, v1, v2  # [op384] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
    # [peephole-li] [op385] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vwadd.vx v2, v1, x0  # [op387] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
    # [peephole-li] [op388] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli t0, t0, e64, m2, ta,ma  # [op389] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li t0, 4  # [op390] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmul.vx v2, v2, t0  # [op391] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li t0, 2176  # [op392] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
ld a1, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add t0, a1, t0  # [op393] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a1, 32  # [op394] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli a1, a1, e32, m1, ta,ma  # [op395] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vluxei64.v v1, (t0), v2  # [op396] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li t0, 32  # [op397] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli t0, t0, e16, m1, ta,ma  # [op398] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li t0, 32  # [op399] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli t0, t0, e32, m1, ta,ma  # [op400] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vid.v v2  # [op401] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vadd.vx v2, v2, t2  # [op402] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li t0, 32  # [op403] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.v.x v3, t0  # [op404] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vrem.vv v2, v2, v3  # [op405] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
    # [peephole-li] [op406] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vwadd.vx v4, v2, x0  # [op408] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
    # [peephole-li] [op409] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli t0, t0, e64, m2, ta,ma  # [op410] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li t0, 4  # [op411] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmul.vx v2, v4, t0  # [op412] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li t0, 1536  # [op413] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
ld a1, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add t0, a1, t0  # [op414] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a1, 32  # [op415] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli a1, a1, e32, m1, ta,ma  # [op416] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vluxei64.v v4, (t0), v2  # [op417] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li t0, 32  # [op418] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli t0, t0, e16, m1, ta,ma  # [op419] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li t0, 32  # [op420] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli t0, t0, e32, m1, ta,ma  # [op421] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vadd.vv v1, v1, v4  # [op422] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li t0, 32  # [op423] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli t0, t0, e16, m1, ta,ma  # [op424] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li t0, 0  # [op425] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.v.x v2, t0  # [op426] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li t0, 32  # [op427] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli t0, t0, e32, m1, ta,ma  # [op428] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vwadd.vx v2, v1, x0  # [op429] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li t0, 32  # [op430] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli t0, t0, e64, m2, ta,ma  # [op431] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li t0, 2  # [op432] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmul.vx v2, v2, t0  # [op433] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li t0, 32  # [op434] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli t0, t0, e16, m1, ta,ma  # [op435] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a1, 0  # [op436] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li t0, 16  # [op437] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli t0, t0, e64, m2, ta,ma  # [op438] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s t0, v2  # [op439] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vid.v v4  # [op440] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 2  # [op441] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmul.vx v4, v4, a2  # [op442] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vadd.vx v4, v4, t0  # [op443] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmsne.vv v4, v2, v4  # [op444] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vcpop.m a2, v4  # [op445] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a1, a1, a2  # [op446] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, s2, t0  # [op447] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vid.v v4  # [op448] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li t0, 16  # [op449] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vadd.vx v6, v4, t0  # [op450] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vrgather.vv v4, v2, v6  # [op451] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s t0, v4  # [op452] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vid.v v2  # [op453] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a3, 2  # [op454] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmul.vx v2, v2, a3  # [op455] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vadd.vx v2, v2, t0  # [op456] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmsne.vv v2, v4, v2  # [op457] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vcpop.m a3, v2  # [op458] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a1, a1, a3  # [op459] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a3, s2, t0  # [op460] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
bne a1, zero, .Lbrc461_true  # [op461] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
j .Lngl.t1  # [op461] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
.Lbrc461_true:  # [op461] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
j .Lngl.e1  # [op461] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
.Lngl.t1:  # block ngl.t1
li t0, 523392  # [op462] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
ld a1, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add t0, a1, t0  # [op463] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a1, 16  # [op464] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli a1, a1, e16, m1, ta,ma  # [op465] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vle16.v v1, 0(a2)  # [op466] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a1, 0  # [op467] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a1, t0, a1  # [op468] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vse16.v v1, 0(a1)  # [op469] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vle16.v v1, 0(a3)  # [op470] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a1, 32  # [op471] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a1, t0, a1  # [op472] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vse16.v v1, 0(a1)  # [op473] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a1, 32  # [op474] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli a1, a1, e16, m1, ta,ma  # [op475] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vle16.v v1, 0(t0)  # [op476] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
j .Lngl.j1  # [op477] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
.Lngl.e1:  # block ngl.e1
li t0, 32  # [op478] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli t0, t0, e32, m1, ta,ma  # [op479] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vwadd.vx v2, v1, x0  # [op480] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li t0, 32  # [op481] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli t0, t0, e64, m2, ta,ma  # [op482] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li t0, 2  # [op483] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmul.vx v2, v2, t0  # [op484] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li t0, 32  # [op485] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli t0, t0, e16, m1, ta,ma  # [op486] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li t0, 523392  # [op487] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
ld a1, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add t0, a1, t0  # [op488] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a1, 128  # [op489] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a1, t0, a1  # [op490] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a1, 32  # [op491] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli a1, a1, e64, m2, ta,ma  # [op492] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vadd.vx v2, v2, s2  # [op493] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a1, v2  # [op494] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 0  # [op495] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, t0, a2  # [op496] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a1, 0(a1)  # [op497] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a1, 0(a2)  # [op498] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op499] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a1, v2  # [op500] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 2  # [op501] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, t0, a2  # [op502] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a1, 0(a1)  # [op503] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a1, 0(a2)  # [op504] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op505] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a1, v2  # [op506] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 4  # [op507] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, t0, a2  # [op508] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a1, 0(a1)  # [op509] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a1, 0(a2)  # [op510] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op511] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a1, v2  # [op512] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 6  # [op513] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, t0, a2  # [op514] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a1, 0(a1)  # [op515] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a1, 0(a2)  # [op516] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op517] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a1, v2  # [op518] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 8  # [op519] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, t0, a2  # [op520] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a1, 0(a1)  # [op521] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a1, 0(a2)  # [op522] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op523] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a1, v2  # [op524] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 10  # [op525] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, t0, a2  # [op526] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a1, 0(a1)  # [op527] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a1, 0(a2)  # [op528] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op529] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a1, v2  # [op530] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 12  # [op531] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, t0, a2  # [op532] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a1, 0(a1)  # [op533] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a1, 0(a2)  # [op534] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op535] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a1, v2  # [op536] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 14  # [op537] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, t0, a2  # [op538] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a1, 0(a1)  # [op539] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a1, 0(a2)  # [op540] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op541] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a1, v2  # [op542] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 16  # [op543] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, t0, a2  # [op544] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a1, 0(a1)  # [op545] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a1, 0(a2)  # [op546] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op547] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a1, v2  # [op548] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 18  # [op549] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, t0, a2  # [op550] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a1, 0(a1)  # [op551] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a1, 0(a2)  # [op552] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op553] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a1, v2  # [op554] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 20  # [op555] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, t0, a2  # [op556] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a1, 0(a1)  # [op557] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a1, 0(a2)  # [op558] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op559] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a1, v2  # [op560] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 22  # [op561] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, t0, a2  # [op562] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a1, 0(a1)  # [op563] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a1, 0(a2)  # [op564] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op565] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a1, v2  # [op566] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 24  # [op567] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, t0, a2  # [op568] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a1, 0(a1)  # [op569] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a1, 0(a2)  # [op570] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op571] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a1, v2  # [op572] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 26  # [op573] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, t0, a2  # [op574] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a1, 0(a1)  # [op575] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a1, 0(a2)  # [op576] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op577] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a1, v2  # [op578] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 28  # [op579] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, t0, a2  # [op580] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a1, 0(a1)  # [op581] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a1, 0(a2)  # [op582] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op583] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a1, v2  # [op584] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 30  # [op585] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, t0, a2  # [op586] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a1, 0(a1)  # [op587] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a1, 0(a2)  # [op588] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op589] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a1, v2  # [op590] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 32  # [op591] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, t0, a2  # [op592] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a1, 0(a1)  # [op593] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a1, 0(a2)  # [op594] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op595] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a1, v2  # [op596] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 34  # [op597] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, t0, a2  # [op598] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a1, 0(a1)  # [op599] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a1, 0(a2)  # [op600] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op601] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a1, v2  # [op602] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 36  # [op603] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, t0, a2  # [op604] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a1, 0(a1)  # [op605] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a1, 0(a2)  # [op606] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op607] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a1, v2  # [op608] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 38  # [op609] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, t0, a2  # [op610] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a1, 0(a1)  # [op611] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a1, 0(a2)  # [op612] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op613] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a1, v2  # [op614] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 40  # [op615] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, t0, a2  # [op616] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a1, 0(a1)  # [op617] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a1, 0(a2)  # [op618] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op619] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a1, v2  # [op620] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 42  # [op621] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, t0, a2  # [op622] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a1, 0(a1)  # [op623] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a1, 0(a2)  # [op624] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op625] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a1, v2  # [op626] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 44  # [op627] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, t0, a2  # [op628] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a1, 0(a1)  # [op629] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a1, 0(a2)  # [op630] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op631] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a1, v2  # [op632] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 46  # [op633] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, t0, a2  # [op634] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a1, 0(a1)  # [op635] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a1, 0(a2)  # [op636] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op637] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a1, v2  # [op638] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 48  # [op639] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, t0, a2  # [op640] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a1, 0(a1)  # [op641] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a1, 0(a2)  # [op642] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op643] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a1, v2  # [op644] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 50  # [op645] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, t0, a2  # [op646] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a1, 0(a1)  # [op647] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a1, 0(a2)  # [op648] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op649] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a1, v2  # [op650] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 52  # [op651] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, t0, a2  # [op652] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a1, 0(a1)  # [op653] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a1, 0(a2)  # [op654] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op655] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a1, v2  # [op656] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 54  # [op657] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, t0, a2  # [op658] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a1, 0(a1)  # [op659] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a1, 0(a2)  # [op660] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op661] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a1, v2  # [op662] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 56  # [op663] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, t0, a2  # [op664] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a1, 0(a1)  # [op665] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a1, 0(a2)  # [op666] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op667] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a1, v2  # [op668] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 58  # [op669] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, t0, a2  # [op670] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a1, 0(a1)  # [op671] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a1, 0(a2)  # [op672] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op673] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a1, v2  # [op674] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 60  # [op675] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, t0, a2  # [op676] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a1, 0(a1)  # [op677] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a1, 0(a2)  # [op678] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op679] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a1, v2  # [op680] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 62  # [op681] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, t0, a2  # [op682] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a1, 0(a1)  # [op683] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a1, 0(a2)  # [op684] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op685] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a1, 32  # [op686] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli a1, a1, e16, m1, ta,ma  # [op687] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vle16.v v1, 0(t0)  # [op688] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
j .Lngl.j1  # [op689] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
.Lngl.j1:  # block ngl.j1
li t0, 32  # [op690] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli t0, t0, e16, m1, ta,ma  # [op691] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li t0, 103552  # [op692] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
ld a1, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add t0, a1, t0  # [op693] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
mv a1, t2  # [op694] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 2  # [op695] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
mul a1, a1, a2  # [op696] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add t0, t0, a1  # [op697] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vse16.v v1, 0(t0)  # [op698] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li t0, 32  # [op699] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add t0, s1, t0  # [op700] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li s1, 32  # [op701] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t2, t2, s1  # [op702] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-li] [op703] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv s1, t0  # [op705] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk10_head  # [op705] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk11_head:  # block chunk11_head
li t0, 8192  # [op706] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
slt t0, t2, t0  # [op707] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
bne t0, zero, .Lbrc708_true  # [op708] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op708] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, s1  # [op708] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk11_exit  # [op708] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lbrc708_true:  # [op708] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk11_body  # [op708] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk11_exit:  # block chunk11_exit
li t2, 0  # [op709] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd t0, 96(sp)  # [op710] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op710] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 96(sp)  # [op710] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk12_head  # [op710] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk11_body:  # block chunk11_body
li t0, 32  # [op711] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli t0, t0, e16, m1, ta,ma  # [op712] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t0, 32  # [op713] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli t0, t0, e32, m1, ta,ma  # [op714] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vid.v v1  # [op715] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vadd.vx v1, v1, t2  # [op716] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li t0, 256  # [op717] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.v.x v2, t0  # [op718] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vdiv.vv v1, v1, v2  # [op719] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li t0, 32  # [op720] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vwadd.vx v2, v1, x0  # [op722] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
    # [peephole-li] [op723] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli t0, t0, e64, m2, ta,ma  # [op724] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li t0, 4  # [op725] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmul.vx v2, v2, t0  # [op726] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li t0, 36608  # [op727] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
ld a1, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add t0, a1, t0  # [op728] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a1, 32  # [op729] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli a1, a1, e32, m1, ta,ma  # [op730] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vluxei64.v v1, (t0), v2  # [op731] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li t0, 32  # [op732] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli t0, t0, e16, m1, ta,ma  # [op733] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li t0, 32  # [op734] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli t0, t0, e32, m1, ta,ma  # [op735] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vid.v v2  # [op736] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vadd.vx v2, v2, t2  # [op737] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li t0, 256  # [op738] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.v.x v3, t0  # [op739] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vrem.vv v2, v2, v3  # [op740] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li t0, 32  # [op741] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vwadd.vx v4, v2, x0  # [op743] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
    # [peephole-li] [op744] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli t0, t0, e64, m2, ta,ma  # [op745] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li t0, 4  # [op746] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmul.vx v2, v4, t0  # [op747] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li t0, 512  # [op748] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
ld a1, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add t0, a1, t0  # [op749] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a1, 32  # [op750] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli a1, a1, e32, m1, ta,ma  # [op751] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vluxei64.v v4, (t0), v2  # [op752] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li t0, 32  # [op753] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli t0, t0, e16, m1, ta,ma  # [op754] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li t0, 32  # [op755] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli t0, t0, e32, m1, ta,ma  # [op756] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vadd.vv v1, v1, v4  # [op757] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li t0, 32  # [op758] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli t0, t0, e16, m1, ta,ma  # [op759] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li t0, 0  # [op760] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.v.x v2, t0  # [op761] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li t0, 32  # [op762] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli t0, t0, e32, m1, ta,ma  # [op763] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vwadd.vx v2, v1, x0  # [op764] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li t0, 32  # [op765] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli t0, t0, e64, m2, ta,ma  # [op766] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li t0, 2  # [op767] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmul.vx v2, v2, t0  # [op768] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li t0, 32  # [op769] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli t0, t0, e16, m1, ta,ma  # [op770] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a1, 0  # [op771] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li t0, 16  # [op772] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli t0, t0, e64, m2, ta,ma  # [op773] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s t0, v2  # [op774] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vid.v v4  # [op775] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 2  # [op776] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmul.vx v4, v4, a2  # [op777] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vadd.vx v4, v4, t0  # [op778] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmsne.vv v4, v2, v4  # [op779] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vcpop.m a2, v4  # [op780] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a1, a1, a2  # [op781] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, s3, t0  # [op782] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vid.v v4  # [op783] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li t0, 16  # [op784] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vadd.vx v6, v4, t0  # [op785] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vrgather.vv v4, v2, v6  # [op786] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s t0, v4  # [op787] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vid.v v2  # [op788] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 2  # [op789] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmul.vx v2, v2, a3  # [op790] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vadd.vx v2, v2, t0  # [op791] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmsne.vv v2, v4, v2  # [op792] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vcpop.m a3, v2  # [op793] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a1, a1, a3  # [op794] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, s3, t0  # [op795] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
bne a1, zero, .Lbrc796_true  # [op796] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
j .Lngl.t2  # [op796] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
.Lbrc796_true:  # [op796] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
j .Lngl.e2  # [op796] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
.Lngl.t2:  # block ngl.t2
li t0, 523392  # [op797] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
ld a1, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add t0, a1, t0  # [op798] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a1, 16  # [op799] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli a1, a1, e16, m1, ta,ma  # [op800] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vle16.v v1, 0(a2)  # [op801] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a1, 0  # [op802] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a1, t0, a1  # [op803] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vse16.v v1, 0(a1)  # [op804] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vle16.v v1, 0(a3)  # [op805] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a1, 32  # [op806] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a1, t0, a1  # [op807] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vse16.v v1, 0(a1)  # [op808] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a1, 32  # [op809] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli a1, a1, e16, m1, ta,ma  # [op810] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vle16.v v1, 0(t0)  # [op811] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
j .Lngl.j2  # [op812] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
.Lngl.e2:  # block ngl.e2
li t0, 32  # [op813] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli t0, t0, e32, m1, ta,ma  # [op814] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vwadd.vx v2, v1, x0  # [op815] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li t0, 32  # [op816] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli t0, t0, e64, m2, ta,ma  # [op817] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li t0, 2  # [op818] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmul.vx v2, v2, t0  # [op819] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li t0, 32  # [op820] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli t0, t0, e16, m1, ta,ma  # [op821] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li t0, 523392  # [op822] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
ld a1, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add t0, a1, t0  # [op823] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a1, 128  # [op824] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a1, t0, a1  # [op825] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a1, 32  # [op826] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli a1, a1, e64, m2, ta,ma  # [op827] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vadd.vx v2, v2, s3  # [op828] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a1, v2  # [op829] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 0  # [op830] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, t0, a2  # [op831] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a1, 0(a1)  # [op832] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a1, 0(a2)  # [op833] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op834] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a1, v2  # [op835] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 2  # [op836] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, t0, a2  # [op837] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a1, 0(a1)  # [op838] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a1, 0(a2)  # [op839] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op840] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a1, v2  # [op841] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 4  # [op842] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, t0, a2  # [op843] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a1, 0(a1)  # [op844] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a1, 0(a2)  # [op845] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op846] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a1, v2  # [op847] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 6  # [op848] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, t0, a2  # [op849] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a1, 0(a1)  # [op850] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a1, 0(a2)  # [op851] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op852] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a1, v2  # [op853] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 8  # [op854] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, t0, a2  # [op855] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a1, 0(a1)  # [op856] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a1, 0(a2)  # [op857] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op858] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a1, v2  # [op859] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 10  # [op860] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, t0, a2  # [op861] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a1, 0(a1)  # [op862] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a1, 0(a2)  # [op863] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op864] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a1, v2  # [op865] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 12  # [op866] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, t0, a2  # [op867] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a1, 0(a1)  # [op868] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a1, 0(a2)  # [op869] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op870] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a1, v2  # [op871] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 14  # [op872] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, t0, a2  # [op873] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a1, 0(a1)  # [op874] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a1, 0(a2)  # [op875] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op876] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a1, v2  # [op877] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 16  # [op878] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, t0, a2  # [op879] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a1, 0(a1)  # [op880] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a1, 0(a2)  # [op881] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op882] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a1, v2  # [op883] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 18  # [op884] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, t0, a2  # [op885] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a1, 0(a1)  # [op886] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a1, 0(a2)  # [op887] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op888] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a1, v2  # [op889] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 20  # [op890] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, t0, a2  # [op891] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a1, 0(a1)  # [op892] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a1, 0(a2)  # [op893] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op894] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a1, v2  # [op895] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 22  # [op896] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, t0, a2  # [op897] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a1, 0(a1)  # [op898] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a1, 0(a2)  # [op899] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op900] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a1, v2  # [op901] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 24  # [op902] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, t0, a2  # [op903] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a1, 0(a1)  # [op904] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a1, 0(a2)  # [op905] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op906] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a1, v2  # [op907] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 26  # [op908] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, t0, a2  # [op909] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a1, 0(a1)  # [op910] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a1, 0(a2)  # [op911] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op912] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a1, v2  # [op913] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 28  # [op914] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, t0, a2  # [op915] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a1, 0(a1)  # [op916] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a1, 0(a2)  # [op917] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op918] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a1, v2  # [op919] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 30  # [op920] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, t0, a2  # [op921] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a1, 0(a1)  # [op922] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a1, 0(a2)  # [op923] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op924] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a1, v2  # [op925] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 32  # [op926] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, t0, a2  # [op927] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a1, 0(a1)  # [op928] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a1, 0(a2)  # [op929] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op930] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a1, v2  # [op931] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 34  # [op932] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, t0, a2  # [op933] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a1, 0(a1)  # [op934] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a1, 0(a2)  # [op935] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op936] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a1, v2  # [op937] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 36  # [op938] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, t0, a2  # [op939] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a1, 0(a1)  # [op940] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a1, 0(a2)  # [op941] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op942] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a1, v2  # [op943] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 38  # [op944] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, t0, a2  # [op945] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a1, 0(a1)  # [op946] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a1, 0(a2)  # [op947] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op948] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a1, v2  # [op949] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 40  # [op950] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, t0, a2  # [op951] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a1, 0(a1)  # [op952] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a1, 0(a2)  # [op953] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op954] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a1, v2  # [op955] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 42  # [op956] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, t0, a2  # [op957] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a1, 0(a1)  # [op958] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a1, 0(a2)  # [op959] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op960] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a1, v2  # [op961] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 44  # [op962] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, t0, a2  # [op963] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a1, 0(a1)  # [op964] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a1, 0(a2)  # [op965] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op966] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a1, v2  # [op967] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 46  # [op968] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, t0, a2  # [op969] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a1, 0(a1)  # [op970] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a1, 0(a2)  # [op971] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op972] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a1, v2  # [op973] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 48  # [op974] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, t0, a2  # [op975] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a1, 0(a1)  # [op976] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a1, 0(a2)  # [op977] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op978] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a1, v2  # [op979] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 50  # [op980] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, t0, a2  # [op981] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a1, 0(a1)  # [op982] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a1, 0(a2)  # [op983] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op984] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a1, v2  # [op985] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 52  # [op986] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, t0, a2  # [op987] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a1, 0(a1)  # [op988] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a1, 0(a2)  # [op989] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op990] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a1, v2  # [op991] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 54  # [op992] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, t0, a2  # [op993] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a1, 0(a1)  # [op994] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a1, 0(a2)  # [op995] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op996] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a1, v2  # [op997] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 56  # [op998] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, t0, a2  # [op999] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a1, 0(a1)  # [op1000] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a1, 0(a2)  # [op1001] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op1002] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a1, v2  # [op1003] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 58  # [op1004] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, t0, a2  # [op1005] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a1, 0(a1)  # [op1006] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a1, 0(a2)  # [op1007] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op1008] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a1, v2  # [op1009] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 60  # [op1010] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, t0, a2  # [op1011] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a1, 0(a1)  # [op1012] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a1, 0(a2)  # [op1013] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op1014] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a1, v2  # [op1015] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 62  # [op1016] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, t0, a2  # [op1017] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a1, 0(a1)  # [op1018] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a1, 0(a2)  # [op1019] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op1020] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a1, 32  # [op1021] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli a1, a1, e16, m1, ta,ma  # [op1022] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vle16.v v1, 0(t0)  # [op1023] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
j .Lngl.j2  # [op1024] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
.Lngl.j2:  # block ngl.j2
li t0, 32  # [op1025] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli t0, t0, e16, m1, ta,ma  # [op1026] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li t0, 111744  # [op1027] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
ld a1, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add t0, a1, t0  # [op1028] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
mv a1, t2  # [op1029] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 2  # [op1030] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
mul a1, a1, a2  # [op1031] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add t0, t0, a1  # [op1032] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vse16.v v1, 0(t0)  # [op1033] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li t0, 32  # [op1034] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add t0, s1, t0  # [op1035] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li s1, 32  # [op1036] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t2, t2, s1  # [op1037] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-li] [op1038] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv s1, t0  # [op1040] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk11_head  # [op1040] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk12_head:  # block chunk12_head
li s1, 32768  # [op1041] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
slt s1, t0, s1  # [op1042] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
bne s1, zero, .Lbrc1043_true  # [op1043] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t1  # [op1043] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv s11, t2  # [op1043] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk12_exit  # [op1043] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lbrc1043_true:  # [op1043] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk12_body  # [op1043] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk12_exit:  # block chunk12_exit
li t0, 522880  # [op1044] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t2, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t0, t2, t0  # [op1045] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sd t0, 168(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t0, 128  # [op1046] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t2, 168(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a1, t2, t0  # [op1047] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t0, 256  # [op1048] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t2, 168(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a2, t2, t0  # [op1049] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t0, 8  # [op1050] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t0, t0, e32, m1, ta,ma  # [op1051] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vid.v v1  # [op1052] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t0, 8  # [op1053] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vid.v v2  # [op1055] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t0, 64  # [op1056] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t0, t0, e16, m1, ta,ma  # [op1057] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t0, 0  # [op1058] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v3, t0  # [op1059] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v4, t0  # [op1060] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-li] [op1061] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t3, 512  # [op1062] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mv a7, t0  # [op1063] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lmtile13.head  # [op1063] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lchunk12_body:  # block chunk12_body
li s1, 32  # [op1064] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli s1, s1, e32, m1, ta,ma  # [op1065] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li s1, 0  # [op1066] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
li a1, 32  # [op1067] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
vmv.v.x v1, s1  # [op1069] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
vid.v v2  # [op1070] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
vadd.vx v2, v2, t0  # [op1071] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
li s1, 32  # [op1072] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
vwadd.vx v4, v2, x0  # [op1074] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
    # [peephole-li] [op1075] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
vsetvli s1, s1, e64, m2, ta,ma  # [op1076] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
li s1, 4  # [op1077] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
vmul.vx v2, v4, s1  # [op1078] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
li s1, 128128  # [op1079] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
ld a1, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
add s1, a1, s1  # [op1080] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
li a1, 32  # [op1081] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
vsetvli a1, a1, e32, m1, ta,ma  # [op1082] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
vsuxei64.v v1, (s1), v2  # [op1083] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
li s1, 32  # [op1084] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
    # [peephole-li] [op1086] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add t2, t2, s1  # [op1087] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-li] [op1088] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t0, s1  # [op1089] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-li] [op1090] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk12_head  # [op1092] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lmtile13.head:  # block mtile13.head
slt t0, a7, t3  # [op1093] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
bne t0, zero, .Lbrc1094_true  # [op1094] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mv t0, a7  # [op1094] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lmtile13.exit  # [op1094] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lbrc1094_true:  # [op1094] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lmtile13.body  # [op1094] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lmtile13.body:  # block mtile13.body
li s5, 32  # [op1095] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
divu t0, a7, s5  # [op1096] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t2, t0, s5  # [op1097] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub s1, a7, t2  # [op1098] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t2, 8  # [op1099] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t0, t0, t2  # [op1100] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t2, s1, t2  # [op1101] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sd t2, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t2, 64  # [op1102] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t2, t2, e32, m2, ta,ma  # [op1103] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t2, 0  # [op1104] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v6, t2  # [op1105] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-li] [op1106] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lmk14.head  # [op1107] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lmtile13.exit:  # block mtile13.exit
li t0, 0  # [op1108] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, s11  # [op1109] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk18_head  # [op1109] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lmk14.head:  # block mk14.head
slt s1, t2, s5  # [op1110] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
bne s1, zero, .Lbrc1111_true  # [op1111] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lmk14.exit  # [op1111] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lbrc1111_true:  # [op1111] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lmk14.body  # [op1111] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lmk14.body:  # block mk14.body
li s1, 32  # [op1112] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub s1, s1, t2  # [op1113] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sd s1, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s1, 8  # [op1114] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a3, t0, s1  # [op1115] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a4, 129  # [op1116] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt a3, a3, a4  # [op1117] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a4, 1  # [op1118] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a5, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a4, a5, a4  # [op1119] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt s1, s1, a4  # [op1120] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and s1, a3, s1  # [op1121] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
bne s1, zero, .Lbrc1122_true  # [op1122] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Ltaf15.else  # [op1122] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lbrc1122_true:  # [op1122] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Ltaf15.then  # [op1122] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lmk14.exit:  # block mk14.exit
li t2, 64  # [op1123] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t2, t2, e32, m2, ta,ma  # [op1124] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse32.v v6, 0(a2)  # [op1125] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t2, 0  # [op1126] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a3, t0, t2  # [op1127] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s1, 128  # [op1128] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt a5, a3, s1  # [op1129] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a4, 256  # [op1130] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a6, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub a6, a4, a6  # [op1131] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub a5, t2, a5  # [op1132] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and a5, a6, a5  # [op1133] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw a5, a5, 0  # [op1134] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a6, 8  # [op1135] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli a6, a6, e32, m1, ta,ma  # [op1136] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, a5  # [op1137] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v2, v5  # [op1138] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1139] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a5, a2, t2  # [op1140] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a6, 8  # [op1141] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle32.v v5, 0(a5)  # [op1143] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a5, 259200  # [op1144] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a6, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s5, a6, a5  # [op1145] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a6, 1024  # [op1146] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul a3, a3, a6  # [op1147] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s5, s5, a3  # [op1148] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a3, 4  # [op1149] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld s6, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s6, s6, a3  # [op1150] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s5, s5, s6  # [op1151] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 8  # [op1152] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse32.v v5, 0(s5), v0.t  # [op1154] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s5, 1  # [op1155] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t0, s5  # [op1156] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t4, s6, s1  # [op1157] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t5, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t5, a4, t5  # [op1158] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, t2, t4  # [op1159] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t4, t5, t4  # [op1160] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw t4, t4, 0  # [op1161] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t5, 8  # [op1162] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, t4  # [op1164] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v2, v5  # [op1165] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1166] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t4, 32  # [op1167] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t4, a2, t4  # [op1168] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-li] [op1169] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle32.v v5, 0(t4)  # [op1171] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t4, t4, a5  # [op1172] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s6, s6, a6  # [op1173] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t4, s6  # [op1174] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t4, t4, a3  # [op1175] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s6, t4  # [op1176] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t4, 8  # [op1177] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse32.v v5, 0(s6), v0.t  # [op1179] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 2  # [op1180] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t0, s6  # [op1181] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t4, s6, s1  # [op1182] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t5, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t5, a4, t5  # [op1183] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, t2, t4  # [op1184] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t4, t5, t4  # [op1185] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw t4, t4, 0  # [op1186] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t5, 8  # [op1187] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, t4  # [op1189] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v2, v5  # [op1190] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1191] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t4, 64  # [op1192] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t4, a2, t4  # [op1193] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-li] [op1194] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle32.v v5, 0(t4)  # [op1196] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t4, t4, a5  # [op1197] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s6, s6, a6  # [op1198] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t4, s6  # [op1199] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t4, t4, a3  # [op1200] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s6, t4  # [op1201] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t4, 8  # [op1202] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse32.v v5, 0(s6), v0.t  # [op1204] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 3  # [op1205] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t0, s6  # [op1206] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t4, s6, s1  # [op1207] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t5, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t5, a4, t5  # [op1208] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, t2, t4  # [op1209] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t4, t5, t4  # [op1210] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw t4, t4, 0  # [op1211] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t5, 8  # [op1212] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, t4  # [op1214] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v2, v5  # [op1215] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1216] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t4, 96  # [op1217] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t4, a2, t4  # [op1218] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-li] [op1219] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle32.v v5, 0(t4)  # [op1221] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t4, t4, a5  # [op1222] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s6, s6, a6  # [op1223] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t4, s6  # [op1224] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t4, t4, a3  # [op1225] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s6, t4  # [op1226] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t4, 8  # [op1227] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse32.v v5, 0(s6), v0.t  # [op1229] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t0, a3  # [op1230] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t4, s6, s1  # [op1231] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t5, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t5, a4, t5  # [op1232] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, t2, t4  # [op1233] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t4, t5, t4  # [op1234] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw t4, t4, 0  # [op1235] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t5, 8  # [op1236] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, t4  # [op1238] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v2, v5  # [op1239] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1240] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t4, a2, s1  # [op1241] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-li] [op1242] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle32.v v5, 0(t4)  # [op1244] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t4, t4, a5  # [op1245] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s6, s6, a6  # [op1246] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t4, s6  # [op1247] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t4, t4, a3  # [op1248] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s6, t4  # [op1249] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t4, 8  # [op1250] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse32.v v5, 0(s6), v0.t  # [op1252] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 5  # [op1253] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t0, s6  # [op1254] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t4, s6, s1  # [op1255] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t5, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t5, a4, t5  # [op1256] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, t2, t4  # [op1257] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t4, t5, t4  # [op1258] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw t4, t4, 0  # [op1259] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t5, 8  # [op1260] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, t4  # [op1262] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v2, v5  # [op1263] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1264] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t4, 160  # [op1265] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t4, a2, t4  # [op1266] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-li] [op1267] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle32.v v5, 0(t4)  # [op1269] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t4, t4, a5  # [op1270] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s6, s6, a6  # [op1271] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t4, s6  # [op1272] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t4, t4, a3  # [op1273] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s6, t4  # [op1274] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t4, 8  # [op1275] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse32.v v5, 0(s6), v0.t  # [op1277] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 6  # [op1278] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t0, s6  # [op1279] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t4, s6, s1  # [op1280] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t5, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t5, a4, t5  # [op1281] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, t2, t4  # [op1282] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t4, t5, t4  # [op1283] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw t4, t4, 0  # [op1284] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t5, 8  # [op1285] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, t4  # [op1287] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v2, v5  # [op1288] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1289] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t4, 192  # [op1290] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t4, a2, t4  # [op1291] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-li] [op1292] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle32.v v5, 0(t4)  # [op1294] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t4, t4, a5  # [op1295] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s6, s6, a6  # [op1296] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t4, s6  # [op1297] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t4, t4, a3  # [op1298] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s6, t4  # [op1299] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t4, 8  # [op1300] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse32.v v5, 0(s6), v0.t  # [op1302] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 7  # [op1303] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t0, t0, s6  # [op1304] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt s1, t0, s1  # [op1305] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld s6, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub a4, a4, s6  # [op1306] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t2, t2, s1  # [op1307] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t2, a4, t2  # [op1308] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw t2, t2, 0  # [op1309] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s1, 8  # [op1310] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, t2  # [op1312] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v2, v5  # [op1313] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1314] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t2, 224  # [op1315] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t2, a2, t2  # [op1316] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-li] [op1317] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle32.v v5, 0(t2)  # [op1319] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t2, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t2, t2, a5  # [op1320] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t0, t0, a6  # [op1321] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t0, t2, t0  # [op1322] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t2, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t2, t2, a3  # [op1323] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t0, t0, t2  # [op1324] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t2, 8  # [op1325] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse32.v v5, 0(t0), v0.t  # [op1327] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t0, a7, s5  # [op1328] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mv a7, t0  # [op1329] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lmtile13.head  # [op1329] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Ltaf15.then:  # block taf15.then
li s1, 8  # [op1330] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli s1, s1, e16, m1, ta,ma  # [op1331] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s1, 103552  # [op1332] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a3, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a3, a3, s1  # [op1333] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s1, 64  # [op1334] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul a4, t0, s1  # [op1335] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a3, a3, a4  # [op1336] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a4, 2  # [op1337] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul a4, t2, a4  # [op1338] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a3, a3, a4  # [op1339] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(a3)  # [op1340] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a4, 168(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a4)  # [op1341] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a4, a3, s1  # [op1342] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a3, 16  # [op1343] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a5, 168(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a5, a5, a3  # [op1344] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(a4)  # [op1345] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a5)  # [op1346] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a4, a4, s1  # [op1347] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a5, a5, a3  # [op1348] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(a4)  # [op1349] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a5)  # [op1350] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a4, a4, s1  # [op1351] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a5, a5, a3  # [op1352] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(a4)  # [op1353] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a5)  # [op1354] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a4, a4, s1  # [op1355] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a5, a5, a3  # [op1356] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(a4)  # [op1357] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a5)  # [op1358] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a4, a4, s1  # [op1359] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a5, a5, a3  # [op1360] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(a4)  # [op1361] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a5)  # [op1362] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a4, a4, s1  # [op1363] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a5, a5, a3  # [op1364] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(a4)  # [op1365] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a5)  # [op1366] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s1, a4, s1  # [op1367] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a3, a5, a3  # [op1368] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(s1)  # [op1369] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a3)  # [op1370] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Ltaf15.join  # [op1371] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Ltaf15.else:  # block taf15.else
li s1, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a4, t0, s1  # [op1373] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a5, 128  # [op1374] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt a3, a4, a5  # [op1375] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s1, 8  # [op1376] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a6, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt a6, a6, s1  # [op1377] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub a6, s6, a6  # [op1378] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld s6, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub s6, s1, s6  # [op1379] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and a6, s6, a6  # [op1380] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld s6, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a6, s6, a6  # [op1381] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub a3, s6, a3  # [op1382] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and a3, a6, a3  # [op1383] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw a3, a3, 0  # [op1384] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a6, 8  # [op1385] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli a6, a6, e32, m1, ta,ma  # [op1386] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, a3  # [op1387] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v1, v5  # [op1388] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1389] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a6, 103552  # [op1390] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a3, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, a3, a6  # [op1391] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a3, 64  # [op1392] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul a4, a4, a3  # [op1393] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s6, a4  # [op1394] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a4, 2  # [op1395] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t4, t2, a4  # [op1396] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s6, t4  # [op1397] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t4, 8  # [op1398] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t4, t4, e16, m1, ta,ma  # [op1399] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(s6), v0.t  # [op1400] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmerge.vvm v5, v3, v5, v0  # [op1401] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld s6, 168(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t4, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s6, t4  # [op1402] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t4, 8  # [op1403] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(s6)  # [op1405] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 1  # [op1406] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t0, s6  # [op1407] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t4, s6, a5  # [op1408] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t5, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t5, t5, s1  # [op1409] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t6, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t5, t6, t5  # [op1410] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t6, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t6, s1, t6  # [op1411] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t5, t6, t5  # [op1412] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t6, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t5, t6, t5  # [op1413] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t6, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, t6, t4  # [op1414] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t4, t5, t4  # [op1415] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw t4, t4, 0  # [op1416] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t5, 8  # [op1417] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t5, t5, e32, m1, ta,ma  # [op1418] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, t4  # [op1419] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v1, v5  # [op1420] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1421] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t4, t4, a6  # [op1422] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s6, s6, a3  # [op1423] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t4, s6  # [op1424] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t4, t2, a4  # [op1425] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s6, t4  # [op1426] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t4, 8  # [op1427] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t4, t4, e16, m1, ta,ma  # [op1428] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(s6), v0.t  # [op1429] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmerge.vvm v5, v3, v5, v0  # [op1430] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 16  # [op1431] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 168(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t4, s6  # [op1432] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t4, 8  # [op1433] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(s6)  # [op1435] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t0, a4  # [op1436] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t4, s6, a5  # [op1437] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t5, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t5, t5, s1  # [op1438] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-li] [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t5, t6, t5  # [op1439] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t6, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t6, s1, t6  # [op1440] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t5, t6, t5  # [op1441] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t6, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t5, t6, t5  # [op1442] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t6, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, t6, t4  # [op1443] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t4, t5, t4  # [op1444] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw t4, t4, 0  # [op1445] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t5, 8  # [op1446] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t5, t5, e32, m1, ta,ma  # [op1447] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, t4  # [op1448] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v1, v5  # [op1449] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1450] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t4, t4, a6  # [op1451] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s6, s6, a3  # [op1452] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t4, s6  # [op1453] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t4, t2, a4  # [op1454] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s6, t4  # [op1455] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t4, 8  # [op1456] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t4, t4, e16, m1, ta,ma  # [op1457] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(s6), v0.t  # [op1458] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmerge.vvm v5, v3, v5, v0  # [op1459] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 32  # [op1460] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 168(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t4, s6  # [op1461] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t4, 8  # [op1462] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(s6)  # [op1464] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 3  # [op1465] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t0, s6  # [op1466] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t4, s6, a5  # [op1467] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t5, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t5, t5, s1  # [op1468] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-li] [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t5, t6, t5  # [op1469] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t6, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t6, s1, t6  # [op1470] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t5, t6, t5  # [op1471] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t6, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t5, t6, t5  # [op1472] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t6, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, t6, t4  # [op1473] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t4, t5, t4  # [op1474] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw t4, t4, 0  # [op1475] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t5, 8  # [op1476] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t5, t5, e32, m1, ta,ma  # [op1477] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, t4  # [op1478] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v1, v5  # [op1479] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1480] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t4, t4, a6  # [op1481] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s6, s6, a3  # [op1482] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t4, s6  # [op1483] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t4, t2, a4  # [op1484] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s6, t4  # [op1485] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t4, 8  # [op1486] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t4, t4, e16, m1, ta,ma  # [op1487] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(s6), v0.t  # [op1488] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmerge.vvm v5, v3, v5, v0  # [op1489] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 48  # [op1490] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 168(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t4, s6  # [op1491] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t4, 8  # [op1492] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(s6)  # [op1494] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 4  # [op1495] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t0, s6  # [op1496] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t4, s6, a5  # [op1497] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t5, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t5, t5, s1  # [op1498] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-li] [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t5, t6, t5  # [op1499] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t6, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t6, s1, t6  # [op1500] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t5, t6, t5  # [op1501] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t6, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t5, t6, t5  # [op1502] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t6, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, t6, t4  # [op1503] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t4, t5, t4  # [op1504] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw t4, t4, 0  # [op1505] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t5, 8  # [op1506] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t5, t5, e32, m1, ta,ma  # [op1507] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, t4  # [op1508] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v1, v5  # [op1509] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1510] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t4, t4, a6  # [op1511] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s6, s6, a3  # [op1512] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t4, s6  # [op1513] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t4, t2, a4  # [op1514] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s6, t4  # [op1515] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t4, 8  # [op1516] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t4, t4, e16, m1, ta,ma  # [op1517] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(s6), v0.t  # [op1518] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmerge.vvm v5, v3, v5, v0  # [op1519] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld s6, 168(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s6, a3  # [op1520] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t4, 8  # [op1521] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(s6)  # [op1523] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 5  # [op1524] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t0, s6  # [op1525] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t4, s6, a5  # [op1526] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t5, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t5, t5, s1  # [op1527] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-li] [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t5, t6, t5  # [op1528] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t6, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t6, s1, t6  # [op1529] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t5, t6, t5  # [op1530] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t6, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t5, t6, t5  # [op1531] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t6, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, t6, t4  # [op1532] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t4, t5, t4  # [op1533] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw t4, t4, 0  # [op1534] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t5, 8  # [op1535] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t5, t5, e32, m1, ta,ma  # [op1536] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, t4  # [op1537] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v1, v5  # [op1538] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1539] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t4, t4, a6  # [op1540] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s6, s6, a3  # [op1541] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t4, s6  # [op1542] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t4, t2, a4  # [op1543] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s6, t4  # [op1544] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t4, 8  # [op1545] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t4, t4, e16, m1, ta,ma  # [op1546] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(s6), v0.t  # [op1547] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmerge.vvm v5, v3, v5, v0  # [op1548] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 80  # [op1549] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 168(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t4, s6  # [op1550] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t4, 8  # [op1551] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(s6)  # [op1553] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 6  # [op1554] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t0, s6  # [op1555] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t4, s6, a5  # [op1556] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t5, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t5, t5, s1  # [op1557] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-li] [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t5, t6, t5  # [op1558] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t6, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t6, s1, t6  # [op1559] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t5, t6, t5  # [op1560] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t6, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t5, t6, t5  # [op1561] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t6, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, t6, t4  # [op1562] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t4, t5, t4  # [op1563] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw t4, t4, 0  # [op1564] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t5, 8  # [op1565] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t5, t5, e32, m1, ta,ma  # [op1566] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, t4  # [op1567] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v1, v5  # [op1568] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1569] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t4, t4, a6  # [op1570] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s6, s6, a3  # [op1571] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t4, s6  # [op1572] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t4, t2, a4  # [op1573] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s6, t4  # [op1574] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t4, 8  # [op1575] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t4, t4, e16, m1, ta,ma  # [op1576] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(s6), v0.t  # [op1577] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmerge.vvm v5, v3, v5, v0  # [op1578] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 96  # [op1579] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 168(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t4, s6  # [op1580] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t4, 8  # [op1581] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(s6)  # [op1583] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 7  # [op1584] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t0, s6  # [op1585] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt a5, s6, a5  # [op1586] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t4, t4, s1  # [op1587] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t5, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, t5, t4  # [op1588] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t5, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub s1, s1, t5  # [op1589] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and s1, s1, t4  # [op1590] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s1, t4, s1  # [op1591] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t4, 0  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub a5, t4, a5  # [op1592] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and s1, s1, a5  # [op1593] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw s1, s1, 0  # [op1594] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a5, 8  # [op1595] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli a5, a5, e32, m1, ta,ma  # [op1596] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, s1  # [op1597] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v1, v5  # [op1598] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1599] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld s1, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s1, s1, a6  # [op1600] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul a3, s6, a3  # [op1601] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s1, s1, a3  # [op1602] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul a3, t2, a4  # [op1603] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s1, s1, a3  # [op1604] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a3, 8  # [op1605] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli a3, a3, e16, m1, ta,ma  # [op1606] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(s1), v0.t  # [op1607] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmerge.vvm v5, v3, v5, v0  # [op1608] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s1, 112  # [op1609] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a3, 168(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s1, a3, s1  # [op1610] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a3, 8  # [op1611] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(s1)  # [op1613] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Ltaf15.join  # [op1614] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Ltaf15.join:  # block taf15.join
li s1, 8  # [op1615] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a3, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a3, a3, s1  # [op1616] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a4, 257  # [op1617] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt a3, a3, a4  # [op1618] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a4, 1  # [op1619] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a5, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a4, a5, a4  # [op1620] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt s1, s1, a4  # [op1621] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and s1, a3, s1  # [op1622] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
bne s1, zero, .Lbrc1623_true  # [op1623] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lpbf16.else  # [op1623] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lbrc1623_true:  # [op1623] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lpbf16.then  # [op1623] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lpbf16.then:  # block pbf16.then
li s1, 8  # [op1624] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli s1, s1, e16, m1, ta,ma  # [op1625] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s1, 512  # [op1626] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a3, 111744  # [op1627] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a4, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a3, a4, a3  # [op1628] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul a4, t2, s1  # [op1629] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a4, a3, a4  # [op1630] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a3, 2  # [op1631] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a5, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul a5, a5, a3  # [op1632] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a4, a4, a5  # [op1633] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vlse16.v v5, 0(a4), s1  # [op1634] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a1)  # [op1635] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a5, a4, a3  # [op1636] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a4, 16  # [op1637] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a6, a1, a4  # [op1638] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vlse16.v v5, 0(a5), s1  # [op1639] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a6)  # [op1640] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a5, a5, a3  # [op1641] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a6, a6, a4  # [op1642] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vlse16.v v5, 0(a5), s1  # [op1643] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a6)  # [op1644] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a5, a5, a3  # [op1645] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a6, a6, a4  # [op1646] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vlse16.v v5, 0(a5), s1  # [op1647] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a6)  # [op1648] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a5, a5, a3  # [op1649] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a6, a6, a4  # [op1650] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vlse16.v v5, 0(a5), s1  # [op1651] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a6)  # [op1652] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a5, a5, a3  # [op1653] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a6, a6, a4  # [op1654] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vlse16.v v5, 0(a5), s1  # [op1655] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a6)  # [op1656] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a5, a5, a3  # [op1657] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a6, a6, a4  # [op1658] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vlse16.v v5, 0(a5), s1  # [op1659] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a6)  # [op1660] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a3, a5, a3  # [op1661] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a4, a6, a4  # [op1662] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vlse16.v v5, 0(a3), s1  # [op1663] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a4)  # [op1664] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lpbf16.join  # [op1665] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lpbf16.else:  # block pbf16.else
li s1, 8  # [op1666] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli s1, s1, e16, m1, ta,ma  # [op1667] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s1, 0  # [op1668] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a3, a1, s1  # [op1669] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v4, 0(a3)  # [op1670] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a3, 16  # [op1671] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a3, a1, a3  # [op1672] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v4, 0(a3)  # [op1673] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a3, 32  # [op1674] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a3, a1, a3  # [op1675] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v4, 0(a3)  # [op1676] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a3, 48  # [op1677] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a3, a1, a3  # [op1678] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v4, 0(a3)  # [op1679] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a3, 64  # [op1680] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a3, a1, a3  # [op1681] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v4, 0(a3)  # [op1682] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a3, 80  # [op1683] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a3, a1, a3  # [op1684] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v4, 0(a3)  # [op1685] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a3, 96  # [op1686] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a3, a1, a3  # [op1687] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v4, 0(a3)  # [op1688] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a3, 112  # [op1689] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a3, a1, a3  # [op1690] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v4, 0(a3)  # [op1691] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a6, 8  # [op1692] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lpb17.head  # [op1693] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lpb17.head:  # block pb17.head
slt a3, s1, a6  # [op1694] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
bne a3, zero, .Lbrc1695_true  # [op1695] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lpb17.exit  # [op1695] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lbrc1695_true:  # [op1695] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lpb17.body  # [op1695] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lpb17.body:  # block pb17.body
ld a3, 184(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a3, a3, s1  # [op1696] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a4, 256  # [op1697] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt s6, a3, a4  # [op1698] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a4, 8  # [op1699] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a5, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t4, a5, a4  # [op1700] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a5, 0  # [op1701] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, a5, t4  # [op1702] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t5, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub a4, a4, t5  # [op1703] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and a4, a4, t4  # [op1704] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 176(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a4, t4, a4  # [op1705] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub a5, a5, s6  # [op1706] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and a5, a4, a5  # [op1707] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a4, 111744  # [op1708] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld s6, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s6, a4  # [op1709] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a4, 512  # [op1710] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t4, t2, a4  # [op1711] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s6, t4  # [op1712] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t4, 2  # [op1713] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul a3, a3, t4  # [op1714] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a3, s6, a3  # [op1715] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 16  # [op1716] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s6, s1, s6  # [op1717] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, a1, s6  # [op1718] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw a5, a5, 0  # [op1719] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli a5, a5, e16, m1, ta,ma  # [op1720] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vlse16.v v5, 0(a3), a4  # [op1721] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(s6)  # [op1722] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a3, 1  # [op1723] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s1, s1, a3  # [op1724] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lpb17.head  # [op1725] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lpb17.exit:  # block pb17.exit
j .Lpbf16.join  # [op1726] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lpbf16.join:  # block pbf16.join
li s1, 64  # [op1727] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli s1, s1, e16, m1, ta,ma  # [op1728] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld s1, 168(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(s1)  # [op1729] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v8, 0(a1)  # [op1730] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli x0, zero, e16, m1, ta, ma
    smt.vfwmadot v6, v5, v8  # [op1731] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s1, 8  # [op1732] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t2, t2, s1  # [op1733] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lmk14.head  # [op1734] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lchunk18_head:  # block chunk18_head
li s1, 32768  # [op1735] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
slt s1, t0, s1  # [op1736] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
bne s1, zero, .Lbrc1737_true  # [op1737] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op1737] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op1737] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk18_exit  # [op1737] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lbrc1737_true:  # [op1737] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk18_body  # [op1737] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk18_exit:  # block chunk18_exit
li t2, 0  # [op1738] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd t0, 96(sp)  # [op1739] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op1739] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 96(sp)  # [op1739] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk19_head  # [op1739] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk18_body:  # block chunk18_body
li s1, 32  # [op1740] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli s1, s1, e32, m1, ta,ma  # [op1741] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li s1, 32  # [op1742] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vid.v v1  # [op1744] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vadd.vx v1, v1, t0  # [op1745] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
    # [peephole-li] [op1746] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vwadd.vx v2, v1, x0  # [op1748] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
    # [peephole-li] [op1749] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vsetvli s1, s1, e64, m2, ta,ma  # [op1750] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
li s1, 4  # [op1751] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vmul.vx v2, v2, s1  # [op1752] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
li s1, 128128  # [op1753] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
ld a1, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
add s1, a1, s1  # [op1754] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
li a1, 32  # [op1755] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vsetvli a1, a1, e32, m1, ta,ma  # [op1756] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vluxei64.v v1, (s1), v2  # [op1757] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
li s1, 32  # [op1758] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vid.v v2  # [op1760] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vadd.vx v2, v2, t0  # [op1761] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
    # [peephole-li] [op1762] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vwadd.vx v4, v2, x0  # [op1764] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
    # [peephole-li] [op1765] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vsetvli s1, s1, e64, m2, ta,ma  # [op1766] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
li s1, 4  # [op1767] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vmul.vx v2, v4, s1  # [op1768] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
li s1, 259200  # [op1769] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
ld a1, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
add s1, a1, s1  # [op1770] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
li a1, 32  # [op1771] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vsetvli a1, a1, e32, m1, ta,ma  # [op1772] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vluxei64.v v4, (s1), v2  # [op1773] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
li s1, 32  # [op1774] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vfadd.vv v1, v1, v4  # [op1776] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vid.v v2  # [op1777] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vadd.vx v2, v2, t0  # [op1778] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
    # [peephole-li] [op1779] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vwadd.vx v4, v2, x0  # [op1781] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
    # [peephole-li] [op1782] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vsetvli s1, s1, e64, m2, ta,ma  # [op1783] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
li s1, 4  # [op1784] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vmul.vx v2, v4, s1  # [op1785] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
li s1, 390272  # [op1786] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
ld a1, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
add s1, a1, s1  # [op1787] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
li a1, 32  # [op1788] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vsetvli a1, a1, e32, m1, ta,ma  # [op1789] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vsuxei64.v v1, (s1), v2  # [op1790] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
li s1, 32  # [op1791] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
    # [peephole-li] [op1793] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add t2, t2, s1  # [op1794] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-li] [op1795] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t0, s1  # [op1796] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-li] [op1797] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk18_head  # [op1799] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk19_head:  # block chunk19_head
li s1, 128  # [op1800] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
slt s1, t0, s1  # [op1801] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
bne s1, zero, .Lbrc1802_true  # [op1802] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op1802] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op1802] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk19_exit  # [op1802] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lbrc1802_true:  # [op1802] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk19_body  # [op1802] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk19_exit:  # block chunk19_exit
li t2, 0  # [op1803] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv s1, t0  # [op1804] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk20_head  # [op1804] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk19_body:  # block chunk19_body
li s1, 32  # [op1805] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli s1, s1, e32, m1, ta,ma  # [op1806] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li s1, 32  # [op1807] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
ld s1, 144(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vmv.v.x v1, s1  # [op1809] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vid.v v2  # [op1810] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vadd.vx v2, v2, t0  # [op1811] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
li s1, 32  # [op1812] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vwadd.vx v4, v2, x0  # [op1814] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
    # [peephole-li] [op1815] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vsetvli s1, s1, e64, m2, ta,ma  # [op1816] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
li s1, 4  # [op1817] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vmul.vx v2, v4, s1  # [op1818] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
li s1, 0  # [op1819] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
ld a1, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
add s1, a1, s1  # [op1820] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
li a1, 32  # [op1821] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vsetvli a1, a1, e32, m1, ta,ma  # [op1822] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vluxei64.v v4, (s1), v2  # [op1823] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
li s1, 32  # [op1824] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vmul.vv v1, v4, v1  # [op1826] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vid.v v2  # [op1827] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vadd.vx v2, v2, t0  # [op1828] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
    # [peephole-li] [op1829] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vwadd.vx v4, v2, x0  # [op1831] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
    # [peephole-li] [op1832] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vsetvli s1, s1, e64, m2, ta,ma  # [op1833] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
li s1, 4  # [op1834] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vmul.vx v2, v4, s1  # [op1835] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
li s1, 521344  # [op1836] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
ld a1, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
add s1, a1, s1  # [op1837] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
li a1, 32  # [op1838] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vsetvli a1, a1, e32, m1, ta,ma  # [op1839] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vsuxei64.v v1, (s1), v2  # [op1840] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
li s1, 32  # [op1841] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
    # [peephole-li] [op1843] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add t2, t2, s1  # [op1844] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-li] [op1845] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t0, s1  # [op1846] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-li] [op1847] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk19_head  # [op1849] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk20_head:  # block chunk20_head
li t0, 32768  # [op1850] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
slt t0, t2, t0  # [op1851] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
bne t0, zero, .Lbrc1852_true  # [op1852] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op1852] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, s1  # [op1852] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk20_exit  # [op1852] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lbrc1852_true:  # [op1852] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk20_body  # [op1852] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk20_exit:  # block chunk20_exit
sd t0, 96(sp)  # [op1853] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t1  # [op1853] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t1, 96(sp)  # [op1853] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lprog_next  # [op1853] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk20_body:  # block chunk20_body
li t0, 32  # [op1854] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli t0, t0, e16, m1, ta,ma  # [op1855] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t0, 32  # [op1856] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
vsetvli t0, t0, e32, m1, ta,ma  # [op1857] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
vid.v v1  # [op1858] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
vadd.vx v1, v1, t2  # [op1859] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
li t0, 256  # [op1860] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
vmv.v.x v2, t0  # [op1861] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
vdiv.vv v1, v1, v2  # [op1862] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
li t0, 32  # [op1863] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
vwadd.vx v2, v1, x0  # [op1865] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
    # [peephole-li] [op1866] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
vsetvli t0, t0, e64, m2, ta,ma  # [op1867] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
li t0, 8  # [op1868] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
vmul.vx v2, v2, t0  # [op1869] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
li t0, 521856  # [op1870] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
ld a1, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
add t0, a1, t0  # [op1871] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
li a1, 32  # [op1872] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
vluxei64.v v4, (t0), v2  # [op1874] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
li t0, 32  # [op1875] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
vsetvli t0, t0, e16, m1, ta,ma  # [op1876] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
li t0, 32  # [op1877] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli t0, t0, e32, m1, ta,ma  # [op1878] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vid.v v1  # [op1879] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vadd.vx v1, v1, t2  # [op1880] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 32  # [op1881] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vwadd.vx v2, v1, x0  # [op1883] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
    # [peephole-li] [op1884] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli t0, t0, e64, m2, ta,ma  # [op1885] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 4  # [op1886] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmul.vx v2, v2, t0  # [op1887] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 390272  # [op1888] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
ld a1, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add t0, a1, t0  # [op1889] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a1, 32  # [op1890] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli a1, a1, e32, m1, ta,ma  # [op1891] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vluxei64.v v1, (t0), v2  # [op1892] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 32  # [op1893] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli t0, t0, e16, m1, ta,ma  # [op1894] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 32  # [op1895] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli t0, t0, e32, m1, ta,ma  # [op1896] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.v.v v2, v1  # [op1897] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 32  # [op1898] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli t0, t0, e16, m1, ta,ma  # [op1899] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vfncvt.f.f.w v1, v2  # [op1900] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 32  # [op1901] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli t0, t0, e32, m1, ta,ma  # [op1902] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vid.v v2  # [op1903] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vadd.vx v2, v2, t2  # [op1904] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 256  # [op1905] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.v.x v3, t0  # [op1906] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vdiv.vv v2, v2, v3  # [op1907] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 32  # [op1908] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vwadd.vx v4, v2, x0  # [op1910] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
    # [peephole-li] [op1911] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli t0, t0, e64, m2, ta,ma  # [op1912] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 4  # [op1913] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmul.vx v2, v4, t0  # [op1914] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 521344  # [op1915] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
ld a1, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add t0, a1, t0  # [op1916] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a1, 32  # [op1917] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli a1, a1, e32, m1, ta,ma  # [op1918] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vluxei64.v v4, (t0), v2  # [op1919] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 32  # [op1920] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli t0, t0, e16, m1, ta,ma  # [op1921] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 32  # [op1922] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli t0, t0, e32, m1, ta,ma  # [op1923] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vid.v v2  # [op1924] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vadd.vx v2, v2, t2  # [op1925] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 256  # [op1926] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.v.x v3, t0  # [op1927] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vrem.vv v2, v2, v3  # [op1928] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 32  # [op1929] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vwadd.vx v6, v2, x0  # [op1931] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
    # [peephole-li] [op1932] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli t0, t0, e64, m2, ta,ma  # [op1933] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 4  # [op1934] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmul.vx v2, v6, t0  # [op1935] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 512  # [op1936] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
ld a1, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add t0, a1, t0  # [op1937] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a1, 32  # [op1938] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli a1, a1, e32, m1, ta,ma  # [op1939] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vluxei64.v v5, (t0), v2  # [op1940] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 32  # [op1941] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli t0, t0, e16, m1, ta,ma  # [op1942] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 32  # [op1943] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli t0, t0, e32, m1, ta,ma  # [op1944] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vadd.vv v4, v4, v5  # [op1945] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 32  # [op1946] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli t0, t0, e16, m1, ta,ma  # [op1947] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 32  # [op1948] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli t0, t0, e32, m1, ta,ma  # [op1949] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vwadd.vx v2, v4, x0  # [op1950] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 32  # [op1951] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli t0, t0, e64, m2, ta,ma  # [op1952] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 2  # [op1953] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmul.vx v2, v2, t0  # [op1954] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 32  # [op1955] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli t0, t0, e16, m1, ta,ma  # [op1956] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a1, 0  # [op1957] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 16  # [op1958] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli t0, t0, e64, m2, ta,ma  # [op1959] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s t0, v2  # [op1960] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vid.v v6  # [op1961] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 2  # [op1962] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmul.vx v6, v6, a2  # [op1963] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vadd.vx v6, v6, t0  # [op1964] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmsne.vv v5, v2, v6  # [op1965] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vcpop.m a2, v5  # [op1966] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a1, a1, a2  # [op1967] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, s4, t0  # [op1968] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vid.v v6  # [op1969] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 16  # [op1970] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vadd.vx v8, v6, t0  # [op1971] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vrgather.vv v6, v2, v8  # [op1972] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s t0, v6  # [op1973] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vid.v v2  # [op1974] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a3, 2  # [op1975] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmul.vx v2, v2, a3  # [op1976] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vadd.vx v2, v2, t0  # [op1977] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmsne.vv v2, v6, v2  # [op1978] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vcpop.m a3, v2  # [op1979] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a1, a1, a3  # [op1980] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add t0, s4, t0  # [op1981] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
bne a1, zero, .Lbrc1982_true  # [op1982] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
j .Lngs.t3  # [op1982] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
.Lbrc1982_true:  # [op1982] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
j .Lngs.e3  # [op1982] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
.Lngs.t3:  # block ngs.t3
li a1, 16  # [op1983] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli a1, a1, e16, m1, ta,ma  # [op1984] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vse16.v v1, 0(a2)  # [op1985] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vid.v v2  # [op1986] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a1, 16  # [op1987] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vadd.vx v2, v2, a1  # [op1988] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vrgather.vv v3, v1, v2  # [op1989] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vse16.v v3, 0(t0)  # [op1990] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
j .Lngs.j3  # [op1991] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
.Lngs.e3:  # block ngs.e3
li t0, 32  # [op1992] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli t0, t0, e32, m1, ta,ma  # [op1993] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vwadd.vx v2, v4, x0  # [op1994] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 32  # [op1995] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli t0, t0, e64, m2, ta,ma  # [op1996] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 2  # [op1997] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmul.vx v2, v2, t0  # [op1998] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 32  # [op1999] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli t0, t0, e16, m1, ta,ma  # [op2000] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 523392  # [op2001] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
ld a1, 160(sp)  # [op-1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add t0, a1, t0  # [op2002] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a1, 128  # [op2003] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a1, t0, a1  # [op2004] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a1, 32  # [op2005] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vse16.v v1, 0(t0)  # [op2007] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
    # [peephole-li] [op2008] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli a1, a1, e64, m2, ta,ma  # [op2009] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vadd.vx v2, v2, s4  # [op2010] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s a1, v2  # [op2011] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 0  # [op2012] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op2013] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op2014] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(a1)  # [op2015] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op2016] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s a1, v2  # [op2017] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 2  # [op2018] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op2019] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op2020] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(a1)  # [op2021] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op2022] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s a1, v2  # [op2023] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 4  # [op2024] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op2025] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op2026] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(a1)  # [op2027] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op2028] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s a1, v2  # [op2029] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 6  # [op2030] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op2031] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op2032] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(a1)  # [op2033] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op2034] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s a1, v2  # [op2035] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 8  # [op2036] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op2037] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op2038] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(a1)  # [op2039] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op2040] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s a1, v2  # [op2041] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 10  # [op2042] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op2043] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op2044] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(a1)  # [op2045] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op2046] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s a1, v2  # [op2047] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 12  # [op2048] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op2049] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op2050] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(a1)  # [op2051] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op2052] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s a1, v2  # [op2053] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 14  # [op2054] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op2055] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op2056] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(a1)  # [op2057] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op2058] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s a1, v2  # [op2059] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 16  # [op2060] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op2061] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op2062] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(a1)  # [op2063] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op2064] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s a1, v2  # [op2065] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 18  # [op2066] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op2067] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op2068] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(a1)  # [op2069] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op2070] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s a1, v2  # [op2071] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 20  # [op2072] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op2073] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op2074] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(a1)  # [op2075] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op2076] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s a1, v2  # [op2077] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 22  # [op2078] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op2079] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op2080] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(a1)  # [op2081] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op2082] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s a1, v2  # [op2083] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 24  # [op2084] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op2085] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op2086] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(a1)  # [op2087] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op2088] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s a1, v2  # [op2089] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 26  # [op2090] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op2091] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op2092] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(a1)  # [op2093] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op2094] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s a1, v2  # [op2095] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 28  # [op2096] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op2097] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op2098] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(a1)  # [op2099] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op2100] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s a1, v2  # [op2101] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 30  # [op2102] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op2103] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op2104] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(a1)  # [op2105] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op2106] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s a1, v2  # [op2107] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 32  # [op2108] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op2109] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op2110] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(a1)  # [op2111] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op2112] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s a1, v2  # [op2113] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 34  # [op2114] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op2115] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op2116] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(a1)  # [op2117] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op2118] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s a1, v2  # [op2119] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 36  # [op2120] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op2121] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op2122] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(a1)  # [op2123] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op2124] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s a1, v2  # [op2125] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 38  # [op2126] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op2127] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op2128] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(a1)  # [op2129] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op2130] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s a1, v2  # [op2131] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 40  # [op2132] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op2133] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op2134] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(a1)  # [op2135] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op2136] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s a1, v2  # [op2137] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 42  # [op2138] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op2139] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op2140] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(a1)  # [op2141] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op2142] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s a1, v2  # [op2143] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 44  # [op2144] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op2145] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op2146] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(a1)  # [op2147] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op2148] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s a1, v2  # [op2149] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 46  # [op2150] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op2151] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op2152] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(a1)  # [op2153] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op2154] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s a1, v2  # [op2155] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 48  # [op2156] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op2157] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op2158] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(a1)  # [op2159] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op2160] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s a1, v2  # [op2161] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 50  # [op2162] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op2163] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op2164] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(a1)  # [op2165] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op2166] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s a1, v2  # [op2167] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 52  # [op2168] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op2169] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op2170] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(a1)  # [op2171] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op2172] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s a1, v2  # [op2173] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 54  # [op2174] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op2175] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op2176] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(a1)  # [op2177] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op2178] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s a1, v2  # [op2179] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 56  # [op2180] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op2181] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op2182] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(a1)  # [op2183] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op2184] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s a1, v2  # [op2185] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 58  # [op2186] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op2187] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op2188] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(a1)  # [op2189] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op2190] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s a1, v2  # [op2191] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 60  # [op2192] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op2193] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op2194] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(a1)  # [op2195] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op2196] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s a1, v2  # [op2197] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 62  # [op2198] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add t0, t0, a2  # [op2199] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu t0, 0(t0)  # [op2200] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh t0, 0(a1)  # [op2201] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op2202] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
j .Lngs.j3  # [op2203] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
.Lngs.j3:  # block ngs.j3
li t0, 32  # [op2204] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli t0, t0, e16, m1, ta,ma  # [op2205] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 32  # [op2206] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add t0, s1, t0  # [op2207] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li s1, 32  # [op2208] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t2, t2, s1  # [op2209] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-li] [op2210] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv s1, t0  # [op2212] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk20_head  # [op2212] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lprog_next:  # block prog_next
add t0, t0, s10  # [op2213] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lprog_head  # [op2214] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lprog_exit:  # block prog_exit
sd t0, 0(s7)  # [op2215] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld ra, 0(sp)  # [op2216] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 8(sp)  # [op2216] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s2, 16(sp)  # [op2216] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s3, 24(sp)  # [op2216] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s4, 32(sp)  # [op2216] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s5, 40(sp)  # [op2216] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s6, 48(sp)  # [op2216] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s7, 56(sp)  # [op2216] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s8, 64(sp)  # [op2216] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s9, 72(sp)  # [op2216] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s10, 80(sp)  # [op2216] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s11, 88(sp)  # [op2216] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addi sp, sp, 192  # [op2216] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ret  # [op2216] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    .size operator_entry, .-operator_entry
    .section .note.GNU-stack,"",@progbits
