"""One-JIT standalone Triton compiler test case."""

OPERATOR = {"name": "hidden/cross_entropy_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["loss"]}
import triton
import triton.language as tl
from case_utils import fast_rng
LOG2_E = tl.constexpr(1.4426950408889634)

@triton.jit
def liger_cross_entropy_kernel(X_ptr, X_stride, Y_ptr, Y_stride, weight_ptr, loss_ptr, z_loss_ptr, loss_stride, token_accuracy_ptr, token_accuracy_stride, predicted_tokens_ptr, predicted_tokens_stride, n_cols, n_non_ignore, sum_non_ignore_weight, weight_sum, ignore_index, lse_square_scale: tl.constexpr, label_smoothing: tl.constexpr, reduction: tl.constexpr, softcap, RETURN_Z_LOSS: tl.constexpr, RETURN_TOKEN_ACCURACY: tl.constexpr, RETURN_PREDICTED_TOKENS: tl.constexpr, BLOCK_SIZE: tl.constexpr, HAS_WEIGHT: tl.constexpr, HAS_SOFTCAPPING: tl.constexpr, HAS_GRADIENTS: tl.constexpr):
    """
    This kernel computes both cross entropy loss and the gradient of the input.
    We only consider hard label + mean reduction for now. Please refer to https://pytorch.org/docs/stable/generated/torch.nn.CrossEntropyLoss.html for the math.

    Parameters:
    X_ptr: Pointer to input tensor.
    X_stride (int): The stride of the input tensor.
    Y_ptr: Pointer to target tensor.
    Y_stride (int): The stride of the target tensor.
    weight_ptr: Pointer to weight tensor.
    loss_ptr: Pointer to tensor to store the loss.
    z_loss_ptr: Pointer to tensor to store the z loss. No operation if RETURN_Z_LOSS is 0.
    loss_stride (int): The stride of the loss tensor.
    token_accuracy_ptr: Pointer to tensor to store the per-token accuracy. No operation if RETURN_TOKEN_ACCURACY is 0.
    token_accuracy_stride (int): The stride of the token accuracy tensor.
    n_cols (int): The number of columns in the input tensor.
    n_non_ignore (float): The number of non-ignored elements in the batch.
    sum_non_ignore_weight (float): The sum of non-ignored target's weights in the batch.
    weight_sum (float): The sum of weight tensor.
    ignore_index (int): The index to ignore in the target.
    label_smoothing (float): The amount of smoothing when computing the loss, where 0.0 means no smoothing.
    lse_square_scale (float): The scaler of (logsumexp(_input)) ^ 2 adding to the loss for the stability of training.
    reduction (str): The string for the reduction to apply
    softcap (float): The upper threshold for scaling logits to the range (-softcap, +softcap).
    RETURN_Z_LOSS (int): The boolean value to decide whether to store z loss to z_loss_ptr or not. It must be 0 or 1.
    RETURN_TOKEN_ACCURACY (int): The boolean value to decide whether to store per-token accuracy to token_accuracy_ptr or not. It must be 0 or 1.
    BLOCK_SIZE (int): The block size for Triton operations.
    HAS_WEIGHT (bool): The boolean value to determine whether assigning weight to each of the classes.
    HAS_SOFTCAPPING (bool): The boolean value to determine whether applying soft-capping or not.
    HAS_GRADIENTS (bool): The boolean value to determine whether calculating gradients in forward pass.
    """
    program_id = tl.program_id(0).to(tl.int64)
    Y_ptr += program_id * Y_stride
    y = tl.load(Y_ptr)
    X_ptr += program_id * X_stride
    if y == ignore_index:
        for i in range(0, n_cols, BLOCK_SIZE):
            X_offsets = i + tl.arange(0, BLOCK_SIZE)
            tl.store(X_ptr + X_offsets, 0.0, mask=X_offsets < n_cols)
        if RETURN_TOKEN_ACCURACY:
            token_accuracy_ptr += program_id * token_accuracy_stride
            tl.store(token_accuracy_ptr, 0.0)
        if RETURN_PREDICTED_TOKENS:
            predicted_tokens_ptr += program_id * predicted_tokens_stride
            tl.store(predicted_tokens_ptr, -1)
        return
    loss_ptr += program_id * loss_stride
    if RETURN_Z_LOSS:
        z_loss_ptr += program_id * loss_stride
    if RETURN_TOKEN_ACCURACY:
        token_accuracy_ptr += program_id * token_accuracy_stride
    if RETURN_PREDICTED_TOKENS:
        predicted_tokens_ptr += program_id * predicted_tokens_stride
    if HAS_SOFTCAPPING:
        softcap = softcap.to(tl.float32)
    if HAS_WEIGHT:
        sum_non_ignore_weight = sum_non_ignore_weight.to(tl.float32)
        weight_sum = weight_sum.to(tl.float32)
    if HAS_WEIGHT:
        weight_y = tl.load(weight_ptr + y).cast(tl.float32)
    m = float('-inf')
    d = 0.0
    argmax_idx = 0
    ori_X_y = tl.load(X_ptr + y).cast(tl.float32)
    if HAS_SOFTCAPPING:
        ori_X_y = softcap * (2.0 / (1.0 + tl.exp(-(2.0 * (ori_X_y / softcap)))) - 1.0)
    scaled_x_sum = 0.0
    eps = label_smoothing / n_cols
    for i in range(0, n_cols, BLOCK_SIZE):
        X_offsets = i + tl.arange(0, BLOCK_SIZE)
        X_block = tl.load(X_ptr + X_offsets, mask=X_offsets < n_cols, other=float('-inf')).cast(tl.float32)
        if HAS_SOFTCAPPING:
            X_block = softcap * (2.0 / (1.0 + tl.exp(-(2.0 * (X_block / softcap)))) - 1.0)
            X_block = tl.where(X_offsets < n_cols, X_block, float('-inf'))
        block_max = tl.max(X_block)
        if RETURN_TOKEN_ACCURACY or RETURN_PREDICTED_TOKENS:
            is_max_mask = X_block == block_max
            masked_offsets = tl.where(is_max_mask, X_offsets, n_cols)
            current_block_argmax_idx = tl.min(masked_offsets)
            is_new_max = block_max > m
            argmax_idx = tl.where(is_new_max, current_block_argmax_idx, argmax_idx)
        if label_smoothing > 0:
            if HAS_WEIGHT:
                weight_block = tl.load(weight_ptr + X_offsets, mask=X_offsets < n_cols)
                scaled_x_sum += tl.sum(tl.where(X_offsets < n_cols, -eps * X_block * weight_block, 0.0))
            else:
                scaled_x_sum += tl.sum(tl.where(X_offsets < n_cols, -eps * X_block, 0.0))
        m_new = tl.maximum(m, block_max)
        d = d * tl.exp2((m - m_new) * LOG2_E) + tl.sum(tl.exp2((X_block - m_new) * LOG2_E))
        m = m_new
    lse = m + tl.log(d)
    if HAS_GRADIENTS:
        for i in range(0, n_cols, BLOCK_SIZE):
            X_offsets = i + tl.arange(0, BLOCK_SIZE)
            X_block = tl.load(X_ptr + X_offsets, mask=X_offsets < n_cols, other=float('-inf')).cast(tl.float32)
            if HAS_SOFTCAPPING:
                intermediate = 2.0 / (1.0 + tl.exp(-(2.0 * (X_block / softcap)))) - 1.0
                X_block = softcap * intermediate
                X_block = tl.where(X_offsets < n_cols, X_block, float('-inf'))
            if not HAS_WEIGHT:
                X_block = tl.exp2((X_block - m) * LOG2_E) / d
                X_block += 2 * lse_square_scale * lse * X_block
                X_block += -eps
                if reduction == 'mean':
                    X_block = X_block / n_non_ignore
            else:
                weight_block = tl.load(weight_ptr + X_offsets, mask=X_offsets < n_cols)
                softmax_X = tl.exp2((X_block - m) * LOG2_E) / d
                dloss_ori = (1 - label_smoothing) * softmax_X
                dloss_ori = dloss_ori * weight_y
                dloss_smooth = eps * (-weight_block + softmax_X * weight_sum)
                dz_loss = 2 * lse_square_scale * lse * softmax_X
                if reduction == 'mean':
                    dloss_ori = dloss_ori / sum_non_ignore_weight
                    dloss_smooth = dloss_smooth / sum_non_ignore_weight
                    dz_loss = dz_loss / n_non_ignore
                X_block = dloss_ori + dloss_smooth + dz_loss
            if HAS_SOFTCAPPING:
                X_block = X_block * (1 - intermediate * intermediate)
            tl.store(X_ptr + X_offsets, X_block, mask=X_offsets < n_cols)
        tl.debug_barrier()
        softmax_X_y = tl.exp2((ori_X_y - m) * LOG2_E) / d
        if not HAS_WEIGHT:
            dx_y = softmax_X_y
            dx_y += 2 * lse_square_scale * lse * dx_y
            dx_y += -eps
            dx_y += -(1 - label_smoothing)
            if reduction == 'mean':
                dx_y = dx_y / n_non_ignore
        else:
            dloss_ori_y = (1 - label_smoothing) * softmax_X_y - (1 - label_smoothing)
            dloss_ori_y = dloss_ori_y * weight_y
            dloss_smooth_y = eps * (-weight_y + softmax_X_y * weight_sum)
            dz_loss_y = 2 * lse_square_scale * lse * softmax_X_y
            if reduction == 'mean':
                dloss_ori_y = dloss_ori_y / sum_non_ignore_weight
                dloss_smooth_y = dloss_smooth_y / sum_non_ignore_weight
                dz_loss_y = dz_loss_y / n_non_ignore
            dx_y = dloss_ori_y + dloss_smooth_y + dz_loss_y
        if HAS_SOFTCAPPING:
            t_y = ori_X_y / softcap
            dx_y = dx_y * (1 - t_y * t_y)
        tl.store(X_ptr + y, dx_y)
    tl.debug_barrier()
    loss = lse - ori_X_y
    if HAS_WEIGHT:
        loss = weight_y * loss
    if label_smoothing > 0:
        if HAS_WEIGHT:
            smooth_loss = scaled_x_sum + eps * lse * weight_sum
        else:
            smooth_loss = scaled_x_sum + label_smoothing * lse
        loss = loss * (1 - label_smoothing) + smooth_loss
    z_loss = lse_square_scale * lse * lse
    if reduction == 'mean':
        if HAS_WEIGHT:
            loss = loss / sum_non_ignore_weight
        else:
            loss = loss / n_non_ignore
        z_loss = z_loss / n_non_ignore
    loss += z_loss
    tl.store(loss_ptr, loss)
    if RETURN_Z_LOSS:
        tl.store(z_loss_ptr, z_loss)
    if RETURN_TOKEN_ACCURACY:
        is_correct = 1.0 if argmax_idx == y else 0.0
        tl.store(token_accuracy_ptr, is_correct)
    if RETURN_PREDICTED_TOKENS:
        tl.store(predicted_tokens_ptr, argmax_idx)
CASE_SCHEMA = 3
SUPPORT_STATUS = "supported"
VALIDATION_SCOPE = "full-launch-correctness"
SEED = 20260826


def _aligned(values, dtype, alignment=64):
    import numpy as np

    values = np.asarray(values, dtype=np.dtype(dtype))
    raw = np.empty(values.size * values.dtype.itemsize + alignment, dtype=np.uint8)
    start = -raw.ctypes.data % alignment
    result = raw[start : start + values.size * values.dtype.itemsize].view(values.dtype)
    result[...] = values.reshape(-1)
    return result.reshape(values.shape)


def _comparison(outputs, exact=False, rtol=0.0001, atol=0.0001, dtype=None):
    if not exact:
        _comparison_dtype_policy = str(dtype)
        if _comparison_dtype_policy == 'torch.float32':
            (rtol, atol) = (0.0001, 0.0001)
        elif _comparison_dtype_policy == 'torch.bfloat16':
            (rtol, atol) = (0.01, 0.01)
    return {name: {'profile': 'exact' if exact else 'elementwise-strict', 'comparator': 'array_equal' if exact else 'allclose', 'exact': bool(exact), 'rtol': 0.0 if exact else float(rtol), 'atol': 0.0 if exact else float(atol), 'equal_nan': not exact} for name in outputs}


def _layouts(args):
    import numpy as np

    return {
        name: {
            "shape": tuple(int(value) for value in np.asarray(array).shape),
            "strides": tuple(int(value // np.asarray(array).dtype.itemsize) for value in np.asarray(array).strides),
        }
        for name, array in args.items()
        if isinstance(array, np.ndarray)
    }
SHAPES = ((1, 17), (17, 97))
DTYPES = ('float32', 'float16', 'bfloat16')
LAUNCH_META = {"num_warps": 4, "num_stages": 1}

FIXED_META = {"lse_square_scale": 0.0, "label_smoothing": 0.0, "reduction": "mean", "RETURN_Z_LOSS": True, "RETURN_TOKEN_ACCURACY": True, "RETURN_PREDICTED_TOKENS": True, "BLOCK_SIZE": 128, "HAS_WEIGHT": False, "HAS_SOFTCAPPING": False, "HAS_GRADIENTS": True}


def ref(args, meta):
    """Row-wise mathematical reference; preserve buffers the kernel does not write."""
    import numpy as np

    x_buffer = np.asarray(args["X_ptr"])
    labels = np.asarray(args["Y_ptr"]).reshape(-1)
    cols = int(args["n_cols"])
    rows = int(args.get("n_rows", x_buffer.shape[0]))
    x = x_buffer.reshape(-1)
    result = {name: np.asarray(args[name]).copy() for name in ('X_ptr', 'loss_ptr', 'z_loss_ptr', 'token_accuracy_ptr', 'predicted_tokens_ptr')}
    flat = {name: value.reshape(-1) for name, value in result.items()}
    mean = meta["reduction"] == "mean"
    with np.errstate(divide="ignore", invalid="ignore"):
        inv_n = np.divide(1.0, np.float64(args["n_non_ignore"])) if mean else 1.0
        inv_weight = np.divide(1.0, np.float64(args["sum_non_ignore_weight"])) if mean and meta["HAS_WEIGHT"] else 1.0
    weight_sum = float(args["weight_sum"])
    smoothing = float(meta["label_smoothing"])
    eps = smoothing / cols
    z_factor = float(meta["lse_square_scale"])
    weights = np.asarray(args["weight_ptr"], dtype=np.float64).reshape(-1)[:cols] if meta["HAS_WEIGHT"] else np.ones(cols)
    ce_scale = (inv_weight if meta["HAS_WEIGHT"] else inv_n) if mean else 1.0
    z_scale = inv_n if mean else 1.0
    for row in range(rows):
        target = int(labels[row * int(args.get("Y_stride", 1))])
        xi = row * int(args["X_stride"]) + np.arange(cols)
        oi = row * int(args.get("loss_stride", 1))
        if target == int(args["ignore_index"]):
            flat["X_ptr"][xi] = 0.0
            if meta["RETURN_TOKEN_ACCURACY"]:
                flat["token_accuracy_ptr"][row * int(args["token_accuracy_stride"])] = 0.0
            if meta["RETURN_PREDICTED_TOKENS"]:
                flat["predicted_tokens_ptr"][row * int(args["predicted_tokens_stride"])] = -1
            continue
        if not 0 <= target < cols:
            raise ValueError("target is outside the class range")
        logits = x[xi].astype(np.float64)
        if meta["HAS_SOFTCAPPING"]:
            cap = float(args["softcap"])
            capped = np.tanh(logits / cap)
            logits = cap * capped
        maximum = logits.max()
        lse = maximum + np.log(np.exp(logits - maximum).sum())
        nll = weights[target] * (lse - logits[target])
        if smoothing > 0.0:
            smooth = eps * (weight_sum * lse - np.dot(weights, logits)) if meta["HAS_WEIGHT"] else smoothing * lse - eps * logits.sum()
            nll = (1.0 - smoothing) * nll + smooth
        z_loss = z_factor * lse * lse * z_scale
        flat["loss_ptr"][oi] = nll * ce_scale + z_loss
        if meta["RETURN_Z_LOSS"]:
            flat["z_loss_ptr"][oi] = z_loss
        predicted = int(np.argmax(logits))
        if meta["RETURN_TOKEN_ACCURACY"]:
            flat["token_accuracy_ptr"][row * int(args["token_accuracy_stride"])] = float(predicted == target)
        if meta["RETURN_PREDICTED_TOKENS"]:
            flat["predicted_tokens_ptr"][row * int(args["predicted_tokens_stride"])] = predicted
        if not meta["HAS_GRADIENTS"]:
            continue
        probability = np.exp(logits - lse)
        grad = (1.0 - smoothing) * weights[target] * probability
        grad[target] -= (1.0 - smoothing) * weights[target]
        smooth_grad = eps * (weight_sum * probability - weights) if meta["HAS_WEIGHT"] else smoothing * probability - eps
        grad = (grad + smooth_grad) * ce_scale + 2.0 * z_factor * lse * probability * z_scale
        if meta["HAS_SOFTCAPPING"]:
            grad *= 1.0 - capped * capped
        flat["X_ptr"][xi] = grad
    return result


def _make_case(shape=SHAPES[0], dtype=DTYPES[0], seed=SEED):
    del dtype
    import numpy as np
    (rows, cols) = (int(value) for value in shape)
    rng = fast_rng(seed)
    x = _aligned(rng.uniform(-4.0, 4.0, rows * cols), 'float32').reshape(rows, cols)
    y = _aligned(rng.integers(0, cols, rows), 'int64')
    args = {'X_ptr': x, 'X_stride': cols, 'Y_ptr': y, 'Y_stride': 1, 'weight_ptr': _aligned(np.ones(cols), 'float32'), 'loss_ptr': _aligned(np.full(rows, -0.875), 'float32'), 'z_loss_ptr': _aligned(np.full(rows, -0.875), 'float32'), 'loss_stride': 1, 'token_accuracy_ptr': _aligned(np.full(rows, -0.875), 'float32'), 'token_accuracy_stride': 1, 'predicted_tokens_ptr': _aligned(np.full(rows, -7), 'int64'), 'predicted_tokens_stride': 1, 'n_cols': cols, 'n_non_ignore': rows, 'sum_non_ignore_weight': float(rows), 'weight_sum': float(cols), 'ignore_index': -100, 'softcap': 0.0}
    meta = dict(FIXED_META)
    outputs = ('X_ptr', 'loss_ptr', 'z_loss_ptr', 'token_accuracy_ptr', 'predicted_tokens_ptr')
    return {'kernel': liger_cross_entropy_kernel, 'grid': (rows,), 'args': args, 'meta': meta, 'launch_meta': dict(LAUNCH_META), 'inputs': ('X_ptr', 'Y_ptr'), 'outputs': outputs, 'expected': ref(args, meta), 'comparison': {**_comparison(outputs[:-1], rtol=0.0002, atol=2e-05, dtype='torch.float32'), **_comparison(outputs[-1:], exact=True, dtype='torch.float32')}, 'pointer_dtypes': {'X_ptr': 'float32', 'Y_ptr': 'int64', 'weight_ptr': 'float32', 'loss_ptr': 'float32', 'z_loss_ptr': 'float32', 'token_accuracy_ptr': 'float32', 'predicted_tokens_ptr': 'int64'}, 'buffer_extents': {'X_ptr': rows * cols, 'Y_ptr': rows, 'weight_ptr': cols, 'loss_ptr': rows, 'z_loss_ptr': rows, 'token_accuracy_ptr': rows, 'predicted_tokens_ptr': rows}, 'buffer_layouts': _layouts(args), 'alignment': 64, 'aliases': {'X_ptr': 'input-output'}, 'seed': int(seed), 'shape': tuple(shape), 'dtype': 'torch.float32', 'support_status': SUPPORT_STATUS, 'validation_scope': VALIDATION_SCOPE, 'coverage': {'complete_logical_output': True, 'grid_formula': '(rows,)', 'outputs': outputs}}

def make_case(shape=None, dtype=None, seed=None):
    """Create one host case; defaults and supported dtypes are operator-owned."""
    import numpy as np

    requested = None
    if dtype is not None:
        try:
            requested = np.dtype(dtype).name
        except TypeError:
            requested = str(dtype).rsplit(".", 1)[-1]
    choices = {str(value).rsplit(".", 1)[-1]: value for value in DTYPES}
    if requested is not None and requested not in choices:
        raise ValueError(f"unsupported dtype {dtype}; choose from {tuple(choices)}")
    options = {}
    if shape is not None:
        options["shape"] = tuple(shape)
    if requested is not None:
        options["dtype"] = choices[requested]
    if seed is not None:
        options["seed"] = seed
    case = _make_case(**options)
    case.setdefault("outputs", tuple(case["expected"]))
    case.setdefault("launch_meta", {})
    return case


# ------------------------------------------------------------------ ② 执行单元(case 驱动)
def run(shape=None, dtype=None, seed=None, to_array=None):
    """直接执行:make_case 构造输入 → kernel[grid] 启动 → 返回输出。

    to_array=None 时数组参数按 numpy 原样传给 launcher(自研编译器的 staging
    语义);传入数组转换器(如 numpy→torch.cuda)即可在真实 Triton 上执行。
    """
    import sys

    from case_utils import run_case

    return run_case(sys.modules[__name__], shape=shape, dtype=dtype,
                    seed=seed, to_array=to_array)


# ---- suite-v3 case enrichment ----
_ENRICH_BASE = 'float32'
_ENRICH_TARGETS = ("float32", "float16", "bfloat16")
_ENRICH_APPLY_FOR_BASE = True
_ENRICH_ORIGINAL_MAKE_CASE = make_case
_ENRICH_ORIGINAL_DTYPES = {'float32': 'torch.float32'}


def make_case(shape=None, dtype=None, seed=None):
    """Enriched case builder: dtype-generic, one shared tolerance table.

    The original case layer built one float case.  For fp16/bf16 we build that
    same case, temporarily wrap the module ``ref`` so the expected outputs are
    computed from the low-precision inputs, then re-express the buffers in the
    requested dtype (``case_utils.dtype_case``).  Integer / bool requests go
    through the original builder unchanged.
    """
    from case_utils import convert_float_arrays, dtype_case, dtype_name

    requested = dtype_name(dtype) or DTYPES[0]
    if requested in _ENRICH_ORIGINAL_DTYPES:
        # declared before enrichment: the operator's own case builder and tolerances
        return _ENRICH_ORIGINAL_MAKE_CASE(shape=shape, dtype=_ENRICH_ORIGINAL_DTYPES[requested], seed=seed)
    if requested not in _ENRICH_TARGETS:
        return _ENRICH_ORIGINAL_MAKE_CASE(shape=shape, dtype=dtype, seed=seed)
    if requested == _ENRICH_BASE:
        case = _ENRICH_ORIGINAL_MAKE_CASE(shape=shape, dtype=requested, seed=seed)
        case["dtype"] = requested
        if _ENRICH_APPLY_FOR_BASE:
            case = dtype_case(case, requested, ref=None)
        return case
    original_ref = ref

    def enriched_ref(args, meta):
        return original_ref(convert_float_arrays(args, requested), meta)

    globals()["ref"] = enriched_ref
    try:
        case = _ENRICH_ORIGINAL_MAKE_CASE(shape=shape, dtype=_ENRICH_BASE, seed=seed)
    finally:
        globals()["ref"] = original_ref
    return dtype_case(case, requested, ref=None)
