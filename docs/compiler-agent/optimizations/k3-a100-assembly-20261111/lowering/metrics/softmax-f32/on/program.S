# a100c emitted program: softmax_kernel
# source: tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py
# specialization identity: 2aff10c8102471c3
# compiler revision: b5c42fbb75a242a8
# target model: a100-rvv1-vlen1024/1 (VLEN=1024, file=4096B)
# options: default
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
sd s7, 56(sp)
mv s1, a0
.Lentry:  # block entry
ld t1, 0(s1)  # [op0] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld t0, 0(t1)  # [op1] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld t1, 8(t1)  # [op2] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld a6, 24(s1)  # [op3] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
lwu t2, 40(s1)  # [op4] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
lwu a1, 44(s1)  # [op5] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld t1, 8(t1)  # [op6] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
addiw t1, t1, 0  # [op7] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld a7, 0(t0)  # [op8] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld s2, 56(t0)  # [op9] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld t0, 8(t0)  # [op10] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld a4, 0(t0)  # [op11] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
li t0, 1  # [op12] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
mul s3, t0, a4  # [op13] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
mv t0, t2  # [op14] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
mv s4, a1  # [op15] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
li t2, 0  # [op16] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
j .Lprog_head  # [op17] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
.Lprog_head:  # block prog_head
slt a1, t0, s3  # [op18] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
bne a1, zero, .Lbrc19_true  # [op19] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
mv t1, t0  # [op19] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
mv t0, t2  # [op19] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
j .Lprog_exit  # [op19] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
.Lbrc19_true:  # [op19] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
mv a1, t0  # [op19] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
j .Lprog_body  # [op19] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
.Lprog_body:  # block prog_body
addiw a5, a1, 0  # [op20] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
addiw t0, a4, 0  # [op21] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld t0, 16(s1)  # [op22] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld a2, 8(s1)  # [op23] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
li a2, 0  # [op24] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
li a3, 32  # [op25] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vsetvli a3, a3, e32, m1, ta,ma  # [op26] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
li a3, 4286578688  # [op27] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vmv.v.x v1, a3  # [op28] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
sd t2, 64(sp)  # [op29] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
mv t2, a2  # [op29] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld a2, 64(sp)  # [op29] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
j .Lchunk1_head  # [op29] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
.Lchunk1_head:  # block chunk1_head
li a3, 1024  # [op30] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
slt s5, t1, a3  # [op31] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
addiw s5, s5, 0  # [op32] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
li s6, 0  # [op33] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
subw s5, s6, s5  # [op34] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
subw s6, t1, a3  # [op35] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
and s5, s6, s5  # [op36] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
addw a3, a3, s5  # [op37] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
slt a3, t2, a3  # [op38] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
bne a3, zero, .Lbrc39_true  # [op39] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
mv t2, a2  # [op39] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
mv a2, a1  # [op39] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
j .Lchunk1_exit  # [op39] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
.Lbrc39_true:  # [op39] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
j .Lchunk1_body  # [op39] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
.Lchunk1_exit:  # block chunk1_exit
li a2, 32  # [op40] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vsetvli a2, a2, e32, m1, ta,ma  # [op41] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vmv.x.s s5, v1  # [op42] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
li a2, 16384  # [op43] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
add a2, t0, a2  # [op44] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
lw a5, 0(a2)  # [op45] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
li a2, 0  # [op46] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
li a3, 0  # [op47] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vmv.v.x v1, a3  # [op48] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vmv1r.v v2, v1  # [op49] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
sd t2, 64(sp)  # [op49] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
mv t2, a2  # [op49] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld a2, 64(sp)  # [op49] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
j .Lchunk2_head  # [op49] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
.Lchunk1_body:  # block chunk1_body
li a3, 32  # [op50] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vsetvli a3, a3, e32, m1, ta,ma  # [op51] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
li a3, 32  # [op52] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:23:12
vid.v v2  # [op54] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:23:12
vadd.vx v3, v2, t2  # [op55] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:23:12
vid.v v2  # [op56] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:23:12
vadd.vx v2, v2, t2  # [op57] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:23:12
    # [peephole-li] [op58] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:23:12
vwadd.vx v4, v2, x0  # [op60] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:23:12
    # [peephole-li] [op61] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:23:12
vsetvli a3, a3, e64, m2, ta,ma  # [op62] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:23:12
li a3, 4  # [op63] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:23:12
vmul.vx v4, v4, a3  # [op64] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:23:12
li a3, 0  # [op65] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:23:12
add a3, t0, a3  # [op66] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:23:12
li s5, 32  # [op67] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:23:12
vsetvli s5, s5, e32, m1, ta,ma  # [op68] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:23:12
vsuxei64.v v3, (a3), v4  # [op69] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:23:12
li a3, 32  # [op70] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:23:12
vmv.v.x v2, t1  # [op72] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
vmslt.vv v2, v3, v2  # [op73] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
vid.v v4  # [op74] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
vadd.vx v4, v4, t2  # [op75] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
    # [peephole-li] [op76] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
vwadd.vx v6, v4, x0  # [op78] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
    # [peephole-li] [op79] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
vsetvli a3, a3, e64, m2, ta,ma  # [op80] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
li a3, 4  # [op81] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
vmul.vx v4, v6, a3  # [op82] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
li a3, 4096  # [op83] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
add a3, t0, a3  # [op84] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
li s5, 32  # [op85] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
vsetvli s5, s5, e32, m1, ta,ma  # [op86] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
li s5, 1  # [op87] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
vmv.v.x v6, s5  # [op88] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
li s5, 0  # [op89] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
vmv.v.x v7, s5  # [op90] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
vmv1r.v v0, v2  # [op91] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
vmerge.vvm v6, v7, v6, v0  # [op92] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
vsuxei64.v v6, (a3), v4  # [op93] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:24:12
mulw a3, a5, t1  # [op94] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:25
li s5, 1065353216  # [op95] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
vmv.v.x v4, s5  # [op96] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
vadd.vx v3, v3, a3  # [op97] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
mv s5, t2  # [op98] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
mv s6, a3  # [op99] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
add s5, s5, s6  # [op100] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
li s6, 4  # [op101] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
mul s5, s5, s6  # [op102] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
add s5, a7, s5  # [op103] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
vmv1r.v v0, v2  # [op104] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
vle32.v v3, 0(s5), v0.t  # [op105] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
vmv1r.v v0, v2  # [op106] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
vmerge.vvm v3, v4, v3, v0  # [op107] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
vid.v v4  # [op108] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
vadd.vx v4, v4, t2  # [op109] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
li s5, 32  # [op110] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
vwadd.vx v6, v4, x0  # [op112] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
    # [peephole-li] [op113] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
vsetvli s5, s5, e64, m2, ta,ma  # [op114] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
li s5, 4  # [op115] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
vmul.vx v4, v6, s5  # [op116] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
li s5, 8192  # [op117] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
add s5, t0, s5  # [op118] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
li s6, 32  # [op119] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
vsetvli s6, s6, e32, m1, ta,ma  # [op120] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
vsuxei64.v v3, (s5), v4  # [op121] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
li s5, 32  # [op122] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:25:9
li s5, 4286578688  # [op124] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:27:16
vmv.v.x v4, s5  # [op125] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:27:16
vmv1r.v v0, v2  # [op126] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:27:16
vmerge.vvm v2, v4, v3, v0  # [op127] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:27:16
    # [peephole-li] [op128] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:27:9
vmv.v.x v3, s5  # [op129] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:27:9
vfredmax.vs v2, v2, v3  # [op130] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:27:9
vmv.x.s s5, v2  # [op131] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:27:9
li s6, 32  # [op132] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
add a2, a2, s6  # [op133] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
    # [peephole-li] [op134] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
addw t2, t2, s6  # [op135] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
    # [peephole-li] [op136] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
    # [peephole-li] [op138] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vmv.v.x v2, s5  # [op140] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vmflt.vv v3, v1, v2  # [op141] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vmv1r.v v0, v3  # [op142] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vmerge.vvm v1, v1, v2, v0  # [op143] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
li s5, 16384  # [op144] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
add s5, t0, s5  # [op145] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
sw a3, 0(s5)  # [op146] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
j .Lchunk1_head  # [op147] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
.Lchunk2_head:  # block chunk2_head
li a3, 1024  # [op148] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
slt s6, t1, a3  # [op149] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
addiw s6, s6, 0  # [op150] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
li s7, 0  # [op151] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
subw s6, s7, s6  # [op152] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
subw s7, t1, a3  # [op153] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
and s6, s7, s6  # [op154] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
addw a3, a3, s6  # [op155] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
slt a3, t2, a3  # [op156] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
bne a3, zero, .Lbrc157_true  # [op157] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
mv t2, a2  # [op157] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
mv a2, a1  # [op157] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vmv1r.v v1, v2  # [op157] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
j .Lchunk2_exit  # [op157] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
.Lbrc157_true:  # [op157] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
j .Lchunk2_body  # [op157] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
.Lchunk2_exit:  # block chunk2_exit
li a2, 32  # [op158] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vsetvli a2, a2, e32, m1, ta,ma  # [op159] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vmv.x.s s5, v1  # [op160] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
li a2, 0  # [op161] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
sd t2, 64(sp)  # [op162] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
mv t2, a2  # [op162] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld a2, 64(sp)  # [op162] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
j .Lchunk3_head  # [op162] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
.Lchunk2_body:  # block chunk2_body
li a3, 32  # [op163] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vsetvli a3, a3, e32, m1, ta,ma  # [op164] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
li a3, 32  # [op165] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:31
vmv.v.x v1, s5  # [op167] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:31
vid.v v3  # [op168] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:31
vadd.vx v3, v3, t2  # [op169] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:31
    # [peephole-li] [op170] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:31
vwadd.vx v4, v3, x0  # [op172] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:31
    # [peephole-li] [op173] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:31
vsetvli a3, a3, e64, m2, ta,ma  # [op174] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:31
li a3, 4  # [op175] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:31
vmul.vx v4, v4, a3  # [op176] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:31
li a3, 8192  # [op177] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:31
add a3, t0, a3  # [op178] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:31
li s6, 32  # [op179] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:31
vsetvli s6, s6, e32, m1, ta,ma  # [op180] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:31
vluxei64.v v3, (a3), v4  # [op181] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:31
li a3, 32  # [op182] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:31
vfsub.vv v3, v3, v1  # [op184] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:31
li a3, 1069066811  # [op185] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.x v1, a3  # [op186] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vfmul.vv v1, v3, v1  # [op187] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
li a3, 1262485504  # [op188] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.x v4, a3  # [op189] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vfadd.vv v5, v1, v4  # [op190] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vfsub.vv v4, v5, v4  # [op191] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vfsub.vv v1, v1, v4  # [op192] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
li a3, 958534664  # [op193] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.x v5, a3  # [op194] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
li a3, 984576714  # [op195] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.x v6, a3  # [op196] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vfmacc.vv v6, v5, v1  # [op197] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
li a3, 1008571674  # [op198] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.x v5, a3  # [op199] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vfmacc.vv v5, v6, v1  # [op200] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
li a3, 1029920722  # [op201] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.x v6, a3  # [op202] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vfmacc.vv v6, v5, v1  # [op203] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
li a3, 1047920112  # [op204] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.x v5, a3  # [op205] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vfmacc.vv v5, v6, v1  # [op206] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
li a3, 1060205080  # [op207] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.x v6, a3  # [op208] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vfmacc.vv v6, v5, v1  # [op209] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
li a3, 1065353216  # [op210] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.x v5, a3  # [op211] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.v v7, v5  # [op212] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vfmacc.vv v7, v1, v6  # [op212] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vfcvt.rtz.x.f.v v1, v4  # [op213] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
li a3, 1  # [op214] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.x v4, a3  # [op215] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vsra.vv v4, v1, v4  # [op216] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vsub.vv v6, v1, v4  # [op217] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
li a3, 127  # [op218] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.x v1, a3  # [op219] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
li a3, 23  # [op220] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.x v5, a3  # [op221] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vadd.vv v4, v4, v1  # [op222] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vadd.vv v1, v6, v1  # [op223] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vsll.vv v4, v4, v5  # [op224] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vsll.vv v1, v1, v5  # [op225] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.v v5, v4  # [op226] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.v v4, v1  # [op227] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vfmul.vv v1, v7, v5  # [op228] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vfmul.vv v1, v1, v4  # [op229] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
li a3, 2139095040  # [op230] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.x v4, a3  # [op231] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
li a3, 0  # [op232] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.x v5, a3  # [op233] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
li a3, 1118961664  # [op234] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.x v6, a3  # [op235] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmflt.vv v6, v6, v3  # [op236] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv1r.v v0, v6  # [op237] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmerge.vvm v1, v1, v4, v0  # [op238] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
li a3, 3268411392  # [op239] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv.v.x v4, a3  # [op240] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmflt.vv v3, v3, v4  # [op241] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmv1r.v v0, v3  # [op242] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
vmerge.vvm v1, v1, v5, v0  # [op243] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:24
li a3, 0  # [op244] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vmv.v.x v3, a3  # [op245] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vid.v v4  # [op246] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vadd.vx v4, v4, t2  # [op247] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
li a3, 32  # [op248] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vwadd.vx v6, v4, x0  # [op250] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
    # [peephole-li] [op251] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vsetvli a3, a3, e64, m2, ta,ma  # [op252] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
li a3, 4  # [op253] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vmul.vx v4, v6, a3  # [op254] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
li a3, 4096  # [op255] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
add a3, t0, a3  # [op256] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
li s6, 32  # [op257] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vsetvli s6, s6, e32, m1, ta,ma  # [op258] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vluxei64.v v6, (a3), v4  # [op259] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
li a3, 0  # [op260] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vmv.v.x v4, a3  # [op261] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vmsne.vv v4, v6, v4  # [op262] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
li a3, 32  # [op263] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vmv1r.v v0, v4  # [op265] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vmerge.vvm v1, v3, v1, v0  # [op266] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vid.v v3  # [op267] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vadd.vx v3, v3, t2  # [op268] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
    # [peephole-li] [op269] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vwadd.vx v4, v3, x0  # [op271] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
    # [peephole-li] [op272] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vsetvli a3, a3, e64, m2, ta,ma  # [op273] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
li a3, 4  # [op274] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vmul.vx v4, v4, a3  # [op275] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
li a3, 12288  # [op276] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
add a3, t0, a3  # [op277] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
li s6, 32  # [op278] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vsetvli s6, s6, e32, m1, ta,ma  # [op279] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
vsuxei64.v v1, (a3), v4  # [op280] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
li a3, 32  # [op281] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:28:9
li a3, 0  # [op283] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:13
vmv.v.x v3, a3  # [op284] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:13
vfredusum.vs v1, v1, v3  # [op285] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:13
vmv.x.s a3, v1  # [op286] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:13
li s6, 32  # [op287] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
add a2, a2, s6  # [op288] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
    # [peephole-li] [op289] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
addw t2, t2, s6  # [op290] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
    # [peephole-li] [op291] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
    # [peephole-li] [op293] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vmv.v.x v1, a3  # [op295] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vfadd.vv v1, v2, v1  # [op296] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vmv1r.v v2, v1  # [op297] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
j .Lchunk2_head  # [op297] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
.Lchunk3_head:  # block chunk3_head
li a3, 1024  # [op298] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
slt s6, t1, a3  # [op299] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
addiw s6, s6, 0  # [op300] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
li s7, 0  # [op301] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
subw s6, s7, s6  # [op302] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
subw s7, t1, a3  # [op303] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
and s6, s7, s6  # [op304] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
addw a3, a3, s6  # [op305] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
slt a3, t2, a3  # [op306] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
bne a3, zero, .Lbrc307_true  # [op307] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
mv t2, a1  # [op307] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
mv t0, a2  # [op307] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
j .Lchunk3_exit  # [op307] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
.Lbrc307_true:  # [op307] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
j .Lchunk3_body  # [op307] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
.Lchunk3_exit:  # block chunk3_exit
mv t2, t0  # [op308] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
mv t0, a1  # [op308] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
j .Lprog_next  # [op308] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
.Lchunk3_body:  # block chunk3_body
li a3, 32  # [op309] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
vsetvli a3, a3, e32, m1, ta,ma  # [op310] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
li a3, 32  # [op311] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:9
vmv.v.x v1, s5  # [op313] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:9
vid.v v2  # [op314] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:9
vadd.vx v2, v2, t2  # [op315] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:9
    # [peephole-li] [op316] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:9
vwadd.vx v4, v2, x0  # [op318] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:9
    # [peephole-li] [op319] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:9
vsetvli a3, a3, e64, m2, ta,ma  # [op320] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:9
li a3, 4  # [op321] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:9
vmul.vx v2, v4, a3  # [op322] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:9
li a3, 12288  # [op323] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:9
add a3, t0, a3  # [op324] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:9
li s6, 32  # [op325] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:9
vsetvli s6, s6, e32, m1, ta,ma  # [op326] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:9
vluxei64.v v4, (a3), v2  # [op327] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:9
li a3, 32  # [op328] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:9
vfdiv.vv v2, v4, v1  # [op330] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:29:9
vid.v v1  # [op331] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vadd.vx v1, v1, t2  # [op332] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
    # [peephole-li] [op333] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vwadd.vx v4, v1, x0  # [op335] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
    # [peephole-li] [op336] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vsetvli a3, a3, e64, m2, ta,ma  # [op337] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
li a3, 4  # [op338] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vmul.vx v4, v4, a3  # [op339] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
li a3, 0  # [op340] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
add a3, t0, a3  # [op341] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
li s6, 32  # [op342] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vsetvli s6, s6, e32, m1, ta,ma  # [op343] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vluxei64.v v1, (a3), v4  # [op344] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
li a3, 32  # [op345] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vadd.vx v1, v1, a5  # [op347] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vid.v v1  # [op348] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vadd.vx v1, v1, t2  # [op349] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
    # [peephole-li] [op350] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vwadd.vx v4, v1, x0  # [op352] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
    # [peephole-li] [op353] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vsetvli a3, a3, e64, m2, ta,ma  # [op354] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
li a3, 4  # [op355] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vmul.vx v4, v4, a3  # [op356] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
li a3, 4096  # [op357] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
add a3, t0, a3  # [op358] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
li s6, 32  # [op359] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vsetvli s6, s6, e32, m1, ta,ma  # [op360] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vluxei64.v v1, (a3), v4  # [op361] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
li a3, 0  # [op362] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vmv.v.x v3, a3  # [op363] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vmsne.vv v1, v1, v3  # [op364] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
li a3, 32  # [op365] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
mv a3, t2  # [op367] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
mv s6, a5  # [op368] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
add a3, a3, s6  # [op369] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
li s6, 4  # [op370] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
mul a3, a3, s6  # [op371] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
add a3, s2, a3  # [op372] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vmv1r.v v0, v1  # [op373] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vse32.v v2, 0(a3), v0.t  # [op374] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
vcpop.m a3, v1  # [op375] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:31:5
add a2, a2, a3  # [op376] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
li a3, 32  # [op377] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
addw t2, t2, a3  # [op378] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
    # [peephole-li] [op379] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
j .Lchunk3_head  # [op381] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
.Lprog_next:  # block prog_next
add t0, t0, s4  # [op382] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
j .Lprog_head  # [op383] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
.Lprog_exit:  # block prog_exit
sd t0, 0(a6)  # [op384] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld ra, 0(sp)  # [op385] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld s1, 8(sp)  # [op385] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld s2, 16(sp)  # [op385] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld s3, 24(sp)  # [op385] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld s4, 32(sp)  # [op385] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld s5, 40(sp)  # [op385] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld s6, 48(sp)  # [op385] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ld s7, 56(sp)  # [op385] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
addi sp, sp, 80  # [op385] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
ret  # [op385] /tmp/a100-k3-lowering-frozen-y111s6ff/ops/suite/perf/softmax.py:21:1
    .size operator_entry, .-operator_entry
    .section .note.GNU-stack,"",@progbits
