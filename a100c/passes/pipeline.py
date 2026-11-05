"""The basic-pass pipeline: registration, ordering and switches (T015).

The six basic optimisations run on TIR between the frontend's verified
output and the lowering, as ordinary implementation work under the
correctness-only scope (IR-BASIC-OPTIMIZATIONS): no timing, no counter
quota, no measured round -- legality and executed comparisons only.

* Registration and order: ``PASS_ORDER`` is the declared sequence
  (constprop first -- it creates the constants the others consume;
  copyprop and strength_reduction clean value identities; cse dedupes;
  licm hoists; dce removes what the others made dead).  The pipeline
  iterates the sequence to a fixpoint (bounded, ``MAX_ROUNDS``), so a
  hoist that exposes a constant or a copy that exposes a duplicate is
  picked up by the next round.
* Switches: ``A100C_PASS_<NAME>=off`` (also ``0``/``false``/``no``)
  disables one pass; ``PassConfig.from_env()`` reads them,
  ``PassConfig.identity_part()`` is the stable identity fragment every
  artifact key must carry (MECH-PASS-ATTRIBUTION: a pass configuration
  is part of the artifact identity, so an artifact compiled with other
  options is never silently reused).
* Trace counters: every pass reports ``fired`` (rewrites applied) and
  ``declined`` (legality refusals, each with its unmet condition) --
  ``fired=0`` with ``enabled=True`` is an examined-but-ineligible
  input, ``enabled=False`` is a disabled pass; the two never look
  alike.
* Analyses: one shared owner (``a100c.passes.analyses``) computes the
  dominance/liveness/loop/memory facts; each pass declares the analyses
  it consumes and invalidates, the pipeline re-freezes the shared view
  after every mutating pass, and a pass that meets a stale view refuses
  (``StaleAnalysisError`` -> a recorded decline, never a stale read).
"""
from __future__ import annotations

import os
from typing import Dict, List, Optional

from a100c.ir import tir
from a100c.passes import cse as cse_mod
from a100c.passes import constprop as constprop_mod
from a100c.passes import copyprop as copyprop_mod
from a100c.passes import dce as dce_mod
from a100c.passes import licm as licm_mod
from a100c.passes import strength_reduction as sr_mod
from a100c.passes.analyses import ANALYSIS_NAMES, AnalysisSuite, \
    FrozenAnalyses, StaleAnalysisError

__all__ = ["PassConfig", "PassPipeline", "PassContext", "TraceCounters",
           "PipelineReport", "PASS_ORDER", "PASS_REGISTRY", "run",
           "MAX_ROUNDS"]

#: the declared order
PASS_ORDER = ("constprop", "copyprop", "strength_reduction", "cse",
              "licm", "dce")

#: the registered passes
PASS_REGISTRY = {
    "constprop": constprop_mod.ConstPropPass,
    "copyprop": copyprop_mod.CopyPropPass,
    "strength_reduction": sr_mod.StrengthReductionPass,
    "cse": cse_mod.CSEPass,
    "licm": licm_mod.LICMPass,
    "dce": dce_mod.DCEPass,
}

MAX_ROUNDS = 4

_OFF = {"off", "0", "false", "no", ""}


class TraceCounters:
    """fired / declined with the recorded unmet conditions."""

    def __init__(self, name: str, enabled: bool):
        self.name = name
        self.enabled = enabled
        self.fired = 0
        self.declined = 0
        self.reasons: Dict[str, int] = {}
        self.samples: List[str] = []

    def record_fired(self, what: str) -> None:
        self.fired += 1
        if len(self.samples) < 24:
            self.samples.append(what)

    def record_decline(self, reason: str) -> None:
        self.declined += 1
        key = reason.split("(")[0].strip()
        self.reasons[key] = self.reasons.get(key, 0) + 1

    def describe(self) -> dict:
        if not self.enabled:
            return {"enabled": False, "fired": None, "declined": 0,
                    "reasons": {}}
        return {"enabled": True, "fired": self.fired,
                "declined": self.declined,
                "reasons": dict(sorted(self.reasons.items())),
                "rewrites": list(self.samples)}


class PassConfig:
    """Which passes run.  The default is every pass on (the normal
    pipeline); ``A100C_PASS_<NAME>=off`` turns one off."""

    def __init__(self, enabled: Optional[Dict[str, bool]] = None):
        self.enabled: Dict[str, bool] = {name: True for name in PASS_ORDER}
        if enabled:
            for name, value in enabled.items():
                if name not in PASS_REGISTRY:
                    raise KeyError(f"unknown pass '{name}'")
                self.enabled[name] = bool(value)

    @staticmethod
    def from_env(env: Optional[Dict[str, str]] = None) -> "PassConfig":
        source = os.environ if env is None else env
        cfg = PassConfig()
        for name in PASS_ORDER:
            value = source.get(f"A100C_PASS_{name.upper()}")
            if value is not None and value.strip().lower() in _OFF:
                cfg.enabled[name] = False
        return cfg

    def with_pass(self, name: str, on: bool) -> "PassConfig":
        cfg = PassConfig(self.enabled)
        cfg.enabled[name] = bool(on)
        return cfg

    def all_off(self) -> "PassConfig":
        return PassConfig({name: False for name in PASS_ORDER})

    def identity_part(self) -> str:
        """The artifact-identity fragment: every disabled pass is listed
        so two configurations never share a key."""
        off = sorted(n for n in PASS_ORDER if not self.enabled[n])
        if not off:
            return "passes=default"
        return "passes=" + ",".join(f"{n}-off" for n in off)

    def describe(self) -> dict:
        return {"identity": self.identity_part(),
                "enabled": dict(self.enabled)}


class PassContext:
    """What a pass sees: the shared analysis views and its trace.  Reads
    go through the digest guard -- a pass that mutated the module and
    then reads again must ``refresh()`` first (or it is refused, which
    is the contract's other half)."""

    def __init__(self, suite: AnalysisSuite, trace: TraceCounters):
        self.suite = suite
        self.trace = trace
        self._frozen: FrozenAnalyses = suite.freeze()

    def refresh(self) -> None:
        """Re-bind after a mutation: the next reads see recomputed
        analyses (never a stale result)."""
        self._frozen = self.suite.freeze()

    def get(self, name: str):
        return self._frozen.get(name)


class PipelineReport:
    """The per-pass outcomes of one run."""

    def __init__(self, config: PassConfig):
        self.config = config
        self.passes: Dict[str, dict] = {}
        self.rounds = 0

    def describe(self) -> dict:
        return {"identity": self.config.identity_part(),
                "rounds": self.rounds,
                "passes": {name: self.passes[name] for name in PASS_ORDER}}


class PassPipeline:
    """A configured pipeline: the object the compiler's driver holds
    (``PassPipeline(config).run(module)``); ``identity_part`` is the
    fragment the driver's artifact key must carry."""

    def __init__(self, config: Optional[PassConfig] = None):
        self.config = config or PassConfig.from_env()

    @property
    def identity_part(self) -> str:
        return self.config.identity_part()

    def run(self, module: tir.Module,
            suite: Optional[AnalysisSuite] = None) -> PipelineReport:
        return run(module, self.config, suite)


def run(module: tir.Module, config: Optional[PassConfig] = None,
        suite: Optional[AnalysisSuite] = None) -> PipelineReport:
    """Run the enabled passes over one TIR module, in the declared
    order, iterating to a fixpoint (bounded).  The module is verified
    before the first pass (the caller owns the frontend's verification)
    and after every mutating pass (a rewrite that breaks the TIR
    contract is a pass defect, raised immediately)."""
    cfg = config or PassConfig.from_env()
    suite = suite or AnalysisSuite(module)
    report = PipelineReport(cfg)
    instances = {name: PASS_REGISTRY[name]() for name in PASS_ORDER}
    traces = {name: TraceCounters(name, cfg.enabled[name])
              for name in PASS_ORDER}
    ctxs = {name: PassContext(suite, traces[name]) for name in PASS_ORDER}
    errors = tir.verify_module(module)
    if errors:
        raise ValueError(f"the pipeline's input module is not valid TIR: "
                         f"{errors[0]}")

    for _round in range(MAX_ROUNDS):
        report.rounds = _round + 1
        any_change = False
        for name in PASS_ORDER:
            if not cfg.enabled[name]:
                report.passes[name] = traces[name].describe()
                continue
            instance = instances[name]
            ctx = ctxs[name]
            # bind this pass's view to the module as it stands now (the
            # previous passes' mutations are already recomputed lazily
            # through the suite when the pass first reads)
            ctx.refresh()
            try:
                changed = instance.run(module, ctx)
            except StaleAnalysisError as exc:
                # the refusal path: the pass never reads a stale result
                ctx.trace.record_decline(
                    f"stale analysis refused: {exc}")
                changed = False
            if changed:
                errors = tir.verify_module(module)
                if errors:
                    raise ValueError(
                        f"pass '{name}' broke the TIR contract: "
                        f"{errors[0]}")
                # the declared invalidation: the shared owner drops what
                # the pass invalidated; the digest check stays as the
                # enforcement
                suite.invalidate(*getattr(instance, "ANALYSES_INVALIDATED",
                                          ()))
                any_change = True
            report.passes[name] = traces[name].describe()
        if not any_change:
            break
    for name in PASS_ORDER:
        report.passes[name] = traces[name].describe()
    return report
