#!/usr/bin/env python3
"""test_t044_repairs.py -- the T044 conv3d-family mismatch class, through
the real compilation path (frontend -> TIR -> verify -> passes -> MIR ->
legalize -> native compile -> execution -> comparison under the case's own
policy), with the controls that prove the checks are load-bearing.

The repaired defect (6 MISMATCH cases: fused_conv3d_kernel
[2,4,7,6,5,6,2,2,2] x fp32/fp16/bf16 -- the only N=2 shape, whose second
batch is the only non-zero input; transposed_conv3d
[1,3,5,2,3,4,1,0]/[1,3,10,2,3,4,1,0]/[3,3,5,2,3,4,1,0] x fp16) was two
shared-path defects in the LOWERING (the TIR and the frontend were
verified correct first; both fixes land in a100c/lower/vectorize.py, no
per-operator branch):

1. fused_conv3d -- the loop-carried weight pointer LOST its per-iteration
   advance.  ``curr_w_ptr`` is advanced once per unrolled tap
   (``curr_w_ptr += w_step`` inside the static_range nest: EIGHT
   ``ptradd`` hops in the Cin loop body), so the body-end value's
   immediate predecessor is not the init and ``_classify_carried``'s
   single-hop check missed the recurrence.  The carry fell to the staged
   path, whose back-edge copy refreshes a pointer-valued region the
   flattened address reads never consult (they read the invariant offset
   operand's region), and EVERY iteration re-read the FIRST iteration's
   weights: iteration ic's tap j read wT[off_m + j*Cout] instead of
   wT[off_m + (ic*8 + j)*Cout].  The x-side addresses were verified
   correct by a one-hot probe (each tap reads exactly x[os] with
   os = base + ic*stride_xc + tap); the accumulated error was
   sum_ic x[os + ic*stride_xc] -- the wrong weights only.  The fix:
   ``_classify_carried`` walks the ptradd CHAIN back to the init (every
   hop a loop-invariant uniform step) and the recurrence's per-iteration
   step is the SUM of the hops (``_recurrence_step_reg``).

2. transposed_conv3d -- the fp16 IME dot's A operand read the WIDENED
   staging region as raw 16-bit.  ``x_flat = tl.reshape(x_tile, ...)``
   is flat-identity, and the reshape's lowering aliases the result's
   staged record to the source's -- clobbering the NATIVE 16-bit record
   the staging analysis had given the dot operand (part (a)) with the
   load result's standard 32-bit-widened record.  The IME tile
   pipeline's esz-strided 16-bit row loads then read the zero low halves
   of the widened fp32 lanes (a one-hot dump showed the A tile all zero
   while the B tile -- the direct load operand -- was correct).  fp32
   (no IME) and bf16 (the fp32-widened vector path) were unaffected.
   The fix: ``_propagate_flat_identity_native`` aliases the SOURCE to
   the result's native record before the regions are allocated, so the
   producer stores the raw 16-bit lanes the tile pipeline reads.

Checks (each must hold for exit 0):

  * t044-multihop-recurrence-classified: the real fused_conv3d frontend
    TIR's Cin loop classifies ``curr_w_ptr`` as a recurrence whose step
    is the LIST of the chain's eight Cout hops; the differential control
    (the pre-fix single-hop arm) classifies it "staged" -- the chain walk
    is load-bearing;
  * t044-reshape-native-alias: the real transposed_conv3d lowering's
    staged records alias x_tile to x_flat's NATIVE 16-bit record (same
    offset/lane width); the differential control (the propagation
    disabled) leaves x_tile on the 32-bit widened record;
  * t044-end-to-end-pass: the previously MISMATCH cases execute and
    compare PASS under their own policies -- fused_conv3d [2,4,7,6,5,6,
    2,2,2] fp32 at one thread and bfloat16 at four threads (the ragged
    tail, low precision, multi-worker), transposed_conv3d
    [1,3,5,2,3,4,1,0] fp16 at one thread and [3,3,5,2,3,4,1,0] fp16 at
    four threads.

Run: python3 a100c/tests/test_t044_repairs.py  (exit 0 = all checks PASS)
"""
from __future__ import annotations

import sys
import tempfile
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap  # noqa: E402

ROOT = _bootstrap.bootstrap()
OPS = ROOT / "ops"

warnings.filterwarnings("ignore")

FAILURES = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    print(f"{'PASS' if ok else 'FAIL'} {name}"
          f"{(' | ' + detail) if detail else ''}", flush=True)
    if not ok:
        FAILURES.append(name)
    return ok


import os  # noqa: E402

sys.path.insert(0, str(OPS / "harness"))
sys.path.insert(0, str(ROOT / "tools"))
os.chdir(str(ROOT))

import run_scan as rs  # noqa: E402
from a100c.frontend import lower_tir, source as fe_source, \
    specialize as fe_spec  # noqa: E402
from a100c.plan import grid as grid_mod  # noqa: E402
from a100c.ir import tir  # noqa: E402
from a100c.lower import binding as binding_mod  # noqa: E402
import a100c.lower.vectorize as V  # noqa: E402
from a100c.passes import pipeline as passes_mod  # noqa: E402
from a100c.plan import partition as part_mod  # noqa: E402
from a100c.target import DEFAULT_TARGET  # noqa: E402

FC3D = "suite/dev/fused_conv3d_kernel.py"
TC3D = "suite/dev/transposed_conv3d.py"
WORK = Path(tempfile.mkdtemp(prefix="a100c-t044-"))


# ---------------------------------------------------------------------------
# shared helpers (the real path pieces)
# ---------------------------------------------------------------------------

def _case_of(operator: str, shape, dtype: str):
    rows = list(rs.enumerated_rows(rs.DEFAULT_MANIFEST, None, [operator]))
    row = next(r for r in rows
               if r["shape"] == list(shape) and r["dtype"] == dtype)
    return rs.build_case(row, 30, use_golden=True)


def _frontend_tir(operator: str, shape, dtype: str):
    """The real frontend output (source -> specialize -> TIR -> passes)."""
    case = _case_of(operator, shape, dtype)
    path = ROOT / "ops" / "suite" / operator.split("/", 1)[1]
    src = fe_source.load_operator(str(path))
    spec = fe_spec.specialize(src, case)
    module = lower_tir.lower(src, spec)
    passes_mod.run(module, passes_mod.PassConfig())
    return module, case


def _loops(block):
    for st in block.statements:
        if isinstance(st, tir.Loop):
            yield st
            yield from _loops(st.body)
        elif isinstance(st, tir.If):
            yield from _loops(st.then)
            yield from _loops(st.els)


def _run_case(operator: str, shape, dtype: str, threads: int):
    case = _case_of(operator, shape, dtype)
    from a100c.factory import FactoryCompiler
    from a100c.driver import CompileOptions
    import a100_support.native_device as nd
    compiler = FactoryCompiler(
        options=CompileOptions(cache_dir=str(WORK / "cache")),
        pass_config=passes_mod.PassConfig())
    staged = nd.NativeStagedCase(case, compiler, threads)
    staged.launch()                       # raises on non-zero native exit
    verdict = rs.compare_outputs(case, staged.outputs())
    return verdict.get("status")


# ---------------------------------------------------------------------------
# 1. the multi-hop carried-pointer recurrence is classified
# ---------------------------------------------------------------------------

def check_multihop_recurrence():
    tir_module, case = _frontend_tir(FC3D, (2, 4, 7, 6, 5, 6, 2, 2, 2),
                                     "float32")
    loops = [lp for lp in _loops(tir_module.functions[0].body)
             if any(name == "curr_w_ptr" for name, _ in lp.carried)]
    if len(loops) != 1:
        check("t044-multihop-recurrence-classified", False,
              f"expected one loop carrying curr_w_ptr, got {len(loops)}")
        return
    loop = loops[0]
    captured = {}
    orig = V.SliceLowering._classify_carried

    def capture(self, stmt):
        out = orig(self, stmt)
        captured[id(stmt)] = out
        return out

    src = fe_source.load_operator(
        str(ROOT / "ops/suite/dev/fused_conv3d_kernel.py"))
    V.SliceLowering._classify_carried = capture
    try:
        V.lower_to_mir(tir_module, part_mod.ExecutionPlan(), DEFAULT_TARGET,
                       binding_mod.argument_layout(
                           case, fe_spec.specialize(src, case)),
                       grid_mod.extract_grid(src, case))
    finally:
        V.SliceLowering._classify_carried = orig
    entries = captured.get(id(loop))
    if entries is None:
        check("t044-multihop-recurrence-classified", False,
              "the Cin loop's classification was not captured")
        return
    rec = [e for e in entries
           if e[0] == "recurrence" and e[1] == "curr_w_ptr"]
    ok_shape = len(rec) == 1 and isinstance(rec[0][3], list) \
        and len(rec[0][3]) == 8
    # the differential control: the PRE-FIX single-hop arm (only
    # end.producer.operands[0].vid == init.vid counts) does not match the
    # chain -- that arm classified the carry "staged" and the loop re-read
    # the first iteration's weights forever
    names = {}
    for st in loop.body.statements:
        if isinstance(st, tir.Op):
            for r in st.results:
                for key in r.scope_names():
                    names[key] = r
    init = dict(loop.carried)["curr_w_ptr"]
    end = names.get("curr_w_ptr")
    old_missed = not (end is not None and end.producer is not None
                      and end.producer.op == "ptradd"
                      and end.producer.operands[0].vid == init.vid)
    hops = 0
    node = end
    while node is not None and node.vid != init.vid and \
            node.producer is not None and node.producer.op == "ptradd":
        hops += 1
        node = node.producer.operands[0]
    chain_rooted = node is not None and node.vid == init.vid
    check("t044-multihop-recurrence-classified",
          ok_shape and old_missed and chain_rooted and hops == 8,
          f"recurrence step list of {len(rec[0][3]) if rec else 0} hops; "
          f"pre-fix single-hop arm matches: {not old_missed}; "
          f"chain hops: {hops}, rooted at init: {chain_rooted}")


# ---------------------------------------------------------------------------
# 2. the reshape aliases the source to the native dot-operand record
# ---------------------------------------------------------------------------

def check_reshape_native_alias():
    tir_module, case = _frontend_tir(TC3D, (1, 3, 5, 2, 3, 4, 1, 0),
                                     "float16")
    src = fe_source.load_operator(str(ROOT / "ops/suite/dev/"
                                      "transposed_conv3d.py"))

    def records_for(patch_none: bool):
        snapshot = {}
        orig_analyze = V.SliceLowering._analyze_staging
        orig_prop = V.SliceLowering._propagate_flat_identity_native

        def analyze(self):
            orig_analyze(self)
            snapshot["staged"] = {vid: dict(rec) for vid, rec
                                  in self._staged.items()}

        def noop(self):
            return None

        V.SliceLowering._analyze_staging = analyze
        if patch_none:
            V.SliceLowering._propagate_flat_identity_native = noop
        try:
            V.lower_to_mir(tir_module, part_mod.ExecutionPlan(),
                           DEFAULT_TARGET,
                           binding_mod.argument_layout(
                               case, fe_spec.specialize(src, case)),
                           grid_mod.extract_grid(src, case))
        finally:
            V.SliceLowering._analyze_staging = orig_analyze
            V.SliceLowering._propagate_flat_identity_native = orig_prop
        return snapshot["staged"]

    # name -> vid map over the TIR
    names = {}

    def walk(block):
        for st in block.statements:
            if isinstance(st, tir.Op):
                for r in st.results:
                    for key in r.scope_names():
                        names.setdefault(key, r.vid)
            elif isinstance(st, tir.If):
                walk(st.then)
                walk(st.els)
            elif isinstance(st, tir.Loop):
                walk(st.body)
    walk(tir_module.functions[0].body)
    x_tile, x_flat = names.get("x_tile"), names.get("x_flat")
    if x_tile is None or x_flat is None:
        check("t044-reshape-native-alias", False,
              f"x_tile/x_flat not found ({x_tile}, {x_flat})")
        return
    fixed = records_for(False)
    rec_src, rec_res = fixed.get(x_tile), fixed.get(x_flat)
    ok = (rec_src is not None and rec_res is not None
          and rec_src.get("native") and rec_res.get("native")
          and rec_src.get("offset") == rec_res.get("offset")
          and rec_src.get("lane_sew") == rec_res.get("lane_sew") == 16
          and rec_src.get("esz") == rec_res.get("esz") == 2)
    # the differential control: the propagation disabled leaves x_tile on
    # the standard 32-bit widened record (the pre-fix state)
    ctrl = records_for(True)
    ctrl_src = ctrl.get(x_tile)
    ctrl_ok = (ctrl_src is not None and not ctrl_src.get("native")
               and ctrl_src.get("lane_sew") == 32
               and ctrl_src.get("esz") == 4)
    check("t044-reshape-native-alias", ok and ctrl_ok,
          f"fixed: x_tile native={rec_src and rec_src.get('native')} "
          f"offset={rec_src and rec_src.get('offset')} == "
          f"{rec_res and rec_res.get('offset')}; "
          f"control (propagation off): x_tile lane_sew="
          f"{ctrl_src and ctrl_src.get('lane_sew')}")


# ---------------------------------------------------------------------------
# 3. the previously MISMATCH cases execute and compare PASS
# ---------------------------------------------------------------------------

def check_end_to_end():
    results = []
    results.append(("fc3d fp32 @1",
                    _run_case(FC3D, (2, 4, 7, 6, 5, 6, 2, 2, 2),
                              "float32", 1)))
    results.append(("fc3d bf16 @4",
                    _run_case(FC3D, (2, 4, 7, 6, 5, 6, 2, 2, 2),
                              "bfloat16", 4)))
    results.append(("tc3d [1,3,5] fp16 @1",
                    _run_case(TC3D, (1, 3, 5, 2, 3, 4, 1, 0),
                              "float16", 1)))
    results.append(("tc3d [3,3,5] fp16 @4",
                    _run_case(TC3D, (3, 3, 5, 2, 3, 4, 1, 0),
                              "float16", 4)))
    ok = all(status == "PASS" for _, status in results)
    check("t044-end-to-end-pass", ok,
          "; ".join(f"{name}={status}" for name, status in results))


def main() -> int:
    check_multihop_recurrence()
    check_reshape_native_alias()
    check_end_to_end()
    if FAILURES:
        print(f"FAILED: {FAILURES}")
        return 1
    print("all T044 checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
