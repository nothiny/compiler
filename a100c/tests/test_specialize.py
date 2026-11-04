#!/usr/bin/env python3
"""test_specialize.py -- specialization identity and constexpr folding
(T006, acceptance[1] and acceptance[3]).

Identity (the corpus's declared meta tier, FE-COMPILE-TIME-VS-RUNTIME):
two cases differing only in shape, grid or scalar value produce ONE
identity; cases differing in constexpr, pointer dtype or scalar
specialization class produce distinct identities; do_not_specialize
parameters are excluded from the class computation; the identity model
matches the corpus's declared meta tier over the full corpus (compile
count 2113 = the live meta-tier census 2116 minus the 3 groups the
mandated do_not_specialize exclusion merges; the corpus's own declared
number is 2161, SUITE_V3.md 10.2 -- recorded drift; never the 2734 case
count).

Constexpr folding: dtype predicates and dead dtype-dispatch branches (the
16 tl.float64 branches no declared case dtype exercises) fold, the folded
comparison is still evaluated and recorded, and a construct outside the
declared surface is refused with a source location.

Run: python3 a100c/tests/test_specialize.py   (exit 0 = all checks PASS)
"""
from __future__ import annotations

import sys
import time
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
          f"{(' | ' + detail) if detail else ''}")
    if not ok:
        FAILURES.append(name)
    return ok


import numpy as np  # noqa: E402

from a100c.frontend import lower_tir, source, specialize  # noqa: E402
from a100c.frontend.source import FrontendError  # noqa: E402
from a100c.ir import tir  # noqa: E402

TEMPLATE = '''\
"""probe operator"""
OPERATOR = {{"name": "probe", "group": "probe", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": []}}
import triton
import triton.language as tl

@triton.jit
def probe_kernel({params}):
{body}
'''


def load(params, body, decorators="@triton.jit"):
    text = TEMPLATE.format(params=params,
                           body="\n".join("    " + line
                                          for line in body.splitlines()))
    text = text.replace("@triton.jit", decorators, 1)
    return source.load_operator_text(text, "<probe>", "probe.py")


def spec_of(src, args, meta=None, launch_meta=None, pointer_dtypes=None):
    case = {"args": args, "meta": meta or {}, "launch_meta": launch_meta or {}}
    if pointer_dtypes:
        case["pointer_dtypes"] = pointer_dtypes
    return specialize.specialize(src, case)


def arr(n=8, dtype=np.float32):
    return np.zeros(n, dtype=dtype)


# ---------------------------------------------------------------------------
# 1. Identity properties on a controlled fixture
# ---------------------------------------------------------------------------

def check_identity_properties():
    src = load("x_ptr, y_ptr, n, scale, flag, BLOCK: tl.constexpr",
               "tl.store(y_ptr + tl.arange(0, BLOCK), 1.0)")

    def ident(n=17, scale=0.5, flag=True, block=8, dtype=np.float32,
              pdt=None, launch=None):
        return spec_of(src, {"x_ptr": arr(8, dtype), "y_ptr": arr(8, dtype),
                             "n": n, "scale": scale, "flag": flag},
                       {"BLOCK": block}, launch, pdt).identity

    base = ident()
    results = []
    # shape/grid/scalar-value-only differences -> ONE identity
    results.append(("shape-only", ident(n=97) == base))
    results.append(("shape-only-2", ident(n=4097) == base))
    results.append(("scalar-value-same-class", ident(scale=1.5) == base))
    results.append(("grid-is-not-part-of-identity",
                    spec_of(src, {"x_ptr": arr(), "y_ptr": arr(), "n": 17,
                                  "scale": 0.5, "flag": True},
                            {"BLOCK": 8}).identity == base))
    # different constexpr / pointer dtype / scalar class -> distinct
    results.append(("constexpr-differs", ident(block=16) != base))
    results.append(("pointer-dtype-differs",
                    ident(dtype=np.float16) != base))
    results.append(("pointer-dtype-override-differs",
                    ident(pdt={"x_ptr": "bfloat16"}) != base))
    results.append(("scalar-class-one", ident(n=1) != base))
    results.append(("scalar-class-div16", ident(n=16) != base))
    results.append(("scalar-class-one-vs-div16", ident(n=1) != ident(n=16)))
    results.append(("scalar-value-same-class-2", ident(n=33) == ident(n=97)))
    results.append(("launch-meta-differs",
                    ident(launch={"num_warps": 8}) != base))
    # dtype-only override wins over the host dtype (bf16 on fp32 storage)
    bf16_id = ident(pdt={"x_ptr": "bfloat16", "y_ptr": "bfloat16"})
    results.append(("pointer-override-wins",
                    bf16_id != base and bf16_id != ident(dtype=np.float16)))
    bad = [name for name, ok in results if not ok]
    check("identity-properties", not bad, "; ".join(bad))


def check_do_not_specialize_excluded():
    src = load("x_ptr, y_ptr, n, k, BLOCK: tl.constexpr",
               "tl.store(y_ptr + tl.arange(0, BLOCK), 1.0)",
               decorators="@triton.jit(do_not_specialize=['n'], "
                          "do_not_specialize_on_alignment=['k'])")

    def ident(n, k=3):
        return spec_of(src, {"x_ptr": arr(), "y_ptr": arr(), "n": n, "k": k},
                       {"BLOCK": 8}).identity

    ok = ident(1) == ident(17) == ident(16)          # n fully excluded
    ok &= ident(3, 16) == ident(3, 17)               # k: div-16 not recorded
    ok &= ident(3, 1) != ident(3, 17)                # ==1 still applies to k
    # and a *specialized* parameter still splits
    src2 = load("x_ptr, y_ptr, n, k, BLOCK: tl.constexpr",
                "tl.store(y_ptr + tl.arange(0, BLOCK), 1.0)")
    ident2 = lambda n: spec_of(src2, {"x_ptr": arr(), "y_ptr": arr(),
                                      "n": n, "k": 3},
                               {"BLOCK": 8}).identity
    ok &= not (ident2(1) == ident2(17)) and not (ident2(16) == ident2(17))
    check("do_not_specialize-excluded-from-class", ok)


def check_autotune_identity():
    text = '''\
"""probe"""
OPERATOR = {"name": "probe", "group": "probe", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": []}
import triton
import triton.language as tl

@triton.autotune(
    configs=[
        triton.Config({'BLOCK': 64}, num_warps=4),
        triton.Config({'BLOCK': 128}, num_warps=8),
    ],
    key=['n'],
)
@triton.jit
def probe_kernel(x_ptr, n, BLOCK: tl.constexpr):
    tl.store(x_ptr + tl.arange(0, BLOCK), 1.0)
'''
    src = source.load_operator_text(text, "<probe>", "probe.py")
    s1 = spec_of(src, {"x_ptr": arr(), "n": 17}, {})
    s2 = spec_of(src, {"x_ptr": arr(), "n": 97}, {})
    s3 = spec_of(src, {"x_ptr": arr(8, np.float16), "n": 17}, {})
    ok = s1.identity == s2.identity          # deterministic choice, same key
    ok &= s1.identity != s3.identity         # pointer dtype still splits
    ok &= s1.param_constexprs == {"BLOCK": 64}
    ok &= s1.constexpr_values.get("config.BLOCK") == 64
    ok &= s1.constexpr_values.get("config.num_warps") == 4
    # an explicit meta value wins over the config
    s4 = spec_of(src, {"x_ptr": arr(), "n": 17}, {"BLOCK": 32})
    ok &= s4.param_constexprs == {"BLOCK": 32}
    check("autotune-deterministic-config-in-identity", ok)


# ---------------------------------------------------------------------------
# 2. Constexpr folding (acceptance[3])
# ---------------------------------------------------------------------------

def check_dtype_predicate_folding():
    src = load("x_ptr, y_ptr, n, BLOCK: tl.constexpr", """
dtype_ = x_ptr.type.element_ty
if dtype_ == tl.float64:
    acc = tl.float64
else:
    acc = tl.float32
z = tl.zeros([BLOCK], dtype=acc)
tl.store(y_ptr + tl.arange(0, BLOCK), z)
""")
    mod = lower_tir.lower(src, spec_of(
        src, {"x_ptr": arr(), "y_ptr": arr(), "n": 17}, {"BLOCK": 8}))
    zeros = [st for st in mod.functions[0].body.statements
             if isinstance(st, tir.Op) and st.op == "zeros"]
    ok = len(zeros) == 1 and zeros[0].results[0].type == tir.FLOAT32
    # the folded comparison was still evaluated and recorded
    folds = mod and None
    spec = spec_of(src, {"x_ptr": arr(), "y_ptr": arr(), "n": 17},
                   {"BLOCK": 8})
    lower_tir.lower(src, spec)
    f64 = spec.fold.float64_comparisons()
    ok &= len(f64) == 1 and f64[0].result is False
    ok &= any("float64" in c.text for c in spec.fold.comparisons)
    ok &= any(b.taken == "orelse" for b in spec.fold.branches)
    check("dtype-dispatch-folds-and-records-comparison", ok,
          f"comparisons={[c.text for c in spec.fold.comparisons]}")

    # the same kernel with a float64 pointer takes the float64 branch
    spec64 = spec_of(src, {"x_ptr": arr(8, np.float64),
                           "y_ptr": arr(8, np.float64), "n": 17},
                     {"BLOCK": 8})
    mod64 = lower_tir.lower(src, spec64)
    zeros64 = [st for st in mod64.functions[0].body.statements
               if isinstance(st, tir.Op) and st.op == "zeros"]
    ok64 = len(zeros64) == 1 and zeros64[0].results[0].type == tir.FLOAT64
    ok64 &= any(c.result is True for c in spec64.fold.float64_comparisons())
    ok64 &= any(b.taken == "body" for b in spec64.fold.branches)
    check("float64-dispatch-live-branch", ok64)


def check_dtype_predicates_surface():
    src = load("x_ptr, y_ptr, n, BLOCK: tl.constexpr", """
d = x_ptr.type.element_ty
a = d.is_floating()
b = d.is_int_signed()
c = d.is_int_unsigned()
q = tl.constexpr(a and not b and not c)
z = tl.zeros([BLOCK], dtype=tl.float32 if q else tl.int32)
tl.store(y_ptr + tl.arange(0, BLOCK), z)
""")
    spec = spec_of(src, {"x_ptr": arr(), "y_ptr": arr(), "n": 17},
                   {"BLOCK": 8})
    mod = lower_tir.lower(src, spec)
    zeros = [st for st in mod.functions[0].body.statements
             if isinstance(st, tir.Op) and st.op == "zeros"]
    ok = len(zeros) == 1 and zeros[0].results[0].type == tir.FLOAT32
    # int pointer: is_floating False, is_int_signed True -> int32 zeros
    spec_i = spec_of(src, {"x_ptr": arr(8, np.int32),
                           "y_ptr": arr(8, np.int32), "n": 17},
                     {"BLOCK": 8})
    mod_i = lower_tir.lower(src, spec_i)
    zeros_i = [st for st in mod_i.functions[0].body.statements
               if isinstance(st, tir.Op) and st.op == "zeros"]
    ok &= len(zeros_i) == 1 and zeros_i[0].results[0].type == tir.INT32
    # int_bitwidth folds on integer dtypes (the corpus's _inl_ pattern)
    src_w = load("x_ptr, y_ptr, n, BLOCK: tl.constexpr", """
d = x_ptr.type.element_ty
w: tl.constexpr = d.int_bitwidth
z = tl.zeros([BLOCK], dtype=tl.int64 if w == 32 else tl.int32)
tl.store(y_ptr + tl.arange(0, BLOCK), z)
""")
    spec_w = spec_of(src_w, {"x_ptr": arr(8, np.int32),
                             "y_ptr": arr(8, np.int32), "n": 17},
                     {"BLOCK": 8})
    mod_w = lower_tir.lower(src_w, spec_w)
    zeros_w = [st for st in mod_w.functions[0].body.statements
               if isinstance(st, tir.Op) and st.op == "zeros"]
    ok &= len(zeros_w) == 1 and zeros_w[0].results[0].type == tir.INT64
    # int_bitwidth on a float dtype is a located error, not a wrong number
    try:
        lower_tir.lower(src_w, spec_of(src_w, {"x_ptr": arr(),
                                               "y_ptr": arr(), "n": 17},
                                       {"BLOCK": 8}))
        ok &= False
    except FrontendError as exc:
        ok &= "int_bitwidth" in str(exc) and exc.line == 12
    # .dtype.element_ty on a loaded tensor folds through the pointer type
    src2 = load("x_ptr, y_ptr, n, BLOCK: tl.constexpr", """
v = tl.load(x_ptr + tl.arange(0, BLOCK))
d2 = v.dtype.element_ty
z = tl.zeros([BLOCK], dtype=tl.float64 if d2 == tl.float64 else tl.float32)
tl.store(y_ptr + tl.arange(0, BLOCK), z)
""")
    spec2 = spec_of(src2, {"x_ptr": arr(), "y_ptr": arr(), "n": 17},
                    {"BLOCK": 8})
    mod2 = lower_tir.lower(src2, spec2)
    zeros2 = [st for st in mod2.functions[0].body.statements
              if isinstance(st, tir.Op) and st.op == "zeros"]
    ok &= len(zeros2) == 1 and zeros2[0].results[0].type == tir.FLOAT32
    ok &= len(spec2.fold.float64_comparisons()) == 1
    check("dtype-predicates-fold", ok)


def check_runtime_condition_not_folded():
    src = load("x_ptr, y_ptr, n, BLOCK: tl.constexpr", """
v = tl.load(x_ptr + tl.arange(0, BLOCK))
if v > 0.0:
    w = v
else:
    w = -v
tl.store(y_ptr + tl.arange(0, BLOCK), w)
""")
    try:
        lower_tir.lower(src, spec_of(src, {"x_ptr": arr(), "y_ptr": arr(),
                                           "n": 17}, {"BLOCK": 8}))
        check("runtime-condition-not-folded-refused", False, "lowered")
    except FrontendError as exc:
        check("runtime-condition-not-folded-refused",
              "runtime 'if'" in str(exc) and exc.line == 12,
              f"line {exc.line}")


def check_real_corpus_folding():
    """The real corpus patterns: mul_scalar's constexpr IfExp and
    vector_norm's float64 dtype dispatch (dead for the declared dtypes)."""
    from opslib.runner import load_operator
    # mul_scalar: IS_BOOL constexpr conditional expression (real operator;
    # the corpus's own cases all carry IS_BOOL=False, so the float case is
    # the real corpus observation and the bool case is the same real kernel
    # with a hand-built bool payload exercising the other arm)
    rel = "suite/dev/mul_scalar_kernel.py"
    src = source.load_operator(str(OPS / rel), corpus_root=str(OPS))
    module = load_operator(str(OPS / rel))
    case = module.make_case(shape=(17,), dtype="float32")
    spec = specialize.specialize(src, case)
    mod = lower_tir.lower(src, spec)
    ops = [st.op for st in mod.functions[0].body.statements
           if isinstance(st, tir.Op)]
    ok = not tir.verify_module(mod)
    # the dead arm is gone: only the pid*BLOCK mul survives, no bit.and
    ok &= ops.count("arith.mul") == 2 and "bit.and" not in ops
    ok &= any(b.taken == "orelse" for b in spec.fold.branches)
    check("real-ifexp-folding-mul_scalar-float32", ok,
          f"branches: {[b.taken for b in spec.fold.branches]}")

    bool_case = {
        "args": {"x_ptr": np.zeros(17, dtype=np.bool_),
                 "output_ptr": np.zeros(17, dtype=np.bool_),
                 "scalar": True, "n_elements": 17},
        "meta": {"dtype": "bool", "BLOCK_SIZE": 128, "IS_BOOL": True},
        "launch_meta": {"num_warps": 4, "num_stages": 1},
    }
    spec_b = specialize.specialize(src, bool_case)
    mod_b = lower_tir.lower(src, spec_b)
    ops_b = [st.op for st in mod_b.functions[0].body.statements
             if isinstance(st, tir.Op)]
    ok_b = not tir.verify_module(mod_b)
    # the live arm is taken: bit.and appears, and only the pid*BLOCK mul
    ok_b &= "bit.and" in ops_b and ops_b.count("arith.mul") == 1
    ok_b &= any(b.taken == "body" for b in spec_b.fold.branches)
    ok_b &= spec_b.identity != spec.identity
    check("real-ifexp-folding-mul_scalar-bool-arm", ok_b,
          f"branches: {[b.taken for b in spec_b.fold.branches]}")

    # nansum_kernel_2: a real float64 dtype-dispatch kernel.  Its float16
    # case re-expresses the buffers in float16, so the tl.constexpr-wrapped
    # comparison folds False: the float64 branch is dead and the zeros is
    # emitted at fp32; the float32 case keeps the original builder's float64
    # buffers, so the same comparison folds True and the zeros is fp64.  The
    # loop after it is T008's scope: the lowering refuses there, after the
    # dispatch has folded and the zeros has been emitted.
    rel = "suite/dev/nansum_kernel_2.py"
    src = source.load_operator(str(OPS / rel), corpus_root=str(OPS))
    module = load_operator(str(OPS / rel))
    for dtype, want_branch, want_zeros in (("float16", "orelse",
                                            tir.FLOAT32),
                                           ("float32", "body",
                                            tir.FLOAT64)):
        case = module.make_case(shape=(17,), dtype=dtype)
        spec = specialize.specialize(src, case)
        lowering = lower_tir.Lowering(src, spec)
        refused_at_loop = False
        try:
            lowering.lower()
        except FrontendError as exc:
            refused_at_loop = "loops are not lowered" in str(exc)
        f64 = spec.fold.float64_comparisons()
        zeros = [st for st in lowering.module.functions[0].body.statements
                 if isinstance(st, tir.Op) and st.op == "zeros"]
        ok = refused_at_loop and len(f64) == 1
        ok &= f64[0].result is (want_branch == "body")
        ok &= len(zeros) == 1 and zeros[0].results[0].type == want_zeros
        ok &= any(b.taken == want_branch for b in spec.fold.branches)
        check(f"real-float64-dispatch-nansum_kernel_2-{dtype}", ok,
              f"folded={[c.text for c in f64]} result={[c.result for c in f64]} "
              f"zeros={zeros[0].results[0].type if zeros else None}")


# ---------------------------------------------------------------------------
# 3. The full-corpus identity census (bounded)
# ---------------------------------------------------------------------------

def check_corpus_census():
    sys.path.insert(0, str(OPS / "harness"))
    import os
    os.chdir(str(OPS))
    from compiler_api import identity as identity_lib
    from compiler_api.run_cases import cases_from_manifest, enumerate_cases
    from opslib import golden

    started = time.time()
    paths = cases_from_manifest(str(OPS / "suite/manifest.json"))
    mine = {}
    corpus = {}
    type_span = {}
    cases = 0
    for spec_h, shape, dtype in enumerate_cases(paths=paths):
        case = golden.load_or_build_spec(spec_h, shape=shape, dtype=dtype,
                                         seed=30, use_cache=True)
        src = source.load_operator(spec_h.path, corpus_root=str(OPS))
        sp = specialize.specialize(src, case)
        cid = identity_lib.case_identity(spec_h.source, case, "meta")
        mine.setdefault(sp.identity, []).append((spec_h.source, tuple(shape),
                                                 str(dtype), cid))
        corpus.setdefault(cid, []).append((spec_h.source, tuple(shape),
                                           str(dtype), sp.identity))
        key = (tuple(sorted((n, repr(t))
                            for n, t in sp.pointer_types.items())),
               tuple(sorted((n, repr(t))
                            for n, t in sp.scalar_types.items())))
        type_span.setdefault(sp.identity, set()).add(key)
        cases += 1
    elapsed = time.time() - started

    # the identity model matches the corpus's declared meta tier: it never
    # splits a corpus identity (pure coarsening) and differs only by the
    # mandated do_not_specialize exclusion
    straddled = [cid for cid, members in corpus.items()
                 if len({m[3] for m in members}) > 1]
    merge_total = 0
    merged_ops = set()
    for mid, members in mine.items():
        cids = {m[3] for m in members}
        if len(cids) > 1:
            merge_total += len(cids) - 1
            merged_ops.add(members[0][0])
    bad_types = {k: v for k, v in type_span.items() if len(v) > 1}

    declared = 2161        # SUITE_V3.md 10.2 / OPERATOR_INVENTORY 1
    live = len(corpus)     # the corpus's own identity.py on this tree
    ok = (cases == 2734 and not straddled and not bad_types
          and len(mine) == live - merge_total
          and merged_ops == {"suite/dev/var_mean_welford_kernel.py"}
          and len(mine) <= declared and len(mine) < 0.78 * cases)
    check("corpus-identity-census-matches-meta-tier", ok,
          f"cases={cases} identities={len(mine)} corpus-meta-tier={live} "
          f"declared={declared} dns-merges={sorted(merged_ops)}x{merge_total} "
          f"({elapsed:.0f}s, never the {cases} case count)")


def main() -> int:
    check_identity_properties()
    check_do_not_specialize_excluded()
    check_autotune_identity()
    check_dtype_predicate_folding()
    check_dtype_predicates_surface()
    check_runtime_condition_not_folded()
    check_real_corpus_folding()
    check_corpus_census()
    if FAILURES:
        print(f"test_specialize: {len(FAILURES)} check(s) FAILED: "
              f"{FAILURES}")
        return 1
    print("test_specialize: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
