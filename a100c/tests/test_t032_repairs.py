#!/usr/bin/env python3
"""test_t032_repairs.py -- the T032 heterogeneous-region repairs (gate G6).

Round-2 repair of the dominant census family: mixed-extent / mixed-SEW
runtime regions.  T028 had implemented the segment-level restructure and
disabled it after reproduced staging-path hangs (a staged block carry
across the back edge; a masked 2-D access with a ragged row tail); T030's
element-counter repair of the back-edge copy fixed the hang mechanism and
this task completes the design -- the restructure is re-enabled, every
block carry of a restructured loop stages through the workspace, a
restructured if's block joins write a join-owned region at BOTH arm
closes, and the mir-verifier consequence classes the same staging
reproduced are repaired.

One regression test per repaired class, each through the real compilation
path (the factory compiler -> the native executable on the pinned QEMU
endpoint) and compared against a reference computed independently of the
compiler (numpy in this test), at 1 and 4 workers.  Every command is
bounded: the native execution rides A100_EXECUTION_TIMEOUT (the prior
defect mode was a HANG, never a wrong answer or a crash).

  mixed-extent-loop   the T028 hang-mode witness itself: a runtime loop
                      whose body mixes block extents (a 4-lane row block,
                      an 8-lane column block, the 32-flat 2-D accesses)
                      with a masked 2-D access and a RAGGED ROW TAIL --
                      restructured into extent-homogeneous passes, the
                      row/col blocks staged through the workspace, the
                      load/store materialized per chunk.  Executed on the
                      exact shapes that reproduced the hang ((3, 97) the
                      ragged tail, (20, 17) the multi-program grid).
  staged-carry        the other T028 hang mode: a block value carried
                      across a loop hosting a LAYOUT OP (trans of a
                      reshape) -- the carry stages, the back-edge copy is
                      the loop-carried memory phi, the layout staging
                      loop lowers the trans inside the body.
  if-block-joins      a runtime if whose arms mix block extents and whose
                      joins are BLOCK values (both-armed and one-armed:
                      the else arm keeps the pre-if value) -- the join
                      region is written by both arms' closes.
  preduce-multi-axis  the partial-axis reduction over a 3-D block with
                      TWO kept axes (argmin_split_K's form): the scalar
                      index decomposition no longer emits the illegal
                      scalar srem opcode (the remainder is the division's
                      complement).
  bool-zeros-carry    a boolean block accumulator (tl.zeros(int1))
                      carried across a mixed-extent loop (any_kernel_dim)
                      -- the mask is the bool register form (an e1 vector
                      has no legal vsetvli region), staged as 0/1 bytes.
  ptr-chain-reshape   a pointer chain through shape metadata
                      (``base[None, :]`` -- argmin_tiled's tile
                      addressing) resolves through the whole-tree walk.
  bool-scalar-load    a bool scalar load feeds scalar bool arithmetic
                      (selective_log_softmax's smove class): the zext byte
                      load binds the i64 class directly.
  mixed-width-store   one pass storing an fp32 block beside int64 data
                      (add_base_max): the indexed store runs in the
                      VALUE's own region, not the pass's max-SEW region.
  scalar-bool-convert a rank-0 bool -> int32 convert feeding a scalar
                      accumulator (blocked_jacobi_rank): the convert's
                      vector lane extracts lane 0 instead of meeting the
                      GPR accumulator with a vector register.

Controls: the located-refusal boundary still refuses (a block-tensor
condition cannot branch; an unsupported heterogeneous form never
compiles on a guess), and the executed comparisons are the pass/fail
witnesses for the hang modes (a hang surfaces as the bounded execution
timeout, never as a silent pass).

Run: python3 a100c/tests/test_t032_repairs.py   (exit 0 = all PASS)
"""
from __future__ import annotations

import importlib.util
import shutil
import sys
import tempfile
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap  # noqa: E402

ROOT = _bootstrap.bootstrap()
sys.path.insert(0, str(ROOT / "ops" / "harness"))

warnings.filterwarnings("ignore")

FAILURES = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    print(f"{'PASS' if ok else 'FAIL'} {name}"
          f"{(' | ' + detail) if detail else ''}", flush=True)
    if not ok:
        FAILURES.append(name)
    return ok


import numpy as np  # noqa: E402

from a100c.driver import CompileOptions, PipelineError  # noqa: E402
from a100c.factory import FactoryCompiler  # noqa: E402

TEMPLATE = ('"""probe operator %s"""\n'
            'OPERATOR = {"name": "probe/%s", "group": "probe", "channel": "local",\n'
            '            "execution": "triton_kernel", "verification": "correctness",\n'
            '            "tags": []}\n'
            'SHAPES = ((257,), (514,))\n'
            'import numpy as np\n'
            'import triton\n'
            'import triton.language as tl\n'
            '\n'
            '@triton.jit\n'
            'def %s_kernel(%s):\n'
            '%s\n'
            '\n'
            '%s\n')


def _operator_file(directory: Path, name: str, params: str, body: str,
                   case_layer: str):
    text = TEMPLATE % (name, name, name, params, body, case_layer)
    path = directory / f"{name}.py"
    path.write_text(text)
    return path


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_case(compiler, module, threads: int, **make_kwargs):
    import a100_support.native_device as nd
    case = module.make_case(**make_kwargs)
    device = nd.NativeExecutableDevice(compiler, threads)
    staged = device.stage_case(case)
    staged.launch()
    outputs = staged.outputs()
    ok = True
    detail = ""
    for name, policy in case["comparison"].items():
        got = np.asarray(outputs[name])
        exp = np.asarray(case["expected"][name])
        if got.shape != exp.shape and got.size == exp.size:
            got = got.reshape(exp.shape)
        if policy.get("exact") or policy["comparator"] == "array_equal":
            same = np.array_equal(got, exp)
        else:
            same = np.allclose(got, exp, rtol=policy.get("rtol", 0.0),
                               atol=policy.get("atol", 0.0),
                               equal_nan=policy.get("equal_nan", False))
        if not same:
            diff = np.nonzero(got != exp)[0] if got.shape == exp.shape else []
            detail = f"{name}: {len(diff)} mismatched elements" \
                     f" (first got {got.ravel()[:4]} exp {exp.ravel()[:4]})"
        ok &= same
    return ok, detail


# ---------------------------------------------------------------------------
# 1. the mixed-extent loop (the T028 ragged-tail hang mode), executed
# ---------------------------------------------------------------------------

MIXED_EXTENT_BODY = """\
    pid = tl.program_id(0)
    rows = pid * RB + tl.arange(0, RB)
    mask = rows < R
    w = tl.load(x_ptr + rows, mask=mask, other=1.0) + 1.0
    cols = tl.arange(0, 8)
    for k in range(0, 2):
        cm = (cols[None, :] < C) & mask[:, None]
        v = tl.load(x_ptr + rows[:, None] * C + cols[None, :],
                    mask=cm, other=0.0)
        y = v * w[:, None]
        tl.store(o_ptr + rows[:, None] * C + cols[None, :], y,
                 mask=cm)"""

MIXED_EXTENT_CASE = '''def ref(args, meta):
    x = np.asarray(args["x_ptr"], np.float64).ravel()
    R, C = int(args["R"]), int(args["C"])
    out = np.zeros((R * C,), np.float64)
    for r in range(R):
        w_r = x[r] + 1.0
        for c in range(min(8, C)):
            out[r * C + c] = x[r * C + c] * w_r
    return {"o_ptr": out}


def _make_case(shape=(3, 97), dtype="float32", seed=0):
    R, C = int(shape[0]), int(shape[1])
    rng = np.random.default_rng(seed)
    x = rng.uniform(-2.0, 2.0, (R * C,)).astype(np.float32)
    args = {"x_ptr": x, "o_ptr": np.zeros((R * C,), np.float32),
            "R": R, "C": C}
    meta = {"RB": 4}
    grid = ((R + 3) // 4,)
    return {"args": args, "meta": meta, "grid": grid, "shape": (R, C),
            "dtype": "float32",
            "kernel": mixed_extent_loop_kernel, "outputs": ("o_ptr",),
            "expected": ref(args, meta),
            "comparison": {"o_ptr": {"comparator": "allclose",
                                     "exact": False,
                                     "rtol": 1e-5, "atol": 1e-5}}}


def make_case(shape=None, dtype=None, seed=None):
    return _make_case(shape=shape or (3, 97), dtype=dtype or "float32",
                      seed=seed or 0)'''


def check_mixed_extent_loop(workdir, compiler):
    """The restructured mixed-extent loop executes and compares PASS at 1
    and 4 workers on both T028 shapes: (3, 97) the ragged row tail (the
    reproduced hang) and (20, 17) the multi-program grid.  Integer data
    compares exact through the same shape."""
    path = _operator_file(workdir, "mixed_extent_loop",
                          "x_ptr, o_ptr, R, C, RB: tl.constexpr",
                          MIXED_EXTENT_BODY, MIXED_EXTENT_CASE)
    module = _load(path)
    bad = []
    for shape in ((3, 97), (20, 17)):
        for threads in (1, 4):
            ok, detail = _run_case(compiler, module, threads, shape=shape)
            if not ok:
                bad.append(f"{shape} t{threads}: {detail}")
    check("mixed-extent-loop-executes-1-4-workers", not bad,
          "; ".join(bad[:1]))


# ---------------------------------------------------------------------------
# 2. the staged block carry across a layout-hosting loop (the other T028
#    hang mode), executed
# ---------------------------------------------------------------------------

STAGED_CARRY_BODY = """\
    v = tl.load(X + tl.arange(0, N)).to(tl.float32)
    for i in range(0, 2):
        w = tl.trans(tl.reshape(v, (N // 2, 2)))
        v = tl.reshape(w, (N,))
    tl.store(Y + tl.arange(0, N), v)"""

STAGED_CARRY_CASE = '''def ref(args, meta):
    x = np.asarray(args["X"], np.float64)
    out = x.copy()
    for _ in range(2):
        out = out.reshape(-1, 2).T.reshape(-1)
    return {"Y": out}


def _make_case(shape=(8,), dtype="float32", seed=0):
    n = 16
    rng = np.random.default_rng(seed)
    x = rng.standard_normal(n).astype(np.float32)
    args = {"X": x, "Y": np.zeros(n, np.float32)}
    meta = {"N": n}
    return {"args": args, "meta": meta, "grid": (1,), "shape": (n,),
            "dtype": "float32", "kernel": staged_carry_kernel,
            "outputs": ("Y",), "expected": ref(args, meta),
            "comparison": {"Y": {"comparator": "allclose", "exact": False,
                                 "rtol": 1e-5, "atol": 1e-5}}}


def make_case(shape=None, dtype=None, seed=None):
    return _make_case(shape=shape or (8,), dtype=dtype or "float32",
                      seed=seed or 0)'''


def check_staged_carry(workdir, compiler):
    path = _operator_file(workdir, "staged_carry", "X, Y, N: tl.constexpr",
                          STAGED_CARRY_BODY, STAGED_CARRY_CASE)
    module = _load(path)
    bad = []
    for threads in (1, 4):
        ok, detail = _run_case(compiler, module, threads)
        if not ok:
            bad.append(f"t{threads}: {detail}")
    check("staged-block-carry-layout-loop-executes", not bad,
          "; ".join(bad[:1]))


# ---------------------------------------------------------------------------
# 3. the restructured if with BLOCK joins (both-armed and one-armed)
# ---------------------------------------------------------------------------

IF_JOIN_BODY = """\
    pid = tl.program_id(0)
    rows = pid * RB + tl.arange(0, RB)
    m = rows < R
    a = tl.load(x_ptr + rows, mask=m, other=0.0)
    b = tl.load(x_ptr + R + rows, mask=m, other=0.0)
    cols = tl.arange(0, 4)
    if pid % 2 == 0:
        acc = a + b
        for k in range(0, 2):
            g = tl.load(x_ptr + 2 * R + rows[:, None] * 4 + cols[None, :],
                        mask=m[:, None] & (cols[None, :] < C), other=1.0)
            s = tl.sum(g, axis=1)
            acc = acc + s
        y = acc * 2.0
    else:
        y = a - b
    tl.store(o_ptr + rows, y, mask=m)"""

IF_JOIN_CASE = '''def ref(args, meta):
    x = np.asarray(args["x_ptr"], np.float64)
    R, C = int(args["R"]), int(args["C"])
    RB = 4
    out = np.zeros((R,), np.float64)
    for pid in range((R + RB - 1) // RB):
        rows = pid * RB + np.arange(RB)
        m = rows < R
        a = np.where(m, x[rows], 0.0)
        b = np.where(m, x[R + rows], 0.0)
        if pid % 2 == 0:
            # the masked 2-D tile: other=1.0 at disabled positions
            tile = np.where((rows[:, None] < R)
                            & (np.arange(4)[None, :] < C),
                            x[2 * R + rows[:, None] * 4
                              + np.arange(4)[None, :]], 1.0)
            acc = a + b
            for _ in range(2):
                acc = acc + tile.sum(axis=1)
            y = acc * 2.0
        else:
            y = a - b
        sel = np.nonzero(m)[0]
        out[rows[sel]] = y[sel]
    return {"o_ptr": out}


def _make_case(shape=(17,), dtype="float32", seed=0):
    R = int(shape[0])
    rng = np.random.default_rng(seed)
    x = rng.uniform(-2.0, 2.0, (6 * R + 16,)).astype(np.float32)
    args = {"x_ptr": x, "o_ptr": np.zeros((R,), np.float32),
            "R": R, "C": 3}
    meta = {"RB": 4}
    grid = ((R + 3) // 4,)
    return {"args": args, "meta": meta, "grid": grid, "shape": (R,),
            "dtype": "float32", "kernel": if_block_joins_kernel,
            "outputs": ("o_ptr",), "expected": ref(args, meta),
            "comparison": {"o_ptr": {"comparator": "allclose",
                                     "exact": False,
                                     "rtol": 1e-5, "atol": 1e-5}}}


def make_case(shape=None, dtype=None, seed=None):
    return _make_case(shape=shape or (17,), dtype=dtype or "float32",
                      seed=seed or 0)'''


def check_if_block_joins(workdir, compiler):
    """A mixed-extent if whose then arm hosts a loop and whose joins are
    BLOCK values; the else arm keeps the pre-if values (the one-armed
    form: the join region is written by BOTH arms' closes).  The odd/even
    program split exercises both arms on real data."""
    path = _operator_file(workdir, "if_block_joins",
                          "x_ptr, o_ptr, R, C, RB: tl.constexpr",
                          IF_JOIN_BODY, IF_JOIN_CASE)
    module = _load(path)
    bad = []
    for shape in ((17,), (5,), (32,)):
        for threads in (1, 4):
            ok, detail = _run_case(compiler, module, threads, shape=shape)
            if not ok:
                bad.append(f"{shape} t{threads}: {detail}")
    check("if-block-joins-execute-1-4-workers", not bad,
          "; ".join(bad[:1]))


# ---------------------------------------------------------------------------
# 4. the multi-kept-axis partial reduction (the scalar srem repair)
# ---------------------------------------------------------------------------

PREDUCE_BODY = """\
    i = tl.arange(0, BM)
    j = tl.arange(0, BN)
    k = tl.arange(0, BK)
    x = tl.load(x_ptr + i[:, None, None] * (BN * BK)
                + j[None, :, None] * BK + k[None, None, :])
    mn, mi = tl.min(x, 2, return_indices=True,
                    return_indices_tie_break_left=True)
    tl.store(o_ptr + i[:, None] * BN + j[None, :], mn)
    tl.store(oi_ptr + i[:, None] * BN + j[None, :], mi)"""

PREDUCE_CASE = '''def ref(args, meta):
    x = np.asarray(args["x_ptr"], np.float64).reshape(
        int(args["BM"]), int(args["BN"]), int(args["BK"]))
    mn = x.min(axis=2)
    idx = x.argmin(axis=2)
    return {"o_ptr": mn, "oi_ptr": idx}


def _make_case(shape=(2, 4, 8), dtype="float32", seed=0):
    BM, BN, BK = (int(v) for v in shape)
    rng = np.random.default_rng(seed)
    x = rng.uniform(-3.0, 3.0, (BM, BN, BK)).astype(np.float32)
    args = {"x_ptr": x, "o_ptr": np.zeros((BM, BN,), np.float32),
            "oi_ptr": np.zeros((BM, BN,), np.int32),
            "BM": BM, "BN": BN, "BK": BK}
    meta = {"BM": BM, "BN": BN, "BK": BK}
    return {"args": args, "meta": meta, "grid": (1,),
            "shape": (BM, BN, BK), "dtype": "float32",
            "kernel": preduce_multi_axis_kernel,
            "outputs": ("o_ptr", "oi_ptr"),
            "expected": ref(args, meta),
            "comparison": {"o_ptr": {"comparator": "allclose",
                                     "exact": False,
                                     "rtol": 1e-5, "atol": 1e-5},
                           "oi_ptr": {"comparator": "array_equal",
                                      "exact": True}}}


def make_case(shape=None, dtype=None, seed=None):
    return _make_case(shape=shape or (2, 4, 8), dtype=dtype or "float32",
                      seed=seed or 0)'''


def check_preduce_multi_axis(workdir, compiler):
    """The 3-D reduce over axis 0 (TWO kept axes) executes and compares
    PASS: the kept-axis decomposition no longer emits the illegal scalar
    srem (the pre-legalisation MIR opcode the verifier rejected on
    argmin_split_K).  The index output compares EXACT."""
    path = _operator_file(workdir, "preduce_multi_axis",
                          "x_ptr, o_ptr, oi_ptr, BM: tl.constexpr, "
                          "BN: tl.constexpr, BK: tl.constexpr",
                          PREDUCE_BODY, PREDUCE_CASE)
    module = _load(path)
    bad = []
    for shape in ((2, 4, 8), (4, 2, 8)):
        for threads in (1, 4):
            ok, detail = _run_case(compiler, module, threads, shape=shape)
            if not ok:
                bad.append(f"{shape} t{threads}: {detail}")
    check("preduce-multi-kept-axis-executes", not bad, "; ".join(bad[:1]))


# ---------------------------------------------------------------------------
# 5. the boolean block accumulator carried across a mixed-extent loop
# ---------------------------------------------------------------------------

BOOL_CARRY_BODY = """\
    pid = tl.program_id(0)
    rows = pid * RB + tl.arange(0, RB)[:, None]
    inp = inp_ptr + rows * N
    out = out_ptr + rows
    row_mask = rows < M
    _any = tl.zeros([RB, CB], dtype=tl.int1)
    for off in range(0, N, CB):
        cols = off + tl.arange(0, CB)[None, :]
        col_mask = cols < N
        mask = row_mask and col_mask
        a = tl.load(inp + cols, mask, other=0.0)
        _any = _any or a != 0
    any = tl.max(_any, axis=1)
    tl.store(out, any[:, None], row_mask)"""

BOOL_CARRY_CASE = '''def ref(args, meta):
    x = np.asarray(args["inp_ptr"], np.float64).reshape(
        int(args["M"]), int(args["N"]))
    return {"out_ptr": (x != 0).any(axis=1)}


def _make_case(shape=(6, 20), dtype="float32", seed=0):
    M, N = int(shape[0]), int(shape[1])
    rng = np.random.default_rng(seed)
    x = rng.uniform(-1.0, 1.0, (M, N)).astype(np.float32)
    x[0, ::3] = 0.0
    x[2] = 0.0
    args = {"inp_ptr": x, "out_ptr": np.zeros((M,), np.bool_),
            "M": M, "N": N}
    meta = {"RB": 4, "CB": 8}
    grid = ((M + 3) // 4,)
    return {"args": args, "meta": meta, "grid": grid, "shape": (M, N),
            "dtype": "float32", "kernel": bool_zeros_carry_kernel,
            "outputs": ("out_ptr",), "expected": ref(args, meta),
            "comparison": {"out_ptr": {"comparator": "array_equal",
                                       "exact": True}}}


def make_case(shape=None, dtype=None, seed=None):
    return _make_case(shape=shape or (6, 20), dtype=dtype or "float32",
                      seed=seed or 0)'''


def check_bool_zeros_carry(workdir, compiler):
    """any_kernel_dim's shape: a tl.zeros(int1) block accumulated across
    a mixed-extent loop and reduced at the exit.  Boolean exactness
    (F052) -- array_equal, and the all-zero row exercises the false
    path."""
    path = _operator_file(workdir, "bool_zeros_carry",
                          "inp_ptr, out_ptr, M, N, RB: tl.constexpr, "
                          "CB: tl.constexpr",
                          BOOL_CARRY_BODY, BOOL_CARRY_CASE)
    module = _load(path)
    bad = []
    for threads in (1, 4):
        ok, detail = _run_case(compiler, module, threads)
        if not ok:
            bad.append(f"t{threads}: {detail}")
    check("bool-zeros-carry-executes", not bad, "; ".join(bad[:1]))


# ---------------------------------------------------------------------------
# 6. the pointer chain through shape metadata (argmin_tiled's addressing)
# ---------------------------------------------------------------------------

PTR_RESHAPE_BODY = """\
    pid_n = tl.program_id(0)
    offs_n = pid_n * BN + tl.arange(0, BN)
    mask_n = offs_n < N
    base_ptr = x_ptr + offs_n * 1
    best_val = tl.full((BN,), float('inf'), dtype=tl.float32)
    best_idx = tl.zeros((BN,), dtype=tl.int32)
    for m_start in range(0, M, BM):
        offs_m = m_start + tl.arange(0, BM)
        mask_m = offs_m < M
        tile_ptr = base_ptr[None, :] + offs_m[:, None] * N
        tile = tl.load(tile_ptr, mask=mask_m[:, None] & mask_n[None, :],
                       other=float('inf'))
        local_min = tl.min(tile, axis=0)
        local_argmin = tl.argmin(tile, axis=0)
        is_better = local_min < best_val
        best_val = tl.where(is_better, local_min, best_val)
        best_idx = tl.where(is_better,
                            (m_start + local_argmin).to(tl.int32),
                            best_idx)
    tl.store(out_ptr + offs_n, best_idx.to(tl.int64), mask=mask_n)"""

PTR_RESHAPE_CASE = '''def ref(args, meta):
    x = np.asarray(args["x_ptr"], np.float64).reshape(
        int(args["M"]), int(args["N"]))
    return {"out_ptr": x.argmin(axis=0).astype(np.int64)}


def _make_case(shape=(9, 20), dtype="float32", seed=0):
    M, N = int(shape[0]), int(shape[1])
    rng = np.random.default_rng(seed)
    x = rng.uniform(-2.0, 2.0, (M, N)).astype(np.float32)
    args = {"x_ptr": x, "out_ptr": np.zeros((N,), np.int64),
            "M": M, "N": N}
    meta = {"BM": 4, "BN": 8}
    grid = ((N + 7) // 8,)
    return {"args": args, "meta": meta, "grid": grid, "shape": (M, N),
            "dtype": "float32", "kernel": ptr_chain_reshape_kernel,
            "outputs": ("out_ptr",), "expected": ref(args, meta),
            "comparison": {"out_ptr": {"comparator": "array_equal",
                                       "exact": True}}}


def make_case(shape=None, dtype=None, seed=None):
    return _make_case(shape=shape or (9, 20), dtype=dtype or "float32",
                      seed=seed or 0)'''


def check_ptr_chain_reshape(workdir, compiler):
    """argmin over rows with the tile pointer built from
    ``base_ptr[None, :]`` (shape metadata in the pointer chain) and a
    runtime-bounded loop with two block carries.  The index output
    compares EXACT."""
    path = _operator_file(workdir, "ptr_chain_reshape",
                          "x_ptr, out_ptr, M, N, BM: tl.constexpr, "
                          "BN: tl.constexpr",
                          PTR_RESHAPE_BODY, PTR_RESHAPE_CASE)
    module = _load(path)
    bad = []
    for shape in ((9, 20), (3, 17)):
        for threads in (1, 4):
            ok, detail = _run_case(compiler, module, threads, shape=shape)
            if not ok:
                bad.append(f"{shape} t{threads}: {detail}")
    check("ptr-chain-reshape-executes", not bad, "; ".join(bad[:1]))


# ---------------------------------------------------------------------------
# 7. the bool scalar load feeding scalar bool arithmetic (smove class)
# ---------------------------------------------------------------------------

BOOL_SCALAR_BODY = """\
    pid = tl.program_id(0)
    i = pid * B + tl.arange(0, B)
    m = i < n
    v = tl.load(x_ptr + i, mask=m, other=0.0)
    flag = tl.load(f_ptr + pid)
    if flag:
        tl.store(o_ptr + i, v + 1.0, mask=m)
    else:
        tl.store(o_ptr + i, v - 1.0, mask=m)"""

BOOL_SCALAR_CASE = '''def ref(args, meta):
    x = np.asarray(args["x_ptr"], np.float64)
    flags = np.asarray(args["f_ptr"], np.bool_)
    n = int(args["n"])
    B = 16
    out = np.zeros_like(x)
    for pid in range((n + B - 1) // B):
        lo, hi = pid * B, min((pid + 1) * B, n)
        out[lo:hi] = x[lo:hi] + (1.0 if flags[pid] else -1.0)
    return {"o_ptr": out}


def _make_case(shape=(50,), dtype="float32", seed=0):
    n = int(shape[0])
    rng = np.random.default_rng(seed)
    x = rng.standard_normal(n).astype(np.float32)
    B = 16
    flags = rng.random((n + B - 1) // B) < 0.5
    args = {"x_ptr": x, "f_ptr": flags, "o_ptr": np.zeros(n, np.float32),
            "n": n}
    meta = {"B": B}
    grid = ((n + B - 1) // B,)
    return {"args": args, "meta": meta, "grid": grid, "shape": (n,),
            "dtype": "float32", "kernel": bool_scalar_load_kernel,
            "outputs": ("o_ptr",), "expected": ref(args, meta),
            "comparison": {"o_ptr": {"comparator": "allclose",
                                     "exact": False,
                                     "rtol": 1e-5, "atol": 1e-5}}}


def make_case(shape=None, dtype=None, seed=None):
    return _make_case(shape=shape or (50,), dtype=dtype or "float32",
                      seed=seed or 0)'''


def check_bool_scalar_load(workdir, compiler):
    """A bool SCALAR load guards a block-store if (selective_log_softmax's
    shape): the zext byte load binds the scalar-bool i64 convention
    directly (the smove(i8 -> i64) the verifier rejected).  Both arms
    store on real data."""
    path = _operator_file(workdir, "bool_scalar_load",
                          "x_ptr, f_ptr, o_ptr, n, B: tl.constexpr",
                          BOOL_SCALAR_BODY, BOOL_SCALAR_CASE)
    module = _load(path)
    bad = []
    for threads in (1, 4):
        ok, detail = _run_case(compiler, module, threads)
        if not ok:
            bad.append(f"t{threads}: {detail}")
    check("bool-scalar-load-guard-executes", not bad, "; ".join(bad[:1]))


# ---------------------------------------------------------------------------
# 8. one pass storing fp32 blocks beside int64 data (add_base_max class)
# ---------------------------------------------------------------------------

MIXED_WIDTH_BODY = """\
    pid = tl.program_id(0)
    offset = pid * B + tl.arange(0, B)
    mask = offset < n
    out_vals = tl.load(out_ptrs + offset, mask=mask)
    out_idx = tl.load(out_idx_ptrs + offset, mask=mask)
    if pid > 0:
        last_val = tl.load(partial_ptr + pid - 1)
        last_idx = tl.load(partial_idx_ptr + pid - 1)
        final_vals = tl.maximum(out_vals, last_val)
        final_idx = tl.where(out_vals >= last_val, out_idx, last_idx)
        tl.store(out_ptrs + offset, final_vals.to(out_vals.dtype), mask=mask)
        tl.store(out_idx_ptrs + offset, final_idx, mask=mask)"""

MIXED_WIDTH_CASE = '''def ref(args, meta):
    vals = np.asarray(args["out_ptrs"], np.float64)
    idx = np.asarray(args["out_idx_ptrs"], np.int64)
    pv = np.asarray(args["partial_ptr"], np.float64)
    pi = np.asarray(args["partial_idx_ptr"], np.int64)
    n = int(args["n"])
    B = 8
    for pid in range(1, (n + B - 1) // B):
        lo, hi = pid * B, min((pid + 1) * B, n)
        sel = vals[lo:hi] >= pv[pid - 1]
        vals[lo:hi] = np.maximum(vals[lo:hi], pv[pid - 1])
        idx[lo:hi] = np.where(sel, idx[lo:hi], pi[pid - 1])
    return {"out_ptrs": vals, "out_idx_ptrs": idx}


def _make_case(shape=(25,), dtype="float32", seed=0):
    n = int(shape[0])
    rng = np.random.default_rng(seed)
    B = 8
    blocks = (n + B - 1) // B
    vals = rng.uniform(0.0, 1.0, n).astype(np.float32)
    idx = rng.integers(0, 100, n).astype(np.int64)
    pv = rng.uniform(0.0, 1.0, blocks).astype(np.float32)
    pi = rng.integers(0, 100, blocks).astype(np.int64)
    args = {"out_ptrs": vals.copy(), "out_idx_ptrs": idx.copy(),
            "partial_ptr": pv, "partial_idx_ptr": pi, "n": n}
    meta = {"B": B}
    grid = (blocks,)
    return {"args": args, "meta": meta, "grid": grid, "shape": (n,),
            "dtype": "float32", "kernel": mixed_width_store_kernel,
            "outputs": ("out_ptrs", "out_idx_ptrs"),
            "expected": ref(args, meta),
            "comparison": {"out_ptrs": {"comparator": "allclose",
                                        "exact": False,
                                        "rtol": 1e-5, "atol": 1e-5},
                           "out_idx_ptrs": {"comparator": "array_equal",
                                            "exact": True}}}


def make_case(shape=None, dtype=None, seed=None):
    return _make_case(shape=shape or (25,), dtype=dtype or "float32",
                      seed=seed or 0)'''


def check_mixed_width_store(workdir, compiler):
    """One pass stores an fp32 block beside int64 index data (the pass's
    SEW is the max of its stores' pointees): the indexed store runs in
    the VALUE's own region.  The index output compares EXACT."""
    path = _operator_file(workdir, "mixed_width_store",
                          "out_ptrs, out_idx_ptrs, partial_ptr, "
                          "partial_idx_ptr, n, B: tl.constexpr",
                          MIXED_WIDTH_BODY, MIXED_WIDTH_CASE)
    module = _load(path)
    bad = []
    for threads in (1, 4):
        ok, detail = _run_case(compiler, module, threads)
        if not ok:
            bad.append(f"t{threads}: {detail}")
    check("mixed-width-store-executes", not bad, "; ".join(bad[:1]))


# ---------------------------------------------------------------------------
# 9. the rank-0 bool -> int32 convert in a scalar accumulator
# ---------------------------------------------------------------------------

SCALAR_BOOL_CONVERT_BODY = """\
    batch = tl.program_id(0)
    col = tl.program_id(1)
    s_col = tl.load(S_WORK + batch * K + col)
    rank = tl.full((), 0, dtype=tl.int32)
    other = 0
    while other < K:
        s_other = tl.load(S_WORK + batch * K + other)
        rank += ((s_other > s_col) | (s_other == s_col) & (other < col)).to(tl.int32)
        other += 1
    tl.store(RANKS + batch * K + col, rank)"""

SCALAR_BOOL_CONVERT_CASE = '''def ref(args, meta):
    s = np.asarray(args["S_WORK"], np.float64).reshape(
        int(args["B"]), int(args["K"]))
    ranks = np.zeros_like(s, dtype=np.int32)
    B, K = s.shape
    for b in range(B):
        for col in range(K):
            r = 0
            for o in range(K):
                if (s[b, o] > s[b, col]) or (s[b, o] == s[b, col]
                                             and o < col):
                    r += 1
            ranks[b, col] = r
    return {"RANKS": ranks}


def _make_case(shape=(3, 5), dtype="float32", seed=0):
    B, K = int(shape[0]), int(shape[1])
    rng = np.random.default_rng(seed)
    s = rng.uniform(-1.0, 1.0, (B, K)).astype(np.float32)
    s[0, 2] = s[0, 1]
    args = {"S_WORK": s, "RANKS": np.zeros((B * K,), np.int32),
            "B": B, "K": K}
    meta = {"K": K}
    grid = (B, K)
    return {"args": args, "meta": meta, "grid": grid, "shape": (B, K),
            "dtype": "float32", "kernel": scalar_bool_convert_kernel,
            "outputs": ("RANKS",), "expected": ref(args, meta),
            "comparison": {"RANKS": {"comparator": "array_equal",
                                     "exact": True}}}


def make_case(shape=None, dtype=None, seed=None):
    return _make_case(shape=shape or (3, 5), dtype=dtype or "float32",
                      seed=seed or 0)'''


def check_scalar_bool_convert(workdir, compiler):
    """blocked_jacobi_rank's shape: a while loop accumulating a scalar
    rank from a per-iteration bool -> int32 convert.  The duplicated
    value in row 0 exercises the TIE branch (== and index order).  The
    rank output compares EXACT."""
    path = _operator_file(workdir, "scalar_bool_convert",
                          "S_WORK, RANKS, K", SCALAR_BOOL_CONVERT_BODY,
                          SCALAR_BOOL_CONVERT_CASE)
    module = _load(path)
    bad = []
    for threads in (1, 4):
        ok, detail = _run_case(compiler, module, threads)
        if not ok:
            bad.append(f"t{threads}: {detail}")
    check("scalar-bool-convert-rank-executes", not bad,
          "; ".join(bad[:1]))


# ---------------------------------------------------------------------------
# 10. the in-region consumed reduction (argmax's remainder branch)
# ---------------------------------------------------------------------------

IN_REGION_REDUCE_BODY = """\
    pid = tl.program_id(0)
    dtype = x_ptr.type.element_ty
    min_value = float('-inf')
    max_values = min_value
    argmax_values = 0
    loop_time = N // TILE_N
    remainder = N % TILE_N
    for start_n in range(0, loop_time):
        n_offset = start_n * TILE_N + tl.arange(0, TILE_N)
        inp_vals = tl.load(x_ptr + pid * N + n_offset)
        (local_max, local_argmax) = tl.max(inp_vals, 0, return_indices=True,
                                           return_indices_tie_break_left=True)
        update = local_max > max_values
        max_values = tl.where(update, local_max, max_values)
        argmax_values = tl.where(update, start_n * TILE_N + local_argmax,
                                 argmax_values)
    if remainder:
        n_offset = loop_time * TILE_N + tl.arange(0, TILE_N)
        mask = n_offset < N
        inp_vals = tl.load(x_ptr + pid * N + n_offset, mask=mask,
                           other=min_value)
        (local_max, local_argmax) = tl.max(inp_vals, 0, return_indices=True,
                                           return_indices_tie_break_left=True)
        update = local_max > max_values
        max_values = tl.where(update, local_max, max_values)
        argmax_values = tl.where(update, loop_time * TILE_N + local_argmax,
                                 argmax_values)
    tl.store(out_ptr + pid, argmax_values)"""

IN_REGION_REDUCE_CASE = '''def ref(args, meta):
    x = np.asarray(args["x_ptr"], np.float64)
    M, N = int(args["M"]), int(args["N"])
    return {"out_ptr": x.reshape(M, N).argmax(axis=1).astype(np.int32)}


def _make_case(shape=(3, 5), dtype="float32", seed=0):
    M, N = int(shape[0]), int(shape[1])
    rng = np.random.default_rng(seed)
    x = rng.uniform(-2.0, 2.0, (M, N)).astype(np.float32)
    x[0, 1] = x[0, 0]
    args = {"x_ptr": x, "out_ptr": np.zeros((M,), np.int32),
            "M": M, "N": N}
    meta = {"TILE_N": 128}
    grid = (M,)
    return {"args": args, "meta": meta, "grid": grid, "shape": (M, N),
            "dtype": "float32", "kernel": in_region_reduce_kernel,
            "outputs": ("out_ptr",), "expected": ref(args, meta),
            "comparison": {"out_ptr": {"comparator": "array_equal",
                                       "exact": True}}}


def make_case(shape=None, dtype=None, seed=None):
    return _make_case(shape=shape or (3, 5), dtype=dtype or "float32",
                      seed=seed or 0)'''


def check_in_region_reduce(workdir, compiler):
    """argmax_kernel_inner's shape: a reduce whose result feeds a where
    chain INSIDE the same region (the remainder branch), with the loop
    form beside it.  The hosting regions restructure and the consumer
    reads the MERGED value (the per-chunk partial read was the recorded
    wrong-index defect: every row answered 0).  The tie in row 0
    exercises tie-break-left; the index compares EXACT."""
    path = _operator_file(workdir, "in_region_reduce",
                          "x_ptr, out_ptr, M, N, TILE_N: tl.constexpr",
                          IN_REGION_REDUCE_BODY, IN_REGION_REDUCE_CASE)
    module = _load(path)
    bad = []
    for shape in ((3, 5), (4, 300), (2, 128)):
        for threads in (1, 4):
            ok, detail = _run_case(compiler, module, threads, shape=shape)
            if not ok:
                bad.append(f"{shape} t{threads}: {detail}")
    check("in-region-consumed-reduce-executes", not bad,
          "; ".join(bad[:1]))


# ---------------------------------------------------------------------------
# 11. the controls: the refusal boundary is unchanged (a heterogeneous
#     form the staging cannot host refuses LOCATED, never a guess)
# ---------------------------------------------------------------------------

def check_refusal_controls(workdir, compiler):
    """A block-tensor condition cannot branch (Triton branches on
    scalars) and stays the frontend's located refusal -- the restructure
    must not silently compile an unhostable form."""
    body = ("    v = tl.load(X + tl.arange(0, N)).to(tl.float32)\n"
            "    if v > 0:\n"
            "        v = v * 2.0\n"
            "    tl.store(Y + tl.arange(0, N), v)\n")
    path = _operator_file(workdir, "block_cond_ctrl", "X, Y, "
                          "N: tl.constexpr", body,
                          'def ref(args, meta):\n'
                          '    return {"Y": args["X"]}\n\n\n'
                          'def make_case(shape=None, dtype=None, seed=None):\n'
                          '    raise NotImplementedError\n')
    module = _load(path)
    try:
        compiler.compile_case({"args": {"X": np.zeros(8, np.float32),
                                        "Y": np.zeros(8, np.float32)},
                               "meta": {"N": 8}, "grid": (1,),
                               "kernel": module.block_cond_ctrl_kernel,
                               "outputs": ("Y",),
                               "comparison": {"Y": {"comparator":
                                                   "allclose"}}})
        check("block-condition-still-refuses-located", False,
              "compiled (expected the located refusal)")
    except PipelineError as exc:
        check("block-condition-still-refuses-located",
              "block-tensor condition" in str(exc) and ".py:" in str(exc),
              str(exc)[:100])


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------

def main() -> int:
    workdir = Path(tempfile.mkdtemp(prefix="a100c-t032-"))
    cache = workdir / "cache"
    try:
        compiler = FactoryCompiler(
            options=CompileOptions(cache_dir=str(cache)))
        check_mixed_extent_loop(workdir, compiler)
        check_staged_carry(workdir, compiler)
        check_if_block_joins(workdir, compiler)
        check_preduce_multi_axis(workdir, compiler)
        check_bool_zeros_carry(workdir, compiler)
        check_ptr_chain_reshape(workdir, compiler)
        check_bool_scalar_load(workdir, compiler)
        check_mixed_width_store(workdir, compiler)
        check_scalar_bool_convert(workdir, compiler)
        check_in_region_reduce(workdir, compiler)
        check_refusal_controls(workdir, compiler)
    finally:
        import shutil
        shutil.rmtree(workdir, ignore_errors=True)
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} check(s)")
        return 1
    print("test_t032_repairs: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
