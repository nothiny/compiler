"""The declared source-language surface as data (FE-UNSUPPORTED-SURFACE).

``SURFACE`` embeds the 107-construct / 280-parameter surface recorded in
``PROJECT_STATE.json`` ``workload.api_spec`` (built from
``ops/docs/API_INVENTORY.md`` -- the shipped 500-operator suite's own AST
inventory -- with parameter surfaces read from the pinned Triton 3.8.0
signatures).  The enumeration test asserts this table equals the recorded
api_spec, so the two cannot drift.

Every construct parameter is classified exactly one of:

``implemented``
    the frontend consumes it (semantic, load-bearing);
``ignorable``
    performance-only, ignored with a recorded reason (a memory-system hint,
    a codegen hint, tuning-time machinery) -- never a semantic parameter;
``refused``
    the frontend rejects a call that uses it (or the whole construct) with
    a located diagnostic naming the construct and reason.

Constructs not in the table are outside the declared surface
(``tl.tanh``/``tl.pow`` do not exist in Triton 3.8, fp8/tf32/libdevice/
tensor descriptors are excluded by the subset -- SUBSET.md 6) and are
refused outright.

The classification is *load-bearing*: ``lower_tir`` consults it for every
call parameter (implemented -> bound, ignorable -> dropped, refused ->
diagnostic), so marking a semantic parameter ignorable visibly changes the
lowered TIR -- that is the enumeration test's control (MECH-WITNESS-TEST).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

__all__ = [
    "SurfaceConstruct", "SurfaceParam", "Surface", "SURFACE",
    "DEFAULT_SURFACE", "CLASS_IMPLEMENTED", "CLASS_IGNORABLE",
    "CLASS_REFUSED", "EXCLUDED_CONSTRUCTS", "IMPLEMENTED_CONSTRUCTS",
    "IGNORABLE_PARAMS", "REFUSED_PARAMS",
]


CLASS_IMPLEMENTED = "implemented"
CLASS_IGNORABLE = "ignorable"
CLASS_REFUSED = "refused"


@dataclass(frozen=True)
class SurfaceParam:
    name: str
    classification: str
    reason: str = ""


@dataclass(frozen=True)
class SurfaceConstruct:
    name: str
    parameters: Tuple[str, ...]
    tier: str
    corpus_calls: int
    out_of_scope: Optional[str] = None
    param_classifications: Tuple[SurfaceParam, ...] = ()


# ---------------------------------------------------------------------------
# The recorded surface (generated from PROJECT_STATE.json workload.api_spec;
# the enumeration test asserts equality with that record)
# ---------------------------------------------------------------------------

_RAW_SURFACE: List[SurfaceConstruct] = [
    SurfaceConstruct(
        name='triton.jit',
        parameters=['fn', 'version', 'repr', 'launch_metadata', 'do_not_specialize', 'do_not_specialize_on_alignment', 'debug', 'noinline'],
        tier='P0',
        corpus_calls=500),
    SurfaceConstruct(
        name='tl.store',
        parameters=['pointer', 'value', 'mask', 'boundary_check', 'cache_modifier', 'eviction_policy'],
        tier='P0',
        corpus_calls=487),
    SurfaceConstruct(
        name='tl.load',
        parameters=['pointer', 'mask', 'other', 'boundary_check', 'padding_option', 'cache_modifier', 'eviction_policy', 'volatile'],
        tier='P0',
        corpus_calls=481),
    SurfaceConstruct(
        name='tl.arange',
        parameters=['start', 'end'],
        tier='P0',
        corpus_calls=466),
    SurfaceConstruct(
        name='tl.program_id',
        parameters=['axis'],
        tier='P0',
        corpus_calls=457),
    SurfaceConstruct(
        name='tl.constexpr',
        parameters=['value'],
        tier='P0',
        corpus_calls=450),
    SurfaceConstruct(
        name='tl.float32',
        parameters=[],
        tier='P0',
        corpus_calls=275),
    SurfaceConstruct(
        name='tl.sum',
        parameters=['input', 'axis', 'keep_dims', 'dtype'],
        tier='P0',
        corpus_calls=195),
    SurfaceConstruct(
        name='tl.where',
        parameters=['condition', 'x', 'y'],
        tier='P0',
        corpus_calls=182),
    SurfaceConstruct(
        name='tl.zeros',
        parameters=['shape', 'dtype'],
        tier='P0',
        corpus_calls=147),
    SurfaceConstruct(
        name='tl.int64',
        parameters=[],
        tier='P0',
        corpus_calls=139),
    SurfaceConstruct(
        name='tl.maximum',
        parameters=['x', 'y', 'propagate_nan'],
        tier='P1',
        corpus_calls=78),
    SurfaceConstruct(
        name='tl.dot',
        parameters=['input', 'other', 'acc', 'out_dtype'],
        tier='P1',
        corpus_calls=74,
        out_of_scope="input_precision= and allow_tf32= are stripped from every kept operator by SUBSET.md principle 2 (fp32 tl.dot is exact IEEE; the harness pins TRITON_F32_DEFAULT=ieee); max_num_imprecise_acc applies to fp8 which the subset excludes entirely. Declared subset parameters: input, other, acc, out_dtype (bf16/fp16 operands with fp32 accumulation; fp32 operands IEEE)."),
    SurfaceConstruct(
        name='tl.exp',
        parameters=['x'],
        tier='P1',
        corpus_calls=73),
    SurfaceConstruct(
        name='tl.max',
        parameters=['input', 'axis', 'return_indices', 'return_indices_tie_break_left', 'keep_dims'],
        tier='P1',
        corpus_calls=70),
    SurfaceConstruct(
        name='tl.abs',
        parameters=['x'],
        tier='P1',
        corpus_calls=66),
    SurfaceConstruct(
        name='tl.cdiv',
        parameters=['x', 'div'],
        tier='P1',
        corpus_calls=59),
    SurfaceConstruct(
        name='tl.full',
        parameters=['shape', 'value', 'dtype'],
        tier='P1',
        corpus_calls=56),
    SurfaceConstruct(
        name='tl.int32',
        parameters=[],
        tier='P1',
        corpus_calls=54),
    SurfaceConstruct(
        name='tl.sqrt',
        parameters=['x'],
        tier='P1',
        corpus_calls=51),
    SurfaceConstruct(
        name='tl.log',
        parameters=['x'],
        tier='P1',
        corpus_calls=44),
    SurfaceConstruct(
        name='tl.minimum',
        parameters=['x', 'y', 'propagate_nan'],
        tier='P1',
        corpus_calls=44),
    SurfaceConstruct(
        name='tl.min',
        parameters=['input', 'axis', 'return_indices', 'return_indices_tie_break_left', 'keep_dims'],
        tier='P1',
        corpus_calls=30),
    SurfaceConstruct(
        name='tl.bfloat16',
        parameters=[],
        tier='P1',
        corpus_calls=25),
    SurfaceConstruct(
        name='tl.range',
        parameters=['arg1', 'arg2', 'step', 'num_stages', 'loop_unroll_factor', 'disallow_acc_multi_buffer', 'flatten', 'warp_specialize', 'disable_licm'],
        tier='P1',
        corpus_calls=25),
    SurfaceConstruct(
        name='tl.float16',
        parameters=[],
        tier='P1',
        corpus_calls=24),
    SurfaceConstruct(
        name='tl.num_programs',
        parameters=['axis'],
        tier='P1',
        corpus_calls=22),
    SurfaceConstruct(
        name='tl.reshape',
        parameters=['input', '*shape', 'can_reorder'],
        tier='P1',
        corpus_calls=22),
    SurfaceConstruct(
        name='tl.static_range',
        parameters=['arg1', 'arg2', 'step'],
        tier='P1',
        corpus_calls=21),
    SurfaceConstruct(
        name='tl.multiple_of',
        parameters=['input', 'values'],
        tier='P1',
        corpus_calls=20),
    SurfaceConstruct(
        name='tl.sigmoid',
        parameters=['x'],
        tier='P1',
        corpus_calls=17),
    SurfaceConstruct(
        name='tl.float64',
        parameters=[],
        tier='P1',
        corpus_calls=16,
        out_of_scope="no float64 tensor case exists: SUBSET.md principle 2 removes fp64 cases; the 16 suite occurrences are constexpr dtype-dispatch comparisons/branches that are dead for the declared case dtypes (verified: no operator declares a float64 case in suite/manifest.json) - the constant must parse and compare during specialization, but no fp64 tensor compute path is exercised by any case"),
    SurfaceConstruct(
        name='tl.rsqrt',
        parameters=['x'],
        tier='P1',
        corpus_calls=16),
    SurfaceConstruct(
        name='tl.trans',
        parameters=['input', '*dims'],
        tier='P1',
        corpus_calls=14),
    SurfaceConstruct(
        name='tl.exp2',
        parameters=['x'],
        tier='P1',
        corpus_calls=12),
    SurfaceConstruct(
        name='tl.uint32',
        parameters=[],
        tier='P1',
        corpus_calls=12),
    SurfaceConstruct(
        name='tl.atomic_add',
        parameters=['pointer', 'val', 'mask', 'sem', 'scope'],
        tier='P1',
        corpus_calls=11),
    SurfaceConstruct(
        name='triton.autotune',
        parameters=['configs', 'key', 'prune_configs_by', 'reset_to_zero', 'restore_value', 'pre_hook', 'post_hook', 'warmup', 'rep', 'use_cuda_graph', 'do_bench', 'cache_results'],
        tier='P1',
        corpus_calls=11),
    SurfaceConstruct(
        name='tl.erf',
        parameters=['x'],
        tier='P1',
        corpus_calls=10),
    SurfaceConstruct(
        name='tl.int1',
        parameters=[],
        tier='P2',
        corpus_calls=9),
    SurfaceConstruct(
        name='tl.make_block_ptr',
        parameters=['base', 'shape', 'strides', 'offsets', 'block_shape', 'order'],
        tier='P2',
        corpus_calls=9),
    SurfaceConstruct(
        name='tl.cast',
        parameters=['input', 'dtype', 'fp_downcast_rounding', 'bitcast'],
        tier='P2',
        corpus_calls=8),
    SurfaceConstruct(
        name='tl.tensor',
        parameters=[],
        tier='P2',
        corpus_calls=8),
    SurfaceConstruct(
        name='tl.argmax',
        parameters=['input', 'axis', 'tie_break_left', 'keep_dims'],
        tier='P2',
        corpus_calls=7),
    SurfaceConstruct(
        name='tl.debug_barrier',
        parameters=[],
        tier='P2',
        corpus_calls=7),
    SurfaceConstruct(
        name='tl.floor',
        parameters=['x'],
        tier='P2',
        corpus_calls=7),
    SurfaceConstruct(
        name='tl.philox',
        parameters=['seed', 'c0', 'c1', 'c2', 'c3', 'n_rounds'],
        tier='P2',
        corpus_calls=7),
    SurfaceConstruct(
        name='tl.advance',
        parameters=['base', 'offsets'],
        tier='P2',
        corpus_calls=5),
    SurfaceConstruct(
        name='tl.cos',
        parameters=['x'],
        tier='P2',
        corpus_calls=5),
    SurfaceConstruct(
        name='tl.join',
        parameters=['a', 'b'],
        tier='P2',
        corpus_calls=5),
    SurfaceConstruct(
        name='tl.log2',
        parameters=['x'],
        tier='P2',
        corpus_calls=5),
    SurfaceConstruct(
        name='tl.sin',
        parameters=['x'],
        tier='P2',
        corpus_calls=5),
    SurfaceConstruct(
        name='tl.split',
        parameters=['a'],
        tier='P2',
        corpus_calls=5),
    SurfaceConstruct(
        name='tl.uint64',
        parameters=[],
        tier='P2',
        corpus_calls=5),
    SurfaceConstruct(
        name='tl.argmin',
        parameters=['input', 'axis', 'tie_break_left', 'keep_dims'],
        tier='P2',
        corpus_calls=4),
    SurfaceConstruct(
        name='tl.cumsum',
        parameters=['input', 'axis', 'reverse', 'dtype'],
        tier='P2',
        corpus_calls=4),
    SurfaceConstruct(
        name='tl.div_rn',
        parameters=['x', 'y'],
        tier='P2',
        corpus_calls=4),
    SurfaceConstruct(
        name='tl.int16',
        parameters=[],
        tier='P2',
        corpus_calls=4),
    SurfaceConstruct(
        name='tl.int8',
        parameters=[],
        tier='P2',
        corpus_calls=4),
    SurfaceConstruct(
        name='tl.permute',
        parameters=['input', '*dims'],
        tier='P2',
        corpus_calls=4),
    SurfaceConstruct(
        name='tl.rand',
        parameters=['seed', 'offset', 'n_rounds'],
        tier='P2',
        corpus_calls=4),
    SurfaceConstruct(
        name='tl.atomic_max',
        parameters=['pointer', 'val', 'mask', 'sem', 'scope'],
        tier='P2',
        corpus_calls=3),
    SurfaceConstruct(
        name='tl.atomic_min',
        parameters=['pointer', 'val', 'mask', 'sem', 'scope'],
        tier='P2',
        corpus_calls=3),
    SurfaceConstruct(
        name='tl.broadcast_to',
        parameters=['input', '*shape'],
        tier='P2',
        corpus_calls=3),
    SurfaceConstruct(
        name='tl.static_assert',
        parameters=['cond', 'msg'],
        tier='P2',
        corpus_calls=3),
    SurfaceConstruct(
        name='tl.zeros_like',
        parameters=['input'],
        tier='P2',
        corpus_calls=3),
    SurfaceConstruct(
        name='tl.atomic_xchg',
        parameters=['pointer', 'val', 'mask', 'sem', 'scope'],
        tier='P2',
        corpus_calls=2),
    SurfaceConstruct(
        name='tl.cat',
        parameters=['input', 'other', 'can_reorder', 'dim'],
        tier='P2',
        corpus_calls=2),
    SurfaceConstruct(
        name='tl.clamp',
        parameters=['x', 'min', 'max', 'propagate_nan'],
        tier='P2',
        corpus_calls=2),
    SurfaceConstruct(
        name='tl.cumprod',
        parameters=['input', 'axis', 'reverse'],
        tier='P2',
        corpus_calls=2),
    SurfaceConstruct(
        name='tl.dtype',
        parameters=['name'],
        tier='P2',
        corpus_calls=2),
    SurfaceConstruct(
        name='tl.fma',
        parameters=['x', 'y', 'z'],
        tier='P2',
        corpus_calls=2),
    SurfaceConstruct(
        name='tl.randn',
        parameters=['seed', 'offset', 'n_rounds'],
        tier='P2',
        corpus_calls=2),
    SurfaceConstruct(
        name='tl.ravel',
        parameters=['x', 'can_reorder'],
        tier='P2',
        corpus_calls=2),
    SurfaceConstruct(
        name='tl.squeeze',
        parameters=['x', 'dim'],
        tier='P2',
        corpus_calls=2),
    SurfaceConstruct(
        name='tl.add',
        parameters=['x', 'y', 'sanitize_overflow'],
        tier='P2',
        corpus_calls=1),
    SurfaceConstruct(
        name='tl.atomic_and',
        parameters=['pointer', 'val', 'mask', 'sem', 'scope'],
        tier='P2',
        corpus_calls=1),
    SurfaceConstruct(
        name='tl.atomic_cas',
        parameters=['pointer', 'cmp', 'val', 'sem', 'scope'],
        tier='P2',
        corpus_calls=1),
    SurfaceConstruct(
        name='tl.atomic_or',
        parameters=['pointer', 'val', 'mask', 'sem', 'scope'],
        tier='P2',
        corpus_calls=1),
    SurfaceConstruct(
        name='tl.atomic_xor',
        parameters=['pointer', 'val', 'mask', 'sem', 'scope'],
        tier='P2',
        corpus_calls=1),
    SurfaceConstruct(
        name='tl.broadcast',
        parameters=['input', 'other'],
        tier='P2',
        corpus_calls=1),
    SurfaceConstruct(
        name='tl.ceil',
        parameters=['x'],
        tier='P2',
        corpus_calls=1),
    SurfaceConstruct(
        name='tl.expand_dims',
        parameters=['input', 'axis'],
        tier='P2',
        corpus_calls=1),
    SurfaceConstruct(
        name='tl.flip',
        parameters=['x', 'dim'],
        tier='P2',
        corpus_calls=1),
    SurfaceConstruct(
        name='tl.gather',
        parameters=['src', 'index', 'axis'],
        tier='P2',
        corpus_calls=1),
    SurfaceConstruct(
        name='tl.histogram',
        parameters=['input', 'num_bins', 'mask'],
        tier='P2',
        corpus_calls=1),
    SurfaceConstruct(
        name='tl.interleave',
        parameters=['a', 'b'],
        tier='P2',
        corpus_calls=1),
    SurfaceConstruct(
        name='tl.max_contiguous',
        parameters=['input', 'values'],
        tier='P2',
        corpus_calls=1),
    SurfaceConstruct(
        name='tl.mul',
        parameters=['x', 'y', 'sanitize_overflow'],
        tier='P2',
        corpus_calls=1),
    SurfaceConstruct(
        name='tl.pointer_type',
        parameters=['element_ty', 'address_space', 'const'],
        tier='P2',
        corpus_calls=1),
    SurfaceConstruct(
        name='tl.rand4x',
        parameters=['seed', 'offsets', 'n_rounds'],
        tier='P2',
        corpus_calls=1),
    SurfaceConstruct(
        name='tl.randint',
        parameters=['seed', 'offset', 'n_rounds'],
        tier='P2',
        corpus_calls=1),
    SurfaceConstruct(
        name='tl.randint4x',
        parameters=['seed', 'offset', 'n_rounds'],
        tier='P2',
        corpus_calls=1),
    SurfaceConstruct(
        name='tl.randn4x',
        parameters=['seed', 'offset', 'n_rounds'],
        tier='P2',
        corpus_calls=1),
    SurfaceConstruct(
        name='tl.reduce_or',
        parameters=['input', 'axis', 'keep_dims'],
        tier='P2',
        corpus_calls=1),
    SurfaceConstruct(
        name='tl.softmax',
        parameters=['x', 'dim', 'keep_dims', 'ieee_rounding'],
        tier='P2',
        corpus_calls=1),
    SurfaceConstruct(
        name='tl.sort',
        parameters=['x', 'dim', 'descending'],
        tier='P2',
        corpus_calls=1),
    SurfaceConstruct(
        name='tl.sqrt_rn',
        parameters=['x'],
        tier='P2',
        corpus_calls=1),
    SurfaceConstruct(
        name='tl.sub',
        parameters=['x', 'y', 'sanitize_overflow'],
        tier='P2',
        corpus_calls=1),
    SurfaceConstruct(
        name='tl.to_tensor',
        parameters=['x'],
        tier='P2',
        corpus_calls=1),
    SurfaceConstruct(
        name='tl.topk',
        parameters=['x', 'k', 'dim', 'descending'],
        tier='P2',
        corpus_calls=1),
    SurfaceConstruct(
        name='tl.uint16',
        parameters=[],
        tier='P2',
        corpus_calls=1),
    SurfaceConstruct(
        name='tl.uint8',
        parameters=[],
        tier='P2',
        corpus_calls=1),
    SurfaceConstruct(
        name='tl.unsqueeze',
        parameters=['x', 'dim'],
        tier='P2',
        corpus_calls=1),
    SurfaceConstruct(
        name='tl.view',
        parameters=['input', '*shape'],
        tier='P2',
        corpus_calls=1),
    SurfaceConstruct(
        name='tl.xor_sum',
        parameters=['input', 'axis', 'keep_dims'],
        tier='P2',
        corpus_calls=1),
    SurfaceConstruct(
        name='tl.swizzle2d',
        parameters=['i', 'j', 'size_i', 'size_j', 'size_g'],
        tier='P2',
        corpus_calls=0),
]


# ---------------------------------------------------------------------------
# Classification (the elementwise core of task T006)
# ---------------------------------------------------------------------------

#: constructs the frontend lowers today (a100c/frontend/lower_tir.py and the
#: source/specialization layers).  Everything else in the recorded surface is
#: refused with a located diagnostic when encountered; later tasks in the DAG
#: (T008-T016) widen this set.
IMPLEMENTED_CONSTRUCTS = {
    "triton.jit",                       # the compile unit decorator
    "triton.autotune",                  # deterministic first-config choice
    "tl.load", "tl.store",
    "tl.arange", "tl.program_id",
    "tl.constexpr",                     # annotation + tl.constexpr(...) folding
    "tl.where",
    "tl.zeros", "tl.full", "tl.zeros_like",
    "tl.multiple_of", "tl.max_contiguous",   # accepted no-op hints
    # dtype constants (no parameters): parse, compare, create
    "tl.float32", "tl.int64", "tl.int32", "tl.bfloat16", "tl.float16",
    "tl.float64", "tl.uint32", "tl.int1", "tl.uint64", "tl.int16", "tl.int8",
    "tl.uint16", "tl.uint8", "tl.tensor",
}

#: performance-only parameters with their recorded reasons (the only legal
#: ``ignorable`` classifications; each reason says why ignoring is safe)
IGNORABLE_PARAMS: Dict[Tuple[str, str], str] = {
    # triton.jit decorator metadata / codegen hints
    ("triton.jit", "version"): "decorator metadata; no kernel semantics",
    ("triton.jit", "repr"): "decorator metadata; no kernel semantics",
    ("triton.jit", "launch_metadata"): "launch telemetry hook; no kernel semantics",
    ("triton.jit", "debug"): "debug-info generation hint; no kernel semantics",
    ("triton.jit", "noinline"): "codegen hint (inlining); no kernel semantics",
    # memory-system hints on load/store
    ("tl.load", "cache_modifier"):
        "cache hint; no effect on loaded values under the declared target model",
    ("tl.load", "eviction_policy"):
        "cache hint; no effect on loaded values under the declared target model",
    ("tl.store", "cache_modifier"):
        "cache hint; no effect on stored values under the declared target model",
    ("tl.store", "eviction_policy"):
        "cache hint; no effect on stored values under the declared target model",
    # alignment/contiguity promises (optimization facts, not requirements)
    ("tl.multiple_of", "values"):
        "divisibility promise; recorded as a fact, ignoring it is always safe",
    ("tl.max_contiguous", "values"):
        "contiguity promise; recorded as a fact, ignoring it is always safe",
    # autotune machinery: the deterministic first-config choice never tunes
    ("triton.autotune", "key"):
        "tuning granularity; the deterministic first-config choice never re-tunes",
    ("triton.autotune", "prune_configs_by"):
        "tuning-space pruning; no tuning trials under deterministic choice",
    ("triton.autotune", "reset_to_zero"):
        "applies between tuning trials; there are no trials under the "
        "deterministic first-config choice",
    ("triton.autotune", "restore_value"):
        "applies between tuning trials; there are no trials under the "
        "deterministic first-config choice",
    ("triton.autotune", "pre_hook"):
        "runs during tuning only; the AST-reading frontend never executes hooks",
    ("triton.autotune", "post_hook"):
        "runs during tuning only; the AST-reading frontend never executes hooks",
    ("triton.autotune", "warmup"):
        "timing machinery; correctness never depends on it",
    ("triton.autotune", "rep"):
        "timing machinery; correctness never depends on it",
    ("triton.autotune", "use_cuda_graph"):
        "timing machinery; correctness never depends on it",
    ("triton.autotune", "do_bench"):
        "timing machinery; correctness never depends on it",
    ("triton.autotune", "cache_results"):
        "tuning-result cache; the deterministic choice needs none",
    # tl.range loop pragmas (performance hints on a construct the core refuses)
    ("tl.range", "num_stages"):
        "software-pipelining hint; not a loop semantic",
    ("tl.range", "loop_unroll_factor"):
        "unrolling hint; not a loop semantic",
    ("tl.range", "disallow_acc_multi_buffer"):
        "pipelining hint; not a loop semantic",
    ("tl.range", "flatten"):
        "loop-flattening hint; not a loop semantic",
    ("tl.range", "warp_specialize"):
        "scheduling hint; not a loop semantic",
    ("tl.range", "disable_licm"):
        "optimization hint; not a loop semantic",
}

#: semantic-but-unsupported parameters of *implemented* constructs: a call
#: that passes one is refused with a located diagnostic (never miscompiled)
REFUSED_PARAMS: Dict[Tuple[str, str], str] = {
    ("tl.load", "boundary_check"):
        "block-pointer boundary checking is semantic and not implemented by "
        "the elementwise core (make_block_ptr is refused)",
    ("tl.load", "padding_option"):
        "padding semantics are semantic and not implemented by the elementwise "
        "core (block-pointer machinery)",
    ("tl.load", "volatile"):
        "volatile ordering is semantic (it forbids elision); not implemented",
    ("tl.store", "boundary_check"):
        "block-pointer boundary checking is semantic and not implemented by "
        "the elementwise core (make_block_ptr is refused)",
}

#: constructs outside the declared surface entirely (SUBSET.md 6; the
#: exclusion table in OPERATOR_INVENTORY 3): refused with a located
#: diagnostic naming the construct
EXCLUDED_CONSTRUCTS = {
    "tl.tanh": "does not exist in Triton 3.8 (SUBSET.md 6)",
    "tl.pow": "does not exist in Triton 3.8 (SUBSET.md 6)",
    "tl.bool": "does not exist in Triton 3.8 (SUBSET.md 6)",
    "tl.fdiv": "no kept operator uses it (SUBSET.md 6, principle 3)",
    "tl.float8e4nv": "fp8 excluded by the declared subset (SUBSET.md 6)",
    "tl.float8e4b8": "fp8 excluded by the declared subset (SUBSET.md 6)",
    "tl.float8e5": "fp8 excluded by the declared subset (SUBSET.md 6)",
    "tl.float8e4b15": "fp8 excluded by the declared subset (SUBSET.md 6)",
    "tl.dot_scaled": "fp4/int4 vendor formats; declared unsupported (SUBSET.md 6)",
    "tl.inline_asm_elementwise":
        "bypasses the compiler; declared unsupported (SUBSET.md 6)",
    "tl.make_tensor_descriptor":
        "tensor descriptors / TMA; declared unsupported (SUBSET.md 6)",
    "tl.extra": "libdevice; excluded by the declared subset (SUBSET.md 6)",
    "tl.math": "libdevice; excluded by the declared subset (SUBSET.md 6)",
}


def _classify(c: SurfaceConstruct) -> Tuple[SurfaceParam, ...]:
    out: List[SurfaceParam] = []
    for p in c.parameters:
        if (c.name, p) in REFUSED_PARAMS:
            out.append(SurfaceParam(p, CLASS_REFUSED,
                                    REFUSED_PARAMS[(c.name, p)]))
        elif (c.name, p) in IGNORABLE_PARAMS:
            out.append(SurfaceParam(p, CLASS_IGNORABLE,
                                    IGNORABLE_PARAMS[(c.name, p)]))
        elif c.name in IMPLEMENTED_CONSTRUCTS:
            out.append(SurfaceParam(p, CLASS_IMPLEMENTED,
                                    "consumed by the elementwise core"))
        else:
            out.append(SurfaceParam(
                p, CLASS_REFUSED,
                "construct not implemented by the frontend elementwise core "
                "yet; refused with a located diagnostic when encountered"))
    return tuple(out)


def _build() -> List[SurfaceConstruct]:
    return [
        SurfaceConstruct(
            name=c.name, parameters=tuple(c.parameters), tier=c.tier,
            corpus_calls=c.corpus_calls, out_of_scope=c.out_of_scope,
            param_classifications=_classify(c))
        for c in _RAW_SURFACE
    ]


#: the recorded 107-construct / 280-parameter surface, classified
SURFACE: List[SurfaceConstruct] = _build()

assert len(SURFACE) == 107, (
    f"declared surface has 107 constructs, got {len(SURFACE)}")
assert sum(len(c.parameters) for c in SURFACE) == 280, (
    "declared surface has 280 parameters, got "
    f"{sum(len(c.parameters) for c in SURFACE)}")


class Surface:
    """The classification the lowering consults (injectable for tests)."""

    def __init__(self, constructs: List[SurfaceConstruct]):
        self.by_name: Dict[str, SurfaceConstruct] = {
            c.name: c for c in constructs}

    def construct(self, name: str) -> Optional[SurfaceConstruct]:
        return self.by_name.get(name)

    def is_implemented(self, name: str) -> bool:
        """Construct-level status: does the frontend lower this construct?"""
        return name in IMPLEMENTED_CONSTRUCTS and name in self.by_name

    def classify_param(self, construct: str, param: str) -> SurfaceParam:
        c = self.by_name.get(construct)
        if c is None:
            raise KeyError(f"construct {construct!r} is not in the surface")
        for p in c.param_classifications:
            if p.name == param:
                return p
        raise KeyError(f"parameter {construct}.{param} is not in the surface")

    def with_param_classification(self, construct: str, param: str,
                                  classification: str,
                                  reason: str = "test override") -> "Surface":
        """A copy with one parameter reclassified (the test control)."""
        out: List[SurfaceConstruct] = []
        for c in self.by_name.values():
            if c.name != construct:
                out.append(c)
                continue
            params = tuple(
                SurfaceParam(p.name,
                             classification if p.name == param
                             else p.classification,
                             reason if p.name == param else p.reason)
                for p in c.param_classifications)
            out.append(SurfaceConstruct(
                name=c.name, parameters=c.parameters, tier=c.tier,
                corpus_calls=c.corpus_calls, out_of_scope=c.out_of_scope,
                param_classifications=params))
        return Surface(out)


DEFAULT_SURFACE = Surface(SURFACE)
