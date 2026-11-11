# a100c emitted program: attention_forward_kernel
# source: tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py
# specialization identity: 7519904ce3f05812
# compiler revision: b5c42fbb75a242a8
# target model: a100-rvv1-vlen1024/1 (VLEN=1024, file=4096B)
# options: default
# argument layout: 925649716db89c20
# every instruction below traces to a selected MIR op: [opN] carries the source location
# passes: passes=default
    .text
    .globl operator_workspace_private
    .type operator_workspace_private, @function
operator_workspace_private:
    li a0, 85232
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
    # [peephole] removed 0 redundant vsetvli, 113 redundant li
operator_entry:  # fn operator_entry
addi sp, sp, -288
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
ld t0, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t0, 0(t0)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t0, 0(t0)  # [op1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sd t0, 128(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t0, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld a2, 24(t0)  # [op3] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t0, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
lwu t0, 40(t0)  # [op4] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
lwu t1, 44(t1)  # [op5] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 0(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 8(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 8(t2)  # [op6] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sd t2, 144(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 144(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addiw t2, t2, 0  # [op7] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sd t2, 136(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 0(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 8(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 24(t2)  # [op8] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sd t2, 120(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 120(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addiw a3, t2, 0  # [op9] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 0(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 8(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 40(t2)  # [op10] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sd t2, 152(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 152(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addiw t2, t2, 0  # [op11] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 0(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 8(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 56(t2)  # [op12] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li s1, 1  # [op13] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vsetvli s1, s1, e64, m1, ta,ma  # [op14] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vmv.v.x v1, t2  # [op15] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vmv.v.v v2, v1  # [op16] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t2, 1  # [op17] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vsetvli t2, t2, e32, m1, ta,ma  # [op18] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vfncvt.f.f.w v1, v2  # [op19] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vmv.x.s a4, v1  # [op20] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 0(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 8(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 72(t2)  # [op21] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addiw a5, t2, 0  # [op22] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 0(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 8(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 88(t2)  # [op23] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addiw t2, t2, 0  # [op24] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 0(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 8(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 104(t2)  # [op25] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addiw a6, t2, 0  # [op26] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 0(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 8(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 120(t2)  # [op27] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addiw a7, t2, 0  # [op28] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 0(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 8(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 136(t2)  # [op29] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addiw s2, t2, 0  # [op30] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 0(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 8(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 152(t2)  # [op31] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addiw s3, t2, 0  # [op32] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 0(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 8(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 168(t2)  # [op33] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addiw t2, t2, 0  # [op34] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 0(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 8(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 184(t2)  # [op35] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addiw s4, t2, 0  # [op36] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 0(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 8(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 200(t2)  # [op37] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addiw s5, t2, 0  # [op38] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 0(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 8(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 216(t2)  # [op39] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addiw t2, t2, 0  # [op40] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 0(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 8(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 232(t2)  # [op41] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addiw s6, t2, 0  # [op42] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 0(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 8(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 248(t2)  # [op43] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addiw t2, t2, 0  # [op44] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sd t2, 160(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 0(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 8(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 264(t2)  # [op45] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addiw t2, t2, 0  # [op46] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sd t2, 168(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 0(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 8(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 280(t2)  # [op47] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addiw t2, t2, 0  # [op48] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sd t2, 176(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 0(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 8(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 296(t2)  # [op49] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addiw t2, t2, 0  # [op50] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 0(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 8(t2)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 312(t2)  # [op51] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addiw t2, t2, 0  # [op52] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sd t2, 184(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 128(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 0(t2)  # [op53] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sd t2, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 128(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s7, 56(t2)  # [op54] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 128(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 112(t2)  # [op55] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sd t2, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 128(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 168(t2)  # [op56] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sd t2, 248(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 144(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s1, 152(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mul t2, s1, t2  # [op57] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sd t2, 200(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t2, 1  # [op58] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s1, 120(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mul t2, t2, s1  # [op59] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s1, 200(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mul s8, t2, s1  # [op60] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t0, t0  # [op61] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv s9, t1  # [op62] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t1, 0  # [op63] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lprog_head  # [op64] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lprog_head:  # block prog_head
slt t2, t0, s8  # [op65] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
bne t2, zero, .Lbrc66_true  # [op66] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sd t1, 96(sp)  # [op66] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t1, t0  # [op66] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t0, 96(sp)  # [op66] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lprog_exit  # [op66] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lbrc66_true:  # [op66] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t2, t1  # [op66] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lprog_body  # [op66] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lprog_body:  # block prog_body
sd t0, 256(sp)  # [op-1]
li t0, 1  # [op67] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t1, 120(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s1, 256(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
divu t1, s1, t1  # [op68] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s1, 120(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mul t1, t1, s1  # [op69] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s1, 256(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sub s1, s1, t1  # [op70] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t1, 120(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mul t0, t0, t1  # [op71] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t1, 256(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
divu t1, t1, t0  # [op72] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld a1, 200(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
divu a1, t1, a1  # [op73] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s10, 200(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mul a1, a1, s10  # [op74] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sub t1, t1, a1  # [op75] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld a1, 200(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mul t0, t0, a1  # [op76] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addiw t0, s1, 0  # [op77] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sd t0, 272(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addiw t0, t1, 0  # [op78] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t1, 120(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addiw t1, t1, 0  # [op79] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t1, 200(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addiw t1, t1, 0  # [op80] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t1, 16(t1)  # [op81] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sd t1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t1, 112(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t1, 8(t1)  # [op82] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t1, 136(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:31:13
divw t1, t0, t1  # [op83] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:31:13
sd t1, 224(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:31:13
ld t1, 136(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:32:13
divw t1, t0, t1  # [op84] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:32:13
ld s1, 136(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:32:13
mulw t1, t1, s1  # [op85] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:32:13
subw t0, t0, t1  # [op86] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:32:13
sd t0, 232(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:32:13
li t0, 0  # [op87] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t1, t2  # [op88] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk1_head  # [op88] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk1_head:  # block chunk1_head
li t2, 64  # [op89] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
slt t2, t0, t2  # [op90] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s1, 256(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
bne t2, zero, .Lbrc91_true  # [op91] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t0, t1  # [op91] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t1, s1  # [op91] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk1_exit  # [op91] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lbrc91_true:  # [op91] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk1_body  # [op91] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk1_exit:  # block chunk1_exit
li t1, 0  # [op92] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk2_head  # [op93] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk1_body:  # block chunk1_body
li t2, 32  # [op94] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vsetvli t2, t2, e32, m1, ta,ma  # [op95] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t2, 32  # [op96] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:34:14
vid.v v1  # [op98] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:34:14
vadd.vx v1, v1, t0  # [op99] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:34:14
vid.v v2  # [op100] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:34:14
vadd.vx v2, v2, t0  # [op101] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:34:14
    # [peephole-li] [op102] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:34:14
vwadd.vx v4, v2, x0  # [op104] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:34:14
    # [peephole-li] [op105] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:34:14
vsetvli t2, t2, e64, m2, ta,ma  # [op106] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:34:14
li t2, 4  # [op107] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:34:14
vmul.vx v2, v4, t2  # [op108] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:34:14
li t2, 0  # [op109] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:34:14
ld s1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:34:14
add t2, s1, t2  # [op110] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:34:14
li s1, 32  # [op111] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:34:14
vsetvli s1, s1, e32, m1, ta,ma  # [op112] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:34:14
vsuxei64.v v1, (t2), v2  # [op113] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:34:14
li t2, 32  # [op114] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:34:14
    # [peephole-li] [op116] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add t1, t1, t2  # [op117] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
    # [peephole-li] [op118] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addw t0, t0, t2  # [op119] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
    # [peephole-li] [op120] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk1_head  # [op122] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk2_head:  # block chunk2_head
sd t1, 240(sp)  # [op-1]
li t1, 32  # [op123] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 240(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
slt t1, t2, t1  # [op124] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 240(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s1, 256(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
bne t1, zero, .Lbrc125_true  # [op125] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t1, s1  # [op125] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk2_exit  # [op125] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lbrc125_true:  # [op125] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t1, t2  # [op125] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk2_body  # [op125] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk2_exit:  # block chunk2_exit
li t1, 85120  # [op126] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add t1, t2, t1  # [op127] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
lw t1, 0(t1)  # [op128] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t2, 85128  # [op129] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add t2, s1, t2  # [op130] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 0(t2)  # [op131] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t2, 85136  # [op132] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add t2, s1, t2  # [op133] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
lw t2, 0(t2)  # [op134] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li s1, 85144  # [op135] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld a1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add s1, a1, s1  # [op136] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s1, 0(s1)  # [op137] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li s1, 85152  # [op138] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld a1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add s1, a1, s1  # [op139] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
lw s10, 0(s1)  # [op140] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li s1, 85160  # [op141] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld a1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add s1, a1, s1  # [op142] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s1, 0(s1)  # [op143] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li s1, 85168  # [op144] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld a1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add s1, a1, s1  # [op145] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
lw s11, 0(s1)  # [op146] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li s1, 85176  # [op147] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld a1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add s1, a1, s1  # [op148] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s1, 0(s1)  # [op149] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li s1, 85184  # [op150] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld a1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add s1, a1, s1  # [op151] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
lw t3, 0(s1)  # [op152] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li s1, 85192  # [op153] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld a1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add s1, a1, s1  # [op154] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s1, 0(s1)  # [op155] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li s1, 85200  # [op156] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld a1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add s1, a1, s1  # [op157] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
lw t4, 0(s1)  # [op158] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li s1, 85208  # [op159] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld a1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add s1, a1, s1  # [op160] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s1, 0(s1)  # [op161] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li s1, 85216  # [op162] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld a1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add s1, a1, s1  # [op163] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
lw s1, 0(s1)  # [op164] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li a1, 85224  # [op165] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t5, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add a1, t5, a1  # [op166] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld a1, 0(a1)  # [op167] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li a1, 0  # [op168] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk3_head  # [op169] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk2_body:  # block chunk2_body
sd t1, 240(sp)  # [op-1]
li t1, 32  # [op170] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vsetvli t1, t1, e32, m1, ta,ma  # [op171] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t1, 32  # [op172] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:35:14
vid.v v1  # [op174] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:35:14
ld t1, 240(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:35:14
vadd.vx v1, v1, t1  # [op175] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:35:14
vid.v v2  # [op176] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:35:14
ld t1, 240(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:35:14
vadd.vx v2, v2, t1  # [op177] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:35:14
li t1, 32  # [op178] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:35:14
vwadd.vx v4, v2, x0  # [op180] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:35:14
    # [peephole-li] [op181] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:35:14
vsetvli t1, t1, e64, m2, ta,ma  # [op182] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:35:14
li t1, 4  # [op183] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:35:14
vmul.vx v2, v4, t1  # [op184] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:35:14
li t1, 256  # [op185] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:35:14
ld t2, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:35:14
add t1, t2, t1  # [op186] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:35:14
li t2, 32  # [op187] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:35:14
vsetvli t2, t2, e32, m1, ta,ma  # [op188] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:35:14
vsuxei64.v v1, (t1), v2  # [op189] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:35:14
li t1, 32  # [op190] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:35:14
ld t1, 160(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:36:22
ld t2, 224(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:36:22
mulw t1, t2, t1  # [op192] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:36:22
ld t2, 232(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:36:42
mulw t2, t2, s5  # [op193] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:36:42
ld s1, 224(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:37:22
mulw s1, s1, a7  # [op194] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:37:22
ld a1, 232(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:37:42
mulw a1, a1, a5  # [op195] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:37:42
ld s10, 184(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:38:22
ld s11, 224(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:38:22
mulw s10, s11, s10  # [op196] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:38:22
ld s11, 168(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:38:42
ld t3, 232(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:38:42
mulw s11, t3, s11  # [op197] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:38:42
ld t3, 272(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:26
mulw t3, t3, s6  # [op198] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:26
li t4, 32  # [op199] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add t0, t0, t4  # [op200] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
    # [peephole-li] [op201] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t5, 240(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addw t4, t5, t4  # [op202] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t5, 32  # [op203] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t5, 85120  # [op205] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t6, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add t5, t6, t5  # [op206] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sw t1, 0(t5)  # [op207] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t1, 85128  # [op208] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t5, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add t1, t5, t1  # [op209] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t5, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sd t5, 0(t1)  # [op210] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t1, 85136  # [op211] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t5, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add t1, t5, t1  # [op212] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sw t2, 0(t1)  # [op213] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t1, 85144  # [op214] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add t1, t2, t1  # [op215] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sd t2, 0(t1)  # [op216] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t1, 85152  # [op217] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add t1, t2, t1  # [op218] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sw s1, 0(t1)  # [op219] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t1, 85160  # [op220] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add t1, t2, t1  # [op221] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sd t2, 0(t1)  # [op222] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t1, 85168  # [op223] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add t1, t2, t1  # [op224] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sw a1, 0(t1)  # [op225] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t1, 85176  # [op226] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add t1, t2, t1  # [op227] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sd t2, 0(t1)  # [op228] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t1, 85184  # [op229] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add t1, t2, t1  # [op230] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sw s10, 0(t1)  # [op231] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t1, 85192  # [op232] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add t1, t2, t1  # [op233] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 248(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sd t2, 0(t1)  # [op234] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t1, 85200  # [op235] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add t1, t2, t1  # [op236] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sw s11, 0(t1)  # [op237] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t1, 85208  # [op238] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add t1, t2, t1  # [op239] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 248(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sd t2, 0(t1)  # [op240] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t1, 85216  # [op241] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add t1, t2, t1  # [op242] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sw t3, 0(t1)  # [op243] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t1, 85224  # [op244] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add t1, t2, t1  # [op245] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t2, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sd t2, 0(t1)  # [op246] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t1, t4  # [op247] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk2_head  # [op247] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk3_head:  # block chunk3_head
sd a1, 264(sp)  # [op-1]
li a1, 64  # [op248] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t5, 264(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
slt a1, t5, a1  # [op249] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t5, 256(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t6, 264(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
bne a1, zero, .Lbrc250_true  # [op250] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t1, t5  # [op250] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk3_exit  # [op250] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lbrc250_true:  # [op250] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv a1, t6  # [op250] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk3_body  # [op250] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk3_exit:  # block chunk3_exit
li t1, 0  # [op251] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sd t0, 96(sp)  # [op252] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t0, t1  # [op252] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t1, 96(sp)  # [op252] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk4_head  # [op252] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk3_body:  # block chunk3_body
sd a1, 264(sp)  # [op-1]
li a1, 32  # [op253] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vsetvli a1, a1, e32, m1, ta,ma  # [op254] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addw a1, t1, t2  # [op255] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
addw a1, a1, s1  # [op256] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
li t5, 32  # [op257] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
vid.v v1  # [op259] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
ld t5, 264(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
vadd.vx v1, v1, t5  # [op260] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
li t5, 32  # [op261] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
vwadd.vx v2, v1, x0  # [op263] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
    # [peephole-li] [op264] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
vsetvli t5, t5, e64, m2, ta,ma  # [op265] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
li t5, 4  # [op266] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
vmul.vx v2, v2, t5  # [op267] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
li t5, 0  # [op268] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
ld t6, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
add t5, t6, t5  # [op269] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
li t6, 32  # [op270] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
vsetvli t6, t6, e32, m1, ta,ma  # [op271] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
vluxei64.v v1, (t5), v2  # [op272] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
li t5, 32  # [op273] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
vadd.vx v1, v1, a1  # [op275] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
ld a1, 264(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
mv a1, a1  # [op276] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
mv t5, t1  # [op277] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
add a1, a1, t5  # [op278] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
mv t5, t2  # [op279] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
add a1, a1, t5  # [op280] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
mv t5, s1  # [op281] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
add a1, a1, t5  # [op282] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
li t5, 4  # [op283] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
mul a1, a1, t5  # [op284] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
ld t5, 208(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
add a1, t5, a1  # [op285] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
vle32.v v1, 0(a1)  # [op286] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
vid.v v2  # [op287] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
ld a1, 264(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
vadd.vx v2, v2, a1  # [op288] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
li a1, 32  # [op289] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
vwadd.vx v4, v2, x0  # [op291] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
    # [peephole-li] [op292] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
vsetvli a1, a1, e64, m2, ta,ma  # [op293] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
li a1, 4  # [op294] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
vmul.vx v2, v4, a1  # [op295] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
li a1, 384  # [op296] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
ld t5, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
add a1, t5, a1  # [op297] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
li t5, 32  # [op298] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
vsetvli t5, t5, e32, m1, ta,ma  # [op299] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
vsuxei64.v v1, (a1), v2  # [op300] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
li a1, 32  # [op301] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:40:9
    # [peephole-li] [op303] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add t0, t0, a1  # [op304] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
    # [peephole-li] [op305] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t5, 264(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addw a1, t5, a1  # [op306] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t5, 32  # [op307] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk3_head  # [op309] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk4_head:  # block chunk4_head
li t2, 32  # [op310] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
slt t2, t0, t2  # [op311] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s1, 256(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
bne t2, zero, .Lbrc312_true  # [op312] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t0, t1  # [op312] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t1, s1  # [op312] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk4_exit  # [op312] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lbrc312_true:  # [op312] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk4_body  # [op312] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk4_exit:  # block chunk4_exit
li t1, 0  # [op313] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sd t0, 96(sp)  # [op314] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t0, t1  # [op314] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t1, 96(sp)  # [op314] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk5_head  # [op314] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk4_body:  # block chunk4_body
li t2, 32  # [op315] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vsetvli t2, t2, e32, m1, ta,ma  # [op316] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t2, 32  # [op317] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
vmv.v.x v1, a3  # [op319] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
vid.v v2  # [op320] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
vadd.vx v2, v2, t0  # [op321] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
    # [peephole-li] [op322] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
vwadd.vx v4, v2, x0  # [op324] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
    # [peephole-li] [op325] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
vsetvli t2, t2, e64, m2, ta,ma  # [op326] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
li t2, 4  # [op327] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
vmul.vx v2, v4, t2  # [op328] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
li t2, 256  # [op329] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
ld s1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
add t2, s1, t2  # [op330] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
li s1, 32  # [op331] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
vsetvli s1, s1, e32, m1, ta,ma  # [op332] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
vluxei64.v v4, (t2), v2  # [op333] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
li t2, 32  # [op334] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
vmslt.vv v1, v4, v1  # [op336] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
vid.v v2  # [op337] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
vadd.vx v2, v2, t0  # [op338] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
    # [peephole-li] [op339] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
vwadd.vx v4, v2, x0  # [op341] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
    # [peephole-li] [op342] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
vsetvli t2, t2, e64, m2, ta,ma  # [op343] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
li t2, 4  # [op344] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
vmul.vx v2, v4, t2  # [op345] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
li t2, 640  # [op346] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
ld s1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
add t2, s1, t2  # [op347] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
li s1, 32  # [op348] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
vsetvli s1, s1, e32, m1, ta,ma  # [op349] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
li s1, 1  # [op350] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
vmv.v.x v4, s1  # [op351] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
li s1, 0  # [op352] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
vmv.v.x v5, s1  # [op353] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
vmv1r.v v0, v1  # [op354] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
vmerge.vvm v1, v5, v4, v0  # [op355] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
vsuxei64.v v1, (t2), v2  # [op356] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:41:13
vmv.v.x v1, a6  # [op357] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:26
vid.v v2  # [op358] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:26
vadd.vx v2, v2, t0  # [op359] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:26
li t2, 32  # [op360] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:26
vwadd.vx v4, v2, x0  # [op362] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:26
    # [peephole-li] [op363] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:26
vsetvli t2, t2, e64, m2, ta,ma  # [op364] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:26
li t2, 4  # [op365] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:26
vmul.vx v2, v4, t2  # [op366] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:26
li t2, 256  # [op367] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:26
ld s1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:26
add t2, s1, t2  # [op368] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:26
li s1, 32  # [op369] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:26
vsetvli s1, s1, e32, m1, ta,ma  # [op370] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:26
vluxei64.v v4, (t2), v2  # [op371] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:26
li t2, 32  # [op372] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:26
vmul.vv v1, v4, v1  # [op374] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:26
vid.v v2  # [op375] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:26
vadd.vx v2, v2, t0  # [op376] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:26
    # [peephole-li] [op377] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:26
vwadd.vx v4, v2, x0  # [op379] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:26
    # [peephole-li] [op380] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:26
vsetvli t2, t2, e64, m2, ta,ma  # [op381] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:26
li t2, 4  # [op382] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:26
vmul.vx v2, v4, t2  # [op383] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:26
li t2, 896  # [op384] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:26
ld s1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:26
add t2, s1, t2  # [op385] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:26
li s1, 32  # [op386] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:26
vsetvli s1, s1, e32, m1, ta,ma  # [op387] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:26
vsuxei64.v v1, (t2), v2  # [op388] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:26
li t2, 32  # [op389] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:26
    # [peephole-li] [op391] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add t1, t1, t2  # [op392] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
    # [peephole-li] [op393] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addw t0, t0, t2  # [op394] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
    # [peephole-li] [op395] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk4_head  # [op397] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk5_head:  # block chunk5_head
li t2, 64  # [op398] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
slt t2, t0, t2  # [op399] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s1, 256(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
bne t2, zero, .Lbrc400_true  # [op400] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t0, t1  # [op400] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t1, s1  # [op400] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk5_exit  # [op400] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lbrc400_true:  # [op400] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk5_body  # [op400] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk5_exit:  # block chunk5_exit
li t1, 0  # [op401] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sd t0, 96(sp)  # [op402] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t0, t1  # [op402] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t1, 96(sp)  # [op402] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk6_head  # [op402] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk5_body:  # block chunk5_body
li t2, 32  # [op403] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vsetvli t2, t2, e32, m1, ta,ma  # [op404] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t2, 32  # [op405] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add t1, t1, t2  # [op406] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
    # [peephole-li] [op407] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addw t0, t0, t2  # [op408] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
    # [peephole-li] [op409] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk5_head  # [op411] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk6_head:  # block chunk6_head
li t2, 2048  # [op412] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
slt t2, t0, t2  # [op413] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s1, 256(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
bne t2, zero, .Lbrc414_true  # [op414] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t0, t1  # [op414] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t1, s1  # [op414] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk6_exit  # [op414] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lbrc414_true:  # [op414] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk6_body  # [op414] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk6_exit:  # block chunk6_exit
li t1, 0  # [op415] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sd t0, 96(sp)  # [op416] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t0, t1  # [op416] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t1, 96(sp)  # [op416] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk7_head  # [op416] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk6_body:  # block chunk6_body
li t2, 32  # [op417] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vsetvli t2, t2, e32, m1, ta,ma  # [op418] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t2, 32  # [op419] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:17
vid.v v1  # [op421] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:17
vadd.vx v1, v1, t0  # [op422] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:17
li t2, 64  # [op423] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:17
vmv.v.x v2, t2  # [op424] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:17
vdiv.vv v1, v1, v2  # [op425] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:17
li t2, 32  # [op426] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:17
vwadd.vx v2, v1, x0  # [op428] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:17
    # [peephole-li] [op429] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:17
vsetvli t2, t2, e64, m2, ta,ma  # [op430] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:17
li t2, 8  # [op431] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:17
vmul.vx v2, v2, t2  # [op432] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:17
li t2, 1024  # [op433] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:17
ld s1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:17
add t2, s1, t2  # [op434] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:17
li s1, 32  # [op435] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:17
vluxei64.v v4, (t2), v2  # [op437] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:17
li t2, 32  # [op438] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:17
vsetvli t2, t2, e32, m1, ta,ma  # [op439] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:17
li t2, 32  # [op440] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add t1, t1, t2  # [op441] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
    # [peephole-li] [op442] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addw t0, t0, t2  # [op443] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
    # [peephole-li] [op444] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk6_head  # [op446] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk7_head:  # block chunk7_head
li t2, 32  # [op447] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
slt t2, t0, t2  # [op448] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s1, 256(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
bne t2, zero, .Lbrc449_true  # [op449] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t0, s1  # [op449] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk7_exit  # [op449] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lbrc449_true:  # [op449] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk7_body  # [op449] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk7_exit:  # block chunk7_exit
li t0, 0  # [op450] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
j .Lstg8_head  # [op451] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
.Lchunk7_body:  # block chunk7_body
li t2, 32  # [op452] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vsetvli t2, t2, e32, m1, ta,ma  # [op453] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t2, 0  # [op454] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li t2, 32  # [op455] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add t1, t1, t2  # [op456] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
    # [peephole-li] [op457] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addw t0, t0, t2  # [op458] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
    # [peephole-li] [op459] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk7_head  # [op461] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lstg8_head:  # block stg8_head
li t2, 2048  # [op462] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
slt t2, t0, t2  # [op463] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
bne t2, zero, .Lbrc464_true  # [op464] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
j .Lstg8_exit  # [op464] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
.Lbrc464_true:  # [op464] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
j .Lstg8_body  # [op464] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
.Lstg8_body:  # block stg8_body
li t2, 32  # [op465] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vsetvli t2, t2, e32, m1, ta,ma  # [op466] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vid.v v1  # [op467] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vadd.vx v1, v1, t0  # [op468] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li t2, 64  # [op469] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vmv.v.x v2, t2  # [op470] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vdiv.vv v2, v1, v2  # [op471] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li t2, 32  # [op472] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vmv.v.x v3, t2  # [op473] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vrem.vv v2, v2, v3  # [op474] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li t2, 64  # [op475] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vmv.v.x v3, t2  # [op476] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vrem.vv v3, v1, v3  # [op477] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li t2, 32  # [op478] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vwadd.vx v4, v2, x0  # [op480] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
    # [peephole-li] [op481] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vsetvli t2, t2, e64, m2, ta,ma  # [op482] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li t2, 4  # [op483] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vmul.vx v2, v4, t2  # [op484] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li t2, 640  # [op485] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
ld s1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
add t2, s1, t2  # [op486] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li s1, 32  # [op487] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vsetvli s1, s1, e32, m1, ta,ma  # [op488] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vluxei64.v v4, (t2), v2  # [op489] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li t2, 32  # [op490] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vwadd.vx v2, v1, x0  # [op492] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
    # [peephole-li] [op493] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vsetvli t2, t2, e64, m2, ta,ma  # [op494] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li t2, 4  # [op495] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vmul.vx v2, v2, t2  # [op496] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li t2, 18048  # [op497] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
ld s1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
add t2, s1, t2  # [op498] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li s1, 32  # [op499] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vsetvli s1, s1, e32, m1, ta,ma  # [op500] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vsuxei64.v v4, (t2), v2  # [op501] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li t2, 32  # [op502] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
addw t0, t0, t2  # [op503] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
j .Lstg8_head  # [op504] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
.Lstg8_exit:  # block stg8_exit
li t0, 0  # [op505] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk9_head  # [op506] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk9_head:  # block chunk9_head
li t2, 2048  # [op507] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
slt t2, t0, t2  # [op508] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s1, 256(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
bne t2, zero, .Lbrc509_true  # [op509] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t0, t1  # [op509] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t1, s1  # [op509] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk9_exit  # [op509] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lbrc509_true:  # [op509] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk9_body  # [op509] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk9_exit:  # block chunk9_exit
li t1, 0  # [op510] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sd t0, 96(sp)  # [op511] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t0, t1  # [op511] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t1, 96(sp)  # [op511] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk10_head  # [op511] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk9_body:  # block chunk9_body
li t2, 32  # [op512] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vsetvli t2, t2, e32, m1, ta,ma  # [op513] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t2, 0  # [op514] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li s1, 32  # [op515] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vmv.v.x v1, t2  # [op517] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vid.v v2  # [op518] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vadd.vx v2, v2, t0  # [op519] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li t2, 32  # [op520] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vwadd.vx v4, v2, x0  # [op522] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
    # [peephole-li] [op523] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vsetvli t2, t2, e64, m2, ta,ma  # [op524] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li t2, 4  # [op525] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vmul.vx v2, v4, t2  # [op526] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li t2, 26240  # [op527] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
ld s1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
add t2, s1, t2  # [op528] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li s1, 32  # [op529] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vsetvli s1, s1, e32, m1, ta,ma  # [op530] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vsuxei64.v v1, (t2), v2  # [op531] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li t2, 32  # [op532] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
addw t2, s10, s11  # [op534] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vid.v v2  # [op535] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vadd.vx v2, v2, t0  # [op536] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li s1, 64  # [op537] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vmv.v.x v3, s1  # [op538] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vdiv.vv v2, v2, v3  # [op539] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li s1, 32  # [op540] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vwadd.vx v4, v2, x0  # [op542] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
    # [peephole-li] [op543] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vsetvli s1, s1, e64, m2, ta,ma  # [op544] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li s1, 4  # [op545] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vmul.vx v2, v4, s1  # [op546] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li s1, 896  # [op547] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
ld a1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
add s1, a1, s1  # [op548] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li a1, 32  # [op549] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vsetvli a1, a1, e32, m1, ta,ma  # [op550] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vluxei64.v v4, (s1), v2  # [op551] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li s1, 32  # [op552] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vadd.vx v2, v4, t2  # [op554] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vid.v v3  # [op555] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vadd.vx v3, v3, t0  # [op556] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li t2, 64  # [op557] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vmv.v.x v4, t2  # [op558] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vrem.vv v3, v3, v4  # [op559] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li t2, 32  # [op560] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vwadd.vx v4, v3, x0  # [op562] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
    # [peephole-li] [op563] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vsetvli t2, t2, e64, m2, ta,ma  # [op564] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li t2, 4  # [op565] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vmul.vx v4, v4, t2  # [op566] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li t2, 0  # [op567] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
ld s1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
add t2, s1, t2  # [op568] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li s1, 32  # [op569] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vsetvli s1, s1, e32, m1, ta,ma  # [op570] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vluxei64.v v3, (t2), v4  # [op571] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li t2, 32  # [op572] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vadd.vv v3, v2, v3  # [op574] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vid.v v2  # [op575] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vadd.vx v2, v2, t0  # [op576] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
    # [peephole-li] [op577] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vwadd.vx v4, v2, x0  # [op579] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
    # [peephole-li] [op580] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vsetvli t2, t2, e64, m2, ta,ma  # [op581] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li t2, 4  # [op582] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vmul.vx v4, v4, t2  # [op583] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li t2, 18048  # [op584] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
ld s1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
add t2, s1, t2  # [op585] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li s1, 32  # [op586] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vsetvli s1, s1, e32, m1, ta,ma  # [op587] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vluxei64.v v2, (t2), v4  # [op588] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li t2, 0  # [op589] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vmv.v.x v4, t2  # [op590] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vmsne.vv v2, v2, v4  # [op591] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li t2, 32  # [op592] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
    # [peephole-li] [op594] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vwadd.vx v4, v3, x0  # [op596] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
    # [peephole-li] [op597] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vsetvli t2, t2, e64, m2, ta,ma  # [op598] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li t2, 4  # [op599] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vmul.vx v4, v4, t2  # [op600] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li t2, 32  # [op601] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vsetvli t2, t2, e32, m1, ta,ma  # [op602] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vmv1r.v v0, v2  # [op603] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
ld t2, 192(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vluxei64.v v3, (t2), v4, v0.t  # [op604] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vmv1r.v v0, v2  # [op605] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vmerge.vvm v1, v1, v3, v0  # [op606] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li t2, 32  # [op607] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vid.v v2  # [op609] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vadd.vx v2, v2, t0  # [op610] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
    # [peephole-li] [op611] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vwadd.vx v4, v2, x0  # [op613] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
    # [peephole-li] [op614] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vsetvli t2, t2, e64, m2, ta,ma  # [op615] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li t2, 4  # [op616] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vmul.vx v2, v4, t2  # [op617] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li t2, 34432  # [op618] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
ld s1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
add t2, s1, t2  # [op619] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li s1, 32  # [op620] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vsetvli s1, s1, e32, m1, ta,ma  # [op621] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
vsuxei64.v v1, (t2), v2  # [op622] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
li t2, 32  # [op623] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:42:9
    # [peephole-li] [op625] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add t1, t1, t2  # [op626] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
    # [peephole-li] [op627] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addw t0, t0, t2  # [op628] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
    # [peephole-li] [op629] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk9_head  # [op631] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk10_head:  # block chunk10_head
li t2, 64  # [op632] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
slt t2, t0, t2  # [op633] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s1, 256(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
bne t2, zero, .Lbrc634_true  # [op634] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t0, s1  # [op634] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk10_exit  # [op634] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lbrc634_true:  # [op634] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk10_body  # [op634] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk10_exit:  # block chunk10_exit
li t0, 0  # [op635] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
j .Lstg11_head  # [op636] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
.Lchunk10_body:  # block chunk10_body
li t2, 32  # [op637] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vsetvli t2, t2, e32, m1, ta,ma  # [op638] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t2, 32  # [op639] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add t1, t1, t2  # [op640] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
    # [peephole-li] [op641] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addw t0, t0, t2  # [op642] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
    # [peephole-li] [op643] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk10_head  # [op645] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lstg11_head:  # block stg11_head
li t2, 2048  # [op646] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
slt t2, t0, t2  # [op647] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
bne t2, zero, .Lbrc648_true  # [op648] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
j .Lstg11_exit  # [op648] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
.Lbrc648_true:  # [op648] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
j .Lstg11_body  # [op648] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
.Lstg11_body:  # block stg11_body
li t2, 32  # [op649] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vsetvli t2, t2, e32, m1, ta,ma  # [op650] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vid.v v1  # [op651] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vadd.vx v1, v1, t0  # [op652] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
li t2, 64  # [op653] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vmv.v.x v2, t2  # [op654] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vdiv.vv v2, v1, v2  # [op655] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
li t2, 32  # [op656] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vmv.v.x v3, t2  # [op657] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vrem.vv v2, v2, v3  # [op658] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
li t2, 64  # [op659] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vmv.v.x v2, t2  # [op660] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vrem.vv v2, v1, v2  # [op661] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
li t2, 32  # [op662] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vwadd.vx v4, v2, x0  # [op664] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
    # [peephole-li] [op665] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vsetvli t2, t2, e64, m2, ta,ma  # [op666] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
li t2, 4  # [op667] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vmul.vx v2, v4, t2  # [op668] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
li t2, 384  # [op669] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
ld s1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
add t2, s1, t2  # [op670] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
li s1, 32  # [op671] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vsetvli s1, s1, e32, m1, ta,ma  # [op672] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vluxei64.v v4, (t2), v2  # [op673] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
li t2, 32  # [op674] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vwadd.vx v2, v1, x0  # [op676] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
    # [peephole-li] [op677] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vsetvli t2, t2, e64, m2, ta,ma  # [op678] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
li t2, 4  # [op679] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vmul.vx v2, v2, t2  # [op680] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
li t2, 42880  # [op681] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
ld s1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
add t2, s1, t2  # [op682] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
li s1, 32  # [op683] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vsetvli s1, s1, e32, m1, ta,ma  # [op684] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vsuxei64.v v4, (t2), v2  # [op685] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
li t2, 32  # [op686] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
addw t0, t0, t2  # [op687] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
j .Lstg11_head  # [op688] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
.Lstg11_exit:  # block stg11_exit
li t0, 0  # [op689] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk12_head  # [op690] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk12_head:  # block chunk12_head
li t2, 2048  # [op691] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
slt t2, t0, t2  # [op692] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s1, 256(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
bne t2, zero, .Lbrc693_true  # [op693] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t0, s1  # [op693] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t2, t1  # [op693] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk12_exit  # [op693] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lbrc693_true:  # [op693] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk12_body  # [op693] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk12_exit:  # block chunk12_exit
li t0, 51072  # [op694] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
ld t1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
add s1, t1, t0  # [op695] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
li t0, 59264  # [op696] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
ld t1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
add a1, t1, t0  # [op697] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
li t1, 64  # [op698] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
li t0, 0  # [op699] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
li s10, 32  # [op700] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
j .Lprk13.head  # [op701] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
.Lchunk12_body:  # block chunk12_body
li t2, 32  # [op702] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vsetvli t2, t2, e32, m1, ta,ma  # [op703] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t2, 32  # [op704] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vid.v v1  # [op706] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vadd.vx v1, v1, t0  # [op707] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
    # [peephole-li] [op708] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vwadd.vx v2, v1, x0  # [op710] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
    # [peephole-li] [op711] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vsetvli t2, t2, e64, m2, ta,ma  # [op712] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
li t2, 4  # [op713] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vmul.vx v2, v2, t2  # [op714] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
li t2, 42880  # [op715] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
ld s1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
add t2, s1, t2  # [op716] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
li s1, 32  # [op717] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vsetvli s1, s1, e32, m1, ta,ma  # [op718] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vluxei64.v v1, (t2), v2  # [op719] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
li t2, 32  # [op720] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vid.v v2  # [op722] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vadd.vx v2, v2, t0  # [op723] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
    # [peephole-li] [op724] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vwadd.vx v4, v2, x0  # [op726] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
    # [peephole-li] [op727] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vsetvli t2, t2, e64, m2, ta,ma  # [op728] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
li t2, 4  # [op729] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vmul.vx v2, v4, t2  # [op730] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
li t2, 34432  # [op731] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
ld s1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
add t2, s1, t2  # [op732] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
li s1, 32  # [op733] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vsetvli s1, s1, e32, m1, ta,ma  # [op734] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vluxei64.v v4, (t2), v2  # [op735] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
li t2, 32  # [op736] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vfmul.vv v1, v1, v4  # [op738] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vid.v v2  # [op739] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vadd.vx v2, v2, t0  # [op740] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
    # [peephole-li] [op741] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vwadd.vx v4, v2, x0  # [op743] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
    # [peephole-li] [op744] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vsetvli t2, t2, e64, m2, ta,ma  # [op745] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
li t2, 4  # [op746] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vmul.vx v2, v4, t2  # [op747] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
li t2, 51072  # [op748] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
ld s1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
add t2, s1, t2  # [op749] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
li s1, 32  # [op750] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vsetvli s1, s1, e32, m1, ta,ma  # [op751] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
vsuxei64.v v1, (t2), v2  # [op752] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
li t2, 32  # [op753] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:17
    # [peephole-li] [op755] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add t1, t1, t2  # [op756] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
    # [peephole-li] [op757] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addw t0, t0, t2  # [op758] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
    # [peephole-li] [op759] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk12_head  # [op761] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lprk13.head:  # block prk13.head
sd t0, 280(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
ld t0, 280(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
slt s11, t0, s10  # [op762] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
ld t0, 280(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
bne s11, zero, .Lbrc763_true  # [op763] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
j .Lprk13.exit  # [op763] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
.Lbrc763_true:  # [op763] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
j .Lprk13.body  # [op763] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
.Lprk13.body:  # block prk13.body
sd t0, 280(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
ld t0, 280(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
mul s11, t0, t1  # [op764] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
li t0, 32  # [op765] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
vsetvli t0, t0, e32, m1, ta,ma  # [op766] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
li t0, 0  # [op767] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
vmv.v.x v1, t0  # [op768] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
    # [peephole-li] [op769] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
j .Lprc14.head  # [op770] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
.Lprk13.exit:  # block prk13.exit
li t0, 0  # [op771] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t1, 32  # [op772] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vsetvli t1, t1, e32, m1, ta,ma  # [op773] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t1, 4286578688  # [op774] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vmv.v.x v1, t1  # [op775] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t1, t2  # [op776] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk15_head  # [op776] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lprc14.head:  # block prc14.head
slt t5, t0, t1  # [op777] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
bne t5, zero, .Lbrc778_true  # [op778] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
j .Lprc14.exit  # [op778] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
.Lbrc778_true:  # [op778] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
j .Lprc14.body  # [op778] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
.Lprc14.body:  # block prc14.body
sub t5, t1, t0  # [op779] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
addiw t5, t5, 0  # [op780] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
vsetvli t5, t5, e32, m1, ta,ma  # [op781] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
add t5, s11, t0  # [op782] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
li t6, 4  # [op783] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
mul t5, t5, t6  # [op784] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
add t5, s1, t5  # [op785] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
vle32.v v2, 0(t5)  # [op786] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
vfredusum.vs v1, v2, v1  # [op787] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
li t5, 32  # [op788] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
add t0, t0, t5  # [op789] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
j .Lprc14.head  # [op790] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
.Lprc14.exit:  # block prc14.exit
li t0, 32  # [op791] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
vsetvli t0, t0, e32, m1, ta,ma  # [op792] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
vmv.x.s t0, v1  # [op793] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
li s11, 4  # [op794] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
ld t5, 280(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
mul s11, t5, s11  # [op795] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
add s11, a1, s11  # [op796] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
sw t0, 0(s11)  # [op797] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
li t0, 1  # [op798] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
ld s11, 280(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
add t0, s11, t0  # [op799] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
j .Lprk13.head  # [op800] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
.Lchunk15_head:  # block chunk15_head
li t2, 32  # [op801] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
slt t2, t0, t2  # [op802] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s1, 256(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
bne t2, zero, .Lbrc803_true  # [op803] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t0, t1  # [op803] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t1, s1  # [op803] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk15_exit  # [op803] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lbrc803_true:  # [op803] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk15_body  # [op803] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk15_exit:  # block chunk15_exit
li t1, 32  # [op804] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vsetvli t1, t1, e32, m1, ta,ma  # [op805] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vmv.x.s t2, v1  # [op806] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t1, 0  # [op807] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li s1, 0  # [op808] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vmv.v.x v1, s1  # [op809] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vmv1r.v v2, v1  # [op810] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sd t0, 96(sp)  # [op810] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t0, t1  # [op810] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t1, 96(sp)  # [op810] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk16_head  # [op810] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk15_body:  # block chunk15_body
li t2, 32  # [op811] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vsetvli t2, t2, e32, m1, ta,ma  # [op812] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t2, 32  # [op813] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
vmv.v.x v2, a4  # [op815] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
vid.v v3  # [op816] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
vadd.vx v3, v3, t0  # [op817] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
    # [peephole-li] [op818] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
vwadd.vx v4, v3, x0  # [op820] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
    # [peephole-li] [op821] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
vsetvli t2, t2, e64, m2, ta,ma  # [op822] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
li t2, 4  # [op823] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
vmul.vx v4, v4, t2  # [op824] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
li t2, 59264  # [op825] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
ld s1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
add t2, s1, t2  # [op826] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
li s1, 32  # [op827] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
vsetvli s1, s1, e32, m1, ta,ma  # [op828] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
vluxei64.v v3, (t2), v4  # [op829] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
li t2, 32  # [op830] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
vfmul.vv v2, v3, v2  # [op832] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:44:10
li t2, 4286578688  # [op833] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
vmv.v.x v3, t2  # [op834] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
vid.v v4  # [op835] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
vadd.vx v4, v4, t0  # [op836] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
li t2, 32  # [op837] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
vwadd.vx v6, v4, x0  # [op839] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
    # [peephole-li] [op840] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
vsetvli t2, t2, e64, m2, ta,ma  # [op841] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
li t2, 4  # [op842] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
vmul.vx v4, v6, t2  # [op843] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
li t2, 640  # [op844] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
ld s1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
add t2, s1, t2  # [op845] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
li s1, 32  # [op846] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
vsetvli s1, s1, e32, m1, ta,ma  # [op847] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
vluxei64.v v6, (t2), v4  # [op848] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
li t2, 0  # [op849] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
vmv.v.x v4, t2  # [op850] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
vmsne.vv v4, v6, v4  # [op851] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
li t2, 32  # [op852] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
vmv1r.v v0, v4  # [op854] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
vmerge.vvm v2, v3, v2, v0  # [op855] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
vid.v v3  # [op856] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
vadd.vx v3, v3, t0  # [op857] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
    # [peephole-li] [op858] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
vwadd.vx v4, v3, x0  # [op860] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
    # [peephole-li] [op861] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
vsetvli t2, t2, e64, m2, ta,ma  # [op862] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
li t2, 4  # [op863] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
vmul.vx v4, v4, t2  # [op864] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
li t2, 59392  # [op865] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
ld s1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
add t2, s1, t2  # [op866] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
li s1, 32  # [op867] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
vsetvli s1, s1, e32, m1, ta,ma  # [op868] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
vsuxei64.v v2, (t2), v4  # [op869] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
li t2, 32  # [op870] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:45:10
li t2, 4286578688  # [op872] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:48:9
vmv.v.x v3, t2  # [op873] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:48:9
vfredmax.vs v2, v2, v3  # [op874] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:48:9
vmv.x.s t2, v2  # [op875] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:48:9
li s1, 32  # [op876] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add t1, t1, s1  # [op877] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
    # [peephole-li] [op878] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addw t0, t0, s1  # [op879] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
    # [peephole-li] [op880] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
    # [peephole-li] [op882] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vmv.v.x v2, t2  # [op884] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vmflt.vv v3, v1, v2  # [op885] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vmv1r.v v0, v3  # [op886] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vmerge.vvm v1, v1, v2, v0  # [op887] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk15_head  # [op888] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk16_head:  # block chunk16_head
li s1, 32  # [op889] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
slt s1, t0, s1  # [op890] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld a1, 256(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
bne s1, zero, .Lbrc891_true  # [op891] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t0, t1  # [op891] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t1, a1  # [op891] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vmv1r.v v1, v2  # [op891] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk16_exit  # [op891] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lbrc891_true:  # [op891] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk16_body  # [op891] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk16_exit:  # block chunk16_exit
li t1, 32  # [op892] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vsetvli t1, t1, e32, m1, ta,ma  # [op893] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vmv.x.s t2, v1  # [op894] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t1, 0  # [op895] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sd t0, 96(sp)  # [op896] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t0, t1  # [op896] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t1, 96(sp)  # [op896] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk17_head  # [op896] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk16_body:  # block chunk16_body
li s1, 32  # [op897] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vsetvli s1, s1, e32, m1, ta,ma  # [op898] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li s1, 32  # [op899] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:16
vmv.v.x v1, t2  # [op901] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:16
vid.v v3  # [op902] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:16
vadd.vx v3, v3, t0  # [op903] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:16
    # [peephole-li] [op904] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:16
vwadd.vx v4, v3, x0  # [op906] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:16
    # [peephole-li] [op907] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:16
vsetvli s1, s1, e64, m2, ta,ma  # [op908] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:16
li s1, 4  # [op909] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:16
vmul.vx v4, v4, s1  # [op910] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:16
li s1, 59392  # [op911] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:16
ld a1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:16
add s1, a1, s1  # [op912] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:16
li a1, 32  # [op913] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:16
vsetvli a1, a1, e32, m1, ta,ma  # [op914] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:16
vluxei64.v v3, (s1), v4  # [op915] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:16
li s1, 32  # [op916] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:16
vfsub.vv v3, v3, v1  # [op918] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:16
li s1, 1069066811  # [op919] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vmv.v.x v1, s1  # [op920] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vfmul.vv v1, v3, v1  # [op921] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
li s1, 1262485504  # [op922] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vmv.v.x v4, s1  # [op923] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vfadd.vv v5, v1, v4  # [op924] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vfsub.vv v4, v5, v4  # [op925] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vfsub.vv v1, v1, v4  # [op926] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
li s1, 958534664  # [op927] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vmv.v.x v5, s1  # [op928] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
li s1, 984576714  # [op929] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vmv.v.x v6, s1  # [op930] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vfmacc.vv v6, v5, v1  # [op931] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
li s1, 1008571674  # [op932] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vmv.v.x v5, s1  # [op933] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vfmacc.vv v5, v6, v1  # [op934] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
li s1, 1029920722  # [op935] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vmv.v.x v6, s1  # [op936] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vfmacc.vv v6, v5, v1  # [op937] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
li s1, 1047920112  # [op938] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vmv.v.x v5, s1  # [op939] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vfmacc.vv v5, v6, v1  # [op940] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
li s1, 1060205080  # [op941] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vmv.v.x v6, s1  # [op942] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vfmacc.vv v6, v5, v1  # [op943] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
li s1, 1065353216  # [op944] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vmv.v.x v5, s1  # [op945] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vmv.v.v v7, v5  # [op946] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vfmacc.vv v7, v1, v6  # [op946] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vfcvt.rtz.x.f.v v1, v4  # [op947] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
li s1, 1  # [op948] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vmv.v.x v4, s1  # [op949] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vsra.vv v4, v1, v4  # [op950] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vsub.vv v6, v1, v4  # [op951] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
li s1, 127  # [op952] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vmv.v.x v1, s1  # [op953] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
li s1, 23  # [op954] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vmv.v.x v5, s1  # [op955] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vadd.vv v4, v4, v1  # [op956] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vadd.vv v1, v6, v1  # [op957] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vsll.vv v4, v4, v5  # [op958] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vsll.vv v1, v1, v5  # [op959] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vmv.v.v v5, v4  # [op960] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vmv.v.v v4, v1  # [op961] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vfmul.vv v1, v7, v5  # [op962] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vfmul.vv v1, v1, v4  # [op963] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
li s1, 2139095040  # [op964] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vmv.v.x v4, s1  # [op965] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
li s1, 0  # [op966] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vmv.v.x v5, s1  # [op967] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
li s1, 1118961664  # [op968] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vmv.v.x v6, s1  # [op969] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vmflt.vv v6, v6, v3  # [op970] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vmv1r.v v0, v6  # [op971] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vmerge.vvm v1, v1, v4, v0  # [op972] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
li s1, 3268411392  # [op973] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vmv.v.x v4, s1  # [op974] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vmflt.vv v3, v3, v4  # [op975] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vmv1r.v v0, v3  # [op976] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vmerge.vvm v1, v1, v5, v0  # [op977] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vid.v v3  # [op978] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vadd.vx v3, v3, t0  # [op979] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
li s1, 32  # [op980] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vwadd.vx v4, v3, x0  # [op982] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
    # [peephole-li] [op983] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vsetvli s1, s1, e64, m2, ta,ma  # [op984] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
li s1, 4  # [op985] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vmul.vx v4, v4, s1  # [op986] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
li s1, 59520  # [op987] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
ld a1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
add s1, a1, s1  # [op988] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
li a1, 32  # [op989] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vsetvli a1, a1, e32, m1, ta,ma  # [op990] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
vsuxei64.v v1, (s1), v4  # [op991] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
li s1, 32  # [op992] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:49:9
li s1, 0  # [op994] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:13
vmv.v.x v3, s1  # [op995] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:13
vfredusum.vs v1, v1, v3  # [op996] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:13
vmv.x.s s1, v1  # [op997] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:13
li a1, 32  # [op998] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add t1, t1, a1  # [op999] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
    # [peephole-li] [op1000] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addw t0, t0, a1  # [op1001] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
    # [peephole-li] [op1002] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
    # [peephole-li] [op1004] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vmv.v.x v1, s1  # [op1006] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vfadd.vv v1, v2, v1  # [op1007] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vmv1r.v v2, v1  # [op1008] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk16_head  # [op1008] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk17_head:  # block chunk17_head
li s1, 32  # [op1009] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
slt s1, t0, s1  # [op1010] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld a1, 256(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
bne s1, zero, .Lbrc1011_true  # [op1011] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t0, t1  # [op1011] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t1, a1  # [op1011] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk17_exit  # [op1011] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lbrc1011_true:  # [op1011] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk17_body  # [op1011] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk17_exit:  # block chunk17_exit
li t1, 0  # [op1012] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sd t0, 96(sp)  # [op1013] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t0, t1  # [op1013] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t1, 96(sp)  # [op1013] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk18_head  # [op1013] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk17_body:  # block chunk17_body
li s1, 32  # [op1014] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vsetvli s1, s1, e32, m1, ta,ma  # [op1015] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li s1, 32  # [op1016] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:9
vmv.v.x v1, t2  # [op1018] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:9
vid.v v2  # [op1019] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:9
vadd.vx v2, v2, t0  # [op1020] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:9
    # [peephole-li] [op1021] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:9
vwadd.vx v4, v2, x0  # [op1023] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:9
    # [peephole-li] [op1024] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:9
vsetvli s1, s1, e64, m2, ta,ma  # [op1025] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:9
li s1, 4  # [op1026] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:9
vmul.vx v2, v4, s1  # [op1027] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:9
li s1, 59520  # [op1028] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:9
ld a1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:9
add s1, a1, s1  # [op1029] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:9
li a1, 32  # [op1030] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:9
vsetvli a1, a1, e32, m1, ta,ma  # [op1031] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:9
vluxei64.v v4, (s1), v2  # [op1032] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:9
li s1, 32  # [op1033] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:9
vfdiv.vv v1, v4, v1  # [op1035] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:9
vid.v v2  # [op1036] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:9
vadd.vx v2, v2, t0  # [op1037] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:9
    # [peephole-li] [op1038] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:9
vwadd.vx v4, v2, x0  # [op1040] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:9
    # [peephole-li] [op1041] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:9
vsetvli s1, s1, e64, m2, ta,ma  # [op1042] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:9
li s1, 4  # [op1043] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:9
vmul.vx v2, v4, s1  # [op1044] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:9
li s1, 59648  # [op1045] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:9
ld a1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:9
add s1, a1, s1  # [op1046] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:9
li a1, 32  # [op1047] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:9
vsetvli a1, a1, e32, m1, ta,ma  # [op1048] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:9
vsuxei64.v v1, (s1), v2  # [op1049] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:9
li s1, 32  # [op1050] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:50:9
ld s1, 176(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:26
vmv.v.x v1, s1  # [op1052] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:26
vid.v v2  # [op1053] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:26
vadd.vx v2, v2, t0  # [op1054] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:26
li s1, 32  # [op1055] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:26
vwadd.vx v4, v2, x0  # [op1057] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:26
    # [peephole-li] [op1058] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:26
vsetvli s1, s1, e64, m2, ta,ma  # [op1059] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:26
li s1, 4  # [op1060] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:26
vmul.vx v2, v4, s1  # [op1061] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:26
li s1, 256  # [op1062] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:26
ld a1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:26
add s1, a1, s1  # [op1063] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:26
li a1, 32  # [op1064] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:26
vsetvli a1, a1, e32, m1, ta,ma  # [op1065] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:26
vluxei64.v v4, (s1), v2  # [op1066] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:26
li s1, 32  # [op1067] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:26
vmul.vv v1, v4, v1  # [op1069] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:26
vid.v v2  # [op1070] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:26
vadd.vx v2, v2, t0  # [op1071] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:26
    # [peephole-li] [op1072] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:26
vwadd.vx v4, v2, x0  # [op1074] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:26
    # [peephole-li] [op1075] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:26
vsetvli s1, s1, e64, m2, ta,ma  # [op1076] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:26
li s1, 4  # [op1077] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:26
vmul.vx v2, v4, s1  # [op1078] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:26
li s1, 59776  # [op1079] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:26
ld a1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:26
add s1, a1, s1  # [op1080] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:26
li a1, 32  # [op1081] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:26
vsetvli a1, a1, e32, m1, ta,ma  # [op1082] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:26
vsuxei64.v v1, (s1), v2  # [op1083] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:26
li s1, 32  # [op1084] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:26
    # [peephole-li] [op1086] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add t1, t1, s1  # [op1087] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
    # [peephole-li] [op1088] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addw t0, t0, s1  # [op1089] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
    # [peephole-li] [op1090] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk17_head  # [op1092] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk18_head:  # block chunk18_head
li t2, 2048  # [op1093] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
slt t2, t0, t2  # [op1094] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s1, 256(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
bne t2, zero, .Lbrc1095_true  # [op1095] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t0, t1  # [op1095] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t1, s1  # [op1095] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk18_exit  # [op1095] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lbrc1095_true:  # [op1095] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk18_body  # [op1095] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk18_exit:  # block chunk18_exit
li t1, 0  # [op1096] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sd t0, 96(sp)  # [op1097] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t0, t1  # [op1097] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t1, 96(sp)  # [op1097] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk19_head  # [op1097] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk18_body:  # block chunk18_body
li t2, 32  # [op1098] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vsetvli t2, t2, e32, m1, ta,ma  # [op1099] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t2, 32  # [op1100] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:17
vid.v v1  # [op1102] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:17
vadd.vx v1, v1, t0  # [op1103] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:17
li t2, 64  # [op1104] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:17
vmv.v.x v2, t2  # [op1105] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:17
vdiv.vv v1, v1, v2  # [op1106] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:17
li t2, 32  # [op1107] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:17
vwadd.vx v2, v1, x0  # [op1109] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:17
    # [peephole-li] [op1110] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:17
vsetvli t2, t2, e64, m2, ta,ma  # [op1111] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:17
li t2, 8  # [op1112] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:17
vmul.vx v2, v2, t2  # [op1113] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:17
li t2, 59904  # [op1114] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:17
ld s1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:17
add t2, s1, t2  # [op1115] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:17
li s1, 32  # [op1116] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:17
vluxei64.v v4, (t2), v2  # [op1118] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:17
li t2, 32  # [op1119] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:17
vsetvli t2, t2, e32, m1, ta,ma  # [op1120] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:17
addw t2, t3, t4  # [op1121] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vid.v v1  # [op1122] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vadd.vx v1, v1, t0  # [op1123] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
li s1, 64  # [op1124] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vmv.v.x v2, s1  # [op1125] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vdiv.vv v1, v1, v2  # [op1126] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
li s1, 32  # [op1127] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vwadd.vx v2, v1, x0  # [op1129] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
    # [peephole-li] [op1130] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vsetvli s1, s1, e64, m2, ta,ma  # [op1131] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
li s1, 4  # [op1132] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vmul.vx v2, v2, s1  # [op1133] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
li s1, 59776  # [op1134] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
ld a1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
add s1, a1, s1  # [op1135] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
li a1, 32  # [op1136] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vsetvli a1, a1, e32, m1, ta,ma  # [op1137] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vluxei64.v v1, (s1), v2  # [op1138] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
li s1, 32  # [op1139] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vadd.vx v1, v1, t2  # [op1141] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vid.v v2  # [op1142] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vadd.vx v2, v2, t0  # [op1143] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
li t2, 64  # [op1144] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vmv.v.x v3, t2  # [op1145] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vrem.vv v2, v2, v3  # [op1146] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
li t2, 32  # [op1147] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vwadd.vx v4, v2, x0  # [op1149] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
    # [peephole-li] [op1150] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vsetvli t2, t2, e64, m2, ta,ma  # [op1151] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
li t2, 4  # [op1152] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vmul.vx v2, v4, t2  # [op1153] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
li t2, 0  # [op1154] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
ld s1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
add t2, s1, t2  # [op1155] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
li s1, 32  # [op1156] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vsetvli s1, s1, e32, m1, ta,ma  # [op1157] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vluxei64.v v4, (t2), v2  # [op1158] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
li t2, 32  # [op1159] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vadd.vv v2, v1, v4  # [op1161] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vid.v v1  # [op1162] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vadd.vx v1, v1, t0  # [op1163] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
    # [peephole-li] [op1164] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vwadd.vx v4, v1, x0  # [op1166] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
    # [peephole-li] [op1167] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vsetvli t2, t2, e64, m2, ta,ma  # [op1168] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
li t2, 4  # [op1169] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vmul.vx v4, v4, t2  # [op1170] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
li t2, 18048  # [op1171] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
ld s1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
add t2, s1, t2  # [op1172] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
li s1, 32  # [op1173] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vsetvli s1, s1, e32, m1, ta,ma  # [op1174] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vluxei64.v v1, (t2), v4  # [op1175] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
li t2, 0  # [op1176] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vmv.v.x v3, t2  # [op1177] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vmsne.vv v1, v1, v3  # [op1178] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
li t2, 32  # [op1179] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
    # [peephole-li] [op1181] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vwadd.vx v4, v2, x0  # [op1183] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
    # [peephole-li] [op1184] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vsetvli t2, t2, e64, m2, ta,ma  # [op1185] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
li t2, 4  # [op1186] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vmul.vx v2, v4, t2  # [op1187] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
li t2, 32  # [op1188] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vsetvli t2, t2, e32, m1, ta,ma  # [op1189] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vmv1r.v v0, v1  # [op1190] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
ld t2, 248(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vluxei64.v v4, (t2), v2, v0.t  # [op1191] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
li t2, 32  # [op1192] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vid.v v2  # [op1194] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vadd.vx v2, v2, t0  # [op1195] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
    # [peephole-li] [op1196] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vwadd.vx v6, v2, x0  # [op1198] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
    # [peephole-li] [op1199] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vsetvli t2, t2, e64, m2, ta,ma  # [op1200] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
li t2, 4  # [op1201] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vmul.vx v2, v6, t2  # [op1202] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
li t2, 26240  # [op1203] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
ld s1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
add t2, s1, t2  # [op1204] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
li s1, 32  # [op1205] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vsetvli s1, s1, e32, m1, ta,ma  # [op1206] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vluxei64.v v5, (t2), v2  # [op1207] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
li t2, 32  # [op1208] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vmv1r.v v0, v1  # [op1210] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vmerge.vvm v1, v5, v4, v0  # [op1211] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vid.v v2  # [op1212] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vadd.vx v2, v2, t0  # [op1213] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
    # [peephole-li] [op1214] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vwadd.vx v4, v2, x0  # [op1216] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
    # [peephole-li] [op1217] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vsetvli t2, t2, e64, m2, ta,ma  # [op1218] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
li t2, 4  # [op1219] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vmul.vx v2, v4, t2  # [op1220] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
li t2, 60160  # [op1221] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
ld s1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
add t2, s1, t2  # [op1222] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
li s1, 32  # [op1223] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vsetvli s1, s1, e32, m1, ta,ma  # [op1224] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
vsuxei64.v v1, (t2), v2  # [op1225] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
li t2, 32  # [op1226] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:51:9
    # [peephole-li] [op1228] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add t1, t1, t2  # [op1229] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
    # [peephole-li] [op1230] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addw t0, t0, t2  # [op1231] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
    # [peephole-li] [op1232] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk18_head  # [op1234] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk19_head:  # block chunk19_head
li t2, 32  # [op1235] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
slt t2, t0, t2  # [op1236] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s1, 256(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
bne t2, zero, .Lbrc1237_true  # [op1237] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t0, s1  # [op1237] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk19_exit  # [op1237] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lbrc1237_true:  # [op1237] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk19_body  # [op1237] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk19_exit:  # block chunk19_exit
li t0, 0  # [op1238] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
j .Lstg20_head  # [op1239] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
.Lchunk19_body:  # block chunk19_body
li t2, 32  # [op1240] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vsetvli t2, t2, e32, m1, ta,ma  # [op1241] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t2, 32  # [op1242] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add t1, t1, t2  # [op1243] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
    # [peephole-li] [op1244] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addw t0, t0, t2  # [op1245] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
    # [peephole-li] [op1246] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk19_head  # [op1248] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lstg20_head:  # block stg20_head
li t2, 2048  # [op1249] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
slt t2, t0, t2  # [op1250] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
bne t2, zero, .Lbrc1251_true  # [op1251] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
j .Lstg20_exit  # [op1251] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
.Lbrc1251_true:  # [op1251] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
j .Lstg20_body  # [op1251] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
.Lstg20_body:  # block stg20_body
li t2, 32  # [op1252] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vsetvli t2, t2, e32, m1, ta,ma  # [op1253] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vid.v v1  # [op1254] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vadd.vx v1, v1, t0  # [op1255] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
li t2, 64  # [op1256] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vmv.v.x v2, t2  # [op1257] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vdiv.vv v2, v1, v2  # [op1258] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
li t2, 32  # [op1259] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vmv.v.x v3, t2  # [op1260] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vrem.vv v2, v2, v3  # [op1261] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
li t2, 64  # [op1262] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vmv.v.x v3, t2  # [op1263] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vrem.vv v3, v1, v3  # [op1264] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
li t2, 32  # [op1265] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vwadd.vx v4, v2, x0  # [op1267] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
    # [peephole-li] [op1268] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vsetvli t2, t2, e64, m2, ta,ma  # [op1269] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
li t2, 4  # [op1270] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vmul.vx v2, v4, t2  # [op1271] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
li t2, 59648  # [op1272] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
ld s1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
add t2, s1, t2  # [op1273] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
li s1, 32  # [op1274] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vsetvli s1, s1, e32, m1, ta,ma  # [op1275] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vluxei64.v v4, (t2), v2  # [op1276] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
li t2, 32  # [op1277] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vwadd.vx v2, v1, x0  # [op1279] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
    # [peephole-li] [op1280] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vsetvli t2, t2, e64, m2, ta,ma  # [op1281] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
li t2, 4  # [op1282] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vmul.vx v2, v2, t2  # [op1283] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
li t2, 68480  # [op1284] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
ld s1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
add t2, s1, t2  # [op1285] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
li s1, 32  # [op1286] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vsetvli s1, s1, e32, m1, ta,ma  # [op1287] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vsuxei64.v v4, (t2), v2  # [op1288] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
li t2, 32  # [op1289] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
addw t0, t0, t2  # [op1290] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
j .Lstg20_head  # [op1291] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
.Lstg20_exit:  # block stg20_exit
li t0, 0  # [op1292] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk21_head  # [op1293] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk21_head:  # block chunk21_head
li t2, 2048  # [op1294] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
slt t2, t0, t2  # [op1295] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s1, 256(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
bne t2, zero, .Lbrc1296_true  # [op1296] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t0, s1  # [op1296] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv s10, t1  # [op1296] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk21_exit  # [op1296] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lbrc1296_true:  # [op1296] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk21_body  # [op1296] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk21_exit:  # block chunk21_exit
li t0, 76672  # [op1297] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
ld t1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
add s1, t1, t0  # [op1298] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
li t0, 84864  # [op1299] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
ld t1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
add a1, t1, t0  # [op1300] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
li t0, 0  # [op1301] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
li s11, 64  # [op1302] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
j .Lkrcols22.head  # [op1303] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
.Lchunk21_body:  # block chunk21_body
li t2, 32  # [op1304] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vsetvli t2, t2, e32, m1, ta,ma  # [op1305] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
li t2, 32  # [op1306] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vid.v v1  # [op1308] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vadd.vx v1, v1, t0  # [op1309] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
    # [peephole-li] [op1310] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vwadd.vx v2, v1, x0  # [op1312] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
    # [peephole-li] [op1313] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vsetvli t2, t2, e64, m2, ta,ma  # [op1314] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
li t2, 4  # [op1315] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vmul.vx v2, v2, t2  # [op1316] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
li t2, 68480  # [op1317] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
ld s1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
add t2, s1, t2  # [op1318] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
li s1, 32  # [op1319] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vsetvli s1, s1, e32, m1, ta,ma  # [op1320] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vluxei64.v v1, (t2), v2  # [op1321] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
li t2, 32  # [op1322] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vid.v v2  # [op1324] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vadd.vx v2, v2, t0  # [op1325] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
    # [peephole-li] [op1326] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vwadd.vx v4, v2, x0  # [op1328] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
    # [peephole-li] [op1329] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vsetvli t2, t2, e64, m2, ta,ma  # [op1330] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
li t2, 4  # [op1331] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vmul.vx v2, v4, t2  # [op1332] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
li t2, 60160  # [op1333] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
ld s1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
add t2, s1, t2  # [op1334] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
li s1, 32  # [op1335] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vsetvli s1, s1, e32, m1, ta,ma  # [op1336] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vluxei64.v v4, (t2), v2  # [op1337] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
li t2, 32  # [op1338] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vfmul.vv v1, v1, v4  # [op1340] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vid.v v2  # [op1341] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vadd.vx v2, v2, t0  # [op1342] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
    # [peephole-li] [op1343] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vwadd.vx v4, v2, x0  # [op1345] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
    # [peephole-li] [op1346] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vsetvli t2, t2, e64, m2, ta,ma  # [op1347] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
li t2, 4  # [op1348] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vmul.vx v2, v4, t2  # [op1349] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
li t2, 76672  # [op1350] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
ld s1, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
add t2, s1, t2  # [op1351] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
li s1, 32  # [op1352] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vsetvli s1, s1, e32, m1, ta,ma  # [op1353] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
vsuxei64.v v1, (t2), v2  # [op1354] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
li t2, 32  # [op1355] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:18
    # [peephole-li] [op1357] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add t1, t1, t2  # [op1358] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
    # [peephole-li] [op1359] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addw t0, t0, t2  # [op1360] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
    # [peephole-li] [op1361] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk21_head  # [op1363] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lkrcols22.head:  # block krcols22.head
slt t1, t0, s11  # [op1364] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
bne t1, zero, .Lbrc1365_true  # [op1365] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
j .Lkrcols22.exit  # [op1365] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
.Lbrc1365_true:  # [op1365] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
j .Lkrcols22.body  # [op1365] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
.Lkrcols22.body:  # block krcols22.body
li t1, 64  # [op1366] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
divu t1, t0, t1  # [op1367] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
li t2, 64  # [op1368] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
mul t2, t1, t2  # [op1369] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
sub t2, t0, t2  # [op1370] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
li t3, 2048  # [op1371] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
mul t1, t1, t3  # [op1372] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
add t1, t1, t2  # [op1373] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
li t2, 4  # [op1374] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
mul t1, t1, t2  # [op1375] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
add t1, s1, t1  # [op1376] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
li t2, 32  # [op1377] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
vsetvli t2, t2, e32, m1, ta,ma  # [op1378] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
li t2, 0  # [op1379] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
vmv.v.x v1, t2  # [op1380] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
    # [peephole-li] [op1381] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
li t3, 32  # [op1382] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
sd t1, 96(sp)  # [op1383] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
mv t1, t2  # [op1383] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
ld t2, 96(sp)  # [op1383] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
j .Lkrrows23.head  # [op1383] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
.Lkrcols22.exit:  # block krcols22.exit
ld t0, 224(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:24
mulw t2, t0, s4  # [op1384] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:24
ld t0, 232(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:44
mulw s1, t0, s2  # [op1385] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:44
ld t0, 272(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:64
mulw a1, t0, s3  # [op1386] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:64
li t0, 0  # [op1387] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t1, s10  # [op1388] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk24_head  # [op1388] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lkrrows23.head:  # block krrows23.head
slt t4, t1, t3  # [op1389] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
bne t4, zero, .Lbrc1390_true  # [op1390] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
j .Lkrrows23.exit  # [op1390] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
.Lbrc1390_true:  # [op1390] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
j .Lkrrows23.body  # [op1390] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
.Lkrrows23.body:  # block krrows23.body
li t4, 32  # [op1391] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
vsetvli t4, t4, e32, m1, ta,ma  # [op1392] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
vle32.v v2, 0(t2)  # [op1393] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
vfadd.vv v1, v1, v2  # [op1394] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
li t4, 1  # [op1395] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
add t1, t1, t4  # [op1396] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
li t4, 256  # [op1397] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
add t2, t2, t4  # [op1398] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
j .Lkrrows23.head  # [op1399] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
.Lkrrows23.exit:  # block krrows23.exit
li t1, 4  # [op1400] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
mul t1, t0, t1  # [op1401] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
add t1, a1, t1  # [op1402] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
li t2, 32  # [op1403] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
vsetvli t2, t2, e32, m1, ta,ma  # [op1404] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
vse32.v v1, 0(t1)  # [op1405] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
li t1, 32  # [op1406] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
add t0, t0, t1  # [op1407] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
j .Lkrcols22.head  # [op1408] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:53:11
.Lchunk24_head:  # block chunk24_head
li s10, 64  # [op1409] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
slt s10, t0, s10  # [op1410] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s11, 256(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
bne s10, zero, .Lbrc1411_true  # [op1411] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t0, t1  # [op1411] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t1, s11  # [op1411] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk24_exit  # [op1411] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lbrc1411_true:  # [op1411] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk24_body  # [op1411] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk24_exit:  # block chunk24_exit
ld t1, 256(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
sd t0, 96(sp)  # [op1412] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
mv t0, t1  # [op1412] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld t1, 96(sp)  # [op1412] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lprog_next  # [op1412] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lchunk24_body:  # block chunk24_body
li s10, 32  # [op1413] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
vsetvli s10, s10, e32, m1, ta,ma  # [op1414] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addw s10, t2, s1  # [op1415] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
addw s10, s10, a1  # [op1416] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
li s11, 32  # [op1417] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
vid.v v1  # [op1419] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
vadd.vx v1, v1, t0  # [op1420] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
    # [peephole-li] [op1421] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
vwadd.vx v2, v1, x0  # [op1423] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
    # [peephole-li] [op1424] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
vsetvli s11, s11, e64, m2, ta,ma  # [op1425] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
li s11, 4  # [op1426] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
vmul.vx v2, v2, s11  # [op1427] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
li s11, 0  # [op1428] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
ld t3, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
add s11, t3, s11  # [op1429] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
li t3, 32  # [op1430] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
vsetvli t3, t3, e32, m1, ta,ma  # [op1431] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
vluxei64.v v1, (s11), v2  # [op1432] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
li s11, 32  # [op1433] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
vadd.vx v1, v1, s10  # [op1435] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
vid.v v1  # [op1436] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
vadd.vx v1, v1, t0  # [op1437] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
li s10, 32  # [op1438] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
vwadd.vx v2, v1, x0  # [op1440] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
    # [peephole-li] [op1441] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
vsetvli s10, s10, e64, m2, ta,ma  # [op1442] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
li s10, 4  # [op1443] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
vmul.vx v2, v2, s10  # [op1444] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
li s10, 84864  # [op1445] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
ld s11, 216(sp)  # [op-1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
add s10, s11, s10  # [op1446] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
li s11, 32  # [op1447] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
vsetvli s11, s11, e32, m1, ta,ma  # [op1448] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
vluxei64.v v1, (s10), v2  # [op1449] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
li s10, 32  # [op1450] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
mv s10, t0  # [op1452] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
mv s11, t2  # [op1453] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
add s10, s10, s11  # [op1454] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
mv s11, s1  # [op1455] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
add s10, s10, s11  # [op1456] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
mv s11, a1  # [op1457] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
add s10, s10, s11  # [op1458] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
li s11, 4  # [op1459] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
mul s10, s10, s11  # [op1460] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
add s10, s7, s10  # [op1461] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
vse32.v v1, 0(s10)  # [op1462] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:54:5
li s10, 32  # [op1463] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
add t1, t1, s10  # [op1464] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
    # [peephole-li] [op1465] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addw t0, t0, s10  # [op1466] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
    # [peephole-li] [op1467] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lchunk24_head  # [op1469] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lprog_next:  # block prog_next
add t0, t0, s9  # [op1470] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
j .Lprog_head  # [op1471] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
.Lprog_exit:  # block prog_exit
sd t0, 0(a2)  # [op1472] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld ra, 0(sp)  # [op1473] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s1, 8(sp)  # [op1473] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s2, 16(sp)  # [op1473] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s3, 24(sp)  # [op1473] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s4, 32(sp)  # [op1473] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s5, 40(sp)  # [op1473] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s6, 48(sp)  # [op1473] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s7, 56(sp)  # [op1473] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s8, 64(sp)  # [op1473] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s9, 72(sp)  # [op1473] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s10, 80(sp)  # [op1473] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ld s11, 88(sp)  # [op1473] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
addi sp, sp, 288  # [op1473] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
ret  # [op1473] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/attention_forward_triton.py:20:1
    .size operator_entry, .-operator_entry
    .section .note.GNU-stack,"",@progbits
