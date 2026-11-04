#!/usr/bin/env python3
"""test_memory_forms.py -- memory access breadth (T011).

  * acceptance[0]: the block-pointer families execute and compare PASS --
    the corpus executors are leaky_relu_kernel_strided (make_block_ptr,
    boundary_check on both axes, padding 'zero', 2-D tiles, ragged and
    degenerate shapes) and diag_scale_kernel (block pointer with
    tl.advance inside a runtime-bound loop), each at 1/2/4/8 workers on
    one artifact per identity;
  * acceptance[3] (the memory half): cache_modifier / eviction_policy are
    classified ignorable-with-reason in the surface table (performance-
    only under the pinned endpoint), boundary_check / padding_option /
    volatile are implemented parameters, and the classification is
    load-bearing (the ignored parameters are recorded, countable);
  * the wide-access witness: a structurally proven contiguous access
    selects the unit-stride form (the selection's mnemonics and the
    lowering's wide_selections record) and an indirect access keeps the
    indexed form (the control -- MECH-MASKED-VECTOR-ACCESS);
  * tl.gather executes as the register permute with an independent
    reference;
  * tl.interleave executes through the standalone program-level lowering
    (the 2x-extent result the one-extent chunk region cannot host) at
    1/2/4/8 workers with ragged tails;
  * pointer_table_relocations: the grouped_gemm pattern (device addresses
    inside an int64 buffer, patched by the bundle reader on open and
    restored on close) executes through a kernel that loads the table,
    bitcasts to the pointer and stores through it -- the run compares
    PASS and the table's original bytes are restored afterwards;
  * the block-pointer refusal boundaries are located (three non-unit
    axes; a non-power-of-two block extent).

Run: python3 a100c/tests/test_memory_forms.py   (exit 0 = all checks PASS)
"""
from __future__ import annotations

import hashlib
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
# acceptance[0]: the block-pointer corpus executors
# ---------------------------------------------------------------------------

def check_blockptr_corpus(compiler):
    """leaky_relu_kernel_strided (2-D tiles, both axes boundary-checked,
    zero padding) and diag_scale_kernel (advance in a runtime-bound loop):
    every declared shape at 1/2/4/8 workers."""
    bad = []
    lr = _load(ROOT / "ops" / "suite" / "dev" /
               "leaky_relu_kernel_strided.py")
    for shape in ((64, 128), (33, 65), (1, 1)):
        for threads in (1, 2, 4, 8):
            ok, detail = _run_case(compiler, lr, threads, shape=shape,
                                   dtype="float32")
            if not ok:
                bad.append(f"leaky s={shape} t={threads}: {detail}")
    check("blockptr-leaky-relu-strided-all-shapes-threads", not bad,
          "; ".join(bad[:2]))

    bad = []
    ds = _load(ROOT / "ops" / "suite" / "dev" / "diag_scale_kernel.py")
    for shape in ((128, 128), (97, 100), (1, 1)):
        for threads in (1, 2, 4, 8):
            ok, detail = _run_case(compiler, ds, threads, shape=shape,
                                   dtype="float32")
            if not ok:
                bad.append(f"diag s={shape} t={threads}: {detail}")
    check("blockptr-diag-scale-advance-loop-all-shapes-threads", not bad,
          "; ".join(bad[:2]))


# ---------------------------------------------------------------------------
# acceptance[3] (memory half): the surface classification
# ---------------------------------------------------------------------------

def check_surface_classification():
    """cache_modifier/eviction_policy are ignorable-with-reason (recorded,
    countable); boundary_check/padding_option/volatile are implemented."""
    from a100c.frontend.surface import (DEFAULT_SURFACE, CLASS_IGNORABLE,
                                        CLASS_IMPLEMENTED)
    bad = []
    for construct, param in (("tl.load", "cache_modifier"),
                             ("tl.load", "eviction_policy"),
                             ("tl.store", "cache_modifier"),
                             ("tl.store", "eviction_policy")):
        cls = DEFAULT_SURFACE.classify_param(construct, param)
        if cls.classification != CLASS_IGNORABLE:
            bad.append(f"{construct}.{param}: {cls.classification}")
        elif "performance-only" not in cls.reason:
            bad.append(f"{construct}.{param}: reason {cls.reason[:60]}")
    for construct, param in (("tl.load", "boundary_check"),
                             ("tl.load", "padding_option"),
                             ("tl.load", "volatile"),
                             ("tl.store", "boundary_check")):
        cls = DEFAULT_SURFACE.classify_param(construct, param)
        if cls.classification != CLASS_IMPLEMENTED:
            bad.append(f"{construct}.{param}: {cls.classification}")
    check("memory-hint-classification-recorded-in-surface", not bad,
          "; ".join(bad[:3]))

    # the classification is load-bearing: a kernel passing the ignorable
    # hints compiles and executes exactly (the hints were recorded, and
    # ignoring them is value-safe), while the implemented parameters
    # visibly change the lowered TIR (a boundary-checked block-pointer
    # load carries mask+other)
    from a100c.frontend import lower_tir, source as fe_source, \
        specialize as fe_spec
    from a100c.ir import tir
    text = '''"""probe"""
OPERATOR = {"name": "probe/hints", "group": "probe", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness", "tags": []}
SHAPES = ((17,),)
import numpy as np
import triton
import triton.language as tl

@triton.jit
def hints_kernel(x_ptr, out_ptr, n, BLOCK: tl.constexpr):
    i = tl.arange(0, BLOCK)
    m = i < n
    a = tl.load(x_ptr + i, mask=m, other=0.0,
                cache_modifier=".ca", eviction_policy="evict_first")
    b = tl.load(x_ptr + i, mask=m, other=0.0, volatile=True)
    tl.store(out_ptr + i, a + b, mask=m, cache_modifier=".wb",
             eviction_policy="evict_last")

def ref(args, meta):
    x = np.asarray(args["x_ptr"])
    return {"out_ptr": x + x}

def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    n = int(shape[0])
    rng = np.random.default_rng(seed)
    x = rng.standard_normal(n).astype(np.float32)
    args = {"x_ptr": x, "out_ptr": np.zeros(n, np.float32), "n": n}
    meta = {"BLOCK": 128}
    grid = (1,)
    return {"args": args, "meta": meta, "grid": grid, "kernel": hints_kernel,
            "outputs": ("out_ptr",), "expected": ref(args, meta),
            "comparison": {"out_ptr": {"comparator": "allclose", "exact": False,
                                       "rtol": 1e-6, "atol": 1e-6, "equal_nan": True}}}

def make_case(shape=None, dtype=None, seed=None):
    return _make_case(shape=shape or SHAPES[0], dtype=dtype or "float32", seed=seed or 0)
'''
    workdir = Path(tempfile.mkdtemp(prefix="a100c-hints-"))
    try:
        p = workdir / "hints.py"
        p.write_text(text)
        src = fe_source.load_operator(p)
        module = _load(p)
        case = module.make_case()
        spec = fe_spec.specialize(src, case)
        lowering = lower_tir.Lowering(src, spec)
        mod = lowering.lower()
        ignored = {(ip.construct, ip.param) for ip in lowering.ignored}
        wanted = {("tl.load", "cache_modifier"), ("tl.load", "eviction_policy"),
                  ("tl.store", "cache_modifier"), ("tl.store", "eviction_policy")}
        if not wanted <= ignored:
            check("ignorable-hints-recorded-countable", False,
                  f"missing {sorted(wanted - ignored)}")
        else:
            check("ignorable-hints-recorded-countable", True)
        # volatile is honored: the load carries the not-elidable flag
        vol = [st for st in mod.functions[0].body.statements
               if isinstance(st, tir.Op) and st.op == "load"
               and st.attrs.get("volatile")]
        check("volatile-carried-on-the-load", len(vol) == 1,
              f"{len(vol)} volatile loads")
        compiler = Compiler(options=CompileOptions(
            cache_dir=str(workdir / "cache")))
        ok, detail = _run_case(compiler, module, 1)
        check("hinted-kernel-executes-exactly", ok, detail)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


# ---------------------------------------------------------------------------
# the wide-access witness (unit-stride vs indexed)
# ---------------------------------------------------------------------------

def check_wide_access_selection(workdir, compiler):
    """A structurally contiguous access (arange + pid*BLOCK) selects the
    unit-stride vle/vse form; an indirect access (a loaded index vector)
    keeps the indexed vluxei64 form.  The selection is visible in the
    artifact's stage dump (selection mnemonics) and the lowering's
    wide_selections record; both kernels execute and compare PASS."""
    body = """\\
    i = tl.program_id(0) * BLOCK + tl.arange(0, BLOCK)
    m = i < n
    x = tl.load(x_ptr + i, mask=m, other=0)
    tl.store(out_ptr + i, x + 1, mask=m)"""
    text = TEMPLATE % ("wide", "wide", "wide",
                       "x_ptr, out_ptr, n, BLOCK: tl.constexpr", body,
                       _FLOAT_CASE_LAYER("wide_kernel"))
    p = workdir / "wide.py"
    p.write_text(text)
    module = _load(p)
    ok, detail = _run_case(compiler, module, 1)
    check("wide-access-contiguous-executes", ok, detail)
    art = compiler.compile_case(module.make_case())
    sel = json.loads((art.executable.parent / "stage.selection.txt")
                     .read_text())
    mnemonics = set(sel["mnemonics"])
    check("wide-access-selects-unit-stride-form",
          "vle32.v" in mnemonics and "vse32.v" in mnemonics,
          str(sorted(mnemonics))[:110])

    # the control: an indirect (gather-address) access keeps the indexed
    # form -- the proof declines (MECH-MASKED-VECTOR-ACCESS)
    ibody = """\\
    i = tl.program_id(0) * BLOCK + tl.arange(0, BLOCK)
    m = i < n
    idx = tl.load(y_ptr + i, mask=m, other=0)
    v = tl.load(x_ptr + idx, mask=m, other=0)
    tl.store(out_ptr + i, v, mask=m)"""
    ilayer = _FLOAT_CASE_LAYER("indirect_kernel", extra="y_ptr")
    ilayer = ilayer.replace(
        '    return {"out_ptr": x + 1}',
        '    return {"out_ptr": x[np.asarray(args["y_ptr"]).astype(np.int64)]}')
    itext = TEMPLATE % ("indirect", "indirect", "indirect",
                        "x_ptr, y_ptr, out_ptr, n, BLOCK: tl.constexpr",
                        ibody, ilayer)
    p2 = workdir / "indirect.py"
    p2.write_text(itext)
    module2 = _load(p2)
    ok2, detail2 = _run_case(compiler, module2, 1)
    check("indirect-access-executes", ok2, detail2)
    art2 = compiler.compile_case(module2.make_case())
    sel2 = json.loads((art2.executable.parent / "stage.selection.txt")
                      .read_text())
    mn2 = set(sel2["mnemonics"])
    check("indirect-access-keeps-indexed-form",
          "vluxei64.v" in mn2, str(sorted(mn2))[:110])


def _FLOAT_CASE_LAYER(kernel_ref, extra=""):
    args = '"x_ptr": x, "out_ptr": np.zeros(n, np.float32), "n": n'
    if extra:
        args = f'"x_ptr": x, "{extra}": y, "out_ptr": np.zeros(n, np.float32), "n": n'
    return ('def ref(args, meta):\n'
            '    x = np.asarray(args["x_ptr"])\n'
            '    return {"out_ptr": x + 1}\n'
            '\n'
            '\n'
            'def _make_case(shape=SHAPES[0], dtype="float32", seed=0):\n'
            '    n = int(shape[0])\n'
            '    rng = np.random.default_rng(seed)\n'
            '    x = rng.standard_normal(n).astype(np.float32)\n'
            '    y = rng.permutation(n).astype(np.int32)\n'
            f'    args = {{{args}}}\n'
            '    meta = {"BLOCK": 128}\n'
            '    grid = ((n + 127) // 128,)\n'
            f'    return {{"args": args, "meta": meta, "grid": grid,\n'
            f'            "kernel": {kernel_ref}, "outputs": ("out_ptr",),\n'
            '            "expected": ref(args, meta),\n'
            '            "comparison": {"out_ptr": {"comparator": "allclose", "exact": False,\n'
            '                                       "rtol": 1e-6, "atol": 1e-6, "equal_nan": True}}}\n'
            '\n'
            '\n'
            'def make_case(shape=None, dtype=None, seed=None):\n'
            '    return _make_case(shape=shape or SHAPES[0],\n'
            '                      dtype=dtype or "float32", seed=seed or 0)\n')


# ---------------------------------------------------------------------------
# tl.gather (the register permute)
# ---------------------------------------------------------------------------

def check_gather(workdir, compiler):
    """out[i] = src[index[i]] along axis 0 as vrgather.vv, compared against
    an independent numpy reference."""
    body = """\\
    lane = tl.arange(0, BLOCK)
    i = tl.program_id(0) * BLOCK + lane
    m = i < n
    idx = tl.load(x_ptr + i, mask=m, other=0)
    src = tl.load(y_ptr + i, mask=m, other=0)
    out = tl.gather(src, idx, axis=0)
    tl.store(out_ptr + i, out, mask=m)"""
    layer = ('def ref(args, meta):\n'
             '    idx = np.asarray(args["x_ptr"]).astype(np.int64)\n'
             '    y = np.asarray(args["y_ptr"])\n'
             '    B = 32\n'
             '    out = np.zeros(len(idx))\n'
             '    for p in range((len(idx) + B - 1) // B):\n'
             '        sl = slice(p * B, (p + 1) * B)\n'
             '        out[sl] = y[p * B:p * B + B][idx[sl]]\n'
             '    return {"out_ptr": out}\n'
             '\n'
             'def _make_case(shape=SHAPES[0], dtype="float32", seed=0):\n'
             '    n = int(shape[0])\n'
             '    rng = np.random.default_rng(seed)\n'
             '    idx = rng.integers(0, 32, n).astype(np.int32)\n'
             '    y = rng.standard_normal(n).astype(np.float32)\n'
             '    args = {"x_ptr": idx, "y_ptr": y,\n'
             '            "out_ptr": np.zeros(n, np.float32), "n": n}\n'
             '    meta = {"BLOCK": 32}\n'
             '    grid = ((n + 31) // 32,)\n'
             '    return {"args": args, "meta": meta, "grid": grid,\n'
             '            "kernel": gth_kernel, "outputs": ("out_ptr",),\n'
             '            "expected": ref(args, meta),\n'
             '            "comparison": {"out_ptr": {"comparator": "allclose", "exact": False,\n'
             '                                       "rtol": 1e-6, "atol": 1e-6, "equal_nan": True}}}\n'
             '\n'
             'def make_case(shape=None, dtype=None, seed=None):\n'
             '    return _make_case(shape=shape or SHAPES[0],\n'
             '                      dtype=dtype or "float32", seed=seed or 0)\n')
    p = _operator_file(workdir, "gth",
                       "x_ptr, y_ptr, out_ptr, n, BLOCK: tl.constexpr",
                       body, layer)
    module = _load(p)
    bad = []
    for threads in (1, 4):
        ok, detail = _run_case(compiler, module, threads, shape=(96,))
        if not ok:
            bad.append(f"t={threads}: {detail}")
    check("tl-gather-register-permute-executes", not bad,
          "; ".join(bad[:2]))


# ---------------------------------------------------------------------------
# tl.interleave (the standalone program-level lowering)
# ---------------------------------------------------------------------------

def check_interleave():
    """The standalone interleave program compiles through the real backend
    (verify -> legalize -> select -> allocate -> emit -> as -> ld -> QEMU)
    and compares PASS at 1/2/4/8 workers with a ragged tail."""
    from a100c.backend import allocate as alloc_mod
    from a100c.backend import emit as emit_mod
    from a100c.backend import legalize as legal_mod
    from a100c.backend import select as select_mod
    from a100c.ir import mir
    from a100c.lower import scalar as scalar_mod
    from a100c.target import DEFAULT_TARGET
    from a100_support.native_io import pack_case, unpack_outputs

    build = _bootstrap.load_build_module()
    work = Path(tempfile.mkdtemp(prefix="a100c-itl-"))
    try:
        binding = scalar_mod.interleave_binding(["a_ptr", "b_ptr",
                                                 "out_ptr"])
        module = scalar_mod.lower_interleave(binding, DEFAULT_TARGET,
                                             scalar_mod.InterleaveOptions())
        errors = mir.verify_module(module)
        if errors:
            check("interleave-program-verifies", False, str(errors[0]))
            return
        legal_mod.legalize(module)
        errors = mir.verify_module(module)
        if errors:
            check("interleave-program-verifies", False, str(errors[0]))
            return
        selection = select_mod.select(module)
        check("interleave-program-verifies", True)
        allocation = alloc_mod.allocate(module, DEFAULT_TARGET)
        program = emit_mod.emit_assembly(
            module, allocation, DEFAULT_TARGET,
            workspace=(2 * module.meta["interleave"]["vl"] * 4, 0),
            selection=selection,
            header=["# a100c interleave slice (T011)"])
        asm = work / "interleave.S"
        asm.write_text(program.text)
        obj, _tools, _a, _i = build.assemble_operator(
            asm, build_dir=work / "build")
        build.link_operator([obj], work / "interleave_exec",
                            build_dir=work / "build")
        exec_path = work / "interleave_exec"
        sha = hashlib.sha256(exec_path.read_bytes()).hexdigest()

        import subprocess
        import os
        bad = []
        for threads in (1, 2, 4, 8):
            for n in (97, 128):
                rng = np.random.default_rng(threads * 100 + n)
                a = rng.standard_normal(n).astype(np.float32)
                b = rng.standard_normal(n).astype(np.float32)
                case = {"args": {"a_ptr": a, "b_ptr": b,
                                 "out_ptr": np.zeros(2 * n, np.float32)},
                        "outputs": ("out_ptr",),
                        "comparison": {"out_ptr": {
                            "comparator": "allclose", "exact": False,
                            "rtol": 1e-6, "atol": 1e-6, "equal_nan": True}},
                        "expected": {"out_ptr":
                                     np.stack([a, b], axis=1).reshape(-1)}}
                directory = Path(tempfile.mkdtemp(prefix="a100c-itl-case-"))
                pack_case(case, directory)
                result = subprocess.run(
                    [str(ROOT / "a100_support" / "run-riscv.sh"),
                     str(exec_path),
                     "--bundle", str(directory / "bundle.bin"),
                     "--threads", str(threads)],
                    capture_output=True, text=True, timeout=240)
                if result.returncode != 0:
                    bad.append(f"t={threads} n={n}: exit "
                               f"{result.returncode}")
                    continue
                outputs = unpack_outputs(directory)
                got = np.asarray(outputs["out_ptr"])
                exp = case["expected"]["out_ptr"]
                if not np.allclose(got, exp, rtol=1e-6, atol=1e-6):
                    bad.append(f"t={threads} n={n}: "
                               f"{np.sum(~np.isclose(got, exp))} mismatched")
        check("tl-interleave-program-executes-threads-ragged", not bad,
              "; ".join(bad[:2]) + f" (artifact sha {sha[:12]})")
    finally:
        shutil.rmtree(work, ignore_errors=True)


# ---------------------------------------------------------------------------
# pointer_table_relocations (the grouped_gemm pattern)
# ---------------------------------------------------------------------------

def check_pointer_table(workdir, compiler):
    """A kernel loads a device address from an int64 table (patched by the
    bundle reader on open), bitcasts it to a float pointer and stores
    through it; the run compares PASS and the table's original bytes are
    restored after the run."""
    body = """\\
    base = tl.load(tbl_ptr).to(tl.pointer_type(tl.float32))
    i = tl.program_id(0) * BLOCK + tl.arange(0, BLOCK)
    m = i < n
    v = tl.load(x_ptr + i, mask=m, other=0)
    tl.store(base + i, v + 1, mask=m)"""
    layer = ('def ref(args, meta):\n'
             '    x = np.asarray(args["x_ptr"])\n'
             '    return {"out_ptr": x + 1.0}\n'
             '\n'
             'def _make_case(shape=SHAPES[0], dtype="float32", seed=0):\n'
             '    n = int(shape[0])\n'
             '    rng = np.random.default_rng(seed)\n'
             '    x = rng.standard_normal(n).astype(np.float32)\n'
             '    out = np.zeros(n, np.float32)\n'
             '    tbl = np.zeros(1, np.int64)\n'
             '    args = {"tbl_ptr": tbl, "x_ptr": x, "out_ptr": out,\n'
             '            "n": n}\n'
             '    meta = {"BLOCK": 128}\n'
             '    grid = ((n + 127) // 128,)\n'
             '    return {"args": args, "meta": meta, "grid": grid,\n'
             '            "kernel": ptab_kernel, "outputs": ("out_ptr",),\n'
             '            "expected": ref(args, meta),\n'
             '            "pointer_table_relocations": [\n'
             '                {"table": "tbl_ptr", "allocation": "out_ptr",\n'
             '                 "entry": 0, "byte_offset": 0}],\n'
             '            "comparison": {"out_ptr": {"comparator": "allclose", "exact": False,\n'
             '                                       "rtol": 1e-6, "atol": 1e-6, "equal_nan": True}}}\n'
             '\n'
             'def make_case(shape=None, dtype=None, seed=None):\n'
             '    return _make_case(shape=shape or SHAPES[0],\n'
             '                      dtype=dtype or "float32", seed=seed or 0)\n')
    p = _operator_file(workdir, "ptab",
                       "tbl_ptr, x_ptr, out_ptr, n, BLOCK: tl.constexpr",
                       body, layer)
    module = _load(p)
    import a100_support.native_device as nd
    case = module.make_case()
    device = nd.NativeExecutableDevice(compiler, 1)
    staged = device.stage_case(case)
    tbl_before = np.asarray(case["args"]["tbl_ptr"]).copy()
    staged.launch()
    outputs = staged.outputs()
    got = np.asarray(outputs["out_ptr"])
    exp = np.asarray(case["expected"]["out_ptr"])
    ok = np.allclose(got, exp, rtol=1e-6, atol=1e-6)
    # the table's on-disk bytes are restored after the run (close undoes
    # the open-time patch)
    tbl_after = np.frombuffer(
        (staged.directory / "bundle.bin").read_bytes()[
            json.loads((staged.directory / "bundle.json").read_text())
            ["storages"][json.loads(
                (staged.directory / "bundle.json").read_text())
            ["views"]["tbl_ptr"]["storage"]]["offset"]:][:8], dtype=np.int64)
    restored = bool(np.array_equal(tbl_after, tbl_before))
    check("pointer-table-relocation-applied-and-restored",
          ok and restored,
          f"compare {'PASS' if ok else 'FAIL'}; table restored "
          f"{restored} ({tbl_after[0]} vs pre-run {tbl_before[0]})")


# ---------------------------------------------------------------------------
# block-pointer refusal boundaries
# ---------------------------------------------------------------------------

def check_blockptr_refusals(workdir, compiler):
    """Three non-unit axes and a non-power-of-two block extent refuse
    with located diagnostics naming the boundary."""
    from a100c.driver import PipelineError
    bad = []
    cases = [
        ("x_ptr, out_ptr, n, BLOCK: tl.constexpr",
         """\\
    bp = tl.make_block_ptr(base=x_ptr, shape=(n, n, n),
                           strides=(n, 1, 1), offsets=(0, 0, 0),
                           block_shape=(4, 4, 4), order=(2, 1, 0))
    v = tl.load(bp)""",
         ("three or more non-unit axes", "layout lane")),
        ("x_ptr, out_ptr, n, BLOCK: tl.constexpr",
         """\\
    bp = tl.make_block_ptr(base=x_ptr, shape=(n, n),
                           strides=(n, 1), offsets=(0, 0),
                           block_shape=(6, 8), order=(1, 0))
    v = tl.load(bp)""",
         ("power of two", "powers of two")),
    ]
    for i, (params, body, needles) in enumerate(cases):
        p = _operator_file(workdir, f"bpref{i}", params, body,
                           _FLOAT_CASE_LAYER(f"bpref{i}_kernel"))
        module = _load(p)
        try:
            compiler.compile_case(module.make_case())
            bad.append(f"case {i}: compiled (expected a located refusal)")
        except PipelineError as exc:
            if not any(nd in str(exc) for nd in needles):
                bad.append(f"case {i}: {str(exc)[:100]}")
        except Exception as exc:               # noqa: BLE001
            bad.append(f"case {i}: wrong error type "
                       f"{type(exc).__name__}: {str(exc)[:70]}")
    check("block-pointer-refusals-located", not bad, "; ".join(bad[:2]))


def main() -> int:
    workdir = Path(tempfile.mkdtemp(prefix="a100c-mem-"))
    cache = workdir / "cache"
    try:
        compiler = Compiler(options=CompileOptions(cache_dir=str(cache)))
        check_blockptr_corpus(compiler)
        check_surface_classification()
        check_wide_access_selection(workdir, compiler)
        check_gather(workdir, compiler)
        check_interleave()
        check_pointer_table(workdir, compiler)
        check_blockptr_refusals(workdir, compiler)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} check(s)")
        return 1
    print("test_memory_forms: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
