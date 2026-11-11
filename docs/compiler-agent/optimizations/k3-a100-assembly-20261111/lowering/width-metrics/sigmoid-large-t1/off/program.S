# a100c emitted program: sigmoid_kernel
# source: tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py
# specialization identity: 335ab464e73cf1da
# compiler revision: 92fa8b4b706f0a76
# target model: a100-rvv1-vlen1024/1 (VLEN=1024, file=4096B)
# options: no-guarded-narrow-access,no-elementwise-width
# argument layout: 633b17d1a57c5f03
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
    li a0, 0
    ret
    .size operator_workspace_shared, .-operator_workspace_shared
    .globl operator_entry
    .type operator_entry, @function
    # [peephole] removed 0 redundant vsetvli, 1 redundant li
operator_entry:  # fn operator_entry
addi sp, sp, -64
sd ra, 0(sp)
sd s1, 8(sp)
sd s2, 16(sp)
sd s3, 24(sp)
sd s4, 32(sp)
sd s5, 40(sp)
mv t0, a0
.Lentry:  # block entry
ld t1, 0(t0)  # [op0] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
ld t2, 0(t1)  # [op1] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
ld t1, 8(t1)  # [op2] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
ld a5, 24(t0)  # [op3] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
lwu s1, 40(t0)  # [op4] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
lwu a1, 44(t0)  # [op5] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
ld t0, 8(t1)  # [op6] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
addiw a2, t0, 0  # [op7] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
ld a6, 0(t2)  # [op8] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
ld a7, 56(t2)  # [op9] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
li t1, 1023  # [op10] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
add t0, t0, t1  # [op11] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
li t1, 1024  # [op12] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
divu a3, t0, t1  # [op13] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
li t0, 1  # [op14] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
mul s2, t0, a3  # [op15] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
mv t0, s1  # [op16] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
mv s3, a1  # [op17] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
li t1, 0  # [op18] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
j .Lprog_head  # [op19] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
.Lprog_head:  # block prog_head
slt t2, t0, s2  # [op20] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
bne t2, zero, .Lbrc21_true  # [op21] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
sd t1, 48(sp)  # [op21] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
mv t1, t0  # [op21] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
ld t0, 48(sp)  # [op21] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
j .Lprog_exit  # [op21] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
.Lbrc21_true:  # [op21] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
mv t2, t0  # [op21] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
mv t0, t1  # [op21] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
j .Lprog_body  # [op21] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
.Lprog_body:  # block prog_body
addiw t1, t2, 0  # [op22] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
addiw s1, a3, 0  # [op23] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
li s1, 10  # [op24] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:23:15
sllw t1, t1, s1  # [op25] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:23:15
li s1, 0  # [op26] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
sd t0, 48(sp)  # [op27] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
mv t0, s1  # [op27] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
ld s1, 48(sp)  # [op27] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
j .Lchunk1_head  # [op27] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
.Lchunk1_head:  # block chunk1_head
subw a4, a2, t1  # [op28] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
li a1, 1024  # [op29] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
slt s4, a4, a1  # [op30] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
addiw s4, s4, 0  # [op31] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
li s5, 0  # [op32] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
subw s4, s5, s4  # [op33] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
subw a4, a4, a1  # [op34] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
and a4, a4, s4  # [op35] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
addw a1, a1, a4  # [op36] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
slt a1, t0, a1  # [op37] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
bne a1, zero, .Lbrc38_true  # [op38] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
mv t1, t2  # [op38] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
mv t0, s1  # [op38] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
j .Lchunk1_exit  # [op38] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
.Lbrc38_true:  # [op38] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
j .Lchunk1_body  # [op38] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
.Lchunk1_exit:  # block chunk1_exit
mv t1, t0  # [op39] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
mv t0, t2  # [op39] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
j .Lprog_next  # [op39] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
.Lchunk1_body:  # block chunk1_body
li a1, 32  # [op40] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
vsetvli a1, a1, e32, m1, ta,ma  # [op41] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
li a1, 32  # [op42] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:23:34
vid.v v1  # [op44] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:23:34
vadd.vx v1, v1, t0  # [op45] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:23:34
vmv.v.x v2, t1  # [op46] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:23:15
vadd.vv v1, v2, v1  # [op47] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:23:15
vmv.v.x v2, a2  # [op48] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:24:12
vmslt.vv v2, v1, v2  # [op49] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:24:12
li a1, 0  # [op50] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:25:9
vmv.v.x v1, a1  # [op51] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:25:9
mv a1, t0  # [op52] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:25:9
mv a4, t1  # [op53] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:25:9
add a1, a1, a4  # [op54] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:25:9
li a4, 4  # [op55] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:25:9
mul a1, a1, a4  # [op56] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:25:9
add a1, a6, a1  # [op57] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:25:9
vmv1r.v v0, v2  # [op58] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:25:9
vle32.v v3, 0(a1), v0.t  # [op59] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:25:9
vmv1r.v v0, v2  # [op60] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:25:9
vmerge.vvm v1, v1, v3, v0  # [op61] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:25:9
vfsgnjn.vv v3, v1, v1  # [op62] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
li a1, 1069066811  # [op63] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vmv.v.x v1, a1  # [op64] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vfmul.vv v1, v3, v1  # [op65] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
li a1, 1262485504  # [op66] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vmv.v.x v4, a1  # [op67] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vfadd.vv v5, v1, v4  # [op68] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vfsub.vv v4, v5, v4  # [op69] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vfsub.vv v1, v1, v4  # [op70] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
li a1, 958534664  # [op71] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vmv.v.x v5, a1  # [op72] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
li a1, 984576714  # [op73] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vmv.v.x v6, a1  # [op74] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vfmacc.vv v6, v5, v1  # [op75] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
li a1, 1008571674  # [op76] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vmv.v.x v5, a1  # [op77] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vfmacc.vv v5, v6, v1  # [op78] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
li a1, 1029920722  # [op79] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vmv.v.x v6, a1  # [op80] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vfmacc.vv v6, v5, v1  # [op81] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
li a1, 1047920112  # [op82] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vmv.v.x v5, a1  # [op83] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vfmacc.vv v5, v6, v1  # [op84] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
li a1, 1060205080  # [op85] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vmv.v.x v6, a1  # [op86] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vfmacc.vv v6, v5, v1  # [op87] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
li a1, 1065353216  # [op88] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vmv.v.x v5, a1  # [op89] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vmv.v.v v7, v5  # [op90] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vfmacc.vv v7, v1, v6  # [op90] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vfcvt.rtz.x.f.v v1, v4  # [op91] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
li a1, 1  # [op92] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vmv.v.x v4, a1  # [op93] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vsra.vv v4, v1, v4  # [op94] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vsub.vv v6, v1, v4  # [op95] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
li a1, 127  # [op96] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vmv.v.x v1, a1  # [op97] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
li a1, 23  # [op98] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vmv.v.x v5, a1  # [op99] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vadd.vv v4, v4, v1  # [op100] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vadd.vv v1, v6, v1  # [op101] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vsll.vv v4, v4, v5  # [op102] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vsll.vv v1, v1, v5  # [op103] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vmv.v.v v5, v4  # [op104] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vmv.v.v v4, v1  # [op105] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vfmul.vv v1, v7, v5  # [op106] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vfmul.vv v1, v1, v4  # [op107] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
li a1, 2139095040  # [op108] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vmv.v.x v4, a1  # [op109] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
li a1, 0  # [op110] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vmv.v.x v5, a1  # [op111] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
li a1, 1118961664  # [op112] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vmv.v.x v6, a1  # [op113] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vmflt.vv v6, v6, v3  # [op114] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vmv1r.v v0, v6  # [op115] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vmerge.vvm v1, v1, v4, v0  # [op116] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
li a1, 3268411392  # [op117] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vmv.v.x v4, a1  # [op118] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vmflt.vv v3, v3, v4  # [op119] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vmv1r.v v0, v3  # [op120] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vmerge.vvm v3, v1, v5, v0  # [op121] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
li a1, 1065353216  # [op122] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vmv.v.x v1, a1  # [op123] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vfadd.vv v3, v1, v3  # [op124] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
vfdiv.vv v1, v1, v3  # [op125] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:26:9
mv a1, t0  # [op126] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:27:5
mv a4, t1  # [op127] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:27:5
add a1, a1, a4  # [op128] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:27:5
li a4, 4  # [op129] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:27:5
mul a1, a1, a4  # [op130] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:27:5
add a1, a7, a1  # [op131] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:27:5
vmv1r.v v0, v2  # [op132] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:27:5
vse32.v v1, 0(a1), v0.t  # [op133] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:27:5
vcpop.m a1, v2  # [op134] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:27:5
add s1, s1, a1  # [op135] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
li a1, 32  # [op136] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
addw t0, t0, a1  # [op137] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
    # [peephole-li] [op138] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
j .Lchunk1_head  # [op140] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
.Lprog_next:  # block prog_next
add t0, t0, s3  # [op141] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
j .Lprog_head  # [op142] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
.Lprog_exit:  # block prog_exit
sd t0, 0(a5)  # [op143] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
ld ra, 0(sp)  # [op144] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
ld s1, 8(sp)  # [op144] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
ld s2, 16(sp)  # [op144] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
ld s3, 24(sp)  # [op144] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
ld s4, 32(sp)  # [op144] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
ld s5, 40(sp)  # [op144] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
addi sp, sp, 64  # [op144] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
ret  # [op144] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/sigmoid.py:21:1
    .size operator_entry, .-operator_entry
    .section .note.GNU-stack,"",@progbits
