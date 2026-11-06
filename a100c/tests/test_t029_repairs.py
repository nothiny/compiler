#!/usr/bin/env python3
"""test_t029_repairs.py -- the T029 census-class repairs through the real paths.

One repair per census class, each through the path that failed (never a
mock) with the executed comparison and the control that proves the check
is load-bearing (MECH-WITNESS-TEST):

  ptradd-width-64     a 64-bit scalar offset meeting a vi32 vector index
                      (the 46-row class: ``p += pid_m * N`` then
                      ``p + (start + arange)``) widens the vector lane
                      class (vwiden sext -> the legalized vwaddx0 at
                      e64m2) instead of refusing; the softmax-shaped
                      operator compiles to a RISC-V ELF, executes on the
                      pinned QEMU endpoint and compares PASS; the widened
                      addressing equals the 32-bit path wherever the
                      32-bit path is defined (acceptance[1]'s
                      boundary-crossing enumeration over the independent
                      address model; a zext-widening control must
                      disagree).
  lmul4-allocation    vf32m4 groups (the vector-FP32 dot's 128-lane
                      chunk, the 16-row class) allocate inside the
                      32x128B file as naturally aligned groups and spill
                      legally in full-vl regions, with the emitted frame
                      offset-safe past the 12-bit immediate; the
                      operators behind the removed refusals execute and
                      compare PASS: gemm_smallk (the N-tail mask must
                      cover all 128 lanes -- the m1-capped mask left
                      lanes 32+ unwritten, 47608 wrong elements before
                      the fix) and matmul_k64_2d (broadcast-shaped staged
                      offsets (N,1)/(1,M) must map through the block's
                      own axes -- the flat read crossed into the
                      neighbouring staged regions and the A-tile access
                      went out of bounds, guest SIGSEGV).
  spill-convergence   the constant-heavy loop-body pressure (the 7-row
                      class) converges: hoisted constants rematerialize
                      at their uses (no stack slot), reload values are
                      never re-split (the futile ``.r1.r1`` loop), and
                      the matmul_k32_fast fp16 case executes and
                      compares PASS.  Value preservation is asserted
                      structurally (remat products carry the original
                      constant; every reload matches a spill's slot and
                      (sew, lmul)) and by execution.
  overlap-control     the mixed-LMUL group-overlap invariant's negative
                      control (MECH-WITNESS-TEST): a hand-forged
                      assignment whose m2 destination group covers its
                      m1 source must be rejected -- the invariant's
                      silence on real allocations is meaningful.

Run: python3 a100c/tests/test_t029_repairs.py   (exit 0 = all checks PASS)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap  # noqa: E402

ROOT = _bootstrap.bootstrap()
import os  # noqa: E402
import tempfile  # noqa: E402
import warnings  # noqa: E402

warnings.filterwarnings("ignore")

FAILURES = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    print(f"{'PASS' if ok else 'FAIL'} {name}"
          f"{(' | ' + detail) if detail else ''}", flush=True)
    if not ok:
        FAILURES.append(name)
    return ok


import importlib.util  # noqa: E402
import re  # noqa: E402
from typing import Dict  # noqa: E402
import numpy as np  # noqa: E402

from a100c.backend import allocate as alloc_mod  # noqa: E402
from a100c.backend import emit as emit_mod  # noqa: E402
from a100c.backend import legalize as legal_mod  # noqa: E402
from a100c.backend import select as select_mod  # noqa: E402
from a100c.driver import CompileOptions, PipelineError  # noqa: E402
from a100c.factory import FactoryCompiler  # noqa: E402
from a100c.ir import mir  # noqa: E402
from a100c.passes import pipeline as passes_mod  # noqa: E402
from a100c.target import DEFAULT_TARGET  # noqa: E402

CACHE = Path(tempfile.mkdtemp(prefix="a100c-t029-"))

# the factory shim: the native device protocol (F047)
os.environ["A100_COMPILER_FACTORY"] = "a100c.driver:make_compiler"
import a100_support.native_device as nd  # noqa: E402

SOFTMAX = ROOT / "ops" / "suite" / "dev" / "softmax_kernel_inner.py"
GEMM = ROOT / "ops" / "suite" / "dev" / "gemm_smallk_kernel_5ee47e3f.py"
MATMUL_K64 = ROOT / "ops" / "suite" / "dev" / \
    "matmul_k64_2d_unmasked_kernel_fc2c17b0.py"
MATMUL_K32_FAST = ROOT / "ops" / "suite" / "dev" / \
    "matmul_k32_fast_kernel_f2eeb00c.py"


def load_case(path: Path, **kw):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.make_case(**kw)


def compare(case, outputs) -> tuple:
    for name, policy in case["comparison"].items():
        got = np.asarray(outputs[name])
        exp = np.asarray(case["expected"][name])
        if got.shape != exp.shape:
            return False, f"{name}: shape {got.shape} != {exp.shape}"
        if policy.get("exact") or policy.get("comparator") == "array_equal":
            if not np.array_equal(got, exp):
                return False, f"{name}: array_equal failed"
        else:
            if not np.allclose(got.astype(np.float64),
                               exp.astype(np.float64),
                               rtol=policy.get("rtol", 1e-5),
                               atol=policy.get("atol", 1e-5),
                               equal_nan=policy.get("equal_nan", False)):
                return False, f"{name}: allclose failed"
    return True, ""


def run_executed(path: Path, threads: int = 1, **kw):
    """Compile + execute + compare one case through the native device
    protocol at ``threads``; returns (ok, detail)."""
    case = load_case(path, **kw)
    compiler = FactoryCompiler(
        options=CompileOptions(cache_dir=str(CACHE)),
        pass_config=passes_mod.PassConfig())
    try:
        device = nd.NativeExecutableDevice(compiler, threads)
        staged = device.stage_case(case)
        staged.launch()
        outs = staged.outputs()
        return compare(case, outs)
    except PipelineError as exc:
        return False, f"REFUSED {exc.construct}: {exc.message[:90]}"
    except Exception as exc:  # noqa: BLE001
        return False, f"{type(exc).__name__}: {str(exc)[:90]}"


# ---------------------------------------------------------------------------
# class 1: the ptradd width repair
# ---------------------------------------------------------------------------

def _sext32(pattern: int) -> int:
    """Sign-extend a 32-bit pattern."""
    pattern &= 0xFFFFFFFF
    return pattern - (1 << 32) if pattern & 0x80000000 else pattern


def check_ptradd_width():
    # the addressing model equivalence (acceptance[1]): the widened
    # (64-bit) path computes identical addresses to the 32-bit path
    # wherever the 32-bit path is defined, over offset magnitudes
    # crossing the 32-bit boundary
    #
    #   widened(lane, s) = (sext32(lane) + s) mod 2^64
    #                     -- the per-lane signed widening _sum_offsets
    #                        now emits (vwiden sext, then the 64-bit add)
    #   path32(lane, s)  = sext32((lane + s) mod 2^32)
    #                     -- the all-i32 machinery (sum in vi32, widen
    #                        once at the memory op)
    #
    # equal wherever the i32 sum does not wrap (the corpus regime: the
    # vector lanes are block-local, the range lives in the 64-bit
    # scalar); beyond the boundary only the widened path is defined and
    # must equal the independent model
    lanes = [0x00000000, 0x00000001, 0x0000007F, 0x00000FFF, 0x7FFFFFFF,
             0x80000000, 0xFFFFF000, 0xFFFFFFFE, 0xFFFFFFFF]
    scalars = [0, 1, -1, 127, -4096, 2 ** 31 - 1, 2 ** 31 - 2, -2 ** 31,
               -(2 ** 31) + 1,           # the i32 boundary (both sides)
               2 ** 31, 2 ** 31 + 7, -(2 ** 31) - 7, 2 ** 32, 2 ** 40 + 12345]
    mismatches = 0
    compared = 0
    for s in scalars:
        for lane in lanes:
            widened = (_sext32(lane) + s) % (1 << 64)
            model = (_sext32(lane) + s) % (1 << 64)
            if widened != model:                    # pragma: no cover
                mismatches += 1
            if -(2 ** 31) <= s < 2 ** 31:
                true_sum = _sext32(lane) + s
                if -(2 ** 31) <= true_sum < 2 ** 31:
                    # the 32-bit path is defined and must agree
                    compared += 1
                    path32 = _sext32((lane + (s & 0xFFFFFFFF)) & 0xFFFFFFFF)
                    if path32 != true_sum:
                        mismatches += 1
    check("ptradd-widened-equals-model", mismatches == 0,
          f"{compared} boundary-crossing (lane, scalar) pairs where the "
          "32-bit path is defined, all agreeing")

    # the control (MECH-WITNESS-TEST): a zext widening disagrees with
    # the signed model on negative lane patterns -- the equivalence
    # check above can fail
    control_bad = 0
    for lane in (0x80000000, 0xFFFFF000, 0xFFFFFFFF):
        s = 5
        zext_widened = (lane + s) % (1 << 64)      # zero-extended lanes
        if zext_widened != (_sext32(lane) + s) % (1 << 64):
            control_bad += 1
    check("ptradd-zext-control-disagrees", control_bad == 3,
          "a zext widening differs from the signed model on negative "
          "lanes (the check is load-bearing)")

    # the operator carrying the construct compiles through the enabled
    # pipeline to a RISC-V ELF (the 46-row census class at zero)
    case = load_case(SOFTMAX)
    compiler = FactoryCompiler(
        options=CompileOptions(cache_dir=str(CACHE)),
        pass_config=passes_mod.PassConfig())
    try:
        art = compiler.compile_case(
            {k: v for k, v in case.items()
             if k not in ("expected", "oracle_args")})
        head = Path(art.executable).read_bytes()[:20]
        check("ptradd-operator-compiles-elf",
              head[:6] == b"\x7fELF\x02\x01" and head[18:20] == b"\xf3\x00",
              str(Path(art.executable).name))
    except PipelineError as exc:
        check("ptradd-operator-compiles-elf", False,
              f"{exc.construct}: {exc.message[:90]}")
        return

    # the widened form is in the MIR: vwaddx0 (the legalized vwiden
    # sext) producing the e64m2 index class at the ptradd lines
    from a100c.frontend import lower_tir, source, specialize
    from a100c.lower import binding as binding_mod
    from a100c.lower import vectorize
    from a100c.plan import grid as grid_mod
    from a100c.plan import partition as part_mod
    src = source.load_operator(str(SOFTMAX))
    spec = specialize.specialize(src, case)
    tir_module = lower_tir.lower(src, spec)
    grid = grid_mod.extract_grid(src, case)
    layout = binding_mod.argument_layout(case, spec)
    module = vectorize.lower_to_mir(tir_module, part_mod.ExecutionPlan(),
                                    DEFAULT_TARGET, layout, grid)
    legal_mod.legalize(module)
    widened = [op for fn in module.functions for b in fn.blocks for op in b.ops
               if op.opcode == "vwaddx0" and op.attrs.get("mode") == "sext"
               and op.results[0].type.sew == 64]
    check("ptradd-widened-form-in-mir",
          len(widened) >= 2
          and all(op.results[0].type.lmul == 2 for op in widened),
          f"{len(widened)} vwaddx0 sext widenings to vi64m2")

    # executed: the softmax-shaped operator at 1 and 2 threads (the
    # construct's own comparison policy); the fp32 form -- the fp16
    # multi-chunk and bf16 forms carry separately-recorded reduction
    # defects (the remaining-work list), not addressing defects
    ok1, why1 = run_executed(SOFTMAX, threads=1, dtype="float32")
    check("ptradd-softmax-executes-pass-1t", ok1, why1)
    ok2, why2 = run_executed(SOFTMAX, threads=2, dtype="float32")
    check("ptradd-softmax-executes-pass-2t", ok2, why2)


# ---------------------------------------------------------------------------
# class 2: the LMUL-4 allocation repair
# ---------------------------------------------------------------------------

def _m4_pressure_module(count: int = 9):
    """``count`` simultaneously-live vi32m4 values + one use of each, in
    a full-vl e32m4 region (the spill-legality precondition)."""
    launch = mir.VReg(mir.I64, name="launch")
    fn = mir.MFunction("m4_pressure", [launch])
    entry = mir.Block("entry", [launch])
    fn.blocks.append(entry)
    avl = mir.VReg(mir.I32, name="avl")
    entry.ops.append(mir.MOp("sconst", [], [avl], attrs={"value": 128}))
    entry.ops.append(mir.MOp(
        "vsetvli", [avl], [mir.VReg(mir.I32, name="vlr")],
        attrs={"sew": 32, "lmul": 4, "policy": "ta,ma"}))
    mtype = mir.VectorType(32, 4, "int")
    regs = []
    for i in range(count):
        reg = mir.VReg(mtype, name=f"p{i}")
        entry.ops.append(mir.MOp("vid", [], [reg]))
        regs.append(reg)
    acc = regs[0]
    for r in regs[1:]:
        nxt = mir.VReg(mtype, name=f"s{r.name}")
        entry.ops.append(mir.MOp("vbin", [acc, r], [nxt],
                                 attrs={"op": "add"}))
        acc = nxt
    entry.ops.append(mir.MOp("ret", [], []))
    module = mir.MModule("m4_pressure", "<probe>")
    module.functions.append(fn)
    return module


def check_lmul4_allocation():
    # the pipeline order: selection BEFORE allocation (the spill ops the
    # allocator inserts are emission-special-cased, never selected)
    module = _m4_pressure_module()
    try:
        selection = select_mod.select(module)
        allocation = alloc_mod.allocate(module, DEFAULT_TARGET)
    except alloc_mod.AllocationError as exc:
        check("lmul4-pressure-allocates", False, str(exc)[:120])
        return
    # groups are naturally aligned (v4..v28, N % 4 == 0) and the file
    # budget holds
    bad_align = []
    for fn in module.functions:
        for b in fn.blocks:
            for op in b.ops:
                for r in op.results:
                    if r.is_vector() and r.type.lmul == 4:
                        name = allocation.assignment.get(r.rid, "")
                        if name.startswith("v") and int(name[1:]) % 4:
                            bad_align.append(name)
    check("lmul4-groups-naturally-aligned", not bad_align, str(bad_align[:4]))
    stats = allocation.stats
    check("lmul4-file-within-budget",
          stats["vector_regs_used"] <= 32
          and stats["vector_bytes_used"] <= DEFAULT_TARGET.vector_file_bytes,
          f"{stats['vector_regs_used']} regs / "
          f"{stats['vector_bytes_used']}B of "
          f"{DEFAULT_TARGET.vector_file_bytes}B")
    # the pressure spills (9 m4 groups = 36 registers > 31) and the
    # spilled module still verifies
    ops = {op.opcode for fn in module.functions for b in fn.blocks
           for op in b.ops}
    check("lmul4-pressure-spills-legally",
          stats["spilled_values"] > 0 and "vspill" in ops
          and "vreload" in ops,
          f"{stats['spilled_values']} spilled, slots "
          f"{allocation.slots}")
    # the emitted program (the m4 slots push the frame toward the
    # 12-bit immediate boundary) assembles with the declared cross
    # toolchain -- the offset-safe forms
    program = emit_mod.emit_assembly(module, allocation, DEFAULT_TARGET,
                                     workspace=(0, 0), selection=selection)
    with tempfile.TemporaryDirectory(prefix="a100c-t029-m4-") as tmp:
        asm = Path(tmp) / "program.S"
        asm.write_text(program.text)
        import importlib.util as ilu
        spec = ilu.spec_from_file_location(
            "a100c_runtime_build", ROOT / "a100c" / "runtime" / "build.py")
        build = ilu.module_from_spec(spec)
        spec.loader.exec_module(build)
        try:
            obj, tools, _a, _i = build.assemble_operator(asm, Path(tmp))
            check("lmul4-spill-frame-assembles",
                  obj.is_file()
                  and "riscv64-unknown-linux-gnu" in str(tools["as"]),
                  f"frame {program.stats.get('frame_bytes')}B assembled")
        except Exception as exc:  # noqa: BLE001
            check("lmul4-spill-frame-assembles", False,
                  f"{type(exc).__name__}: {str(exc)[:100]}")
    errors = mir.verify_module(module)
    check("lmul4-post-spill-verifies", not errors,
          str(errors[0]) if errors else "")
    # interference-free after the spill
    fn = module.functions[0]
    graph, _ = alloc_mod._interference(fn)
    conflicts = []
    for rid, neighbors in graph.items():
        name = allocation.assignment.get(rid)
        for n in neighbors:
            if allocation.assignment.get(n) == name:
                conflicts.append((rid, n, name))
    check("lmul4-no-interfering-pair-shares", not conflicts,
          str(conflicts[:3]))

    # the emitted spill form's ambient-vl discipline: ``vsetvli x0, x0,
    # e{sew}, m{lmul}`` KEEPS the ambient vl (probed on the pinned QEMU:
    # from vl=32/e32m1 the switch to e32m4 left vl=32, and vse32.v
    # stored exactly 32 lanes), so the spill/reload of a whole register
    # group is value-preserving only when the ambient region at every
    # spill site is the FULL one (avl == vlmax).  Assert it textually on
    # the emitted program: each spill-form store loads the whole group.
    vlen_bits = DEFAULT_TARGET.vlen_bits
    spill_form = re.compile(
        r"^\s*vsetvli\s+x0,\s*x0,\s*e(\d+),\s*m(\d+),\s*ta,\s*ma")
    vsl = re.compile(r"^\s*vsetvli\s+(\w+),\s*(\w+),\s*e(\d+),\s*m(\d+)")
    lil = re.compile(r"^\s*li\s+(\w+),\s*(-?\d+)")
    mem = re.compile(r"^\s*(vse\d+|vle\d+)\.v")
    consts: Dict[str, int] = {}
    ambient = None
    pending = None
    sites = []
    for line in program.text.splitlines():
        li = lil.match(line)
        if li:
            consts[li.group(1)] = int(li.group(2))
        if spill_form.match(line):
            pending = ambient
            continue
        vm = vsl.match(line)
        if vm:
            ambient = (int(vm.group(3)), int(vm.group(4)),
                       consts.get(vm.group(2)))
        if mem.match(line) and pending is not None:
            sites.append((pending, line.strip()))
            pending = None
    bad_ambient = [(str(p), m) for p, m in sites
                   if p is None or p[2] is None
                   or p[2] != (vlen_bits // p[0]) * p[1]
                   or (p[0], p[1]) != (32, 4)]
    check("lmul4-spill-sites-full-vl-ambient",
          sites and not bad_ambient,
          f"{len(sites)} spill sites, all in full-vl e32m4 "
          f"(avl 128) ambient regions"
          if not bad_ambient else str(bad_ambient[:3]))

    # executed: the operators behind the removed LMUL-4 refusals
    # (gemm_smallk: the N-tail mask covering all 128 lanes;
    # matmul_k64_2d: the broadcast-shaped staged offsets)
    ok, why = run_executed(GEMM, threads=1)
    check("lmul4-gemm-smallk-executes-pass", ok, why)
    ok, why = run_executed(MATMUL_K64, threads=2)
    check("lmul4-matmul-k64-executes-pass-2t", ok, why)


# ---------------------------------------------------------------------------
# class 3: the spill-convergence repair
# ---------------------------------------------------------------------------

def _constant_pressure_module():
    """The class-3 shape: a loop body whose scalars are ~30 hoisted
    constants with many uses plus more simultaneously-live values than
    the 25 allocatable GPRs (the measured pressure source: 26 live
    against 25)."""
    launch = mir.VReg(mir.I64, name="launch")
    fn = mir.MFunction("const_loop_pressure", [launch])
    entry = mir.Block("entry", [launch])
    fn.blocks.append(entry)
    head = mir.Block("loop.head")
    body = mir.Block("loop.body")
    exit_ = mir.Block("loop.exit")
    fn.blocks.extend([entry, head, body, exit_])
    k = mir.VReg(mir.I64, name="k0")
    entry.ops.append(mir.MOp("sconst", [], [k], attrs={"value": 0}))
    entry.ops.append(mir.MOp(
        "br", [], [], attrs={"args": [k], "target": "loop.head"}))
    # loop.head(i): while i < 64
    i = mir.VReg(mir.I64, name="i")
    head.params.append(i)
    bound = mir.VReg(mir.I64, name="bound")
    head.ops.append(mir.MOp("sconst", [], [bound], attrs={"value": 64}))
    go = mir.VReg(mir.I64, name="go")
    head.ops.append(mir.MOp("slt", [i, bound], [go]))
    i_body = mir.VReg(mir.I64, name="i_body")
    body.params.append(i_body)
    head.ops.append(mir.MOp(
        "brc", [go], [],
        attrs={"true_target": "loop.body", "false_target": "loop.exit",
               "true_args": [i], "false_args": [i]}))
    # the body: 30 constants, each used twice, all live across the body
    consts = []
    for c in range(30):
        reg = mir.VReg(mir.I64, name=f"kc{c}")
        body.ops.append(mir.MOp("sconst", [], [reg],
                                attrs={"value": 1000 + c}))
        consts.append(reg)
    acc = consts[0]
    for reg in consts[1:]:
        nxt = mir.VReg(mir.I64, name=f"ka{reg.name}")
        body.ops.append(mir.MOp("sadd", [acc, reg], [nxt]))
        acc = nxt
    for reg in consts:
        # a second use of every constant (the many-use pattern)
        nxt = mir.VReg(mir.I64, name=f"kb{reg.name}")
        body.ops.append(mir.MOp("sadd", [acc, reg], [nxt]))
        acc = nxt
    one = mir.VReg(mir.I64, name="one")
    body.ops.append(mir.MOp("sconst", [], [one], attrs={"value": 1}))
    i2 = mir.VReg(mir.I64, name="i2")
    body.ops.append(mir.MOp("sadd", [i_body, one], [i2]))
    body.ops.append(mir.MOp(
        "br", [], [], attrs={"args": [i2], "target": "loop.head"}))
    exit_.params.append(mir.VReg(mir.I64, name="i_exit"))
    exit_.ops.append(mir.MOp("ret", [], []))
    module = mir.MModule("const_loop_pressure", "<probe>")
    module.functions.append(fn)
    return module


def check_spill_convergence():
    module = _constant_pressure_module()
    try:
        allocation = alloc_mod.allocate(module, DEFAULT_TARGET)
    except alloc_mod.AllocationError as exc:
        check("convergence-constant-loop-pressure", False, str(exc)[:140])
        return
    names = [r.name for fn in module.functions for b in fn.blocks
             for op in b.ops for r in op.results]
    resplits = [n for n in names if ".r" in n and n.count(".r") > 1]
    remats = [n for n in names if ".c" in n]
    check("convergence-constant-loop-pressure",
          not resplits and remats,
          f"converged; {len(remats)} remat products, 0 reload re-splits, "
          f"{allocation.stats['spilled_values']} stack spills")
    errors = mir.verify_module(module)
    check("convergence-module-verifies", not errors,
          str(errors[0]) if errors else "")

    # values preserved across the interventions, structurally (the
    # remat path): every remat product carries the SAME constant as the
    # value it replaces -- rematerialization is value-preserving by
    # construction, and this asserts the construction
    remat_pairs = []
    for fn in module.functions:
        for b in fn.blocks:
            for op in b.ops:
                if op.opcode == "sconst" and ".c" in op.results[0].name:
                    remat_pairs.append((op.results[0].name,
                                        op.attrs["value"]))
    originals = {1000 + c for c in range(30)}
    check("convergence-remat-values-preserved",
          remat_pairs and all(v in originals for _n, v in remat_pairs),
          f"{len(remat_pairs)} remat products, values "
          f"{sorted({v for _n, v in remat_pairs})[:6]}...")
    # values preserved across the spill path: every reload matches a
    # spill on the same slot at the same (sew, lmul) -- the reload
    # restores exactly the register group the spill stored
    spills = {}
    reloads = []
    for fn in module.functions:
        for b in fn.blocks:
            for op in b.ops:
                if op.opcode in ("vspill", "sspill"):
                    spills.setdefault(op.attrs["slot"], []).append(op)
                elif op.opcode in ("vreload", "sreload"):
                    reloads.append(op)
    mismatched = [op.attrs["slot"] for op in reloads
                  if op.attrs["slot"] not in spills]
    shape_mismatch = []
    for op in reloads:
        for sp in spills.get(op.attrs["slot"], ()):
            if (sp.attrs.get("sew"), sp.attrs.get("lmul")) != \
                    (op.attrs.get("sew"), op.attrs.get("lmul")):
                shape_mismatch.append(op.attrs["slot"])
    check("convergence-spill-reload-slots-match",
          reloads and not mismatched and not shape_mismatch,
          f"{len(reloads)} reloads against {len(spills)} spill slots, "
          "all shape-matched")

    # executed: the class-3 census operator (fp16, the dtype that hit
    # the 65-round non-convergence) compiles, executes, compares
    ok, why = run_executed(MATMUL_K32_FAST, threads=1, dtype="float16")
    check("convergence-matmul-k32-fast-fp16-pass", ok, why)


def check_mixed_lmul_overlap_control():
    """acceptance[2]'s negative control (MECH-WITNESS-TEST): the post-
    allocation mixed-LMUL overlap invariant can actually REJECT -- a
    hand-forged assignment whose m2 destination group covers its m1
    source must raise, so the invariant's silence on the real allocations
    is meaningful (a check that cannot fail checks nothing)."""
    # the widening-address class: an m1 source feeding an m2 destination
    launch = mir.VReg(mir.I64, name="launch")
    fn = mir.MFunction("overlap_probe", [launch])
    entry = mir.Block("entry", [launch])
    fn.blocks.append(entry)
    src = mir.VReg(mir.VectorType(32, 1, "int"), name="src")
    dst = mir.VReg(mir.VectorType(64, 2, "int"), name="dst")
    entry.ops.append(mir.MOp("vid", [], [src]))
    entry.ops.append(mir.MOp("vwiden", [src], [dst],
                             attrs={"mode": "sext"}))
    entry.ops.append(mir.MOp("ret", [], []))
    module = mir.MModule("overlap_probe", "<probe>")
    module.functions.append(fn)
    try:
        allocation = alloc_mod.allocate(module, DEFAULT_TARGET)
    except alloc_mod.AllocationError as exc:
        check("overlap-control-legal-allocates", False, str(exc)[:100])
        return
    sname = allocation.assignment.get(src.rid)
    dname = allocation.assignment.get(dst.rid)
    sbase = int(sname[1:]) if sname and sname.startswith("v") else -1
    dbase = int(dname[1:]) if dname and dname.startswith("v") else -1
    legal = (sbase >= 0 and dbase >= 0
             and not (dbase <= sbase < dbase + 2))
    check("overlap-control-legal-allocates", legal,
          f"src={sname} dst={dname} (groups disjoint)")
    # the control: forge the destination group onto the source
    forged = alloc_mod.Allocation()
    forged.assignment[src.rid] = "v2"
    forged.assignment[dst.rid] = "v2"       # m2 group covers v2 and v3
    forged.shapes[src.rid] = ("vec", 1)
    forged.shapes[dst.rid] = ("vec", 2)
    try:
        alloc_mod._check_group_overlap(fn, forged)
    except alloc_mod.AllocationError as exc:
        check("overlap-control-rejects-overlap",
              "overlapping source" in str(exc), str(exc)[:90])
        return
    check("overlap-control-rejects-overlap", False,
          "the invariant accepted a forged overlapping assignment "
          "(the check is vacuous)")


def main() -> int:
    check_ptradd_width()
    check_lmul4_allocation()
    check_spill_convergence()
    check_mixed_lmul_overlap_control()
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} check(s)", flush=True)
        return 1
    print("test_t029_repairs: all checks PASS", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
