# RUNBOOK — 用这个语料库编译得最快

给**写编译器 / 驱动编译的 agent**。目标只有一个：**在预算内把整个语料库编译通、
跑通、并且能反复跑**。目标无关，不含 torch，正确性一律对 NumPy 参考。

下面所有命令都在本项目的 `ops/` 目录下执行。

---

## 0. 先记三条数

| 量 | 值 | 意思 |
|---|---|---|
| **case** | 3465 | `(算子, shape, dtype)`。**不是**编译单元 |
| **identity** | 1511 | 真正的编译单元 = 源码 + dtype + constexpr meta + launch cfg，**不含 shape/grid** |
| **cases/identity** | 2.29 | 一个身份平均覆盖 2.29 个 case |

总编译时间 ≈ `identity 数 × 单次成本`。**只降 case 数没用，必须降身份数或单次成本。**
两个旋钮都在语料里（shape 的规模档、constexpr 的取值），不在编译器里。

---

## 1. 三条车道，别混用

| 车道 | 目的 | 规模 | 预算 |
|---|---|---|---|
| **dev** | 内循环，改一行就想知道有没有坏 | 一组（`--group basic`）或 `--limit` | ≤5 min |
| **gate** | 每轮验收 | 全量 3465 case / 1511 身份 | **≤15 min 冷跑**，p99 ≤10 s/身份 |
| **perf** | 性能，只跑 `suite/perf/`（100 算子，真尺寸） | 100 算子 | 独立车道，不进正确性 gate |

`suite/perf/` 的 shape 是**性能尺寸**，`suite/dev/` 的是**语义尺寸**
（只覆盖"对齐/尾块/退化"这些布尔性质，不追求规模）。**不要**把两边的 shape 互相搬。

---

## 2. 五条命令

```bash
# ① 规模 & 身份普查(不编译,几秒)
python3 harness/compiler_api/run_cases.py --dry-run
python3 harness/compiler_api/run_cases.py --dry-run --identities
python3 harness/compiler_api/run_cases.py --dry-run --identities --group basic

# ② 生成并行驱动的任务表(按身份去重 + 重尾优先排序)
python3 harness/compiler_api/run_cases.py --dry-run --identities \
        --schedule runs/schedule.json

# ③ 门禁:全量跑一遍 + 判定预算(退出码 0/1,可直接给 CI)
python3 harness/compiler_api/gate.py --device cuda --report runs/gate.json
python3 harness/compiler_api/gate.py --device mycompiler:Device \
        --compile-budget 10 --max-wall 900 --max-p99 10

# ④ 内循环:只跑一组 / 只跑一个算子
python3 harness/compiler_api/run_cases.py --device cuda --group basic
python3 harness/compiler_api/run_cases.py --device cuda --operator suite/dev/matmul_kernel.py

# ⑤ 长跑:可断点续跑 + 心跳 + 每 case 三重资源上限
python3 harness/compiler_api/run_cases.py --device mycompiler:Device \
        --journal runs/all.jsonl --heartbeat runs/all.status.json --resume \
        --case-timeout 120 --case-cpu-seconds 300 --case-memory-mb 16384 \
        --progress-every 25 --report runs/all.json
```

`--device` 取值：

| 值 | 含义 |
|---|---|
| `cpu` | NumPy 解释器，只验证 case 层（不编译） |
| `cuda` | **stock Triton 3.8**，torch-free。语料自身的参照实现 |
| `torch-gpu` / `torch-cpu` | torch 参照（只给基线用，不进正确性 gate） |
| `module:attr` | **你自己的编译器适配器**，按 `COMPILE_CONTRACT.md` 实现 |

---

## 3. 最快编译的 8 条（按收益排序）

1. **按身份编译，不按 case 编译。** 每个身份编译一次，它的所有 case 复用 artifact。
   现在 newops 是 2.33×（grid 进了 cache key），updateops 是 1.0×。
   *验收*：`--dry-run --identities` 里 `cases/id` ≥ 1.25。
2. **语料 shape 用语义尺寸。** 实测：`17×33×1000` 编 1193 s，`17×33×100` 只要几秒；
   `256×512×2048` 编 1058 s，`128³` 编 3.4 s。**38× 的差距，语义覆盖一模一样。**
   正确性语料的 dot 类 `M,N,K ≤ 128`；attention `seq ≤ 128`、`head_dim ∈ {32,64,128}`。
3. **干掉 shape 派生的 constexpr。** 现状：1511 个身份里 **247 个**只是因为
   `NUM_K_BLOCKS` / `NTILES` / `EVEN_*` 这类"shape 算出来的"常量才存在
   （看 `--identities` 输出的 `structural` 行：1264）。把这些改运行时标量能直接少 16%。
4. **tile 预算**：正确性语料 `BLOCK` 取 16/32（真 tile 留给 `suite/perf/`）。
   matmul 实测 vreg 12,377 → ~800，regalloc 23.6 s → ~1 s。
5. **编译成本设上限，且上限是失败类。** 超过预算记 `COMPILE_BUDGET_EXCEEDED`
   （`gate.py --compile-budget`），归因**编译器**，不许靠删 case 掩盖。
   建议：dev 10 s、生产天花板 60 s、整轮 gate 15 min。
6. **分片缓存 + 批处理。** 16 个 worker 各用独立 cache 目录（`build/cc-w{i}/`），
   每个 worker 吃一批身份而不是一个 case：
   "每 case 一个进程"在 4426 case 上 ≈ 13 min 纯 `import`。
7. **重尾优先（LPT）。** 按上轮成本降序投递，否则墙钟由最后启动的那个慢身份决定。
   `--schedule` 已经按 `cost_hint_s` 排好序。
8. **编译器版本指纹别用整个目录的哈希。** newops 的 `COMPILER_VERSION` 是
   `compiler/` 下所有 .py 的 sha256 → 改一行注释，2401 个 artifact 全失效。

---

## 4. 16 进程驱动怎么接（`schedule.json`）

```bash
python3 harness/compiler_api/run_cases.py --dry-run --identities \
        --schedule runs/schedule.json
```

```json
{
  "tier": "meta",
  "identities": 1511,
  "cases": 3465,
  "items": [
    {"identity": "54f6b31e0c0d", "operator": "suite/dev/sum.py", "kernel": "sum_kernel",
     "cost_hint_s": null,
     "cases": [{"shape": [2, 128], "dtype": "float32"}, ...]}
  ]
}
```

驱动规则：

1. 任务单元 = **一个 item**（一个身份），不是 case；
2. `items` 已按 `cost_hint_s` 降序 —— **按顺序投递**；上一轮的实测成本回填到
   `cost_hint_s`，排序会自己变好；
3. 每个 worker：`compile(identity)` → 对该 item 的每个 case `launch` + 与 NumPy 比；
4. 每个 worker 用独立编译缓存分片，写自己的 journal（`runs/xx.shard-{i}.jsonl`）；
5. 单个身份超过预算 → 记 `COMPILE_BUDGET_EXCEEDED` 继续跑，**不要中止整轮**。

协议细节（工作流的适配器要实现什么）见 [`COMPILE_CONTRACT.md`](COMPILE_CONTRACT.md)。

---

## 5. 门禁的判定标准

`gate.py` 退出码 0 才是通过，五个 check 全绿：

| check | 默认 | 说明 |
|---|---|---|
| `no_failures` | — | 有任何非 PASS 即红 |
| `dedupe` | `cases/id ≥ 1.25` | 编译次数没有显著多于身份数 |
| `p99` | `≤10 s` | 身份级编译 p99 |
| `wall` | `≤900 s` | 整轮墙钟（冷跑） |
| `budget` | 若给了 `--compile-budget` | 超预算身份数必须为 0 |

**冷跑才算数**：stock Triton 有磁盘缓存，第二次跑会把 `compile` 测成 0。

```bash
rm -rf /tmp/cc && TRITON_CACHE_DIR=/tmp/cc python3 harness/compiler_api/gate.py --device cuda
```

---

## 6. 现状基线（可直接对账）

**语料**：500 算子 / 2893 case / 1422 身份（`dtype` 口径 630、`triton` 口径 1079、
`structural` 口径 1217）。`suite/dev` 400 算子 1717 case，`suite/perf` 100 算子 1176 case。

**stock Triton 3.8（`--device cuda`，冷编译）**：身份级 0.36 s 量级
（basic 组实测 264 身份 96 s / p99 2.0 s）；本语料 1422 身份 ≈ **8–12 min 单线程**。

**一个自研编译器（updateops，350 算子那版、改 shape 前）**：876 身份 / 158 min /
p50 0.60 s / p90 19.5 s / p99 195 s / max 1193 s；
其中 **148 个 ≥10 s 的身份吃掉 95% 的时间**，9 个 ≥100 s 的吃掉 64%。
改成语义尺寸后估计 **35–40 min**；本语料 1422 身份按其单价估计 **30–40 min 单线程**，
16 并发 **4–6 min**。

这张表就是"预算"的来源：**整轮时间由尾部决定，尾部由少数大 shape 决定。**

---

## 7. 报错了怎么读

| 状态 | 是谁的问题 | 怎么办 |
|---|---|---|
| `PASS` | — | — |
| `CASE_FAIL` | 语料 | `make_case`/`ref` 抛异常 → 修算子文件 |
| `MISMATCH` | 编译器**或**语料 | 先确认 NumPy 参考对不对，再查 kernel |
| `LAUNCH_FAIL` | 编译器 | 设备未接线 / launch 太早返回 |
| `TIMEOUT` | 编译器（编译慢）或语料（死循环） | 加 `--case-timeout` 定位到具体 case |
| `COMPILE_BUDGET_EXCEEDED` | **编译器** | 不是语料缺陷：要么修编译（vreg 膨胀、无谓展开），要么声明不支持并给诊断 |
| `OOM` | 编译器 | 同上；用 `--case-memory-mb` 把爆炸限制在单个 case |

**红线**：不许用"删掉这个 case / 放宽容差 / 改 `ref` 的数值语义"让红变绿。
慢或崩的 case 是**信息**，不是噪声。

---

## 8. 常见坑（都踩过）

- **grid 进 cache key** → 每个 shape 都是新编译（newops：3465 次 vs 1511 身份）。
- **shape 派生 constexpr**（`EVEN_M`、`NTILES`、`NUM_K_BLOCKS`）→ 身份数随 shape 膨胀。
- **整目录哈希当版本号** → 改注释丢全部 artifact。
- **每 case 一进程** → 启动开销吃掉整轮时间。
- **`--group-order` 只用于看规模**，跑全量直接用默认（顺序稳定、可 shard）。
- **CUDA context 占几十 GiB 虚拟地址空间** → 别用 `RLIMIT_AS` 限内存，用
  `--case-memory-mb`（RSS 看门狗）或 cgroup。
