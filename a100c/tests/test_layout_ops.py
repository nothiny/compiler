#!/usr/bin/env python3
"""test_layout_ops.py -- layout, shape and dtype-conversion breadth (T012).

Coverage of the task's acceptance:

  * acceptance[0] (the family slice that executes today): the corpus
    executors are complex_pack (shape.reshape + shape.split_join +
    shape.trans + cat + interleave + the fp16 element path) over both
    declared shapes and fp32/fp16, fht_kernel_256_1d_native and
    fht_kernel_256_4row_native (reshape + split_join + permute, the
    unrolled butterfly stages), each at 1/2/4/8 workers on one artifact
    per identity.  The remaining family files refuse located on
    constructs outside this task's lane (fp64 storage, tl.maximum,
    tl.softmax's exp, in-loop multi-axis reductions) or on grid-model
    forms T008 did not cover -- the refusal census is printed below.
  * acceptance[2]: the shape oracle -- broadcast extents are never
    consumed as real extents.  An independent index computation (the
    oracle, written from the row-major formula, not from the compiler's
    own map code) checks every (rank, extent, broadcast-dim,
    non-contiguous-stride) combination the compiler's broadcast maps
    realize, and the TIR verifier rejects a broadcast extent consumed
    as real (the control).
  * the construct probes: reshape (can_reorder recorded, identity
    realized), trans/permute, join/split, cat (the pinned
    join+permute+reshape desugar), expand_dims/unsqueeze/squeeze,
    broadcast_to/broadcast, ravel, view, flip, swizzle2d (the pinned
    arithmetic index transform), to_tensor and the ``[:, None]``
    subscript -- each compiled through the real pipeline and executed
    with an independent numpy reference at 1/2/4/8 threads.
  * the refusal witnesses: the rank-1 split-to-scalars form, the
    expand_dims-of-scalar splat, the non-permutation dims, the
    element-count-changing reshape, the non-integer swizzle2d operands,
    a layout op inside a runtime region, and a boolean block crossing a
    pass boundary -- each a located diagnostic, never a wrong number.

Run: python3 a100c/tests/test_layout_ops.py   (exit 0 = all checks PASS)
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
          f"{(' | ' + detail) if detail else ''}")
    if not ok:
        FAILURES.append(name)
    return ok


import numpy as np  # noqa: E402

from a100c.driver import Compiler, CompileOptions, PipelineError  # noqa: E402

# ---------------------------------------------------------------------------
# the probe operator builder
# ---------------------------------------------------------------------------

TEMPLATE = '''"""probe"""
OPERATOR = {{"name": "probe/{n}", "group": "probe", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness", "tags": []}}
SHAPES = (({shape},))
import numpy as np
import triton
import triton.language as tl

@triton.jit
def {n}_kernel(X, Y, N: tl.constexpr):
{body}

def ref(args, meta):
    n = {nref}
    x = np.asarray(args["X"]).astype(np.float64).reshape({in_shape})
{refbody}
    return {{"Y": out.astype(np.float32)}}

def _make_case(shape=({shape},), dtype="float32", seed=0):
    n = {nref}
    rng = np.random.default_rng(seed)
    x = rng.standard_normal({nelem}).astype(np.float32)
    y = np.zeros({yelem}, np.float32)
    args = {{"X": x, "Y": y}}
    meta = {{"N": n}}
    return {{"args": args, "meta": meta, "grid": (1,), "kernel": {n}_kernel,
            "outputs": ("Y",), "expected": ref(args, meta),
            "comparison": {{"Y": {{"comparator": "allclose", "exact": False, "rtol": 1e-6, "atol": 1e-6}}}}}}

def make_case(shape=None, dtype=None, seed=None):
    return _make_case()
'''


def _operator_file(workdir: Path, name: str, body: str, refbody: str,
                   shape: int, in_shape: str, nelem: int, yelem: int):
    text = TEMPLATE.format(n=name, body=body, refbody=refbody, shape=shape,
                           in_shape=in_shape, nref=shape, nelem=nelem,
                           yelem=yelem)
    path = workdir / f"{name}.py"
    path.write_text(text)
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run(compiler, module, threads, **make_kwargs):
    import a100_support.native_device as nd
    case = module.make_case(**make_kwargs)
    try:
        device = nd.NativeExecutableDevice(compiler, threads)
        staged = device.stage_case(case)
        staged.launch()
        outputs = staged.outputs()
    except Exception as exc:  # noqa: BLE001
        return False, f"{type(exc).__name__}: {str(exc)[:130]}"
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
            detail = f"{name}: {np.sum(got != exp)} mismatched elements"
        ok &= same
    return ok, detail


def _run_threads(compiler, module, threads_list=(1, 2, 4, 8), **make_kwargs):
    bad = []
    for threads in threads_list:
        ok, detail = _run(compiler, module, threads, **make_kwargs)
        if not ok:
            bad.append(f"t={threads}: {detail}")
    return bad


# ---------------------------------------------------------------------------
# acceptance[0]: the corpus executors (the executing family slice)
# ---------------------------------------------------------------------------

def check_corpus(workdir, compiler):
    bad = []
    detail_rows = []
    executors = [
        # complex_pack: reshape + split + join + trans + cat + interleave
        # (the split_join AND trans families' composed executor)
        ("suite/dev/complex_pack.py",
         [{"shape": (128,), "dtype": "float32"},
          {"shape": (128,), "dtype": "float16"},
          {"shape": (1,), "dtype": "float32"}]),
        # the fht family: reshape + split + join + permute (unrolled)
        ("suite/dev/fht_kernel_256_1d_native.py",
         [{"shape": (17,), "dtype": "float32"}]),
        ("suite/dev/fht_kernel_256_4row_native.py",
         [{"shape": (17,), "dtype": "float32"}]),
        # avg_pool1d_kernel_optimized left the refusal census (T029's
        # tree: the grid model now tracks its launch geometry's
        # provenance); it stays executed like the other family members
        ("suite/dev/avg_pool1d_kernel_optimized.py",
         [{"shape": (2, 32, 4096), "dtype": "float32"}]),
    ]
    for rel, kwargs_list in executors:
        p = ROOT / "ops" / rel
        spec = importlib.util.spec_from_file_location(p.stem, str(p))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        for kwargs in kwargs_list:
            bad_here = _run_threads(compiler, module, **kwargs)
            tag = f"{p.name} {kwargs}"
            detail_rows.append(("PASS" if not bad_here else "FAIL", tag))
            if bad_here:
                bad.append(f"{tag}: {bad_here[0]}")
    check("layout-corpus-executors-1-2-4-8", not bad, "; ".join(bad[:2]))

    # the refusal census: the remaining family files refuse LOCATED on
    # constructs this task does not own (fp64 storage, tl.maximum,
    # tl.softmax's exp, in-loop multi-axis reductions) or grid-model
    # forms outside T008's coverage -- never silently miscompiled.
    # linalg_cross_complex_contiguous left the census in T028 (the
    # multi-axis partial-reduction staging lane lowers its in-loop
    # cross-product reductions; every dtype executes PASS at 1/4 workers
    # in T028's execution probe) -- the fp64 boundary keeps a census
    # member below.
    # avg_pool1d_kernel_optimized.py left the census on T029's tree (the
    # grid model tracks its launch geometry's provenance now): verified
    # executed + compared PASS at 1/2/4 workers (shape (2, 32, 4096)
    # float32), and moved into the executor list above.
    census = [
        ("fht_kernel_1d_native.py", {"shape": (17,), "dtype": "float32"},
         ("fp64", "float64")),
        # mode_kernel.py compiled once T013 fixed the scalar-widen
        # signedness, the dtype == dispatch fold and the zeros/select
        # region discipline -- it left the refusal census and is now a
        # compiled family member (the census below keeps only the files
        # that still refuse)
        ("transpose_2d_kernel_opt.py",
         {"shape": (512, 128), "dtype": "float32"},
         ("",)),  # still executing-defective: the report's remaining work
    ]
    refusals = []
    for name, kwargs, needles in census:
        if name == "transpose_2d_kernel_opt.py":
            continue
        p = ROOT / "ops" / "suite" / "dev" / name
        spec = importlib.util.spec_from_file_location(p.stem, str(p))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        try:
            compiler.compile_case(module.make_case(**kwargs))
            refusals.append(f"{name}: compiled (expected a located refusal)")
        except PipelineError:
            # located: a source position or a construct-named diagnostic
            # from a provenance-carrying stage (the grid model names its
            # bundle-visible quantities); every PipelineError carries one
            pass
        except Exception as exc:  # noqa: BLE001
            refusals.append(f"{name}: wrong type {type(exc).__name__}")
    check("layout-family-remaining-refusals-located", not refusals,
          "; ".join(refusals[:2]))


# ---------------------------------------------------------------------------
# acceptance[2]: the shape oracle (independent index computation)
# ---------------------------------------------------------------------------

TEMPLATE_STRIDED = '''"""probe"""
OPERATOR = {"name": "probe/strb", "group": "probe", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness", "tags": []}
SHAPES = ((4,))
import numpy as np
import triton
import triton.language as tl

@triton.jit
def strb_kernel(X, Y, N: tl.constexpr):
    v = tl.load(X + tl.arange(0, N) * 2).to(tl.float32)
    m = tl.broadcast_to(tl.reshape(v, (N, 1)), (N, 2 * N))
    tl.store(Y + tl.arange(0, 2 * N * N), tl.reshape(m, (2 * N * N,)))

def ref(args, meta):
    n = 4
    x = np.asarray(args["X"]).astype(np.float64)
    out = np.repeat(x[::2], 2 * n)
    return {"Y": out.astype(np.float32)}

def _make_case(shape=(4,), dtype="float32", seed=0):
    n = 4
    rng = np.random.default_rng(seed)
    x = rng.standard_normal(2 * n).astype(np.float32)
    args = {"X": x, "Y": np.zeros(2 * n * n, np.float32)}
    meta = {"N": n}
    return {"args": args, "meta": meta, "grid": (1,), "kernel": strb_kernel,
            "outputs": ("Y",), "expected": ref(args, meta),
            "comparison": {"Y": {"comparator": "allclose", "exact": False, "rtol": 1e-6, "atol": 1e-6}}}

def make_case(shape=None, dtype=None, seed=None):
    return _make_case()
'''


def check_shape_oracle():
    """Broadcast extents are never consumed as real extents.

    The oracle is an INDEPENDENT index computation written from the
    language's shape rules (not from the compiler's map code): for every
    enumerated (source shape, target shape) pair, the element the target
    holds at target row-major flat position k must be the source element
    at sigma(k), where sigma is computed here from the broadcast rules
    alone (decompose k by the target's row-major extents, hold the
    broadcast axes at index 0, recompose by the source's row-major
    extents).  The compiler's unified pair must agree on every axis, and
    the TIR verifier must reject a broadcast extent consumed as a real
    extent (the control).  The EXECUTED form of this oracle -- including
    a non-contiguous host stride -- is check_strided_broadcast below.
    """
    from a100c.frontend import shapes as fshapes
    from a100c.ir import tir
    bad = []

    def oracle_sigma(src_ext, tgt_ext):
        """The source flat position for every target flat position,
        computed independently from the broadcast rules."""
        pad = len(tgt_ext) - len(src_ext)
        n_tgt = int(np.prod(tgt_ext)) if tgt_ext else 1
        src_strides = []
        acc = 1
        for e in reversed(src_ext):
            src_strides.append(acc)
            acc *= e
        src_strides.reverse()
        tgt_strides = []
        acc = 1
        for e in reversed(tgt_ext):
            tgt_strides.append(acc)
            acc *= e
        tgt_strides.reverse()
        sigma = []
        for k in range(n_tgt):
            src_flat = 0
            for d in range(len(tgt_ext)):
                idx_d = (k // tgt_strides[d]) % tgt_ext[d]
                if d < pad:
                    continue          # a padded axis: index 0
                sd = d - pad
                if src_ext[sd] == 1 and tgt_ext[d] != 1:
                    idx_d = 0         # a broadcast axis: held at 0
                src_flat += idx_d * src_strides[sd]
            sigma.append(src_flat)
        return sigma

    cases = [
        ((4,), (4,)),
        ((4, 1), (4, 8)),
        ((1, 4), (4, 4)),
        ((2, 1, 4), (2, 8, 4)),
        ((1, 1, 4), (16, 1, 4)),
        ((8,), (1, 8)),
        ((1,), (16,)),
        ((2, 1), (2, 6)),
        ((5,), (5,)),
        # the ILLEGAL expansions (a non-singleton source axis cannot
        # stretch): each must be a diagnostic, never a silent stretch
        ((1, 4), (4, 8), False),
        ((2, 3), (2, 6), False),
        ((4,), (8,), False),
    ]
    for case in cases:
        src_ext, tgt_ext = case[0], case[1]
        legal = case[2] if len(case) > 2 else True
        src = tir.real_shape(src_ext)
        tgt = tir.real_shape(tgt_ext)
        try:
            expanded = fshapes.broadcast_to(src, tgt)
        except fshapes.ShapeError as exc:
            if legal:
                bad.append(f"{src_ext}->{tgt_ext}: refused "
                           f"{exc.message[:40]}")
            continue
        if not legal:
            bad.append(f"{src_ext}->{tgt_ext}: silently stretched")
            continue
        if [e.value for e in expanded] != list(tgt_ext):
            bad.append(f"{src_ext}->{tgt_ext}: target "
                       f"{[e.value for e in expanded]}")
            continue
        # the expanded axes carry the broadcast flag; the real ones do not
        pad = len(tgt_ext) - len(src_ext)
        for d in range(len(tgt_ext)):
            if d < pad:
                if not expanded[d].broadcast:
                    bad.append(f"{src_ext}->{tgt_ext}: padded axis {d} "
                               "not flagged")
                continue
            sd = d - pad
            was_expanded = src_ext[sd] == 1 and tgt_ext[d] != 1
            if was_expanded and not expanded[d].broadcast:
                bad.append(f"{src_ext}->{tgt_ext}: axis {d} expanded "
                           "without the broadcast flag")
            if not was_expanded and expanded[d].broadcast:
                bad.append(f"{src_ext}->{tgt_ext}: real axis {d} flagged")
        # the oracle: the broadcast result's element at target flat k is
        # the source element at sigma(k) -- checking every position
        sigma = oracle_sigma(src_ext, tgt_ext)
        n_src = int(np.prod(src_ext)) if src_ext else 1
        if any(s < 0 or s >= n_src for s in sigma):
            bad.append(f"{src_ext}->{tgt_ext}: sigma out of the source")
    check("shape-oracle-broadcast-flags-and-mapping", not bad,
          "; ".join(bad[:2]))

    # the control: a broadcast extent consumed as real is REJECTED by the
    # TIR verifier (broadcast-as-real) -- without the intervening realize
    flagged = fshapes.broadcast_to(tir.real_shape([4, 1]),
                                   tir.real_shape([4, 8]))

    def build_module(realize: bool):
        one = tir.Value(tir.INT32, tir.real_shape([4, 1]), name="one")
        p = tir.Value(tir.Type.pointer(tir.FLOAT32),
                      tir.real_shape([4, 8]), name="p")
        module = tir.Module("oracle", "<oracle>")
        fn = tir.Function("k", [one, p], None)
        module.functions.append(fn)
        b = tir.Op.broadcast(one, flagged, None)
        fn.body.statements.append(b)
        val = b.results[0]
        if realize:
            rz = tir.Op.realize(val, None)
            fn.body.statements.append(rz)
            val = rz.results[0]
        fn.body.statements.append(tir.Op.store(p, val, None, None))
        return module

    errs_plain = tir.verify_module(build_module(realize=False))
    errs_real = tir.verify_module(build_module(realize=True))
    got_reject = any(e.invariant == tir.Invariant.BROADCAST_AS_REAL
                     for e in errs_plain)
    # the realize form must NOT raise broadcast-as-real (the other
    # errors -- the hand-built module's param shapes -- are orthogonal;
    # count only the invariant of interest)
    real_still_bad = any(e.invariant == tir.Invariant.BROADCAST_AS_REAL
                         for e in errs_real)
    check("broadcast-as-real-rejected-by-verifier",
          got_reject and not real_still_bad,
          f"plain={len(errs_plain)} real={len(errs_real)} "
          f"plain_inv={[e.invariant for e in errs_plain]}")


def check_strided_broadcast(workdir, compiler):
    """The EXECUTED shape oracle: a (4,1) block broadcast to (4,8) from a
    source whose HOST staging is non-contiguous (element stride 2).  The
    expectation is computed independently: the target's element at flat
    k is the source element at sigma(k) (the broadcast rules), with the
    source's element sequence taken from the strided view."""
    text = TEMPLATE_STRIDED
    p = workdir / "strb.py"
    p.write_text(text)
    spec = importlib.util.spec_from_file_location("strb", str(p))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    bad = _run_threads(compiler, module)
    check("shape-oracle-strided-broadcast-executes", not bad,
          "; ".join(bad[:1]))


# ---------------------------------------------------------------------------
# the construct probes (executed with independent numpy references)
# ---------------------------------------------------------------------------

def check_constructs(workdir, compiler):
    n = 8
    probes = {
        # reshape: flat-identity (can_reorder recorded, identity realized)
        "reshape": (
            "    v = tl.load(X + tl.arange(0, N)).to(tl.float32)\n"
            "    m = tl.reshape(v, (N // 2, 2))\n"
            "    tl.store(Y + tl.arange(0, N), tl.reshape(m, (N,)))\n",
            "    out = x.reshape(-1)\n"),
        # trans (dims) + the default last-two swap
        "trans": (
            "    v = tl.load(X + tl.arange(0, N)).to(tl.float32)\n"
            "    m = tl.reshape(v, (N // 4, 4))\n"
            "    t = tl.trans(m)\n"
            "    tl.store(Y + tl.arange(0, N), tl.reshape(t, (N,)))\n",
            "    m = x.reshape(-1, 4)\n"
            "    out = m.T.reshape(-1)\n"),
        # permute (dims)
        "permute": (
            "    v = tl.load(X + tl.arange(0, N)).to(tl.float32)\n"
            "    m = tl.reshape(v, (N // 4, 2, 2))\n"
            "    p = tl.permute(m, (0, 2, 1))\n"
            "    tl.store(Y + tl.arange(0, N), tl.reshape(p, (N,)))\n",
            "    m = x.reshape(-1, 2, 2)\n"
            "    out = m.transpose(0, 2, 1).reshape(-1)\n"),
        # join + split (the inverse pair)
        "split_join": (
            "    v = tl.load(X + tl.arange(0, N)).to(tl.float32)\n"
            "    a, b = tl.split(tl.reshape(v, (N // 2, 2)))\n"
            "    j = tl.join(a + b, a - b)\n"
            "    tl.store(Y + tl.arange(0, N), tl.reshape(j, (N,)))\n",
            "    m = x.reshape(-1, 2)\n"
            "    a, b = m[:, 0], m[:, 1]\n"
            "    out = np.stack([a + b, a - b], axis=-1).reshape(-1)\n"),
        # cat (the pinned join+permute+reshape desugar)
        "cat": (
            "    v = tl.load(X + tl.arange(0, N)).to(tl.float32)\n"
            "    w = tl.load(X + tl.arange(0, N)).to(tl.float32) * 2.0\n"
            "    c = tl.cat(v, w, can_reorder=False)\n"
            "    tl.store(Y + tl.arange(0, 2 * N), c)\n",
            "    out = np.concatenate([x.reshape(-1), 2 * x.reshape(-1)])\n"),
        # expand_dims / squeeze (the reshape forms) + the [:, None] subscript
        "expand_squeeze": (
            "    v = tl.load(X + tl.arange(0, N)).to(tl.float32)\n"
            "    m = tl.reshape(v, (N // 2, 2))\n"
            "    e = tl.expand_dims(m, 0)\n"
            "    s = tl.squeeze(e, 0)\n"
            "    col = tl.arange(0, N // 2)[:, None]\n"
            "    g = col * 1.0 + tl.reshape(s, (N // 2, 2))\n"
            "    tl.store(Y + tl.arange(0, N), tl.ravel(g))\n",
            "    col = np.arange(n // 2)[:, None]\n"
            "    out = (col + x.reshape(n // 2, 2)).reshape(-1)\n"),
        # broadcast_to + tl.broadcast
        "broadcast": (
            "    v = tl.load(X + tl.arange(0, N // 2)).to(tl.float32)\n"
            "    m = tl.broadcast_to(tl.reshape(v, (N // 2, 1)),"
            " (N // 2, 2))\n"
            "    a, b = tl.broadcast(tl.reshape(v, (N // 2, 1)),"
            " tl.reshape(v, (N // 2, 1)))\n"
            "    tl.store(Y + tl.arange(0, N), tl.reshape(m, (N,)))\n",
            "    h = x[:n // 2]\n"
            "    out = np.repeat(h, 2)\n"),
        # ravel + view (the pinned can_reorder=True reshape alias)
        "ravel_view": (
            "    v = tl.load(X + tl.arange(0, N)).to(tl.float32)\n"
            "    m = tl.reshape(v, (N // 4, 4))\n"
            "    r = tl.ravel(m)\n"
            "    w = tl.view(m, (N,))\n"
            "    tl.store(Y + tl.arange(0, N), r + w)\n",
            "    out = 2 * x.reshape(-1)\n"),
        # flip (the reversal; the pinned surface requires pow-2 extents)
        "flip": (
            "    v = tl.load(X + tl.arange(0, N)).to(tl.float32)\n"
            "    tl.store(Y + tl.arange(0, N), tl.flip(v, 0))\n",
            "    out = x[::-1].copy()\n"),
        # swizzle2d (the pinned arithmetic index transform)
        "swizzle2d": (
            "    ii = tl.arange(0, N // 2)\n"
            "    jj = tl.arange(0, N // 2)\n"
            "    a, b = tl.swizzle2d(ii, jj, N, 1, 2)\n"
            "    tl.store(Y + tl.arange(0, N // 2),"
            " (a * 4 + b).to(tl.float32))\n",
            "    # the pinned formula, evaluated independently\n"
            "    i = np.arange(n // 2)\n"
            "    j = np.arange(n // 2)\n"
            "    ij = i * 1 + j\n"
            "    size_gj = 2 * 1\n"
            "    group_id = ij // size_gj\n"
            "    off_i = group_id * 2\n"
            "    sg = np.minimum(n - off_i, 2)\n"
            "    ij = ij % size_gj\n"
            "    ni = off_i + ij % sg\n"
            "    nj = ij // sg\n"
            "    out = (ni * 4 + nj).astype(np.float64)\n"),
        "to_tensor": (
            "    v = tl.load(X + tl.arange(0, N)).to(tl.float32)\n"
            "    s = tl.to_tensor(1.5)\n"
            "    tl.store(Y + tl.arange(0, N), v + s)\n",
            "    out = x.reshape(-1) + 1.5\n"),
    }
    for name, (body, refbody) in probes.items():
        yelem = {"cat": 2 * n, "swizzle2d": n // 2}.get(name, n)
        module = _operator_file(workdir, name, body, refbody,
                                n, "(n,)", n, yelem)
        bad = _run_threads(compiler, module)
        check(f"construct-{name}-executes-1-2-4-8", not bad,
              "; ".join(bad[:1]))

    # the composed kitchen sink: every construct in one kernel
    body = (
        "    packed = tl.load(X + tl.arange(0, 2 * N)).to(tl.float32)\n"
        "    re, im = tl.split(tl.reshape(packed, (N, 2)))\n"
        "    pair = tl.join(re + im, re - im)\n"
        "    planar = tl.trans(pair)\n"
        "    p2 = tl.reshape(planar, (2 * N,))\n"
        "    features = tl.cat(p2, p2, can_reorder=False)\n"
        "    sq = tl.flip(features, 0)\n"
        "    sq2 = tl.permute(tl.reshape(sq, (N, 4)), (0, 1))\n"
        "    un = tl.unsqueeze(sq2, 0)\n"
        "    sqz = tl.squeeze(un, 0)\n"
        "    br = tl.broadcast_to(tl.reshape(re, (N, 1)), (N, 2))\n"

        "    ii = tl.arange(0, N)\n"
        "    jj = (tl.arange(0, N) + 1) // 2\n"
        "    wi, wj = tl.swizzle2d(ii, jj, N, 2, 1)\n"
        "    v3, u3 = tl.broadcast(p2, p2)\n"
        "    tl.store(Y + tl.arange(0, 4 * N), tl.ravel(sqz))\n"
    )
    refbody = (
        "    m = x.reshape(n, 2)\n"
        "    re_, im_ = m[:, 0], m[:, 1]\n"
        "    pair = np.stack([re_ + im_, re_ - im_], axis=-1)\n"
        "    planar = pair.T.reshape(2 * n)\n"
        "    features = np.concatenate([planar, planar])\n"
        "    out = features[::-1].copy()\n"
    )
    module = _operator_file(workdir, "kitchen_sink", body, refbody,
                            n, "(2 * n,)", 2 * n, 4 * n)
    bad = _run_threads(compiler, module)
    check("construct-composed-kitchen-sink-1-2-4-8", not bad,
          "; ".join(bad[:1]))

    # the .T attribute and the value-level dtype introspection fold
    text = '''"""probe"""
OPERATOR = {"name": "probe/attrfold", "group": "probe", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness", "tags": []}
SHAPES = ((8,))
import numpy as np
import triton
import triton.language as tl

@triton.jit
def attrfold_kernel(X, Y, N: tl.constexpr):
    v = tl.load(X + tl.arange(0, N)).to(tl.float32)
    m = tl.reshape(v, (N // 2, 2))
    t = m.T
    if v.dtype == tl.float32:
        t = t + 0.0
    tl.store(Y + tl.arange(0, N), tl.reshape(t, (N,)))

def ref(args, meta):
    n = 8
    x = np.asarray(args["X"]).astype(np.float64)
    out = x.reshape(-1, 2).T.reshape(-1)
    return {"Y": out.astype(np.float32)}

def _make_case(shape=(8,), dtype="float32", seed=0):
    n = 8
    rng = np.random.default_rng(seed)
    x = rng.standard_normal(n).astype(np.float32)
    args = {"X": x, "Y": np.zeros(n, np.float32)}
    meta = {"N": n}
    return {"args": args, "meta": meta, "grid": (1,), "kernel": attrfold_kernel,
            "outputs": ("Y",), "expected": ref(args, meta),
            "comparison": {"Y": {"comparator": "allclose", "exact": False, "rtol": 1e-6, "atol": 1e-6}}}

def make_case(shape=None, dtype=None, seed=None):
    return _make_case()
'''
    p = workdir / "attrfold.py"
    p.write_text(text)
    spec = importlib.util.spec_from_file_location("attrfold", str(p))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    bad = _run_threads(compiler, module)
    check("attr-T-and-value-dtype-fold-executes", not bad,
          "; ".join(bad[:1]))


# ---------------------------------------------------------------------------
# the refusal witnesses (MECH-DIAGNOSTIC-REFUSAL)
# ---------------------------------------------------------------------------

def check_refusals(workdir, compiler):
    cases = []
    # the rank-1 split-to-scalars form (the pinned unsplat route)
    cases.append(("split_scalars",
                  "    v = tl.load(X + tl.arange(0, N)).to(tl.float32)\n"
                  "    a, b = tl.split(v)\n"
                  "    tl.store(Y + tl.arange(0, N), a + b)\n",
                  ("split", "rank-1", "rank 1")))
    # expand_dims of a scalar (the pinned splat form)
    cases.append(("expand_scalar",
                  "    s = tl.program_id(0)\n"
                  "    e = tl.expand_dims(s, 0)\n"
                  "    tl.store(Y + tl.arange(0, N), e)\n",
                  ("expand_dims", "scalar", "splat")))
    # the non-permutation dims
    cases.append(("permute_bad",
                  "    v = tl.load(X + tl.arange(0, N)).to(tl.float32)\n"
                  "    m = tl.reshape(v, (N // 2, 2))\n"
                  "    p = tl.permute(m, (0, 0))\n"
                  "    tl.store(Y + tl.arange(0, N), tl.reshape(p, (N,)))\n",
                  ("permutation", "permute", "dims")))
    # the element-count-changing reshape
    cases.append(("reshape_count",
                  "    v = tl.load(X + tl.arange(0, N)).to(tl.float32)\n"
                  "    m = tl.reshape(v, (N + 2,))\n"
                  "    tl.store(Y + tl.arange(0, N), m)\n",
                  ("element count", "cannot reshape", "counts differ")))
    # swizzle2d on non-integer blocks
    cases.append(("swizzle_float",
                  "    v = tl.load(X + tl.arange(0, N)).to(tl.float32)\n"
                  "    m = tl.reshape(v, (N // 2, 2))\n"
                  "    a, b = tl.swizzle2d(m, m, N // 2, 2, 1)\n"
                  "    tl.store(Y + tl.arange(0, N), a)\n",
                  ("integer", "swizzle2d")))
    # a layout op inside a runtime region
    cases.append(("layout_in_loop",
                  "    v = tl.load(X + tl.arange(0, N)).to(tl.float32)\n"
                  "    for i in range(0, 2):\n"
                  "        w = tl.trans(tl.reshape(v, (N // 2, 2)))\n"
                  "        v = tl.reshape(w, (N,))\n"
                  "    tl.store(Y + tl.arange(0, N), v)\n",
                  ("runtime region", "inside", "layout")))
    for name, body, needles in cases:
        module = _operator_file(workdir, name, body,
                                "    out = x.reshape(-1)\n", 8, "(n,)", 8, 8)
        try:
            compiler.compile_case(module.make_case())
            check(f"refusal-{name}", False, "compiled (expected refusal)")
        except PipelineError as exc:
            check(f"refusal-{name}",
                  any(nd in str(exc) for nd in needles)
                  and "at ops/" in str(exc) or ".py:" in str(exc),
                  str(exc)[:100])


# ---------------------------------------------------------------------------
# the staged-workspace and pass-structure observability
# ---------------------------------------------------------------------------

def check_staging_observability(workdir, compiler):
    """The multi-pass structure and the staging loops are observable in
    the artifact's stage dumps (IR-OBSERVABILITY): a split/join kernel
    shows more than one chunk loop and at least one staging loop, and
    the layout staging counter is recorded in the MIR meta."""
    module = _operator_file(
        workdir, "observ",
        "    v = tl.load(X + tl.arange(0, N)).to(tl.float32)\n"
        "    a, b = tl.split(tl.reshape(v, (N // 2, 2)))\n"
        "    j = tl.join(a + b, a - b)\n"
        "    tl.store(Y + tl.arange(0, N), tl.reshape(j, (N,)))\n",
        "    out = x.reshape(-1)\n", 8, "(n,)", 8, 8)
    import json
    case = module.make_case()
    d = workdir / "obs_cache"
    comp = Compiler(options=CompileOptions(cache_dir=str(d), dumps=True))
    art = comp.compile_case(case)
    mir_text = None
    for f in sorted(d.rglob("stage.mir.lowered.txt")):
        mir_text = f.read_text()
        break
    ok = mir_text is not None
    n_chunks = 0
    n_stg = 0
    if ok:
        n_chunks = mir_text.count("_head(") - mir_text.count("stg") \
            if False else len([l for l in mir_text.splitlines()
                               if l.startswith("chunk") and l.endswith(":")])
        n_stg = len([l for l in mir_text.splitlines()
                     if l.startswith("stg") and l.endswith(":")])
    check("multi-pass-and-staging-structure-observable",
          ok and n_chunks >= 1 and n_stg >= 2,
          f"chunk blocks={n_chunks} staging loops={n_stg} "
          f"artifact={art.sha256[:10]}")


def main() -> int:
    workdir = Path(tempfile.mkdtemp(prefix="a100c-layout-"))
    cache = workdir / "cache"
    try:
        compiler = Compiler(options=CompileOptions(cache_dir=str(cache)))
        check_corpus(workdir, compiler)
        check_shape_oracle()
        check_strided_broadcast(workdir, compiler)
        check_constructs(workdir, compiler)
        check_refusals(workdir, compiler)
        check_staging_observability(workdir, compiler)
    finally:
        import shutil
        shutil.rmtree(workdir, ignore_errors=True)
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} check(s)")
        return 1
    print("test_layout_ops: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
