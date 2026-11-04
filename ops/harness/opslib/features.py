"""Semantic feature extraction for Triton operators (AST, no execution).

Selection of a development suite has to be driven by what the *source* makes
the compiler do, not by operator names.  This module parses every
``@triton.jit`` function in an operator file and emits a set of feature tags
plus derived feature *interactions* (pairs), which is what
``harness/tools/select_suite.py`` optimises over.

Tags are deliberately coarse: a tag means "the compiler must implement this
reusable capability", not "this exact call appears".  ``math.exp`` and
``math.sigmoid`` both lower to a transcendental path, so they share
``math.transcendental``; ``red.sum`` and ``red.max`` share the reduction
machinery but are kept apart because the combine function differs.

Anything the project declares unsupported (``AGENTS.md``: ``dot_scaled``/fp4,
int4, ``inline_asm_elementwise``, TMA descriptors, ``tl.extra``/``tl.math``/
libdevice) is reported in ``unsupported`` instead of becoming a feature, so
a candidate using it is rejected rather than quietly counted as coverage.
"""
from __future__ import annotations

import ast
import hashlib
import re
from pathlib import Path

#: Tags whose co-occurrence is a *feature interaction* worth covering.
PRIMITIVE = "primitive"
DERIVED = "derived"

#: ``tl.<name>`` / method calls -> tags.
TL_CALL_TAGS = {
    # memory
    "load": ("mem.load",),
    "store": ("mem.store",),
    "atomic_add": ("mem.atomic",),
    "atomic_max": ("mem.atomic",),
    "atomic_min": ("mem.atomic",),
    "atomic_xchg": ("mem.atomic",),
    "atomic_cas": ("mem.atomic",),
    "atomic_xor": ("mem.atomic",),
    "make_block_ptr": ("mem.blockptr",),
    "advance": ("mem.blockptr",),
    "multiple_of": ("mem.alignment_hint",),
    "max_contiguous": ("mem.alignment_hint",),
    # shape / layout
    "reshape": ("shape.reshape",),
    "view": ("shape.reshape",),
    "ravel": ("shape.reshape",),
    "trans": ("shape.trans",),
    "permute": ("shape.trans",),
    "expand_dims": ("shape.expand",),
    "broadcast_to": ("shape.broadcast",),
    "squeeze": ("shape.expand",),
    "split": ("shape.split_join",),
    "join": ("shape.split_join",),
    "interleave": ("shape.split_join",),
    "zeros": ("construct.zeros",),
    "full": ("construct.full",),
    "arange": ("construct.arange",),
    "where": ("select.where",),
    # reductions
    "sum": ("red.sum",),
    "max": ("red.maxmin",),
    "min": ("red.maxmin",),
    "argmax": ("red.argmaxmin",),
    "argmin": ("red.argmaxmin",),
    "reduce": ("red.custom",),
    "cumsum": ("red.scan",),
    "associative_scan": ("red.scan",),
    "sort": ("red.sort",),
    "histogram": ("red.histogram",),
    # math
    "exp": ("math.transcendental",),
    "exp2": ("math.transcendental",),
    "log": ("math.transcendental",),
    "log2": ("math.transcendental",),
    "sin": ("math.transcendental",),
    "cos": ("math.transcendental",),
    "sigmoid": ("math.transcendental",),
    "erf": ("math.transcendental",),
    "sqrt": ("math.sqrt_rsqrt",),
    "rsqrt": ("math.sqrt_rsqrt",),
    "abs": ("math.abs",),
    "fabs": ("math.abs",),
    "floor": ("math.round",),
    "ceil": ("math.round",),
    "minimum": ("math.clamp",),
    "maximum": ("math.clamp",),
    "clamp": ("math.clamp",),
    # dot
    "dot": ("dot.matmul",),
    # control / debug
    "static_range": ("flow.static_range",),
    "static_assert": ("hint.static_assert",),
    "device_assert": ("hint.static_assert",),
    "assume": ("hint.static_assert",),
    # rng / misc
    "rand": ("misc.rng",),
    "randn": ("misc.rng",),
    "randint4x": ("misc.rng",),
    "philox": ("misc.rng",),
    "debug_barrier": ("misc.barrier",),
    "max_contiguous_": ("mem.alignment_hint",),
}

#: ``tl.<name>`` constants/attributes -> tags.
TL_ATTR_TAGS = {
    "constexpr": ("lang.constexpr",),
}

#: Substrings that mean the construct is out of scope for this project.
UNSUPPORTED_PATTERNS = {
    "dot_scaled": "dot_scaled / fp4 is declared unsupported",
    "inline_asm_elementwise": "inline asm is declared unsupported",
    "make_tensor_descriptor": "TMA tensor descriptors are declared unsupported",
    "TensorDescriptor": "TMA tensor descriptors are declared unsupported",
    "tl.extra": "tl.extra is declared unsupported",
    "tl.math": "tl.math is declared unsupported",
    "libdevice": "libdevice is declared unsupported",
    "tl.tanh": "tl.tanh does not exist in Triton 3.8",
    "tl.pow": "tl.pow does not exist in Triton 3.8",
    "tl.bool": "tl.bool does not exist in Triton 3.8",
}

#: Binops / compare ops -> tags.
BINOP_TAGS = {
    ast.Add: "arith.add", ast.Sub: "arith.sub", ast.Mult: "arith.mul",
    ast.Div: "arith.div", ast.FloorDiv: "arith.div", ast.Mod: "arith.mod",
    ast.Pow: "arith.pow", ast.MatMult: "arith.mul",
    ast.BitAnd: "logic.bitwise", ast.BitOr: "logic.bitwise",
    ast.BitXor: "logic.bitwise", ast.LShift: "logic.bitwise",
    ast.RShift: "logic.bitwise",
}
CMP_TAGS = (ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.Eq, ast.NotEq, ast.Is, ast.IsNot)
BOOL_TAGS = {ast.And: "logic.bool", ast.Or: "logic.bool"}


def _dotted(node) -> str:
    """``tl.load`` from ``Attribute(value=Name('tl'), attr='load')``."""
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


def _kernel_functions(tree: ast.Module):
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        decorators = [ast.unparse(d) for d in node.decorator_list]
        if any("triton.jit" in d for d in decorators):
            out.append(node)
    return out


def _decorators(tree: ast.Module):
    names = []
    for node in ast.walk(tree):
        for dec in getattr(node, "decorator_list", []) or []:
            names.append(ast.unparse(dec))
    return names


def _axis_tag(call: ast.Call) -> set:
    """Distinguish single-axis, tuple-axis and keep_dims reductions."""
    tags = set()
    for kw in call.keywords:
        if kw.arg == "axis":
            if isinstance(kw.value, (ast.Tuple, ast.List)):
                tags.add("red.multi_axis")
            tags.add("red.axis")
        if kw.arg == "keep_dims":
            tags.add("red.keep_dims")
    if len(call.args) >= 2:
        arg = call.args[1]
        if isinstance(arg, (ast.Tuple, ast.List)):
            tags.add("red.multi_axis")
        tags.add("red.axis")
    return tags


def _load_store_tags(call: ast.Call, name: str) -> set:
    tags = set()
    kwargs = {kw.arg for kw in call.keywords}
    if "mask" in kwargs:
        tags.add("mem.masked_load" if name == "load" else "mem.masked_store")
    if "boundary_check" in kwargs:
        tags.add("mem.boundary_check")
    if "padding_option" in kwargs:
        tags.add("mem.padding")
    if "other" in kwargs:
        tags.add("mem.other")
    if "cache_modifier" in kwargs or "eviction_policy" in kwargs:
        tags.add("mem.cache_hint")
    if "volatile" in kwargs:
        tags.add("mem.volatile")
    return tags


def extract(source: str, *, path: str = "") -> dict:
    """Feature record for one operator source."""
    record = {"tags": set(), "unsupported": [], "kernels": [],
              "n_jit": 0, "n_arange": 0, "max_arange_rank": 0,
              "constexpr_params": 0, "has_autotune": False,
              "num_warps": None, "num_stages": None, "source_bytes": len(source)}
    text = source
    for needle, why in UNSUPPORTED_PATTERNS.items():
        if needle in text:
            record["unsupported"].append(f"{why} ({needle})")

    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        record["unsupported"].append(f"SyntaxError: {exc}")
        return record

    for dec in _decorators(tree):
        if "autotune" in dec:
            record["has_autotune"] = True
            record["tags"].add("tune.autotune")
        m = re.search(r"num_warps\s*=\s*(\d+)", dec)
        if m:
            record["num_warps"] = int(m.group(1))
        m = re.search(r"num_stages\s*=\s*(\d+)", dec)
        if m:
            record["num_stages"] = int(m.group(1))

    kernels = _kernel_functions(tree)
    record["kernels"] = [k.name for k in kernels]
    record["n_jit"] = len(kernels)

    for kernel in kernels:
        for arg in kernel.args.args + kernel.args.kwonlyargs:
            annotation = getattr(arg, "annotation", None)
            if annotation is not None and "constexpr" in ast.unparse(annotation):
                record["constexpr_params"] += 1
        for node in ast.walk(kernel):
            # triton calls
            if isinstance(node, ast.Call):
                dotted = _dotted(node.func)
                name = dotted.split(".")[-1]
                if dotted.startswith("tl.") or dotted.startswith("triton.language"):
                    for tag in TL_CALL_TAGS.get(name, ()):
                        record["tags"].add(tag)
                    if name in ("load", "store"):
                        record["tags"].update(_load_store_tags(node, name))
                    if name in ("sum", "max", "min", "argmax", "argmin"):
                        record["tags"].update(_axis_tag(node))
                    if name == "arange":
                        record["n_arange"] += 1
                    if name == "dot":
                        kwargs = {kw.arg for kw in node.keywords}
                        if "acc" in kwargs:
                            record["tags"].add("dot.acc")
                        if kwargs & {"input_precision", "allow_tf32"}:
                            record["tags"].add("dot.precision_kw")
                        if "out_dtype" in kwargs:
                            record["tags"].add("dot.out_dtype")
                    if name == "range":
                        record["tags"].add("flow.tl_range")
                        kwargs = {kw.arg for kw in node.keywords}
                        if kwargs & {"num_stages", "loop_unroll_factor"}:
                            record["tags"].add("tune.loop_pragma")
                elif name in ("range", "enumerate"):
                    record["tags"].add("flow.dynamic_range")
                elif name == "static_range":
                    record["tags"].add("flow.static_range")
                # method calls: x.to(tl.float32), x.trans(), ...
                if isinstance(node.func, ast.Attribute):
                    method = node.func.attr
                    if method in ("to", "cast"):
                        record["tags"].add("cast.explicit")
                        target = _dotted(node.args[0]) if node.args else ""
                        if "float32" in target:
                            record["tags"].add("cast.to_fp32")
                        if "float16" in target or "bfloat16" in target:
                            record["tags"].add("cast.to_fp16")
                        if "int" in target:
                            record["tags"].add("dtype.int")
                        if "uint" in target:
                            record["tags"].add("dtype.uint")
                    for tag in TL_CALL_TAGS.get(method, ()):
                        record["tags"].add(tag)
            # arange rank: count tl.arange calls in one expression chain
            if isinstance(node, ast.BinOp):
                tag = BINOP_TAGS.get(type(node.op))
                if tag:
                    record["tags"].add(tag)
            elif isinstance(node, ast.UnaryOp):
                if isinstance(node.op, ast.USub):
                    record["tags"].add("arith.neg")
                elif isinstance(node.op, ast.Invert):
                    record["tags"].add("logic.bitwise")
                elif isinstance(node.op, ast.Not):
                    record["tags"].add("logic.bool")
            elif isinstance(node, CMP_TAGS):
                record["tags"].add("cmp.compare")
            elif isinstance(node, ast.BoolOp):
                record["tags"].add(BOOL_TAGS.get(type(node.op), "logic.bool"))
            elif isinstance(node, ast.IfExp):
                record["tags"].add("select.where")
            elif isinstance(node, ast.If):
                test = ast.unparse(node.test)
                if "program_id" in test or "pid" in test:
                    record["tags"].add("flow.if_pid")
                else:
                    record["tags"].add("flow.if")
            elif isinstance(node, ast.While):
                record["tags"].add("flow.while")
            elif isinstance(node, ast.For):
                if "program_id" not in ast.unparse(node.iter):
                    record["tags"].add("flow.loop")

    # rank of the tile: distinct tl.arange calls used in one expression.
    ranks = set()
    for kernel in kernels:
        for node in ast.walk(kernel):
            if isinstance(node, ast.Assign) and isinstance(node.value, ast.BinOp):
                count = sum(1 for sub in ast.walk(node.value)
                            if isinstance(sub, ast.Call)
                            and _dotted(sub.func).endswith("arange"))
                if count:
                    ranks.add(count)
    record["max_arange_rank"] = max(ranks) if ranks else 0
    if record["max_arange_rank"] >= 3:
        record["tags"].add("index.rank3plus")
    if record["max_arange_rank"] == 2:
        record["tags"].add("index.rank2")
    if record["n_arange"] > 1:
        record["tags"].add("index.multi_offset")

    _ops_signature(record, kernels)
    _derive(record)
    return record


def _ops_signature(record: dict, kernels) -> None:
    """Exact arithmetic/lowering signature, so ``exp`` != ``sigmoid``.

    Tag-level dedupe alone would call two different transcendental kernels
    redundant; this keeps the distinction that matters for lowering while
    still collapsing literal near-duplicates (same code under a new name).
    """
    parts = []
    for kernel in kernels:
        for node in ast.walk(kernel):
            if isinstance(node, ast.BinOp):
                parts.append(type(node.op).__name__)
            elif isinstance(node, ast.UnaryOp):
                parts.append("U" + type(node.op).__name__)
            elif isinstance(node, ast.Call):
                parts.append(_dotted(node.func).split(".")[-1])
            elif isinstance(node, ast.Compare):
                parts.append("Cmp" + "".join(type(o).__name__ for o in node.ops))
    record["ops_signature"] = sorted(parts)


def _derive(record: dict) -> None:
    """Composite capabilities inferred from primitive co-occurrence."""
    tags = record["tags"]
    if {"red.maxmin", "math.transcendental", "red.sum", "arith.div"} <= tags:
        tags.add("pat.softmax")
    if {"red.sum", "math.sqrt_rsqrt", "arith.div"} <= tags and "arith.sub" in tags:
        tags.add("pat.normalize")
    if "dot.matmul" in tags and tags & {"math.clamp", "math.transcendental",
                                        "select.where", "cast.explicit"}:
        tags.add("pat.matmul_epilogue")
    if "dot.matmul" in tags and "red.sum" in tags:
        tags.add("pat.dot_reduce")
    if "red.sum" in tags and "arith.sub" in tags and "arith.mul" in tags:
        tags.add("pat.reduce_broadcast")
    if "mem.masked_load" in tags and "mem.masked_store" in tags:
        tags.add("pat.masked_both")
    if "mem.blockptr" in tags and "mem.boundary_check" in tags:
        tags.add("pat.blockptr_boundary")
    if "flow.loop" in tags and "dot.matmul" in tags:
        tags.add("pat.k_loop")
    if "flow.loop" in tags and tags & {"red.sum", "red.maxmin"}:
        tags.add("pat.persistent_reduce")


def interactions(tags) -> set:
    """Unordered pairs of primitive tags -- the interaction coverage unit."""
    prim = sorted(t for t in tags if not t.startswith("pat."))
    return {f"{a}+{b}" for i, a in enumerate(prim) for b in prim[i + 1:]}


def structural_hash(record: dict) -> str:
    """Fingerprint used to detect near-duplicate operators.

    Two operators with the same tag set, the same tile rank and the same
    number of constexpr parameters are almost certainly variants of one
    another; the suite only needs the best-covered one.
    """
    key = ("|".join(sorted(record["tags"]))
           + f"|rank{record['max_arange_rank']}"
           + "|" + ",".join(record.get("ops_signature") or []))
    return hashlib.sha1(key.encode()).hexdigest()[:12]


def extract_file(path: str | Path) -> dict:
    path = Path(path)
    record = extract(path.read_text(), path=str(path))
    record["path"] = str(path)
    record["name"] = path.stem
    record["hash"] = structural_hash(record)
    return record
