# 门控探针记录（matmul 优化轮）

固定执行端点：`$A100_QEMU`（jdsk-qemu-10.0.2 用户态 qemu-riscv64），
`-L $A100_SYSROOT -cpu max,vlen=1024,elen=64,vext_spec=v1.0`；交叉汇编
`-march=rv64gcv`（同 a100c/runtime/build.py ASFLAGS）。两探针均双跑一致。

## probe-strided.S —— 跨步向量访存（B 打包所需形态）

结果：**全 PASS**（标记 1-6 依次打印，exit 0，双跑一致）。

| # | 形态 | 结果 |
|---|---|---|
| 1 | `vlse16.v` 步长 128B、vl 8（打包确切 gather 形态） | PASS，逐 lane 数据正确 |
| 2 | `vlse16.v` 步长 2B、vl 32（近单位步长） | PASS |
| 3 | `vlse8.v` 步长 3B、vl 5（奇数字节步长、8 位数据） | PASS |
| 4 | `vsse16.v` 步长 128B、vl 8（跨步存储侧） | PASS，未写位置保持零 |
| 5 | e64/m2 区域（avl 16）→ e16/m1 + vlse（区域切换形态） | PASS |
| 6 | avl 0：vlse/vse 无操作且不故障 | PASS |

结论：**固定 QEMU 的已记录索引式缺陷（e64 索引 + 子 32 位数据 SEGFAULT，
vectorize.py:2579）不覆盖跨步形式**；本轮的 B 打包向量化在仿真器证据上成立。

## probe-e64m2.S —— 迭代中发现的新仿真器约束

结果：**`vmv.v.i` 与 `vmv.v.x` 在 e64/m2 区域 SIGILL**（avl 16 与 32 均然；
退出码 132）。纯区域切换（e64m2 avl16 → e16m1 → vlse16 → vse16）全 PASS
（标记 ABCDE，exit 0）。

- 与既有记录"e64m2 index at avl 32 crashes"同根的可能性未深究（本轮不需要）。
- 编译器自身 selection 从不发射 `vmv.v.i`（mnemonics 表无此形），现状安全；
  **后续任何 lowering 若需在 e64/m2 上做向量搬移，必须避开 vmv.\*（用
  vmerge/vmv1r 等已验证形式）**——已作为可复用约束记录。
- 复现：`as -march=rv64gcv probe-e64m2.S && ld && qemu`（本目录）。

## 探针迭代记录（诚实保留）

1. 首版 probe-strided 用裸字 `0xe200302b` 触发 SIGILL → 改为镜像
   vector_matrix.S 的已知良好 smt.vmadot 形态（Phase-A 校准的一部分）。
2. 首次全量探针 test 5 SIGILL → 逐标记二分：先误判为 avl-32 vsetvli
   （标记在指令**之前**打印，判读修正），再定位到 `vmv.v.i/vmv.v.x @
   e64m2`；test 5 改为纯区域切换后全绿。
3. 两处汇编立即数超界（±2048）与向量访存无立即数偏移，均已修正并保留
   记录（见 TOOLING.md 迭代记录）。
