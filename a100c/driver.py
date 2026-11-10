"""The a100c driver: pipeline orchestration, artifact cache, factory shim.

Pipeline (one compile, from the case payload the a100_support transport
hands over -- never the expected outputs):

  source (AST) -> specialization (identity = meta tier) -> TIR (verified)
  -> grid model (provenance-checked, self-checked) -> execution plan
  -> MIR (verified) -> legalisation -> selection -> allocation -> emission
  -> cross as + ld + precompiled runtime -> ELF64-little-RISC-V

Cache identity (BE-ARTIFACT-IDENTITY, F043): specialization identity +
compiler revision (digest of the code-affecting files, not the whole tree)
+ target-model version + compile options that affect codegen + the
argument-layout digest.  Shapes, grid values, buffer contents, scalar
values and worker counts are runtime inputs and NEVER enter the key: one
artifact serves every case of an identity and every thread count (the
program computes its partition from --threads).

Per-stage dumps (TIR, plan, MIR after each backend stage, the assembly
listing) are written beside the artifact with source attribution
(IR-OBSERVABILITY); identical inputs produce identical artifact bytes
(RT-DETERMINISM).
"""
from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from a100c.backend import allocate as alloc_mod
from a100c.backend import emit as emit_mod
from a100c.backend import legalize as legal_mod
from a100c.backend import select as select_mod
from a100c.frontend import lower_tir, source as fe_source, specialize as fe_spec
from a100c.frontend.source import FrontendError
from a100c.ir import dump as tir_dump
from a100c.ir import mir, tir
from a100c.lower import binding as binding_mod
from a100c.lower import vectorize
from a100c.lower.vectorize import LowerOptions, VectorizeError
from a100c.plan import grid as grid_mod
from a100c.plan import partition as part_mod
from a100c.plan.grid import GridError
from a100c.target import DEFAULT_TARGET, TargetModel

__all__ = ["CompileOptions", "Compiler", "make_compiler", "compiler_revision",
           "PipelineError"]

ROOT = Path(__file__).resolve().parents[1]

#: code-affecting files of the compiler revision (never the whole tree)
_REVISION_FILES = (
    "a100c/target.py", "a100c/ir/mir.py", "a100c/ir/tir.py",
    "a100c/plan/partition.py", "a100c/plan/grid.py",
    "a100c/lower/binding.py", "a100c/lower/addresses.py",
    "a100c/lower/scalar.py", "a100c/lower/matrix.py",
    "a100c/lower/vectorize.py",
    "a100c/backend/repertoire.py", "a100c/backend/legalize.py",
    "a100c/backend/select.py", "a100c/backend/allocate.py",
    "a100c/backend/emit.py", "a100c/driver.py",
    "a100c/frontend/source.py", "a100c/frontend/specialize.py",
    "a100c/frontend/types.py", "a100c/frontend/shapes.py",
    "a100c/frontend/surface.py", "a100c/frontend/lower_tir.py",
    "a100c/frontend/gridmodel.py",
    "a100c/runtime/build.py", "a100c/runtime/a100rt.h",
    "a100c/runtime/bundle.c", "a100c/runtime/pool.c", "a100c/runtime/main.c",
)


class PipelineError(Exception):
    """A located compile refusal from any stage (never a silent guess)."""

    def __init__(self, loc, construct: str, message: str):
        super().__init__(f"{construct}: {message}"
                         + (f" (at {loc})" if loc else ""))
        self.loc = loc
        self.construct = construct
        self.message = message


@dataclass
class CompileOptions:
    #: where artifacts + dumps are cached (default a100c/cache)
    cache_dir: Optional[str] = None
    #: write per-stage dumps (TIR, plan, MIR stages, assembly)
    dumps: bool = True
    #: witness-only degraded build (tools/check_masked_tails.py); recorded
    #: in the artifact identity so it can never leak into the normal cache
    witness_drop_tail_predicates: bool = False
    #: witness-only degraded build (tools/check_stage_barriers.py): the
    #: stage barrier call is dropped from the two-phase split path so the
    #: cross-worker visibility race becomes observable; recorded in the
    #: artifact identity when set
    witness_drop_stage_barrier: bool = False
    #: witness-only degraded build (T011 test_atomics.py): the masked
    #: block atomic's disabled-lane address redirection is dropped so the
    #: out-of-range lanes touch a poisoned guard region; recorded in the
    #: artifact identity when set
    witness_drop_atomic_masks: bool = False
    #: the B-operand staging pack rides the vector strided load (vlse,
    #: the matmul optimization round); True forces the scalar per-element
    #: pack loops -- the on/off contrast and rollback path.  Recorded in
    #: the artifact identity when set.  Env route (the A100C_PASS_*
    #: switches' pattern): A100C_MATRIX_PACK=scalar.
    matrix_scalar_pack: bool = False
    #: the fp32 transcendental vector-polynomial path (the unified
    #: optimization round's W1); True forces the per-element libm vmath
    #: path -- the on/off contrast and rollback.  Env route:
    #: A100C_VMATH_LIBM=1.
    vmath_libm: bool = False

    def __post_init__(self):
        if os.environ.get("A100C_MATRIX_PACK", "").strip().lower() in \
                ("scalar", "1", "true", "yes"):
            self.matrix_scalar_pack = True
        if os.environ.get("A100C_VMATH_LIBM", "").strip().lower() in \
                ("libm", "1", "true", "yes", "on"):
            self.vmath_libm = True
    def identity_part(self) -> str:
        parts = []
        if self.witness_drop_tail_predicates:
            parts.append("witness-drop-tail-predicates")
        if self.witness_drop_stage_barrier:
            parts.append("witness-drop-stage-barrier")
        if self.witness_drop_atomic_masks:
            parts.append("witness-drop-atomic-masks")
        if self.matrix_scalar_pack:
            parts.append("matrix-scalar-pack")
        if self.vmath_libm:
            parts.append("vmath-libm")
        if not self.dumps:
            parts.append("no-dumps")      # dumps do not affect the ELF
        return ",".join(parts) if parts else "default"


def compiler_revision() -> str:
    """Digest of the code-affecting files (not the whole tree)."""
    digest = hashlib.sha256()
    for rel in _REVISION_FILES:
        path = ROOT / rel
        if path.is_file():
            digest.update(rel.encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()[:16]


def _load_runtime_build():
    import importlib.util
    path = ROOT / "a100c" / "runtime" / "build.py"
    spec = importlib.util.spec_from_file_location("a100c_runtime_build", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@dataclass
class _Artifact:
    executable: Path
    arguments: Tuple[str, ...] = ("--bundle", "{bundle}", "--threads",
                                  "{threads}")
    provenance: str = ""
    identity: str = ""
    cache_hit: bool = False
    sha256: str = ""
    compile_ms: int = 0
    stage_stats: Dict[str, object] = field(default_factory=dict)


class Compiler:
    """The compile_case protocol target (a100_support/native_device)."""

    def __init__(self, target: Optional[TargetModel] = None,
                 options: Optional[CompileOptions] = None):
        self.target = target or DEFAULT_TARGET
        self.options = options or CompileOptions()
        self.cache_dir = Path(self.options.cache_dir) if self.options.cache_dir \
            else ROOT / "a100c" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._runtime = _load_runtime_build()
        self.compile_count = 0
        self.cache_hits = 0

    # -- public protocol -------------------------------------------------------
    def compile_case(self, case: dict) -> _Artifact:
        """Compile one case payload to a cached native executable.

        Idempotent per artifact identity: a second call for the same identity
        is a cache lookup (no toolchain invocation).
        """
        started = time.monotonic()
        key_material = self._identity(case)
        entry = self.cache_dir / key_material["key"]
        marker = entry / "artifact.json"
        executable = entry / "operator_exec"
        if marker.is_file() and executable.is_file():
            meta = json.loads(marker.read_text())
            self.cache_hits += 1
            return _Artifact(executable=executable,
                             provenance=meta["provenance"],
                             identity=meta["identity"], cache_hit=True,
                             sha256=meta["sha256"],
                             stage_stats=meta.get("stages", {}))
        self.compile_count += 1
        entry.mkdir(parents=True, exist_ok=True)
        stages = self._compile_into(case, entry, key_material)
        elapsed = int((time.monotonic() - started) * 1000)
        meta = {"identity": key_material["specialization"],
                "key": key_material["key"],
                "provenance": f"a100c/{compiler_revision()}",
                "sha256": _sha256_file(executable),
                "stages": stages, "compile_ms": elapsed}
        marker.write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n")
        return _Artifact(executable=executable,
                         provenance=meta["provenance"],
                         identity=meta["identity"], cache_hit=False,
                         sha256=meta["sha256"], compile_ms=elapsed,
                         stage_stats=stages)

    # -- identity ------------------------------------------------------------------
    def _identity(self, case: dict) -> Dict[str, str]:
        src = self._load_source(case)
        spec = fe_spec.specialize(src, case)
        layout = binding_mod.argument_layout(case, spec)
        key = hashlib.sha256(
            "a100c-artifact/1\n".encode()
            + f"specialization={spec.identity}\n".encode()
            + f"revision={compiler_revision()}\n".encode()
            + f"target={self.target.model_version}\n".encode()
            + f"options={self.options.identity_part()}\n".encode()
            + f"layout={layout.digest}\n".encode()
            + f"abi={self.target.abi}\n".encode()
        ).hexdigest()
        return {"key": key, "specialization": spec.identity,
                "layout": layout.digest}

    # -- the pipeline -----------------------------------------------------------------
    def _load_source(self, case: dict):
        kernel = case.get("kernel")
        path = None
        # unwrap the kernel wrapper chain: a bare @triton.jit hands the
        # raw function (its __code__ names the operator file); an
        # @triton.autotune operator hands an Autotuner whose .fn is the
        # JITFunction whose .fn is the raw function -- ONE unwrap level
        # never reached the source, so the 11 autotune operators could
        # not load their compile unit at all (the T024 'case' class).
        # The chosen config is the specialization's deterministic pick
        # (frontend.specialize.chosen_autotune_config: the FIRST declared
        # config; correctness-neutral, part of the identity, never
        # re-tuned per key), so the unwrap only needs the source file.
        fn = kernel
        for _ in range(8):
            code = getattr(fn, "__code__", None)
            if code is not None and code.co_filename:
                path = code.co_filename
                break
            nxt = getattr(fn, "fn", None)
            if nxt is None or nxt is fn:
                break
            fn = nxt
        if path is None:
            raise PipelineError(
                None, "case",
                "the case carries no kernel function with a source file; "
                "the AST frontend cannot load the compile unit")
        try:
            return fe_source.load_operator(path)
        except FrontendError as exc:
            raise PipelineError(f"{exc.path}:{exc.line}:{exc.col}",
                                exc.construct, exc.message) from None

    def _compile_into(self, case: dict, entry: Path,
                      key_material: Dict[str, str]) -> Dict[str, object]:
        dumps = self.options.dumps
        src = self._load_source(case)
        # 1. specialization
        spec = fe_spec.specialize(src, case)
        # 2. TIR (frontend) + verification
        try:
            tir_module = lower_tir.lower(src, spec)
        except FrontendError as exc:
            raise PipelineError(f"{exc.path}:{exc.line}:{exc.col}",
                                exc.construct, exc.message) from None
        errors = tir.verify_module(tir_module)
        if errors:
            raise PipelineError(None, "tir-verifier", str(errors[0]))
        if dumps:
            (entry / "stage.tir.txt").write_text(tir_dump.dump_module(tir_module))
        # 3. grid model (provenance-checked, self-checked).  T039: a grid
        #    whose axes are individually untraceable but whose product is
        #    bundle-visible flattens to one product axis when the kernel's
        #    whole pid surface is the C-order linear index -- the TIR is
        #    then rewritten to program_id(0) before the MIR lowering
        try:
            grid = grid_mod.extract_grid(src, case, tir_module=tir_module)
        except GridError as exc:
            raise PipelineError(f"{exc.path}:{exc.line}:{exc.col}",
                                exc.construct, exc.message) from None
        if grid.linear_ndim:
            grid_mod.apply_linear_flattening(tir_module, grid.linear_ndim)
            errors = tir.verify_module(tir_module)
            if errors:
                raise PipelineError(
                    None, "tir-verifier-post-flatten", str(errors[0]))
        # 4. execution plan (work partition; the chunk plan is refined by the
        #    lowering from the TIR block form)
        plan = part_mod.ExecutionPlan()
        # 5. argument layout
        layout = binding_mod.argument_layout(case, spec)
        # 6. TIR -> MIR + verification
        options = LowerOptions(
            witness_drop_tail_predicates=self.options.witness_drop_tail_predicates,
            witness_drop_stage_barrier=self.options.witness_drop_stage_barrier,
            witness_drop_atomic_masks=self.options.witness_drop_atomic_masks,
            # the identity records these switches, so the compile must
            # honor them here too (the plain-driver path predated the
            # matrix pack switch and silently ignored it; W1 adds both)
            matrix_scalar_pack=self.options.matrix_scalar_pack,
            vmath_libm=self.options.vmath_libm)
        try:
            mir_module = vectorize.lower_to_mir(tir_module, plan, self.target,
                                                layout, grid, options)
        except VectorizeError as exc:
            raise PipelineError(exc.loc, exc.construct, exc.message) from None
        except vectorize.scalar_mod.ScalarLoweringError as exc:
            # a located scalar-core refusal surfacing through the vector
            # path (T012: the widened conversion matrix reaches deeper
            # before refusing)
            raise PipelineError(None, "scalar-lowering", str(exc)) from None
        from a100c.lower import matrix as matrix_verify
        errors = matrix_verify.verify_module(mir_module)
        if errors:
            raise PipelineError(None, "mir-verifier", str(errors[0]))
        if dumps:
            (entry / "stage.plan.txt").write_text(
                json.dumps({"plan": plan.describe(),
                            "grid": grid.describe(),
                            "layout": layout.describe(),
                            "target": self.target.describe()}, indent=2,
                           sort_keys=True) + "\n")
            (entry / "stage.mir.lowered.txt").write_text(mir.dump_module(mir_module))
        # 7. legalisation (contract: after it, everything is in the repertoire)
        report = legal_mod.legalize(mir_module)
        from a100c.lower import matrix as matrix_verify
        errors = matrix_verify.verify_module(mir_module)
        if errors:
            raise PipelineError(None, "mir-verifier-post-legalize",
                                str(errors[0]))
        # 8. selection (one generic matcher over the repertoire table)
        try:
            selection = select_mod.select(mir_module)
        except select_mod.SelectionError as exc:
            raise PipelineError(exc.loc, exc.construct, exc.message) from None
        if dumps:
            (entry / "stage.mir.legalized.txt").write_text(mir.dump_module(mir_module))
        # 9. allocation (interference + spill/split against the budget)
        try:
            allocation = alloc_mod.allocate(mir_module, self.target)
        except alloc_mod.AllocationError as exc:
            raise PipelineError(exc.loc, "allocation", exc.message) from None
        if dumps:
            (entry / "stage.mir.allocated.txt").write_text(
                mir.dump_module(mir_module)
                + "\n// allocation: " + json.dumps(allocation.describe(),
                                                   sort_keys=True) + "\n")
        # 10. emission (complete program-level assembly).  T030: an
        #     emission refusal is located (construct + source position) --
        #     surfaced as a PipelineError so the census counts it as a
        #     located refusal, never as an unclassified crash
        header = [
            f"# a100c emitted program: {tir_module.name}",
            f"# source: {src.rel_path}",
            f"# specialization identity: {spec.identity}",
            f"# compiler revision: {compiler_revision()}",
            f"# target model: {self.target.model_version} "
            f"(VLEN={self.target.vlen_bits}, file="
            f"{self.target.vector_file_bytes}B)",
            f"# options: {self.options.identity_part()}",
            f"# argument layout: {layout.digest}",
            "# every instruction below traces to a selected MIR op: "
            "[opN] carries the source location",
        ]
        try:
            program = emit_mod.emit_assembly(
                mir_module, allocation, self.target,
                workspace=(plan.workspace_private,
                           plan.workspace_shared),
                selection=selection, header=header)
        except emit_mod.EmissionError as exc:
            raise PipelineError(exc.loc, f"emission:{exc.construct}",
                                exc.message) from None
        asm_path = entry / "program.S"
        asm_path.write_text(program.text)
        # 11. cross as + ld + precompiled runtime -> ELF
        obj, tools, assembled, invocations = self._runtime.assemble_operator(
            asm_path, build_dir=self.cache_dir / "build")
        info = self._runtime.link_operator([obj], entry / "operator_exec",
                                           build_dir=self.cache_dir / "build",
                                           extra_invocations=invocations)
        stages = {
            "specialization": spec.identity,
            "tir_ops": sum(1 for fn in tir_module.functions
                           for st in fn.body.statements if isinstance(st, tir.Op)),
            "grid": grid.describe(),
            "legalize": report.describe(),
            "selection": mir_module.meta.get("selection", {}),
            "allocation": allocation.stats,
            "emission": program.stats,
            "address_trees": mir_module.meta.get("address_trees", []),
            "witness": mir_module.meta.get("witness", "default"),
            "matrix_segments": mir_module.meta.get("matrix_segments", []),
            "matrix_staging_offset":
                mir_module.meta.get("matrix_staging_offset"),
            "toolchain": {
                "as": str(tools["as"]),
                "ld": str(tools["gcc"]),
                "invocations": [" ".join(str(p) for p in cmd)
                                for cmd in info["invocations"]],
            },
        }
        if dumps:
            (entry / "stage.selection.txt").write_text(
                json.dumps({"mnemonics": selection_mnemonics(selection),
                            "per_op": {str(idx): s.mnemonic
                                       for idx, s in sorted(selection.items())}},
                           indent=2) + "\n")
        return stages


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def selection_mnemonics(selection: Dict[int, "select_mod.Selected"]) -> List[str]:
    return sorted({s.mnemonic for s in selection.values()})


def make_compiler() -> Compiler:
    """The factory shim: A100_COMPILER_FACTORY=a100c.driver:make_compiler."""
    return Compiler()
