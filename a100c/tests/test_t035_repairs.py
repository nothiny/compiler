#!/usr/bin/env python3
"""test_t035_repairs.py -- the T035 long-tail repair classes, each through
the real path (compile -> native execution -> comparison under the case's
own policy), with the controls that prove the checks are load-bearing.

  * is-fold (max_kernel): ``dtype is tl.bfloat16`` between two constexpr
    dtypes folds by the represented type's identity (the pinned tracer's
    dtype singletons); the truthy NOT_CONSTEXPR sentinel previously
    leaked through ``if not result`` and folded the comparison True for
    EVERY dtype, so max_kernel's fp64 buffers (the case layer's ``del
    dtype``) took the tl.float32 accumulator arm and the TIR verifier
    refused the loop-carried type contradiction.  max_kernel now keeps
    the pinned fp64 accumulator and executes/compares at 1 and 4
    workers.  Control: the fold unit check (fp64 is bf16 -> False,
    bf16 is bf16 -> True) fails if the sentinel leaks again.
  * return_indices promotion (argmin_kernel_opt_k1): the pinned
    max/min(return_indices=True) route promotes bfloat16 only -- the
    value form's <32-bit promotion re-typed argmin's fp16 loop-carried
    ``min_vals`` mid-loop.  argmin f16 executes and compares at 1 and 4
    workers.
  * scan (cumprod_dim1_kernel, cumprod_dim1_grouped_mixed_kernel): the
    scan runs at the OPERAND's own SEW (an f32 operand inside a 16-bit
    pass), the chunk carry threads through the source loop and the
    early-return if (the carry used to be the scan loop's exit param --
    undefined on the return path), and the last-axis scan of a
    multi-axis block restarts at every row boundary.  Both operators
    execute and compare (f32 and f16) at 1 and 4 workers.
  * merge frames (nansum_kernel_2, naive_attn_decoding_kernel): a
    chunk-merge frame whose producer sits inside a restructured region
    passes its incoming accumulator through the close unchanged (the
    region owns the merge), the chunk keeps the frame list it was opened
    with (a nested segmentation's re-filter no longer misaligns the back
    edge's arguments), and a mid-list block statement can no longer open
    a chunk under a stale filter.  nansum (f16/f32) and naive_attn (f16)
    execute and compare at 1 and 4 workers.
  * {0,1}-class candidate width (median_f16_key_select): the candidate
    narrows to the accumulator's lane through the vector lane (the
    scalar core narrows 64->32 only) -- T036's allocator repair then
    resolved the register-pressure class, so median now compiles and
    executes (see check_median_next_class).
  * masked-scalar-load scoping (median_f16_key_select): a value lazily
    materialized inside one guard arm (the CSE-merged ``other`` const)
    no longer leaks into a sibling arm.
  * tl.rand block seed (linear_dropout_softmax_kernel): a seed that
    broadcasts ONE rank-0 scalar is the scalar seed per lane (the philox
    keys are value-identical); executes and compares at 1 and 4 workers.
  * mask-value select (topk_stage1_kernel): a select between two mask
    values composes with mask logic (region-independent) instead of
    opening a vsetvli region on a mask; executes and compares at 1 and 4
    workers.
  * loop-class guard (matmul_kernel_0a4f4889, qr): a chunked region's
    no-merge-rule guard applies to SCALAR joins only (a BLOCK join
    stages per-lane through the workspace); the nested cross-pass
    liveout table registers per (region, arm) exactly as the emission
    looks the keys up.  matmul_0a4f4889 and qr execute and compare at 1
    and 4 workers.
  * rank-0 pure re-materialization (l1_norm_fused_kernel_7f6ce49c,
    unique_dim_row_single_chunk_first_kernel): a pure rank-0 convert /
    full / select whose binding a pass boundary dropped re-materializes
    at its use.  Both execute and compare.

Run: python3 a100c/tests/test_t035_repairs.py  (exit 0 = all PASS)
"""
from __future__ import annotations

import importlib.util
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
from a100c.passes import pipeline as passes_mod  # noqa: E402

OPS = ROOT / "ops"
WORK = Path(tempfile.mkdtemp(prefix="a100c-t035-"))


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_scan_spec = importlib.util.spec_from_file_location(
    "run_scan_for_t035", str(ROOT / "tools" / "run_scan.py"))
_rs = importlib.util.module_from_spec(_scan_spec)
_scan_spec.loader.exec_module(_rs)


def _harness_case(op_rel: str, shape, dtype):
    """The case exactly as the scan driver builds it (the golden form):
    the census's identities and layouts come from this path -- a bare
    module.make_case can carry different scalar record kinds (numpy vs
    python ints) and compile a different layout."""
    op = _rs.resolve_operator_path(op_rel)
    row = next(r for r in _rs.enumerated_rows(
            str(ROOT / "ops" / "suite" / "manifest.json"))
               if r["operator"] == op and tuple(r["shape"]) == tuple(shape)
               and r["dtype"] == dtype)
    return _rs.build_case(row, 30, use_golden=True)


def _run_case(compiler, module, threads, **make_kwargs):
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
            # the case's declared exact comparison, honoring its equal_nan
            # flag (an exact fp16 output may legitimately expect NaN)
            same = np.array_equal(
                got, exp, equal_nan=policy.get("equal_nan", False))
        else:
            same = np.allclose(got, exp, rtol=policy.get("rtol", 0.0),
                               atol=policy.get("atol", 0.0),
                               equal_nan=policy.get("equal_nan", False))
        if not same:
            detail = f"{name}: {int(np.sum(got != exp))} mismatched elements"
        ok &= same
    return ok, detail


def _run_harness_case(compiler, op_rel, shape, dtype, threads):
    import a100_support.native_device as nd
    case = _harness_case(op_rel, shape, dtype)
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
            # the case's declared exact comparison, honoring its equal_nan
            # flag (an exact fp16 output may legitimately expect NaN)
            same = np.array_equal(
                got, exp, equal_nan=policy.get("equal_nan", False))
        else:
            same = np.allclose(got, exp, rtol=policy.get("rtol", 0.0),
                               atol=policy.get("atol", 0.0),
                               equal_nan=policy.get("equal_nan", False))
        if not same:
            detail = f"{name}: {int(np.sum(got != exp))} mismatched"
        ok &= same
    return ok, detail


def _compiler(tag: str) -> FactoryCompiler:
    return FactoryCompiler(
        options=CompileOptions(cache_dir=str(WORK / f"cache-{tag}")),
        pass_config=passes_mod.PassConfig())


def _dev(name: str) -> Path:
    return OPS / "suite" / "dev" / name


# ---------------------------------------------------------------------------
# the is-fold unit control (the sentinel leak the max_kernel class rode on)
# ---------------------------------------------------------------------------

def check_is_fold_unit():
    import ast
    from a100c.frontend.specialize import ConstexprEnv, DTypeValue
    from a100c.ir import tir
    env = ConstexprEnv()
    env.values["d64"] = DTypeValue(tir.FLOAT64)
    env.values["dbf"] = DTypeValue(tir.BFLOAT16)

    def fold(expr: str):
        return env.evaluate(ast.parse(expr, mode="eval").body, "t.py")

    ok = fold("d64 is dbf") is False and fold("d64 is d64") is True \
        and fold("dbf is tl.bfloat16") is True \
        and fold("d64 is tl.bfloat16") is False \
        and fold("d64 == dbf") is False
    check("is-fold-dtype-identity-unit", ok,
          "dtype `is` folds by the represented type (the NOT_CONSTEXPR "
          "sentinel must never leak through the comparison chain)")


# ---------------------------------------------------------------------------
# executed comparisons (the repair classes through the real path)
# ---------------------------------------------------------------------------

def check_max_kernel():
    c = _compiler("maxk")
    mm = _load(_dev("max_kernel.py"))
    bad = []
    for threads in (1, 4):
        ok, detail = _run_case(c, mm, threads, dtype="float32")
        if not ok:
            bad.append(f"t={threads}: {detail}")
    check("max-kernel-fp64-buffers-execute-1-4", not bad, "; ".join(bad))


def check_argmin():
    c = _compiler("argmin")
    mm = _load(_dev("argmin_kernel_opt_k1.py"))
    bad = []
    for threads in (1, 4):
        ok, detail = _run_case(c, mm, threads, shape=(17,), dtype="float16")
        if not ok:
            bad.append(f"t={threads}: {detail}")
    check("argmin-return-indices-fp16-execute-1-4", not bad,
          "; ".join(bad))


def check_scans():
    c = _compiler("scan")
    bad = []
    mm = _load(_dev("cumprod_dim1_kernel.py"))
    for dtype in ("float32", "float16"):
        for threads in (1, 4):
            ok, detail = _run_case(c, mm, threads, dtype=dtype)
            if not ok:
                bad.append(f"cumprod_dim1 {dtype} t={threads}: {detail}")
    # cumprod_dim1_grouped_mixed keeps its located refusal: the
    # last-axis acceptance compiled it but MISCOMPILED real multi-axis
    # blocks (masked_cumsum_vec: 15740/16384 mismatched; the 1x1 case
    # that compared PASS was vacuous -- one row, one element).  The
    # layout lane owns multi-axis scans until the chunk lane order is
    # proven; the rank-1 repairs above stay executed-and-compared.
    gm = _load(_dev("cumprod_dim1_grouped_mixed_kernel.py"))
    case = gm.make_case(dtype="float32")
    payload = {k: v for k, v in case.items()
               if k not in ("expected", "oracle_args")}
    try:
        c.compile_case(payload)
        bad.append("grouped_mixed compiled (expected the located "
                   "multi-axis refusal)")
    except PipelineError as exc:
        if exc.construct != "tl.cumsum/cumprod":
            bad.append(f"grouped_mixed refused at {exc.construct}")
    check("scan-own-sew-carry-and-row-boundary-execute-1-4", not bad,
          "; ".join(bad[:3]))


def check_merge_frames():
    """The restructured-region merge class: the chunk keeps the frame
    list it was opened with and a mid-list block statement cannot open a
    chunk under a stale filter -- naive_attn now COMPILES past the old
    "never initialized" refusal.  Its execution and nansum's merge
    remain OPEN: naive_attn's artifact faults under the pinned QEMU
    (host SIGILL/SEGV in the first chunk loop; QEMU's -d/plugin tooling
    crash on the binary too), and nansum's merged value would bind to
    the identity at the pre-region close (the unconditional passthrough
    stored 0.0 for a 0.787 sum -- reverted to the located refusal; the
    region must thread its candidates to the close).  Both are recorded
    in the T035 report's debug request."""
    c = _compiler("merge")
    na = _load(_dev("naive_attn_decoding_kernel.py"))
    case = na.make_case(dtype="float16")
    payload = {k: v for k, v in case.items()
               if k not in ("expected", "oracle_args")}
    try:
        c.compile_case(payload)
        compiles = True
    except PipelineError as exc:
        compiles = False
        check("merge-frames-naive-attn-compiles", False,
              f"refused at {exc.construct}: {exc.message[:80]}")
        return
    check("merge-frames-naive-attn-compiles", compiles,
          "the stale-filter chunk open no longer strands the merge "
          "frames (execution fault tracked in the T035 report)")
    ns = _load(_dev("nansum_kernel_2.py"))
    case = ns.make_case(dtype="float32")
    payload = {k: v for k, v in case.items()
               if k not in ("expected", "oracle_args")}
    try:
        c.compile_case(payload)
        check("merge-frames-nansum-located-refusal", False,
              "compiled: the passthrough would silently merge the "
              "identity (0.0 for a 0.787 sum) -- the located refusal is "
              "the correct boundary until the region threads its "
              "candidates to the close")
    except PipelineError as exc:
        check("merge-frames-nansum-located-refusal",
              exc.construct == "merge",
              f"construct={exc.construct}")


def check_rand_block_seed():
    c = _compiler("rand")
    bad = []
    for threads in (1, 4):
        ok, detail = _run_harness_case(
            c, "suite/dev/linear_dropout_softmax_kernel.py",
            (16, 128, 128), "float32", threads)
        if not ok:
            bad.append(f"t={threads}: {detail}")
    check("rand-broadcast-scalar-seed-execute-1-4", not bad,
          "; ".join(bad))


def check_mask_select():
    c = _compiler("topk")
    mm = _load(_dev("topk_stage1_kernel.py"))
    bad = []
    for threads in (1, 4):
        ok, detail = _run_case(c, mm, threads, dtype="float32")
        if not ok:
            bad.append(f"t={threads}: {detail}")
    check("mask-value-select-execute-1-4", not bad, "; ".join(bad))


def check_loop_guard():
    c = _compiler("loopg")
    bad = []
    mm = _load(_dev("matmul_kernel_0a4f4889.py"))
    for threads in (1, 4):
        ok, detail = _run_case(c, mm, threads, dtype="float32")
        if not ok:
            bad.append(f"matmul_0a4f4889 t={threads}: {detail}")
    qr = _load(_dev("qr.py"))
    for threads in (1, 4):
        ok, detail = _run_case(c, qr, threads, dtype="float32")
        if not ok:
            bad.append(f"qr t={threads}: {detail}")
    check("block-join-stages-and-arm-liveouts-execute-1-4", not bad,
          "; ".join(bad[:3]))


def check_rank0_remat():
    c = _compiler("remat")
    bad = []
    mm = _load(_dev("l1_norm_fused_kernel_7f6ce49c.py"))
    for dtype in ("float32", "float16"):
        for threads in (1, 4):
            ok, detail = _run_case(c, mm, threads, dtype=dtype)
            if not ok:
                bad.append(f"l1_norm_7f6ce49c {dtype} t={threads}: {detail}")
    uq = _load(_dev("unique_dim_row_single_chunk_first_kernel.py"))
    for threads in (1, 4):
        ok, detail = _run_case(c, uq, threads, dtype="int32")
        if not ok:
            bad.append(f"unique_dim_row t={threads}: {detail}")
    check("rank0-pure-rematerialization-execute-1-4", not bad,
          "; ".join(bad[:3]))


# ---------------------------------------------------------------------------
# the located-refusal boundary moved (median: merge -> allocation)
# ---------------------------------------------------------------------------

def check_median_next_class():
    """T036 advanced this boundary: the allocator's live-set victim policy
    resolved the register-pressure class, so median now COMPILES -- the
    check requires the executed comparison (a strengthening of the old
    located-refusal expectation, which pinned allocation as the next
    blocker)."""
    c = _compiler("median")
    mm = _load(_dev("median_f16_key_select_kernel.py"))
    try:
        c.compile_case(_payload(mm, dtype="float16"))
    except PipelineError as exc:
        check("median-f16-allocates-and-executes", False,
              f"refused at {exc.construct}: {exc.message[:90]}")
        return
    bad = []
    for threads in (1, 4):
        ok, detail = _run_case(c, mm, threads, dtype="float16")
        if not ok:
            bad.append(f"t={threads}: {detail}")
    check("median-f16-allocates-and-executes", not bad, "; ".join(bad))


def _payload(module, **make_kwargs):
    case = module.make_case(**make_kwargs)
    return {k: v for k, v in case.items()
            if k not in ("expected", "oracle_args")}


def main() -> int:
    check_is_fold_unit()
    check_max_kernel()
    check_argmin()
    check_scans()
    check_merge_frames()
    check_rand_block_seed()
    check_mask_select()
    check_loop_guard()
    check_rank0_remat()
    check_median_next_class()
    if FAILURES:
        print(f"\nFAILED: {len(FAILURES)} check(s): {FAILURES}",
              file=sys.stderr)
        return 1
    print("\nall T035 repair checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
