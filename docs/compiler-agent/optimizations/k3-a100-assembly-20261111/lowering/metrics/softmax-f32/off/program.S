# a100c emitted program: softmax_kernel
# source: tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py
# specialization identity: 2aff10c8102471c3
# compiler revision: b5c42fbb75a242a8
# target model: a100-rvv1-vlen1024/1 (VLEN=1024, file=4096B)
# options: no-kept-axis-reduction,no-neutral-reduction-trim,no-matrix-row-reuse
# argument layout: a01134d1601afbe4
# every instruction below traces to a selected MIR op: [opN] carries the source location
# passes: passes=default
    .text
    .globl operator_workspace_private
    .type operator_workspace_private, @function
operator_workspace_private:
    li a0, 16392
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
    # [peephole] removed 0 redundant vsetvli, 24 redundant li
operator_entry:  # fn operator_entry
addi sp, sp, -80
sd ra, 0(sp)
sd s1, 8(sp)
sd s2, 16(sp)
sd s3, 24(sp)
sd s4, 32(sp)
sd s5, 40(sp)
sd s6, 48(sp)
mv t2, a0
.Lentry:  # block entry
ld t1, 0(t2)  # [op0] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld t0, 0(t1)  # [op1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld t1, 8(t1)  # [op2] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld a5, 24(t2)  # [op3] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
lwu s1, 40(t2)  # [op4] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
lwu a1, 44(t2)  # [op5] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld t1, 8(t1)  # [op6] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
addiw a3, t1, 0  # [op7] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld a6, 0(t0)  # [op8] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld a7, 56(t0)  # [op9] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld t0, 8(t0)  # [op10] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld a4, 0(t0)  # [op11] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
li t0, 1  # [op12] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
mul s2, t0, a4  # [op13] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
mv t0, s1  # [op14] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
mv s3, a1  # [op15] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
li t1, 0  # [op16] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
j .Lprog_head  # [op17] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
.Lprog_head:  # block prog_head
slt s1, t0, s2  # [op18] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
bne s1, zero, .Lbrc19_true  # [op19] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
sd t1, 56(sp)  # [op19] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
mv t1, t0  # [op19] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld t0, 56(sp)  # [op19] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
j .Lprog_exit  # [op19] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
.Lbrc19_true:  # [op19] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
mv s1, t0  # [op19] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
j .Lprog_body  # [op19] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
.Lprog_body:  # block prog_body
addiw s4, s1, 0  # [op20] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
addiw t0, a4, 0  # [op21] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld t0, 16(t2)  # [op22] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld a1, 8(t2)  # [op23] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
li a1, 0  # [op24] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
li a2, 32  # [op25] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vsetvli a2, a2, e32, m1, ta,ma  # [op26] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
li a2, 4286578688  # [op27] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vmv.v.x v1, a2  # [op28] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
sd t1, 56(sp)  # [op29] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
mv t1, a1  # [op29] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld a1, 56(sp)  # [op29] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
j .Lchunk1_head  # [op29] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
.Lchunk1_head:  # block chunk1_head
li a2, 1024  # [op30] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
slt a2, t1, a2  # [op31] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
bne a2, zero, .Lbrc32_true  # [op32] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
mv t1, a1  # [op32] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
mv a1, s1  # [op32] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
j .Lchunk1_exit  # [op32] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
.Lbrc32_true:  # [op32] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
j .Lchunk1_body  # [op32] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
.Lchunk1_exit:  # block chunk1_exit
li a1, 32  # [op33] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vsetvli a1, a1, e32, m1, ta,ma  # [op34] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vmv.x.s s4, v1  # [op35] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
li a1, 16384  # [op36] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
add a1, t0, a1  # [op37] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
lw a2, 0(a1)  # [op38] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
li a1, 0  # [op39] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
li s5, 0  # [op40] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vmv.v.x v1, s5  # [op41] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vmv1r.v v2, v1  # [op42] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
sd t1, 56(sp)  # [op42] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
mv t1, a1  # [op42] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld a1, 56(sp)  # [op42] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
j .Lchunk2_head  # [op42] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
.Lchunk1_body:  # block chunk1_body
li a2, 32  # [op43] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vsetvli a2, a2, e32, m1, ta,ma  # [op44] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
li a2, 32  # [op45] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:23:12
vid.v v2  # [op47] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:23:12
vadd.vx v3, v2, t1  # [op48] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:23:12
vid.v v2  # [op49] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:23:12
vadd.vx v2, v2, t1  # [op50] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:23:12
    # [peephole-li] [op51] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:23:12
vwadd.vx v4, v2, x0  # [op53] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:23:12
    # [peephole-li] [op54] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:23:12
vsetvli a2, a2, e64, m2, ta,ma  # [op55] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:23:12
li a2, 4  # [op56] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:23:12
vmul.vx v4, v4, a2  # [op57] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:23:12
li a2, 0  # [op58] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:23:12
add a2, t0, a2  # [op59] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:23:12
li s5, 32  # [op60] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:23:12
vsetvli s5, s5, e32, m1, ta,ma  # [op61] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:23:12
vsuxei64.v v3, (a2), v4  # [op62] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:23:12
li a2, 32  # [op63] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:23:12
vmv.v.x v2, a3  # [op65] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
vmslt.vv v2, v3, v2  # [op66] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
vid.v v4  # [op67] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
vadd.vx v4, v4, t1  # [op68] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
    # [peephole-li] [op69] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
vwadd.vx v6, v4, x0  # [op71] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
    # [peephole-li] [op72] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
vsetvli a2, a2, e64, m2, ta,ma  # [op73] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
li a2, 4  # [op74] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
vmul.vx v4, v6, a2  # [op75] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
li a2, 4096  # [op76] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
add a2, t0, a2  # [op77] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
li s5, 32  # [op78] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
vsetvli s5, s5, e32, m1, ta,ma  # [op79] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
li s5, 1  # [op80] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
vmv.v.x v6, s5  # [op81] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
li s5, 0  # [op82] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
vmv.v.x v7, s5  # [op83] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
vmv1r.v v0, v2  # [op84] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
vmerge.vvm v6, v7, v6, v0  # [op85] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
vsuxei64.v v6, (a2), v4  # [op86] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
mulw a2, s4, a3  # [op87] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:25
li s5, 1065353216  # [op88] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
vmv.v.x v4, s5  # [op89] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
vadd.vx v3, v3, a2  # [op90] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
mv s5, t1  # [op91] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
mv s6, a2  # [op92] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
add s5, s5, s6  # [op93] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
li s6, 4  # [op94] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
mul s5, s5, s6  # [op95] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
add s5, a6, s5  # [op96] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
vmv1r.v v0, v2  # [op97] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
vle32.v v3, 0(s5), v0.t  # [op98] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
vmv1r.v v0, v2  # [op99] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
vmerge.vvm v3, v4, v3, v0  # [op100] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
vid.v v4  # [op101] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
vadd.vx v4, v4, t1  # [op102] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
li s5, 32  # [op103] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
vwadd.vx v6, v4, x0  # [op105] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
    # [peephole-li] [op106] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
vsetvli s5, s5, e64, m2, ta,ma  # [op107] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
li s5, 4  # [op108] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
vmul.vx v4, v6, s5  # [op109] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
li s5, 8192  # [op110] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
add s5, t0, s5  # [op111] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
li s6, 32  # [op112] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
vsetvli s6, s6, e32, m1, ta,ma  # [op113] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
vsuxei64.v v3, (s5), v4  # [op114] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
li s5, 32  # [op115] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
li s5, 4286578688  # [op117] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:27:16
vmv.v.x v4, s5  # [op118] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:27:16
vmv1r.v v0, v2  # [op119] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:27:16
vmerge.vvm v2, v4, v3, v0  # [op120] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:27:16
    # [peephole-li] [op121] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:27:9
vmv.v.x v3, s5  # [op122] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:27:9
vfredmax.vs v2, v2, v3  # [op123] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:27:9
vmv.x.s s5, v2  # [op124] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:27:9
li s6, 32  # [op125] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
add a1, a1, s6  # [op126] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
    # [peephole-li] [op127] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
addw t1, t1, s6  # [op128] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
    # [peephole-li] [op129] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
    # [peephole-li] [op131] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vmv.v.x v2, s5  # [op133] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vmflt.vv v3, v1, v2  # [op134] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vmv1r.v v0, v3  # [op135] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vmerge.vvm v1, v1, v2, v0  # [op136] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
li s5, 16384  # [op137] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
add s5, t0, s5  # [op138] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
sw a2, 0(s5)  # [op139] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
j .Lchunk1_head  # [op140] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
.Lchunk2_head:  # block chunk2_head
li s5, 1024  # [op141] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
slt s5, t1, s5  # [op142] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
bne s5, zero, .Lbrc143_true  # [op143] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
mv t1, a1  # [op143] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
mv a1, s1  # [op143] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vmv1r.v v1, v2  # [op143] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
j .Lchunk2_exit  # [op143] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
.Lbrc143_true:  # [op143] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
j .Lchunk2_body  # [op143] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
.Lchunk2_exit:  # block chunk2_exit
li a1, 32  # [op144] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vsetvli a1, a1, e32, m1, ta,ma  # [op145] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vmv.x.s s4, v1  # [op146] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
li a1, 0  # [op147] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
sd t1, 56(sp)  # [op148] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
mv t1, a1  # [op148] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld a1, 56(sp)  # [op148] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
j .Lchunk3_head  # [op148] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
.Lchunk2_body:  # block chunk2_body
li s5, 32  # [op149] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vsetvli s5, s5, e32, m1, ta,ma  # [op150] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
li s5, 32  # [op151] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:31
vmv.v.x v1, s4  # [op153] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:31
vid.v v3  # [op154] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:31
vadd.vx v3, v3, t1  # [op155] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:31
    # [peephole-li] [op156] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:31
vwadd.vx v4, v3, x0  # [op158] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:31
    # [peephole-li] [op159] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:31
vsetvli s5, s5, e64, m2, ta,ma  # [op160] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:31
li s5, 4  # [op161] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:31
vmul.vx v4, v4, s5  # [op162] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:31
li s5, 8192  # [op163] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:31
add s5, t0, s5  # [op164] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:31
li s6, 32  # [op165] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:31
vsetvli s6, s6, e32, m1, ta,ma  # [op166] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:31
vluxei64.v v3, (s5), v4  # [op167] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:31
li s5, 32  # [op168] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:31
vfsub.vv v3, v3, v1  # [op170] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:31
li s5, 1069066811  # [op171] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.x v1, s5  # [op172] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vfmul.vv v1, v3, v1  # [op173] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
li s5, 1262485504  # [op174] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.x v4, s5  # [op175] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vfadd.vv v5, v1, v4  # [op176] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vfsub.vv v4, v5, v4  # [op177] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vfsub.vv v1, v1, v4  # [op178] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
li s5, 958534664  # [op179] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.x v5, s5  # [op180] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
li s5, 984576714  # [op181] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.x v6, s5  # [op182] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vfmacc.vv v6, v5, v1  # [op183] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
li s5, 1008571674  # [op184] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.x v5, s5  # [op185] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vfmacc.vv v5, v6, v1  # [op186] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
li s5, 1029920722  # [op187] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.x v6, s5  # [op188] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vfmacc.vv v6, v5, v1  # [op189] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
li s5, 1047920112  # [op190] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.x v5, s5  # [op191] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vfmacc.vv v5, v6, v1  # [op192] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
li s5, 1060205080  # [op193] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.x v6, s5  # [op194] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vfmacc.vv v6, v5, v1  # [op195] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
li s5, 1065353216  # [op196] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.x v5, s5  # [op197] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.v v7, v5  # [op198] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vfmacc.vv v7, v1, v6  # [op198] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vfcvt.rtz.x.f.v v1, v4  # [op199] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
li s5, 1  # [op200] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.x v4, s5  # [op201] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vsra.vv v4, v1, v4  # [op202] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vsub.vv v6, v1, v4  # [op203] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
li s5, 127  # [op204] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.x v1, s5  # [op205] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
li s5, 23  # [op206] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.x v5, s5  # [op207] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vadd.vv v4, v4, v1  # [op208] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vadd.vv v1, v6, v1  # [op209] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vsll.vv v4, v4, v5  # [op210] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vsll.vv v1, v1, v5  # [op211] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.v v5, v4  # [op212] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.v v4, v1  # [op213] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vfmul.vv v1, v7, v5  # [op214] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vfmul.vv v1, v1, v4  # [op215] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
li s5, 2139095040  # [op216] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.x v4, s5  # [op217] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
li s5, 0  # [op218] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.x v5, s5  # [op219] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
li s5, 1118961664  # [op220] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.x v6, s5  # [op221] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmflt.vv v6, v6, v3  # [op222] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv1r.v v0, v6  # [op223] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmerge.vvm v1, v1, v4, v0  # [op224] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
li s5, 3268411392  # [op225] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.x v4, s5  # [op226] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmflt.vv v3, v3, v4  # [op227] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv1r.v v0, v3  # [op228] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmerge.vvm v1, v1, v5, v0  # [op229] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
li s5, 0  # [op230] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vmv.v.x v3, s5  # [op231] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vid.v v4  # [op232] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vadd.vx v4, v4, t1  # [op233] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
li s5, 32  # [op234] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vwadd.vx v6, v4, x0  # [op236] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
    # [peephole-li] [op237] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vsetvli s5, s5, e64, m2, ta,ma  # [op238] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
li s5, 4  # [op239] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vmul.vx v4, v6, s5  # [op240] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
li s5, 4096  # [op241] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
add s5, t0, s5  # [op242] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
li s6, 32  # [op243] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vsetvli s6, s6, e32, m1, ta,ma  # [op244] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vluxei64.v v6, (s5), v4  # [op245] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
li s5, 0  # [op246] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vmv.v.x v4, s5  # [op247] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vmsne.vv v4, v6, v4  # [op248] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
li s5, 32  # [op249] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vmv1r.v v0, v4  # [op251] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vmerge.vvm v1, v3, v1, v0  # [op252] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vid.v v3  # [op253] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vadd.vx v3, v3, t1  # [op254] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
    # [peephole-li] [op255] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vwadd.vx v4, v3, x0  # [op257] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
    # [peephole-li] [op258] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vsetvli s5, s5, e64, m2, ta,ma  # [op259] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
li s5, 4  # [op260] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vmul.vx v4, v4, s5  # [op261] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
li s5, 12288  # [op262] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
add s5, t0, s5  # [op263] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
li s6, 32  # [op264] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vsetvli s6, s6, e32, m1, ta,ma  # [op265] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vsuxei64.v v1, (s5), v4  # [op266] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
li s5, 32  # [op267] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
li s5, 0  # [op269] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:13
vmv.v.x v3, s5  # [op270] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:13
vfredusum.vs v1, v1, v3  # [op271] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:13
vmv.x.s s5, v1  # [op272] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:13
li s6, 32  # [op273] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
add a1, a1, s6  # [op274] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
    # [peephole-li] [op275] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
addw t1, t1, s6  # [op276] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
    # [peephole-li] [op277] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
    # [peephole-li] [op279] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vmv.v.x v1, s5  # [op281] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vfadd.vv v1, v2, v1  # [op282] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vmv1r.v v2, v1  # [op283] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
j .Lchunk2_head  # [op283] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
.Lchunk3_head:  # block chunk3_head
li s5, 1024  # [op284] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
slt s5, t1, s5  # [op285] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
bne s5, zero, .Lbrc286_true  # [op286] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
mv t1, s1  # [op286] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
mv t0, a1  # [op286] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
j .Lchunk3_exit  # [op286] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
.Lbrc286_true:  # [op286] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
j .Lchunk3_body  # [op286] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
.Lchunk3_exit:  # block chunk3_exit
mv t1, t0  # [op287] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
mv t0, s1  # [op287] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
j .Lprog_next  # [op287] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
.Lchunk3_body:  # block chunk3_body
li s5, 32  # [op288] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vsetvli s5, s5, e32, m1, ta,ma  # [op289] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
li s5, 32  # [op290] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:9
vmv.v.x v1, s4  # [op292] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:9
vid.v v2  # [op293] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:9
vadd.vx v2, v2, t1  # [op294] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:9
    # [peephole-li] [op295] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:9
vwadd.vx v4, v2, x0  # [op297] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:9
    # [peephole-li] [op298] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:9
vsetvli s5, s5, e64, m2, ta,ma  # [op299] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:9
li s5, 4  # [op300] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:9
vmul.vx v2, v4, s5  # [op301] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:9
li s5, 12288  # [op302] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:9
add s5, t0, s5  # [op303] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:9
li s6, 32  # [op304] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:9
vsetvli s6, s6, e32, m1, ta,ma  # [op305] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:9
vluxei64.v v4, (s5), v2  # [op306] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:9
li s5, 32  # [op307] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:9
vfdiv.vv v2, v4, v1  # [op309] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:9
vid.v v1  # [op310] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vadd.vx v1, v1, t1  # [op311] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
    # [peephole-li] [op312] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vwadd.vx v4, v1, x0  # [op314] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
    # [peephole-li] [op315] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vsetvli s5, s5, e64, m2, ta,ma  # [op316] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
li s5, 4  # [op317] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vmul.vx v4, v4, s5  # [op318] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
li s5, 0  # [op319] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
add s5, t0, s5  # [op320] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
li s6, 32  # [op321] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vsetvli s6, s6, e32, m1, ta,ma  # [op322] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vluxei64.v v1, (s5), v4  # [op323] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
li s5, 32  # [op324] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vadd.vx v1, v1, a2  # [op326] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vid.v v1  # [op327] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vadd.vx v1, v1, t1  # [op328] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
    # [peephole-li] [op329] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vwadd.vx v4, v1, x0  # [op331] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
    # [peephole-li] [op332] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vsetvli s5, s5, e64, m2, ta,ma  # [op333] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
li s5, 4  # [op334] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vmul.vx v4, v4, s5  # [op335] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
li s5, 4096  # [op336] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
add s5, t0, s5  # [op337] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
li s6, 32  # [op338] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vsetvli s6, s6, e32, m1, ta,ma  # [op339] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vluxei64.v v1, (s5), v4  # [op340] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
li s5, 0  # [op341] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vmv.v.x v3, s5  # [op342] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vmsne.vv v1, v1, v3  # [op343] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
li s5, 32  # [op344] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
mv s5, t1  # [op346] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
mv s6, a2  # [op347] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
add s5, s5, s6  # [op348] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
li s6, 4  # [op349] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
mul s5, s5, s6  # [op350] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
add s5, a7, s5  # [op351] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vmv1r.v v0, v1  # [op352] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vse32.v v2, 0(s5), v0.t  # [op353] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vcpop.m s5, v1  # [op354] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
add a1, a1, s5  # [op355] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
li s5, 32  # [op356] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
addw t1, t1, s5  # [op357] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
    # [peephole-li] [op358] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
j .Lchunk3_head  # [op360] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
.Lprog_next:  # block prog_next
add t0, t0, s3  # [op361] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
j .Lprog_head  # [op362] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
.Lprog_exit:  # block prog_exit
sd t0, 0(a5)  # [op363] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld ra, 0(sp)  # [op364] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld s1, 8(sp)  # [op364] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld s2, 16(sp)  # [op364] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld s3, 24(sp)  # [op364] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld s4, 32(sp)  # [op364] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld s5, 40(sp)  # [op364] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld s6, 48(sp)  # [op364] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
addi sp, sp, 80  # [op364] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ret  # [op364] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
    .size operator_entry, .-operator_entry
    .section .note.GNU-stack,"",@progbits
