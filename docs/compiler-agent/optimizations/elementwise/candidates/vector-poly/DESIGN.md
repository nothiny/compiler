# 候选设计：vmath 向量多项式路径（elementwise 轮主瓶颈修复）

状态：**设计已定稿并经宿主端数值验证，代码未实施**（用户将自行实现并验证）。
判据：QEMU 模拟执行的 guest 动态指令数（代理指标），非墙钟、非真实硬件加速比。

## 1. 瓶颈依据（基线证据）

- 范围：`elementwise_reduce` 家族去除归约/RNG/原子 tag 后的 **134 算子 / 683 cases**
  （`baseline/operators-elementwise-family.txt`），基线 scoped scan
  **683/683 PASS**（t1，`baseline/scan/`）。
- 基线画像（`baseline/metrics/`，guest 动态指令/每次调用，t1）：

  | case | total/call | 说明 |
  |---|---:|---|
  | gelu / erf f32[128] | ~69-70k | erf 逐元素 libm 机制占 ~89% |
  | pow f32[128] | 79k | 每元素 exp+log 两次调用 |
  | selu / sigmoid f32 | ~54-55k | 每元素 exp |
  | tanh f16[97] | 55k | exp 组合 + f16→f32 转换 |
  | softplus f32 | 15k | 部分 exp/log |
  | 纯逐元素（add_value/relu/sqrt/mul_relu/leaky_relu） | 2.0-3.4k | 无超越函数 |

- 机制（gelu f32 的 program.S 123-142 行，缓存条目
  `63f20fc8…/program.S`）：`tl.erf` → `vmath` MIR op → 发射为
  **栈中转 + 逐元素标量循环调用 glibc `erff`**：向量 `vse32` 到栈缓冲，
  循环变量（指针、计数）驻留栈内存（每迭代 4×ld/sd），每元素
  `flw + call erff + fsw + 指针/计数栈回写`，最后 `vle32` 载回。
  PLT 3096 条/调用也是 erff 链接开销。
- vmath 普查（`baseline/vmath_census.json`，499 identities）：
  **expf 72 ids/19 算子**（tanh/sigmoid/selu/softplus/swiglu 都组合成 exp）、
  logf 34/7、floorf 19/3、exp2f 15/3、erff 13/4、sin/cos ~19/3、log2f 6/1、
  cos@sew64 2/1。

## 2. 修改思路（总述）

**在 lowering 层（`a100c/lower/vectorize.py` 的 `_vector_math_unary`）按
`(fn, sew)` 结构分派**：sew=32 且 fn ∈ {expf, exp2f, logf, log2f, erff,
floorf} 时发射**向量多项式 MIR 序列**（全部为既有 repertoire 形式：
vbin/vfmacc/vunary/vcmp/vsel/vmovv/s2v splat），不再产生 `vmath` op。
sin/cos/ceilf 与全部 sew=64（f64 内部宽度）保留 libm 路径。
`emit.py` 零改动（vmath 展开保留给非多项式函数）。

- 这是 matmul 轮 L5 教训的既定路线：修产生者（lowering），不加 MIR pass
  （架构契约 mir/v1 的 pass 列表不变，无 DesignIssue）。
- 不按算子名分派（结构分派于数学函数身份）。
- **回退开关**：`LowerOptions.vmath_libm: bool = False`，
  `A100C_VMATH_LIBM=1` 强制旧路径；identity_part 增加 `"vmath-libm"`
  （仅开关打开时）——照抄 `matrix_scalar_pack` 的三处接线
  （vectorize.py LowerOptions / driver.py CompileOptions+env / factory.py 透传）。
  缓存键已含 compiler_revision（代码摘要），新旧编译器产物天然隔离。
- 全部多项式运算在操作数自己的 (sew=32, lmul, vl) 区域内进行；**整型与
  浮点 op 共享同一 (sew,lmul,vl) 区域**，位重解释（vmovv f32↔i32）不切
  vsetvli——多项式体内零区域切换。
- 预期每 chunk 向量 op 数：exp ~26、log ~25、erf ~45、floor ~15
  （对比现状 ~330/chunk + 每元素一次 libm 调用）；预期 gelu/sigmoid 类
  每调用动态指令 **-93%~-97%**，纯逐元素 case 生成代码不变（0.0%）。

## 3. 各函数的 MIR 序列（已验证的算法与系数）

构建块（全部既有）：`vbin [a,b] op=fadd/fsub/fmul/fdiv/fmax/fmin`（浮点）
或 `add/sub/sll/srl/sra/and`（整型，结果 = a∘b）；`vfmacc (x,y,z) → x·y+z`
单舍入（Horner 主力）；`vunary op=fabs/fneg/fcvt(i→f)/fcvt.xf(f→i,rtz)`；
`vcmp [a,b] pred=lt/le/eq/ne fp=bool → mask`；`vsel [mask, then, else]`；
`vmovv(reg, vtype)` 位级重定型（f32↔i32，同 lmul）；`_splat_const`。

### 3.1 expf / exp2f（同一核心，exp2f 跳过第 1 步）

```
y    = fmul(x, LOG2E)                     # exp2f: y = x
t    = fadd(y, 12582912.0)                # 1.5*2^23 魔数；和落在 (2^23,2^24)，ulp=1
k    = fsub(t, 12582912.0)                # k = rne(y)（对 |y|<2^22 精确；exp 定义域内恒成立）
f    = fsub(y, k)                         # f ∈ [-0.5,0.5]，Sterbenz 精确
p    = Horner(f, EXP_P)                   # 5×vfmacc
two_f= vfmacc(f, p, 1.0)                  # 2^f = 1 + f·P(f)   [x=0 时精确 =1]
ki   = fcvt.xf(k)                         # rtz，k 整数 → 精确
k1   = sra(ki, 1); k2 = sub(ki, k1)       # k 二分（floor 除法）
s1   = vmovv( (k1+127)<<23 , i32→f32 )    # 2^k1
s2   = vmovv( (k2+127)<<23 , i32→f32 )    # 2^k2
res  = fmul(fmul(two_f, s1), s2)          # 二分缩放：次正规渐进下溢 ✓；k=128 → 溢出 +inf ✓
res  = vsel( vcmp(x, 88.72283935546875, gt), +inf, res )     # exp2f 阈值 127.9999
res  = vsel( vcmp(x, -104.0, lt), 0.0, res )                 # exp2f 阈值 -150.0
```
- NaN 自传播（two_f=NaN 使乘积 NaN，ki 为垃圾不影响）；±inf 被两个 select
  覆盖。k ∈ [-150,128] ⇒ k1+127, k2+127 ∈ [52,191]，`<<23` 不溢出。
- `EXP_P = [0.6931471857326423, 0.2402265086478695, 0.055503674298855665,
  0.00961806832877608, 0.001338565020577674, 0.0001545698671819237]`
  （chebfit 推导；2^f 逼近最大相对误差 3.6e-8）。

### 3.2 logf（log2f = logf · INV_LN2，多 1 次 fmul）

```
m_sub= vmand( vcmp(x,0,gt), vcmp(x, 1.1754943508222875e-38, lt) )   # 次正规输入
xs   = vsel(m_sub, fmul(x, 8388608.0), x)                           # ×2^23 规格化
ix   = vmovv(xs, f32→i32)
e    = sub( srl(ix, 23), 127 )
z    = vmovv( sub(ix, sll(e, 23)), i32→f32 )                        # z ∈ [1,2)
mb   = vcmp(z, 1.4142135623730951, gt)
zh   = vsel(mb, fmul(z, 0.5), z);  eh = vsel(mb, add(e, 1), e)      # 归约到 [√2/2, √2)
r    = fdiv( fsub(zh,1.0), fadd(zh,1.0) )                           # |r| ≤ 0.1716
r2   = fmul(r, r)
h    = Horner(r2, [1/3, 1/5, 1/7, 1/9])                             # 3×vfmacc
s    = vfmacc( fmul(r, r2), h, r );  s = fadd(s, s)                 # ×2（atanh 级数系数！）
ef   = fcvt(eh, i→f)
res  = fadd( fmul(ef, 0.693359375), fadd(s, fmul(ef, -2.12194440e-4)) )   # ln2 hi/lo
res  = vsel(m_sub, fsub(res, 15.942204913308808), res)              # -23·ln2
res  = vsel( vcmp(x,x,ne), NaN,            # NaN 守卫（必需：否则产生垃圾而非 NaN）
       vsel( vcmp(x,0,lt), NaN,
       vsel( vcmp(x,0,eq), -inf,           # 覆盖 ±0
       vsel( vcmp(x,+inf,eq), +inf, res ) ) ) )
```

### 3.3 floorf（三分支；ceilf 本轮不做——普查中未出现）

```
t    = fadd(x, 12582912.0);  r = fsub(t, 12582912.0)      # rne(x)，|x|<2^22 有效
res_s= vsel( vcmp(r,x,gt), fsub(r,1.0), r )
w    = fadd(x,x);  wi = vmovv(w, f32→i32)                 # [2^22,2^23) 带：ulp(x)=0.5
odd  = vcmp( and(wi,1), 0, ne )                           # 整型 pred（fp=False）
res_m= vsel( odd, fsub(x, 0.5), x )
res  = vsel( vcmp(fabs(x), 4194304.0, ge), res_m, res_s )
res  = vsel( vcmp(fabs(x), 8388608.0, ge), x, res )       # |x|≥2^23 恒整
```
- 魔数**必须 1.5·2^23**（2^23 对负 x 失效：和落入 ulp=0.5 区）；
  [2^22,2^23) 带必须用 2x 奇偶判别（魔数和落入 ulp=2 区，奇整数会被
  round 掉）。这两个坑都在模拟中踩到并修复，见 §5。
- NaN 自传播（r=NaN，比较 false → res_s=NaN）✓。

### 3.4 erff（分段）

```
ax   = fabs(x);  z = fmul(ax, ax)
p    = Horner(z, ERF_P_LO)                                # erf(t)=t·P(t²), |t|<1
pa   = fmul(x, p)
ti   = fdiv(1.0, z);  w = Horner(ti, ERF_TAIL_W)          # W(1/z), z ≥ 1
ez   = <exp 核心>( fmul(z, -LOG2E) )                      # e^{-z}（复用 3.1 核心，无需其溢出 select）
term = fdiv( fmul(ez, w), ax )                            # |x| ≥ 1，除法安全
one_m= fsub(1.0, term)
neg  = vcmp(x, 0, lt);  sgn = vsel(neg, -1.0, 1.0)
pb   = fmul(sgn, one_m)
res  = vsel( vcmp(ax, 4.0, ge), sgn,                      # |x|≥4: ±1（erf(4) 已 = f32 1.0）
       vsel( vcmp(ax, 1.0, ge), pb, pa ) )
res  = vsel( vcmp(x,x,ne), NaN, res )                     # NaN 守卫（必需）
```
- `ERF_P_LO = [1.1283791670949297, -0.3761263889320303, 0.1128379138964683,
  -0.026866140194897532, 0.005223812641953173, -0.0008543298099749196,
  0.00011964801459056699, -1.396267464929573e-05, 1.0729163118306902e-06]`
- `ERF_TAIL_W = [0.5641751233324483, -0.2813598202473231, 0.407041793198911,
  -0.8501695704192889, 1.8443547089405885, -3.406454802105437,
  4.794277470200201, -4.7842971297096035, 3.148805865370541,
  -1.2173561826391135, 0.20856641201419582]`
  （W 的相对误差 1.74e-6 = f32 Horner 消解噪声下限；对 erf 的绝对影响
  ≤ 0.157·1.74e-6 ≈ 3e-7，与 glibc 同级）。
- 尾部参数化必须用 **t=1/z 基底**（纯 z 基底的多项式不收敛，已实测）。

## 4. 数值验证（宿主端严格 f32 序列模拟，`tooling/fit_math_coeffs.py`）

模拟逐条对应将发射的 MIR 序列（vfmacc 以 f64 单舍入模拟；位操作用 int32
view；每步 f32 舍入）。参考 = **f32 输入的 f64 函数值再舍入 f32**
（f32 函数的真值；验证口径 bug 见 §5）。稠密网格 + 极值点（±0/±inf/NaN/
次正规/溢出边界）：

| 函数 | 正规区最大相对误差 | 次正规带 | inf/nan 类 |
|---|---|---|---|
| expf | 3.9e-6（集中于 \|x\|≈88，为 x·log2e 单次舍入所致；算法本体 ~1.2e-7） | ≤32 ulp（abs ≤ 4.5e-44） | ✓ |
| exp2f | 1.2e-7 | 1 ulp | 1 点待查（±inf 网格点） |
| logf / log2f | 2.0e-7 / 2.4e-7（次正规输入带 8.7e-8） | — | ✓（需 NaN 守卫） |
| floorf | **0**（420 万点） | — | ✓ |
| erff | 4.2e-7 | — | ✓（需 NaN 守卫） |

范围 case 容差 rtol=atol=2e-3（gelu/sigmoid/tanh 等声明值），上述误差
裕度 ≥ 500×。可选精化：LOG2E hi/lo 分裂可把 expf 大 \|x\| 区压到 ~2e-7。

## 5. 实现时必须避免的坑（模拟阶段已踩过）

1. **log 级数 ×2 因子**：log((1+r)/(1-r)) = 2(r + r³/3 + …)，漏 ×2 则
   结果恰为一半。
2. **floor 魔数**：必须 1.5·2^23（2^23 对负 x 落入 ulp=0.5 区）；且
   [2^22,2^23) 带必须 2x 奇偶判别（1.5·2^24 的偶数格点会把奇整数 round 掉）。
3. **exp 溢出/下溢 select 必须做在原始 x 上**（k 间接判定在魔数失效区
   不可靠）；k 二分缩放天然处理次正规渐进下溢与 k=128 的 +inf。
4. **exp2f 的阈值**：over 127.9999（2^x > f32max）、under -150.0。
5. **erf/log 的 NaN 守卫必需**（比较链全 false 会落到非 NaN 分支）；
   exp/exp2/floor 的 NaN 自传播已证。
6. **验证口径**：参考必须取 f32 输入的函数值（f64 格点直接算参考会把
   输入舍入误报为误差——x≈1 处可虚报 2.7e-3）。
7. **erf 尾部拟合基底** t=1/z；2^f 多项式用 `1 + f·P(f)` 形式（x=0 精确）。

## 6. 接线与验证清单（实现者执行）

接线（照抄 matrix_scalar_pack 模式）：
- `a100c/lower/vectorize.py`：`LowerOptions.vmath_libm=False` +
  `identity_part()` 追加 `"vmath-libm"`；`_vector_math_unary`（~9876 行）
  sqrt/rsqrt 早退之后、fn-map 之前插入多项式分派；系数表与
  `_vmath_poly` 系列方法放同文件（~300 行）。
- `a100c/driver.py`：`CompileOptions.vmath_libm` + `A100C_VMATH_LIBM=1`
  env + `identity_part()`。
- `a100c/factory.py`：透传至 LowerOptions。
- `tools/profiling/fit_math_coeffs.py`：从 `tooling/` 移入（推导+验证脚本）。

验证顺序：
1. 单测（a100c/tests/test_math_ops.py 增例）：各 fn 走多项式路径
   （stage.mir.legalized.txt 无 vmath op）+ 执行比较 PASS +
   `A100C_VMATH_LIBM=1` 身份不同且走旧路径。
2. 宿主端复跑 fit_math_coeffs.py（系数/边界不回归）。
3. scoped scan：134 算子 683 cases t1 全 PASS（命令见 baseline/scan/）；
   对比 baseline 的 max_abs_error（预期 ~1e-6 级，原 ~1e-7 级）。
4. 开关对照：同 case default vs A100C_VMATH_LIBM=1 双 PASS。
5. 指标复测：collect_metrics 重跑 13 个基线 case（预期 gelu/erf/sigmoid/
   selu/tanh/softplus/pow/swiglu -93%~-97%；纯逐元素 0.0%）；再取
   代表 case 的 1/2/4/8 worker。
6. 全量输入回归（2734）+ 三个 behaviour 检查（check_no_name_dispatch
   --witness 等）。

## 7. 残余机会（本轮不做，汇编普查所得，供后续轮）

1. sinf/cosf 多项式（19 ids/3 算子仍走 libm）。
2. emit 侧 vmath 循环的归纳变量驻栈（每元素 4×ld/sd）——寄存器化 ~2×。
3. 每 chunk 标量地址重算（li+add+li+mul+add）→ 指针递归（L13）。
4. 每 chunk 掩码重建（vid.v+vadd+vmv.v.x×2+vadd.vv+vmslt+vmv1r×2+vmerge
   ≈9 向量 op）→ 前缀掩码改精确 vl（需 TIR 级合法性分析：掩码为连续
   前缀且禁用 lane 消费者全为同掩码 store）。
5. 循环体内 (sew,lmul) 区域交替的 vsetvli churn（MIR 不变量"区域不跨块"）。
6. 多项式常数 splat 每 chunk 体重发（~26 标量指令/chunk；寄存器不跨块）。
7. fp16/bf16 掩码窄 store 走 staging+逐元素标量拷贝（vslidedown+vmv.x.s
   每元素 ~6 条）。

## 8. 证据索引（绝对路径）

- 基线扫描：`docs/compiler-agent/optimizations/elementwise/baseline/scan/`
  （683/683 PASS，report.json + journal.jsonl）
- 基线指标：`docs/compiler-agent/optimizations/elementwise/baseline/metrics/`
  （13 case：metrics.json；原始 per-PC counts 留在 /tmp/opt-ew，可重采）
- vmath 普查：`baseline/vmath_census.json`；范围清单：
  `baseline/operators-elementwise-family.txt`；锚点：`baseline/CONTEXT.txt`
  （HEAD 4217b79）
- 系数推导+验证脚本与输出：`tooling/fit_math_coeffs.py`、
  `tooling/fit_validation_output.txt`
- gelu 基线汇编（瓶颈现场）：`a100c/cache/63f20fc874428ac43ab7e3a8e8aa916b33fbe1da09e1098318cf36159497e2a4/program.S`（主仓库缓存，123-142 行）
- 工作副本（含未实施改动的 git 基线）：`/tmp/opt-ew`（git log: f4b4ae7
  baseline @ 4217b79）
