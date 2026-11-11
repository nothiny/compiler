# a100c emitted program: gelu_kernel
# source: tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py
# specialization identity: 6b6546636779df79
# compiler revision: 92fa8b4b706f0a76
# target model: a100-rvv1-vlen1024/1 (VLEN=1024, file=4096B)
# options: no-guarded-narrow-access
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
    # [peephole] removed 0 redundant vsetvli, 2 redundant li
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
ld t2, 0(t0)  # [op0] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
ld t1, 0(t2)  # [op1] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
ld t2, 8(t2)  # [op2] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
ld a5, 24(t0)  # [op3] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
lwu s1, 40(t0)  # [op4] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
lwu a1, 44(t0)  # [op5] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
ld t0, 8(t2)  # [op6] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
addiw a3, t0, 0  # [op7] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
ld a6, 0(t1)  # [op8] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
ld a7, 56(t1)  # [op9] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
li t2, 1023  # [op10] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
add t0, t0, t2  # [op11] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
li t2, 1024  # [op12] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
divu t0, t0, t2  # [op13] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
li t2, 1  # [op14] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
mul s2, t2, t0  # [op15] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
mv s1, s1  # [op16] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
mv s3, a1  # [op17] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
li a1, 0  # [op18] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
    # [peephole-li] [op19]
ld t0, 48(t1)  # [op20]
ld t1, 104(t1)  # [op21]
sltu a2, t0, t1  # [op22]
sltu t0, t1, t0  # [op23]
or t0, a2, t0  # [op24]
and t0, t2, t0  # [op25]
li t1, 32  # [op26]
mul t0, t0, t1  # [op27]
    # [peephole-li] [op28]
add t0, t1, t0  # [op29]
addiw t2, t0, 0  # [op30]
mv t0, s1  # [op31] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
mv t1, a1  # [op31] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
j .Lprog_head  # [op31] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
.Lprog_head:  # block prog_head
slt s1, t0, s2  # [op32] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
bne s1, zero, .Lbrc33_true  # [op33] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
sd t1, 48(sp)  # [op33] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
mv t1, t0  # [op33] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
ld t0, 48(sp)  # [op33] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
j .Lprog_exit  # [op33] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
.Lbrc33_true:  # [op33] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
mv s1, t0  # [op33] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
mv t0, t1  # [op33] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
j .Lprog_body  # [op33] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
.Lprog_body:  # block prog_body
addiw t1, s1, 0  # [op34] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
li a1, 10  # [op35] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:23:15
sllw t1, t1, a1  # [op36] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:23:15
li a1, 0  # [op37] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
sd t0, 48(sp)  # [op38] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
mv t0, a1  # [op38] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
ld a1, 48(sp)  # [op38] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
j .Lchunk1_head  # [op38] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
.Lchunk1_head:  # block chunk1_head
subw a4, a3, t1  # [op39] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
li a2, 1024  # [op40] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
slt s4, a4, a2  # [op41] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
addiw s4, s4, 0  # [op42] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
li s5, 0  # [op43] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
subw s4, s5, s4  # [op44] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
subw a4, a4, a2  # [op45] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
and a4, a4, s4  # [op46] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
addw a2, a2, a4  # [op47] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
slt a2, t0, a2  # [op48] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
bne a2, zero, .Lbrc49_true  # [op49] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
mv t1, s1  # [op49] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
mv t0, a1  # [op49] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
j .Lchunk1_exit  # [op49] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
.Lbrc49_true:  # [op49] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
j .Lchunk1_body  # [op49] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
.Lchunk1_exit:  # block chunk1_exit
mv t1, t0  # [op50] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
mv t0, s1  # [op50] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
j .Lprog_next  # [op50] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
.Lchunk1_body:  # block chunk1_body
vsetvli a2, t2, e32, m2, ta,ma  # [op51] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
vid.v v2  # [op53] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:23:34
vadd.vx v2, v2, t0  # [op54] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:23:34
vmv.v.x v4, t1  # [op55] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:23:15
vadd.vv v2, v4, v2  # [op56] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:23:15
vmv.v.x v4, a3  # [op57] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:24:12
vmslt.vv v1, v2, v4  # [op58] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:24:12
li a2, 0  # [op59] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:25:9
vmv.v.x v2, a2  # [op60] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:25:9
mv a2, t0  # [op61] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:25:9
mv a4, t1  # [op62] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:25:9
add a2, a2, a4  # [op63] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:25:9
li a4, 4  # [op64] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:25:9
mul a2, a2, a4  # [op65] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:25:9
add a2, a6, a2  # [op66] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:25:9
vmv1r.v v0, v1  # [op67] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:25:9
vle32.v v4, 0(a2), v0.t  # [op68] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:25:9
vmv1r.v v0, v1  # [op69] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:25:9
vmerge.vvm v2, v2, v4, v0  # [op70] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:25:9
li a2, 1056964608  # [op71] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:9
vmv.v.x v4, a2  # [op72] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:9
vfmul.vv v14, v4, v2  # [op73] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:9
li a2, 1060439283  # [op74] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:33
vmv.v.x v4, a2  # [op75] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:33
vfmul.vv v6, v4, v2  # [op76] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:33
vfsgnjx.vv v8, v6, v6  # [op77] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfmul.vv v2, v8, v8  # [op78] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 1065353216  # [op79] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v10, a2  # [op80] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 898629920  # [op81] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v4, a2  # [op82] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 3077194043  # [op83] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v12, a2  # [op84] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfmacc.vv v12, v4, v2  # [op85] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 955968394  # [op86] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v4, a2  # [op87] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfmacc.vv v4, v12, v2  # [op88] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 3126850842  # [op89] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v12, a2  # [op90] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfmacc.vv v12, v4, v2  # [op91] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 1001073796  # [op92] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v4, a2  # [op93] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfmacc.vv v4, v12, v2  # [op94] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 3168540257  # [op95] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v12, a2  # [op96] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfmacc.vv v12, v4, v2  # [op97] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 1038555024  # [op98] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v4, a2  # [op99] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfmacc.vv v4, v12, v2  # [op100] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 3200291747  # [op101] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v12, a2  # [op102] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfmacc.vv v12, v4, v2  # [op103] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 1066430139  # [op104] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v4, a2  # [op105] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfmacc.vv v4, v12, v2  # [op106] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfmul.vv v16, v6, v4  # [op107] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfdiv.vv v4, v10, v2  # [op108] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 1045795439  # [op109] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v12, a2  # [op110] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 3214660180  # [op111] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v18, a2  # [op112] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfmacc.vv v18, v12, v4  # [op113] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 1078560265  # [op114] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v12, a2  # [op115] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfmacc.vv v12, v18, v4  # [op116] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 3231258870  # [op117] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v18, a2  # [op118] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfmacc.vv v18, v12, v4  # [op119] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 1083796153  # [op120] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v12, a2  # [op121] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfmacc.vv v12, v18, v4  # [op122] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 3227124571  # [op123] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v18, a2  # [op124] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfmacc.vv v18, v12, v4  # [op125] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 1072436177  # [op126] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v12, a2  # [op127] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfmacc.vv v12, v18, v4  # [op128] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 3210323127  # [op129] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v18, a2  # [op130] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfmacc.vv v18, v12, v4  # [op131] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 1053845448  # [op132] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v12, a2  # [op133] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfmacc.vv v12, v18, v4  # [op134] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 3197111909  # [op135] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v18, a2  # [op136] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfmacc.vv v18, v12, v4  # [op137] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 1058041288  # [op138] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v12, a2  # [op139] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv2r.v v20, v12  # [op140] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfmacc.vv v20, v18, v4  # [op140] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 3216550459  # [op141] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v4, a2  # [op142] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfmul.vv v2, v2, v4  # [op143] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 1262485504  # [op144] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v4, a2  # [op145] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfadd.vv v12, v2, v4  # [op146] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfsub.vv v4, v12, v4  # [op147] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfsub.vv v2, v2, v4  # [op148] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 958534664  # [op149] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v12, a2  # [op150] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 984576714  # [op151] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v18, a2  # [op152] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfmacc.vv v18, v12, v2  # [op153] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 1008571674  # [op154] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v12, a2  # [op155] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfmacc.vv v12, v18, v2  # [op156] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 1029920722  # [op157] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v18, a2  # [op158] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfmacc.vv v18, v12, v2  # [op159] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 1047920112  # [op160] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v12, a2  # [op161] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfmacc.vv v12, v18, v2  # [op162] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 1060205080  # [op163] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v18, a2  # [op164] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfmacc.vv v18, v12, v2  # [op165] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 1065353216  # [op166] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v12, a2  # [op167] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv2r.v v22, v12  # [op168] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfmacc.vv v22, v2, v18  # [op168] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfcvt.rtz.x.f.v v2, v4  # [op169] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 1  # [op170] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v4, a2  # [op171] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vsra.vv v4, v2, v4  # [op172] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vsub.vv v18, v2, v4  # [op173] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 127  # [op174] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v2, a2  # [op175] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 23  # [op176] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v12, a2  # [op177] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vadd.vv v4, v4, v2  # [op178] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vadd.vv v2, v18, v2  # [op179] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vsll.vv v4, v4, v12  # [op180] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vsll.vv v2, v2, v12  # [op181] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.v v12, v4  # [op182] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.v v4, v2  # [op183] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfmul.vv v2, v22, v12  # [op184] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfmul.vv v2, v2, v4  # [op185] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfmul.vv v2, v2, v20  # [op186] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfdiv.vv v2, v2, v8  # [op187] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfsub.vv v4, v10, v2  # [op188] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 0  # [op189] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v2, a2  # [op190] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmflt.vv v2, v6, v2  # [op191] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 3212836864  # [op192] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v12, a2  # [op193] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 1065353216  # [op194] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v18, a2  # [op195] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv1r.v v0, v2  # [op196] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmerge.vvm v2, v18, v12, v0  # [op197] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vfmul.vv v4, v2, v4  # [op198] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 1082130432  # [op199] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v12, a2  # [op200] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmfle.vv v12, v12, v8  # [op201] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmfle.vv v8, v10, v8  # [op202] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv1r.v v0, v8  # [op203] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmerge.vvm v4, v16, v4, v0  # [op204] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv1r.v v0, v12  # [op205] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmerge.vvm v2, v4, v2, v0  # [op206] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmfne.vv v4, v6, v6  # [op207] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 2143289344  # [op208] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv.v.x v6, a2  # [op209] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmv1r.v v0, v4  # [op210] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
vmerge.vvm v2, v2, v6, v0  # [op211] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:26
li a2, 1065353216  # [op212] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:20
vmv.v.x v4, a2  # [op213] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:20
vfadd.vv v2, v4, v2  # [op214] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:20
vfmul.vv v2, v14, v2  # [op215] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:26:9
mv a2, t0  # [op216] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:27:5
mv a4, t1  # [op217] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:27:5
add a2, a2, a4  # [op218] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:27:5
li a4, 4  # [op219] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:27:5
mul a2, a2, a4  # [op220] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:27:5
add a2, a7, a2  # [op221] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:27:5
vmv1r.v v0, v1  # [op222] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:27:5
vse32.v v2, 0(a2), v0.t  # [op223] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:27:5
vcpop.m a2, v1  # [op224] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:27:5
add a1, a1, a2  # [op225] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
addw t0, t0, t2  # [op226] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
j .Lchunk1_head  # [op228] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
.Lprog_next:  # block prog_next
add t0, t0, s3  # [op229] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
j .Lprog_head  # [op230] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
.Lprog_exit:  # block prog_exit
sd t0, 0(a5)  # [op231] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
ld ra, 0(sp)  # [op232] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
ld s1, 8(sp)  # [op232] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
ld s2, 16(sp)  # [op232] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
ld s3, 24(sp)  # [op232] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
ld s4, 32(sp)  # [op232] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
ld s5, 40(sp)  # [op232] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
addi sp, sp, 64  # [op232] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
ret  # [op232] /tmp/a100-k3-width-frozen-spjhbebe/ops/suite/perf/gelu.py:21:1
    .size operator_entry, .-operator_entry
    .section .note.GNU-stack,"",@progbits
