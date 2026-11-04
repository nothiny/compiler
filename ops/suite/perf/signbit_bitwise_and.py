"""signbit_bitwise_and: TritonBench 算子( 类)。
模式: memory.load.masked、memory.store.masked、creation.arange、args.runtime_scalar。

文件只有两层:
  ① 编译单元   编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层    SHAPES / DTYPES / ref / make_case,只用 numpy,不 import torch。
     make_case 接受任意合法 shape(bench 以稳态 shape 调用)。"""
from __future__ import annotations

OPERATOR = {'name': 'bench/signbit_bitwise_and', 'group': 'bench', 'channel': 'local', 'execution': 'triton_kernel', 'verification': 'correctness', 'tags': ['memory.load.masked', 'memory.store.masked', 'creation.arange', 'args.runtime_scalar']}
BENCH_SOURCE = {'pool': 'tritonbench', 'path': 'tritonbench/signbit_bitwise_and.py', 'sha256': '9603f24c3bc952c5cb6a47d4e04b94a7a07d21c8895ecd87e9ce654ab496ef67'}

import numpy as np
import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def signbit_bitwise_and_kernel(a_ptr, b_ptr, y0_ptr, y1_ptr, n_elements,
                               BLOCK: tl.constexpr):
    pid = tl.program_id(0)
    offs = pid * BLOCK + tl.arange(0, BLOCK)
    mask = offs < n_elements
    a = tl.load(a_ptr + offs, mask=mask, other=0)
    b = tl.load(b_ptr + offs, mask=mask, other=0)
    tl.store(y0_ptr + offs, a < 0, mask=mask)
    tl.store(y1_ptr + offs, a & b, mask=mask)


# ------------------------------------------------------------------ ② case 层

DTYPES = ("int32",)

SHAPES = ((128,), (99,))

def ref(args, meta):
    del meta
    a = np.asarray(args["a_ptr"])
    b = np.asarray(args["b_ptr"])
    return {"y0_ptr": np.signbit(a).astype(np.bool_),
            "y1_ptr": (a.astype(np.int8) & b.astype(np.int8)).astype(np.int32)}

def make_case(shape=None, *, dtype="int32", seed=20261008):
    if dtype is None:
        dtype = "int32"
    if np.dtype(dtype).name not in DTYPES:
        raise ValueError(f"unsupported dtype {dtype!r}; choose from {DTYPES}")
    from case_utils import fast_rng
    rng = fast_rng(seed)
    actual = SHAPES[0] if shape is None else shape
    n = int(np.prod(actual, dtype=np.int64))
    a = rng.integers(-128, 128, n, dtype=np.int64).astype(np.int8)
    b = rng.integers(-128, 128, n, dtype=np.int64).astype(np.int8)
    args = {'a_ptr': a.astype(np.int32), 'b_ptr': b.astype(np.int32), 'y0_ptr': np.zeros(n, dtype=np.bool_), 'y1_ptr': np.zeros(n, dtype=np.int32), 'n_elements': n}
    expected = ref(args, {})
    tolerance = {"comparator": "allclose", "exact": False, "rtol": 2e-3, "atol": 2e-3,
                   "equal_nan": True}
    comparison = {name: ({"comparator": "array_equal", "exact": True}
                    if np.asarray(value).dtype == np.bool_ else dict(tolerance))
                  for name, value in expected.items()}
    return {
        "args": args,
        "meta": {"BLOCK": 1024},
        "grid": ((n + 1023) // 1024,),
        "outputs": tuple(expected),
        "expected": expected,
        "comparison": comparison,
        "shape": actual,
        "dtype": "int32",
        "kernel": signbit_bitwise_and_kernel,
    }
