# ops/AGENTS.md — 这份输入语料怎么用

**只读本目录就够了**:这里包含输入算子、运行器、门禁与全部说明,不需要任何
目录之外的东西(除运行时的 golden 缓存 `$HOME/.cache/ops-golden`)。命令一律在
本目录(`ops/`)下执行。

## 阅读顺序(写完编译器为止)

| 顺序 | 文件 | 什么时候读 |
|---|---|---|
| 1 | `harness/compiler_api/AGENT_GUIDE.md` | **先读**:怎么把编译器接进来、Device 协议、四状态反馈、case 字段 |
| 2 | `harness/compiler_api/RUNBOOK.md` | 怎么编译得最快:按身份编译、三条车道、预算 |
| 3 | `harness/compiler_api/COMPILE_CONTRACT.md` | 接适配器时:五个方法 + `schedule.json` / `gate.json` 格式 |
| 4 | `docs/SUBSET.md` | 声明的推理子集:五条原则、包含/排除的构造 |
| 5 | `docs/SUITE_V3.md` | 想知道"为什么是这些算子、覆盖了什么、holdout 怎么切";`docs/SUITE_V2.md` 是上一版(目标无关)历史 |
| 6 | `docs/API_INVENTORY.md` | 要实现哪些 `tl.*` 构造(500 个算子的 AST 统计) |
| 7 | `docs/CORPUS_USAGE.md` · `docs/COVERAGE_MATRIX.md` · `harness/benchmark/README.md` | 需要时查阅 |

## 这是什么

**声明的推理子集**(LLM inference)上的 Triton 算子语料,经五条原则
(`docs/SUBSET.md`)+「语义覆盖 + 编译经济学」筛选后的开发集。前向-only:
无 backward、无 fp8、无 `input_precision=`/`allow_tf32=`,fp32 dot 为 IEEE
(runner 固定 `TRITON_F32_DEFAULT=ieee`)。

```
suite/dev/    400 算子 / 2192 case   正确性车道,语义尺寸(<=128);fp32/fp16/bf16 推理 dtype
suite/perf/   100 算子 /  542 case   性能车道;bf16 为主 dtype,稳态计时尺寸由 workload.json 解析
suite/manifest.json                  机器可读清单(族/特征/交互/成本/来源)
suite/heldout.json                   500 个 held-out 算子(按 origin;只在维护分支,发布包不含)
docs/SUBSET.md                       五条原则、包含/排除的构造
docs/SUITE_V3.md                     选区方法、前后对比、覆盖、验证状态、评估协议
docs/CORPUS_USAGE.md                 怎么用(可替换 KICKOFF 的语料节)
```

合计 **500 算子 / 2734 case / 2161 编译身份**(cases/identity = 1.26)。
池 = **1000 算子 / 5612 case**(维护者本地保管,不入 git、不进发布包),
universe 1600 算子;选材来源池**不在本镜像内**;本目录是自包含的,
`suite/` 就是全部输入。

## 命令

```bash
python3 harness/compiler_api/run_cases.py --manifest suite/manifest.json --dry-run --identities
python3 harness/compiler_api/run_cases.py --device cuda --manifest suite/manifest.json --jobs 8
python3 harness/compiler_api/gate.py --manifest suite/manifest.json --compile-budget 10 \
        --max-wall 900 --max-p99 10 --report gate.json
python3 harness/compiler_api/run_cases.py --dry-run --identities --schedule runs/schedule.json
```

`python3 -m opslib catalog|golden ...` 需要 `PYTHONPATH=harness`。

## 规则

- **算子文件只放算子**;新脚本一律进 `harness/`。
- **零 torch**:算子文件不 import torch;正确性入口默认拦截 torch(`--allow-torch`
  只用于 stock Triton 的 autotuner,它自己会 import torch)。
- **case 层用 `case_utils.fast_rng(seed)`**,不直接用 `np.random.default_rng`。
- **不放宽容差、不改 `ref` 的数值语义、不删 case** 来让某个实现通过;
  慢或崩的 case 是信息,不是噪声。
- **shape 是语义尺寸,不是性能尺寸**:正确性语料 dot 类 `M,N,K <= 128`、
  attention `seq <= 128`、`head_dim ∈ {32,64,128}`;大 K / 大 seq 只出现在
  `suite/perf/`(性能车道)。
- **声明不支持,不要加入**:`dot_scaled`/fp4、int4、`inline_asm_elementwise`、
  tensor descriptor(TMA)、`tl.extra`/`tl.math`/libdevice;`tl.tanh`/`tl.pow`
  在 Triton 3.8 不存在。

## 架构

- **算子文件**:docstring + 字面量 `OPERATOR` + 来源记录 + 唯一的 `@triton.jit`
  + case 层(`SHAPES`、`DTYPES`、`ref`、`_make_case`、`make_case`)。
- **`harness/opslib/`**:共享实现(`runner`、`device`、`case`、`compare`、
  `golden`、`catalog`、`mathref`)。
- **`harness/compiler_api/`**:`run_cases.py`(正确性入口)、`gate.py`(编译门禁)、
  `identity.py`(身份普查)、`RUNBOOK.md`(怎么最快编译)、
  `COMPILE_CONTRACT.md`(适配器协议)。
