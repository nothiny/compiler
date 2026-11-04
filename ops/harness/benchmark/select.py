"""Select the benchmark operators and write them into ``suite/perf/``.

**Not applicable in this image**: it needs the upstream candidate pool, which
is not shipped.  The selected 100 operators and ``suite/perf/workload.json``
are already in place; use ``run.py`` directly.

Original contract:

``suite/perf/`` is the performance input directory.  Its operators come from a **pool** -- the tritonbench set, kept out
of the input tree (see ``--pool``) -- and are chosen by hand in ``PICKS``,
grouped by **computation pattern** rather than by name: streaming and fused
elementwise, broadcast, gather, indexed writes, pooling, GEMV, row
reductions, softmax, norms, scans, losses, similarity, GEMM with and without
fused epilogues, batched / low-precision dot, attention, linear attention
and convolution.  A pattern gets a handful of entries so none dominates its
class geomean.

For every pick this script

1. refuses it when its kernel already exists in basic/medium/hard: the input
   corpus is the four directories together, and a duplicate adds a file but
   no kernel;
2. copies the file to ``bench/<id>.py`` with only its ``OPERATOR`` header
   rewritten (group ``bench``) and a ``BENCH_SOURCE`` record added -- the
   kernel and case layer are byte-identical to the pool file;
3. derives a steady-state scale rule (``classify``) and runs a cheap
   ``make_case`` at a validation shape; a pick that only accepts its declared
   shapes cannot be benchmarked and is refused.

    python3 harness/benchmark/select.py --pool ~/ops-plan-pool/tritonbench

writes ``bench/*.py`` and ``bench/workload.json``.  The pool is kept outside
the corpus (it is not compiler input); the committed selection used
``~/ops-plan-pool/tritonbench``, which is ``tritonbench/`` of git commit
``8be41aa`` with its case layers moved to ``fast_rng``.
"""
from __future__ import annotations

import ast
import collections
import hashlib
import json
import re
import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[1]     # <root>/harness
ROOT = HARNESS.parent                               # the corpus root
sys.path.insert(0, str(HARNESS))
from opslib.case import split_ref_is_exact  # noqa: E402
from opslib.runner import load_operator  # noqa: E402

OUT_DIR = ROOT / "bench"
TIERS = ("basic", "medium", "hard")

FAM_RULES = [
    ("attention", r"attn|attention|flash|gqa|paged|sliding|lightning"),
    ("matmul",    r"matmul|bmm|addmm|gemm|llama_ff|vecmat|tensordot|linear_activation|_linear$|mm_and|tril_mm"),
    ("linalg",    r"\bqr\b|^lu$|\bdet\b|\beig\b|cholesky|solve|\bldl\b|inverse|\bsvd\b|least_squares|matrix_power|\bgram\b|jacobi"),
    ("norm",      r"norm|softmax|log_softmax|ksoftmax|welfold|layer_norm|rms"),
    ("reduce",    r"reduce|reduction|argmax|argmin|^sum$|^mean$|^std$|^var$|^max$|^min$|logsumexp|topk|cumsum"),
    ("loss",      r"loss|ce_loss|cross_entropy|kldiv|mse|nll"),
    ("quant",     r"int8|quant|dequant|fp4|fp8"),
    ("conv_pool", r"conv|pool|upsample|pixel|interpolate|batch_norm|instance_norm|group_norm"),
    ("layout",    r"transpose|permute|reshape|flip|roll|shift|shuffle|gather|scatter|index_select|index_fill|ifftshift|destindex"),
    ("fla",       r"^(chunk|fused_recurrent|parallel|prepare|gdn|delta_rule|retention|hgrn|gla|wy|comba|attnres|kda|rwkv|gated_delta)"),
]

GEMM_SIZE, BMM_SIZE, BMM_BATCH = 2048, 1024, 8
ATTN_HEADS, ATTN_DIM, ATTN_SEQ = 8, 64, 2048
LINALG_N = 128
STEADY_ELEMS = 1 << 24

# (class, pattern, operator stem in the pool, explicit rule or None).  None
# takes the shape-aware rule from ``classify``.  Every pick must be a kernel
# that is NOT already in basic/medium/hard: the input corpus is the four
# directories together, and a duplicate would add a file but no new kernel.
M, R, C = "memory", "reduction", "compute"
PICKS = [
    # ------------------------------------------------------------ memory
    (M, "elementwise.transcendental", "gelu", None),
    (M, "elementwise.transcendental", "erf", None),
    (M, "elementwise.transcendental", "gammaln", None),
    (M, "elementwise.transcendental", "logit", None),
    (M, "elementwise.transcendental", "tanh", None),
    (M, "elementwise.transcendental", "pow", None),
    (M, "elementwise.transcendental", "sin_kernel", None),
    (M, "elementwise.simple", "sqrt", None),
    (M, "elementwise.simple", "leaky_relu", None),
    (M, "elementwise.simple", "sigmoid", None),
    (M, "elementwise.simple", "rsqrt", None),
    (M, "elementwise.simple", "selu", None),
    (M, "elementwise.fused", "add_gelu", None),
    (M, "elementwise.fused", "mul_sub", None),
    (M, "elementwise.fused", "combined_activation", None),
    (M, "elementwise.fused", "geglu_tanh_triton", None),
    (M, "elementwise.fused", "swiglu_triton", None),
    (M, "elementwise.fused", "swiglu_backward", None),
    (M, "elementwise.bitwise", "signbit_bitwise_and", None),
    (M, "elementwise.bitwise", "cos_signbit", None),
    (M, "elementwise.strided", "relu_strided_buffer", None),
    (M, "broadcast", "add_mean", None),
    (M, "broadcast", "exp_mean", None),
    (M, "broadcast", "gelu_std", None),
    (M, "broadcast", "fused_hstack_div", None),
    (M, "broadcast", "fused_tile_exp", None),
    (M, "gather", "index_select_cat", None),
    (M, "gather", "fused_index_select_eq", None),
    (M, "gather", "index_select_bwd", None),
    (M, "gather", "fused_embedding_add_tanh", None),
    (M, "quant", "dequantize_rowwise", None),
    (M, "recurrent", "fused_recurrent_hgrn", None),
    (M, "recurrent", "fused_recurrent_retention", None),
    (M, "pool", "sigmoid_adaptive_avg_pool2d", None),
    (M, "pool", "fused_pairwise_distance_adaptive_avg_pool2d", None),
    (M, "gemv", "matrix_vector_multip", None),
    # --------------------------------------------------------- reduction
    (R, "reduce.row", "max", None),
    (R, "reduce.row", "mean", None),
    (R, "reduce.row", "min", None),
    (R, "reduce.row", "std", None),
    (R, "reduce.row", "argmax", None),
    (R, "softmax", "softmax", None),
    (R, "softmax", "softmax_log", None),
    (R, "softmax", "softmax_mul", None),
    (R, "softmax", "logsumexp", None),
    (R, "softmax", "fused_repeat_interleave_log_softmax", None),
    (R, "norm", "fast_rms_layernorm", None),
    (R, "norm", "l2_norm_triton2", None),
    (R, "norm", "l2_norm_bwd", None),
    (R, "norm", "scaled_add_norm", None),
    (R, "norm", "sigmoid_batch_norm", None),
    (R, "norm", "silu_batch_norm", None),
    (R, "norm", "fused_hardsigmoid_batch_norm", None),
    (R, "norm", "fused_add_mul_groupnorm", None),
    (R, "loss", "fast_ce_loss", None),
    (R, "loss", "kldiv_compute", None),
    (R, "loss", "kldiv_ops", None),
    (R, "loss", "kldiv_triton", None),
    (R, "loss", "fused_cross_entropy_log_softmax", None),
    (R, "similarity", "normalized_cosine_similarity", None),
    # ----------------------------------------------------------- compute
    (C, "gemm", "matmul", None),
    (C, "gemm", "matmul_triton2", None),
    (C, "gemm", "matmul_triton_autotune", None),
    (C, "gemm.epilogue", "triton_linear_activation", None),
    (C, "gemm.epilogue", "softplus_linear", None),
    (C, "gemm.epilogue", "tanh_linear", None),
    (C, "gemm.epilogue", "elu_linear", None),
    (C, "gemm.epilogue", "log_softmax_linear", None),
    (C, "gemm.epilogue", "fused_layer_norm_relu_linear", None),
    (C, "gemm.batched", "batched_vecmat_mult", None),
    (C, "gemm.low_precision", "dequantize_matmul", None),
    (C, "attention", "attn_fwd_causal", None),
    (C, "attention", "attention_forward_triton", None),
    (C, "attention", "attention_kernel", None),
    (C, "attention", "context_attn_fwd", None),
    (C, "attention", "block_sparse_attn", None),
    (C, "attention", "flash_decode", None),
    (C, "attention.linear", "parallel_retention_attention", None),
    (C, "attention.linear", "chunk_delta_rule", None),
    (C, "attention.linear", "chunk_retention", None),
    (C, "attention.linear", "chunk_retention_ops", None),
    # ------------------------------------------------ second-round candidates
    (M, "stencil", "conv2d_add", {"kind": "fixed", "shape": [4096]}),
    (M, "stencil", "relu_conv2d", {"kind": "fixed", "shape": [4096]}),
    (M, "stencil", "gelu_conv2d", {"kind": "fixed", "shape": [4096]}),
    (M, "elementwise.fused", "mul_relu", None),
    (M, "elementwise.fused", "exp_sqrt", None),
    (R, "reduce.arg", "sigmoid_argmax", None),
    # ------------------------------------------------- third-round candidates
    (M, "stencil", "leaky_relu_conv2d", {"kind": "fixed", "shape": [4096]}),
    (M, "layout.shift", "ifftshift", None),
    (M, "elementwise.transcendental", "sin_computation", None),
    (M, "elementwise.polynomial", "chebyshev_polynomial_t", None),
    (M, "elementwise.fused", "sqrt_exp", None),
    (M, "elementwise.binary", "add_value", None),
    (R, "similarity", "cosine_compute", None),
    (C, "gemm.epilogue_reduce", "matrix_multiply_and_row_dot", None),
    (C, "gemm.epilogue_reduce", "scaled_add_dot", None),
    (C, "gemm", "square_matrix", None),
    (C, "linalg", "det", None),
    (C, "linalg", "fused_lu_solve", None),
    (C, "linalg", "cholesky_solve", None),
]



def is_jit(dec) -> bool:
    tgt = dec.func if isinstance(dec, ast.Call) else dec
    return (isinstance(tgt, ast.Attribute) and tgt.attr == "jit"
            and isinstance(tgt.value, ast.Name) and tgt.value.id == "triton") \
        or (isinstance(tgt, ast.Name) and tgt.id == "jit")


def kernel_body(module: Path) -> str:
    tree = ast.parse(module.read_text(errors="ignore"))
    out = ""
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and any(is_jit(d) for d in node.decorator_list):
            out += ast.unparse(node)
    return out


def family(name: str) -> str:
    for fam, rx in FAM_RULES:
        if re.search(rx, name):
            return fam
    return "elementwise"


def _prod(values) -> int:
    out = 1
    for v in values:
        out *= int(v)
    return out


def _output_shape(case: dict):
    expected = case.get("expected") or {}
    for name in list(case.get("outputs", ())) + list(expected):
        if name in expected:
            return list(expected[name].shape)
    return None


def classify(fam: str, name: str, shape: list[int], out_shape, full: int, aux: int):
    """Return (class, validate_shape, scale_rule, bytes_model).

    ``full`` = number of tensors sized like the whole shape; ``aux`` = summed
    element count of the rest (per-row/per-column inputs such as weight/bias).
    """
    nd = len(shape)
    if fam == "matmul":
        if nd == 3:
            return ("compute", [GEMM_SIZE // 8] * 3,
                    {"kind": "matmul", "size": GEMM_SIZE}, {"kind": "matmul"})
        if nd == 4:
            v = BMM_SIZE // 8
            return ("compute", [shape[0], v, v, v],
                    {"kind": "batched_matmul", "batch": shape[0], "size": BMM_SIZE},
                    {"kind": "batched_matmul"})
        if nd == 2:
            n = out_shape[1] if (out_shape and len(out_shape) == 2) else shape[1]
            return ("compute", [256, shape[1]],
                    {"kind": "linear", "k": shape[1], "n": n},
                    {"kind": "linear", "k": shape[1], "n": n})
    if fam == "attention":
        # per-op shape semantics (from each op's ref); a generic formula is wrong
        if "score" in name and nd >= 5:            # [Z, H, N, NKV, D] : QK^T only
            z, h = (list(shape) + [1] * 5)[:2]
            return ("compute", [z, h, 64, 256, ATTN_DIM],
                    {"kind": "attention_score", "z": z, "h": h, "n": ATTN_SEQ,
                     "nkv": ATTN_SEQ, "d": ATTN_DIM}, {"kind": "attention_score"})
        if "paged" in name and nd >= 6:            # [S, H, HKV, NB, BS, D]
            _s, h, hkv, _nb, bs, _d = (list(shape) + [1, 8, 2, 256, 16, 64])[:6]
            return ("compute", [64, h, hkv, 4, bs, ATTN_DIM],
                    {"kind": "paged", "s": 512, "h": h, "hkv": hkv, "bs": bs,
                     "nb": 256, "d": ATTN_DIM}, {"kind": "paged"})
        if nd == 4:                                # [Z, H, N, D] : full attention
            return ("compute", [1, ATTN_HEADS, 256, ATTN_DIM],
                    {"kind": "attention", "heads": ATTN_HEADS,
                     "seq": ATTN_SEQ, "dim": ATTN_DIM}, {"kind": "attention"})
        if "gqa" in name and nd == 5:              # [Z, HQ, HKV, N, D]
            z, hq, hkv = (list(shape) + [1, 8, 2, 2048, 64])[:3]
            return ("compute", [z, hq, hkv, 256, ATTN_DIM],
                    {"kind": "gqa", "z": z, "hq": hq, "hkv": max(1, hkv),
                     "seq": ATTN_SEQ, "d": ATTN_DIM}, {"kind": "gqa"})
        if nd == 5:                                # [B, H, T, D, DV] : linear attention
            b, h = (list(shape) + [2, 8, 2048, 64, 64])[:2]
            return ("compute", [b, h, 256, ATTN_DIM, ATTN_DIM],
                    {"kind": "lightning", "b": b, "h": h, "seq": ATTN_SEQ,
                     "d": ATTN_DIM, "dv": ATTN_DIM}, {"kind": "lightning"})
    if fam == "linalg":
        return ("compute", [256], {"kind": "linalg", "n": LINALG_N}, {"kind": "linalg", "n": LINALG_N})
    cls = "reduction" if fam in ("norm", "reduce", "loss") else "memory"
    model = {"kind": "rowreduce" if cls == "reduction" else "elementwise",
             "full": full, "aux": aux}
    if cls == "reduction" and nd >= 2:
        cols = max(1024, int(shape[-1]))     # a real reduction width, not 16
        return cls, [64, cols], {"kind": "reduce", "cols": cols}, model
    base = _prod(shape[1:]) if nd > 1 else 1
    n0 = max(1, (1 << 18) // max(1, base))
    return cls, [n0] + list(shape[1:]), {"kind": "first_dim", "target_elems": STEADY_ELEMS}, model


def _trial_model(case) -> tuple[int, int]:
    """(full, aux): tensors sized like the biggest one, summed size of the rest."""
    import numpy as np

    host = {**case.get("allocations", {}), **case["args"]}
    sizes = [int(v.size) for v in host.values() if isinstance(v, np.ndarray)]
    biggest = max(sizes) if sizes else 1
    return (sum(1 for s in sizes if s == biggest),
            sum(s for s in sizes if s != biggest))


def kernel_digest(path: Path) -> str:
    """sha256 of the file's ``@triton.jit`` source (unparsed AST): the same
    kernel under a different header or case layer has the same digest."""
    return hashlib.sha256(kernel_body(path).encode()).hexdigest()


def _rewrite_header(text: str, ident: str, source: str, sha: str) -> str:
    """Point ``OPERATOR`` at the bench group and record where the file came
    from; everything else in the file is left byte-identical."""
    tree = ast.parse(text)
    lines = text.splitlines(keepends=True)
    for node in tree.body:
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == "OPERATOR"):
            meta = ast.literal_eval(node.value)
            meta.update({"name": f"bench/{ident}", "group": "bench",
                         "channel": "local"})
            new = (f"OPERATOR = {meta!r}\n"
                   f"BENCH_SOURCE = {{'pool': 'tritonbench', 'path': {source!r}, "
                   f"'sha256': {sha!r}}}\n")
            return ("".join(lines[:node.lineno - 1]) + new
                    + "".join(lines[node.end_lineno:]))
    raise ValueError("no literal OPERATOR dict")


def build_entry(cls, pattern, path: Path, rule, tier_kernels):
    name = path.stem
    if kernel_digest(path) in tier_kernels:
        raise ValueError("kernel already in basic/medium/hard")
    op = load_operator(path)
    declared = [list(s) for s in getattr(op, "SHAPES", ())]
    flat = [s for s in declared if s and all(isinstance(x, int) for x in s)]
    if not flat:
        raise ValueError("no integer SHAPES")
    shape = flat[0]
    dtype = str(getattr(op, "DTYPES", ("float32",))[0])
    trial = op.make_case(shape=tuple(shape), dtype=dtype, seed=7)
    full, aux = _trial_model(trial)
    _, vshape, scale, model = classify(family(name), name, shape,
                                       _output_shape(trial), full, aux)
    if rule is not None:
        scale, vshape, model = rule, list(rule["shape"]), {"kind": "fixed"}
    # a non-declared shape proves the operator scales at all
    op.make_case(shape=tuple(vshape), dtype=dtype, seed=7)
    # a row-independent oracle is built on row blocks in threads at
    # benchmark size; only claimed when the split result is bit-identical
    split = (rule is None
             and split_ref_is_exact(op, vshape, dtype))
    return {"id": name, "operator": f"bench/{name}.py", "name": name,
            "pattern": pattern, "family": pattern.split(".")[0], "class": cls,
            "dtype": dtype, "declared_shape": list(shape),
            "validated_shape": list(vshape), "scale": scale,
            "bytes_model": model, "ref_split": "rows" if split else None}


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--pool", required=True,
                        help="directory holding the pool operator files")
    parser.add_argument("--dry-run", action="store_true",
                        help="report the selection, write nothing")
    args = parser.parse_args()
    pool = Path(args.pool).resolve()
    tier_kernels = {kernel_digest(p) for g in TIERS for p in (ROOT / g).glob("*.py")}

    entries, refused, sources = [], [], {}
    for cls, pattern, name, rule in PICKS:
        path = pool / f"{name}.py"
        try:
            entries.append(build_entry(cls, pattern, path, rule, tier_kernels))
            sources[name] = path
        except Exception as exc:  # noqa: BLE001
            refused.append(f"{name}: {type(exc).__name__}: {exc}"[:160])
    print(f"{len(entries)} entries "
          f"{dict(collections.Counter(e['class'] for e in entries))}, "
          f"{len(set(e['pattern'] for e in entries))} patterns")
    for line in refused:
        print(f"REFUSED {line}")
    if args.dry_run:
        return

    for old in OUT_DIR.glob("*.py"):           # the directory is generated
        old.unlink()
    for entry in entries:
        path = sources[entry["id"]]
        text = path.read_text()
        sha = hashlib.sha256(path.read_bytes()).hexdigest()
        (ROOT / entry["operator"]).write_text(_rewrite_header(
            text, entry["id"], f"tritonbench/{path.name}", sha))
    workload = {
        "schema": "ops-plan-bench/3",
        "metric": "kernel_time_s",
        "dtype": "float32",                  # default; each entry names its own
        "source": "bench/*.py (selected by harness/benchmark/select.py)",
        "classes": ["memory", "reduction", "compute"],
        "size_target": {"kind": "llc_multiple", "multiple": 8,
                        "default_llc_bytes": 134217728},
        "entries": entries,
    }
    out = OUT_DIR / "workload.json"
    out.write_text(json.dumps(workload, indent=2) + "\n")
    print(f"wrote {out} and {len(entries)} operator files")


if __name__ == "__main__":
    main()
