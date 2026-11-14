# a100c emitted program: matmul_k32_fast_kernel
# source: tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py
# specialization identity: 2a88f075d4d8f751
# compiler revision: 933de52c1aedb43e
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
    # [peephole] removed 0 redundant vsetvli, 23 redundant li
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
ld t0, 112(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t0, 0(t0)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t0, 0(t0)  # [op1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd t0, 120(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t0, 112(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s8, 24(t0)  # [op3] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t0, 112(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
lwu t0, 40(t0)  # [op4] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t1, 112(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
lwu t1, 44(t1)  # [op5] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 112(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 0(t2)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 8(t2)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 8(t2)  # [op6] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw t2, t2, 0  # [op7] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 112(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 0(t2)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 8(t2)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 24(t2)  # [op8] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd t2, 128(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 128(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw t2, t2, 0  # [op9] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 112(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 0(t2)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 8(t2)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 40(t2)  # [op10] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw t2, t2, 0  # [op11] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 112(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 0(t2)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 8(t2)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 56(t2)  # [op12] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw t2, t2, 0  # [op13] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 112(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 0(t2)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 8(t2)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 72(t2)  # [op14] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw t2, t2, 0  # [op15] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd t2, 136(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 112(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 0(t2)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 8(t2)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 88(t2)  # [op16] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw t2, t2, 0  # [op17] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd t2, 144(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 112(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 0(t2)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 8(t2)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 104(t2)  # [op18] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw t2, t2, 0  # [op19] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 112(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 0(t2)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 8(t2)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 120(t2)  # [op20] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw t2, t2, 0  # [op21] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd t2, 152(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 112(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 0(t2)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 8(t2)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 136(t2)  # [op22] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw t2, t2, 0  # [op23] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 120(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s3, 0(t2)  # [op24] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 120(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s4, 56(t2)  # [op25] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 120(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s5, 112(t2)  # [op26] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t2, 128  # [op27] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 128(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
divu t2, s1, t2  # [op28] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd t2, 160(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t2, 1  # [op30] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 160(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mul t2, t2, s1  # [op31] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li s1, 2  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mul s9, t2, s1  # [op32] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t0  # [op33] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv s10, t1  # [op34] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t1, 0  # [op35] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lprog_head  # [op36] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lprog_head:  # block prog_head
slt t2, t0, s9  # [op37] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
bne t2, zero, .Lbrc38_true  # [op38] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd t1, 96(sp)  # [op38] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t1, t0  # [op38] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t0, 96(sp)  # [op38] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lprog_exit  # [op38] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lbrc38_true:  # [op38] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv s1, t1  # [op38] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t1, t0  # [op38] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lprog_body  # [op38] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lprog_body:  # block prog_body
li t0, 1  # [op39] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 160(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
divu t2, t1, t2  # [op40] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld a1, 160(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mul t2, t2, a1  # [op41] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sub a1, t1, t2  # [op42] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 160(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mul t0, t0, t2  # [op43] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
divu t2, t1, t0  # [op44] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li a2, 2  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
divu a2, t2, a2  # [op45] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li a3, 2  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mul a2, a2, a3  # [op46] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sub t2, t2, a2  # [op47] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li a2, 2  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mul t0, t0, a2  # [op48] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw t0, a1, 0  # [op49] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw a1, t2, 0  # [op50] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 160(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw t2, t2, 0  # [op51] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t2, 2  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addiw t2, t2, 0  # [op52] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 112(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 16(t2)  # [op53] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd t2, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 112(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 8(t2)  # [op54] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t2, 7  # [op55] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
sllw a2, t0, t2  # [op56] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
li t0, 0  # [op57] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk1_head  # [op58] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk1_head:  # block chunk1_head
li t2, 128  # [op59] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
slt t2, t0, t2  # [op60] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
bne t2, zero, .Lbrc61_true  # [op61] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op61] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, s1  # [op61] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk1_exit  # [op61] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lbrc61_true:  # [op61] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk1_body  # [op61] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk1_exit:  # block chunk1_exit
li t2, 523528  # [op62] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add t2, s1, t2  # [op63] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
lw a1, 0(t2)  # [op64] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t2, 0  # [op65] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv s1, t0  # [op66] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op66] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk2_head  # [op66] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk1_body:  # block chunk1_body
    # [peephole-dead-li] [op67] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli t2, x0, e32, m1, ta,ma  # [op68] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t2, 32  # [op69] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:32
vid.v v1  # [op71] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:32
vadd.vx v1, v1, t0  # [op72] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:32
vmv.v.x v2, a2  # [op73] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
vadd.vv v1, v2, v1  # [op74] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
vid.v v2  # [op75] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
vadd.vx v2, v2, t0  # [op76] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
vwadd.vx v4, v2, x0  # [op77] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
vsetvli a3, x0, e64, m2, ta,ma  # [op78] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
li a3, 4  # [op79] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
vmul.vx v2, v4, a3  # [op80] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
li a3, 0  # [op81] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
ld a4, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
add a3, a4, a3  # [op82] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
vsetvli a4, x0, e32, m1, ta,ma  # [op83] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
vsuxei64.v v1, (a3), v2  # [op84] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:40:14
li a3, 8  # [op85] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
sllw a3, a1, a3  # [op86] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
li a4, 32  # [op87] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add s1, s1, a4  # [op88] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t0, t2  # [op89] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t2, 523528  # [op90] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld a4, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add t2, a4, t2  # [op91] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sw a3, 0(t2)  # [op92] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk1_head  # [op93] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk2_head:  # block chunk2_head
li t2, 256  # [op94] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
slt t2, t0, t2  # [op95] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
bne t2, zero, .Lbrc96_true  # [op96] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op96] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, s1  # [op96] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk2_exit  # [op96] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lbrc96_true:  # [op96] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk2_body  # [op96] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk2_exit:  # block chunk2_exit
li t2, 0  # [op97] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv s1, t0  # [op98] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op98] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk3_head  # [op98] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk2_body:  # block chunk2_body
    # [peephole-dead-li] [op99] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli t2, x0, e32, m1, ta,ma  # [op100] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t2, 32  # [op101] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:32
vid.v v1  # [op103] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:32
vadd.vx v1, v1, t0  # [op104] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:32
vmv.v.x v2, a1  # [op105] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
vadd.vv v1, v2, v1  # [op106] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
vid.v v2  # [op107] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
vadd.vx v2, v2, t0  # [op108] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
vwadd.vx v4, v2, x0  # [op109] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
vsetvli a2, x0, e64, m2, ta,ma  # [op110] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
li a2, 4  # [op111] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
vmul.vx v2, v4, a2  # [op112] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
li a2, 512  # [op113] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
ld a3, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
add a2, a3, a2  # [op114] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
vsetvli a3, x0, e32, m1, ta,ma  # [op115] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
vsuxei64.v v1, (a2), v2  # [op116] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:41:14
li a2, 32  # [op117] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add s1, s1, a2  # [op118] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t0, t2  # [op119] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk2_head  # [op120] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk3_head:  # block chunk3_head
li t2, 32  # [op121] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
slt t2, t0, t2  # [op122] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
bne t2, zero, .Lbrc123_true  # [op123] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op123] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, s1  # [op123] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk3_exit  # [op123] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lbrc123_true:  # [op123] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk3_body  # [op123] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk3_exit:  # block chunk3_exit
li t2, 0  # [op124] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv s1, t0  # [op125] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk4_head  # [op125] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk3_body:  # block chunk3_body
    # [peephole-dead-li] [op126] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli t2, x0, e32, m1, ta,ma  # [op127] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t2, 32  # [op128] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
vid.v v1  # [op130] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
vadd.vx v1, v1, t0  # [op131] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
vid.v v2  # [op132] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
vadd.vx v2, v2, t0  # [op133] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
vwadd.vx v4, v2, x0  # [op134] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
vsetvli a1, x0, e64, m2, ta,ma  # [op135] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
li a1, 4  # [op136] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
vmul.vx v2, v4, a1  # [op137] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
li a1, 1536  # [op138] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
ld a2, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
add a1, a2, a1  # [op139] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
vsetvli a2, x0, e32, m1, ta,ma  # [op140] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
vsuxei64.v v1, (a1), v2  # [op141] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:42:14
li a1, 32  # [op142] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add s1, s1, a1  # [op143] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t0, t2  # [op144] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk3_head  # [op145] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk4_head:  # block chunk4_head
li t0, 128  # [op146] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
slt t0, t2, t0  # [op147] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
bne t0, zero, .Lbrc148_true  # [op148] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op148] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, s1  # [op148] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk4_exit  # [op148] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lbrc148_true:  # [op148] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk4_body  # [op148] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk4_exit:  # block chunk4_exit
li t2, 0  # [op149] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd t0, 96(sp)  # [op150] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op150] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 96(sp)  # [op150] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk5_head  # [op150] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk4_body:  # block chunk4_body
    # [peephole-dead-li] [op151] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli t0, x0, e32, m1, ta,ma  # [op152] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t0, 32  # [op153] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
ld a1, 136(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vmv.v.x v2, a1  # [op155] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vid.v v1  # [op156] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vadd.vx v1, v1, t2  # [op157] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vwadd.vx v4, v1, x0  # [op158] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vsetvli a1, x0, e64, m2, ta,ma  # [op159] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
li a1, 4  # [op160] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vmul.vx v4, v4, a1  # [op161] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
li a2, 0  # [op162] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
ld a3, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
add a2, a3, a2  # [op163] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vsetvli a3, x0, e32, m1, ta,ma  # [op164] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vluxei64.v v3, (a2), v4  # [op165] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vmul.vv v2, v3, v2  # [op166] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vwadd.vx v4, v1, x0  # [op167] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vsetvli a2, x0, e64, m2, ta,ma  # [op168] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vmul.vx v4, v4, a1  # [op169] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
li a1, 2176  # [op170] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
ld a2, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
add a1, a2, a1  # [op171] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vsetvli a2, x0, e32, m1, ta,ma  # [op172] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
vsuxei64.v v2, (a1), v4  # [op173] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:22
li a1, 32  # [op174] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add s1, s1, a1  # [op175] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t2, t0  # [op176] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t0  # [op177] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk4_head  # [op177] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk5_head:  # block chunk5_head
li s1, 32  # [op178] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
slt s1, t0, s1  # [op179] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
bne s1, zero, .Lbrc180_true  # [op180] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op180] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op180] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk5_exit  # [op180] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lbrc180_true:  # [op180] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk5_body  # [op180] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk5_exit:  # block chunk5_exit
li t2, 0  # [op181] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv s1, t0  # [op182] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk6_head  # [op182] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk5_body:  # block chunk5_body
    # [peephole-dead-li] [op183] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli s1, x0, e32, m1, ta,ma  # [op184] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li s1, 32  # [op185] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add s1, t2, s1  # [op186] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t2, 32  # [op187] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t0, t2  # [op188] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, s1  # [op190] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk5_head  # [op190] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk6_head:  # block chunk6_head
li t0, 4096  # [op191] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
slt t0, t2, t0  # [op192] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
bne t0, zero, .Lbrc193_true  # [op193] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op193] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, s1  # [op193] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk6_exit  # [op193] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lbrc193_true:  # [op193] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk6_body  # [op193] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk6_exit:  # block chunk6_exit
li t2, 0  # [op194] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv s1, t0  # [op195] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk7_head  # [op195] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk6_body:  # block chunk6_body
    # [peephole-dead-li] [op196] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli t0, x0, e32, m1, ta,ma  # [op197] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t0, 32  # [op198] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
vid.v v1  # [op200] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
vadd.vx v1, v1, t2  # [op201] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
vmv.v.x v2, t0  # [op202] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
vdiv.vv v1, v1, v2  # [op203] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
vwadd.vx v2, v1, x0  # [op204] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
vsetvli a1, x0, e64, m2, ta,ma  # [op205] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
li a1, 8  # [op206] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
vmul.vx v2, v2, a1  # [op207] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
li a1, 2688  # [op208] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
ld a2, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
add a1, a2, a1  # [op209] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
vluxei64.v v4, (a1), v2  # [op210] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
vsetvli a1, x0, e32, m1, ta,ma  # [op211] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:45:14
li a1, 32  # [op212] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add s1, s1, a1  # [op213] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t2, t0  # [op214] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t0  # [op215] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk6_head  # [op215] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk7_head:  # block chunk7_head
li t0, 32  # [op216] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
slt t0, t2, t0  # [op217] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
bne t0, zero, .Lbrc218_true  # [op218] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op218] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, s1  # [op218] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk7_exit  # [op218] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lbrc218_true:  # [op218] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk7_body  # [op218] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk7_exit:  # block chunk7_exit
li t2, 0  # [op219] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
sd t0, 96(sp)  # [op220] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op220] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t2, 96(sp)  # [op220] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk8_head  # [op220] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk7_body:  # block chunk7_body
    # [peephole-dead-li] [op221] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli t0, x0, e32, m1, ta,ma  # [op222] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t0, 32  # [op223] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
ld a1, 144(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vmv.v.x v2, a1  # [op225] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vid.v v1  # [op226] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vadd.vx v1, v1, t2  # [op227] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vwadd.vx v4, v1, x0  # [op228] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vsetvli a1, x0, e64, m2, ta,ma  # [op229] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
li a1, 4  # [op230] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vmul.vx v4, v4, a1  # [op231] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
li a2, 1536  # [op232] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
ld a3, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
add a2, a3, a2  # [op233] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vsetvli a3, x0, e32, m1, ta,ma  # [op234] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vluxei64.v v3, (a2), v4  # [op235] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vmul.vv v2, v3, v2  # [op236] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vwadd.vx v4, v1, x0  # [op237] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vsetvli a2, x0, e64, m2, ta,ma  # [op238] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vmul.vx v4, v4, a1  # [op239] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
li a1, 36608  # [op240] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
ld a2, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
add a1, a2, a1  # [op241] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vsetvli a2, x0, e32, m1, ta,ma  # [op242] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
vsuxei64.v v2, (a1), v4  # [op243] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:22
li a1, 32  # [op244] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add s1, s1, a1  # [op245] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t2, t0  # [op246] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t0  # [op247] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk7_head  # [op247] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk8_head:  # block chunk8_head
li s1, 256  # [op248] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
slt s1, t0, s1  # [op249] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
bne s1, zero, .Lbrc250_true  # [op250] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op250] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op250] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk8_exit  # [op250] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lbrc250_true:  # [op250] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk8_body  # [op250] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk8_exit:  # block chunk8_exit
li t2, 0  # [op251] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv s1, t0  # [op252] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op252] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk9_head  # [op252] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk8_body:  # block chunk8_body
    # [peephole-dead-li] [op253] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli s1, x0, e32, m1, ta,ma  # [op254] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li s1, 32  # [op255] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add s1, t2, s1  # [op256] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t2, 32  # [op257] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t0, t2  # [op258] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, s1  # [op260] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk8_head  # [op260] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk9_head:  # block chunk9_head
li t2, 8192  # [op261] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
slt t2, t0, t2  # [op262] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
bne t2, zero, .Lbrc263_true  # [op263] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op263] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, s1  # [op263] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk9_exit  # [op263] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lbrc263_true:  # [op263] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk9_body  # [op263] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk9_exit:  # block chunk9_exit
li t2, 0  # [op264] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv a1, t0  # [op265] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk10_head  # [op265] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk9_body:  # block chunk9_body
    # [peephole-dead-li] [op266] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli t2, x0, e32, m1, ta,ma  # [op267] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t2, 32  # [op268] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
vid.v v1  # [op270] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
vadd.vx v1, v1, t0  # [op271] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
li a1, 256  # [op272] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
vmv.v.x v2, a1  # [op273] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
vdiv.vv v1, v1, v2  # [op274] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
vwadd.vx v2, v1, x0  # [op275] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
vsetvli a1, x0, e64, m2, ta,ma  # [op276] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
li a1, 8  # [op277] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
vmul.vx v2, v2, a1  # [op278] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
li a1, 36736  # [op279] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
ld a2, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
add a1, a2, a1  # [op280] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
vluxei64.v v4, (a1), v2  # [op281] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
vsetvli a1, x0, e32, m1, ta,ma  # [op282] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:46:14
li a1, 32  # [op283] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add s1, s1, a1  # [op284] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t0, t2  # [op285] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk9_head  # [op286] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk10_head:  # block chunk10_head
li t0, 4096  # [op287] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
slt t0, t2, t0  # [op288] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
bne t0, zero, .Lbrc289_true  # [op289] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op289] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, a1  # [op289] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk10_exit  # [op289] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lbrc289_true:  # [op289] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk10_body  # [op289] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk10_exit:  # block chunk10_exit
li t2, 0  # [op290] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv a1, t0  # [op291] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk11_head  # [op291] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk10_body:  # block chunk10_body
li t0, 32  # [op292] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli t0, t0, e16, m1, ta,ma  # [op293] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t0, 32  # [op294] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli s1, x0, e32, m1, ta,ma  # [op295] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vid.v v1  # [op296] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vadd.vx v1, v1, t2  # [op297] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.v.x v2, t0  # [op298] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vdiv.vv v2, v1, v2  # [op299] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vwadd.vx v4, v2, x0  # [op300] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli s1, x0, e64, m2, ta,ma  # [op301] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li s1, 4  # [op302] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmul.vx v2, v4, s1  # [op303] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 2176  # [op304] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
ld a3, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, a3, a2  # [op305] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli a3, x0, e32, m1, ta,ma  # [op306] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vluxei64.v v4, (a2), v2  # [op307] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli a2, t0, e16, m1, ta,ma  # [op308] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli a2, x0, e32, m1, ta,ma  # [op309] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.v.x v2, t0  # [op310] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vrem.vv v1, v1, v2  # [op311] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vwadd.vx v2, v1, x0  # [op312] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli a2, x0, e64, m2, ta,ma  # [op313] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmul.vx v2, v2, s1  # [op314] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li s1, 1536  # [op315] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
ld a2, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add s1, a2, s1  # [op316] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli a2, x0, e32, m1, ta,ma  # [op317] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vluxei64.v v1, (s1), v2  # [op318] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli s1, t0, e16, m1, ta,ma  # [op319] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli s1, x0, e32, m1, ta,ma  # [op320] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vadd.vv v1, v4, v1  # [op321] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli s1, t0, e16, m1, ta,ma  # [op322] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li s1, 0  # [op323] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.v.x v2, s1  # [op324] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli s1, x0, e32, m1, ta,ma  # [op325] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vwadd.vx v2, v1, x0  # [op326] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli s1, x0, e64, m2, ta,ma  # [op327] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li s1, 2  # [op328] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmul.vx v2, v2, s1  # [op329] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli t0, t0, e16, m1, ta,ma  # [op330] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 0  # [op331] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li t0, 16  # [op332] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli t0, t0, e64, m2, ta,ma  # [op333] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s t0, v2  # [op334] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vid.v v4  # [op335] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmul.vx v4, v4, s1  # [op336] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vadd.vx v4, v4, t0  # [op337] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmsne.vv v4, v2, v4  # [op338] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vcpop.m a3, v4  # [op339] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, a2, a3  # [op340] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a3, s3, t0  # [op341] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vid.v v4  # [op342] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li t0, 16  # [op343] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vadd.vx v6, v4, t0  # [op344] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vrgather.vv v4, v2, v6  # [op345] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s t0, v4  # [op346] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vid.v v2  # [op347] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmul.vx v2, v2, s1  # [op348] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vadd.vx v2, v2, t0  # [op349] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmsne.vv v2, v4, v2  # [op350] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vcpop.m s1, v2  # [op351] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add s1, a2, s1  # [op352] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, s3, t0  # [op353] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
bne s1, zero, .Lbrc354_true  # [op354] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
j .Lngl.t1  # [op354] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
.Lbrc354_true:  # [op354] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
j .Lngl.e1  # [op354] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
.Lngl.t1:  # block ngl.t1
li t0, 523392  # [op355] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
ld s1, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add t0, s1, t0  # [op356] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li s1, 16  # [op357] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli s1, s1, e16, m1, ta,ma  # [op358] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vle16.v v1, 0(a3)  # [op359] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li s1, 0  # [op360] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add s1, t0, s1  # [op361] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vse16.v v1, 0(s1)  # [op362] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vle16.v v1, 0(a2)  # [op363] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li s1, 32  # [op364] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add s1, t0, s1  # [op365] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vse16.v v1, 0(s1)  # [op366] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li s1, 32  # [op367] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli s1, s1, e16, m1, ta,ma  # [op368] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vle16.v v1, 0(t0)  # [op369] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
j .Lngl.j1  # [op370] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
.Lngl.e1:  # block ngl.e1
li s1, 32  # [op371] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli t0, x0, e32, m1, ta,ma  # [op372] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vwadd.vx v2, v1, x0  # [op373] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli t0, x0, e64, m2, ta,ma  # [op374] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a2, 2  # [op375] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmul.vx v2, v2, a2  # [op376] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli t0, s1, e16, m1, ta,ma  # [op377] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li t0, 523392  # [op378] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
ld a3, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add t0, a3, t0  # [op379] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a3, 128  # [op380] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a3, t0, a3  # [op381] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli a3, x0, e64, m2, ta,ma  # [op382] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vadd.vx v2, v2, s3  # [op383] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a3, v2  # [op384] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a4, 0  # [op385] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a4, t0, a4  # [op386] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a3, 0(a3)  # [op387] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a3, 0(a4)  # [op388] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op389] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a3, v2  # [op390] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a2, t0, a2  # [op391] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a3, 0(a3)  # [op392] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a3, 0(a2)  # [op393] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op394] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a2, v2  # [op395] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a3, 4  # [op396] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a3, t0, a3  # [op397] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a2, 0(a2)  # [op398] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a2, 0(a3)  # [op399] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op400] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a2, v2  # [op401] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a3, 6  # [op402] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a3, t0, a3  # [op403] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a2, 0(a2)  # [op404] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a2, 0(a3)  # [op405] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op406] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a2, v2  # [op407] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a3, 8  # [op408] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a3, t0, a3  # [op409] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a2, 0(a2)  # [op410] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a2, 0(a3)  # [op411] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op412] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a2, v2  # [op413] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a3, 10  # [op414] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a3, t0, a3  # [op415] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a2, 0(a2)  # [op416] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a2, 0(a3)  # [op417] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op418] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a2, v2  # [op419] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a3, 12  # [op420] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a3, t0, a3  # [op421] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a2, 0(a2)  # [op422] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a2, 0(a3)  # [op423] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op424] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a2, v2  # [op425] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a3, 14  # [op426] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a3, t0, a3  # [op427] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a2, 0(a2)  # [op428] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a2, 0(a3)  # [op429] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op430] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a2, v2  # [op431] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a3, 16  # [op432] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a3, t0, a3  # [op433] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a2, 0(a2)  # [op434] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a2, 0(a3)  # [op435] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op436] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a2, v2  # [op437] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a3, 18  # [op438] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a3, t0, a3  # [op439] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a2, 0(a2)  # [op440] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a2, 0(a3)  # [op441] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op442] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a2, v2  # [op443] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a3, 20  # [op444] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a3, t0, a3  # [op445] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a2, 0(a2)  # [op446] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a2, 0(a3)  # [op447] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op448] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a2, v2  # [op449] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a3, 22  # [op450] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a3, t0, a3  # [op451] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a2, 0(a2)  # [op452] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a2, 0(a3)  # [op453] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op454] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a2, v2  # [op455] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a3, 24  # [op456] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a3, t0, a3  # [op457] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a2, 0(a2)  # [op458] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a2, 0(a3)  # [op459] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op460] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a2, v2  # [op461] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a3, 26  # [op462] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a3, t0, a3  # [op463] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a2, 0(a2)  # [op464] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a2, 0(a3)  # [op465] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op466] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a2, v2  # [op467] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a3, 28  # [op468] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a3, t0, a3  # [op469] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a2, 0(a2)  # [op470] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a2, 0(a3)  # [op471] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op472] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a2, v2  # [op473] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a3, 30  # [op474] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a3, t0, a3  # [op475] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a2, 0(a2)  # [op476] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a2, 0(a3)  # [op477] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op478] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a2, v2  # [op479] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a3, 32  # [op480] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a3, t0, a3  # [op481] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a2, 0(a2)  # [op482] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a2, 0(a3)  # [op483] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op484] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a2, v2  # [op485] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a3, 34  # [op486] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a3, t0, a3  # [op487] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a2, 0(a2)  # [op488] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a2, 0(a3)  # [op489] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op490] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a2, v2  # [op491] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a3, 36  # [op492] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a3, t0, a3  # [op493] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a2, 0(a2)  # [op494] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a2, 0(a3)  # [op495] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op496] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a2, v2  # [op497] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a3, 38  # [op498] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a3, t0, a3  # [op499] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a2, 0(a2)  # [op500] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a2, 0(a3)  # [op501] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op502] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a2, v2  # [op503] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a3, 40  # [op504] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a3, t0, a3  # [op505] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a2, 0(a2)  # [op506] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a2, 0(a3)  # [op507] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op508] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a2, v2  # [op509] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a3, 42  # [op510] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a3, t0, a3  # [op511] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a2, 0(a2)  # [op512] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a2, 0(a3)  # [op513] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op514] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a2, v2  # [op515] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a3, 44  # [op516] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a3, t0, a3  # [op517] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a2, 0(a2)  # [op518] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a2, 0(a3)  # [op519] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op520] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a2, v2  # [op521] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a3, 46  # [op522] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a3, t0, a3  # [op523] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a2, 0(a2)  # [op524] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a2, 0(a3)  # [op525] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op526] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a2, v2  # [op527] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a3, 48  # [op528] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a3, t0, a3  # [op529] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a2, 0(a2)  # [op530] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a2, 0(a3)  # [op531] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op532] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a2, v2  # [op533] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a3, 50  # [op534] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a3, t0, a3  # [op535] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a2, 0(a2)  # [op536] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a2, 0(a3)  # [op537] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op538] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a2, v2  # [op539] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a3, 52  # [op540] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a3, t0, a3  # [op541] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a2, 0(a2)  # [op542] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a2, 0(a3)  # [op543] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op544] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a2, v2  # [op545] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a3, 54  # [op546] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a3, t0, a3  # [op547] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a2, 0(a2)  # [op548] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a2, 0(a3)  # [op549] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op550] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a2, v2  # [op551] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a3, 56  # [op552] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a3, t0, a3  # [op553] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a2, 0(a2)  # [op554] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a2, 0(a3)  # [op555] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op556] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a2, v2  # [op557] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a3, 58  # [op558] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a3, t0, a3  # [op559] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a2, 0(a2)  # [op560] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a2, 0(a3)  # [op561] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op562] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a2, v2  # [op563] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a3, 60  # [op564] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a3, t0, a3  # [op565] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a2, 0(a2)  # [op566] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a2, 0(a3)  # [op567] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op568] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vmv.x.s a2, v2  # [op569] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a3, 62  # [op570] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add a3, t0, a3  # [op571] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
lhu a2, 0(a2)  # [op572] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
sh a2, 0(a3)  # [op573] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vslidedown.vi v2, v2, 1  # [op574] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli s1, s1, e16, m1, ta,ma  # [op575] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vle16.v v1, 0(t0)  # [op576] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
j .Lngl.j1  # [op577] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
.Lngl.j1:  # block ngl.j1
li t0, 32  # [op578] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vsetvli s1, t0, e16, m1, ta,ma  # [op579] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li s1, 103552  # [op580] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
ld a2, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add s1, a2, s1  # [op581] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
mv a2, t2  # [op582] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li a3, 2  # [op583] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
mul a2, a2, a3  # [op584] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
add s1, s1, a2  # [op585] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
vse16.v v1, 0(s1)  # [op586] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:49:9
li s1, 32  # [op587] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add s1, a1, s1  # [op588] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t2, t0  # [op589] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t0  # [op590] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv a1, s1  # [op590] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk10_head  # [op590] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk11_head:  # block chunk11_head
li t0, 8192  # [op591] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
slt t0, t2, t0  # [op592] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
bne t0, zero, .Lbrc593_true  # [op593] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op593] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, a1  # [op593] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk11_exit  # [op593] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lbrc593_true:  # [op593] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk11_body  # [op593] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk11_exit:  # block chunk11_exit
li t2, 0  # [op594] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv s1, t0  # [op595] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t2  # [op595] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk12_head  # [op595] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk11_body:  # block chunk11_body
li t0, 32  # [op596] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli t0, t0, e16, m1, ta,ma  # [op597] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t0, 32  # [op598] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli s1, x0, e32, m1, ta,ma  # [op599] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vid.v v1  # [op600] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vadd.vx v1, v1, t2  # [op601] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li s1, 256  # [op602] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.v.x v2, s1  # [op603] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vdiv.vv v2, v1, v2  # [op604] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vwadd.vx v4, v2, x0  # [op605] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli a2, x0, e64, m2, ta,ma  # [op606] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 4  # [op607] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmul.vx v2, v4, a2  # [op608] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 36608  # [op609] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
ld a4, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, a4, a3  # [op610] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli a4, x0, e32, m1, ta,ma  # [op611] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vluxei64.v v4, (a3), v2  # [op612] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli a3, t0, e16, m1, ta,ma  # [op613] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli a3, x0, e32, m1, ta,ma  # [op614] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.v.x v2, s1  # [op615] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vrem.vv v1, v1, v2  # [op616] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vwadd.vx v2, v1, x0  # [op617] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli s1, x0, e64, m2, ta,ma  # [op618] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmul.vx v2, v2, a2  # [op619] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li s1, 512  # [op620] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
ld a2, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add s1, a2, s1  # [op621] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli a2, x0, e32, m1, ta,ma  # [op622] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vluxei64.v v1, (s1), v2  # [op623] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli s1, t0, e16, m1, ta,ma  # [op624] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli s1, x0, e32, m1, ta,ma  # [op625] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vadd.vv v1, v4, v1  # [op626] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli s1, t0, e16, m1, ta,ma  # [op627] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li s1, 0  # [op628] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.v.x v2, s1  # [op629] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli s1, x0, e32, m1, ta,ma  # [op630] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vwadd.vx v2, v1, x0  # [op631] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli s1, x0, e64, m2, ta,ma  # [op632] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li s1, 2  # [op633] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmul.vx v2, v2, s1  # [op634] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli t0, t0, e16, m1, ta,ma  # [op635] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 0  # [op636] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li t0, 16  # [op637] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli t0, t0, e64, m2, ta,ma  # [op638] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s t0, v2  # [op639] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vid.v v4  # [op640] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmul.vx v4, v4, s1  # [op641] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vadd.vx v4, v4, t0  # [op642] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmsne.vv v4, v2, v4  # [op643] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vcpop.m a3, v4  # [op644] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, a2, a3  # [op645] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, s4, t0  # [op646] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vid.v v4  # [op647] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li t0, 16  # [op648] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vadd.vx v6, v4, t0  # [op649] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vrgather.vv v4, v2, v6  # [op650] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s t0, v4  # [op651] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vid.v v2  # [op652] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmul.vx v2, v2, s1  # [op653] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vadd.vx v2, v2, t0  # [op654] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmsne.vv v2, v4, v2  # [op655] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vcpop.m s1, v2  # [op656] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add s1, a2, s1  # [op657] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, s4, t0  # [op658] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
bne s1, zero, .Lbrc659_true  # [op659] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
j .Lngl.t2  # [op659] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
.Lbrc659_true:  # [op659] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
j .Lngl.e2  # [op659] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
.Lngl.t2:  # block ngl.t2
li t0, 523392  # [op660] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
ld s1, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add t0, s1, t0  # [op661] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li s1, 16  # [op662] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli s1, s1, e16, m1, ta,ma  # [op663] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vle16.v v1, 0(a3)  # [op664] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li s1, 0  # [op665] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add s1, t0, s1  # [op666] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vse16.v v1, 0(s1)  # [op667] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vle16.v v1, 0(a2)  # [op668] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li s1, 32  # [op669] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add s1, t0, s1  # [op670] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vse16.v v1, 0(s1)  # [op671] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li s1, 32  # [op672] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli s1, s1, e16, m1, ta,ma  # [op673] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vle16.v v1, 0(t0)  # [op674] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
j .Lngl.j2  # [op675] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
.Lngl.e2:  # block ngl.e2
li s1, 32  # [op676] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli t0, x0, e32, m1, ta,ma  # [op677] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vwadd.vx v2, v1, x0  # [op678] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli t0, x0, e64, m2, ta,ma  # [op679] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a2, 2  # [op680] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmul.vx v2, v2, a2  # [op681] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli t0, s1, e16, m1, ta,ma  # [op682] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li t0, 523392  # [op683] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
ld a3, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add t0, a3, t0  # [op684] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 128  # [op685] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op686] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli a3, x0, e64, m2, ta,ma  # [op687] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vadd.vx v2, v2, s4  # [op688] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a3, v2  # [op689] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a4, 0  # [op690] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a4, t0, a4  # [op691] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a3, 0(a3)  # [op692] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a3, 0(a4)  # [op693] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op694] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a3, v2  # [op695] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a2, t0, a2  # [op696] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a3, 0(a3)  # [op697] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a3, 0(a2)  # [op698] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op699] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op700] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 4  # [op701] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op702] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op703] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op704] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op705] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op706] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 6  # [op707] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op708] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op709] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op710] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op711] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op712] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 8  # [op713] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op714] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op715] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op716] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op717] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op718] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 10  # [op719] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op720] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op721] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op722] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op723] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op724] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 12  # [op725] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op726] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op727] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op728] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op729] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op730] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 14  # [op731] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op732] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op733] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op734] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op735] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op736] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 16  # [op737] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op738] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op739] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op740] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op741] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op742] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 18  # [op743] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op744] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op745] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op746] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op747] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op748] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 20  # [op749] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op750] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op751] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op752] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op753] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op754] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 22  # [op755] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op756] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op757] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op758] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op759] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op760] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 24  # [op761] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op762] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op763] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op764] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op765] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op766] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 26  # [op767] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op768] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op769] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op770] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op771] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op772] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 28  # [op773] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op774] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op775] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op776] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op777] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op778] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 30  # [op779] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op780] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op781] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op782] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op783] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op784] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 32  # [op785] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op786] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op787] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op788] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op789] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op790] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 34  # [op791] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op792] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op793] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op794] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op795] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op796] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 36  # [op797] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op798] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op799] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op800] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op801] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op802] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 38  # [op803] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op804] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op805] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op806] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op807] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op808] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 40  # [op809] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op810] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op811] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op812] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op813] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op814] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 42  # [op815] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op816] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op817] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op818] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op819] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op820] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 44  # [op821] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op822] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op823] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op824] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op825] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op826] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 46  # [op827] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op828] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op829] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op830] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op831] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op832] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 48  # [op833] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op834] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op835] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op836] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op837] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op838] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 50  # [op839] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op840] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op841] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op842] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op843] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op844] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 52  # [op845] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op846] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op847] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op848] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op849] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op850] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 54  # [op851] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op852] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op853] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op854] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op855] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op856] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 56  # [op857] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op858] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op859] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op860] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op861] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op862] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 58  # [op863] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op864] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op865] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op866] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op867] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op868] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 60  # [op869] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op870] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op871] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op872] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op873] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vmv.x.s a2, v2  # [op874] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 62  # [op875] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add a3, t0, a3  # [op876] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
lhu a2, 0(a2)  # [op877] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
sh a2, 0(a3)  # [op878] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vslidedown.vi v2, v2, 1  # [op879] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli s1, s1, e16, m1, ta,ma  # [op880] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vle16.v v1, 0(t0)  # [op881] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
j .Lngl.j2  # [op882] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
.Lngl.j2:  # block ngl.j2
li t0, 32  # [op883] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vsetvli s1, t0, e16, m1, ta,ma  # [op884] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li s1, 111744  # [op885] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
ld a2, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add s1, a2, s1  # [op886] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
mv a2, t2  # [op887] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li a3, 2  # [op888] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
mul a2, a2, a3  # [op889] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
add s1, s1, a2  # [op890] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
vse16.v v1, 0(s1)  # [op891] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:50:9
li s1, 32  # [op892] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add s1, a1, s1  # [op893] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t2, t0  # [op894] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t0  # [op895] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv a1, s1  # [op895] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk11_head  # [op895] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk12_head:  # block chunk12_head
li t2, 32768  # [op896] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
slt t2, t0, t2  # [op897] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
bne t2, zero, .Lbrc898_true  # [op898] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t1  # [op898] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv s11, s1  # [op898] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk12_exit  # [op898] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lbrc898_true:  # [op898] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk12_body  # [op898] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk12_exit:  # block chunk12_exit
li t0, 522880  # [op899] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t2, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t0, t2, t0  # [op900] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sd t0, 176(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t0, 128  # [op901] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t2, 176(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a2, t2, t0  # [op902] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t0, 256  # [op903] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t2, 176(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a3, t2, t0  # [op904] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t0, 8  # [op905] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t0, t0, e32, m1, ta,ma  # [op906] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vid.v v1  # [op907] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vid.v v2  # [op908] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-dead-li] [op909] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t0, x0, e16, m1, ta,ma  # [op910] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t0, 0  # [op911] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v3, t0  # [op912] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v4, t0  # [op913] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-li] [op914] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t3, 512  # [op915] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mv s2, t0  # [op916] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lmtile13.head  # [op916] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lchunk12_body:  # block chunk12_body
    # [peephole-dead-li] [op917] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli t2, x0, e32, m1, ta,ma  # [op918] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li a1, 0  # [op919] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
li t2, 32  # [op920] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
vmv.v.x v1, a1  # [op922] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
vid.v v2  # [op923] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
vadd.vx v2, v2, t0  # [op924] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
vwadd.vx v4, v2, x0  # [op925] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
vsetvli a1, x0, e64, m2, ta,ma  # [op926] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
li a1, 4  # [op927] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
vmul.vx v2, v4, a1  # [op928] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
li a1, 128128  # [op929] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
ld a2, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
add a1, a2, a1  # [op930] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
vsetvli a2, x0, e32, m1, ta,ma  # [op931] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
vsuxei64.v v1, (a1), v2  # [op932] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:53:11
li a1, 32  # [op933] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add s1, s1, a1  # [op934] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t0, t2  # [op935] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk12_head  # [op936] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lmtile13.head:  # block mtile13.head
slt t0, s2, t3  # [op937] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
bne t0, zero, .Lbrc938_true  # [op938] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mv t0, s2  # [op938] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lmtile13.exit  # [op938] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lbrc938_true:  # [op938] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lmtile13.body  # [op938] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lmtile13.body:  # block mtile13.body
li s6, 32  # [op939] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
divu t0, s2, s6  # [op940] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t2, t0, s6  # [op941] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub s1, s2, t2  # [op942] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t2, 8  # [op943] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t0, t0, t2  # [op944] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t2, s1, t2  # [op945] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sd t2, 192(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-dead-li] [op946] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t2, x0, e32, m2, ta,ma  # [op947] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t2, 0  # [op948] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v6, t2  # [op949] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-li] [op950] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lmk14.head  # [op951] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lmtile13.exit:  # block mtile13.exit
li t0, 0  # [op952] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t0  # [op953] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv s1, s11  # [op953] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk18_head  # [op953] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lmk14.head:  # block mk14.head
slt s1, t2, s6  # [op954] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
bne s1, zero, .Lbrc955_true  # [op955] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lmk14.exit  # [op955] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lbrc955_true:  # [op955] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lmk14.body  # [op955] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lmk14.body:  # block mk14.body
li s1, 32  # [op956] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub s1, s1, t2  # [op957] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sd s1, 184(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s1, 8  # [op958] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a1, t0, s1  # [op959] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a4, 129  # [op960] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt a1, a1, a4  # [op961] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a4, 1  # [op962] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a5, 184(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a4, a5, a4  # [op963] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt s1, s1, a4  # [op964] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and s1, a1, s1  # [op965] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
bne s1, zero, .Lbrc966_true  # [op966] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Ltaf15.else  # [op966] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lbrc966_true:  # [op966] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Ltaf15.then  # [op966] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lmk14.exit:  # block mk14.exit
    # [peephole-dead-li] [op967] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t2, x0, e32, m2, ta,ma  # [op968] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse32.v v6, 0(a3)  # [op969] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t2, 0  # [op970] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a1, t0, t2  # [op971] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s1, 128  # [op972] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt a5, a1, s1  # [op973] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a4, 256  # [op974] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a6, 192(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub a6, a4, a6  # [op975] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub a5, t2, a5  # [op976] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and a5, a6, a5  # [op977] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw a5, a5, 0  # [op978] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a6, 8  # [op979] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli a6, a6, e32, m1, ta,ma  # [op980] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, a5  # [op981] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v2, v5  # [op982] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op983] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a5, a3, t2  # [op984] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle32.v v5, 0(a5)  # [op985] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a5, 259200  # [op986] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a6, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a7, a6, a5  # [op987] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a6, 1024  # [op988] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul a1, a1, a6  # [op989] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a7, a7, a1  # [op990] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a1, 4  # [op991] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld s6, 192(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s6, s6, a1  # [op992] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a7, a7, s6  # [op993] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse32.v v5, 0(a7), v0.t  # [op994] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a7, 1  # [op995] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t0, a7  # [op996] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt s7, s6, s1  # [op997] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 192(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, a4, t4  # [op998] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub s7, t2, s7  # [op999] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and s7, t4, s7  # [op1000] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw s7, s7, 0  # [op1001] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, s7  # [op1002] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v2, v5  # [op1003] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1004] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s7, 32  # [op1005] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, a3, s7  # [op1006] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle32.v v5, 0(s7)  # [op1007] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld s7, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, s7, a5  # [op1008] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s6, s6, a6  # [op1009] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s7, s6  # [op1010] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld s7, 192(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s7, s7, a1  # [op1011] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s6, s7  # [op1012] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse32.v v5, 0(s6), v0.t  # [op1013] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 2  # [op1014] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t0, s6  # [op1015] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt s7, s6, s1  # [op1016] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 192(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, a4, t4  # [op1017] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub s7, t2, s7  # [op1018] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and s7, t4, s7  # [op1019] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw s7, s7, 0  # [op1020] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, s7  # [op1021] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v2, v5  # [op1022] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1023] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s7, 64  # [op1024] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, a3, s7  # [op1025] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle32.v v5, 0(s7)  # [op1026] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld s7, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, s7, a5  # [op1027] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s6, s6, a6  # [op1028] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s7, s6  # [op1029] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld s7, 192(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s7, s7, a1  # [op1030] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s6, s7  # [op1031] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse32.v v5, 0(s6), v0.t  # [op1032] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 3  # [op1033] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t0, s6  # [op1034] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt s7, s6, s1  # [op1035] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 192(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, a4, t4  # [op1036] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub s7, t2, s7  # [op1037] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and s7, t4, s7  # [op1038] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw s7, s7, 0  # [op1039] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, s7  # [op1040] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v2, v5  # [op1041] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1042] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s7, 96  # [op1043] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, a3, s7  # [op1044] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle32.v v5, 0(s7)  # [op1045] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld s7, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, s7, a5  # [op1046] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s6, s6, a6  # [op1047] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s7, s6  # [op1048] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld s7, 192(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s7, s7, a1  # [op1049] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s6, s7  # [op1050] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse32.v v5, 0(s6), v0.t  # [op1051] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t0, a1  # [op1052] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt s7, s6, s1  # [op1053] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 192(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, a4, t4  # [op1054] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub s7, t2, s7  # [op1055] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and s7, t4, s7  # [op1056] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw s7, s7, 0  # [op1057] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, s7  # [op1058] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v2, v5  # [op1059] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1060] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, a3, s1  # [op1061] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle32.v v5, 0(s7)  # [op1062] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld s7, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, s7, a5  # [op1063] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s6, s6, a6  # [op1064] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s7, s6  # [op1065] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld s7, 192(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s7, s7, a1  # [op1066] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s6, s7  # [op1067] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse32.v v5, 0(s6), v0.t  # [op1068] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 5  # [op1069] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t0, s6  # [op1070] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt s7, s6, s1  # [op1071] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 192(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, a4, t4  # [op1072] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub s7, t2, s7  # [op1073] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and s7, t4, s7  # [op1074] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw s7, s7, 0  # [op1075] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, s7  # [op1076] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v2, v5  # [op1077] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1078] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s7, 160  # [op1079] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, a3, s7  # [op1080] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle32.v v5, 0(s7)  # [op1081] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld s7, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, s7, a5  # [op1082] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s6, s6, a6  # [op1083] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s7, s6  # [op1084] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld s7, 192(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s7, s7, a1  # [op1085] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s6, s7  # [op1086] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse32.v v5, 0(s6), v0.t  # [op1087] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 6  # [op1088] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, t0, s6  # [op1089] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt s7, s6, s1  # [op1090] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 192(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, a4, t4  # [op1091] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub s7, t2, s7  # [op1092] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and s7, t4, s7  # [op1093] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw s7, s7, 0  # [op1094] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, s7  # [op1095] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v2, v5  # [op1096] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1097] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s7, 192  # [op1098] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, a3, s7  # [op1099] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle32.v v5, 0(s7)  # [op1100] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld s7, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, s7, a5  # [op1101] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s6, s6, a6  # [op1102] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s7, s6  # [op1103] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld s7, 192(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s7, s7, a1  # [op1104] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s6, s6, s7  # [op1105] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse32.v v5, 0(s6), v0.t  # [op1106] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s6, 7  # [op1107] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t0, t0, s6  # [op1108] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt s1, t0, s1  # [op1109] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld s6, 192(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub a4, a4, s6  # [op1110] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t2, t2, s1  # [op1111] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t2, a4, t2  # [op1112] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw t2, t2, 0  # [op1113] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, t2  # [op1114] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v2, v5  # [op1115] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1116] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t2, 224  # [op1117] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t2, a3, t2  # [op1118] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle32.v v5, 0(t2)  # [op1119] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t2, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t2, t2, a5  # [op1120] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t0, t0, a6  # [op1121] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t0, t2, t0  # [op1122] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t2, 192(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t2, t2, a1  # [op1123] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t0, t0, t2  # [op1124] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse32.v v5, 0(t0), v0.t  # [op1125] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t0, s2, a7  # [op1126] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mv s2, t0  # [op1127] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lmtile13.head  # [op1127] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Ltaf15.then:  # block taf15.then
li s1, 8  # [op1128] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli s1, s1, e16, m1, ta,ma  # [op1129] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s1, 103552  # [op1130] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a1, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a1, a1, s1  # [op1131] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s1, 64  # [op1132] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul a4, t0, s1  # [op1133] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a1, a1, a4  # [op1134] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a4, 2  # [op1135] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul a4, t2, a4  # [op1136] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a1, a1, a4  # [op1137] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(a1)  # [op1138] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a4, 176(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a4)  # [op1139] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a4, a1, s1  # [op1140] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a1, 16  # [op1141] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a5, 176(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a5, a5, a1  # [op1142] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(a4)  # [op1143] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a5)  # [op1144] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a4, a4, s1  # [op1145] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a5, a5, a1  # [op1146] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(a4)  # [op1147] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a5)  # [op1148] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a4, a4, s1  # [op1149] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a5, a5, a1  # [op1150] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(a4)  # [op1151] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a5)  # [op1152] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a4, a4, s1  # [op1153] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a5, a5, a1  # [op1154] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(a4)  # [op1155] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a5)  # [op1156] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a4, a4, s1  # [op1157] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a5, a5, a1  # [op1158] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(a4)  # [op1159] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a5)  # [op1160] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a4, a4, s1  # [op1161] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a5, a5, a1  # [op1162] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(a4)  # [op1163] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a5)  # [op1164] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s1, a4, s1  # [op1165] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a1, a5, a1  # [op1166] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(s1)  # [op1167] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a1)  # [op1168] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Ltaf15.join  # [op1169] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Ltaf15.else:  # block taf15.else
li s1, 0  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a5, t0, s1  # [op1171] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a6, 128  # [op1172] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt a1, a5, a6  # [op1173] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s1, 8  # [op1174] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a4, 184(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt a4, a4, s1  # [op1175] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a7, 0  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub a4, a7, a4  # [op1176] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a7, 184(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub a7, s1, a7  # [op1177] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and a4, a7, a4  # [op1178] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a7, 184(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a4, a7, a4  # [op1179] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a7, 0  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub a1, a7, a1  # [op1180] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and a1, a4, a1  # [op1181] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw a4, a1, 0  # [op1182] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a1, 8  # [op1183] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli a7, a1, e32, m1, ta,ma  # [op1184] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, a4  # [op1185] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v1, v5  # [op1186] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1187] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a7, 103552  # [op1188] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a4, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, a4, a7  # [op1189] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a4, 64  # [op1190] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul a5, a5, a4  # [op1191] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, s7, a5  # [op1192] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a5, 2  # [op1193] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t4, t2, a5  # [op1194] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, s7, t4  # [op1195] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t4, a1, e16, m1, ta,ma  # [op1196] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(s7), v0.t  # [op1197] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmerge.vvm v5, v3, v5, v0  # [op1198] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld s7, 176(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t4, 0  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, s7, t4  # [op1199] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(s7)  # [op1200] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s7, 1  # [op1201] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, t0, s7  # [op1202] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t4, s7, a6  # [op1203] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t5, 184(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t5, t5, s1  # [op1204] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t6, 0  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t5, t6, t5  # [op1205] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t6, 184(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t6, s1, t6  # [op1206] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t5, t6, t5  # [op1207] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t6, 184(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t5, t6, t5  # [op1208] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t6, 0  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, t6, t4  # [op1209] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t4, t5, t4  # [op1210] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw t4, t4, 0  # [op1211] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t5, a1, e32, m1, ta,ma  # [op1212] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, t4  # [op1213] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v1, v5  # [op1214] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1215] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t4, t4, a7  # [op1216] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s7, s7, a4  # [op1217] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, t4, s7  # [op1218] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t4, t2, a5  # [op1219] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, s7, t4  # [op1220] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t4, a1, e16, m1, ta,ma  # [op1221] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(s7), v0.t  # [op1222] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmerge.vvm v5, v3, v5, v0  # [op1223] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s7, 16  # [op1224] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 176(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, t4, s7  # [op1225] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(s7)  # [op1226] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, t0, a5  # [op1227] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t4, s7, a6  # [op1228] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t5, 184(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t5, t5, s1  # [op1229] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-li] [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t5, t6, t5  # [op1230] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t6, 184(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t6, s1, t6  # [op1231] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t5, t6, t5  # [op1232] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t6, 184(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t5, t6, t5  # [op1233] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t6, 0  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, t6, t4  # [op1234] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t4, t5, t4  # [op1235] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw t4, t4, 0  # [op1236] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t5, a1, e32, m1, ta,ma  # [op1237] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, t4  # [op1238] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v1, v5  # [op1239] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1240] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t4, t4, a7  # [op1241] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s7, s7, a4  # [op1242] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, t4, s7  # [op1243] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t4, t2, a5  # [op1244] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, s7, t4  # [op1245] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t4, a1, e16, m1, ta,ma  # [op1246] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(s7), v0.t  # [op1247] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmerge.vvm v5, v3, v5, v0  # [op1248] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s7, 32  # [op1249] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 176(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, t4, s7  # [op1250] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(s7)  # [op1251] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s7, 3  # [op1252] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, t0, s7  # [op1253] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t4, s7, a6  # [op1254] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t5, 184(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t5, t5, s1  # [op1255] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-li] [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t5, t6, t5  # [op1256] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t6, 184(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t6, s1, t6  # [op1257] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t5, t6, t5  # [op1258] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t6, 184(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t5, t6, t5  # [op1259] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t6, 0  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, t6, t4  # [op1260] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t4, t5, t4  # [op1261] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw t4, t4, 0  # [op1262] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t5, a1, e32, m1, ta,ma  # [op1263] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, t4  # [op1264] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v1, v5  # [op1265] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1266] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t4, t4, a7  # [op1267] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s7, s7, a4  # [op1268] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, t4, s7  # [op1269] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t4, t2, a5  # [op1270] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, s7, t4  # [op1271] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t4, a1, e16, m1, ta,ma  # [op1272] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(s7), v0.t  # [op1273] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmerge.vvm v5, v3, v5, v0  # [op1274] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s7, 48  # [op1275] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 176(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, t4, s7  # [op1276] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(s7)  # [op1277] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s7, 4  # [op1278] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, t0, s7  # [op1279] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t4, s7, a6  # [op1280] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t5, 184(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t5, t5, s1  # [op1281] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-li] [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t5, t6, t5  # [op1282] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t6, 184(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t6, s1, t6  # [op1283] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t5, t6, t5  # [op1284] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t6, 184(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t5, t6, t5  # [op1285] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t6, 0  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, t6, t4  # [op1286] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t4, t5, t4  # [op1287] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw t4, t4, 0  # [op1288] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t5, a1, e32, m1, ta,ma  # [op1289] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, t4  # [op1290] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v1, v5  # [op1291] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1292] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t4, t4, a7  # [op1293] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s7, s7, a4  # [op1294] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, t4, s7  # [op1295] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t4, t2, a5  # [op1296] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, s7, t4  # [op1297] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t4, a1, e16, m1, ta,ma  # [op1298] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(s7), v0.t  # [op1299] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmerge.vvm v5, v3, v5, v0  # [op1300] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld s7, 176(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, s7, a4  # [op1301] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(s7)  # [op1302] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s7, 5  # [op1303] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, t0, s7  # [op1304] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t4, s7, a6  # [op1305] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t5, 184(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t5, t5, s1  # [op1306] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-li] [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t5, t6, t5  # [op1307] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t6, 184(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t6, s1, t6  # [op1308] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t5, t6, t5  # [op1309] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t6, 184(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t5, t6, t5  # [op1310] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t6, 0  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, t6, t4  # [op1311] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t4, t5, t4  # [op1312] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw t4, t4, 0  # [op1313] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t5, a1, e32, m1, ta,ma  # [op1314] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, t4  # [op1315] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v1, v5  # [op1316] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1317] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t4, t4, a7  # [op1318] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s7, s7, a4  # [op1319] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, t4, s7  # [op1320] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t4, t2, a5  # [op1321] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, s7, t4  # [op1322] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t4, a1, e16, m1, ta,ma  # [op1323] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(s7), v0.t  # [op1324] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmerge.vvm v5, v3, v5, v0  # [op1325] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s7, 80  # [op1326] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 176(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, t4, s7  # [op1327] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(s7)  # [op1328] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s7, 6  # [op1329] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, t0, s7  # [op1330] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t4, s7, a6  # [op1331] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t5, 184(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t5, t5, s1  # [op1332] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
    # [peephole-li] [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t5, t6, t5  # [op1333] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t6, 184(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t6, s1, t6  # [op1334] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t5, t6, t5  # [op1335] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t6, 184(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t5, t6, t5  # [op1336] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t6, 0  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, t6, t4  # [op1337] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and t4, t5, t4  # [op1338] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw t4, t4, 0  # [op1339] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t5, a1, e32, m1, ta,ma  # [op1340] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, t4  # [op1341] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v1, v5  # [op1342] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1343] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t4, t4, a7  # [op1344] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s7, s7, a4  # [op1345] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, t4, s7  # [op1346] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul t4, t2, a5  # [op1347] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, s7, t4  # [op1348] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli t4, a1, e16, m1, ta,ma  # [op1349] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(s7), v0.t  # [op1350] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmerge.vvm v5, v3, v5, v0  # [op1351] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s7, 96  # [op1352] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 176(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, t4, s7  # [op1353] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(s7)  # [op1354] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s7, 7  # [op1355] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s7, t0, s7  # [op1356] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt a6, s7, a6  # [op1357] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 184(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt t4, t4, s1  # [op1358] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t5, 0  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub t4, t5, t4  # [op1359] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t5, 184(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub s1, s1, t5  # [op1360] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and s1, s1, t4  # [op1361] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 184(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s1, t4, s1  # [op1362] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li t4, 0  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub a6, t4, a6  # [op1363] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and s1, s1, a6  # [op1364] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw s1, s1, 0  # [op1365] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli a6, a1, e32, m1, ta,ma  # [op1366] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv.v.x v5, s1  # [op1367] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmslt.vv v5, v1, v5  # [op1368] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmv1r.v v0, v5  # [op1369] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld s1, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s1, s1, a7  # [op1370] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul a4, s7, a4  # [op1371] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s1, s1, a4  # [op1372] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul a4, t2, a5  # [op1373] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s1, s1, a4  # [op1374] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli a1, a1, e16, m1, ta,ma  # [op1375] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(s1), v0.t  # [op1376] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vmerge.vvm v5, v3, v5, v0  # [op1377] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s1, 112  # [op1378] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a1, 176(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s1, a1, s1  # [op1379] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(s1)  # [op1380] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Ltaf15.join  # [op1381] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Ltaf15.join:  # block taf15.join
li s1, 8  # [op1382] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a1, 192(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a1, a1, s1  # [op1383] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a4, 257  # [op1384] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt a1, a1, a4  # [op1385] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a4, 1  # [op1386] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a5, 184(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a4, a5, a4  # [op1387] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt s1, s1, a4  # [op1388] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and s1, a1, s1  # [op1389] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
bne s1, zero, .Lbrc1390_true  # [op1390] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lpbf16.else  # [op1390] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lbrc1390_true:  # [op1390] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lpbf16.then  # [op1390] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lpbf16.then:  # block pbf16.then
li s1, 8  # [op1391] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli s1, s1, e16, m1, ta,ma  # [op1392] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s1, 512  # [op1393] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a1, 111744  # [op1394] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a4, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a1, a4, a1  # [op1395] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul a4, t2, s1  # [op1396] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a4, a1, a4  # [op1397] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a1, 2  # [op1398] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a5, 192(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul a5, a5, a1  # [op1399] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a4, a4, a5  # [op1400] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vlse16.v v5, 0(a4), s1  # [op1401] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a2)  # [op1402] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a5, a4, a1  # [op1403] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a4, 16  # [op1404] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a6, a2, a4  # [op1405] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vlse16.v v5, 0(a5), s1  # [op1406] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a6)  # [op1407] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a5, a5, a1  # [op1408] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a6, a6, a4  # [op1409] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vlse16.v v5, 0(a5), s1  # [op1410] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a6)  # [op1411] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a5, a5, a1  # [op1412] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a6, a6, a4  # [op1413] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vlse16.v v5, 0(a5), s1  # [op1414] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a6)  # [op1415] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a5, a5, a1  # [op1416] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a6, a6, a4  # [op1417] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vlse16.v v5, 0(a5), s1  # [op1418] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a6)  # [op1419] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a5, a5, a1  # [op1420] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a6, a6, a4  # [op1421] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vlse16.v v5, 0(a5), s1  # [op1422] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a6)  # [op1423] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a5, a5, a1  # [op1424] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a6, a6, a4  # [op1425] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vlse16.v v5, 0(a5), s1  # [op1426] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a6)  # [op1427] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a1, a5, a1  # [op1428] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a4, a6, a4  # [op1429] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vlse16.v v5, 0(a1), s1  # [op1430] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a4)  # [op1431] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lpbf16.join  # [op1432] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lpbf16.else:  # block pbf16.else
li s1, 8  # [op1433] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli s1, s1, e16, m1, ta,ma  # [op1434] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s1, 0  # [op1435] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a1, a2, s1  # [op1436] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v4, 0(a1)  # [op1437] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a1, 16  # [op1438] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a1, a2, a1  # [op1439] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v4, 0(a1)  # [op1440] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a1, 32  # [op1441] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a1, a2, a1  # [op1442] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v4, 0(a1)  # [op1443] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a1, 48  # [op1444] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a1, a2, a1  # [op1445] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v4, 0(a1)  # [op1446] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a1, 64  # [op1447] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a1, a2, a1  # [op1448] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v4, 0(a1)  # [op1449] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a1, 80  # [op1450] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a1, a2, a1  # [op1451] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v4, 0(a1)  # [op1452] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a1, 96  # [op1453] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a1, a2, a1  # [op1454] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v4, 0(a1)  # [op1455] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a1, 112  # [op1456] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a1, a2, a1  # [op1457] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v4, 0(a1)  # [op1458] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a6, 8  # [op1459] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lpb17.head  # [op1460] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lpb17.head:  # block pb17.head
slt a1, s1, a6  # [op1461] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
bne a1, zero, .Lbrc1462_true  # [op1462] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lpb17.exit  # [op1462] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lbrc1462_true:  # [op1462] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lpb17.body  # [op1462] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lpb17.body:  # block pb17.body
ld a1, 192(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a1, a1, s1  # [op1463] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a4, 256  # [op1464] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt a7, a1, a4  # [op1465] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a4, 8  # [op1466] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a5, 184(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
slt s7, a5, a4  # [op1467] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a5, 0  # [op1468] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub s7, a5, s7  # [op1469] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld t4, 184(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub a4, a4, t4  # [op1470] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and a4, a4, s7  # [op1471] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld s7, 184(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a4, s7, a4  # [op1472] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
sub a5, a5, a7  # [op1473] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
and a5, a4, a5  # [op1474] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a4, 111744  # [op1475] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld a7, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a7, a7, a4  # [op1476] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a4, 512  # [op1477] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul s7, t2, a4  # [op1478] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a7, a7, s7  # [op1479] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s7, 2  # [op1480] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul a1, a1, s7  # [op1481] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a1, a7, a1  # [op1482] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a7, 16  # [op1483] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
mul a7, s1, a7  # [op1484] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add a7, a2, a7  # [op1485] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
addiw a5, a5, 0  # [op1486] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli a5, a5, e16, m1, ta,ma  # [op1487] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vlse16.v v5, 0(a1), a4  # [op1488] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vse16.v v5, 0(a7)  # [op1489] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li a1, 1  # [op1490] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add s1, s1, a1  # [op1491] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lpb17.head  # [op1492] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lpb17.exit:  # block pb17.exit
j .Lpbf16.join  # [op1493] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lpbf16.join:  # block pbf16.join
    # [peephole-dead-li] [op1494] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli s1, x0, e16, m1, ta,ma  # [op1495] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
ld s1, 176(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v5, 0(s1)  # [op1496] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vle16.v v8, 0(a2)  # [op1497] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
vsetvli x0, zero, e16, m1, ta, ma
    smt.vfwmadot v6, v5, v8  # [op1498] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
li s1, 8  # [op1499] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
add t2, t2, s1  # [op1500] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
j .Lmk14.head  # [op1501] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:12
.Lchunk18_head:  # block chunk18_head
li t0, 32768  # [op1502] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
slt t0, t2, t0  # [op1503] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
bne t0, zero, .Lbrc1504_true  # [op1504] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op1504] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, s1  # [op1504] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk18_exit  # [op1504] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lbrc1504_true:  # [op1504] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk18_body  # [op1504] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk18_exit:  # block chunk18_exit
li t2, 0  # [op1505] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv s1, t0  # [op1506] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk19_head  # [op1506] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk18_body:  # block chunk18_body
    # [peephole-dead-li] [op1507] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli t0, x0, e32, m1, ta,ma  # [op1508] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t0, 32  # [op1509] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vid.v v1  # [op1511] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vadd.vx v1, v1, t2  # [op1512] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vwadd.vx v2, v1, x0  # [op1513] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vsetvli a1, x0, e64, m2, ta,ma  # [op1514] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
li a1, 4  # [op1515] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vmul.vx v2, v2, a1  # [op1516] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
li a2, 128128  # [op1517] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
ld a3, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
add a2, a3, a2  # [op1518] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vsetvli a3, x0, e32, m1, ta,ma  # [op1519] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vluxei64.v v4, (a2), v2  # [op1520] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vwadd.vx v2, v1, x0  # [op1521] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vsetvli a2, x0, e64, m2, ta,ma  # [op1522] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vmul.vx v2, v2, a1  # [op1523] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
li a2, 259200  # [op1524] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
ld a3, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
add a2, a3, a2  # [op1525] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vsetvli a3, x0, e32, m1, ta,ma  # [op1526] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vluxei64.v v5, (a2), v2  # [op1527] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vfadd.vv v2, v4, v5  # [op1528] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vwadd.vx v4, v1, x0  # [op1529] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vsetvli a2, x0, e64, m2, ta,ma  # [op1530] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vmul.vx v4, v4, a1  # [op1531] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
li a1, 390272  # [op1532] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
ld a2, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
add a1, a2, a1  # [op1533] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vsetvli a2, x0, e32, m1, ta,ma  # [op1534] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
vsuxei64.v v2, (a1), v4  # [op1535] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:54:5
li a1, 32  # [op1536] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add s1, s1, a1  # [op1537] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t2, t0  # [op1538] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t0  # [op1539] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk18_head  # [op1539] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk19_head:  # block chunk19_head
li t0, 128  # [op1540] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
slt t0, t2, t0  # [op1541] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
bne t0, zero, .Lbrc1542_true  # [op1542] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op1542] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, s1  # [op1542] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk19_exit  # [op1542] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lbrc1542_true:  # [op1542] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk19_body  # [op1542] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk19_exit:  # block chunk19_exit
li t2, 0  # [op1543] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv a1, t0  # [op1544] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk20_head  # [op1544] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk19_body:  # block chunk19_body
    # [peephole-dead-li] [op1545] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli t0, x0, e32, m1, ta,ma  # [op1546] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t0, 32  # [op1547] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
ld a1, 152(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vmv.v.x v2, a1  # [op1549] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vid.v v1  # [op1550] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vadd.vx v1, v1, t2  # [op1551] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vwadd.vx v4, v1, x0  # [op1552] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vsetvli a1, x0, e64, m2, ta,ma  # [op1553] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
li a1, 4  # [op1554] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vmul.vx v4, v4, a1  # [op1555] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
li a2, 0  # [op1556] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
ld a3, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
add a2, a3, a2  # [op1557] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vsetvli a3, x0, e32, m1, ta,ma  # [op1558] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vluxei64.v v3, (a2), v4  # [op1559] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vmul.vv v2, v3, v2  # [op1560] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vwadd.vx v4, v1, x0  # [op1561] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vsetvli a2, x0, e64, m2, ta,ma  # [op1562] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vmul.vx v4, v4, a1  # [op1563] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
li a1, 521344  # [op1564] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
ld a2, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
add a1, a2, a1  # [op1565] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vsetvli a2, x0, e32, m1, ta,ma  # [op1566] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
vsuxei64.v v2, (a1), v4  # [op1567] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:22
li a1, 32  # [op1568] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add s1, s1, a1  # [op1569] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t2, t0  # [op1570] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t0  # [op1571] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk19_head  # [op1571] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk20_head:  # block chunk20_head
li t0, 32768  # [op1572] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
slt t0, t2, t0  # [op1573] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
bne t0, zero, .Lbrc1574_true  # [op1574] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t1  # [op1574] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, a1  # [op1574] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk20_exit  # [op1574] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lbrc1574_true:  # [op1574] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk20_body  # [op1574] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk20_exit:  # block chunk20_exit
sd t0, 96(sp)  # [op1575] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t0, t1  # [op1575] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld t1, 96(sp)  # [op1575] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lprog_next  # [op1575] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lchunk20_body:  # block chunk20_body
li t0, 32  # [op1576] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
vsetvli t0, t0, e16, m1, ta,ma  # [op1577] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
li t0, 32  # [op1578] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
vsetvli s1, x0, e32, m1, ta,ma  # [op1579] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
vid.v v1  # [op1580] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
vadd.vx v1, v1, t2  # [op1581] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
li s1, 256  # [op1582] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
vmv.v.x v2, s1  # [op1583] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
vdiv.vv v2, v1, v2  # [op1584] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
vwadd.vx v4, v2, x0  # [op1585] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
vsetvli a2, x0, e64, m2, ta,ma  # [op1586] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
li a2, 8  # [op1587] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
vmul.vx v2, v4, a2  # [op1588] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
li a2, 521856  # [op1589] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
ld a3, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
add a2, a3, a2  # [op1590] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
vluxei64.v v4, (a2), v2  # [op1591] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
vsetvli a2, t0, e16, m1, ta,ma  # [op1592] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:57:14
vsetvli a2, x0, e32, m1, ta,ma  # [op1593] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vwadd.vx v2, v1, x0  # [op1594] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli a2, x0, e64, m2, ta,ma  # [op1595] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 4  # [op1596] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmul.vx v2, v2, a2  # [op1597] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a3, 390272  # [op1598] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
ld a4, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a3, a4, a3  # [op1599] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli a4, x0, e32, m1, ta,ma  # [op1600] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vluxei64.v v4, (a3), v2  # [op1601] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli a3, t0, e16, m1, ta,ma  # [op1602] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli a3, x0, e32, m1, ta,ma  # [op1603] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.v.v v6, v4  # [op1604] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli a3, t0, e16, m1, ta,ma  # [op1605] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vfncvt.f.f.w v2, v6  # [op1606] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli a3, x0, e32, m1, ta,ma  # [op1607] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.v.x v3, s1  # [op1608] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vdiv.vv v3, v1, v3  # [op1609] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vwadd.vx v4, v3, x0  # [op1610] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli a3, x0, e64, m2, ta,ma  # [op1611] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmul.vx v4, v4, a2  # [op1612] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a3, 521344  # [op1613] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
ld a4, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a3, a4, a3  # [op1614] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli a4, x0, e32, m1, ta,ma  # [op1615] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vluxei64.v v3, (a3), v4  # [op1616] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli a3, t0, e16, m1, ta,ma  # [op1617] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli a3, x0, e32, m1, ta,ma  # [op1618] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.v.x v4, s1  # [op1619] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vrem.vv v1, v1, v4  # [op1620] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vwadd.vx v4, v1, x0  # [op1621] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli s1, x0, e64, m2, ta,ma  # [op1622] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmul.vx v4, v4, a2  # [op1623] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li s1, 512  # [op1624] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
ld a2, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add s1, a2, s1  # [op1625] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli a2, x0, e32, m1, ta,ma  # [op1626] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vluxei64.v v1, (s1), v4  # [op1627] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli s1, t0, e16, m1, ta,ma  # [op1628] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli s1, x0, e32, m1, ta,ma  # [op1629] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vadd.vv v1, v3, v1  # [op1630] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli s1, t0, e16, m1, ta,ma  # [op1631] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli s1, x0, e32, m1, ta,ma  # [op1632] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vwadd.vx v4, v1, x0  # [op1633] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli s1, x0, e64, m2, ta,ma  # [op1634] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li s1, 2  # [op1635] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmul.vx v4, v4, s1  # [op1636] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli t0, t0, e16, m1, ta,ma  # [op1637] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 0  # [op1638] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 16  # [op1639] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli t0, t0, e64, m2, ta,ma  # [op1640] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s t0, v4  # [op1641] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vid.v v6  # [op1642] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmul.vx v6, v6, s1  # [op1643] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vadd.vx v6, v6, t0  # [op1644] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmsne.vv v3, v4, v6  # [op1645] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vcpop.m a3, v3  # [op1646] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, a2, a3  # [op1647] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a3, s5, t0  # [op1648] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vid.v v6  # [op1649] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 16  # [op1650] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vadd.vx v8, v6, t0  # [op1651] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vrgather.vv v6, v4, v8  # [op1652] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s t0, v6  # [op1653] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vid.v v4  # [op1654] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmul.vx v4, v4, s1  # [op1655] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vadd.vx v4, v4, t0  # [op1656] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmsne.vv v3, v6, v4  # [op1657] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vcpop.m s1, v3  # [op1658] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add s1, a2, s1  # [op1659] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add t0, s5, t0  # [op1660] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
bne s1, zero, .Lbrc1661_true  # [op1661] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
j .Lngs.t3  # [op1661] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
.Lbrc1661_true:  # [op1661] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
j .Lngs.e3  # [op1661] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
.Lngs.t3:  # block ngs.t3
li s1, 16  # [op1662] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli s1, s1, e16, m1, ta,ma  # [op1663] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vse16.v v2, 0(a3)  # [op1664] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vid.v v1  # [op1665] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li s1, 16  # [op1666] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vadd.vx v1, v1, s1  # [op1667] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vrgather.vv v3, v2, v1  # [op1668] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vse16.v v3, 0(t0)  # [op1669] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
j .Lngs.j3  # [op1670] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
.Lngs.e3:  # block ngs.e3
li s1, 32  # [op1671] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli t0, x0, e32, m1, ta,ma  # [op1672] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vwadd.vx v4, v1, x0  # [op1673] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli t0, x0, e64, m2, ta,ma  # [op1674] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 2  # [op1675] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmul.vx v4, v4, a2  # [op1676] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli t0, s1, e16, m1, ta,ma  # [op1677] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li t0, 523392  # [op1678] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
ld a3, 168(sp)  # [op-1] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add t0, a3, t0  # [op1679] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a3, 128  # [op1680] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a3, t0, a3  # [op1681] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vse16.v v2, 0(t0)  # [op1682] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli s1, x0, e64, m2, ta,ma  # [op1683] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vadd.vx v2, v4, s5  # [op1684] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1685] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a3, 0  # [op1686] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a3, t0, a3  # [op1687] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a3, 0(a3)  # [op1688] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a3, 0(s1)  # [op1689] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1690] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1691] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1692] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1693] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1694] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1695] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1696] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 4  # [op1697] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1698] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1699] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1700] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1701] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1702] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 6  # [op1703] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1704] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1705] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1706] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1707] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1708] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 8  # [op1709] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1710] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1711] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1712] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1713] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1714] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 10  # [op1715] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1716] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1717] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1718] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1719] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1720] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 12  # [op1721] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1722] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1723] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1724] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1725] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1726] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 14  # [op1727] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1728] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1729] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1730] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1731] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1732] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 16  # [op1733] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1734] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1735] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1736] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1737] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1738] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 18  # [op1739] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1740] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1741] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1742] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1743] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1744] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 20  # [op1745] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1746] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1747] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1748] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1749] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1750] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 22  # [op1751] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1752] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1753] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1754] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1755] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1756] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 24  # [op1757] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1758] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1759] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1760] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1761] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1762] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 26  # [op1763] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1764] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1765] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1766] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1767] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1768] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 28  # [op1769] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1770] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1771] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1772] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1773] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1774] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 30  # [op1775] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1776] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1777] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1778] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1779] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1780] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 32  # [op1781] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1782] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1783] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1784] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1785] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1786] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 34  # [op1787] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1788] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1789] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1790] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1791] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1792] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 36  # [op1793] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1794] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1795] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1796] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1797] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1798] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 38  # [op1799] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1800] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1801] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1802] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1803] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1804] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 40  # [op1805] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1806] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1807] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1808] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1809] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1810] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 42  # [op1811] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1812] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1813] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1814] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1815] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1816] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 44  # [op1817] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1818] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1819] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1820] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1821] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1822] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 46  # [op1823] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1824] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1825] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1826] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1827] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1828] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 48  # [op1829] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1830] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1831] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1832] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1833] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1834] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 50  # [op1835] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1836] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1837] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1838] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1839] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1840] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 52  # [op1841] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1842] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1843] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1844] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1845] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1846] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 54  # [op1847] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1848] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1849] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1850] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1851] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1852] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 56  # [op1853] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1854] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1855] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1856] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1857] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1858] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 58  # [op1859] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1860] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1861] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1862] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1863] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1864] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 60  # [op1865] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add a2, t0, a2  # [op1866] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu a2, 0(a2)  # [op1867] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh a2, 0(s1)  # [op1868] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1869] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vmv.x.s s1, v2  # [op1870] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li a2, 62  # [op1871] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
add t0, t0, a2  # [op1872] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
lhu t0, 0(t0)  # [op1873] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
sh t0, 0(s1)  # [op1874] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vslidedown.vi v2, v2, 1  # [op1875] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
j .Lngs.j3  # [op1876] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
.Lngs.j3:  # block ngs.j3
li t0, 32  # [op1877] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
vsetvli s1, t0, e16, m1, ta,ma  # [op1878] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:58:5
li s1, 32  # [op1879] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
add s1, a1, s1  # [op1880] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addw t0, t2, t0  # [op1881] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv t2, t0  # [op1882] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
mv a1, s1  # [op1882] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lchunk20_head  # [op1882] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lprog_next:  # block prog_next
add t0, t0, s10  # [op1883] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
j .Lprog_head  # [op1884] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
.Lprog_exit:  # block prog_exit
sd t0, 0(s8)  # [op1885] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld ra, 0(sp)  # [op1886] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s1, 8(sp)  # [op1886] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s2, 16(sp)  # [op1886] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s3, 24(sp)  # [op1886] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s4, 32(sp)  # [op1886] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s5, 40(sp)  # [op1886] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s6, 48(sp)  # [op1886] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s7, 56(sp)  # [op1886] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s8, 64(sp)  # [op1886] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s9, 72(sp)  # [op1886] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s10, 80(sp)  # [op1886] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ld s11, 88(sp)  # [op1886] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
addi sp, sp, 208  # [op1886] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
ret  # [op1886] /tmp/a100-opt3-scan0/ops/suite/dev/matmul_k32_fast_kernel_f2eeb00c.py:25:1
    .size operator_entry, .-operator_entry
    .section .note.GNU-stack,"",@progbits
