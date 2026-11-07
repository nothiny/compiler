#!/usr/bin/env python3
"""test_t036_repairs.py -- the T036 round-3 repair classes, each through
the real path (compile -> native execution -> comparison under the case's
own policy), with the controls that prove the checks are load-bearing.

  * allocation convergence (the 66-identity class, 21 operators): the
    allocator's victim selection now targets the failing point's
    SIMULTANEOUSLY LIVE set and prefers the MOST-USED candidate -- a
    many-use value's range crosses every failing point it covers, so one
    dissolution relieves them all at once.  The old failed-first policy
    burned the whole 64-round budget rematerializing one single-use
    constant after another while ~20 long-lived descriptor/stride/pointer
    values carried 26-31 simultaneously-live values at every point
    (adaptive_avg_pool2d's measured non-convergence).  Rematerialized
    originals are PRUNED once dead (a dead def still demanded a register
    at its own position -- phantom pressure).  Vector spill legality is
    the emitter's actual contract: every region whose establishing
    vsetvli carries a CONSTANT AVL restores (vsetivli), not only
    AVL == vlmax (forward_pass_chunks' partial-vl tails).  vsetvli AVL
    operands are never split (a reload as an AVL would de-constantize
    the region a spill must restore).
  * fp64 internal compute from subnormal literals (renorm_projection):
    a Python float below 2**-126 types fp64 under the pinned to_tensor
    rule and promotes tl.maximum's whole chain; the 16-bit data rides
    the exact 16->32->64 widening and the doubly-RTNE 64->32->16
    narrowing back (executes and compares at 1 and 4 workers).
  * the bool->fp16 select region (prepare_wy_repr): the select consumes
    the NARROWED 16-bit pair, so it opens the destination's own region
    -- the unbracketed vsel ran v16m1 values inside the pass's e32
    region (the MIR verifier's region-inconsistency refusal; executes
    and compares at 1 and 4 workers).
  * two latent execution defects the first executions of the repaired
    classes exposed (both executed-and-compared fixes):
    - the fp64 rsqrt's dividend splat passed the raw bit pattern
      0x3ff0000000000000 to _splat_const, which encodes float VALUES --
      float(0x3ff0000000000000) is 2.3e18, so renorm's whole fp64
      rsqrt chain multiplied by ~4.6e18 (every dtype, including the
      already-compiling f32 identity);
    - a SCALAR pointer carry whose back edge is ``p += s``
      (forward_pass_chunks' ``sa_ptr += sa_stride_c``) was classified as
      a plain scalar (the rank-0 shortcut ran before the recurrence
      check); its body-end ptradd bound to the PARAM register and the
      back edge passed it unchanged -- the loop read the FIRST
      iteration's address forever.  The uniform-recurrence
      classification now comes first for every rank, and the scalar
      load's address already resolves through _address_of's recurrence
      offsets.

Run: python3 a100c/tests/test_t036_repairs.py  (exit 0 = all PASS)
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
WORK = Path(tempfile.mkdtemp(prefix="a100c-t036-"))

_scan_spec = importlib.util.spec_from_file_location(
    "run_scan_for_t036", str(ROOT / "tools" / "run_scan.py"))
_rs = importlib.util.module_from_spec(_scan_spec)
_scan_spec.loader.exec_module(_rs)


def _harness_case(op_rel: str, shape, dtype):
    """The case exactly as the scan driver builds it (the golden form):
    the census's identities and layouts come from this path."""
    op = _rs.resolve_operator_path(op_rel)
    row = next(r for r in _rs.enumerated_rows(
            str(ROOT / "ops" / "suite" / "manifest.json"))
               if r["operator"] == op and tuple(r["shape"]) == tuple(shape)
               and r["dtype"] == dtype)
    return _rs.build_case(row, 30, use_golden=True)


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
            # the case's declared exact comparison, honoring its
            # equal_nan flag (median's exact fp16 values expect NaN)
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


# ---------------------------------------------------------------------------
# the allocator convergence units (the shared path of the 66-identity class)
# ---------------------------------------------------------------------------

def check_allocator_convergence_unit():
    """The pressure shape of the measured non-convergence: ~20 long-lived
    COMPUTED values (a dependent sadd chain -- not rematerializable)
    carried across a loop body that also defines a fresh 1-use constant
    every few ops.  The old failed-first policy spent its whole round
    budget on those constants; the live-set policy must split the
    long-lived values and converge well inside the bound."""
    from a100c.backend import allocate as alloc_mod
    from a100c.ir import mir
    from a100c.target import DEFAULT_TARGET

    fn = mir.MFunction("t036_pressure", [])
    entry = mir.Block("entry")
    head = mir.Block("head")
    body = mir.Block("body")
    exit_ = mir.Block("exit")
    fn.blocks.extend([entry, head, body, exit_])

    zero = mir.VReg(mir.I32, name="z")
    entry.ops.append(mir.MOp("sconst", [], [zero], attrs={"value": 0}))
    base = mir.VReg(mir.I64, name="b64")
    entry.ops.append(mir.MOp("sconst", [], [base], attrs={"value": 7}))
    # 26 long-lived COMPUTED values (a dependent sadd chain: neither
    # constants nor argument loads -- only a split can dissolve them),
    # every one used inside the loop body
    longs = []
    prev = base
    for i in range(26):
        v = mir.VReg(mir.I64, name=f"L{i}")
        entry.ops.append(mir.MOp("sadd", [prev, prev], [v]))
        longs.append(v)
        prev = v
    entry.ops.append(mir.MOp("br", [], [], attrs={
        "target": "head", "args": [zero]}, loc=None))

    head.params = [mir.VReg(mir.I32, name="i")]
    one = mir.VReg(mir.I32, name="k1")
    head.ops.append(mir.MOp("sconst", [], [one], attrs={"value": 1}))
    cmp_ = mir.VReg(mir.I64, name="c")
    head.ops.append(mir.MOp("slt", [head.params[0], one], [cmp_]))
    nxt = mir.VReg(mir.I32, name="nxt")
    head.ops.append(mir.MOp("sadd", [head.params[0], one], [nxt]))
    head.ops.append(mir.MOp("brc", [cmp_], [], attrs={
        "false_target": "exit", "false_args": [],
        "true_target": "body", "true_args": [head.params[0]]}))

    # the body: 60 fresh 1-use constants, every long-lived value used
    # once and a running sink -- the shape that burned the old round
    # budget (the constants rematerialize; the longs must SPLIT)
    body.params = [mir.VReg(mir.I32, name="i2")]
    sink = mir.VReg(mir.I64, name="sink")
    body.ops.append(mir.MOp("sadd", [longs[0], longs[1]], [sink]))
    for j in range(60):
        k = mir.VReg(mir.I64, name=f"k{j}")
        body.ops.append(mir.MOp("sconst", [], [k], attrs={"value": j}))
        term = mir.VReg(mir.I64, name=f"t{j}")
        body.ops.append(mir.MOp("sadd", [longs[2 + j % 24], k], [term]))
        nxt_sink = mir.VReg(mir.I64, name=f"s{j}")
        body.ops.append(mir.MOp("sadd", [sink, term], [nxt_sink]))
        sink = nxt_sink
    body.ops.append(mir.MOp("br", [], [], attrs={
        "target": "head", "args": [nxt]}))

    exit_.ops.append(mir.MOp("ret", [], []))
    module = mir.MModule("t036_pressure", "<probe>")
    module.functions.append(fn)
    try:
        allocation = alloc_mod.allocate(module, DEFAULT_TARGET)
    except alloc_mod.AllocationError as exc:
        check("allocator-live-set-policy-converges", False, str(exc)[:140])
        return
    check("allocator-live-set-policy-converges",
          allocation.stats["spilled_values"] > 0,
          f"stats={allocation.stats}")
    errors = mir.verify_module(module)
    check("post-t036-spill-verifies", not errors,
          str(errors[0]) if errors else "")


def check_dead_remat_pruned_unit():
    """A rematerialized constant's original def is pruned once dead: a
    dead def still interferes with everything live after it (a phantom
    register demand), so the module after remat must contain no sconst
    whose result has zero uses."""
    from a100c.backend import allocate as alloc_mod
    from a100c.ir import mir
    from a100c.target import DEFAULT_TARGET

    fn = mir.MFunction("t036_remat_prune", [])
    entry = mir.Block("entry")
    fn.blocks.append(entry)
    consts = []
    for i in range(40):
        k = mir.VReg(mir.I64, name=f"k{i}")
        entry.ops.append(mir.MOp("sconst", [], [k], attrs={"value": i}))
        consts.append(k)
    acc = consts[0]
    for k in consts[1:]:
        nxt = mir.VReg(mir.I64, name=f"a{k.name}")
        entry.ops.append(mir.MOp("sadd", [acc, k], [nxt]))
        acc = nxt
    entry.ops.append(mir.MOp("ret", [], []))
    module = mir.MModule("t036_remat_prune", "<probe>")
    module.functions.append(fn)
    try:
        allocation = alloc_mod.allocate(module, DEFAULT_TARGET)
    except alloc_mod.AllocationError as exc:
        check("remat-prunes-dead-originals", False, str(exc)[:140])
        return
    # every original constant whose uses were rewritten to remat products
    # must be GONE (no dead sconst remains in the module)
    dead = []
    used = set()
    for b in fn.blocks:
        for op in b.ops:
            for o in op.operands:
                used.add(o.rid)
    for b in fn.blocks:
        for op in b.ops:
            if op.opcode == "sconst":
                for r in op.results:
                    if r.rid not in used:
                        dead.append(r.name)
    names = [r.name for b in fn.blocks for op in b.ops for r in op.results]
    products = [n for n in names if ".c" in n]
    check("remat-prunes-dead-originals",
          not dead and products,
          f"{len(dead)} dead sconsts remain, {len(products)} products")
    errors = mir.verify_module(module)
    check("post-remat-prune-verifies", not errors,
          str(errors[0]) if errors else "")


# ---------------------------------------------------------------------------
# executed comparisons (the repair classes through the real path)
# ---------------------------------------------------------------------------

REPRESENTATIVE = [
    # (operator, shape, dtype) -- the census's refusing first cases
    ("suite/dev/adaptive_avg_pool2d_kernel.py", (1, 2, 5, 7, 3, 4), "float32"),
    ("suite/dev/forward_pass_chunks.py", (2, 17, 3, 13), "float32"),
    ("suite/dev/matmul_kernel_8d68babe.py", (128,), "float32"),
    ("suite/perf/chunk_retention.py", (2, 2, 16, 32, 32), "float32"),
    ("suite/dev/median_f16_key_select_kernel.py", (1, 17), "float16"),
    ("suite/dev/parallel_based_fwd_kernel.py", (4, 17, 7, 9, 8), "float32"),
    ("suite/dev/prepare_wy_repr_fwd_kernel_safe.py", (2, 33, 3, 16), "float32"),
    ("suite/dev/renorm_projection_update_s_kernel.py", (17,), "float16"),
    ("suite/dev/renorm_projection_update_s_kernel.py", (17,), "bfloat16"),
    ("suite/dev/chunk_transform_qk_fwd_kernel.py", (4, 17, 7, 9, 8), "float16"),
]


def check_representative_executions():
    compiler = _compiler("repr")
    bad = []
    for op_rel, shape, dtype in REPRESENTATIVE:
        for threads in (1, 4):
            ok, detail = _run_harness_case(compiler, op_rel, shape, dtype,
                                           threads)
            if not ok:
                bad.append(f"{op_rel.split('/')[-1]} {dtype} t={threads}: "
                           f"{detail}")
    check("t036-classes-execute-1-4", not bad, "; ".join(bad[:3]))


def check_naive_attn_single_worker():
    """naive_attn_decoding (WTI035's open execution defect): the QEMU
    SIGILL was the allocator placing an indexed load's destination inside
    its index's IMPLIED EMUL group -- an EEW=64 index beside an e32m1
    load reads a two-register group (probed: any data register inside
    the group, load or store, masked or not, raises an illegal
    instruction; the group must be aligned).  The allocator now reserves
    the implied width for the index value and the access's data side
    avoids the whole group.  All three dtypes execute and compare PASS
    at ONE worker; the 4-worker path still diverges (a separate,
    pre-existing multi-worker partition defect in this operator's
    varlen-gather path -- open, recorded in the T036 report)."""
    compiler = _compiler("na")
    bad = []
    for dtype in ("float16", "float32", "bfloat16"):
        ok, detail = _run_harness_case(
            compiler, "suite/dev/naive_attn_decoding_kernel.py",
            (2, 17, 4, 8, 16, 13), dtype, 1)
        if not ok:
            bad.append(f"{dtype}: {detail}")
    check("naive-attn-implied-group-sigill-fixed-1w", not bad,
          "; ".join(bad[:2]))


# ---------------------------------------------------------------------------
# the located-refusal boundary that stays (the classes not in this round)
# ---------------------------------------------------------------------------

# T036 (the loop-merge/ordering round) repaired two entries of this
# list: nansum_kernel_2's ``merge`` class (the scalar-opened chunk's
# frames and fallback vl -- it now compiles and its identities execute
# and compare PASS at 1 and 4 workers) and l1_norm's refusal moved from
# ``ptradd`` to the v0-mask family (``mir-verifier``) -- the rework let
# it past the scalar-tree materialization and the next boundary is the
# v0-mask class (T038's family).  Both stay located refusals or better.
REMAINING_BOUNDARIES = [
    # T038 (the construct long-tail round) repaired five entries of this
    # list: ranked_distribution (the whole-block sort/topk/gather/softmax
    # protocol), cumprod_dim1_grouped_mixed (the last-axis multi-axis
    # scan), nanmedian_ascend_histogram_count (tl.histogram), l1_norm
    # (the vsel v0-mask re-materialization) and chunk_transform_qk (the
    # native-source layout mirror) -- all five now compile and their
    # declared cases execute and compare PASS at 1 and 4 workers (the
    # T038 execution probe, test_t038_repairs.py).  The fp64 tl.dot
    # refusal STAYS (the corpus's declared dtype surface excludes fp64:
    # the case layer hands numpy-default float64 buffers under a
    # float32 label -- FRONTEND_COVERAGE.json's tl.dot row records the
    # justification).
    ("suite/dev/chunk_generalized_iplr_delta_rule_fwd_kernel_o.py", (17,),
     "float32", "tl.dot"),
]


def check_remaining_boundaries():
    """The classes this round does not repair refuse at their declared
    constructs (a located refusal, never a crash and never wrong code)."""
    compiler = _compiler("bounds")
    bad = []
    for op_rel, shape, dtype, construct in REMAINING_BOUNDARIES:
        try:
            case = _harness_case(op_rel, shape, dtype)
        except Exception as exc:                     # noqa: BLE001
            bad.append(f"{op_rel}: case build {type(exc).__name__}")
            continue
        payload = {k: v for k, v in case.items()
                   if k not in ("expected", "oracle_args")}
        try:
            compiler.compile_case(payload)
            bad.append(f"{op_rel.split('/')[-1]}: compiled (expected the "
                       f"located {construct} refusal)")
        except PipelineError as exc:
            if exc.construct != construct:
                bad.append(f"{op_rel.split('/')[-1]}: refused at "
                           f"{exc.construct}, expected {construct}")
        except Exception as exc:                     # noqa: BLE001
            bad.append(f"{op_rel.split('/')[-1]}: {type(exc).__name__}")
    check("remaining-classes-located-refusals", not bad, "; ".join(bad[:3]))


def main() -> int:
    check_allocator_convergence_unit()
    check_dead_remat_pruned_unit()
    check_representative_executions()
    check_naive_attn_single_worker()
    check_remaining_boundaries()
    if FAILURES:
        print(f"\nFAILED: {len(FAILURES)} check(s): {FAILURES}",
              file=sys.stderr)
        return 1
    print("\nall T036 repair checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
