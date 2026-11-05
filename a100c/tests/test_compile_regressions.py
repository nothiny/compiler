#!/usr/bin/env python3
"""test_compile_regressions.py -- the T024 crash/load class repairs.

One regression test per repaired census class, each through the real path
that crashed (never a mock), with the control that proves the check is
load-bearing (MECH-WITNESS-TEST):

  licm-name-shadow      LICM hoisted a loop-invariant op whose RESULT NAME
                        the loop body rebinds (implicit_conv2d's reshape
                        ``rs`` vs the source variable ``rs`` riding the
                        srem's alias): the hoist moved the definition
                        above the body's binding and the remaining in-body
                        uses resolved against the shadow -- the TIR
                        verifier's use-before-definition.  The fix declines
                        such hoists; the control (the legality check
                        disabled) must reproduce the verifier rejection.
                        The verifier stays the control, never weakened.
  mask-complement       ``~mask`` (logical.not / bit.invert on an i1
                        block) crashed reading .sew off a MaskType; the
                        mask-typed path now lowers the complement
                        (vmnand.mm m, m -- the pinned binutils has no
                        vmnot pseudo, probed) and the fp32 amp operator
                        builds a real RISC-V ELF.
  float-inf-identity    the fp64 max-index identity (-inf) crashed in
                        int() during the identity splat; float identities
                        now travel as packed IEEE bits.
  autotune-unwrap       @triton.autotune operators (an Autotuner wrapping
                        a JITFunction wrapping the raw function) never
                        loaded their compile unit: _load_source unwraps
                        recursively, the config is the specialization's
                        deterministic first-declared pick.
  grid-multi-index      the case-layer interpreter crashed int() over a
                        tuple on multi-dimensional element stores
                        (x[1, -1]); such accesses degrade to untracked.
  is-not-none           ``x is [not] None`` folds on the argument's
                        presence (the pinned semantics) instead of typing
                        the None literal; a runtime identity comparison
                        refuses located naming the construct.

Run: python3 a100c/tests/test_compile_regressions.py  (exit 0 = all PASS)
"""
from __future__ import annotations

import ast
import importlib.util
import re
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


from a100c.driver import Compiler, CompileOptions, PipelineError  # noqa: E402
from a100c.factory import FactoryCompiler  # noqa: E402
from a100c.frontend import lower_tir  # noqa: E402
from a100c.frontend import source as fe_source  # noqa: E402
from a100c.frontend import specialize as fe_spec  # noqa: E402
from a100c.frontend.source import OperatorSource  # noqa: E402
from a100c.ir import tir  # noqa: E402
from a100c.passes import licm as licm_mod  # noqa: E402
from a100c.passes import pipeline as passes_mod  # noqa: E402
from a100c.passes.analyses import AnalysisSuite  # noqa: E402
from a100c.plan import grid as grid_mod  # noqa: E402

WORK = Path(tempfile.mkdtemp(prefix="a100c-t024-"))
CACHE = WORK / "cache"


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _case(operator: str, shape=None, dtype=None):
    """The first payload of one operator through the corpus's own harness
    (exactly the way tools/run_scan.py builds it)."""
    module = _load(OPS / operator)
    case = module.make_case(shape=shape, dtype=dtype)
    if case.get("expected") is None:
        case["expected"] = module.ref(case["args"], case["meta"])
    return {k: v for k, v in case.items()
            if k not in ("expected", "oracle_args")}


def _compiler() -> FactoryCompiler:
    return FactoryCompiler(options=CompileOptions(cache_dir=str(CACHE)),
                           pass_config=passes_mod.PassConfig())


def is_riscv64_elf(path: Path) -> bool:
    head = path.read_bytes()[:20]
    return head[:6] == b"\x7fELF\x02\x01" and head[18:20] == b"\xf3\x00"


LOC = tir.SrcLoc("handbuilt.py", 1, 1)


# ---------------------------------------------------------------------------
# class 1: the LICM name-shadow hoist (acceptance[1])
# ---------------------------------------------------------------------------

def _shadow_module():
    """The original illegal-hoist shape, hand-built and VALID before the
    pass: inside the loop body an earlier op (``shadow``, per-iteration
    through the induction) binds the name ``rs`` by alias; the invariant
    ``hoistable`` (its operand ``base`` is defined outside) is named
    ``rs`` itself and its result is used later in the body (``use``).
    Hoisting ``hoistable`` to the preheader leaves ``use`` resolving
    ``rs`` against ``shadow`` -- use-before-definition."""
    mod = tir.Module("shadow", "handbuilt.py")
    fn = tir.Function("k", [tir.Value(tir.Type.pointer(tir.FLOAT32), (),
                                     LOC, name="p")], LOC)
    mod.functions.append(fn)
    base = tir.Op.const(7, tir.INT32, LOC)
    hoistable = tir.Op.binop("arith.add", base.result(), base.result(), LOC)
    hoistable.results[0].name = "rs"
    zero = tir.Op.const(0, tir.INT32, LOC)
    one = tir.Op.const(1, tir.INT32, LOC)
    upper = tir.Op.const(9, tir.INT32, LOC)
    z = tir.Op.zeros((), tir.FLOAT32, LOC)
    for st in (base, zero, one, upper, z):
        fn.body.statements.append(st)
    loop = tir.Loop(zero.result(), upper.result(), one.result(), LOC)
    loop.carried = (("k0", zero.result()), ("acc", z.result()))
    body = loop.body
    # the shadow: per-iteration (its operand is the carried induction
    # init), and it binds "rs" by alias -- exactly the corpus shape (the
    # srem of ``rs = k_idx % khw`` aliasing the source name)
    shadow = tir.Op.binop("arith.add", zero.result(), zero.result(), LOC)
    shadow.results[0].add_alias("rs")
    body.statements.append(shadow)
    # the invariant candidate: its own result NAME is "rs" (the reshape
    # of the corpus shape), its operand is defined outside the loop
    body.statements.append(hoistable)
    # a use later in the body (resolves "rs" -> hoistable before any
    # hoist; against shadow once hoistable leaves the body)
    use = tir.Op.binop("arith.add", shadow.result(), hoistable.result(),
                       LOC)
    body.statements.append(use)
    # the carried steps (both declined by the carried-init rule)
    k0next = tir.Op.binop("arith.add", zero.result(), one.result(), LOC)
    k0next.results[0].add_alias("k0")
    body.statements.append(k0next)
    fzero = tir.Op.const(0.0, tir.FLOAT32, LOC)
    body.statements.append(fzero)
    accnext = tir.Op.binop("arith.add", z.result(), fzero.result(), LOC)
    accnext.results[0].add_alias("acc")
    body.statements.append(accnext)
    fn.body.statements.append(loop)
    return mod, hoistable


def _run_licm(module):
    suite = AnalysisSuite(module)
    trace = passes_mod.TraceCounters("licm", True)
    ctx = passes_mod.PassContext(suite, trace)
    ctx.refresh()
    changed = passes_mod.PASS_REGISTRY["licm"]().run(module, ctx)
    return changed, trace


def _in_loop_body(module, op) -> bool:
    """Is op's statement still inside the (first) loop's body?"""
    for fn in module.functions:
        for st in fn.body.statements:
            if isinstance(st, tir.Loop):
                return any(s is op for s in st.body.statements)
    return False


def test_licm_name_shadow():
    # (a) the shape itself is valid TIR before the pass
    mod, hoistable = _shadow_module()
    errors = tir.verify_module(mod)
    check("licm-name-shadow-module-valid", not errors,
          "; ".join(f"{e.invariant}: {e.message}" for e in errors[:2]))

    # (b) LICM declines the hoist: the op stays inside the loop body and
    # the post-pass verifier is green (either not hoisted or hoisted with
    # its definition -- here the shadow is per-iteration, so NOT hoisted)
    changed, trace = _run_licm(mod)
    errors = tir.verify_module(mod)
    stayed = _in_loop_body(mod, hoistable)
    declined = any("re-bound" in r for r in trace.reasons)
    check("licm-name-shadow-declined-and-green",
          stayed and not errors,
          f"hoistable in body={stayed}, verifier errors={len(errors)}, "
          f"decline recorded={declined}, pass changed={changed}")

    # (c) the control (MECH-WITNESS-TEST): with the legality check
    # disabled, the same module MUST break the verifier -- the original
    # census crash, reproduced
    mod2, hoistable2 = _shadow_module()
    real = licm_mod._result_name_rebound
    licm_mod._result_name_rebound = lambda op, owners: False
    try:
        _run_licm(mod2)
        errors2 = tir.verify_module(mod2)
        hoisted = not _in_loop_body(mod2, hoistable2)
    finally:
        licm_mod._result_name_rebound = real
    broke = any(e.invariant == tir.Invariant.USE_BEFORE_DEFINITION
                for e in errors2)
    check("licm-name-shadow-control-reproduces",
          hoisted and broke,
          f"check disabled: hoisted={hoisted}, "
          f"use-before-def={broke} ({errors2[0].message if errors2 else ''})")

    # (d) the corpus control (acceptance[1]): implicit_conv2d's own TIR
    # through the FULL enabled pipeline keeps the post-pass verifier green
    # (the original ValueError came from the pipeline's own post-pass
    # verification), and licm really fired on this module
    case = _case("suite/dev/implicit_conv2d.py")
    src = fe_source.load_operator(case["kernel"].fn.__code__.co_filename)
    spec = fe_spec.specialize(src, case)
    tir_module = lower_tir.lower(src, spec)
    report = passes_mod.run(tir_module, passes_mod.PassConfig())
    errors3 = tir.verify_module(tir_module)
    fired = report.passes["licm"]["fired"]
    check("licm-implicit-conv2d-post-pass-green",
          not errors3 and fired > 0,
          f"verifier errors={len(errors3)}, licm fired={fired}")


# ---------------------------------------------------------------------------
# class 2: the mask complement (the MaskType .sew crash)
# ---------------------------------------------------------------------------

def test_mask_complement():
    case = _case("suite/dev/amp_foreach_non_finite_check_and_unscale_kernel.py",
                 dtype="float32")
    compiler = _compiler()
    try:
        artifact = compiler.compile_case(case)
    except PipelineError as exc:
        check("mask-complement-amp-fp32", False,
              f"the fp32 amp operator still refuses: {exc.construct}: "
              f"{exc.message[:120]}")
        return
    except Exception as exc:                              # noqa: BLE001
        check("mask-complement-amp-fp32", False,
              f"the fp32 amp operator still crashes: "
              f"{type(exc).__name__}: {str(exc)[:120]}")
        return
    program = artifact.executable.parent / "program.S"
    text = program.read_text()
    vmnand = [l for l in text.splitlines() if "vmnand.mm" in l]
    # the complement carries the ~'s own source line (line 20)
    attributed = any(":20:" in l for l in vmnand)
    check("mask-complement-amp-fp32",
          is_riscv64_elf(artifact.executable) and bool(vmnand) and attributed,
          f"ELF={is_riscv64_elf(artifact.executable)}, "
          f"vmnand lines={len(vmnand)}, source-attributed={attributed}"
          + (f" first: {vmnand[0].strip()[:90]}" if vmnand else ""))


# ---------------------------------------------------------------------------
# class 3: the float('-inf') identity splat (the OverflowError)
# ---------------------------------------------------------------------------

def test_float_inf_identity():
    # the packing itself: every float width encodes -inf as IEEE bits
    # (what the identity splat materializes -- int(-inf) raised)
    import struct
    bits = {
        16: struct.unpack("<H", struct.pack("<e", float("-inf")))[0],
        32: struct.unpack("<I", struct.pack("<f", float("-inf")))[0],
        64: struct.unpack("<Q", struct.pack("<d", float("-inf")))[0],
    }
    check("float-inf-bit-packing",
          bits[16] == 0xFC00 and bits[32] == 0xFF800000
          and bits[64] == 0xFFF0000000000000,
          f"fp16={bits[16]:#06x} fp32={bits[32]:#010x} "
          f"fp64={bits[64]:#018x}")

    case = _case("suite/dev/hidden__argmax_kernel_2.py")
    compiler = _compiler()
    try:
        artifact = compiler.compile_case(case)
        check("float-inf-identity-argmax2",
              is_riscv64_elf(artifact.executable),
              f"artifact {artifact.executable}")
    except PipelineError as exc:
        # located by the sweep's own rule: the location or the rendered
        # message carries path:line:col
        located = bool(re.search(
            r"[\w./+-]+\.py:\d+:\d+",
            f"{exc.loc or ''} {exc.message}"))
        check("float-inf-identity-argmax2", located,
              f"a located refusal of a different construct "
              f"({exc.construct}: {exc.message[:90]}) -- never the "
              "OverflowError")
    except Exception as exc:                              # noqa: BLE001
        check("float-inf-identity-argmax2", False,
              f"still crashes: {type(exc).__name__}: {str(exc)[:140]}")


# ---------------------------------------------------------------------------
# class 4: the @triton.autotune unwrap (acceptance[2])
# ---------------------------------------------------------------------------

AUTOTUNE_OPERATORS = (
    "suite/dev/fused_layernorm_triton.py",
    "suite/dev/max_reduction.py",
    "suite/dev/quant_transpose_kernel.py",
    "suite/dev/reversed_cumsum.py",
    "suite/dev/rowwise_quantization_triton.py",
    "suite/perf/dequantize_matmul.py",
    "suite/perf/matmul_triton2.py",
    "suite/perf/matmul_triton_autotune.py",
    "suite/perf/matrix_vector_multip.py",
    "suite/perf/swiglu_fwd.py",
    "suite/perf/triton_linear_activation.py",
)


def test_autotune_unwrap():
    ok = True
    loaded = 0
    progressed = 0
    for operator in AUTOTUNE_OPERATORS:
        case = _case(operator)
        kernel = case.get("kernel")
        # the wrapper chain is really the autotuner's (the class the
        # corpus hands the compiler: Autotuner -> JITFunction -> function)
        raw = getattr(getattr(kernel, "fn", None), "fn", None)
        chain = raw is not None and getattr(raw, "__code__", None) is not None
        compiler = _compiler()
        try:
            src = compiler._load_source(case)
        except PipelineError as exc:
            ok &= False
            print(f"    {operator}: still refuses the load: "
                  f"{exc.construct}: {exc.message[:90]}")
            continue
        loaded += 1
        right_file = Path(src.path).resolve() == (OPS / operator).resolve()
        deterministic = (src.is_autotune
                         and fe_spec.chosen_autotune_config(src)
                         is src.autotune_configs[0])
        ok &= chain and right_file and deterministic and \
            isinstance(src, OperatorSource)
        # the compile unit loads and the identity progresses: artifact or
        # a located refusal of a DIFFERENT construct (never 'case')
        try:
            compiler.compile_case(case)
            progressed += 1
        except PipelineError as exc:
            if exc.construct == "case":
                ok = False
                print(f"    {operator}: still the unlocated 'case' refusal")
            else:
                progressed += 1
        except Exception as exc:                          # noqa: BLE001
            ok = False
            print(f"    {operator}: crashes: {type(exc).__name__}: "
                  f"{str(exc)[:90]}")
    check("autotune-unwrap-loads-11-units",
          ok and loaded == len(AUTOTUNE_OPERATORS),
          f"{loaded}/{len(AUTOTUNE_OPERATORS)} compile units loaded "
          f"(kernel.fn.fn reached, config = first declared, "
          f"deterministic)")
    check("autotune-unwrap-progresses-11-units",
          progressed == len(AUTOTUNE_OPERATORS),
          f"{progressed}/{len(AUTOTUNE_OPERATORS)} identities progressed "
          "past the load (artifact or a located refusal of another "
          "construct)")


# ---------------------------------------------------------------------------
# class 5: the case-layer interpreter's multi-index subscript
# ---------------------------------------------------------------------------

def test_grid_multi_index():
    ok = True
    for operator in ("suite/dev/median_int_lastdim_select_kernel.py",
                     "suite/dev/nanmedian_select_kernel.py"):
        case = _case(operator)
        src = fe_source.load_operator(case["kernel"].fn.__code__.co_filename)
        try:
            grid = grid_mod.extract_grid(src, case)
            described = grid.describe()
            ok &= isinstance(described, dict)
            print(f"    {operator}: grid extracted "
                  f"({described.get('ndim', '?')}-d)")
        except Exception as exc:                          # noqa: BLE001
            # the interpreter must never raise the int(tuple) TypeError;
            # a located GridError refusal is a legal outcome
            crashed = "int() argument" in str(exc) and "tuple" in str(exc)
            ok &= not crashed
            print(f"    {operator}: {type(exc).__name__}: "
                  f"{str(exc)[:90]}")
    check("grid-multi-index-interprets", ok,
          "x[1, -1]-style multi-index stores no longer crash the "
          "provenance interpreter (int() over a tuple)")

    # and the compile path: both operators' identities are artifacts or
    # located refusals of a different construct (never the _make_case
    # interpreter failure)
    progressed = 0
    total = 0
    for operator in ("suite/dev/median_int_lastdim_select_kernel.py",
                     "suite/dev/nanmedian_select_kernel.py"):
        module = _load(OPS / operator)
        made = module.make_case()
        if made.get("expected") is None:
            made["expected"] = module.ref(made["args"], made["meta"])
        payload = {k: v for k, v in made.items()
                   if k not in ("expected", "oracle_args")}
        total += 1
        compiler = _compiler()
        try:
            compiler.compile_case(payload)
            progressed += 1
        except PipelineError as exc:
            if exc.construct == "_make_case":
                print(f"    {operator}: still the interpreter refusal: "
                      f"{exc.message[:90]}")
            else:
                progressed += 1
        except Exception as exc:                          # noqa: BLE001
            print(f"    {operator}: crashes: {type(exc).__name__}: "
                  f"{str(exc)[:90]}")
    check("grid-multi-index-progresses", progressed == total,
          f"{progressed}/{total} identities past the interpreter "
          "(artifact or a located refusal of another construct)")


# ---------------------------------------------------------------------------
# class 6: ``x is [not] None`` (the literal None typing)
# ---------------------------------------------------------------------------

def test_is_not_none():
    case = _case("suite/dev/grpo_loss__selective_log_softmax_kernel.py")
    src = fe_source.load_operator(case["kernel"].fn.__code__.co_filename)
    spec = fe_spec.specialize(src, case)
    env = spec.env()
    present = env.evaluate(
        ast.parse("MASK is not None", mode="eval").body, src.path)
    absent = env.evaluate(
        ast.parse("MASK is None", mode="eval").body, src.path)
    check("is-not-none-folds-on-presence",
          present is True and absent is False,
          f"MASK is not None -> {present!r}, MASK is None -> {absent!r} "
          "(MASK is a passed pointer argument: its traced object is "
          "never None)")

    # both grpo operators' identities progress past the 'literal' class
    progressed = 0
    total = 0
    for operator in ("suite/dev/grpo_loss__selective_log_softmax_kernel.py",
                     "suite/dev/backends__ascend__ops__grpo_loss__"
                     "selective_log_softmax_kernel.py"):
        module = _load(OPS / operator)
        made = module.make_case()
        if made.get("expected") is None:
            made["expected"] = module.ref(made["args"], made["meta"])
        payload = {k: v for k, v in made.items()
                   if k not in ("expected", "oracle_args")}
        total += 1
        compiler = _compiler()
        try:
            compiler.compile_case(payload)
            progressed += 1
        except PipelineError as exc:
            if exc.construct == "literal":
                print(f"    {operator}: still the literal-None refusal")
            else:
                progressed += 1
        except Exception as exc:                          # noqa: BLE001
            print(f"    {operator}: crashes: {type(exc).__name__}: "
                  f"{str(exc)[:90]}")
    check("is-not-none-progresses", progressed == total,
          f"{progressed}/{total} identities past the literal class "
          "(artifact or a located refusal of another construct)")


def main() -> int:
    test_licm_name_shadow()
    test_mask_complement()
    test_float_inf_identity()
    test_autotune_unwrap()
    test_grid_multi_index()
    test_is_not_none()
    if FAILURES:
        print(f"\n{len(FAILURES)} check(s) failed: {FAILURES}",
              file=sys.stderr)
        return 1
    print("\ntest_compile_regressions: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
