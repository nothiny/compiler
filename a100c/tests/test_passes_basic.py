#!/usr/bin/env python3
"""test_passes_basic.py -- the basic optimization passes (T015).

The six passes (cse, dce, constprop, copyprop, strength_reduction, licm)
run on TIR under their legality conditions, as ordinary correctness
work (F055: no timing, no counter quota, no measured round is claimed
anywhere in this file).  The checks:

  acceptance[0] per-pass legality: each pass has a witness operator
                whose eligible expression/loop is actually rewritten
                (the structural trace -- fired counters with the
                rewrite samples -- is observed) and whose executed
                result compares PASS against the case's own independent
                reference under its declared policy; the unsafe
                candidates are DECLINED with the unmet condition
                recorded (float 0*x, the overlapping-store CSE, the
                runtime-divisor division, the never-hoisted load, the
                non-power-of-two divisor).  The load-bearing declines
                are proven by execution: a pass that ignored them would
                fail the same comparison;
  acceptance[1] the shared-analysis invalidation contract: a mutated
                module forces recomputation (get), a frozen view raises
                StaleAnalysisError (a pass holding one refuses to run),
                and the forced-wrong-analysis controls change the
                dependent pass's outcome (the passes consume what they
                declare);
  acceptance[2] real switches: disabling a pass changes the emitted
                code for a matching input, the pass configuration is
                part of the artifact identity (no silent reuse across
                configurations), and the trace distinguishes
                fired-zero-times from disabled;
  acceptance[3] a representative corpus subset (elementwise+mask,
                flow.loop/dynamic-range, reductions, dot/matrix,
                atomics, special math, layout split/join, dtype
                conversions, persistent reduce, both tiers) executes
                and compares PASS at 1 and 4 workers with the passes
                ENABLED and DISABLED; with every pass disabled the
                artifact is byte-identical to the plain driver's (the
                general path is intact -- MECH-GENERAL-PATH-FIRST).

The compile path is the driver's own stage sequence (frontend -> TIR ->
verify -> [the basic passes] -> grid -> plan -> layout -> MIR -> verify
-> legalise -> select -> allocate -> emit -> cross as + ld -> ELF) with
the pass pipeline inserted between TIR verification and the lowering --
the integration seam a100c/factory.py (T017) adopts; driver.py is not
in this task's write surface.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap  # noqa: E402

ROOT = _bootstrap.bootstrap()
import warnings  # noqa: E402

warnings.filterwarnings("ignore")

FAILURES = []
EVIDENCE = {"cases": []}


def check(name: str, ok: bool, detail: str = "") -> bool:
    print(f"{'PASS' if ok else 'FAIL'} {name}"
          f"{(' | ' + detail) if detail else ''}", flush=True)
    if not ok:
        FAILURES.append(name)
    return ok


import numpy as np  # noqa: E402

from a100c.driver import Compiler, CompileOptions, compiler_revision  # noqa: E402
from a100c.frontend import lower_tir  # noqa: E402
from a100c.frontend import source as fe_source  # noqa: E402
from a100c.frontend import specialize as fe_spec  # noqa: E402
from a100c.frontend.source import FrontendError  # noqa: E402
from a100c.ir import dump as tir_dump  # noqa: E402
from a100c.ir import tir  # noqa: E402
from a100c.lower import binding as binding_mod  # noqa: E402
from a100c.lower import matrix as matrix_verify  # noqa: E402
from a100c.lower import vectorize  # noqa: E402
from a100c.lower.vectorize import LowerOptions  # noqa: E402
from a100c.passes import analyses as analyses_mod  # noqa: E402
from a100c.passes import pipeline as passes_mod  # noqa: E402
from a100c.passes import rewrite as rewrite_mod  # noqa: E402
from a100c.backend import allocate as alloc_mod  # noqa: E402
from a100c.backend import emit as emit_mod  # noqa: E402
from a100c.backend import legalize as legal_mod  # noqa: E402
from a100c.backend import select as select_mod  # noqa: E402
from a100c.plan import grid as grid_mod  # noqa: E402
from a100c.plan import partition as part_mod  # noqa: E402

import a100_support.native_device as nd  # noqa: E402

WORK = Path(tempfile.mkdtemp(prefix="a100c-passes-"))
CACHE = WORK / "cache"


# ---------------------------------------------------------------------------
# the compile path: the driver's stages with the pass seam
# ---------------------------------------------------------------------------

class Artifact:
    def __init__(self, executable: Path, passes: dict):
        self.executable = executable
        self.arguments = ("--bundle", "{bundle}", "--threads", "{threads}")
        self.provenance = "a100c/basic-passes"
        self.passes = passes
        self.cache_hit = False
        self.sha256 = ""


class PassesCompiler:
    """compile_case over the real driver stages, with the basic-pass
    pipeline between TIR verification and the lowering.  The artifact
    identity is the driver's own identity plus the pass configuration
    (a configuration change is never a silent cache hit)."""

    def __init__(self, config: passes_mod.PassConfig, cache_dir):
        self.config = config
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._inner = Compiler(options=CompileOptions(
            cache_dir=str(self.cache_dir / "inner")))
        self._runtime = self._inner._runtime
        self.compile_count = 0
        self.cache_hits = 0

    def compile_case(self, case: dict) -> Artifact:
        started = time.monotonic()
        base = self._inner._identity(case)
        key = hashlib.sha256(
            (base["key"] + "|" + self.config.identity_part()).encode()
        ).hexdigest()
        entry = self.cache_dir / key
        marker = entry / "artifact.json"
        executable = entry / "operator_exec"
        if marker.is_file() and executable.is_file():
            meta = json.loads(marker.read_text())
            self.cache_hits += 1
            art = Artifact(executable, meta["passes"])
            art.cache_hit = True
            art.sha256 = meta["sha256"]
            return art
        self.compile_count += 1
        entry.mkdir(parents=True, exist_ok=True)
        art = self._compile_into(case, entry, base)
        art.sha256 = hashlib.sha256(
            Path(art.executable).read_bytes()).hexdigest()
        meta = {"identity": base["specialization"], "key": key,
                "passes": art.passes, "sha256": art.sha256,
                "compile_ms": int((time.monotonic() - started) * 1000)}
        marker.write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n")
        return art

    def _compile_into(self, case: dict, entry: Path, base: dict) -> Artifact:
        src = self._inner._load_source(case)
        spec = fe_spec.specialize(src, case)
        tir_module = lower_tir.lower(src, spec)
        errors = tir.verify_module(tir_module)
        if errors:
            raise RuntimeError(f"TIR verification failed: {errors[0]}")
        # -- the T015 seam: the basic passes run on verified TIR, and the
        #    result is verified again (a rewrite that breaks the contract
        #    is a pass defect, raised here)
        report = passes_mod.run(tir_module, self.config)
        errors = tir.verify_module(tir_module)
        if errors:
            raise RuntimeError(f"post-pass TIR verification failed: "
                               f"{errors[0]}")
        (entry / "stage.tir.txt").write_text(tir_dump.dump_module(tir_module))
        grid = grid_mod.extract_grid(src, case)
        plan = part_mod.ExecutionPlan()
        layout = binding_mod.argument_layout(case, spec)
        mir_module = vectorize.lower_to_mir(
            tir_module, plan, self._inner.target, layout, grid,
            LowerOptions())
        errors = matrix_verify.verify_module(mir_module)
        if errors:
            raise RuntimeError(f"MIR verification failed: {errors[0]}")
        legal_mod.legalize(mir_module)
        errors = matrix_verify.verify_module(mir_module)
        if errors:
            raise RuntimeError(f"post-legalize verification failed: "
                               f"{errors[0]}")
        selection = select_mod.select(mir_module)
        allocation = alloc_mod.allocate(mir_module, self._inner.target)
        header = [
            f"# a100c emitted program: {tir_module.name}",
            f"# source: {src.rel_path}",
            f"# specialization identity: {spec.identity}",
            f"# compiler revision: {compiler_revision()}",
            f"# target model: {self._inner.target.model_version} "
            f"(VLEN={self._inner.target.vlen_bits}, file="
            f"{self._inner.target.vector_file_bytes}B)",
            f"# options: {self._inner.options.identity_part()}",
            f"# argument layout: {layout.digest}",
            "# every instruction below traces to a selected MIR op: "
            "[opN] carries the source location",
        ]
        if any(self.config.enabled.values()):
            header.append(f"# passes: {self.config.identity_part()}")
        program = emit_mod.emit_assembly(
            mir_module, allocation, self._inner.target,
            workspace=(plan.workspace_private, plan.workspace_shared),
            selection=selection, header=header)
        (entry / "program.S").write_text(program.text)
        obj, _tools, _assembled, invocations = self._runtime.assemble_operator(
            entry / "program.S", build_dir=self.cache_dir / "build")
        self._runtime.link_operator(
            [obj], entry / "operator_exec",
            build_dir=self.cache_dir / "build",
            extra_invocations=invocations)
        return Artifact(entry / "operator_exec", report.describe())


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def make_case(module, **kwargs):
    case = module.make_case(**kwargs)
    if case.get("expected") is None:
        case["expected"] = module.ref(case["args"], case["meta"])
    return case


def compare(case, outputs) -> str:
    """The case's own comparison policy (tolerance and reference read
    from the case, never widened)."""
    for name, policy in case["comparison"].items():
        got = np.asarray(outputs[name])
        exp = np.asarray(case["expected"][name])
        if policy.get("exact") or policy.get("comparator") == "array_equal":
            if not np.array_equal(got, exp):
                return f"{name}: array_equal failed"
        else:
            if not np.allclose(got, exp, rtol=policy.get("rtol", 0.0),
                               atol=policy.get("atol", 0.0),
                               equal_nan=policy.get("equal_nan", False)):
                return f"{name}: allclose failed (max err " \
                      f"{np.max(np.abs(got - exp))})"
    return ""


def execute(compiler, case, threads):
    device = nd.NativeExecutableDevice(compiler, threads)
    staged = device.stage_case(case)
    staged.launch()
    return compare(case, staged.outputs()), staged


# ---------------------------------------------------------------------------
# the witness operators (written into the workdir at test time, corpus
# case-layer form: a numpy ref and a declared comparison policy)
# ---------------------------------------------------------------------------

_WITNESS_TEMPLATE = '''"""probe"""
OPERATOR = {{"name": "probe/{name}", "group": "probe", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": []}}
SHAPES = ((128,), (17,))
import numpy as np
import triton
import triton.language as tl

@triton.jit
def {name}_kernel(x_ptr, y_ptr, out_ptr, out_ptr2, out_ptr3, out_ptr4, n,
                  flag, BLOCK: tl.constexpr):
{body}

def ref(args, meta):
{ref}

def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
{case}

def make_case(shape=None, dtype=None, seed=None):
    return _make_case(shape=shape or SHAPES[0],
                      dtype=dtype or "float32", seed=seed or 0)
'''

_STANDARD_CASE = """    n = 128
    x = {data}
    return {{"args": {{"x_ptr": x, "y_ptr": np.zeros(n, np.float32),
                     "out_ptr": np.zeros({outsz}, np.float32),
                     "out_ptr2": np.zeros(n, np.float32),
                     "out_ptr3": np.zeros(n, np.float32),
                     "out_ptr4": np.zeros(n, np.float32),
                     "n": n, "flag": {flag}}},
            "meta": {{"BLOCK": 128}}, "grid": (1,),
            "kernel": {name}_kernel,
            "outputs": {outputs}, "expected": None,
            "comparison": {comparison}}}"""

_DEFAULT_COMPARISON = (
    '{"out_ptr": {"comparator": "array_equal", "exact": True}}')
_DEFAULT_OUTPUTS = '("out_ptr",)'

_WITNESSES = {
    # CSE with the disjointness proof: two identical scalar loads, the
    # intervening store provably writes a disjoint constant range
    "cse_disjoint": ("""    a = tl.load(x_ptr + 5)
    tl.store(x_ptr + 100, a)
    b = tl.load(x_ptr + 5)
    offs = tl.arange(0, BLOCK)
    tl.store(out_ptr + offs, a + b + offs.to(tl.float32) * 0.0,
             mask=offs < 1)""",
                     """    x = args["x_ptr"].copy()
    a = x[5]
    x[100] = a
    b = x[5]
    return {"out_ptr": np.array([a + b], np.float32)}"""),
    # CSE across an overlapping write: refused (and the refusal is
    # load-bearing -- reusing the first load would fail the compare)
    "cse_overlap": ("""    a = tl.load(x_ptr + 5)
    tl.store(x_ptr + 5, a + 1.0)
    b = tl.load(x_ptr + 5)
    offs = tl.arange(0, BLOCK)
    tl.store(out_ptr + offs, a + b + offs.to(tl.float32) * 0.0,
             mask=offs < 1)""",
                     """    x = args["x_ptr"].copy()
    a = x[5]
    x[5] = a + 1.0
    b = x[5]
    return {"out_ptr": np.array([a + b], np.float32)}"""),
    # DCE: dead pure arithmetic removed; the dead division with a
    # runtime divisor retained (the trapping class)
    "dce_witness": ("""    i = tl.arange(0, BLOCK)
    m = i < n
    x = tl.load(x_ptr + i, mask=m, other=0.0)
    dead = x * 2.0 + 4.0
    dead2 = n // flag
    tl.store(out_ptr + i, x, mask=m)""",
                     """    x = args["x_ptr"]
    return {"out_ptr": x.astype(np.float32)}"""),
    # constprop: integer identity elimination (0 + i, i * 1)
    "cp_int_witness": ("""    i = tl.arange(0, BLOCK)
    m0 = 0 + i
    m1 = i * 1
    x = tl.load(x_ptr + m0, mask=m1 < n, other=0.0)
    tl.store(out_ptr + i, x, mask=i < n)""",
                       """    x = args["x_ptr"]
    return {"out_ptr": x.astype(np.float32)}"""),
    # constprop: the float 0*x identity is REFUSED (NaN/Inf/-0.0); the
    # data contains -inf, so folding it would change the result
    "cp_float_witness": ("""    x = tl.load(x_ptr + tl.arange(0, BLOCK))
    g = x * 0.0
    y = tl.where(x < g, -x, x)
    tl.store(out_ptr + tl.arange(0, BLOCK), y)""",
                         """    x = args["x_ptr"]
    g = x * 0.0
    y = np.where(x < g, -x, x)
    return {"out_ptr": y.astype(np.float32)}"""),
    # constprop: the path-condition where (the arm's own condition)
    "cp_pathcond_witness": ("""    i = tl.arange(0, BLOCK)
    m = i < n
    x = tl.load(x_ptr + i, mask=m, other=0.0)
    if flag > 0:
        y = tl.where(flag > 0, x + 1.0, x) * 3.0
    else:
        y = x
    tl.store(out_ptr + i, y, mask=m)""",
                            """    x = args["x_ptr"]
    if args["flag"] > 0:
        y = (x + 1.0) * 3.0
    else:
        y = x
    return {"out_ptr": y.astype(np.float32)}"""),
    # strength reduction: sdiv/srem by 16 (sign-corrected), mul by 12
    # (shifts+add), division by 100 refused (non-power-of-two)
    "sr_witness": ("""    i = tl.arange(0, BLOCK) + flag - 100
    q = i // 16
    r = i % 16
    q2 = i * 12
    q3 = i // 100
    tl.store(out_ptr + tl.arange(0, BLOCK), q.to(tl.float32))
    tl.store(out_ptr2 + tl.arange(0, BLOCK), r.to(tl.float32))
    tl.store(out_ptr3 + tl.arange(0, BLOCK), q2.to(tl.float32))
    tl.store(out_ptr4 + tl.arange(0, BLOCK), q3.to(tl.float32))""",
                   """    i = np.arange(128, dtype=np.int64) + args["flag"] - 100
    q = np.trunc(i / 16).astype(np.int64)
    r = (i - q * 16).astype(np.int64)
    q2 = i * 12
    q3 = np.trunc(i / 100).astype(np.int64)
    return {"out_ptr": q.astype(np.float32),
            "out_ptr2": r.astype(np.float32),
            "out_ptr3": q2.astype(np.float32),
            "out_ptr4": q3.astype(np.float32)}"""),
    # copyprop: ptradd(p, 0), the identity reshape, where(c, x, x)
    "cp_copy_witness": ("""    i = tl.arange(0, BLOCK)
    p = x_ptr + 0
    x = tl.load(p + i, mask=i < n, other=0.0)
    y0 = tl.reshape(x, (BLOCK,))
    y = tl.where(flag > 0, y0, y0)
    tl.store(out_ptr + i, y, mask=i < n)""",
                        """    x = args["x_ptr"]
    return {"out_ptr": x.astype(np.float32)}"""),
    # LICM: invariant pure ops hoisted; the invariant-address load is
    # never hoisted (a store crosses it inside the loop -- the refusal
    # is load-bearing: hoisting would read the pre-loop value)
    "licm_witness": ("""    base = tl.load(x_ptr + 7)
    scale = flag * 2
    acc = tl.zeros((), dtype=tl.float32)
    p = x_ptr + 7
    for k in range(0, 4):
        v = tl.load(p)
        tl.store(p, v + 1.0)
        acc = acc + v + scale
    offs = tl.arange(0, BLOCK)
    tl.store(out_ptr + offs, acc + base + offs.to(tl.float32) * 0.0,
             mask=offs < 1)""",
                     """    x = args["x_ptr"].copy()
    base = x[7]
    acc = 0.0
    for k in range(4):
        v = x[7]
        x[7] = v + 1.0
        acc = acc + v + args["flag"] * 2
    return {"out_ptr": np.array([acc + base], np.float32)}"""),
}

_WITNESS_CASES = {
    "cse_disjoint": ("np.arange(n, dtype=np.float32)", "1", "1",
                     _DEFAULT_OUTPUTS, _DEFAULT_COMPARISON),
    "cse_overlap": ("np.arange(n, dtype=np.float32)", "1", "1",
                    _DEFAULT_OUTPUTS, _DEFAULT_COMPARISON),
    "dce_witness": ("np.arange(n, dtype=np.float32) / 8.0", "3", "n",
                    _DEFAULT_OUTPUTS, _DEFAULT_COMPARISON),
    "cp_int_witness": ("np.arange(n, dtype=np.float32) / 7.0", "1", "n",
                       _DEFAULT_OUTPUTS, _DEFAULT_COMPARISON),
    "cp_float_witness": (
        "(np.arange(n, dtype=np.float32) - 64.0)\n"
        "    x[3] = -np.inf\n    x[5] = np.inf\n    x[7] = np.nan",
        "1", "n", _DEFAULT_OUTPUTS,
        '{"out_ptr": {"comparator": "allclose", "exact": False,\n'
        '                       "rtol": 0.0, "atol": 0.0,\n'
        '                       "equal_nan": True}}'),
    "cp_pathcond_witness": ("np.arange(n, dtype=np.float32) / 5.0", "1",
                            "n", _DEFAULT_OUTPUTS, _DEFAULT_COMPARISON),
    "sr_witness": ("np.zeros(n, np.float32)", "7", "n",
                   '("out_ptr", "out_ptr2", "out_ptr3", "out_ptr4")',
                   '{name: {"comparator": "array_equal", "exact": True}\n'
                   '             for name in ("out_ptr", "out_ptr2",\n'
                   '                         "out_ptr3", "out_ptr4")}'),
    "cp_copy_witness": ("np.arange(n, dtype=np.float32) / 11.0", "1", "n",
                        _DEFAULT_OUTPUTS, _DEFAULT_COMPARISON),
    "licm_witness": ("np.arange(n, dtype=np.float32) / 3.0", "5", "1",
                     _DEFAULT_OUTPUTS, _DEFAULT_COMPARISON),
}


def write_witnesses() -> Path:
    directory = WORK / "witnesses"
    directory.mkdir(parents=True, exist_ok=True)
    for name, (body, ref) in _WITNESSES.items():
        data, flag, outsz, outputs, comparison = _WITNESS_CASES[name]
        case = _STANDARD_CASE.format(data=data, flag=flag, name=name,
                                      outsz=outsz, outputs=outputs,
                                      comparison=comparison)
        text = _WITNESS_TEMPLATE.format(name=name, body=body, ref=ref,
                                        case=case)
        (directory / f"{name}.py").write_text(text)
    return directory


# the dot/matrix representative (the T014-proven probe form: the corpus
# dot operators are behind the recorded dots-in-runtime-loops boundary,
# so the class is covered by a synthetic operator with its own numpy
# reference)
_DOT_PROBE = '''"""probe"""
OPERATOR = {"name": "probe/dot_passes", "group": "probe", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": []}
SHAPES = ((16,), (17,))
import numpy as np
import triton
import triton.language as tl

@triton.jit
def dot_passes_kernel(A_ptr, B_ptr, C_ptr, O_ptr, M, N, K,
                      BM: tl.constexpr, BN: tl.constexpr, BK: tl.constexpr):
    offs_m = tl.arange(0, BM)
    offs_n = tl.arange(0, BN)
    offs_k = tl.arange(0, BK)
    a_ptrs = A_ptr + (offs_m[:, None] * BK + offs_k[None, :])
    b_ptrs = B_ptr + (offs_k[:, None] * BN + offs_n[None, :])
    a = tl.load(a_ptrs, mask=(offs_m[:, None] < M) & (offs_k[None, :] < K),
                other=0.0)
    b = tl.load(b_ptrs, mask=(offs_k[:, None] < K) & (offs_n[None, :] < N),
                other=0.0)
    c = tl.dot(a, b)
    tl.store(O_ptr + (offs_m[:, None] * BN + offs_n[None, :]),
             c.to(O_ptr.dtype.element_ty),
             mask=(offs_m[:, None] < M) & (offs_n[None, :] < N))

def ref(args, meta):
    return {"O_ptr": args["O_ptr"]}

def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    M, N, K = 16, 16, 16
    rng = np.random.default_rng(seed)
    a = (rng.integers(-16, 16, (M, K), dtype=np.int16) / 16).astype(np.float32)
    b = (rng.integers(-16, 16, (K, N), dtype=np.int16) / 16).astype(np.float32)
    prod = a.astype(np.float64) @ b.astype(np.float64)
    args = {"A_ptr": a.reshape(-1), "B_ptr": b.reshape(-1),
            "C_ptr": np.zeros(M*N, np.float32),
            "O_ptr": np.zeros(M*N, np.float32),
            "M": np.int32(M), "N": np.int32(N), "K": np.int32(K)}
    return {"args": args, "meta": {"BM": 16, "BN": 16, "BK": 16},
            "grid": (1,), "kernel": dot_passes_kernel,
            "outputs": ("O_ptr",),
            "expected": {"O_ptr": prod.astype(np.float32).reshape(-1)},
            "comparison": {"O_ptr": {"comparator": "allclose",
                                      "exact": False,
                                      "rtol": 1e-3, "atol": 1e-3}}}

def make_case(shape=None, dtype=None, seed=None):
    return _make_case()
'''


def _witness_modules():
    directory = write_witnesses()
    (directory / "dot_passes.py").write_text(_DOT_PROBE)
    return {name: _load(directory / f"{name}.py")
            for name in list(_WITNESSES) + ["dot_passes"]}


# ---------------------------------------------------------------------------
# acceptance[0]: per-pass legality (fired + executed PASS + declined)
# ---------------------------------------------------------------------------

def check_acceptance0(compilers, modules):
    on = compilers["on"]
    ok = True

    def run(name, expect_fired, expect_decline):
        nonlocal ok
        case = make_case(modules[name])
        why, staged = execute(on, case, 1)
        report = staged.artifact.passes["passes"]
        fired = {p: report[p]["fired"] for p in passes_mod.PASS_ORDER}
        good = not why
        detail = []
        for pass_name, count in expect_fired.items():
            if (fired[pass_name] or 0) < count:
                good = False
                detail.append(f"{pass_name} fired {fired[pass_name]} "
                              f"< {count}")
        for pass_name, key in expect_decline.items():
            reasons = report[pass_name].get("reasons", {})
            if not any(key in r for r in reasons):
                good = False
                detail.append(f"{pass_name} missing decline '{key}' "
                              f"(has {list(reasons)})")
        check(f"legality-{name}", good,
              (why or "") + ("; " + "; ".join(detail) if detail else "")
              + " | " + " ".join(f"{p}:{fired[p]}" for p in
                                 passes_mod.PASS_ORDER if fired[p]))
        EVIDENCE["cases"].append({"witness": name, "compare": why or "PASS",
                                  "fired": fired})
        ok &= good

    # CSE: the load reuse with the disjointness proof fires; the
    # overlapping write is refused
    run("cse_disjoint", {"cse": 1}, {})
    run("cse_overlap", {"cse": 1},
        {"cse": "load reuse across an intervening write refused"})
    # DCE: the dead pure chain is removed; the runtime-divisor division
    # is retained
    run("dce_witness", {"dce": 1},
        {"dce": "dead division/remainder retained"})
    # constprop: the integer identities fold; the float 0*x / x+0 forms
    # are refused; the path-condition where folds
    run("cp_int_witness", {"constprop": 1}, {})
    run("cp_float_witness", {},
        {"constprop": "float identity folding declined"})
    run("cp_pathcond_witness", {"constprop": 1}, {})
    # strength reduction: shifts/corrections fire; the non-power-of-two
    # divisor and the floating forms are refused
    run("sr_witness", {"strength_reduction": 2},
        {"strength_reduction": "division/remainder by 100"})
    # copyprop: ptradd(p,0)/identity-reshape/where(x,x) rewire
    run("cp_copy_witness", {"copyprop": 1}, {})
    # LICM: the invariant pure ops hoist; the load is never hoisted
    run("licm_witness", {"licm": 1},
        {"licm": "memory access 'load' is never hoisted"})
    # the dot probe (feature-class representative) executes PASS with
    # the passes on
    run("dot_passes", {}, {})

    # the corpus float-identity refusal on the REAL operator
    # (absolute_kernel's 0*x guard), executed and compared under the
    # case's own policy
    mod = _load(ROOT / "ops/suite/dev/absolute_kernel.py")
    case = mod.make_case(shape=(97,))
    why, staged = execute(on, case, 1)
    report = staged.artifact.passes["passes"]
    reasons = report["constprop"].get("reasons", {})
    good = not why and any("float identity folding declined" in r
                           for r in reasons)
    check("legality-absolute-kernel-float-identity-refusal", good,
          (why or "") + f" | constprop reasons={list(reasons)}")
    ok &= good
    check("acceptance0-per-pass-legality", ok)
    return ok


# ---------------------------------------------------------------------------
# acceptance[1]: the shared-analysis invalidation contract
# ---------------------------------------------------------------------------

def _tiny_module():
    """A frontend-produced module with a loop and a dead value (the
    invalidation-contract substrate)."""
    src = fe_source.load_operator(
        str(ROOT / "ops/suite/dev/var_len_copy.py"))
    module = _load(ROOT / "ops/suite/dev/var_len_copy.py")
    case = {k: v for k, v in module.make_case(shape=(3,),
                                              dtype="float32").items()
            if k not in ("expected", "oracle_args")}
    spec = fe_spec.specialize(src, case)
    return lower_tir.lower(src, spec)


def _witness_tir(name):
    """A fresh frontend-produced TIR module of one witness operator."""
    path = WORK / "witnesses" / f"{name}.py"
    src = fe_source.load_operator(str(path))
    module = _load(path)
    case = {k: v for k, v in make_case(module).items()
            if k not in ("expected", "oracle_args")}
    spec = fe_spec.specialize(src, case)
    return lower_tir.lower(src, spec)


def check_acceptance1():
    ok = True
    # (a) get() after a mutation recomputes -- never a stale read: remove
    # one USING statement and the observed use count drops
    m = _tiny_module()
    suite = analyses_mod.AnalysisSuite(m)
    l1 = suite.get("liveness")
    stmts = [st for fn in m.functions
             for st in fn.body.statements if isinstance(st, tir.Op)]
    tracked = None
    using = None
    for st in stmts:
        for operand in st.operands:
            if l1.use_count(operand) > 1:
                tracked, using = operand, st
                break
        if tracked is not None:
            break
    assert tracked is not None and using is not None
    uses_before = l1.use_count(tracked)
    rewrite_mod.remove_statement(m, using)
    l2 = suite.get("liveness")
    recomputed = (l2 is not l1 and l2.use_count(tracked) < uses_before)
    check("invalidation-mutation-forces-recomputation", recomputed,
          f"{tracked.name}: uses {uses_before} -> {l2.use_count(tracked)} "
          f"after removing one use site (the digest moved, so the suite "
          f"recomputed)")
    ok &= recomputed

    # (b) a frozen view refuses after the module moved (StaleAnalysisError)
    m = _tiny_module()
    suite = analyses_mod.AnalysisSuite(m)
    suite.get("loops")
    frozen = suite.freeze()
    stmts = [st for fn in m.functions
             for st in fn.body.statements if isinstance(st, tir.Op)]
    rewrite_mod.remove_statement(m, stmts[0])
    refused = False
    try:
        frozen.get("loops")
    except analyses_mod.StaleAnalysisError:
        refused = True
    check("invalidation-frozen-view-refuses-after-mutation", refused)
    ok &= refused

    # (c) a PASS holding the stale view refuses to run (the pipeline
    # records the refusal as a decline instead of reading it)
    m = _tiny_module()
    suite = analyses_mod.AnalysisSuite(m)
    trace = passes_mod.TraceCounters("licm", True)
    ctx = passes_mod.PassContext(suite, trace)
    suite.get("loops")            # the view has a computed result
    stmts = [st for fn in m.functions
             for st in fn.body.statements if isinstance(st, tir.Op)]
    rewrite_mod.remove_statement(m, stmts[0])   # the module moves
    refused = False
    try:
        passes_mod.PASS_REGISTRY["licm"]().run(m, ctx)
    except analyses_mod.StaleAnalysisError:
        refused = True
    check("invalidation-pass-refuses-on-stale-view", refused,
          "the LICM pass raised StaleAnalysisError instead of reading "
          "the stale loops result")
    ok &= refused

    # (d) the control (IR-ANALYSIS-VALIDITY): a deliberately wrong but
    # digest-consistent analysis changes the dependent pass's outcome --
    # the passes consume what they declare
    m = _tiny_module()
    real = passes_mod.run(m, passes_mod.PassConfig(
        {n: n == "licm" for n in passes_mod.PASS_ORDER}))
    real_fired = real.passes["licm"]["fired"]
    m2 = _tiny_module()
    suite = analyses_mod.AnalysisSuite(m2)
    suite.force_result("loops", analyses_mod.LoopStructure(
        tir.Module("empty", "empty.py")))
    forced = passes_mod.run(m2, passes_mod.PassConfig(
        {n: n == "licm" for n in passes_mod.PASS_ORDER}), suite=suite)
    forced_fired = forced.passes["licm"]["fired"]
    check("invalidation-licm-consumes-loops-analysis",
          real_fired > 0 and forced_fired == 0,
          f"licm fired {real_fired} with the real loops analysis, "
          f"{forced_fired} with a forced-empty one")
    ok &= real_fired > 0 and forced_fired == 0

    # (e) the same control for DCE's liveness: an all-live liveness
    # (every value pinned by an effect site) removes nothing
    m = _witness_tir("dce_witness")
    real = passes_mod.run(m, passes_mod.PassConfig(
        {n: n == "dce" for n in passes_mod.PASS_ORDER}))
    real_fired = real.passes["dce"]["fired"]
    m2 = _witness_tir("dce_witness")
    suite = analyses_mod.AnalysisSuite(m2)

    store_op = None

    def _find_store(block):
        nonlocal store_op
        for st in block.statements:
            if isinstance(st, tir.Op) and st.op == "store":
                store_op = st
                return
            if isinstance(st, tir.If):
                _find_store(st.then)
                _find_store(st.els)
            elif isinstance(st, tir.Loop):
                _find_store(st.body)

    for fn in m2.functions:
        _find_store(fn.body)
    assert store_op is not None

    class _Site:
        def __init__(self, op):
            self.op = op
            self.path = ()
            self.slot = "operand0"

    class _AllLive:
        def __init__(self, vids):
            self.uses = {vid: [_Site(store_op)] for vid in vids}

    every_vid = set()

    def _collect(block):
        for st in block.statements:
            if isinstance(st, tir.Op):
                for r in st.results:
                    every_vid.add(r.vid)
                for o in st.operands:
                    every_vid.add(o.vid)
            elif isinstance(st, tir.If):
                _collect(st.then)
                _collect(st.els)
            elif isinstance(st, tir.Loop):
                _collect(st.body)

    for fn in m2.functions:
        for p in fn.params:
            every_vid.add(p.vid)
        _collect(fn.body)
    suite.force_result("liveness", _AllLive(sorted(every_vid)))
    forced = passes_mod.run(m2, passes_mod.PassConfig(
        {n: n == "dce" for n in passes_mod.PASS_ORDER}), suite=suite)
    forced_fired = forced.passes["dce"]["fired"]
    check("invalidation-dce-consumes-liveness-analysis",
          real_fired > 0 and forced_fired == 0,
          f"dce fired {real_fired} with the real liveness, {forced_fired} "
          f"with a forced all-live one")
    ok &= real_fired > 0 and forced_fired == 0
    check("acceptance1-invalidation-contract", ok)
    return ok


# ---------------------------------------------------------------------------
# acceptance[2]: real switches
# ---------------------------------------------------------------------------

def check_acceptance2(compilers, modules):
    on = compilers["on"]
    ok = True

    # per-pass matching inputs: disabling the pass changes the emitted
    # code, and the trace distinguishes disabled from fired-zero-times
    matching = {
        "constprop": ("cp_int_witness", {}),
        "copyprop": ("cp_copy_witness", {}),
        "strength_reduction": ("absolute_kernel", {"shape": (97,)}),
        "cse": ("vdot_kernel_complex", {"shape": (97,),
                                         "dtype": "float32"}),
        "licm": ("var_len_copy", {"shape": (3,), "dtype": "float32"}),
        "dce": ("dce_witness", {}),
    }
    for pass_name, (witness, kwargs) in matching.items():
        case = (make_case(modules[witness]) if not kwargs
                else modules[witness].make_case(**kwargs))
        why_on, staged_on = execute(on, case, 1)
        rep_on = staged_on.artifact.passes["passes"]
        fired_on = rep_on[pass_name]["fired"]
        asm_on = Path(staged_on.artifact.executable).parent.joinpath(
            "program.S").read_text()
        sha_on = staged_on.artifact.sha256
        off_compiler = PassesCompiler(
            passes_mod.PassConfig(
                {n: n != pass_name for n in passes_mod.PASS_ORDER}),
            CACHE / f"off-{pass_name}")
        why_off, staged_off = execute(off_compiler, case, 1)
        rep_off = staged_off.artifact.passes["passes"][pass_name]
        asm_off = Path(staged_off.artifact.executable).parent.joinpath(
            "program.S").read_text()
        sha_off = staged_off.artifact.sha256
        good = (not why_on and not why_off
                and fired_on is not None and fired_on > 0
                and rep_off["enabled"] is False
                and rep_off["fired"] is None
                and sha_off != sha_on and asm_off != asm_on)
        check(f"switch-{pass_name}-changes-emitted-code", good,
              f"on: fired={fired_on} (compare {why_on or 'PASS'}); "
              f"off: enabled={rep_off['enabled']} "
              f"fired={rep_off['fired']}; artifact differs: "
              f"{sha_off != sha_on}; assembly differs: "
              f"{asm_off != asm_on}")
        ok &= good

    # fired-zero-times vs disabled: a pass that examines an input and
    # finds nothing still reports enabled with fired=0
    case = modules["absolute_kernel"].make_case(shape=(97,))
    why, staged = execute(on, case, 1)
    rep = staged.artifact.passes["passes"]
    cse_report = rep["cse"]
    licm_report = rep["licm"]
    zero_ok = (not why
               and cse_report["enabled"] is True
               and cse_report["fired"] == 0
               and licm_report["enabled"] is True
               and licm_report["fired"] == 0)
    check("switch-fired-zero-is-not-disabled", zero_ok,
          f"cse={cse_report['enabled']}/{cse_report['fired']} "
          f"licm={licm_report['enabled']}/{licm_report['fired']}")
    ok &= zero_ok

    # the configuration is part of the artifact identity: no silent
    # reuse across configurations, hits within one
    cfg_a = passes_mod.PassConfig()
    cfg_b = passes_mod.PassConfig({"cse": False})
    comp = PassesCompiler(cfg_a, CACHE / "identity")
    case = make_case(modules["cp_int_witness"])
    a1 = comp.compile_case(case)
    a2 = comp.compile_case(case)
    comp_b = PassesCompiler(cfg_b, CACHE / "identity")
    b1 = comp_b.compile_case(case)
    good = (a2.cache_hit and comp.compile_count == 1
            and not b1.cache_hit and comp_b.compile_count == 1
            and a1.sha256 == a2.sha256 and b1.sha256 != a1.sha256)
    check("switch-configuration-in-artifact-identity", good,
          f"same-config hit={a2.cache_hit}; other-config hit="
          f"{b1.cache_hit}; bytes differ={b1.sha256 != a1.sha256}")
    ok &= good

    # the environment switch is read and lands in the identity
    env_off = passes_mod.PassConfig.from_env(
        {"A100C_PASS_STRENGTH_REDUCTION": "off"})
    env_on = passes_mod.PassConfig.from_env({})
    good = (env_off.identity_part() != env_on.identity_part()
            and "strength_reduction-off" in env_off.identity_part()
            and env_on.identity_part() == "passes=default")
    check("switch-env-namespace", good,
          f"from_env: {env_off.identity_part()} vs {env_on.identity_part()}")
    ok &= good
    check("acceptance2-real-switches", ok)
    return ok


# ---------------------------------------------------------------------------
# acceptance[3]: the representative corpus subset
# ---------------------------------------------------------------------------

SUBSET = [
    # (path, make_case kwargs, feature classes covered)
    ("suite/dev/absolute_kernel.py", {},
     "elementwise/mask/where"),
    ("suite/dev/var_len_copy.py", {"shape": (3,), "dtype": "float32"},
     "flow.loop/dynamic-range"),
    ("suite/dev/reduce_kernel.py", {"shape": (97,), "dtype": "float32"},
     "red.sum + if_pid"),
    ("suite/dev/row_reduce_min_kernel.py",
     {"shape": (17, 128), "dtype": "float32"}, "red.maxmin + axis"),
    ("suite/dev/bincount_kernel.py", {}, "atomics"),
    ("suite/dev/asinh_kernel.py", {"shape": (17,)},
     "math.transcendental"),
    ("suite/dev/complex_pack.py", {}, "layout split/join"),
    ("suite/dev/bitcast.py", {}, "dtype conversions/bitcast"),
    ("suite/dev/vdot_kernel_complex.py", {"shape": (97,),
                                          "dtype": "float32"},
     "persistent reduce (complex)"),
    ("suite/perf/mean.py", {"shape": (4, 97), "dtype": "float32"},
     "red.sum (perf tier)"),
]


def check_acceptance3(compilers, modules, plain):
    on = compilers["on"]
    off = compilers["off"]
    ok = True
    for rel, kwargs, classes in SUBSET:
        module = _load(ROOT / "ops" / rel)
        case = module.make_case(**kwargs)
        msgs = []
        for label, compiler in (("off", off), ("on", on)):
            for threads in (1, 4):
                why, _staged = execute(compiler, case, threads)
                if why:
                    msgs.append(f"{label} t={threads}: {why}")
        # with every pass disabled the artifact is byte-identical to the
        # plain driver's: the general path is intact
        compile_case = {k: v for k, v in case.items()
                        if k not in ("expected", "oracle_args")}
        art_plain = plain.compile_case(compile_case)
        art_off = off.compile_case(compile_case)
        art_on = on.compile_case(compile_case)
        same = art_plain.sha256 == art_off.sha256
        rep = art_off.passes["passes"]
        all_disabled = all(p["enabled"] is False for p in rep.values())
        fired = {p: art_on.passes["passes"][p]["fired"]
                 for p in passes_mod.PASS_ORDER}
        good = not msgs and same and all_disabled
        check(f"corpus-subset-{rel.split('/')[-1][:-3]}", good,
              (f"{classes} | " if classes else "")
              + (msgs[0] if msgs else
                 ("" if same else "all-off bytes differ from the driver"))
              + ("" if all_disabled else " | off config not fully disabled")
              + " | on-fires: "
              + " ".join(f"{p}:{v}" for p, v in fired.items() if v))
        EVIDENCE["cases"].append(
            {"operator": rel, "classes": classes,
             "compare": msgs[0] if msgs else "PASS",
             "general-path-intact": same,
             "passes-fired": {p: v for p, v in fired.items() if v}})
        ok &= good

    # the dot/matrix class through the same both-configuration protocol
    case = make_case(modules["dot_passes"])
    msgs = []
    for label, compiler in (("off", compilers["off"]),
                            ("on", compilers["on"])):
        for threads in (1, 4):
            why, _staged = execute(compiler, case, threads)
            if why:
                msgs.append(f"{label} t={threads}: {why}")
    check("corpus-subset-dot-matrix-probe", not msgs,
          "dot/matrix class (the corpus dot operators sit behind the "
          "recorded dots-in-runtime-loops boundary; the probe carries "
          "its own numpy reference)"
          + (f" | {msgs[0]}" if msgs else ""))
    ok &= not msgs
    check("acceptance3-corpus-subset-both-configurations", ok)
    return ok


# ---------------------------------------------------------------------------

def main() -> int:
    try:
        modules = _witness_modules()
        corpus = {}
        for rel, kwargs, _c in SUBSET:
            name = rel.split("/")[-1][:-3]
            corpus[name] = _load(ROOT / "ops" / rel)
        modules.update({"absolute_kernel": corpus["absolute_kernel"],
                        "var_len_copy": corpus["var_len_copy"],
                        "vdot_kernel_complex":
                            corpus["vdot_kernel_complex"]})

        compilers = {
            "on": PassesCompiler(passes_mod.PassConfig(), CACHE / "on"),
            "off": PassesCompiler(
                passes_mod.PassConfig(
                    {n: False for n in passes_mod.PASS_ORDER}),
                CACHE / "off"),
        }
        plain = Compiler(options=CompileOptions(cache_dir=str(CACHE /
                                                              "plain")))

        check_acceptance0(compilers, modules)
        check_acceptance1()
        check_acceptance2(compilers, modules)
        check_acceptance3(compilers, modules, plain)

        (WORK / "evidence.json").write_text(
            json.dumps(EVIDENCE, indent=1, sort_keys=True) + "\n")
        print(f"# evidence: {WORK / 'evidence.json'}")
    finally:
        shutil.rmtree(WORK, ignore_errors=True)
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} check(s)")
        return 1
    print("test_passes_basic: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
