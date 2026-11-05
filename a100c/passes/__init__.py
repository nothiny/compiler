"""a100c.passes: the basic optimization passes on TIR (T015).

Six passes -- cse, dce, constprop, copyprop, strength_reduction, licm --
under their legality conditions, with one shared analysis owner
(``analyses``), per-pass switches (``A100C_PASS_<NAME>=off``) and trace
counters (fired/declined with the unmet conditions).  Correctness-only
scope: these are ordinary implementation work, never a measured
performance round (F055).

The integration seam: ``pipeline.run(tir_module, config)`` runs between
the frontend's verified TIR and the lowering; ``config.identity_part()``
is the fragment every artifact identity must carry so an artifact
compiled with other pass options is never silently reused.
"""
from a100c.passes.analyses import (ANALYSIS_NAMES, AnalysisSuite,  # noqa: F401
                                   FrozenAnalyses, StaleAnalysisError,
                                   module_digest)
from a100c.passes.pipeline import (MAX_ROUNDS, PASS_ORDER,  # noqa: F401
                                   PASS_REGISTRY, PassConfig, PassContext,
                                   PassPipeline, PipelineReport,
                                   TraceCounters, run)

__all__ = [
    "ANALYSIS_NAMES", "AnalysisSuite", "FrozenAnalyses", "StaleAnalysisError",
    "module_digest", "MAX_ROUNDS", "PASS_ORDER", "PASS_REGISTRY",
    "PassConfig", "PassContext", "PassPipeline", "PipelineReport",
    "TraceCounters", "run",
]
