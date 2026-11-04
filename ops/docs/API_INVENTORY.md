# tl API 清单(生成物)

由 `python3 harness/compiler_api/api_inventory.py` 从两个输入目录(suite/dev、suite/perf)的 kernel AST 生成,**不要手改**;
算子变了就重新生成。表中数字是**使用该构造的算子文件数**(每个文件最多计一次)。

这是语料**用到了什么**(语言的一个样本),不是语言的规范:一个构造没出现在这里,不代表编译器
可以不支持它;出现在这里的每一个,编译器都必须支持或明确拒绝。

扫描范围:suite/dev 400, suite/perf 100,共 500 个算子文件。

## 调用与装饰器(`tl.*(...)`、`triton.*(...)`、`@...`)

| 构造 | suite/dev | suite/perf | 合计 |
|---|---:|---:|---:|
| `@triton.jit` | 400 | 100 | 500 |
| `tl.store` | 387 | 100 | 487 |
| `tl.load` | 381 | 100 | 481 |
| `tl.arange` | 374 | 92 | 466 |
| `tl.program_id` | 364 | 93 | 457 |
| `tl.sum` | 154 | 41 | 195 |
| `tl.where` | 144 | 38 | 182 |
| `tl.zeros` | 128 | 19 | 147 |
| `tl.maximum` | 63 | 15 | 78 |
| `tl.dot` | 68 | 6 | 74 |
| `tl.exp` | 50 | 23 | 73 |
| `tl.max` | 51 | 19 | 70 |
| `tl.abs` | 61 | 5 | 66 |
| `tl.cdiv` | 55 | 4 | 59 |
| `tl.full` | 54 | 2 | 56 |
| `tl.sqrt` | 35 | 16 | 51 |
| `tl.log` | 31 | 13 | 44 |
| `tl.minimum` | 38 | 6 | 44 |
| `tl.min` | 26 | 4 | 30 |
| `tl.range` | 25 |  | 25 |
| `tl.constexpr` | 22 |  | 22 |
| `tl.num_programs` | 22 |  | 22 |
| `tl.reshape` | 22 |  | 22 |
| `tl.static_range` | 21 |  | 21 |
| `tl.multiple_of` | 20 |  | 20 |
| `tl.sigmoid` | 5 | 12 | 17 |
| `tl.rsqrt` | 15 | 1 | 16 |
| `tl.trans` | 12 | 2 | 14 |
| `tl.exp2` | 12 |  | 12 |
| `@triton.autotune` | 5 | 6 | 11 |
| `tl.atomic_add` | 11 |  | 11 |
| `tl.erf` | 4 | 6 | 10 |
| `tl.make_block_ptr` | 9 |  | 9 |
| `tl.cast` | 6 | 2 | 8 |
| `tl.argmax` | 7 |  | 7 |
| `tl.debug_barrier` | 7 |  | 7 |
| `tl.floor` | 7 |  | 7 |
| `tl.philox` | 7 |  | 7 |
| `tl.advance` | 5 |  | 5 |
| `tl.cos` | 3 | 2 | 5 |
| `tl.join` | 5 |  | 5 |
| `tl.log2` | 5 |  | 5 |
| `tl.sin` | 3 | 2 | 5 |
| `tl.split` | 5 |  | 5 |
| `tl.argmin` | 4 |  | 4 |
| `tl.cumsum` | 4 |  | 4 |
| `tl.div_rn` | 2 | 2 | 4 |
| `tl.permute` | 4 |  | 4 |
| `tl.rand` | 4 |  | 4 |
| `tl.atomic_max` | 3 |  | 3 |
| `tl.atomic_min` | 3 |  | 3 |
| `tl.broadcast_to` | 3 |  | 3 |
| `tl.static_assert` | 3 |  | 3 |
| `tl.zeros_like` | 3 |  | 3 |
| `tl.atomic_xchg` | 2 |  | 2 |
| `tl.cat` | 2 |  | 2 |
| `tl.clamp` | 2 |  | 2 |
| `tl.cumprod` | 2 |  | 2 |
| `tl.dtype` | 2 |  | 2 |
| `tl.fma` | 2 |  | 2 |
| `tl.randn` | 2 |  | 2 |
| `tl.ravel` | 2 |  | 2 |
| `tl.squeeze` | 2 |  | 2 |
| `tl.add` | 1 |  | 1 |
| `tl.atomic_and` | 1 |  | 1 |
| `tl.atomic_cas` | 1 |  | 1 |
| `tl.atomic_or` | 1 |  | 1 |
| `tl.atomic_xor` | 1 |  | 1 |
| `tl.broadcast` | 1 |  | 1 |
| `tl.ceil` | 1 |  | 1 |
| `tl.expand_dims` | 1 |  | 1 |
| `tl.flip` | 1 |  | 1 |
| `tl.gather` | 1 |  | 1 |
| `tl.histogram` | 1 |  | 1 |
| `tl.interleave` | 1 |  | 1 |
| `tl.max_contiguous` | 1 |  | 1 |
| `tl.mul` | 1 |  | 1 |
| `tl.pointer_type` | 1 |  | 1 |
| `tl.rand4x` | 1 |  | 1 |
| `tl.randint` | 1 |  | 1 |
| `tl.randint4x` | 1 |  | 1 |
| `tl.randn4x` | 1 |  | 1 |
| `tl.reduce_or` | 1 |  | 1 |
| `tl.softmax` | 1 |  | 1 |
| `tl.sort` | 1 |  | 1 |
| `tl.sqrt_rn` | 1 |  | 1 |
| `tl.sub` | 1 |  | 1 |
| `tl.to_tensor` | 1 |  | 1 |
| `tl.topk` | 1 |  | 1 |
| `tl.unsqueeze` | 1 |  | 1 |
| `tl.view` | 1 |  | 1 |
| `tl.xor_sum` | 1 |  | 1 |

## dtype 与常量(`tl.float16`、`tl.constexpr` 等非调用属性)

| 构造 | suite/dev | suite/perf | 合计 |
|---|---:|---:|---:|
| `tl.constexpr` | 365 | 85 | 450 |
| `tl.float32` | 240 | 35 | 275 |
| `tl.int64` | 139 |  | 139 |
| `tl.int32` | 51 | 3 | 54 |
| `tl.bfloat16` | 25 |  | 25 |
| `tl.float16` | 24 |  | 24 |
| `tl.float64` | 16 |  | 16 |
| `tl.uint32` | 12 |  | 12 |
| `tl.int1` | 9 |  | 9 |
| `tl.tensor` | 8 |  | 8 |
| `tl.uint64` | 5 |  | 5 |
| `tl.int16` | 4 |  | 4 |
| `tl.int8` | 4 |  | 4 |
| `tl.uint16` | 1 |  | 1 |
| `tl.uint8` | 1 |  | 1 |
