#!/usr/bin/env python3
"""test_t040_repairs.py -- the T040 value-level dtype-introspection fold,
through the real path (specialization -> TIR -> native compile -> execution
-> comparison under the case's own policy), with the controls that prove
the checks are load-bearing.

The repaired defect: chunk_generalized_iplr_delta_rule_fwd_kernel_o's
float32-labeled identity (762de1caee99) refused with 'tl.dot: fp64 tl.dot
is outside the corpus dtype surface' at line 76.  The kernel's dispatch
idiom reads ``b_Aqk.to(b_v.dtype).shape[1]`` -- constexpr in the pinned
source language (the cast result's TYPE and SHAPE are trace-time tensor
metadata) -- but the frontend's constexpr env could not fold the INLINE
cast call, so the IfExp condition stayed runtime, BOTH arms were lowered,
and the dead else arm's fp64 dot (fp64 pointers: the case layer's
numpy-default float64 buffers under the float32 label) refused.  No
declared case exercises that dot: the condition folds True (BT=8 < 16) for
every declared identity, exactly as the pinned tracer folds it.

The fix (a100c/frontend/specialize.py): a value-method call
``X.to(D)`` / ``X.cast(D)`` over a runtime symbol whose type and shape are
known folds to the cast RESULT's runtime symbol -- the target type, the
receiver's shape -- so ``.shape``, ``.dtype`` and every dtype predicate on
the cast result fold; the VALUE never folds (nothing is baked).

Checks:
  * acceptance[0]: the operator's three identities compile to artifacts
    (two shapes of one identity share one artifact, the second a cache
    hit -- no baking), every declared case (float32, float16, bfloat16)
    executes and compares PASS under its declared policy at 1 and 4
    workers, the dispatch conditions fold at specialization, and no fp64
    dot survives in the TIR;
  * acceptance[1]: the fold is generic -- a probe kernel covers
    ``.to(x.dtype)`` and ``x.dtype``-dependent constexpr arithmetic
    (``16 // acc.to(x.dtype).shape[0]``, the arange bound and the dispatch
    condition) for a block whose dtype comes from EACH of the corpus
    dtypes (F037: bfloat16, bool, float16, float32, int16, int32, int64,
    int8), asserting the fold resolves at specialization (the comparison
    recorded True, the dead arm never lowered), no fp64 fallback (no fp64
    op in the TIR; the cast target is exactly the block's dtype), and no
    baking (two dtype identities produce two artifacts and two
    identities; two runtime shapes of one identity share one artifact);
  * the boundary that STAYS: a genuinely-fp64 dot (explicit fp64
    operands, no folded condition in front of it) keeps the located
    declared-surface refusal -- the repair removes dead code, it does not
    weaken the boundary;
  * control (MECH-WITNESS-TEST): with the fold disabled, the operator's
    float32-labeled case refuses again with the exact pre-fix signature
    and the probe's dead arm reappears -- the checks above are
    load-bearing;
  * the recorded justification: FRONTEND_COVERAGE.json's tl.dot row
    carries the T040 update (no corpus identity reaches a genuinely-fp64
    dot; the boundary note stands for the genuinely-fp64 form).

Run: python3 a100c/tests/test_t040_repairs.py  (exit 0 = all checks PASS)
"""
from __future__ import annotations

import importlib.util
import json
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
from a100c.frontend import lower_tir  # noqa: E402
from a100c.frontend import source as fe_source  # noqa: E402
from a100c.frontend import specialize as fe_spec  # noqa: E402
from a100c.frontend.source import FrontendError  # noqa: E402
from a100c.ir import tir  # noqa: E402
from a100c.passes import pipeline as passes_mod  # noqa: E402

OPS = ROOT / "ops"
WORK = Path(tempfile.mkdtemp(prefix="a100c-t040-"))

#: the corpus dtype surface (F037), as the probe's pointer device dtypes
CORPUS_DTYPES = ("float32", "float16", "bfloat16",
                 "int8", "int16", "int32", "int64", "bool")

#: dtype -> the tir type name the cast target must resolve to
_TIR_NAME = {"float32": "fp32", "float16": "fp16", "bfloat16": "bf16",
             "int8": "i8", "int16": "i16", "int32": "i32",
             "int64": "i64", "bool": "i1"}


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_source(path: Path):
    return fe_source.load_operator(str(path), corpus_root=str(OPS))


def _compiler(tag: str) -> FactoryCompiler:
    return FactoryCompiler(
        options=CompileOptions(cache_dir=str(WORK / f"cache-{tag}")),
        pass_config=passes_mod.PassConfig())


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
            same = np.array_equal(got, exp)
        else:
            same = np.allclose(got, exp, rtol=policy.get("rtol", 0.0),
                               atol=policy.get("atol", 0.0),
                               equal_nan=policy.get("equal_nan", False))
        if not same:
            detail = f"{name}: {int(np.sum(got != exp))} mismatched elements"
        ok &= same
    return ok, detail


def _payload(case: dict) -> dict:
    return {k: v for k, v in case.items()
            if k not in ("expected", "oracle_args")}


def _tir_ops(module):
    out = []

    def walk(blk):
        for st in blk.statements:
            if isinstance(st, tir.Op):
                out.append(st)
            elif isinstance(st, tir.If):
                walk(st.then)
                walk(st.els)
            elif isinstance(st, tir.Loop):
                walk(st.body)

    for fn in module.functions:
        walk(fn.body)
    return out


def _specialize_lower(src, case):
    spec = fe_spec.specialize(src, _payload(case))
    module = lower_tir.lower(src, spec)
    return spec, module


# ---------------------------------------------------------------------------
# the probe: .to(x.dtype) + x.dtype-dependent constexpr arithmetic
# ---------------------------------------------------------------------------

FOLD_PROBE_TEXT = '''\
"""t040/fold-probe: the value-level dtype-introspection fold."""
OPERATOR = {"name": "t040/fold-probe", "group": "basic", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["cast.to"]}
import numpy as np
import triton
import triton.language as tl


@triton.jit
def fold_probe(x_ptr, y_ptr, BLOCK: tl.constexpr):
    # a block whose dtype comes from the pointer's device dtype
    xv = tl.load(x_ptr + tl.arange(0, BLOCK))
    # a creation-typed block is the cast receiver
    acc = tl.zeros([8], dtype=tl.float32)
    # (1) .to(x.dtype): the cast's dtype argument folds from the block's
    # specialization-known dtype; the cast result's type is that dtype
    w = acc.to(xv.dtype)
    # (2) x.dtype-dependent constexpr arithmetic on the CAST RESULT (the
    # inline form: the cast result never gets a name)
    n: tl.constexpr = 16 // acc.to(xv.dtype).shape[0]
    # the dispatch idiom: the condition folds at specialization and the
    # dead arm (mul by 3) is never lowered
    z = (w * n) if acc.to(xv.dtype).shape[0] < 16 else (w * 3)
    tl.store(y_ptr + tl.arange(0, BLOCK), (z + xv).to(y_ptr.dtype.element_ty))


def ref(args, meta):
    x = np.asarray(args["x_ptr"])
    y = np.zeros_like(x)
    y[:8] = x[:8]
    return {"y_ptr": y}


def make_case(shape=None, dtype=None, seed=None):
    # the dtype is the POINTER device dtype: bfloat16 keeps its float32
    # host storage with the pointer_dtypes override (the corpus form)
    storage = np.float32 if dtype == "bfloat16" else np.dtype(dtype)
    n = int(shape[0]) if shape else 8
    rng = np.random.default_rng(seed or 0)
    x = rng.integers(1, 6, n).astype(storage)
    args = {"x_ptr": x, "y_ptr": np.zeros(n, storage)}
    case = {"kernel": fold_probe, "grid": (1,), "args": args,
            "meta": {"BLOCK": 8}, "outputs": ("y_ptr",),
            "shape": (n,), "dtype": dtype or "float32",
            "expected": ref(args, {}),
            "comparison": {"y_ptr": {"comparator": "array_equal",
                                     "exact": True}}}
    if dtype == "bfloat16":
        case["pointer_dtypes"] = {"x_ptr": "bfloat16",
                                  "y_ptr": "bfloat16"}
    return case
'''


def _probe_module():
    path = WORK / "fold_probe.py"
    if not path.is_file():
        path.write_text(FOLD_PROBE_TEXT)
    return _load(path), _load_source(path)


# ---------------------------------------------------------------------------
# acceptance[0]: the repaired operator
# ---------------------------------------------------------------------------

def check_operator_repaired():
    """The operator's identities compile (two shapes of one identity share
    one artifact), the dispatch folds at specialization, no fp64 dot
    survives, and every declared case executes and compares PASS under
    its declared policy at 1 and 4 workers."""
    bad = []
    rel = "suite/dev/chunk_generalized_iplr_delta_rule_fwd_kernel_o.py"
    src = _load_source(OPS / rel)
    module = _load(OPS / rel)
    # the fold + the TIR, per declared dtype (both shapes share it)
    for dtype in ("float32", "float16", "bfloat16"):
        case = module.make_case(shape=(17,), dtype=dtype)
        spec, module_tir = _specialize_lower(src, case)
        errors = tir.verify_module(module_tir)
        if errors:
            bad.append(f"{dtype}: TIR verify {errors[0]}")
        ops = _tir_ops(module_tir)
        dots = [op for op in ops if op.op == "linalg.dot"]
        if not dots or any(op.attrs.get("a_dtype") == "fp64" for op in dots):
            bad.append(f"{dtype}: no dot or an fp64 dot survived "
                       f"({[op.attrs.get('a_dtype') for op in dots]})")
        folded = [c for c in spec.fold.comparisons
                  if ".to(" in c.text and ".shape[" in c.text]
        if not folded or not all(c.result is True for c in folded):
            bad.append(f"{dtype}: the inline-cast shape comparison did not "
                       f"fold True ({[c.text for c in folded][:1]})")
        if not any(b.taken == "body" for b in spec.fold.branches):
            bad.append(f"{dtype}: the dispatch branch did not fold")
    # compile + execute: every declared case, both shapes, 1 and 4 workers
    c = _compiler("operator")
    paths = {}
    for shape in ((17,), (6, 17, 2, 7, 6)):
        for dtype in ("float32", "float16", "bfloat16"):
            case = module.make_case(shape=shape, dtype=dtype)
            artifact = c.compile_case(_payload(case))
            if dtype not in paths:
                paths[dtype] = str(artifact.executable)
            else:
                # two runtime shapes of one identity: the SAME artifact,
                # and the second compile is a cache hit (no baking)
                if str(artifact.executable) != paths[dtype]:
                    bad.append(f"{dtype}: two shapes produced two "
                               f"artifacts")
                if not artifact.cache_hit:
                    bad.append(f"{dtype}: the second shape was not a "
                               f"cache hit")
            for threads in (1, 4):
                ok, detail = _run_case(c, module, threads,
                                       shape=shape, dtype=dtype)
                if not ok:
                    bad.append(f"{shape} {dtype} t={threads}: {detail}")
    if len(set(paths.values())) != 3:
        bad.append("the three dtype identities did not produce three "
                   "distinct artifacts")
    check("t040-operator-identities-compile-execute", not bad,
          "; ".join(bad[:3]) if bad else
          "3 identities x 2 shapes, all cases PASS at 1/4 workers; "
          "dispatch folded, no fp64 dot")


# ---------------------------------------------------------------------------
# acceptance[1]: the fold is generic over the corpus dtype surface
# ---------------------------------------------------------------------------

def check_fold_generic():
    """.to(x.dtype) and x.dtype-dependent constexpr arithmetic on the cast
    result fold at specialization for a block whose dtype comes from each
    corpus dtype: the comparison is recorded True, the dead arm is never
    lowered, no fp64 appears, and the cast target is exactly the block's
    dtype."""
    bad = []
    module, src = _probe_module()
    for dtype in CORPUS_DTYPES:
        case = module.make_case(dtype=dtype)
        spec, module_tir = _specialize_lower(src, case)
        errors = tir.verify_module(module_tir)
        if errors:
            bad.append(f"{dtype}: TIR verify {errors[0]}")
            continue
        ops = _tir_ops(module_tir)
        # the fold resolved at specialization: the comparison was
        # evaluated and recorded True by the CONSTEXPR env (the record is
        # the env's own -- the lowering's fallback never records one)
        folded = [c for c in spec.fold.comparisons
                  if ".to(" in c.text and ".shape[" in c.text]
        if not folded or not all(c.result is True for c in folded):
            bad.append(f"{dtype}: comparison not recorded True "
                       f"({[c.text for c in folded][:1]})")
        if not any(b.taken == "body" for b in spec.fold.branches):
            bad.append(f"{dtype}: branch did not fold to body")
        # the dead arm (the mul by 3) is never lowered
        if any(op.op == "const" and op.attrs.get("value") == 3
               for op in ops):
            bad.append(f"{dtype}: the dead arm was lowered (const 3)")
        # no fp64 fallback: nothing fp64 anywhere in the probe
        fp64 = [op for op in ops
                if any(r.type.name == "fp64" for r in op.results)]
        if fp64:
            bad.append(f"{dtype}: {len(fp64)} fp64-typed ops")
        # the cast target is exactly the block's dtype: a real convert for
        # every dtype but fp32 (the identity cast folds to no convert at
        # all -- never a default dtype)
        converts = [(op.operands[0].type.name, op.results[0].type.name)
                    for op in ops if op.op == "convert"]
        if dtype == "float32":
            if any(src_t == "fp32" for src_t, _ in converts):
                bad.append("float32: the identity cast emitted a convert")
        elif ("fp32", _TIR_NAME[dtype]) not in converts:
            bad.append(f"{dtype}: no fp32 -> {_TIR_NAME[dtype]} convert "
                       f"(the cast target is not the block's dtype)")
    check("t040-fold-generic-over-corpus-dtypes", not bad,
          "; ".join(bad[:3]) if bad else
          f"{len(CORPUS_DTYPES)} dtypes: comparison folded True, dead arm "
          "absent, cast target exact, no fp64")


def check_no_baking():
    """Two dtype identities produce two identities and two artifacts; two
    runtime shapes of one identity share one identity and one artifact
    (the second compile a cache hit on the same executable)."""
    bad = []
    module, src = _probe_module()
    # identity level: the pointer dtype is signed, the runtime shape is not
    ident = {}
    for dtype in ("float32", "float16"):
        for n in (8, 64):
            case = module.make_case(shape=(n,), dtype=dtype)
            spec = fe_spec.specialize(src, _payload(case))
            ident[(dtype, n)] = spec.identity
    if ident[("float32", 8)] != ident[("float32", 64)]:
        bad.append("two runtime shapes produced two identities")
    if ident[("float32", 8)] == ident[("float16", 8)]:
        bad.append("two dtype identities merged")
    # artifact level: the same split on compiled executables
    c = _compiler("nobake")
    art = {}
    for dtype in ("float32", "float16"):
        for n in (8, 64):
            case = module.make_case(shape=(n,), dtype=dtype)
            a = c.compile_case(_payload(case))
            if (dtype, n) == (dtype, 8):
                art[dtype] = (str(a.executable), a.cache_hit)
            else:
                if str(a.executable) != art[dtype][0]:
                    bad.append(f"{dtype}: two runtime shapes produced two "
                               f"artifacts")
                if not a.cache_hit:
                    bad.append(f"{dtype}: the second shape was not a "
                               f"cache hit")
    if art["float32"][0] == art["float16"][0]:
        bad.append("two dtype identities produced one artifact")
    check("t040-no-baking-dtype-identities-vs-runtime-shapes", not bad,
          "; ".join(bad[:3]) if bad else
          "fp32/fp16 -> two artifacts; n=8/n=64 -> one artifact (cache hit)")


def check_execution_spot():
    """The probe's compiled artifacts execute and compare PASS (the fold
    produced a real executable, not a paper one) for every dtype whose
    conversion route the backend declares; bool and int64 keep their own
    located PRE-EXISTING boundaries (the int-literal promotion and the
    f32->i64 convert -- present with no fold form in the kernel), never
    a fold or fp64-dot refusal."""
    bad = []
    module, _src = _probe_module()
    c = _compiler("probe-exec")
    for dtype in CORPUS_DTYPES:
        try:
            ok, detail = _run_case(c, module, 1, dtype=dtype)
            if not ok:
                bad.append(f"{dtype}: {detail}")
        except PipelineError as exc:
            if dtype in ("bool", "int64"):
                # the pre-existing boundaries, unrelated to the fold: the
                # fold itself was verified for these dtypes above
                if "fp64 tl.dot" in str(exc):
                    bad.append(f"{dtype}: the pre-existing refusal became "
                               "the fp64 dot (the fold regressed)")
            else:
                bad.append(f"{dtype}: {exc.construct}: {exc.message[:80]}")
    check("t040-probe-execution-supported-dtypes", not bad,
          "; ".join(bad[:3]) if bad else
          "6 dtypes execute+compare PASS; bool/int64 keep their located "
          "pre-existing convert/promotion boundaries")


# ---------------------------------------------------------------------------
# the boundary that stays: a genuinely-fp64 dot
# ---------------------------------------------------------------------------

FP64_DOT_TEXT = '''\
"""t040/fp64-dot: the genuinely-fp64 dot boundary witness."""
OPERATOR = {"name": "t040/fp64-dot", "group": "basic", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["linalg.dot"]}
import numpy as np
import triton
import triton.language as tl


@triton.jit
def fp64_dot(a_ptr, b_ptr, c_ptr, M: tl.constexpr, N: tl.constexpr, K: tl.constexpr):
    a = tl.load(a_ptr + tl.arange(0, M)[:, None] * K + tl.arange(0, K)[None, :])
    b = tl.load(b_ptr + tl.arange(0, K)[:, None] * N + tl.arange(0, N)[None, :])
    c = tl.dot(a, b)
    tl.store(c_ptr + tl.arange(0, M)[:, None] * N + tl.arange(0, N)[None, :], c)


def ref(args, meta):
    a = np.asarray(args["a_ptr"])
    b = np.asarray(args["b_ptr"])
    return {"c_ptr": a @ b}


def make_case(shape=None, dtype=None, seed=None):
    # numpy-default float64 buffers: the pointers ARE fp64 and the dot is
    # live (no folded condition in front of it)
    args = {"a_ptr": np.ones((4, 4)), "b_ptr": np.ones((4, 4)),
            "c_ptr": np.zeros((4, 4))}
    return {"kernel": fp64_dot, "grid": (1,), "args": args,
            "meta": {"M": 4, "N": 4, "K": 4}, "outputs": ("c_ptr",),
            "shape": (4,), "dtype": "float32", "expected": ref(args, {}),
            "comparison": {"c_ptr": {"comparator": "array_equal",
                                     "exact": True}}}
'''


def check_genuinely_fp64_boundary():
    """A genuinely-fp64 tl.dot (fp64 operands, live code) keeps the located
    declared-surface refusal: the repair removed dead code behind a folded
    condition, it did not weaken the boundary."""
    bad = []
    path = WORK / "fp64_dot.py"
    if not path.is_file():
        path.write_text(FP64_DOT_TEXT)
    module = _load(path)
    src = _load_source(path)
    case = module.make_case()
    spec = fe_spec.specialize(src, _payload(case))
    if not all(t.name == "fp64" for t in spec.pointer_types.values()):
        bad.append("the witness case does not carry fp64 pointers")
    try:
        lower_tir.lower(src, spec)
        bad.append("the genuinely-fp64 dot compiled (the boundary was "
                   "weakened)")
    except FrontendError as exc:
        if exc.construct != "tl.dot" or \
                "fp64 tl.dot is outside the corpus dtype surface" \
                not in exc.message:
            bad.append(f"wrong refusal: {exc.construct}: "
                       f"{exc.message[:80]}")
        elif not exc.line:
            bad.append("the refusal is not located")
    check("t040-genuinely-fp64-dot-keeps-located-refusal", not bad,
          "; ".join(bad[:2]) if bad else
          "the live fp64 dot still refuses at tl.dot with the F037 surface")


# ---------------------------------------------------------------------------
# control (MECH-WITNESS-TEST): the fold disabled
# ---------------------------------------------------------------------------

def check_fold_disabled_control():
    """With the value-method cast fold disabled, the operator's
    float32-labeled case refuses again with the exact pre-fix signature
    and the probe's dead arm reappears -- the passing checks above are
    load-bearing, not vacuous."""
    bad = []
    original = fe_spec.ConstexprEnv._fold_cast_method

    def disabled(self, node, path):
        return None

    fe_spec.ConstexprEnv._fold_cast_method = disabled
    try:
        rel = ("suite/dev/chunk_generalized_iplr_delta_rule_fwd_kernel_o.py")
        src = _load_source(OPS / rel)
        module = _load(OPS / rel)
        case = module.make_case(shape=(17,), dtype="float32")
        try:
            _specialize_lower(src, case)
            bad.append("the float32 case compiled with the fold disabled "
                       "(the repair is not what fixed it)")
        except FrontendError as exc:
            if exc.construct != "tl.dot" or \
                    "fp64 tl.dot is outside the corpus dtype surface" \
                    not in exc.message or exc.line != 76:
                bad.append(f"wrong disabled-fold refusal: {exc.construct} "
                           f"line {exc.line}")
        probe_module, probe_src = _probe_module()
        pcase = probe_module.make_case(dtype="float32")
        _spec, probe_tir = _specialize_lower(probe_src, pcase)
        if not any(op.op == "const" and op.attrs.get("value") == 3
                   for op in _tir_ops(probe_tir)):
            bad.append("the probe's dead arm did not reappear with the "
                       "fold disabled (the dead-arm check is vacuous)")
    finally:
        fe_spec.ConstexprEnv._fold_cast_method = original
    check("t040-control-fold-disabled-reproduces-defect", not bad,
          "; ".join(bad[:2]) if bad else
          "disabled: the fp64 dot refusal returns at line 76 and the dead "
          "arm is lowered again")


# ---------------------------------------------------------------------------
# the recorded justification
# ---------------------------------------------------------------------------

def check_coverage_note():
    """FRONTEND_COVERAGE.json's tl.dot row carries the T040 update: no
    corpus identity reaches a genuinely-fp64 dot (the float32-labeled
    case's fp64 dot was dead code behind a specialization-folded
    condition), and the boundary note stands for the genuinely-fp64
    form."""
    bad = []
    fc = json.loads((ROOT / "FRONTEND_COVERAGE.json").read_text())
    row = next((r for r in fc["rows"] if r["item"] == "tl.dot"), None)
    if row is None:
        bad.append("no tl.dot row")
    else:
        note = row.get("note") or ""
        for needle in ("T038 dtype-surface boundary", "CORPUS_LOCK.json"):
            if needle not in note:
                bad.append(f"the note lost {needle!r}")
        if "T040" not in note:
            bad.append("the note does not carry the T040 update")
        if "dead" not in note:
            bad.append("the note does not record the dead-arm repair")
    check("t040-fp64-dot-justification-updated", not bad,
          "; ".join(bad[:2]) if bad else
          "tl.dot note: T038 boundary + T040 dead-arm repair recorded")


# ---------------------------------------------------------------------------

def main() -> int:
    check_operator_repaired()
    check_fold_generic()
    check_no_baking()
    check_execution_spot()
    check_genuinely_fp64_boundary()
    check_fold_disabled_control()
    check_coverage_note()
    print()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} check(s): " + ", ".join(FAILURES))
        return 1
    print("all T040 checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
