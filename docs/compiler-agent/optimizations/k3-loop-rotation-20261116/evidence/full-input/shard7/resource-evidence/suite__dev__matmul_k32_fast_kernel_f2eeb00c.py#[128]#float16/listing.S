# a100c emitted program: matmul_k32_fast_kernel
# source: home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py
# specialization identity: 5b9701b642fc9e77
# compiler revision: 359f81c6f5000d1f
# target model: a100-rvv1-vlen1024/1 (VLEN=1024, file=4096B)
# options: no-chunk-mask-split,no-loop-const-hoist,no-mir-loop-predicate
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
    # [peephole] removed 28 redundant vsetvli, 29 redundant li, 27 dead-vl setters to x0-dst
    # [peephole-branch] removed 22 bare-stub jumps, fused 19 compare+branch pairs (declined: 1 stubs, 0 compares)
operator_entry:  # fn operator_entry
addi sp, sp, -224
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
sd t0, 112(sp)  # [op0]
ld t0, 112(sp)  # [op1] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t1, 0(t0)  # [op2] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t1, 0(t1)  # [op3] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd t1, 120(sp)  # [op4] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s7, 24(t0)  # [op5] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
lwu t1, 40(t0)  # [op6] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
lwu t2, 44(t0)  # [op7] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 0(t0)  # [op8] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 8(s1)  # [op9] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 8(s1)  # [op10] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw s1, s1, 0  # [op11] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 0(t0)  # [op12] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 8(s1)  # [op13] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 24(s1)  # [op14] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd s1, 128(sp)  # [op15] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 128(sp)  # [op16] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw s1, s1, 0  # [op17] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 0(t0)  # [op18] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 8(s1)  # [op19] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 40(s1)  # [op20] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw s1, s1, 0  # [op21] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 0(t0)  # [op22] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 8(s1)  # [op23] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 56(s1)  # [op24] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw s1, s1, 0  # [op25] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 0(t0)  # [op26] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 8(s1)  # [op27] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 72(s1)  # [op28] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw s8, s1, 0  # [op29] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 0(t0)  # [op30] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 8(s1)  # [op31] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 88(s1)  # [op32] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw s1, s1, 0  # [op33] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd s1, 136(sp)  # [op34] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 0(t0)  # [op35] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 8(s1)  # [op36] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 104(s1)  # [op37] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw s1, s1, 0  # [op38] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 0(t0)  # [op39] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 8(s1)  # [op40] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 120(s1)  # [op41] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw s1, s1, 0  # [op42] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd s1, 144(sp)  # [op43] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t0, 0(t0)  # [op44] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t0, 8(t0)  # [op45] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t0, 136(t0)  # [op46] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw t0, t0, 0  # [op47] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t0, 120(sp)  # [op48] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t0, 0(t0)  # [op49] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd t0, 152(sp)  # [op50] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t0, 120(sp)  # [op51] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t0, 56(t0)  # [op52] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd t0, 176(sp)  # [op53] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t0, 120(sp)  # [op54] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s4, 112(t0)  # [op55] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t0, 128  # [op56] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 128(sp)  # [op57] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
divu t0, s1, t0  # [op58] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd t0, 160(sp)  # [op59] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t0, 1  # [op60] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 160(sp)  # [op61] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mul t0, t0, s1  # [op62] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li s1, 2  # [op63] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mul s9, t0, s1  # [op64] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t1  # [op65] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv s10, t2  # [op66] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t1, 0  # [op67] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lprog_head  # [op68] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lprog_head:  # block prog_head
    # [peephole-cmpfuse] slt t2, t0, s9 removed (fused into the branch)
blt t0, s9, .Lbrc70_true  # [op70] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd t1, 96(sp)  # [op70] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t1, t0  # [op70] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t0, 96(sp)  # [op70] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lprog_exit  # [op70] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lbrc70_true:  # [op70] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv a1, t1  # [op70] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t1, t0  # [op70] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lprog_body  # [op70] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lprog_body:  # block prog_body
li t2, 1  # [op71] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t0, 160(sp)  # [op72] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
divu s1, t1, t0  # [op73] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mul s1, s1, t0  # [op74] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sub a2, t1, s1  # [op75] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mul t2, t2, t0  # [op76] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
divu s1, t1, t2  # [op77] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li a3, 2  # [op78] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
divu a3, s1, a3  # [op79] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li a4, 2  # [op80] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mul a3, a3, a4  # [op81] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sub s1, s1, a3  # [op82] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li a3, 2  # [op83] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mul t2, t2, a3  # [op84] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw t2, a2, 0  # [op85] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw a2, s1, 0  # [op86] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw t0, t0, 0  # [op87] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t0, 2  # [op88] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw t0, t0, 0  # [op89] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t0, 112(sp)  # [op90] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 16(t0)  # [op91] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd s1, 168(sp)  # [op92] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t0, 8(t0)  # [op93] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t0, 7  # [op94] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
sllw a3, t2, t0  # [op95] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
li t0, 0  # [op96] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv s1, a1  # [op97] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk1_head  # [op97] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk1_head:  # block chunk1_head
li t2, 128  # [op98] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-cmpfuse] slt t2, t0, t2 removed (fused into the branch)
blt t0, t2, .Lchunk1_body  # [op100] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op100] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, s1  # [op100] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk1_exit  # [op100] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-stub] bare trampoline .Lbrc100_true -> .Lchunk1_body removed
    # [peephole-stub] removed: j .Lchunk1_body
.Lchunk1_exit:  # block chunk1_exit
li t2, 523528  # [op101] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 168(sp)  # [op102] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add t2, s1, t2  # [op103] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
lw a1, 0(t2)  # [op104] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t2, 0  # [op105] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv s1, t0  # [op106] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op106] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk2_head  # [op106] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk1_body:  # block chunk1_body
    # [peephole-dead-li2] [op107] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli t2, x0, e32, m1, ta,ma  # [op108] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t2, 32  # [op109] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:32
vid.v v1  # [op111] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:32
vadd.vx v1, v1, t0  # [op112] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:32
vmv.v.x v2, a3  # [op113] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
vadd.vv v1, v2, v1  # [op114] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
vsetvli a1, x0, e64, m2, ta,ma  # [op115] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
vid.v v2  # [op116] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
vadd.vx v2, v2, t0  # [op117] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
li a1, 4  # [op118] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
vmul.vx v2, v2, a1  # [op119] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
li a4, 0  # [op120] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
ld a1, 168(sp)  # [op121] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
add a4, a1, a4  # [op122] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
vsetvli a5, x0, e32, m1, ta,ma  # [op123] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
vsuxei64.v v1, (a4), v2  # [op124] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
li a4, 8  # [op125] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
sllw a4, a2, a4  # [op126] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
li a5, 32  # [op127] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add s1, s1, a5  # [op128] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t0, t2  # [op129] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t2, 523528  # [op130] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add t2, a1, t2  # [op131] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sw a4, 0(t2)  # [op132] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk1_head  # [op133] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk2_head:  # block chunk2_head
li t2, 256  # [op134] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-cmpfuse] slt t2, t0, t2 removed (fused into the branch)
blt t0, t2, .Lchunk2_body  # [op136] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op136] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, s1  # [op136] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk2_exit  # [op136] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-stub] bare trampoline .Lbrc136_true -> .Lchunk2_body removed
    # [peephole-stub] removed: j .Lchunk2_body
.Lchunk2_exit:  # block chunk2_exit
li t2, 0  # [op137] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv s1, t0  # [op138] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op138] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk3_head  # [op138] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk2_body:  # block chunk2_body
    # [peephole-dead-li2] [op139] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli t2, x0, e32, m1, ta,ma  # [op140] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t2, 32  # [op141] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:32
vid.v v1  # [op143] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:32
vadd.vx v1, v1, t0  # [op144] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:32
vmv.v.x v2, a1  # [op145] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
vadd.vv v1, v2, v1  # [op146] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
vsetvli a2, x0, e64, m2, ta,ma  # [op147] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
vid.v v2  # [op148] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
vadd.vx v2, v2, t0  # [op149] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
li a2, 4  # [op150] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
vmul.vx v2, v2, a2  # [op151] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
li a2, 512  # [op152] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
ld a3, 168(sp)  # [op153] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
add a2, a3, a2  # [op154] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
vsetvli a3, x0, e32, m1, ta,ma  # [op155] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
vsuxei64.v v1, (a2), v2  # [op156] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
li a2, 32  # [op157] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add s1, s1, a2  # [op158] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t0, t2  # [op159] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk2_head  # [op160] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk3_head:  # block chunk3_head
li t2, 32  # [op161] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-cmpfuse] slt t2, t0, t2 removed (fused into the branch)
blt t0, t2, .Lchunk3_body  # [op163] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op163] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, s1  # [op163] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk3_exit  # [op163] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-stub] bare trampoline .Lbrc163_true -> .Lchunk3_body removed
    # [peephole-stub] removed: j .Lchunk3_body
.Lchunk3_exit:  # block chunk3_exit
li t2, 0  # [op164] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv s1, t0  # [op165] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk4_head  # [op165] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk3_body:  # block chunk3_body
    # [peephole-dead-li2] [op166] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli t2, x0, e32, m1, ta,ma  # [op167] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t2, 32  # [op168] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
vid.v v1  # [op170] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
vadd.vx v1, v1, t0  # [op171] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
vsetvli a1, x0, e64, m2, ta,ma  # [op172] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
vid.v v2  # [op173] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
vadd.vx v2, v2, t0  # [op174] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
li a1, 4  # [op175] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
vmul.vx v2, v2, a1  # [op176] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
li a1, 1536  # [op177] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
ld a2, 168(sp)  # [op178] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
add a1, a2, a1  # [op179] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
vsetvli a2, x0, e32, m1, ta,ma  # [op180] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
vsuxei64.v v1, (a1), v2  # [op181] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
li a1, 32  # [op182] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add s1, s1, a1  # [op183] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t0, t2  # [op184] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk3_head  # [op185] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk4_head:  # block chunk4_head
li t0, 128  # [op186] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-cmpfuse] slt t0, t2, t0 removed (fused into the branch)
blt t2, t0, .Lchunk4_body  # [op188] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op188] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, s1  # [op188] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk4_exit  # [op188] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-stub] bare trampoline .Lbrc188_true -> .Lchunk4_body removed
    # [peephole-stub] removed: j .Lchunk4_body
.Lchunk4_exit:  # block chunk4_exit
li t2, 0  # [op189] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd t0, 96(sp)  # [op190] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op190] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 96(sp)  # [op190] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk5_head  # [op190] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk4_body:  # block chunk4_body
    # [peephole-dead-li2] [op191] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli t0, x0, e32, m1, ta,ma  # [op192] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t0, 32  # [op193] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vmv.v.x v1, s8  # [op195] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vsetvli a1, x0, e64, m2, ta,ma  # [op196] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vid.v v2  # [op197] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vadd.vx v2, v2, t2  # [op198] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
li a1, 4  # [op199] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vmul.vx v2, v2, a1  # [op200] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
li a2, 0  # [op201] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
ld a1, 168(sp)  # [op202] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
add a2, a1, a2  # [op203] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vsetvli a3, x0, e32, m1, ta,ma  # [op204] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vluxei64.v v4, (a2), v2  # [op205] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vmul.vv v1, v4, v1  # [op206] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
    # [peephole-superseded-vsetvli] [op207] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
li a2, 2176  # [op208] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
add a1, a1, a2  # [op209] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vsetvli a2, x0, e32, m1, ta,ma  # [op210] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vsuxei64.v v1, (a1), v2  # [op211] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
li a1, 32  # [op212] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add s1, s1, a1  # [op213] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t2, t0  # [op214] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t0  # [op215] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk4_head  # [op215] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk5_head:  # block chunk5_head
li s1, 32  # [op216] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-cmpfuse] slt s1, t0, s1 removed (fused into the branch)
blt t0, s1, .Lchunk5_body  # [op218] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op218] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op218] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk5_exit  # [op218] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-stub] bare trampoline .Lbrc218_true -> .Lchunk5_body removed
    # [peephole-stub] removed: j .Lchunk5_body
.Lchunk5_exit:  # block chunk5_exit
li t2, 0  # [op219] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd t0, 96(sp)  # [op220] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op220] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 96(sp)  # [op220] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk6_head  # [op220] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk5_body:  # block chunk5_body
    # [peephole-dead-li2] [op221] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli s1, x0, e32, m1, ta,ma  # [op222] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li s1, 32  # [op223] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add s1, t2, s1  # [op224] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t2, 32  # [op225] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t0, t2  # [op226] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, s1  # [op228] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk5_head  # [op228] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk6_head:  # block chunk6_head
li s1, 4096  # [op229] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-cmpfuse] slt s1, t0, s1 removed (fused into the branch)
blt t0, s1, .Lchunk6_body  # [op231] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op231] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op231] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk6_exit  # [op231] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-stub] bare trampoline .Lbrc231_true -> .Lchunk6_body removed
    # [peephole-stub] removed: j .Lchunk6_body
.Lchunk6_exit:  # block chunk6_exit
li t2, 0  # [op232] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv s1, t0  # [op233] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk7_head  # [op233] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk6_body:  # block chunk6_body
    # [peephole-dead-li2] [op234] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-superseded-vsetvli] [op235] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li s1, 32  # [op236] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
vsetvli a1, x0, e64, m2, ta,ma  # [op237] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
vid.v v2  # [op238] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
vadd.vx v2, v2, t0  # [op239] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
li a1, 32  # [op240] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
vmv.v.x v4, a1  # [op241] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
vdiv.vv v2, v2, v4  # [op242] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
li a2, 8  # [op243] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
vmul.vx v2, v2, a2  # [op244] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
li a2, 2688  # [op245] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
ld a3, 168(sp)  # [op246] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
add a2, a3, a2  # [op247] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
vluxei64.v v4, (a2), v2  # [op248] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
vsetvli a2, x0, e32, m1, ta,ma  # [op249] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
add t2, t2, a1  # [op250] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t0, s1  # [op251] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk6_head  # [op252] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk7_head:  # block chunk7_head
li t0, 32  # [op253] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-cmpfuse] slt t0, t2, t0 removed (fused into the branch)
blt t2, t0, .Lchunk7_body  # [op255] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op255] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, s1  # [op255] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk7_exit  # [op255] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-stub] bare trampoline .Lbrc255_true -> .Lchunk7_body removed
    # [peephole-stub] removed: j .Lchunk7_body
.Lchunk7_exit:  # block chunk7_exit
li t2, 0  # [op256] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd t0, 96(sp)  # [op257] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op257] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 96(sp)  # [op257] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk8_head  # [op257] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk7_body:  # block chunk7_body
    # [peephole-dead-li2] [op258] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli t0, x0, e32, m1, ta,ma  # [op259] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t0, 32  # [op260] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
ld a1, 136(sp)  # [op262] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vmv.v.x v1, a1  # [op263] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vsetvli a1, x0, e64, m2, ta,ma  # [op264] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vid.v v2  # [op265] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vadd.vx v2, v2, t2  # [op266] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
li a1, 4  # [op267] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vmul.vx v2, v2, a1  # [op268] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
li a2, 1536  # [op269] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
ld a1, 168(sp)  # [op270] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
add a2, a1, a2  # [op271] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vsetvli a3, x0, e32, m1, ta,ma  # [op272] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vluxei64.v v4, (a2), v2  # [op273] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vmul.vv v1, v4, v1  # [op274] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
    # [peephole-superseded-vsetvli] [op275] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
li a2, 36608  # [op276] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
add a1, a1, a2  # [op277] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vsetvli a2, x0, e32, m1, ta,ma  # [op278] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vsuxei64.v v1, (a1), v2  # [op279] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
li a1, 32  # [op280] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add s1, s1, a1  # [op281] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t2, t0  # [op282] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t0  # [op283] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk7_head  # [op283] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk8_head:  # block chunk8_head
li s1, 256  # [op284] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-cmpfuse] slt s1, t0, s1 removed (fused into the branch)
blt t0, s1, .Lchunk8_body  # [op286] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op286] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op286] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk8_exit  # [op286] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-stub] bare trampoline .Lbrc286_true -> .Lchunk8_body removed
    # [peephole-stub] removed: j .Lchunk8_body
.Lchunk8_exit:  # block chunk8_exit
li t2, 0  # [op287] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd t0, 96(sp)  # [op288] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op288] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 96(sp)  # [op288] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk9_head  # [op288] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk8_body:  # block chunk8_body
    # [peephole-dead-li2] [op289] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli s1, x0, e32, m1, ta,ma  # [op290] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li s1, 32  # [op291] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add s1, t2, s1  # [op292] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t2, 32  # [op293] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t0, t2  # [op294] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, s1  # [op296] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk8_head  # [op296] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk9_head:  # block chunk9_head
li s1, 8192  # [op297] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-cmpfuse] slt s1, t0, s1 removed (fused into the branch)
blt t0, s1, .Lchunk9_body  # [op299] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op299] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op299] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk9_exit  # [op299] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-stub] bare trampoline .Lbrc299_true -> .Lchunk9_body removed
    # [peephole-stub] removed: j .Lchunk9_body
.Lchunk9_exit:  # block chunk9_exit
li t2, 0  # [op300] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv s1, t0  # [op301] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk10_head  # [op301] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk9_body:  # block chunk9_body
    # [peephole-dead-li2] [op302] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-superseded-vsetvli] [op303] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li s1, 32  # [op304] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
vsetvli a1, x0, e64, m2, ta,ma  # [op305] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
vid.v v2  # [op306] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
vadd.vx v2, v2, t0  # [op307] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
li a1, 256  # [op308] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
vmv.v.x v4, a1  # [op309] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
vdiv.vv v2, v2, v4  # [op310] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
li a1, 8  # [op311] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
vmul.vx v2, v2, a1  # [op312] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
li a1, 36736  # [op313] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
ld a2, 168(sp)  # [op314] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
add a1, a2, a1  # [op315] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
vluxei64.v v4, (a1), v2  # [op316] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
vsetvli a1, x0, e32, m1, ta,ma  # [op317] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
li a1, 32  # [op318] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add t2, t2, a1  # [op319] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t0, s1  # [op320] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk9_head  # [op321] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk10_head:  # block chunk10_head
li t0, 4096  # [op322] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-cmpfuse] slt t0, t2, t0 removed (fused into the branch)
blt t2, t0, .Lchunk10_body  # [op324] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op324] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, s1  # [op324] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk10_exit  # [op324] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-stub] bare trampoline .Lbrc324_true -> .Lchunk10_body removed
    # [peephole-stub] removed: j .Lchunk10_body
.Lchunk10_exit:  # block chunk10_exit
li t2, 0  # [op325] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv a1, t0  # [op326] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk11_head  # [op326] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk10_body:  # block chunk10_body
li t0, 32  # [op327] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-superseded-vsetvli] [op328] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-li] [op329] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli a1, x0, e64, m2, ta,ma  # [op330] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vid.v v2  # [op331] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vadd.vx v2, v2, t2  # [op332] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a1, 32  # [op333] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.v.x v4, a1  # [op334] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vdiv.vv v4, v2, v4  # [op335] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 4  # [op336] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmul.vx v4, v4, a2  # [op337] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a4, 2176  # [op338] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
ld a3, 168(sp)  # [op339] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a4, a3, a4  # [op340] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli a5, x0, e32, m1, ta,ma  # [op341] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vluxei64.v v1, (a4), v4  # [op342] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
    # [peephole-superseded-vsetvli] [op343] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli a4, x0, e64, m2, ta,ma  # [op344] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.v.x v4, a1  # [op345] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vrem.vv v2, v2, v4  # [op346] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmul.vx v2, v2, a2  # [op347] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 1536  # [op348] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, a3, a2  # [op349] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli a4, x0, e32, m1, ta,ma  # [op350] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vluxei64.v v4, (a2), v2  # [op351] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
    # [peephole-superseded-vsetvli] [op352] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli a2, x0, e32, m1, ta,ma  # [op353] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vadd.vv v1, v1, v4  # [op354] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
    # [peephole-superseded-vsetvli] [op355] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
    # [peephole-vsetvli] [op356] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vwadd.vx v2, v1, x0  # [op357] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli a2, x0, e64, m2, ta,ma  # [op358] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 2  # [op359] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmul.vx v2, v2, a2  # [op360] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
    # [peephole-superseded-vsetvli] [op361] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli a4, x0, e64, m2, ta,ma  # [op362] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a4, v2  # [op363] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
ld a5, 152(sp)  # [op364] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a4, a5, a4  # [op365] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli a5, t0, e16, m1, ta,ma  # [op366] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vle16.v v1, 0(a4)  # [op367] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a4, 103552  # [op368] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a3, a3, a4  # [op369] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
mv a4, t2  # [op370] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
mul a4, a4, a2  # [op371] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a4, a3, a4  # [op372] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vse16.v v1, 0(a4)  # [op373] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
mv a4, t2  # [op374] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
mul a2, a4, a2  # [op375] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, a3, a2  # [op376] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vse16.v v1, 0(a2)  # [op377] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add s1, s1, a1  # [op378] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t2, t0  # [op379] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t0  # [op380] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk10_head  # [op380] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk11_head:  # block chunk11_head
li t0, 8192  # [op381] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-cmpfuse] slt t0, t2, t0 removed (fused into the branch)
blt t2, t0, .Lchunk11_body  # [op383] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op383] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, a1  # [op383] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk11_exit  # [op383] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-stub] bare trampoline .Lbrc383_true -> .Lchunk11_body removed
    # [peephole-stub] removed: j .Lchunk11_body
.Lchunk11_exit:  # block chunk11_exit
li t2, 0  # [op384] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv s1, t0  # [op385] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op385] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk12_head  # [op385] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk11_body:  # block chunk11_body
li t0, 32  # [op386] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-superseded-vsetvli] [op387] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-li] [op388] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli s1, x0, e64, m2, ta,ma  # [op389] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vid.v v2  # [op390] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vadd.vx v2, v2, t2  # [op391] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li s1, 256  # [op392] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.v.x v4, s1  # [op393] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vdiv.vv v4, v2, v4  # [op394] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 4  # [op395] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmul.vx v4, v4, a2  # [op396] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a4, 36608  # [op397] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
ld a3, 168(sp)  # [op398] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a4, a3, a4  # [op399] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli a5, x0, e32, m1, ta,ma  # [op400] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vluxei64.v v1, (a4), v4  # [op401] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
    # [peephole-superseded-vsetvli] [op402] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli a4, x0, e64, m2, ta,ma  # [op403] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.v.x v4, s1  # [op404] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vrem.vv v2, v2, v4  # [op405] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmul.vx v2, v2, a2  # [op406] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li s1, 512  # [op407] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add s1, a3, s1  # [op408] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli a2, x0, e32, m1, ta,ma  # [op409] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vluxei64.v v4, (s1), v2  # [op410] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
    # [peephole-superseded-vsetvli] [op411] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli s1, x0, e32, m1, ta,ma  # [op412] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vadd.vv v1, v1, v4  # [op413] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli x0, t0, e16, m1, ta,ma  # [op414] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
    # [peephole-dead-li2] [op415] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.v.x v2, zero  # [op416] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli s1, x0, e32, m1, ta,ma  # [op417] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vwadd.vx v2, v1, x0  # [op418] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli s1, x0, e64, m2, ta,ma  # [op419] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li s1, 2  # [op420] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmul.vx v2, v2, s1  # [op421] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
    # [peephole-superseded-vsetvli] [op422] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 0  # [op423] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li t0, 16  # [op424] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli x0, t0, e64, m2, ta,ma  # [op425] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s t0, v2  # [op426] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vid.v v4  # [op427] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmul.vx v4, v4, s1  # [op428] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vadd.vx v4, v4, t0  # [op429] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmsne.vv v4, v2, v4  # [op430] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vcpop.m a3, v4  # [op431] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, a2, a3  # [op432] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
ld a2, 176(sp)  # [op433] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a4, a2, t0  # [op434] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vid.v v4  # [op435] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li t0, 16  # [op436] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vadd.vx v6, v4, t0  # [op437] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vrgather.vv v4, v2, v6  # [op438] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s t0, v4  # [op439] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vid.v v2  # [op440] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmul.vx v2, v2, s1  # [op441] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vadd.vx v2, v2, t0  # [op442] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmsne.vv v2, v4, v2  # [op443] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vcpop.m s1, v2  # [op444] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add s1, a3, s1  # [op445] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, a2, t0  # [op446] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
bne s1, zero, .Lngl.e1  # [op447] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
j .Lngl.t1  # [op447] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
    # [peephole-stub] bare trampoline .Lbrc447_true -> .Lngl.e1 removed
    # [peephole-stub] removed: j .Lngl.e1
.Lngl.t1:  # block ngl.t1
li t0, 523392  # [op448] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
ld s1, 168(sp)  # [op449] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add t0, s1, t0  # [op450] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li s1, 16  # [op451] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli x0, s1, e16, m1, ta,ma  # [op452] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vle16.v v1, 0(a4)  # [op453] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li s1, 0  # [op454] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add s1, t0, s1  # [op455] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vse16.v v1, 0(s1)  # [op456] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vle16.v v1, 0(a2)  # [op457] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li s1, 32  # [op458] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add s1, t0, s1  # [op459] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vse16.v v1, 0(s1)  # [op460] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li s1, 32  # [op461] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli s1, s1, e16, m1, ta,ma  # [op462] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vle16.v v1, 0(t0)  # [op463] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
j .Lngl.j1  # [op464] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
.Lngl.e1:  # block ngl.e1
li s1, 32  # [op465] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli t0, x0, e32, m1, ta,ma  # [op466] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vwadd.vx v2, v1, x0  # [op467] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli t0, x0, e64, m2, ta,ma  # [op468] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 2  # [op469] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmul.vx v2, v2, a2  # [op470] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
    # [peephole-superseded-vsetvli] [op471] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li t0, 523392  # [op472] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
ld a3, 168(sp)  # [op473] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add t0, a3, t0  # [op474] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 128  # [op475] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op476] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli a3, x0, e64, m2, ta,ma  # [op477] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
ld a3, 176(sp)  # [op478] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vadd.vx v2, v2, a3  # [op479] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a3, v2  # [op480] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a4, 0  # [op481] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a4, t0, a4  # [op482] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a3, 0(a3)  # [op483] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a3, 0(a4)  # [op484] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op485] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a3, v2  # [op486] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, t0, a2  # [op487] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a3, 0(a3)  # [op488] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a3, 0(a2)  # [op489] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op490] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op491] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 4  # [op492] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op493] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op494] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op495] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op496] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op497] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 6  # [op498] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op499] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op500] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op501] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op502] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op503] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 8  # [op504] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op505] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op506] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op507] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op508] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op509] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 10  # [op510] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op511] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op512] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op513] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op514] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op515] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 12  # [op516] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op517] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op518] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op519] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op520] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op521] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 14  # [op522] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op523] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op524] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op525] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op526] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op527] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 16  # [op528] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op529] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op530] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op531] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op532] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op533] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 18  # [op534] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op535] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op536] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op537] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op538] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op539] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 20  # [op540] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op541] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op542] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op543] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op544] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op545] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 22  # [op546] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op547] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op548] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op549] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op550] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op551] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 24  # [op552] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op553] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op554] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op555] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op556] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op557] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 26  # [op558] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op559] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op560] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op561] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op562] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op563] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 28  # [op564] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op565] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op566] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op567] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op568] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op569] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 30  # [op570] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op571] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op572] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op573] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op574] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op575] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 32  # [op576] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op577] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op578] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op579] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op580] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op581] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 34  # [op582] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op583] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op584] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op585] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op586] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op587] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 36  # [op588] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op589] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op590] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op591] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op592] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op593] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 38  # [op594] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op595] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op596] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op597] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op598] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op599] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 40  # [op600] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op601] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op602] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op603] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op604] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op605] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 42  # [op606] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op607] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op608] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op609] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op610] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op611] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 44  # [op612] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op613] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op614] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op615] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op616] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op617] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 46  # [op618] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op619] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op620] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op621] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op622] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op623] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 48  # [op624] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op625] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op626] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op627] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op628] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op629] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 50  # [op630] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op631] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op632] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op633] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op634] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op635] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 52  # [op636] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op637] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op638] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op639] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op640] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op641] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 54  # [op642] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op643] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op644] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op645] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op646] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op647] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 56  # [op648] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op649] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op650] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op651] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op652] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op653] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 58  # [op654] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op655] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op656] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op657] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op658] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op659] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 60  # [op660] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op661] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op662] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op663] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op664] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op665] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 62  # [op666] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op667] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op668] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op669] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op670] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli s1, s1, e16, m1, ta,ma  # [op671] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vle16.v v1, 0(t0)  # [op672] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
j .Lngl.j1  # [op673] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
.Lngl.j1:  # block ngl.j1
li t0, 32  # [op674] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli x0, t0, e16, m1, ta,ma  # [op675] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li s1, 111744  # [op676] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
ld a2, 168(sp)  # [op677] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add s1, a2, s1  # [op678] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
mv a2, t2  # [op679] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 2  # [op680] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
mul a2, a2, a3  # [op681] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add s1, s1, a2  # [op682] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vse16.v v1, 0(s1)  # [op683] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li s1, 32  # [op684] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add s1, a1, s1  # [op685] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t2, t0  # [op686] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t0  # [op687] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv a1, s1  # [op687] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk11_head  # [op687] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk12_head:  # block chunk12_head
li t2, 32768  # [op688] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-cmpfuse] slt t2, t0, t2 removed (fused into the branch)
blt t0, t2, .Lchunk12_body  # [op690] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t1  # [op690] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv s11, s1  # [op690] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk12_exit  # [op690] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-stub] bare trampoline .Lbrc690_true -> .Lchunk12_body removed
    # [peephole-stub] removed: j .Lchunk12_body
.Lchunk12_exit:  # block chunk12_exit
li t0, 522880  # [op691] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t2, 168(sp)  # [op692] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t0, t2, t0  # [op693] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sd t0, 184(sp)  # [op694] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t0, 128  # [op695] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t2, 184(sp)  # [op696] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t0, t2, t0  # [op697] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sd t0, 192(sp)  # [op698] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t0, 256  # [op699] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t2, 184(sp)  # [op700] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a1, t2, t0  # [op701] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t0, 8  # [op702] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli x0, t0, e32, m1, ta,ma  # [op703] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vid.v v1  # [op704] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vid.v v2  # [op705] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-dead-li2] [op706] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t0, x0, e16, m1, ta,ma  # [op707] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-dead-li2] [op708] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v3, zero  # [op709] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v4, zero  # [op710] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t0, 0  # [op711] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t3, 512  # [op712] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mv s3, t0  # [op713] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lmtile13.head  # [op713] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lchunk12_body:  # block chunk12_body
    # [peephole-dead-li2] [op714] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli t2, x0, e32, m1, ta,ma  # [op715] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-dead-li2] [op716] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
li t2, 32  # [op717] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
vmv.v.x v1, zero  # [op719] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
vsetvli a1, x0, e64, m2, ta,ma  # [op720] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
vid.v v2  # [op721] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
vadd.vx v2, v2, t0  # [op722] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
li a1, 4  # [op723] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
vmul.vx v2, v2, a1  # [op724] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
li a1, 128128  # [op725] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
ld a2, 168(sp)  # [op726] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
add a1, a2, a1  # [op727] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
vsetvli a2, x0, e32, m1, ta,ma  # [op728] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
vsuxei64.v v1, (a1), v2  # [op729] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
li a1, 32  # [op730] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add s1, s1, a1  # [op731] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t0, t2  # [op732] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk12_head  # [op733] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lmtile13.head:  # block mtile13.head
    # [peephole-cmpfuse] slt t0, s3, t3 removed (fused into the branch)
blt s3, t3, .Lmtile13.body  # [op735] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mv t0, s3  # [op735] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lmtile13.exit  # [op735] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-stub] bare trampoline .Lbrc735_true -> .Lmtile13.body removed
    # [peephole-stub] removed: j .Lmtile13.body
.Lmtile13.body:  # block mtile13.body
li s5, 32  # [op736] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
divu t0, s3, s5  # [op737] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t2, t0, s5  # [op738] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub s1, s3, t2  # [op739] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t2, 8  # [op740] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t0, t0, t2  # [op741] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sd t0, 216(sp)  # [op742] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t0, s1, t2  # [op743] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sd t0, 208(sp)  # [op744] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-dead-li2] [op745] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t0, x0, e32, m2, ta,ma  # [op746] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-dead-li2] [op747] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v6, zero  # [op748] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t0, 0  # [op749] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mv t2, t0  # [op750] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lmk14.head  # [op750] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lmtile13.exit:  # block mtile13.exit
li t0, 0  # [op751] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t0  # [op752] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv s1, s11  # [op752] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk18_head  # [op752] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lmk14.head:  # block mk14.head
    # [peephole-cmpfuse] slt t0, t2, s5 removed (fused into the branch)
blt t2, s5, .Lmk14.body  # [op754] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mv t0, t2  # [op754] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lmk14.exit  # [op754] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-stub] bare trampoline .Lbrc754_true -> .Lmk14.body removed
    # [peephole-stub] removed: j .Lmk14.body
.Lmk14.body:  # block mk14.body
li t0, 32  # [op755] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t0, t0, t2  # [op756] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sd t0, 200(sp)  # [op757] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t0, 8  # [op758] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld s1, 216(sp)  # [op759] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s1, s1, t0  # [op760] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a2, 129  # [op761] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt s1, s1, a2  # [op762] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a2, 1  # [op763] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a3, 200(sp)  # [op764] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a2, a3, a2  # [op765] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t0, t0, a2  # [op766] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t0, s1, t0  # [op767] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
bne t0, zero, .Ltaf15.then  # [op768] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Ltaf15.else  # [op768] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-stub] bare trampoline .Lbrc768_true -> .Ltaf15.then removed
    # [peephole-stub] removed: j .Ltaf15.then
.Lmk14.exit:  # block mk14.exit
    # [peephole-dead-li2] [op769] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t0, x0, e32, m2, ta,ma  # [op770] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse32.v v6, 0(a1)  # [op771] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t2, 0  # [op772] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a7, 216(sp)  # [op773] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a2, a7, t2  # [op774] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s1, 128  # [op775] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt a4, a2, s1  # [op776] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a3, 256  # [op777] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t0, 208(sp)  # [op778] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub a5, a3, t0  # [op779] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub a4, t2, a4  # [op780] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and a4, a5, a4  # [op781] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw a4, a4, 0  # [op782] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a5, 8  # [op783] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli x0, a5, e32, m1, ta,ma  # [op784] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, a4  # [op785] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v2, v5  # [op786] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op787] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a4, a1, t2  # [op788] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle32.v v5, 0(a4)  # [op789] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a4, 259200  # [op790] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a6, 168(sp)  # [op791] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s2, a6, a4  # [op792] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a5, 1024  # [op793] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul a2, a2, a5  # [op794] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s2, s2, a2  # [op795] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a2, 4  # [op796] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s5, t0, a2  # [op797] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s2, s2, s5  # [op798] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse32.v v5, 0(s2), v0.t  # [op799] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s2, 1  # [op800] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s5, a7, s2  # [op801] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt s6, s5, s1  # [op802] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, a3, t0  # [op803] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub s6, t2, s6  # [op804] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and s6, t4, s6  # [op805] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw s6, s6, 0  # [op806] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, s6  # [op807] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v2, v5  # [op808] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op809] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 32  # [op810] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, a1, s6  # [op811] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle32.v v5, 0(s6)  # [op812] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, a6, a4  # [op813] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s5, s5, a5  # [op814] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s5, s6, s5  # [op815] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s6, t0, a2  # [op816] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s5, s5, s6  # [op817] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse32.v v5, 0(s5), v0.t  # [op818] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s5, 2  # [op819] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s5, a7, s5  # [op820] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt s6, s5, s1  # [op821] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, a3, t0  # [op822] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub s6, t2, s6  # [op823] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and s6, t4, s6  # [op824] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw s6, s6, 0  # [op825] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, s6  # [op826] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v2, v5  # [op827] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op828] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 64  # [op829] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, a1, s6  # [op830] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle32.v v5, 0(s6)  # [op831] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, a6, a4  # [op832] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s5, s5, a5  # [op833] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s5, s6, s5  # [op834] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s6, t0, a2  # [op835] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s5, s5, s6  # [op836] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse32.v v5, 0(s5), v0.t  # [op837] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s5, 3  # [op838] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s5, a7, s5  # [op839] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt s6, s5, s1  # [op840] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, a3, t0  # [op841] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub s6, t2, s6  # [op842] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and s6, t4, s6  # [op843] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw s6, s6, 0  # [op844] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, s6  # [op845] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v2, v5  # [op846] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op847] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 96  # [op848] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, a1, s6  # [op849] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle32.v v5, 0(s6)  # [op850] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, a6, a4  # [op851] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s5, s5, a5  # [op852] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s5, s6, s5  # [op853] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s6, t0, a2  # [op854] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s5, s5, s6  # [op855] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse32.v v5, 0(s5), v0.t  # [op856] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s5, a7, a2  # [op857] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt s6, s5, s1  # [op858] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, a3, t0  # [op859] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub s6, t2, s6  # [op860] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and s6, t4, s6  # [op861] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw s6, s6, 0  # [op862] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, s6  # [op863] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v2, v5  # [op864] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op865] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, a1, s1  # [op866] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle32.v v5, 0(s6)  # [op867] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, a6, a4  # [op868] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s5, s5, a5  # [op869] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s5, s6, s5  # [op870] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s6, t0, a2  # [op871] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s5, s5, s6  # [op872] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse32.v v5, 0(s5), v0.t  # [op873] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s5, 5  # [op874] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s5, a7, s5  # [op875] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt s6, s5, s1  # [op876] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, a3, t0  # [op877] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub s6, t2, s6  # [op878] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and s6, t4, s6  # [op879] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw s6, s6, 0  # [op880] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, s6  # [op881] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v2, v5  # [op882] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op883] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 160  # [op884] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, a1, s6  # [op885] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle32.v v5, 0(s6)  # [op886] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, a6, a4  # [op887] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s5, s5, a5  # [op888] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s5, s6, s5  # [op889] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s6, t0, a2  # [op890] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s5, s5, s6  # [op891] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse32.v v5, 0(s5), v0.t  # [op892] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s5, 6  # [op893] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s5, a7, s5  # [op894] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt s6, s5, s1  # [op895] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, a3, t0  # [op896] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub s6, t2, s6  # [op897] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and s6, t4, s6  # [op898] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw s6, s6, 0  # [op899] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, s6  # [op900] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v2, v5  # [op901] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op902] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 192  # [op903] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, a1, s6  # [op904] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle32.v v5, 0(s6)  # [op905] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, a6, a4  # [op906] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s5, s5, a5  # [op907] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s5, s6, s5  # [op908] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s6, t0, a2  # [op909] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s5, s5, s6  # [op910] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse32.v v5, 0(s5), v0.t  # [op911] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s5, 7  # [op912] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a7, a7, s5  # [op913] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt s1, a7, s1  # [op914] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub a3, a3, t0  # [op915] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t2, t2, s1  # [op916] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t2, a3, t2  # [op917] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw t2, t2, 0  # [op918] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, t2  # [op919] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v2, v5  # [op920] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op921] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t2, 224  # [op922] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t2, a1, t2  # [op923] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle32.v v5, 0(t2)  # [op924] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t2, a6, a4  # [op925] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s1, a7, a5  # [op926] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t2, t2, s1  # [op927] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t0, t0, a2  # [op928] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t0, t2, t0  # [op929] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse32.v v5, 0(t0), v0.t  # [op930] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t0, s3, s2  # [op931] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mv s3, t0  # [op932] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lmtile13.head  # [op932] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Ltaf15.then:  # block taf15.then
li t0, 8  # [op933] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli x0, t0, e16, m1, ta,ma  # [op934] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t0, 103552  # [op935] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld s1, 168(sp)  # [op936] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s1, s1, t0  # [op937] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t0, 64  # [op938] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a2, 216(sp)  # [op939] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul a2, a2, t0  # [op940] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s1, s1, a2  # [op941] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a2, 2  # [op942] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul a2, t2, a2  # [op943] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s1, s1, a2  # [op944] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(s1)  # [op945] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a3, 184(sp)  # [op946] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a3)  # [op947] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a2, s1, t0  # [op948] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s1, 16  # [op949] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a3, a3, s1  # [op950] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(a2)  # [op951] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a3)  # [op952] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a2, a2, t0  # [op953] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a3, a3, s1  # [op954] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(a2)  # [op955] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a3)  # [op956] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a2, a2, t0  # [op957] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a3, a3, s1  # [op958] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(a2)  # [op959] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a3)  # [op960] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a2, a2, t0  # [op961] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a3, a3, s1  # [op962] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(a2)  # [op963] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a3)  # [op964] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a2, a2, t0  # [op965] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a3, a3, s1  # [op966] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(a2)  # [op967] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a3)  # [op968] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a2, a2, t0  # [op969] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a3, a3, s1  # [op970] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(a2)  # [op971] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a3)  # [op972] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t0, a2, t0  # [op973] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s1, a3, s1  # [op974] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(t0)  # [op975] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(s1)  # [op976] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Ltaf15.join  # [op977] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Ltaf15.else:  # block taf15.else
li t0, 0  # [op978] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld s2, 216(sp)  # [op979] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a3, s2, t0  # [op980] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a4, 128  # [op981] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt s1, a3, a4  # [op982] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t0, 200(sp)  # [op983] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a2, 8  # [op984] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt a2, t0, a2  # [op985] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a5, 0  # [op986] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub a2, a5, a2  # [op987] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a5, 8  # [op988] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub a5, a5, t0  # [op989] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and a2, a5, a2  # [op990] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a2, t0, a2  # [op991] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a5, 0  # [op992] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub s1, a5, s1  # [op993] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and s1, a2, s1  # [op994] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw a2, s1, 0  # [op995] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s1, 8  # [op996] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli x0, s1, e32, m1, ta,ma  # [op997] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, a2  # [op998] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v1, v5  # [op999] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1000] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a5, 103552  # [op1001] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a6, 168(sp)  # [op1002] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a7, a6, a5  # [op1003] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a2, 64  # [op1004] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul a3, a3, a2  # [op1005] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a7, a7, a3  # [op1006] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a3, 2  # [op1007] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s6, t2, a3  # [op1008] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a7, a7, s6  # [op1009] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli x0, s1, e16, m1, ta,ma  # [op1010] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(a7), v0.t  # [op1011] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmerge.vvm v5, v3, v5, v0  # [op1012] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a7, 184(sp)  # [op1013] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 0  # [op1014] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, a7, s6  # [op1015] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(s6)  # [op1016] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 1  # [op1017] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s2, s6  # [op1018] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t4, s6, a4  # [op1019] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t5, 8  # [op1020] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t5, t0, t5  # [op1021] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t6, 0  # [op1022] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t5, t6, t5  # [op1023] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t6, 8  # [op1024] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t6, t6, t0  # [op1025] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t5, t6, t5  # [op1026] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t5, t0, t5  # [op1027] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t6, 0  # [op1028] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, t6, t4  # [op1029] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t4, t5, t4  # [op1030] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw t4, t4, 0  # [op1031] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli x0, s1, e32, m1, ta,ma  # [op1032] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, t4  # [op1033] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v1, v5  # [op1034] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1035] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t4, a6, a5  # [op1036] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s6, s6, a2  # [op1037] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t4, s6  # [op1038] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t4, t2, a3  # [op1039] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s6, t4  # [op1040] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli x0, s1, e16, m1, ta,ma  # [op1041] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(s6), v0.t  # [op1042] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmerge.vvm v5, v3, v5, v0  # [op1043] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 16  # [op1044] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, a7, s6  # [op1045] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(s6)  # [op1046] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s2, a3  # [op1047] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t4, s6, a4  # [op1048] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t5, 8  # [op1049] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t5, t0, t5  # [op1050] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-li] [op1051] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t5, t6, t5  # [op1052] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t6, 8  # [op1053] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t6, t6, t0  # [op1054] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t5, t6, t5  # [op1055] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t5, t0, t5  # [op1056] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t6, 0  # [op1057] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, t6, t4  # [op1058] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t4, t5, t4  # [op1059] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw t4, t4, 0  # [op1060] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli x0, s1, e32, m1, ta,ma  # [op1061] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, t4  # [op1062] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v1, v5  # [op1063] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1064] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t4, a6, a5  # [op1065] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s6, s6, a2  # [op1066] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t4, s6  # [op1067] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t4, t2, a3  # [op1068] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s6, t4  # [op1069] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli x0, s1, e16, m1, ta,ma  # [op1070] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(s6), v0.t  # [op1071] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmerge.vvm v5, v3, v5, v0  # [op1072] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 32  # [op1073] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, a7, s6  # [op1074] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(s6)  # [op1075] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 3  # [op1076] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s2, s6  # [op1077] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t4, s6, a4  # [op1078] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t5, 8  # [op1079] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t5, t0, t5  # [op1080] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-li] [op1081] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t5, t6, t5  # [op1082] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t6, 8  # [op1083] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t6, t6, t0  # [op1084] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t5, t6, t5  # [op1085] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t5, t0, t5  # [op1086] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t6, 0  # [op1087] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, t6, t4  # [op1088] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t4, t5, t4  # [op1089] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw t4, t4, 0  # [op1090] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli x0, s1, e32, m1, ta,ma  # [op1091] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, t4  # [op1092] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v1, v5  # [op1093] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1094] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t4, a6, a5  # [op1095] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s6, s6, a2  # [op1096] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t4, s6  # [op1097] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t4, t2, a3  # [op1098] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s6, t4  # [op1099] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli x0, s1, e16, m1, ta,ma  # [op1100] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(s6), v0.t  # [op1101] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmerge.vvm v5, v3, v5, v0  # [op1102] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 48  # [op1103] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, a7, s6  # [op1104] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(s6)  # [op1105] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 4  # [op1106] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s2, s6  # [op1107] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t4, s6, a4  # [op1108] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t5, 8  # [op1109] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t5, t0, t5  # [op1110] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-li] [op1111] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t5, t6, t5  # [op1112] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t6, 8  # [op1113] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t6, t6, t0  # [op1114] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t5, t6, t5  # [op1115] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t5, t0, t5  # [op1116] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t6, 0  # [op1117] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, t6, t4  # [op1118] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t4, t5, t4  # [op1119] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw t4, t4, 0  # [op1120] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli x0, s1, e32, m1, ta,ma  # [op1121] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, t4  # [op1122] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v1, v5  # [op1123] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1124] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t4, a6, a5  # [op1125] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s6, s6, a2  # [op1126] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t4, s6  # [op1127] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t4, t2, a3  # [op1128] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s6, t4  # [op1129] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli x0, s1, e16, m1, ta,ma  # [op1130] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(s6), v0.t  # [op1131] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmerge.vvm v5, v3, v5, v0  # [op1132] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, a7, a2  # [op1133] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(s6)  # [op1134] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 5  # [op1135] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s2, s6  # [op1136] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t4, s6, a4  # [op1137] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t5, 8  # [op1138] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t5, t0, t5  # [op1139] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-li] [op1140] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t5, t6, t5  # [op1141] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t6, 8  # [op1142] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t6, t6, t0  # [op1143] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t5, t6, t5  # [op1144] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t5, t0, t5  # [op1145] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t6, 0  # [op1146] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, t6, t4  # [op1147] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t4, t5, t4  # [op1148] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw t4, t4, 0  # [op1149] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli x0, s1, e32, m1, ta,ma  # [op1150] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, t4  # [op1151] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v1, v5  # [op1152] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1153] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t4, a6, a5  # [op1154] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s6, s6, a2  # [op1155] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t4, s6  # [op1156] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t4, t2, a3  # [op1157] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s6, t4  # [op1158] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli x0, s1, e16, m1, ta,ma  # [op1159] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(s6), v0.t  # [op1160] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmerge.vvm v5, v3, v5, v0  # [op1161] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 80  # [op1162] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, a7, s6  # [op1163] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(s6)  # [op1164] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 6  # [op1165] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s2, s6  # [op1166] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t4, s6, a4  # [op1167] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t5, 8  # [op1168] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t5, t0, t5  # [op1169] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-li] [op1170] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t5, t6, t5  # [op1171] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t6, 8  # [op1172] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t6, t6, t0  # [op1173] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t5, t6, t5  # [op1174] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t5, t0, t5  # [op1175] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t6, 0  # [op1176] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, t6, t4  # [op1177] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t4, t5, t4  # [op1178] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw t4, t4, 0  # [op1179] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t5, s1, e32, m1, ta,ma  # [op1180] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, t4  # [op1181] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v1, v5  # [op1182] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1183] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t4, a6, a5  # [op1184] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s6, s6, a2  # [op1185] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t4, s6  # [op1186] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t4, t2, a3  # [op1187] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s6, t4  # [op1188] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli x0, s1, e16, m1, ta,ma  # [op1189] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(s6), v0.t  # [op1190] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmerge.vvm v5, v3, v5, v0  # [op1191] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 96  # [op1192] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, a7, s6  # [op1193] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(s6)  # [op1194] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 7  # [op1195] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s2, s2, s6  # [op1196] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt a4, s2, a4  # [op1197] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 8  # [op1198] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt s6, t0, s6  # [op1199] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t4, 0  # [op1200] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub s6, t4, s6  # [op1201] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t4, 8  # [op1202] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, t4, t0  # [op1203] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and s6, t4, s6  # [op1204] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t0, t0, s6  # [op1205] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 0  # [op1206] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub a4, s6, a4  # [op1207] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t0, t0, a4  # [op1208] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw t0, t0, 0  # [op1209] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli a4, s1, e32, m1, ta,ma  # [op1210] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, t0  # [op1211] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v1, v5  # [op1212] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1213] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t0, a6, a5  # [op1214] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul a2, s2, a2  # [op1215] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t0, t0, a2  # [op1216] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul a2, t2, a3  # [op1217] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t0, t0, a2  # [op1218] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli s1, s1, e16, m1, ta,ma  # [op1219] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(t0), v0.t  # [op1220] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmerge.vvm v5, v3, v5, v0  # [op1221] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t0, 112  # [op1222] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t0, a7, t0  # [op1223] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(t0)  # [op1224] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Ltaf15.join  # [op1225] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Ltaf15.join:  # block taf15.join
li t0, 8  # [op1226] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld s1, 208(sp)  # [op1227] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s1, s1, t0  # [op1228] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a2, 257  # [op1229] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt s1, s1, a2  # [op1230] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a2, 1  # [op1231] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a3, 200(sp)  # [op1232] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a2, a3, a2  # [op1233] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t0, t0, a2  # [op1234] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t0, s1, t0  # [op1235] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
bne t0, zero, .Lpbf16.then  # [op1236] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lpbf16.else  # [op1236] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-stub] bare trampoline .Lbrc1236_true -> .Lpbf16.then removed
    # [peephole-stub] removed: j .Lpbf16.then
.Lpbf16.then:  # block pbf16.then
li t0, 8  # [op1237] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli x0, t0, e16, m1, ta,ma  # [op1238] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t0, 512  # [op1239] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s1, 111744  # [op1240] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a2, 168(sp)  # [op1241] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s1, a2, s1  # [op1242] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul a2, t2, t0  # [op1243] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a2, s1, a2  # [op1244] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s1, 2  # [op1245] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a3, 208(sp)  # [op1246] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul a3, a3, s1  # [op1247] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a2, a2, a3  # [op1248] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vlse16.v v5, 0(a2), t0  # [op1249] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a4, 192(sp)  # [op1250] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a4)  # [op1251] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a3, a2, s1  # [op1252] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a2, 16  # [op1253] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a4, a4, a2  # [op1254] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vlse16.v v5, 0(a3), t0  # [op1255] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a4)  # [op1256] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a3, a3, s1  # [op1257] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a4, a4, a2  # [op1258] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vlse16.v v5, 0(a3), t0  # [op1259] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a4)  # [op1260] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a3, a3, s1  # [op1261] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a4, a4, a2  # [op1262] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vlse16.v v5, 0(a3), t0  # [op1263] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a4)  # [op1264] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a3, a3, s1  # [op1265] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a4, a4, a2  # [op1266] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vlse16.v v5, 0(a3), t0  # [op1267] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a4)  # [op1268] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a3, a3, s1  # [op1269] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a4, a4, a2  # [op1270] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vlse16.v v5, 0(a3), t0  # [op1271] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a4)  # [op1272] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a3, a3, s1  # [op1273] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a4, a4, a2  # [op1274] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vlse16.v v5, 0(a3), t0  # [op1275] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a4)  # [op1276] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s1, a3, s1  # [op1277] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a2, a4, a2  # [op1278] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vlse16.v v5, 0(s1), t0  # [op1279] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a2)  # [op1280] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lpbf16.join  # [op1281] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lpbf16.else:  # block pbf16.else
li t0, 8  # [op1282] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli x0, t0, e16, m1, ta,ma  # [op1283] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s1, 0  # [op1284] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t0, 192(sp)  # [op1285] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a2, t0, s1  # [op1286] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v4, 0(a2)  # [op1287] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a2, 16  # [op1288] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a2, t0, a2  # [op1289] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v4, 0(a2)  # [op1290] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a2, 32  # [op1291] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a2, t0, a2  # [op1292] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v4, 0(a2)  # [op1293] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a2, 48  # [op1294] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a2, t0, a2  # [op1295] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v4, 0(a2)  # [op1296] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a2, 64  # [op1297] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a2, t0, a2  # [op1298] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v4, 0(a2)  # [op1299] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a2, 80  # [op1300] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a2, t0, a2  # [op1301] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v4, 0(a2)  # [op1302] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a2, 96  # [op1303] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a2, t0, a2  # [op1304] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v4, 0(a2)  # [op1305] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a2, 112  # [op1306] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t0, t0, a2  # [op1307] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v4, 0(t0)  # [op1308] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a5, 8  # [op1309] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mv t0, s1  # [op1310] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lpb17.head  # [op1310] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lpb17.head:  # block pb17.head
    # [peephole-cmpfuse] slt s1, t0, a5 removed (fused into the branch)
blt t0, a5, .Lpb17.body  # [op1312] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lpb17.exit  # [op1312] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-stub] bare trampoline .Lbrc1312_true -> .Lpb17.body removed
    # [peephole-stub] removed: j .Lpb17.body
.Lpb17.body:  # block pb17.body
ld s1, 208(sp)  # [op1313] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a2, s1, t0  # [op1314] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s1, 256  # [op1315] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt a6, a2, s1  # [op1316] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a3, 8  # [op1317] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld s1, 200(sp)  # [op1318] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt a7, s1, a3  # [op1319] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a4, 0  # [op1320] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub a7, a4, a7  # [op1321] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub a3, a3, s1  # [op1322] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and a3, a3, a7  # [op1323] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s1, s1, a3  # [op1324] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub a3, a4, a6  # [op1325] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and a3, s1, a3  # [op1326] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s1, 111744  # [op1327] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a4, 168(sp)  # [op1328] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a4, a4, s1  # [op1329] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s1, 512  # [op1330] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul a6, t2, s1  # [op1331] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a4, a4, a6  # [op1332] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a6, 2  # [op1333] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul a2, a2, a6  # [op1334] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a2, a4, a2  # [op1335] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a4, 16  # [op1336] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul a4, t0, a4  # [op1337] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a6, 192(sp)  # [op1338] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a4, a6, a4  # [op1339] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw a3, a3, 0  # [op1340] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli a3, a3, e16, m1, ta,ma  # [op1341] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vlse16.v v5, 0(a2), s1  # [op1342] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a4)  # [op1343] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s1, 1  # [op1344] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t0, t0, s1  # [op1345] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lpb17.head  # [op1346] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lpb17.exit:  # block pb17.exit
j .Lpbf16.join  # [op1347] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lpbf16.join:  # block pbf16.join
    # [peephole-dead-li2] [op1348] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t0, x0, e16, m1, ta,ma  # [op1349] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t0, 184(sp)  # [op1350] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(t0)  # [op1351] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t0, 192(sp)  # [op1352] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v8, 0(t0)  # [op1353] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli x0, zero, e16, m1, ta, ma
    smt.vfwmadot v6, v5, v8  # [op1354] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t0, 8  # [op1355] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t0, t2, t0  # [op1356] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mv t2, t0  # [op1357] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lmk14.head  # [op1357] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lchunk18_head:  # block chunk18_head
li t0, 32768  # [op1358] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-cmpfuse] slt t0, t2, t0 removed (fused into the branch)
blt t2, t0, .Lchunk18_body  # [op1360] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op1360] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, s1  # [op1360] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk18_exit  # [op1360] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-stub] bare trampoline .Lbrc1360_true -> .Lchunk18_body removed
    # [peephole-stub] removed: j .Lchunk18_body
.Lchunk18_exit:  # block chunk18_exit
li t2, 0  # [op1361] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv s1, t0  # [op1362] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk19_head  # [op1362] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk18_body:  # block chunk18_body
    # [peephole-dead-li2] [op1363] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-superseded-vsetvli] [op1364] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t0, 32  # [op1365] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vsetvli a1, x0, e64, m2, ta,ma  # [op1366] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vid.v v2  # [op1367] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vadd.vx v2, v2, t2  # [op1368] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
li a1, 4  # [op1369] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vmul.vx v2, v2, a1  # [op1370] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
li a2, 128128  # [op1371] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
ld a1, 168(sp)  # [op1372] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
add a2, a1, a2  # [op1373] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vsetvli a3, x0, e32, m1, ta,ma  # [op1374] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vluxei64.v v1, (a2), v2  # [op1375] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
    # [peephole-superseded-vsetvli] [op1376] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
li a2, 259200  # [op1377] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
add a2, a1, a2  # [op1378] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
    # [peephole-vsetvli] [op1379] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vluxei64.v v4, (a2), v2  # [op1380] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vfadd.vv v1, v1, v4  # [op1381] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
    # [peephole-superseded-vsetvli] [op1382] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
li a2, 390272  # [op1383] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
add a1, a1, a2  # [op1384] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vsetvli a2, x0, e32, m1, ta,ma  # [op1385] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vsuxei64.v v1, (a1), v2  # [op1386] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
li a1, 32  # [op1387] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add s1, s1, a1  # [op1388] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t2, t0  # [op1389] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t0  # [op1390] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk18_head  # [op1390] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk19_head:  # block chunk19_head
li t0, 128  # [op1391] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-cmpfuse] slt t0, t2, t0 removed (fused into the branch)
blt t2, t0, .Lchunk19_body  # [op1393] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op1393] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, s1  # [op1393] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk19_exit  # [op1393] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-stub] bare trampoline .Lbrc1393_true -> .Lchunk19_body removed
    # [peephole-stub] removed: j .Lchunk19_body
.Lchunk19_exit:  # block chunk19_exit
li t2, 0  # [op1394] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv a1, t0  # [op1395] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk20_head  # [op1395] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk19_body:  # block chunk19_body
    # [peephole-dead-li2] [op1396] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli t0, x0, e32, m1, ta,ma  # [op1397] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t0, 32  # [op1398] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
ld a1, 144(sp)  # [op1400] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vmv.v.x v1, a1  # [op1401] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vsetvli a1, x0, e64, m2, ta,ma  # [op1402] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vid.v v2  # [op1403] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vadd.vx v2, v2, t2  # [op1404] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
li a1, 4  # [op1405] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vmul.vx v2, v2, a1  # [op1406] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
li a2, 0  # [op1407] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
ld a1, 168(sp)  # [op1408] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
add a2, a1, a2  # [op1409] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vsetvli a3, x0, e32, m1, ta,ma  # [op1410] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vluxei64.v v4, (a2), v2  # [op1411] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vmul.vv v1, v4, v1  # [op1412] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
    # [peephole-superseded-vsetvli] [op1413] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
li a2, 521344  # [op1414] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
add a1, a1, a2  # [op1415] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vsetvli a2, x0, e32, m1, ta,ma  # [op1416] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vsuxei64.v v1, (a1), v2  # [op1417] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
li a1, 32  # [op1418] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add s1, s1, a1  # [op1419] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t2, t0  # [op1420] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t0  # [op1421] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk19_head  # [op1421] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk20_head:  # block chunk20_head
li t0, 32768  # [op1422] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-cmpfuse] slt t0, t2, t0 removed (fused into the branch)
blt t2, t0, .Lchunk20_body  # [op1424] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op1424] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, a1  # [op1424] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk20_exit  # [op1424] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-stub] bare trampoline .Lbrc1424_true -> .Lchunk20_body removed
    # [peephole-stub] removed: j .Lchunk20_body
.Lchunk20_exit:  # block chunk20_exit
sd t0, 96(sp)  # [op1425] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t1  # [op1425] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t1, 96(sp)  # [op1425] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lprog_next  # [op1425] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk20_body:  # block chunk20_body
li t0, 32  # [op1426] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-superseded-vsetvli] [op1427] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    # [peephole-li] [op1428] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
vsetvli s1, x0, e64, m2, ta,ma  # [op1429] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
vid.v v2  # [op1430] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
vadd.vx v2, v2, t2  # [op1431] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
li a2, 256  # [op1432] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
vmv.v.x v4, a2  # [op1433] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
vdiv.vv v4, v2, v4  # [op1434] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
li s1, 8  # [op1435] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
vmul.vx v4, v4, s1  # [op1436] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
li a3, 521856  # [op1437] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
ld s1, 168(sp)  # [op1438] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
add a3, s1, a3  # [op1439] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
vluxei64.v v6, (a3), v4  # [op1440] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
    # [peephole-superseded-vsetvli] [op1441] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
vsetvli a3, x0, e64, m2, ta,ma  # [op1442] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a3, 4  # [op1443] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmul.vx v4, v2, a3  # [op1444] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a4, 390272  # [op1445] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a4, s1, a4  # [op1446] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli a5, x0, e32, m1, ta,ma  # [op1447] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vluxei64.v v1, (a4), v4  # [op1448] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
    # [peephole-superseded-vsetvli] [op1449] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli a4, x0, e32, m1, ta,ma  # [op1450] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.v.v v4, v1  # [op1451] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli x0, t0, e16, m1, ta,ma  # [op1452] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vfncvt.f.f.w v1, v4  # [op1453] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli a4, x0, e64, m2, ta,ma  # [op1454] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.v.x v4, a2  # [op1455] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vdiv.vv v4, v2, v4  # [op1456] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmul.vx v4, v4, a3  # [op1457] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a4, 521344  # [op1458] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a4, s1, a4  # [op1459] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli a5, x0, e32, m1, ta,ma  # [op1460] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vluxei64.v v6, (a4), v4  # [op1461] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
    # [peephole-superseded-vsetvli] [op1462] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli a4, x0, e64, m2, ta,ma  # [op1463] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.v.x v4, a2  # [op1464] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vrem.vv v2, v2, v4  # [op1465] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmul.vx v2, v2, a3  # [op1466] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 512  # [op1467] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add s1, s1, a2  # [op1468] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli a2, x0, e32, m1, ta,ma  # [op1469] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vluxei64.v v4, (s1), v2  # [op1470] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
    # [peephole-superseded-vsetvli] [op1471] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli s1, x0, e32, m1, ta,ma  # [op1472] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vadd.vv v4, v6, v4  # [op1473] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
    # [peephole-superseded-vsetvli] [op1474] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
    # [peephole-vsetvli] [op1475] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vwadd.vx v2, v4, x0  # [op1476] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli s1, x0, e64, m2, ta,ma  # [op1477] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li s1, 2  # [op1478] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmul.vx v2, v2, s1  # [op1479] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
    # [peephole-superseded-vsetvli] [op1480] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 0  # [op1481] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 16  # [op1482] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli x0, t0, e64, m2, ta,ma  # [op1483] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s t0, v2  # [op1484] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vid.v v6  # [op1485] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmul.vx v6, v6, s1  # [op1486] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vadd.vx v6, v6, t0  # [op1487] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmsne.vv v5, v2, v6  # [op1488] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vcpop.m a3, v5  # [op1489] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, a2, a3  # [op1490] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a3, s4, t0  # [op1491] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vid.v v6  # [op1492] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 16  # [op1493] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vadd.vx v8, v6, t0  # [op1494] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vrgather.vv v6, v2, v8  # [op1495] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s t0, v6  # [op1496] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vid.v v2  # [op1497] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmul.vx v2, v2, s1  # [op1498] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vadd.vx v2, v2, t0  # [op1499] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmsne.vv v2, v6, v2  # [op1500] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vcpop.m s1, v2  # [op1501] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add s1, a2, s1  # [op1502] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add t0, s4, t0  # [op1503] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
bne s1, zero, .Lngs.e2  # [op1504] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
j .Lngs.t2  # [op1504] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
    # [peephole-stub] bare trampoline .Lbrc1504_true -> .Lngs.e2 removed
    # [peephole-stub] removed: j .Lngs.e2
.Lngs.t2:  # block ngs.t2
li s1, 16  # [op1505] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli x0, s1, e16, m1, ta,ma  # [op1506] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vse16.v v1, 0(a3)  # [op1507] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vid.v v2  # [op1508] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
    # [peephole-li] [op1509] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vadd.vx v2, v2, s1  # [op1510] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vrgather.vv v3, v1, v2  # [op1511] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vse16.v v3, 0(t0)  # [op1512] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
j .Lngs.j2  # [op1513] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
.Lngs.e2:  # block ngs.e2
li s1, 32  # [op1514] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli t0, x0, e32, m1, ta,ma  # [op1515] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vwadd.vx v2, v4, x0  # [op1516] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli t0, x0, e64, m2, ta,ma  # [op1517] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 2  # [op1518] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmul.vx v2, v2, a2  # [op1519] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli x0, s1, e16, m1, ta,ma  # [op1520] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 523392  # [op1521] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
ld a3, 168(sp)  # [op1522] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add t0, a3, t0  # [op1523] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a3, 128  # [op1524] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a3, t0, a3  # [op1525] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vse16.v v1, 0(t0)  # [op1526] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli s1, x0, e64, m2, ta,ma  # [op1527] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vadd.vx v2, v2, s4  # [op1528] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1529] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a3, 0  # [op1530] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a3, t0, a3  # [op1531] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a3, 0(a3)  # [op1532] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a3, 0(s1)  # [op1533] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1534] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1535] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1536] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1537] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1538] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1539] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1540] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 4  # [op1541] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1542] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1543] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1544] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1545] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1546] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 6  # [op1547] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1548] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1549] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1550] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1551] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1552] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 8  # [op1553] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1554] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1555] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1556] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1557] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1558] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 10  # [op1559] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1560] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1561] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1562] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1563] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1564] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 12  # [op1565] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1566] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1567] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1568] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1569] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1570] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 14  # [op1571] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1572] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1573] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1574] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1575] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1576] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 16  # [op1577] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1578] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1579] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1580] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1581] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1582] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 18  # [op1583] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1584] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1585] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1586] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1587] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1588] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 20  # [op1589] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1590] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1591] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1592] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1593] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1594] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 22  # [op1595] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1596] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1597] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1598] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1599] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1600] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 24  # [op1601] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1602] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1603] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1604] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1605] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1606] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 26  # [op1607] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1608] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1609] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1610] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1611] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1612] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 28  # [op1613] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1614] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1615] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1616] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1617] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1618] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 30  # [op1619] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1620] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1621] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1622] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1623] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1624] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 32  # [op1625] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1626] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1627] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1628] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1629] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1630] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 34  # [op1631] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1632] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1633] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1634] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1635] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1636] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 36  # [op1637] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1638] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1639] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1640] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1641] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1642] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 38  # [op1643] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1644] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1645] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1646] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1647] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1648] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 40  # [op1649] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1650] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1651] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1652] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1653] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1654] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 42  # [op1655] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1656] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1657] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1658] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1659] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1660] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 44  # [op1661] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1662] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1663] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1664] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1665] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1666] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 46  # [op1667] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1668] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1669] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1670] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1671] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1672] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 48  # [op1673] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1674] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1675] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1676] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1677] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1678] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 50  # [op1679] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1680] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1681] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1682] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1683] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1684] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 52  # [op1685] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1686] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1687] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1688] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1689] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1690] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 54  # [op1691] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1692] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1693] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1694] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1695] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1696] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 56  # [op1697] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1698] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1699] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1700] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1701] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1702] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 58  # [op1703] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1704] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1705] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1706] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1707] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1708] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 60  # [op1709] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1710] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1711] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1712] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1713] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1714] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 62  # [op1715] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add t0, t0, a2  # [op1716] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu t0, 0(t0)  # [op1717] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh t0, 0(s1)  # [op1718] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1719] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
j .Lngs.j2  # [op1720] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
.Lngs.j2:  # block ngs.j2
li t0, 32  # [op1721] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli x0, t0, e16, m1, ta,ma  # [op1722] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li s1, 32  # [op1723] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add s1, a1, s1  # [op1724] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t2, t0  # [op1725] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t0  # [op1726] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv a1, s1  # [op1726] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk20_head  # [op1726] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lprog_next:  # block prog_next
add t0, t0, s10  # [op1727] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lprog_head  # [op1728] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lprog_exit:  # block prog_exit
sd t0, 0(s7)  # [op1729] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld ra, 0(sp)  # [op1730] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 8(sp)  # [op1730] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s2, 16(sp)  # [op1730] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s3, 24(sp)  # [op1730] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s4, 32(sp)  # [op1730] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s5, 40(sp)  # [op1730] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s6, 48(sp)  # [op1730] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s7, 56(sp)  # [op1730] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s8, 64(sp)  # [op1730] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s9, 72(sp)  # [op1730] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s10, 80(sp)  # [op1730] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s11, 88(sp)  # [op1730] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addi sp, sp, 224  # [op1730] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ret  # [op1730] /home/i_yinzida/compiler-a100-experiment-001/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    .size operator_entry, .-operator_entry
    .section .note.GNU-stack,"",@progbits
