#!/usr/bin/env python3
"""test_atomics.py -- the atomic core (T011).

  * acceptance[1]: the atomic families execute and compare PASS --
    atomic_bitmap (all eight operators in one kernel: add/max/min/xchg/
    and/or/xor/cas, the debug_barrier, the power-of-two remainder fold),
    count_nonzero_kernel_1 and bincount_kernel (multi-worker
    cross-program accumulation on one artifact at 1/2/4/8 threads --
    every program's atomic contribution must land exactly once),
    scatter_atomic_kernel (the fp32 synthesis: the lr/sc pair on the raw
    bits), and a scalar fp32 atomic_min equivalent form (the
    min_reduce_lastdim_partials construct; that corpus operator itself
    refuses at the grid model -- a constexpr-typed shape scalar no
    bundle-visible quantity can tie, an unrelated located boundary);
  * acceptance[1] (pointer table): the grouped_gemm pointer-table pattern
    is test_memory_forms' check (the relocation applied-and-restored
    witness); grouped_gemm_kernel itself refuses located on its
    out-of-slice parts (dot/bf16) -- verified here as the honest
    boundary;
  * acceptance[2]: the guard-region witness -- a masked block atomic
    whose disabled lanes address a poisoned guard region behind the
    output buffer leaves the guard intact in the real build, and the
    degraded build (witness_drop_atomic_masks: the disabled-lane address
    redirection removed, a separate artifact identity) corrupts it (the
    check can fail);
  * acceptance[3]: the sem/scope mapping is declared and legal -- every
    (sem, scope) pair of the declared table emits the ordered/fenced form
    the scope requires (the .aq/.rl/.aqrl suffixes and the scope=sys
    fence), asserted on the emitted assembly of equivalent-form kernels;
    the unsigned min/max forms select their u rows from the pointee's own
    signedness.

Run: python3 a100c/tests/test_atomics.py   (exit 0 = all checks PASS)
"""
from __future__ import annotations

import importlib.util
import json
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
          f"{(' | ' + detail) if detail else ''}")
    if not ok:
        FAILURES.append(name)
    return ok


import numpy as np  # noqa: E402

from a100c.driver import Compiler, CompileOptions, PipelineError  # noqa: E402

TEMPLATE = ('"""probe operator %s"""\n'
            'OPERATOR = {"name": "probe/%s", "group": "probe", "channel": "local",\n'
            '            "execution": "triton_kernel", "verification": "correctness",\n'
            '            "tags": []}\n'
            'SHAPES = ((257,),)\n'
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
            detail = f"{name}: {np.sum(got != exp)} mismatched elements"
        ok &= same
    return ok, detail


# ---------------------------------------------------------------------------
# acceptance[1]: the corpus executors
# ---------------------------------------------------------------------------

def check_corpus_atomics(compiler):
    bad = []
    ab = _load(ROOT / "ops" / "suite" / "dev" / "atomic_bitmap.py")
    for threads in (1, 2, 4, 8):
        ok, detail = _run_case(compiler, ab, threads)
        if not ok:
            bad.append(f"atomic_bitmap t={threads}: {detail}")
    check("atomic-bitmap-all-eight-ops-threads", not bad,
          "; ".join(bad[:2]))

    bad = []
    cn = _load(ROOT / "ops" / "suite" / "dev" / "count_nonzero_kernel_1.py")
    for shape in ((17,), (97,)):
        for threads in (1, 2, 4, 8):
            ok, detail = _run_case(compiler, cn, threads, shape=shape,
                                   dtype="float32")
            if not ok:
                bad.append(f"count_nonzero s={shape} t={threads}: {detail}")
    check("atomic-add-cross-program-accumulation-threads", not bad,
          "; ".join(bad[:2]))

    bad = []
    bc = _load(ROOT / "ops" / "suite" / "dev" / "bincount_kernel.py")
    for shape in ((17, 7), (97, 33)):
        for threads in (1, 2, 4, 8):
            ok, detail = _run_case(compiler, bc, threads, shape=shape)
            if not ok:
                bad.append(f"bincount s={shape} t={threads}: {detail}")
    check("atomic-add-block-masked-threads", not bad, "; ".join(bad[:2]))

    bad = []
    sc = _load(ROOT / "ops" / "suite" / "dev" / "scatter_atomic_kernel.py")
    for threads in (1, 2, 4, 8):
        ok, detail = _run_case(compiler, sc, threads)
        if not ok:
            bad.append(f"scatter t={threads}: {detail}")
    check("atomic-add-fp32-synthesis-scatter-threads", not bad,
          "; ".join(bad[:2]))


def check_scalar_fp_min(workdir, compiler):
    """The scalar fp32 atomic_min construct (min_reduce_lastdim's), on an
    equivalent form whose grid ties to runtime scalars."""
    body = """\\
    row = tl.program_id(0)
    i = tl.arange(0, BLOCK)
    m = i < n
    x = tl.load(x_ptr + row * n + i, mask=m, other=float('inf'))
    v = tl.min(x, axis=0)
    tl.atomic_min(out_ptr + row, v)"""
    layer = ('import numpy as np\n'
             'def ref(args, meta):\n'
             '    x = np.asarray(args["x_ptr"]).reshape(meta["rows"], meta["n"])\n'
             '    return {"out_ptr": x.min(axis=1)}\n'
             '\n'
             'def _make_case(shape=(8, 97), dtype="float32", seed=0):\n'
             '    rows, n = int(shape[0]), int(shape[1])\n'
             '    rng = np.random.default_rng(seed)\n'
             '    x = rng.standard_normal((rows, n)).astype(np.float32)\n'
             '    args = {"x_ptr": x.reshape(-1),\n'
             '            "out_ptr": np.full(rows, np.inf, np.float32),\n'
             '            "n": n}\n'
             '    meta = {"BLOCK": 128, "rows": rows, "n": n}\n'
             '    grid = (rows, (n + 127) // 128)\n'
             '    return {"args": args, "meta": meta, "grid": grid,\n'
             '            "shape": (rows, n),\n'
             '            "kernel": sfmin_kernel, "outputs": ("out_ptr",),\n'
             '            "expected": ref(args, meta),\n'
             '            "comparison": {"out_ptr": {"comparator": "allclose", "exact": False,\n'
             '                                       "rtol": 1e-6, "atol": 1e-6, "equal_nan": True}}}\n'
             '\n'
             'def make_case(shape=None, dtype=None, seed=None):\n'
             '    return _make_case(shape=shape or (8, 97),\n'
             '                      dtype=dtype or "float32", seed=seed or 0)\n')
    p = _operator_file(workdir, "sfmin",
                       "x_ptr, out_ptr, n, BLOCK: tl.constexpr",
                       body, layer)
    module = _load(p)
    bad = []
    for threads in (1, 4, 8):
        ok, detail = _run_case(compiler, module, threads)
        if not ok:
            bad.append(f"t={threads}: {detail}")
    check("atomic-min-fp32-scalar-synthesis-threads", not bad,
          "; ".join(bad[:2]))


def check_grouped_gemm_boundary(compiler):
    """grouped_gemm_kernel refuses located on its out-of-slice parts --
    never a silent miscompile; its pointer-table pattern is
    test_memory_forms' executed check.

    T034: the two-axis block-pointer tile now lowers through the dot
    lane (the rank-1 flattening repair), so the located refusal the
    boundary test pins moved past the dot/bf16 parts to the GRID model:
    the tile-count sum runs over a symbolic-bound range the expression
    language cannot carry (``sum(ceil_div(m, BM) * ceil_div(n, BN) for
    (m, n, k) in dimensions)`` over ``range(groups)`` with groups a
    symbolic shape extent) -- still located, still never a guess."""
    gg = _load(ROOT / "ops" / "suite" / "dev" / "grouped_gemm_kernel.py")
    try:
        compiler.compile_case(gg.make_case())
        check("grouped-gemm-refuses-located-out-of-slice", False,
              "compiled (expected a located refusal)")
    except PipelineError as exc:
        needles = ("dot", "width", "SEW", "matrix", "bf16", "bfloat16",
                   "and/or", "not supported",
                   # T034: the moved boundary (the grid tie)
                   "grid")
        check("grouped-gemm-refuses-located-out-of-slice",
              any(n in str(exc) for n in needles), str(exc)[:110])
    except Exception as exc:               # noqa: BLE001
        check("grouped-gemm-refuses-located-out-of-slice", False,
              f"wrong error type {type(exc).__name__}: {str(exc)[:80]}")


# ---------------------------------------------------------------------------
# acceptance[2]: the guard-region witness
# ---------------------------------------------------------------------------

GUARD_BYTES = 256
POISON_U32 = 0xDA5A5A5A

GUARD_BODY = """\\
    i = tl.arange(0, BLOCK)
    m = i < n
    tl.atomic_add(out_ptr + i, 1, mask=m)"""

_GUARD_LAYER = ('import numpy as np\n'
                'def ref(args, meta):\n'
                '    out = np.asarray(args["out_ptr"]).copy()\n'
                '    n = int(args["n"])\n'
                '    out[:n] = out[:n] + 1\n'
                '    return {"out_ptr": out}\n'
                '\n'
                'def _make_case(shape=(33,), dtype="int32", seed=0):\n'
                '    n = int(shape[0])\n'
                '    args = {"out_ptr": np.zeros(n, np.int32), "n": n}\n'
                '    meta = {"BLOCK": 128}\n'
                '    grid = (1,)\n'
                '    return {"args": args, "meta": meta, "grid": grid,\n'
                '            "kernel": gwit_kernel, "outputs": ("out_ptr",),\n'
                '            "expected": ref(args, meta),\n'
                '            "comparison": {"out_ptr": {"comparator": "array_equal",\n'
                '                                       "exact": True}}}\n'
                '\n'
                'def make_case(shape=None, dtype=None, seed=None):\n'
                '    return _make_case(shape=shape or (33,),\n'
                '                      dtype=dtype or "int32", seed=seed or 0)\n')


def _guard_case(directory: Path):
    """The guard case: a 33-int output row followed in the bundle by a
    256-byte poison guard.  The 128-lane block's disabled lanes (33..127)
    address output bytes 132..511 -- the row padding plus the guard -- so
    an atomic that fires there corrupts the poison."""
    p = _operator_file(directory, "gwit",
                       "out_ptr, n, BLOCK: tl.constexpr",
                       GUARD_BODY, _GUARD_LAYER)
    module = _load(p)
    case = module.make_case()
    args = dict(case["args"])
    guard = np.frombuffer(
        np.array([POISON_U32], dtype="<u4").tobytes()
        * (GUARD_BYTES // 4), dtype=np.uint8)
    args["z_guard"] = guard
    case = dict(case)
    case["args"] = args
    case["pointer_dtypes"] = dict(case.get("pointer_dtypes") or {})
    case["pointer_dtypes"]["z_guard"] = "uint8"
    return case


def _guard_span(staged):
    info = json.loads((staged.directory / "bundle.json").read_text())
    out_view = info["views"]["out_ptr"]
    out_row = info["storages"][out_view["storage"]]
    guard_view = info["views"]["z_guard"]
    guard_row = info["storages"][guard_view["storage"]]
    image = (staged.directory / "bundle.bin").read_bytes()
    tail_end = 128 * 4
    span = image[guard_row["offset"]:
                 guard_row["offset"] + max(0, tail_end - out_row["size"])]
    return bytes(span), out_row, guard_row


def check_guard_witness(workdir):
    """acceptance[2]: the masked block atomic performs no access at its
    disabled positions.  The real build leaves the poisoned guard behind
    the output row intact (and compares PASS); the degraded build (the
    compile option ``witness_drop_atomic_masks``: the disabled-lane
    address redirection removed, a separate artifact identity) lets the
    disabled lanes fire at their out-of-range addresses and corrupts the
    poison -- the witness can fail, so the property is load-bearing."""
    import a100_support.native_device as nd
    realdir = workdir / "gwit-real"
    realdir.mkdir(parents=True, exist_ok=True)
    case = _guard_case(realdir)

    real = Compiler(options=CompileOptions(
        cache_dir=str(workdir / "real")))
    device = nd.NativeExecutableDevice(real, 1)
    staged = device.stage_case(case)
    staged.launch()
    outputs = staged.outputs()
    cmp_ok = np.array_equal(np.asarray(outputs["out_ptr"]),
                            np.asarray(case["expected"]["out_ptr"]))
    span, out_row, guard_row = _guard_span(staged)
    expected_span = bytes(np.array([POISON_U32], dtype="<u4").tobytes()
                          * (len(span) // 4))
    guard_ok = span == expected_span
    check("guard-region-real-build-intact", cmp_ok and guard_ok,
          f"compare {'PASS' if cmp_ok else 'FAIL'}; guard "
          f"{'intact' if guard_ok else 'corrupted'} "
          f"(out row {out_row['size']}B, guard at "
          f"+{guard_row['offset'] - out_row['offset']})")

    degradedir = workdir / "gwit-degraded"
    degradedir.mkdir(parents=True, exist_ok=True)
    case2 = _guard_case(degradedir)
    degraded = Compiler(options=CompileOptions(
        cache_dir=str(workdir / "degraded"),
        witness_drop_atomic_masks=True))
    try:
        device2 = nd.NativeExecutableDevice(degraded, 1)
        staged2 = device2.stage_case(case2)
        staged2.launch()
        span2, _o, _g = _guard_span(staged2)
        witness_corrupted = span2 != expected_span
        check("guard-region-witness-degraded-build-corrupts",
              witness_corrupted,
              "the degraded build left the guard intact -- the no-access "
              "property is NOT load-bearing (the check cannot fail)"
              if not witness_corrupted else
              f"corrupted as required ({span2[:8].hex()} != "
              f"{expected_span[:8].hex()})")
    except Exception as exc:               # noqa: BLE001
        # a crash or transport failure of the degraded build is also a
        # failing witness
        check("guard-region-witness-degraded-build-corrupts", True,
              f"degraded run failed as required ({type(exc).__name__})")


# ---------------------------------------------------------------------------
# acceptance[3]: the sem/scope mapping (declared and legal)
# ---------------------------------------------------------------------------

def check_sem_scope_mapping(workdir, compiler):
    """The declared ATOMIC_ORDERING table: every (sem, scope) pair emits
    the ordered/fenced form its scope requires, asserted on the emitted
    assembly of equivalent-form kernels (one scalar atomic each); the
    default (no explicit sem/scope) is acq_rel/gpu; the unsigned min/max
    select their u rows from the pointee's signedness."""
    from a100c.lower.scalar import ATOMIC_ORDERING, ATOMIC_SEMS, \
        ATOMIC_SCOPES
    bad = []
    for sem in ATOMIC_SEMS:
        for scope in ATOMIC_SCOPES:
            o = ATOMIC_ORDERING[(sem, scope)]
            sfx = (".aqrl" if o.aq and o.rl else ".aq" if o.aq
                   else ".rl" if o.rl else "")
            kname = f"sem_{sem.replace('_', '')}_{scope}_kernel"
            body = f"""\\
    i = tl.arange(0, BLOCK)
    m = i < n
    tl.atomic_add(out_ptr + i, 1, mask=m, sem="{sem}", scope="{scope}")"""
            layer = ('def ref(args, meta):\n'
                     '    out = np.asarray(args["out_ptr"]).copy()\n'
                     '    n = int(args["n"])\n'
                     '    out[:n] = out[:n] + 1\n'
                     '    return {"out_ptr": out}\n'
                     '\n'
                     'def _make_case(shape=(17,), dtype="int32", seed=0):\n'
                     '    n = int(shape[0])\n'
                     '    args = {"out_ptr": np.zeros(n, np.int32), "n": n}\n'
                     '    meta = {"BLOCK": 32}\n'
                     '    grid = ((n + 31) // 32,)\n'
                     '    return {"args": args, "meta": meta, "grid": grid,\n'
                     f'            "kernel": {kname}, "outputs": ("out_ptr",),\n'
                     '            "expected": ref(args, meta),\n'
                     '            "comparison": {"out_ptr": {"comparator": "array_equal",\n'
                     '                                       "exact": True}}}\n'
                     '\n'
                     'def make_case(shape=None, dtype=None, seed=None):\n'
                     '    return _make_case(shape=shape or (17,),\n'
                     '                      dtype=dtype or "int32", seed=seed or 0)\n')
            fname = f"sem_{sem.replace('_', '')}_{scope}"
            assert kname == f"{fname}_kernel"
            p = _operator_file(workdir, fname,
                               "out_ptr, n, BLOCK: tl.constexpr", body,
                               layer)
            module = _load(p)
            try:
                art = compiler.compile_case(module.make_case())
                asm = (art.executable.parent / "program.S").read_text()
                want = f"amoadd.w{sfx}"
                if want not in asm:
                    bad.append(f"{sem}/{scope}: no {want}")
                if scope == "sys" and "fence iorw, iorw" not in asm:
                    bad.append(f"{sem}/{scope}: no sys fence")
            except PipelineError as exc:
                bad.append(f"{sem}/{scope}: {str(exc)[:80]}")
    check("sem-scope-mapping-emits-declared-forms", not bad,
          "; ".join(bad[:4]))

    # the default (no explicit sem/scope) is acq_rel/gpu: .aqrl, no fence
    body = """\\
    i = tl.arange(0, BLOCK)
    m = i < n
    tl.atomic_add(out_ptr + i, 1, mask=m)"""
    layer = ('def ref(args, meta):\n'
             '    out = np.asarray(args["out_ptr"]).copy()\n'
             '    n = int(args["n"])\n'
             '    out[:n] = out[:n] + 1\n'
             '    return {"out_ptr": out}\n'
             '\n'
             'def _make_case(shape=(17,), dtype="int32", seed=0):\n'
             '    n = int(shape[0])\n'
             '    args = {"out_ptr": np.zeros(n, np.int32), "n": n}\n'
             '    meta = {"BLOCK": 32}\n'
             '    grid = ((n + 31) // 32,)\n'
             '    return {"args": args, "meta": meta, "grid": grid,\n'
             '            "kernel": dsem_kernel, "outputs": ("out_ptr",),\n'
             '            "expected": ref(args, meta),\n'
             '            "comparison": {"out_ptr": {"comparator": "array_equal",\n'
             '                                       "exact": True}}}\n'
             '\n'
             'def make_case(shape=None, dtype=None, seed=None):\n'
             '    return _make_case(shape=shape or (17,),\n'
             '                      dtype=dtype or "int32", seed=seed or 0)\n')
    p = _operator_file(workdir, "dsem",
                       "out_ptr, n, BLOCK: tl.constexpr", body, layer)
    module = _load(p)
    art = compiler.compile_case(module.make_case())
    asm = (art.executable.parent / "program.S").read_text()
    ok = ("amoadd.w.aqrl" in asm or "amoadd.w.aq" in asm) \
        and "fence iorw, iorw" not in asm.split("amoadd")[0][-200:]
    check("default-sem-scope-acq-rel-gpu", ok,
          "" if ok else "default form not the declared acq_rel/gpu")

    # the unsigned pointee selects the u rows (min on a uint32 buffer)
    ubody = """\\
    i = tl.arange(0, BLOCK)
    m = i < n
    c = tl.load(c_ptr)
    tl.atomic_min(out_ptr + i, c, mask=m)"""
    ulayer = ('def ref(args, meta):\n'
              '    out = np.asarray(args["out_ptr"]).copy()\n'
              '    n = int(args["n"])\n'
              '    out[:n] = np.minimum(out[:n], np.uint32(3))\n'
              '    return {"out_ptr": out}\n'
              '\n'
              'def _make_case(shape=(17,), dtype="uint32", seed=0):\n'
              '    n = int(shape[0])\n'
              '    args = {"out_ptr": np.full(n, 2**32 - 7, np.uint32),\n'
              '            "c_ptr": np.full(1, 3, np.uint32), "n": n}\n'
              '    meta = {"BLOCK": 32}\n'
              '    grid = ((n + 31) // 32,)\n'
              '    return {"args": args, "meta": meta, "grid": grid,\n'
              '            "kernel": umin_kernel, "outputs": ("out_ptr",),\n'
              '            "expected": ref(args, meta),\n'
              '            "pointer_dtypes": {"out_ptr": "uint32"},\n'
              '            "comparison": {"out_ptr": {"comparator": "array_equal",\n'
              '                                       "exact": True}}}\n'
              '\n'
              'def make_case(shape=None, dtype=None, seed=None):\n'
              '    return _make_case(shape=shape or (17,),\n'
              '                      dtype=dtype or "uint32", seed=seed or 0)\n')
    p2 = _operator_file(workdir, "umin",
                        "out_ptr, c_ptr, n, BLOCK: tl.constexpr", ubody,
                        ulayer)
    module2 = _load(p2)
    art2 = compiler.compile_case(module2.make_case())
    asm2 = (art2.executable.parent / "program.S").read_text()
    ok2 = "amominu" in asm2 and "amomin." not in asm2
    # execute: the unsigned min of (2^32-7, 3) = 3
    import a100_support.native_device as nd
    device = nd.NativeExecutableDevice(compiler, 1)
    staged = device.stage_case(module2.make_case())
    staged.launch()
    got = np.asarray(staged.outputs()["out_ptr"])
    ok2 &= bool(np.all(np.asarray(got)[:17] == 3))
    check("unsigned-min-selects-u-row-and-executes", ok2,
          f"amominu {'present' if 'amominu' in asm2 else 'absent'}; "
          f"got {np.ravel(got)[:3]} want 3s")


def main() -> int:
    workdir = Path(tempfile.mkdtemp(prefix="a100c-atm-"))
    cache = workdir / "cache"
    try:
        compiler = Compiler(options=CompileOptions(cache_dir=str(cache)))
        check_corpus_atomics(compiler)
        check_scalar_fp_min(workdir, compiler)
        check_grouped_gemm_boundary(compiler)
        check_guard_witness(workdir)
        check_sem_scope_mapping(workdir, compiler)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} check(s)")
        return 1
    print("test_atomics: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
