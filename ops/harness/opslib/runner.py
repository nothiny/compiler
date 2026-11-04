"""Shared standalone operator execution and NumPy validation.

The single implementation lives here; the repository-root ``runner.py`` and
the per-group copies are compatibility shims.

CLI: python3 runner.py basic/add.py --dtype float16 --shape 4097
Python: test(op, executor=lambda case: backend.execute(op, case))
PyTorch is optional and imported only by the default GPU execution path.
"""
from pathlib import Path


# case-buffer validation lives once, in opslib.compare
from opslib.compare import _alias_pairs, _validate_case_buffers  # noqa: E402


def _invoke_executor(executor, case, device):
    """Call an executor while optionally passing the selected device.

    Existing ``executor(case)`` callables remain unchanged.  New executors can
    opt in to device propagation by declaring a ``device`` parameter or
    accepting ``**kwargs``.  Signature inspection avoids catching a TypeError
    raised *inside* an executor and retrying the kernel with different
    semantics.
    """
    import inspect

    try:
        parameters = inspect.signature(executor).parameters
    except (TypeError, ValueError):
        return executor(case)
    parameter = parameters.get("device")
    if parameter is not None:
        if parameter.kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY):
            return executor(case, device=device)
        if parameter.kind == inspect.Parameter.POSITIONAL_ONLY:
            return executor(case, device)
    if any(value.kind == inspect.Parameter.VAR_KEYWORD for value in parameters.values()):
        return executor(case, device=device)
    return executor(case)


def launch(op, case, device_args):
    """Launch a module's JIT with caller-owned device buffers."""
    import inspect

    kernel = case.get("kernel")
    if kernel is None:
        kernels = [value for value in vars(op).values()
                   if hasattr(value, "fn") and hasattr(value, "__getitem__")
                   and getattr(value.fn, "__module__", None) == op.__name__]
        if len(kernels) != 1:
            raise ValueError("Expected exactly one JIT kernel or an explicit case['kernel']")
        kernel = kernels[0]
    # Autotune/heuristics wrappers expose ``fn`` as a JITFunction, whose own
    # signature is ``(*args, **kwargs)``.  Unwrap until the Python function so
    # the compiler receives the real kernel parameter names.
    signature_target = kernel
    for _ in range(6):
        if inspect.isfunction(signature_target):
            break
        nested = getattr(signature_target, "fn", None)
        if nested is None or nested is signature_target:
            break
        signature_target = nested
    parameters = inspect.signature(signature_target).parameters
    configs = getattr(kernel, "configs", None)
    autotune_meta = set()
    if configs:
        autotune_meta = set((getattr(configs[0], "kwargs", {}) or {}).keys())
    for overrides in case.get("launches", ({},)):
        values = {**device_args, **case["meta"], **overrides}
        positional, keywords = [], {}
        for name, parameter in parameters.items():
            if name in values:
                value = values[name]
            elif parameter.default is not inspect.Parameter.empty:
                value = parameter.default
            elif name in autotune_meta:
                # The Autotuner launcher supplies constexpr config values
                # after receiving the runtime arguments. Passing one here
                # would produce ``multiple values for BLOCK_SIZE``.
                continue
            else:
                raise TypeError(f"Missing kernel argument: {name}")
            if parameter.kind == inspect.Parameter.KEYWORD_ONLY:
                keywords[name] = value
            else:
                positional.append(value)
        # Positional forwarding avoids collisions with JITFunction.run's own 'self'.
        kernel[case["grid"]](*positional, **keywords, **case.get("launch_meta", {}))


def prepare_gpu_case(case, device="cuda"):
    """Materialize a runner case once on GPU for repeated execution.

    Returns the :class:`opslib.device.StagedCase` (``launch()`` re-launches
    without re-staging; ``outputs()`` downloads the outputs).  Staging lives
    in one place only: the Device implementation (``opslib.devices.torch_ref``
    by default).
    """
    from opslib.device import stage_case
    from opslib.devices.torch_ref import TorchGpuDevice
    _validate_case_buffers(case)
    return stage_case(case, TorchGpuDevice(device))


def outputs_from_prepared(prepared):
    """Copy prepared output buffers to NumPy using runner dtype semantics."""
    return prepared.outputs()


def run(op, case, *, executor=None, device="cuda"):
    """Execute once; return named NumPy output buffers, without comparing.

    The single execution path is the ``Device`` protocol: the default
    (torch reference) device stages, launches and reads back.  A legacy
    ``executor(case)`` / ``executor(op, case)`` callable short-circuits it
    (that API predates Devices and owns the whole execution itself).
    """
    from opslib.device import run_case
    from opslib.devices.torch_ref import TorchGpuDevice

    _validate_case_buffers(case)
    if executor is not None:
        return _invoke_executor(executor, case, device)
    if not str(device).startswith("cuda"):
        raise RuntimeError(
            "The default execution path needs a CUDA device (or supply "
            "executor(case)); for CPU execution use a compiler Device via "
            "compiler_api.run_cases")
    return run_case(case, TorchGpuDevice(device))


def compare(case, actual, expected=None, *, rtol=None, atol=None):
    """Validate output contracts and apply per-output NumPy comparison
    policies.  Forwards to the single-pass implementation in
    :mod:`opslib.compare` (verdicts and error metrics are identical to the
    historical three-pass version; the tests pin that equivalence)."""
    from opslib.compare import compare_case
    return compare_case(case, actual, expected, rtol=rtol, atol=atol)


def test(op, case=None, *, shape=None, dtype=None, seed=None, executor=None, device="cuda", rtol=None, atol=None):
    """Run one case and compare every output using its declared NumPy policy."""
    import numpy as np

    if case is not None and any(value is not None for value in (shape, dtype, seed)):
        raise ValueError("Pass either case or shape/dtype/seed options")
    case = op.make_case(shape=shape, dtype=dtype, seed=seed) if case is None else case
    # BF16 may use float32 host arrays. Quantize inputs before evaluating the oracle.
    changed = False
    for name, kind in case.get("pointer_dtypes", {}).items():
        value = case["args"].get(name)
        if str(kind).rsplit(".", 1)[-1] == "bfloat16" and isinstance(value, np.ndarray) and value.dtype == np.float32:
            bits = value.view(np.uint32)
            rounded = (bits + np.uint32(0x7fff) + ((bits >> 16) & 1)) & np.uint32(0xffff0000)
            rounded = np.where(np.isnan(value), bits | np.uint32(0x00400000), rounded).astype(np.uint32)
            value[...] = rounded.view(np.float32)
            changed = True
    oracle = op.ref({**case["args"], **case.get("allocations", {}), **case.get("oracle_args", {})}, case.get("reference_meta", case["meta"])) if changed else case["expected"]
    expected = {name: np.asarray(value).copy() for name, value in oracle.items()}
    if set(expected) != set(case["outputs"]):
        raise AssertionError("Oracle output names do not match case outputs")
    actual = run(op, case, executor=executor, device=device)
    return compare(case, actual, expected, rtol=rtol, atol=atol)


def load_operator(path):
    """Load one operator module; this path requires Triton to be installed."""
    import hashlib
    import importlib.util
    import sys

    path = Path(path).resolve()
    # operator files import ``case_utils`` / ``mathref`` lazily; those
    # shims live in harness/, next to this package
    harness = str(Path(__file__).resolve().parent.parent)
    if harness not in sys.path:
        sys.path.insert(0, harness)
    name = "_standalone_op_" + hashlib.sha256(str(path).encode()).hexdigest()[:16]
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ValueError(f"Cannot load operator: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    except BaseException:
        sys.modules.pop(name, None)
        raise
    return module
