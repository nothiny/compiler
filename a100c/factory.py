"""a100c/factory.py -- the production compile path (T017).

``make_compiler()`` is the object ``a100_support.native_device.make_device``
constructs through ``A100_COMPILER_FACTORY=a100c.factory:make_compiler``; it
returns the ``compile_case(case) -> artifact`` protocol the native device
stages whole cases with (artifact arguments ``('--bundle','{bundle}',
'--threads','{threads}')``).

The compile path is the driver's own stage sequence with the T015 basic-pass
seam inserted between TIR verification and the lowering (the integration seam
``a100c/tests/test_passes_basic.py`` declared for this module):

  source (AST) -> specialization -> TIR -> verify
    -> [constprop, copyprop, strength_reduction, cse, licm, dce] -> verify
    -> grid model -> plan -> argument layout -> MIR -> verify
    -> legalise -> verify -> select -> allocate -> emit
    -> cross as + ld + precompiled runtime -> ELF64-little-RISC-V

Artifact identity = the driver's identity (specialization + compiler revision
+ target model + options + argument layout) + the pass configuration
(MECH-PASS-ATTRIBUTION: ``A100C_PASS_<NAME>=off`` changes the key, so an
artifact compiled with other options is never a silent cache hit).  With every
pass disabled the emitted program is byte-identical to the plain driver's
(the general path stays intact, MECH-GENERAL-PATH-FIRST).

Environment:
  A100C_CACHE_DIR     artifact cache root (default ``a100c/cache``); isolated
                      roots keep cold/warm compile-count accounting honest.
  A100C_PASS_<NAME>   ``off``/``0``/``false``/``no`` disables one basic pass.

This module (and everything it imports) contains no torch and no reference
device: the reference service never substitutes for candidate execution
(F049/F052).  Shapes, grid values, buffer contents and scalar values never
enter the artifact identity; the worker count is a launch argument.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Dict, Optional

from a100c.backend import allocate as alloc_mod
from a100c.backend import emit as emit_mod
from a100c.backend import legalize as legal_mod
from a100c.backend import select as select_mod
from a100c.driver import Compiler, CompileOptions, PipelineError, \
    compiler_revision, selection_mnemonics
from a100c.frontend import lower_tir, specialize as fe_spec
from a100c.frontend.source import FrontendError
from a100c.ir import dump as tir_dump
from a100c.ir import mir, tir
from a100c.lower import binding as binding_mod
from a100c.lower import vectorize
from a100c.lower.vectorize import LowerOptions, VectorizeError
from a100c.passes import pipeline as passes_mod
from a100c.plan import grid as grid_mod
from a100c.plan import partition as part_mod
from a100c.plan.grid import GridError

__all__ = ["FactoryCompiler", "make_compiler"]

ROOT = Path(__file__).resolve().parents[1]


class FactoryCompiler(Compiler):
    """``Compiler`` with the basic-pass seam and a pass-aware cache key.

    Everything except ``_identity`` and ``_compile_into`` is the driver's own
    code: the cache protocol, the counters (``compile_count`` /
    ``cache_hits``) and the marker format are inherited, so the scan driver's
    accounting measures this class exactly as it measures the plain driver.
    """

    def __init__(self, target=None, options: Optional[CompileOptions] = None,
                 pass_config: Optional["passes_mod.PassConfig"] = None):
        if options is None:
            # an isolated cache root keeps cold/warm compile counting honest
            # without touching the shared on-disk cache
            cache = os.environ.get("A100C_CACHE_DIR")
            if cache:
                options = CompileOptions(cache_dir=cache)
        super().__init__(target=target, options=options)
        self.pass_config = pass_config or passes_mod.PassConfig.from_env()

    # -- identity: the driver's key plus the pass configuration ---------------
    def _identity(self, case: dict) -> Dict[str, str]:
        base = super()._identity(case)
        digest = hashlib.sha256(
            ("a100c-factory/1\n" + base["key"] + "|"
             + self.pass_config.identity_part()).encode()).hexdigest()
        return {"key": digest, "specialization": base["specialization"],
                "layout": base["layout"],
                "passes": self.pass_config.identity_part()}

    # -- the pipeline: the driver's stages with the T015 seam ------------------
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
        # 3. the T015 seam: the basic passes run on verified TIR, and the
        #    result is verified again (a rewrite that breaks the contract is
        #    a pass defect, refused here -- never a silent miscompile)
        pass_report = passes_mod.run(tir_module, self.pass_config)
        errors = tir.verify_module(tir_module)
        if errors:
            raise PipelineError(None, "tir-verifier-post-passes",
                                str(errors[0]))
        if dumps:
            (entry / "stage.tir.txt").write_text(tir_dump.dump_module(tir_module))
            (entry / "stage.passes.txt").write_text(
                json.dumps(pass_report.describe(), indent=2, sort_keys=True)
                + "\n")
        # 4. grid model (provenance-checked, self-checked)
        try:
            grid = grid_mod.extract_grid(src, case)
        except GridError as exc:
            raise PipelineError(f"{exc.path}:{exc.line}:{exc.col}",
                                exc.construct, exc.message) from None
        # 5. execution plan (work partition)
        plan = part_mod.ExecutionPlan()
        # 6. argument layout
        layout = binding_mod.argument_layout(case, spec)
        # 7. TIR -> MIR + verification
        options = LowerOptions(
            witness_drop_tail_predicates=self.options.witness_drop_tail_predicates,
            witness_drop_stage_barrier=self.options.witness_drop_stage_barrier,
            witness_drop_atomic_masks=self.options.witness_drop_atomic_masks)
        try:
            mir_module = vectorize.lower_to_mir(tir_module, plan, self.target,
                                                layout, grid, options)
        except VectorizeError as exc:
            raise PipelineError(exc.loc, exc.construct, exc.message) from None
        except vectorize.scalar_mod.ScalarLoweringError as exc:
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
        # 8. legalisation
        report = legal_mod.legalize(mir_module)
        errors = matrix_verify.verify_module(mir_module)
        if errors:
            raise PipelineError(None, "mir-verifier-post-legalize",
                                str(errors[0]))
        # 9. selection (one generic matcher over the repertoire table)
        try:
            selection = select_mod.select(mir_module)
        except select_mod.SelectionError as exc:
            raise PipelineError(exc.loc, exc.construct, exc.message) from None
        if dumps:
            (entry / "stage.mir.legalized.txt").write_text(mir.dump_module(mir_module))
        # 10. allocation
        try:
            allocation = alloc_mod.allocate(mir_module, self.target)
        except alloc_mod.AllocationError as exc:
            raise PipelineError(exc.loc, "allocation", exc.message) from None
        if dumps:
            (entry / "stage.mir.allocated.txt").write_text(
                mir.dump_module(mir_module)
                + "\n// allocation: " + json.dumps(allocation.describe(),
                                                   sort_keys=True) + "\n")
        # 11. emission (complete program-level assembly).  The pass line is
        #     appended only when a pass is enabled so the all-off build stays
        #     byte-identical to the plain driver's (MECH-GENERAL-PATH-FIRST).
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
        if any(self.pass_config.enabled.values()):
            header.append(f"# passes: {self.pass_config.identity_part()}")
        # T030: an emission refusal is located (construct + source
        # position) -- surfaced as a PipelineError so the census counts it
        # as a located refusal, never as an unclassified crash
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
        # 12. cross as + ld + precompiled runtime -> ELF
        obj, tools, assembled, invocations = self._runtime.assemble_operator(
            asm_path, build_dir=self.cache_dir / "build")
        info = self._runtime.link_operator([obj], entry / "operator_exec",
                                           build_dir=self.cache_dir / "build",
                                           extra_invocations=invocations)
        stages = {
            "specialization": spec.identity,
            "passes": pass_report.describe(),
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


def make_compiler() -> FactoryCompiler:
    """The factory shim: ``A100_COMPILER_FACTORY=a100c.factory:make_compiler``."""
    return FactoryCompiler()
