"""Shared host helpers for operator files(算子文件 ②③ 层的公共实现)。

The single implementation lives here; the repository-root ``case_utils.py``
and the per-group copies are compatibility shims that re-export this module
(operator files use lazy ``from case_utils import ...`` imports, which any
of the shim locations resolves).

内容:
  - 数组 duck-typing(numpy / torch / cupy / 自研 DeviceArray 通用协议)
  - public_make_case:原各算子文件 ~25 行公共 make_case 包装的集中实现
  - run_case:case 驱动的直接执行(复杂算子的 ② 执行单元)
"""
from __future__ import annotations

import numpy as np


# ---------------------------------------------------------------- 数组 duck-typing
def _array_module(x):
    """数组对象所属的顶层模块(numpy / torch / cupy / 自研 runtime)。"""
    return __import__(type(x).__module__.split(".", 1)[0])


def _dtype_name(dtype):
    """np.dtype / np 标量类型(np.int32) / 'float32' / torch.float32 → 统一名字。"""
    if isinstance(dtype, np.dtype):
        return dtype.name
    if isinstance(dtype, type):
        try:
            return np.dtype(dtype).name
        except TypeError:
            pass
    return str(dtype).rsplit(".", 1)[-1].rstrip("'>")


def _coerce_np_dtype(dtype):
    """torch.float32 / 'float32' / np.int32 / np.dtype → np.dtype。"""
    if isinstance(dtype, np.dtype):
        return dtype
    try:
        return np.dtype(dtype)
    except TypeError:
        return np.dtype(_dtype_name(dtype))


def _map_dtype(module, dtype):
    """dtype 名映射到目标数组库(torch.float32 等;未知库原样传回)。"""
    target = getattr(module, _dtype_name(dtype), None)
    return target if target is not None else dtype


def numel(x):
    """元素个数:numpy/cupy/DeviceArray 用 .size 属性;torch 用 .numel() 方法。"""
    value = getattr(x, "numel", None)
    return int(value()) if callable(value) else int(x.size)


def empty_like(x, dtype=None):
    """与 x 同形(可覆写 dtype)的新数组:numpy → np.empty_like;
    torch/自研数组 → 其所属模块的 empty_like 工厂。"""
    if isinstance(x, np.ndarray):
        element = np.dtype(x.dtype)
        target = element if dtype is None else _coerce_np_dtype(dtype)
        return np.empty_like(x, dtype=target)
    module = _array_module(x)
    if dtype is None:
        return module.empty_like(x)
    return module.empty_like(x, dtype=_map_dtype(module, dtype))


def empty(shape, like, dtype=None):
    """按 shape 新建数组;dtype 与设备语义沿用 like(可覆写 dtype)。"""
    shape = tuple(int(value) for value in shape)
    if isinstance(like, np.ndarray):
        element = np.dtype(like.dtype) if dtype is None else _coerce_np_dtype(dtype)
        return np.empty(shape, dtype=element)
    module = _array_module(like)
    target = getattr(like, "dtype", None) if dtype is None else _map_dtype(module, dtype)
    try:
        return module.empty(shape, dtype=target, device=getattr(like, "device", None))
    except TypeError:
        return module.empty(shape, dtype=target)


def _to_host(value):
    """设备数组 → numpy:torch → .cpu().numpy();DeviceArray → .to_host();numpy 原样。"""
    if isinstance(value, np.ndarray):
        return value
    if hasattr(value, "cpu") and hasattr(value, "numpy"):    # torch
        return value.detach().cpu().numpy().copy()
    if hasattr(value, "to_host"):                             # 自研 DeviceArray
        return value.to_host()
    return value


# ---------------------------------------------------------------- ③ 验证层公共包装
def public_make_case(_make_case, kernel, dtypes, shape=None, dtype=None,
                     seed=None, exact=False):
    """原各文件 ~25 行公共 make_case 的集中实现。

    dtype 归一化(接受 "float32" / "torch.float32" / np.dtype)→ 白名单校验 →
    委托 _make_case → 补 kernel / outputs / launch_meta 默认键 → 构造比较策略。
    ``exact``:该算子输出是否逐位确定(原 basic 文件被 bake 成 ``True or`` /
    ``False or`` 的那个开关,现显式传参);整数输出(kind in "biu")始终精确比较。
    """
    requested = None
    if dtype is not None:
        try:
            requested = np.dtype(dtype).name
        except TypeError:
            requested = str(dtype).rsplit(".", 1)[-1]
    choices = {str(value).rsplit(".", 1)[-1]: value for value in dtypes}
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
    case.setdefault("kernel", kernel)
    case.setdefault("outputs", tuple(case["expected"]))
    case.setdefault("launch_meta", {})
    if "comparison" not in case:
        case["comparison"] = {
            name: {
                "comparator": "array_equal" if exact or value.dtype.kind in "biu" else "allclose",
                "exact": bool(exact or value.dtype.kind in "biu"),
                "rtol": 5e-3 if value.dtype.name == "float16" else 1e-4,
                "atol": 5e-3 if value.dtype.name == "float16" else 1e-4,
                "equal_nan": True,
            }
            for name, value in case["expected"].items()
        }
    return case


# ---------------------------------------------------------------- dtype policy
#: The suite's single tolerance table, derived from the case dtype only.  It is
#: applied uniformly by ``dtype_case`` (the enriched case builder) so no
#: operator can tune a tolerance to make one shape or dtype pass:
#:
#:   float32  -- IEEE single, fused reduction/dot accumulation  1e-3 / 1e-3
#:   float16  -- 10-bit significand, fp32 accumulation        1e-2 / 1e-2
#:   bfloat16 -- 8-bit significand, fp32 accumulation         2e-2 / 2e-2
#:   integer / bool -- exact                                   array_equal
#:
#: bf16 is *wider* than fp16 in exponent and *narrower* in mantissa, so its
#: tolerance is larger.  These are value tolerances (the bf16 host buffers are
#: decoded to float32 before comparison), never bit tolerances.
DTYPE_TOLERANCES = {
    "float32": (1e-3, 1e-3),
    "float16": (1e-2, 1e-2),
    "bfloat16": (2e-2, 2e-2),
}
FLOAT_DTYPES = ("float32", "float16", "bfloat16")


def dtype_name(dtype) -> str:
    """Normalize ``'torch.float32'`` / ``np.float32`` / ``np.dtype`` / ``None``.

    ``None`` means "the operator's default" and is returned as the empty
    string so callers can distinguish it from an explicit dtype.
    """
    if dtype is None:
        return ""
    try:
        return np.dtype(dtype).name
    except TypeError:
        return str(dtype).rsplit(".", 1)[-1].rstrip("'>")


def tolerance_for(dtype) -> tuple[float, float]:
    """(rtol, atol) for one floating case dtype from the shared table."""
    name = dtype_name(dtype)
    if name not in DTYPE_TOLERANCES:
        raise ValueError(f"no tolerance policy for dtype {dtype!r}; "
                         f"choose from {tuple(DTYPE_TOLERANCES)}")
    return DTYPE_TOLERANCES[name]


def comparison_for(dtype, outputs, *, exact=False, storage=None,
                   pointer_dtypes=None) -> dict:
    """Uniform per-output comparison policy for an enriched case.

    Integer and boolean outputs are always bit-exact (``array_equal``), never
    routed through a float tolerance.  Floating outputs use the dtype table;
    a bf16 output is declared on the host as float32 (or uint16) and is decoded
    by the comparator, so the policy compares values.
    """
    pointer_dtypes = pointer_dtypes or {}
    storage = storage or {}
    rtol, atol = tolerance_for(dtype)
    policy = {}
    for name in outputs:
        value = storage.get(name)
        kind = dtype_name(pointer_dtypes.get(
            name, getattr(value, "dtype", dtype)))
        integer = bool(value is not None and getattr(value, "dtype", None) is not None
                       and getattr(value.dtype, "kind", "f") in "biu")
        if exact or integer or kind not in DTYPE_TOLERANCES:
            policy[name] = {"profile": "exact", "comparator": "array_equal",
                            "exact": True, "rtol": 0.0, "atol": 0.0,
                            "equal_nan": False}
        else:
            policy[name] = {"profile": "numerical", "comparator": "allclose",
                            "exact": False, "rtol": rtol, "atol": atol,
                            "equal_nan": True}
    return policy


def _bf16_host(array):
    """float32 host values rounded to bfloat16 (round-to-nearest-even)."""
    values = np.ascontiguousarray(array, dtype=np.float32)
    bits = values.view(np.uint32)
    rounded = (bits + np.uint32(0x7FFF) + ((bits >> 16) & np.uint32(1))) & np.uint32(0xFFFF0000)
    rounded = np.where(np.isnan(values), bits | np.uint32(0x00400000), rounded)
    return rounded.astype(np.uint32).view(np.float32)


def _cast_float_array(array, target):
    """One float array -> the host representation of ``target``.

    bf16 stays on the host as float32 values already rounded to bf16 (the
    runner uploads it as a bf16 pointer); fp16 uses a real float16 host
    buffer; fp32 is a plain float32 buffer.
    """
    if target == "bfloat16":
        return _bf16_host(array)
    return np.ascontiguousarray(array, dtype=np.dtype(target))


def _array_view(shape, dtype, buffer, offset, strides):
    return np.ndarray(tuple(int(v) for v in shape), dtype=dtype, buffer=buffer,
                      offset=int(offset), strides=tuple(int(v) for v in strides))


def _cast_group(entries, target):
    """Cast arrays that share storage while preserving the sharing relation.

    ``entries`` is ``[(key, array), ...]`` with a common storage region.  A
    single array is just cast; a group (in-place / pointer-table cases) is
    cast once and re-viewed, so the kernel still observes the same aliases.
    Returns ``{key: new_array}``.
    """
    import ctypes

    arrays = [array for _, array in entries]
    if len({id(array) for array in arrays}) == 1:
        new = _cast_float_array(arrays[0], target)
        return {key: new for key, _ in entries}
    old_dtype = arrays[0].dtype
    old_itemsize = old_dtype.itemsize
    ptr0 = min(array.ctypes.data for array in arrays)
    end = max(array.ctypes.data + array.nbytes for array in arrays)
    span = end - ptr0
    # A float view whose byte span is not an integral number of elements is
    # not a float buffer we can reinterpret; leave it to the caller.
    if span % old_itemsize:
        raise ValueError("shared storage is not element-aligned")
    count = span // old_itemsize
    raw = (ctypes.c_char * span).from_address(ptr0)
    flat = np.frombuffer(raw, dtype=old_dtype, count=count)
    new_flat = _cast_float_array(flat, target).reshape(-1)
    new_itemsize = new_flat.dtype.itemsize
    out = {}
    for key, array in entries:
        offset = array.ctypes.data - ptr0
        if offset % old_itemsize or any(int(s) % old_itemsize for s in array.strides):
            raise ValueError("shared storage view is not element-aligned")
        new_strides = tuple(int(s) // old_itemsize * new_itemsize
                            for s in array.strides)
        new_offset = offset // old_itemsize * new_itemsize
        out[key] = _array_view(array.shape, new_flat.dtype, new_flat.data,
                               new_offset, new_strides)
    return out


def _array_sections(case):
    for section in ("args", "allocations", "oracle_args"):
        values = case.get(section)
        if isinstance(values, dict):
            for name, value in values.items():
                if isinstance(value, np.ndarray) and value.dtype.kind == "f":
                    yield section, name, value


def convert_float_arrays(mapping, dtype):
    """Return ``mapping`` with every floating array converted to ``dtype``.

    Used to feed a reference implementation the same low-precision values the
    kernel will see, including bf16's float32 host representation.  Shared
    storage between entries is preserved.  Non-arrays (scalars, metadata) and
    integer/boolean arrays pass through unchanged.
    """
    target = dtype_name(dtype)
    if target not in FLOAT_DTYPES:
        return mapping
    items = [(name, value) for name, value in mapping.items()
             if isinstance(value, np.ndarray) and value.dtype.kind == "f"]
    if not items:
        return mapping
    parent = list(range(len(items)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if np.shares_memory(items[i][1], items[j][1]):
                parent[find(i)] = find(j)
    groups = {}
    for index, item in enumerate(items):
        groups.setdefault(find(index), []).append((index, item))
    out = dict(mapping)
    for group in groups.values():
        entries = [(name, value) for _, (name, value) in group]
        replaced = _cast_group(entries, target)
        out.update(replaced)
    return out


def dtype_case(case, dtype, ref=None, *, exact=False):
    """Re-express a float case in ``dtype`` and apply the shared tolerance table.

    The original case is built in one base dtype (usually float32).  Every
    floating array in ``args`` / ``allocations`` / ``oracle_args`` is converted
    to the requested host representation (bf16: float32 values already rounded
    to bf16, see :func:`_bf16_host`), aliases are preserved, ``ref`` is
    recomputed **from the low-precision inputs**, and every floating output
    gets the dtype table's tolerance.  Integer and boolean buffers are left
    untouched and keep exact comparison.
    """
    target = dtype_name(dtype)
    if target not in FLOAT_DTYPES:
        return case

    # Group arrays by storage so in-place cases stay in place.
    items = list(_array_sections(case))
    parent = list(range(len(items)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if np.shares_memory(items[i][2], items[j][2]):
                parent[find(i)] = find(j)
    groups = {}
    for index, item in enumerate(items):
        groups.setdefault(find(index), []).append((index, item))

    replacements = {}
    for group in groups.values():
        entries = [((section, name), array) for _, (section, name, array) in group]
        replaced = _cast_group(entries, target)
        for (section, name), array in replaced.items():
            replacements[(section, name)] = array

    changed = False
    for (section, name), array in replacements.items():
        if not np.shares_memory(array, case[section][name]) or \
                array.dtype != case[section][name].dtype or not np.array_equal(
                    np.asarray(array, dtype=np.float64),
                    np.asarray(case[section][name], dtype=np.float64),
                    equal_nan=True):
            changed = True
        case[section][name] = array

    # Every converted kernel buffer is a device pointer of the requested
    # dtype.  ``oracle_args`` is host-only and is never declared as a pointer.
    pointer_dtypes = dict(case.get("pointer_dtypes") or {})
    for section, name, _array in _array_sections(case):
        if section in ("args", "allocations"):
            pointer_dtypes[name] = target
    case["pointer_dtypes"] = pointer_dtypes

    # Buffers changed dtype/shape metadata: keep the declarations in sync.
    if "buffer_layouts" in case and isinstance(case["buffer_layouts"], dict):
        layouts = {}
        for name, layout in case["buffer_layouts"].items():
            value = case.get("args", {}).get(name, case.get("allocations", {}).get(name))
            if isinstance(value, np.ndarray):
                layouts[name] = {
                    "shape": tuple(int(v) for v in value.shape),
                    "strides": tuple(int(s // value.dtype.itemsize) for s in value.strides),
                }
            else:
                layouts[name] = layout
        case["buffer_layouts"] = layouts
    if "buffer_extents" in case and isinstance(case["buffer_extents"], dict):
        extents = {}
        for name, value in case["buffer_extents"].items():
            array = case.get("args", {}).get(name, case.get("allocations", {}).get(name))
            extents[name] = int(array.size) if isinstance(array, np.ndarray) else value
        case["buffer_extents"] = extents

    if ref is not None:
        merged = {**case.get("args", {}), **case.get("allocations", {}),
                  **case.get("oracle_args", {})}
        case["expected"] = {key: np.asarray(value)
                            for key, value in ref(merged, case.get("reference_meta", case.get("meta", {}))).items()}

    # One dtype-derived policy for every ordinary output; special comparators
    # (quantised interval, sign-invariant) are semantic and stay untouched.
    existing = case.get("comparison") or {}
    policies = {}
    for name in case.get("outputs", tuple(case.get("expected", {})).__iter__()):
        old = existing.get(name) or {}
        # Semantic comparators are not tolerances: an exact bit / mask check
        # and the two interval/sign-invariant policies stay exactly as the
        # operator declared them.
        if old.get("exact") or old.get("comparator") in (
                "array_equal", "quantized_interval", "allclose_sign_invariant"):
            policies[name] = old
            continue
        if name not in case.get("expected", {}):
            if old:
                policies[name] = old
            continue
        storage = {name: case.get("args", {}).get(name, case.get("allocations", {}).get(name))}
        policies[name] = comparison_for(
            target, [name], exact=exact, storage=storage,
            pointer_dtypes=case["pointer_dtypes"])[name]
    case["comparison"] = policies
    case["dtype"] = target
    return case


# ---------------------------------------------------------------- 通用直跑(② 执行单元)
def run_case(module, shape=None, dtype=None, seed=None, to_array=None):
    """case 驱动的直接执行:make_case 构造输入 → kernel[grid] 启动 → 返回输出。

    to_array=None:数组参数按 numpy 原样传给 launcher(自研编译器的 staging
    语义,真实 Triton 会拒收 numpy);传入转换器(如 numpy→torch.cuda 张量)
    即可在真实 Triton/GPU 上执行同一 case(基线自检)。
    """
    from opslib import runner as _runner

    case = module.make_case(shape=shape, dtype=dtype, seed=seed)
    convert = to_array or (lambda array: array)

    def _convert(value):
        if isinstance(value, np.ndarray):
            return convert(value)
        if isinstance(value, np.generic):
            return value.item()
        return value

    args = {name: _convert(value) for name, value in case["args"].items()}
    allocations = {name: convert(value) for name, value in case.get("allocations", {}).items()
                   if isinstance(value, np.ndarray)}
    _runner.launch(module, case, {**allocations, **args})
    pool = {**allocations, **args}
    return {name: _to_host(pool[name]) for name in case["outputs"]}


# ------------------------------------------------------------ data generation
# Building a benchmark-sized case (hundreds of MiB per tensor) is dominated by
# single-threaded host work: numpy's Generator fills one array on one core.
# ``fast_rng`` is a drop-in for ``np.random.default_rng``: a draw of fewer
# than ``_PARALLEL_MIN`` elements is delegated to the plain Generator, so every
# correctness-sized case keeps exactly the values it always had; a larger
# draw is filled in fixed ``_CHUNK``-element chunks, each from its own child
# seed, on a thread pool.  The values depend on the seed and the chunk size
# only -- never on the number of threads.
_PARALLEL_MIN = 1 << 22
_CHUNK = 1 << 22


def _datagen_threads() -> int:
    import os
    value = os.environ.get("OPS_DATAGEN_THREADS")
    if value:
        return max(1, int(value))
    return max(1, min(32, os.cpu_count() or 1))


def parallel_chunks(n: int, work, chunk: int = _CHUNK) -> None:
    """Call ``work(start, stop)`` for every ``chunk``-sized slice of ``range(n)``
    on a thread pool (numpy releases the GIL inside its loops)."""
    from concurrent.futures import ThreadPoolExecutor
    bounds = [(start, min(n, start + chunk)) for start in range(0, n, chunk)]
    threads = min(_datagen_threads(), len(bounds))
    if threads <= 1:
        for start, stop in bounds:
            work(start, stop)
        return
    with ThreadPoolExecutor(threads) as pool:
        for _ in pool.map(lambda b: work(*b), bounds):
            pass


def _size_of(size) -> int | None:
    if size is None:
        return None
    if isinstance(size, (int, np.integer)):
        return int(size)
    total = 1
    for dim in size:
        total *= int(dim)
    return total


def _is_scalar(*values) -> bool:
    return all(np.ndim(v) == 0 for v in values)


class FastGenerator:
    """``np.random.Generator`` with chunked, threaded fills for large draws.

    Methods not overridden here (``permutation``, ``choice``, ...) and every
    small draw go straight to the wrapped Generator.
    """

    def __init__(self, seed=None):
        self._generator = np.random.default_rng(seed)

    def __getattr__(self, name):
        return getattr(self._generator, name)

    def _large(self, size) -> bool:
        n = _size_of(size)
        return n is not None and n >= _PARALLEL_MIN

    def _fill(self, size, dtype, draw):
        """One parent draw seeds the children, so later draws on this
        generator stay deterministic too."""
        n = _size_of(size)
        out = np.empty(n, dtype=dtype)
        base = int(self._generator.integers(0, 2**63))
        children = np.random.SeedSequence(base).spawn((n + _CHUNK - 1) // _CHUNK)

        def work(start, stop):
            child = np.random.Generator(np.random.PCG64(children[start // _CHUNK]))
            draw(child, out[start:stop])
        parallel_chunks(n, work)
        return out.reshape(size if not isinstance(size, (int, np.integer)) else (n,))

    def standard_normal(self, size=None, dtype=np.float64, out=None):
        if out is not None or not self._large(size):
            return self._generator.standard_normal(size, dtype=dtype, out=out)
        return self._fill(size, dtype,
                          lambda g, o: g.standard_normal(dtype=dtype, out=o))

    def random(self, size=None, dtype=np.float64, out=None):
        if out is not None or not self._large(size):
            return self._generator.random(size, dtype=dtype, out=out)
        return self._fill(size, dtype, lambda g, o: g.random(dtype=dtype, out=o))

    def normal(self, loc=0.0, scale=1.0, size=None):
        if not (self._large(size) and _is_scalar(loc, scale)):
            return self._generator.normal(loc, scale, size)
        return self._fill(size, np.float64,
                          lambda g, o: (g.standard_normal(out=o),
                                        np.multiply(o, scale, out=o),
                                        np.add(o, loc, out=o)))

    def uniform(self, low=0.0, high=1.0, size=None):
        if not (self._large(size) and _is_scalar(low, high)):
            return self._generator.uniform(low, high, size)
        return self._fill(size, np.float64,
                          lambda g, o: (g.random(out=o),
                                        np.multiply(o, high - low, out=o),
                                        np.add(o, low, out=o)))

    def integers(self, low, high=None, size=None, dtype=np.int64, endpoint=False):
        if not (self._large(size) and _is_scalar(low, high)):
            return self._generator.integers(low, high, size, dtype=dtype,
                                            endpoint=endpoint)

        def draw(g, o):
            o[...] = g.integers(low, high, o.size, dtype=dtype, endpoint=endpoint)
        return self._fill(size, dtype, draw)


def fast_rng(seed=None) -> FastGenerator:
    """Drop-in for ``np.random.default_rng(seed)`` in operator case layers."""
    return FastGenerator(seed)


# ------------------------------------------------------------- split oracle
def split_ref(ref, rows_per_chunk: int | None = None):
    """Wrap ``ref(args, meta)`` so it runs on row blocks of axis 0 in threads.

    Every array argument whose leading dimension equals the largest array's
    leading dimension is sliced; everything else is passed whole.  Every
    output whose leading dimension matches is concatenated back; any other
    output shape makes the wrapper refuse (``ValueError``).

    Splitting is only correct when each output row depends on the same input
    rows alone -- a property of the operator, not of the harness.  Callers
    must establish it first (``split_ref_is_exact``); the benchmark records
    it per entry as ``"ref_split": "rows"``.
    """
    def wrapped(args, meta):
        arrays = {k: v for k, v in args.items() if isinstance(v, np.ndarray) and v.ndim}
        if not arrays:
            return ref(args, meta)
        lead = max(arrays.values(), key=lambda a: a.size).shape[0]
        split = {k for k, v in arrays.items() if v.shape[0] == lead}
        width = max(1, max(arrays[k].size for k in split) // lead)
        rows = rows_per_chunk or max(1, _CHUNK // width)
        if lead <= rows:
            return ref(args, meta)
        bounds = [(r, min(lead, r + rows)) for r in range(0, lead, rows)]
        parts = [None] * len(bounds)

        def work(i):
            r0, r1 = bounds[i]
            chunk = {k: (v[r0:r1] if k in split else v) for k, v in args.items()}
            parts[i] = ref(chunk, meta)
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(min(_datagen_threads(), len(bounds))) as pool:
            list(pool.map(work, range(len(bounds))))
        out = {}
        for name in parts[0]:
            pieces = [np.asarray(p[name]) for p in parts]
            if any(p.ndim == 0 or p.shape[0] != r1 - r0
                   for p, (r0, r1) in zip(pieces, bounds)):
                raise ValueError(f"output {name!r} is not row-aligned")
            out[name] = np.concatenate(pieces, axis=0)
        return out
    return wrapped


def split_ref_is_exact(module, shape, dtype, seed=7, chunks: int = 4) -> bool:
    """True when ``module.ref`` split into ``chunks`` row blocks reproduces the
    whole-array result bit for bit on the case built at ``shape``."""
    case = module.make_case(shape=tuple(shape), dtype=dtype, seed=seed)
    args = case.get("oracle_args") or case["args"]
    meta = case.get("meta", {})
    whole = module.ref(args, meta)
    arrays = [v for v in args.values() if isinstance(v, np.ndarray) and v.ndim]
    if not arrays:
        return False
    lead = max(arrays, key=lambda a: a.size).shape[0]
    if lead < chunks:
        return False
    try:
        parted = split_ref(module.ref, rows_per_chunk=-(-lead // chunks))(args, meta)
    except Exception:  # noqa: BLE001
        return False
    if set(parted) != set(whole):
        return False
    return all(np.asarray(parted[k]).shape == np.asarray(whole[k]).shape
               and np.array_equal(np.asarray(parted[k]), np.asarray(whole[k]),
                                  equal_nan=True)
               for k in whole)


class split_ref_scope:
    """``with split_ref_scope(module):`` -- inside, the module-level ``ref``
    is the split version (``split_ref``); the case layer looks ``ref`` up at
    call time, so ``make_case`` picks it up.  ``enabled=False`` is a no-op."""

    def __init__(self, module, enabled: bool = True):
        self.module, self.enabled, self.original = module, enabled, None

    def __enter__(self):
        if self.enabled and callable(getattr(self.module, "ref", None)):
            self.original = self.module.ref
            self.module.ref = split_ref(self.original)
        return self.module

    def __exit__(self, *exc):
        if self.original is not None:
            self.module.ref = self.original
        return False


def make_case_split(module, shape=None, dtype=None, seed=None):
    """``module.make_case`` with its ``ref`` split into row blocks."""
    with split_ref_scope(module):
        return module.make_case(shape=shape, dtype=dtype, seed=seed)
