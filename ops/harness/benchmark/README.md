# 性能基准(suite/perf,100 算子)

性能测试**复用 `suite/perf/` 的 100 个算子**:同一批文件既是正确性输入,又在**稳态 shape**下
计时。只比较 **kernel 时间**,与 stock Triton 的同一 kernel 逐项对比(加速比)。正确性由
`harness/compiler_api/run_cases.py` 负责。

> **为什么不直接用 `SHAPES`**:`SHAPES` 是正确性用例,绝大多数只有几千到几十万个元素,
> launch-bound。性能必须在稳态 shape 上测,由执行设备的末级缓存推导。

## 速查

**门槛**:每个 class(memory / reduction / compute)的 geomean 加速比 ≥ 0.80。写编译器的
agent 把输出写进自己的项目仓库(`--out-dir`),不要写进语料。

```bash
EVID=<项目仓库>/bench-evidence

# 1) stock Triton 基线(同机同 shape;torch 版参考装置)
python3 harness/benchmark/run.py --device torch-gpu --baseline --out-dir $EVID

# 2) 你的编译器(先对拍后计时)
python3 harness/benchmark/run.py --device yourmod:make_device --out-dir $EVID

# 3) 逐类 geomean 加速比
python3 harness/benchmark/report.py --results-dir $EVID --out $EVID/BENCH_SUMMARY.json
```

读数规则:

- **`kernel_s` = median**(设备端计时,不含 host launch 开销);`compile_s` = 首次 launch
  (含编译);`n_samples` = 采样次数。
- **输出在 `<out-dir>/<device-fingerprint>/`**:`--baseline` → `BENCH_TRITON.json` +
  `evidence-triton/`;普通运行 → `BENCH_REPORT.json` + `evidence/`;`--verify-only` →
  `BENCH_VERIFY.json` + `evidence-verify/`。`--out-dir` 默认是语料根下的 `results/`(不进 git)。
- 每条记录带 `verified: true|false`,**未对拍(`--no-verify`)的编译器记录不计分**。
- **`report.py` 只在两边 `operator_sha256` 和 shape 都一致时配对**;改过算子或换 shape,
  旧基线列为 stale、不进 geomean——这是刻意的防错。
- 只比较同方法学的运行(`--timer` / `--stat` 一致)。

## 组成

`suite/perf/workload.json` 每个 entry 一条:`id`、`operator`(`suite/perf/<id>.py`)、`class`、
`pattern`(计算模式)、`dtype`、`declared_shape`(典型 shape)、`scale`(稳态尺寸规则)、
`ref_split`(见下)。按计算模式选材,每个模式几个算子,任何一个模式都不主导一类的 geomean:

| class | 计算模式 |
|---|---|
| `memory` | 逐元素(超越函数 / 简单 / 融合 / 位运算 / 多项式)、broadcast、跨步访问、gather、layout shift、stencil(小通道卷积)、pooling、GEMV、量化、循环递推 |
| `reduction` | 行归约、arg 归约、softmax / logsumexp、norm、loss、相似度 |
| `compute` | GEMM、带融合 epilogue 的 GEMM、GEMM + 归约 epilogue、batched / 低精度 dot、attention、线性注意力、小矩阵线性代数 |

逐 class / pattern 的数量:`python3 -c "import json,collections;w=json.load(open('suite/perf/workload.json'));print(collections.Counter((e['class'],e['pattern']) for e in w['entries']))"`。

`suite/perf/` 的 100 个算子在上游选材时从 tritonbench 候选池挑出后随语料一起发布,
**与 `suite/dev/` 的 kernel 互不重复**;它们只改写了 `OPERATOR` 头并加 `BENCH_SOURCE`
记录来源。选材池本身不在本镜像内,所以 `select.py`(重新选材)在这里不适用;
workload 与算子文件已就位,`run.py` 直接读 `suite/perf/workload.json` 即可。

## 测量口径(只测 kernel)

- **搬运一次**:输入只 staging 一次,不计时;相邻 entry 复用已上传 buffer 的条件是两个 case
  都把它声明为纯输入且逐字节相同;输出缓冲每次重新分配并清零。
- **首次 launch 单独计时**为 `compile_s`。
- **计时优先设备端**:默认用设备 event(`timer: "device"`);设备没有 `timer()` 时退回
  `perf_counter + synchronize` 并标 `timer: "host"`。
- **自适应采样**:至少 `--min-samples`(默认 50)次,直到累计 `--min-time-s`(默认 0.2s),
  上限 `--max-samples`(默认 1000);主指标是 median。
- host↔device 搬运、`make_case` 的参考计算都不进入指标。
- 每条记录带溯源:`operator_sha256`、workload sha、解析 shape、设备属性、版本、git commit。

## 稳态尺寸

每个 entry 只存一条**尺寸规则**,由 `size.py` 按执行设备的末级缓存解析:

- 带宽类(memory / reduction):工作集 ≈ 8 × LLC(`--llc-bytes`,默认取设备 L2),按 entry
  的 dtype 计算字节数;
- 计算类与形状有语义的算子:`fixed` 规则给出明确 shape(如 2048³ GEMM、2048 token 注意力)。

```bash
python3 harness/benchmark/size.py --llc-bytes 134217728   # 查看解析后的稳态 shape
python3 harness/benchmark/size.py --check                  # 小块验证每条规则可用
```

## 造数据为什么不再是瓶颈

稳态 case 每个张量几百 MiB,原来的单线程 numpy 造数据和 float64 `ref` 一个 entry 要 5–10 s,
远大于 kernel 本身。现在:

- 所有算子的 case 层用 `case_utils.fast_rng(seed)`:≥ 4M 元素的抽样按固定 4M 分块、每块独立
  子种子在线程池里填充(结果只取决于 seed,与线程数无关);小抽样与 `default_rng` 逐位相同。
  `OPS_DATAGEN_THREADS` 控制线程数(默认 min(32, 核数))。
- `workload.json` 里 `ref_split: "rows"` 的 entry(逐行独立的 `ref`),期望值按行分块在
  线程里计算。只有在验证 shape 上**分块结果与整体结果逐位相同**的算子才会被标记
  (`select.py` 用 `opslib.case.split_ref_is_exact` 检查)。
- 预构建 golden:`python3 -m opslib golden --build --workload suite/perf/workload.json -j 16`
  (需要 `PYTHONPATH=harness`),之后每次运行直接读缓存。

## 稳态验证

`run.py --verify-only` 在稳态 shape 下逐个对拍(只跑一次,不计时),确认每个 entry 放大后
依然正确。"小 shape 能过、放大就挂"的 kernel 不能进基准。

```bash
python3 harness/benchmark/run.py --device torch-gpu --verify-only
python3 harness/benchmark/run.py --device torch-gpu --verify-only --group compute
```

autotune 算子在 `--device cuda`(拦截 torch)上会 `LAUNCH_FAIL`:stock Triton 的 autotuner
计时时要 import torch。这是参考装置的限制;基线用 `--device torch-gpu`。

## 重新选材

候选池不在镜像里(选材工具只在语料维护仓库中运行,本项目不含候选池)。选材表在 `select.py` 的 `PICKS`(class、pattern、池中文件名、可选的
固定 shape),脚本会拒绝 kernel 与前三组重复的候选和无法放大的候选,然后写出
`suite/perf/*.py` 与 `suite/perf/workload.json`:

```bash
# select.py 需要语料维护仓库里的候选池,本项目不含
# select.py 需要语料维护仓库里的候选池,本项目不含
```

新选出的 entry 必须过稳态对拍(`run.py --verify-only`)才能留下;过不了就换候选。
