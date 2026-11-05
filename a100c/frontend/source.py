"""Operator module and case-layer loading by AST (FE-SOURCE-CONTRACT).

The compile unit is one operator file from the corpus's declared set
(``suite/dev/*.py``, ``suite/perf/*.py``): docstring + ``OPERATOR`` literal
+ exactly one ``@triton.jit`` function (possibly ``@triton.autotune``
wrapped) + case layer (``SHAPES``, ``DTYPES``, ``FIXED_META``,
``LAUNCH_META``, ``ref``, ``_make_case``, ``make_case``).

The frontend reads the module AST -- it never imports the operator module
for execution semantics.  A unit that violates the declared invariants (two
jit functions, a foreign import on the execution path, ``import torch``,
an unparseable case layer) is refused with a source location, never
compiled on a guess (MECH-DIAGNOSTIC-REFUSAL).
"""
from __future__ import annotations

import ast
import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

__all__ = ["FrontendError", "KernelParam", "AutotuneConfig",
           "OperatorSource", "load_operator", "load_operator_text"]


class FrontendError(Exception):
    """A located refusal: the file, the position, the construct, the reason."""

    def __init__(self, path: str, line: int, col: int, construct: str,
                 message: str):
        super().__init__(
            f"{path}:{line}:{col}: {construct}: {message}")
        self.path = path
        self.line = line
        self.col = col
        self.construct = construct
        self.message = message

    @property
    def location(self) -> str:
        return f"{self.path}:{self.line}:{self.col}"


@dataclass(frozen=True)
class KernelParam:
    name: str
    is_constexpr: bool
    annotation: Optional[str] = None       # e.g. "tl.constexpr", "tl.tensor"
    default: object = None                 # constexpr default (resolved)
    has_default: bool = False


@dataclass(frozen=True)
class AutotuneConfig:
    """One ``triton.Config`` of an ``@triton.autotune`` space."""
    constexprs: Dict[str, object]
    num_warps: Optional[int] = None
    num_stages: Optional[int] = None


@dataclass
class OperatorSource:
    """The AST-loaded compile unit (no execution semantics)."""
    path: str
    rel_path: str
    sha256: str
    kernel_name: str
    params: Tuple[KernelParam, ...]
    do_not_specialize: Tuple[str, ...]
    do_not_specialize_on_alignment: Tuple[str, ...]
    autotune_configs: Tuple[AutotuneConfig, ...] = ()
    autotune_key: Tuple[str, ...] = ()
    constexpr_globals: Dict[str, object] = field(default_factory=dict)
    case_literals: Dict[str, object] = field(default_factory=dict)
    kernel_ast: Optional[ast.FunctionDef] = None

    @property
    def is_autotune(self) -> bool:
        return bool(self.autotune_configs)

    def constexpr_param_names(self) -> Tuple[str, ...]:
        return tuple(p.name for p in self.params if p.is_constexpr)

    def param_names(self) -> Tuple[str, ...]:
        return tuple(p.name for p in self.params)


_SOURCE_CACHE: Dict[str, tuple] = {}


def load_operator(path, corpus_root=None) -> OperatorSource:
    """Load and validate one operator file (cached by content)."""
    path = Path(path)
    text = path.read_text(encoding="utf-8", errors="replace")
    rel = _rel_path(path, corpus_root)
    key = str(path.resolve())
    digest = hashlib.sha256(text.encode()).hexdigest()
    cached = _SOURCE_CACHE.get(key)
    if cached is not None and cached[0] == digest:
        return cached[1]
    unit = load_operator_text(text, str(path), rel)
    unit.sha256 = digest
    _SOURCE_CACHE[key] = (digest, unit)
    return unit


def _rel_path(path: Path, corpus_root) -> str:
    if corpus_root is not None:
        try:
            return str(Path(path).resolve()
                       .relative_to(Path(corpus_root).resolve()))
        except ValueError:
            pass
    return str(Path(path).resolve()).lstrip("/")


def load_operator_text(text: str, path: str, rel_path: str = "") -> OperatorSource:
    """Parse and validate operator source text (the real loader path)."""
    try:
        tree = ast.parse(text)
    except SyntaxError as exc:
        raise FrontendError(path, exc.lineno or 1, exc.offset or 1,
                            "operator module", f"syntax error: {exc.msg}") \
            from None

    _check_imports(tree, path)

    operator_meta = _operator_literal(tree, path)
    if operator_meta is None:
        raise FrontendError(path, 1, 0, "OPERATOR",
                            "the OPERATOR literal is missing or not a "
                            "literal dict (FE-SOURCE-CONTRACT)")

    kernels = _find_jit_kernels(tree)
    if len(kernels) == 0:
        raise FrontendError(path, 1, 0, "@triton.jit",
                            "no @triton.jit function in the operator module "
                            "(FE-SOURCE-CONTRACT)")
    if len(kernels) > 1:
        first, second = kernels[0], kernels[1]
        raise FrontendError(
            path, second.lineno, second.col_offset + 1, "@triton.jit",
            f"two @triton.jit functions in one operator module "
            f"('{first.name}' at line {first.lineno} and "
            f"'{second.name}' at line {second.lineno}); the compile unit is "
            "exactly one kernel (FE-SOURCE-CONTRACT)")

    kernel = kernels[0]
    jit_kwargs, autotune_configs, autotune_key = _decorators(kernel, path)
    module_constants, constexpr_globals = _module_constants(tree)
    params = _kernel_params(kernel, path, module_constants)
    _check_kernel_body(kernel, path)

    unit = OperatorSource(
        path=path,
        rel_path=rel_path or path,
        sha256="",
        kernel_name=kernel.name,
        params=params,
        do_not_specialize=_normalize_dns(jit_kwargs.get("do_not_specialize"),
                                         params, path, kernel),
        do_not_specialize_on_alignment=_normalize_dns(
            jit_kwargs.get("do_not_specialize_on_alignment"), params,
            path, kernel),
        autotune_configs=autotune_configs,
        autotune_key=autotune_key,
        case_literals=_case_literals(tree, path),
        kernel_ast=kernel,
        constexpr_globals=constexpr_globals,
    )
    return unit


# ---------------------------------------------------------------------------
# Module-level checks
# ---------------------------------------------------------------------------

_ALLOWED_MODULE_IMPORTS = {"numpy", "triton", "case_utils", "math", "mathref",
                           "sys", "__future__"}


def _check_imports(tree: ast.Module, path: str) -> None:
    """Zero torch anywhere; module-level imports serve the case layer only."""
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module or ""]
        else:
            continue
        for name in names:
            root = name.split(".")[0]
            if root == "torch":
                raise FrontendError(
                    path, node.lineno, node.col_offset + 1,
                    f"import {name}",
                    "torch is not allowed in operator files (zero-torch "
                    "rule, ops/AGENTS.md)")


def _operator_literal(tree: ast.Module, path: str) -> Optional[dict]:
    for node in tree.body:
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == "OPERATOR"):
            try:
                value = ast.literal_eval(node.value)
            except (ValueError, SyntaxError):
                return None
            return value if isinstance(value, dict) else None
    return None


def _find_jit_kernels(tree: ast.Module) -> List[ast.FunctionDef]:
    out = []
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        for dec in node.decorator_list:
            target = dec.func if isinstance(dec, ast.Call) else dec
            if (isinstance(target, ast.Attribute)
                    and isinstance(target.value, ast.Name)
                    and target.value.id == "triton"
                    and target.attr in ("jit", "autotune")):
                out.append(node)
                break
            if isinstance(target, ast.Name) and target.id in ("jit",
                                                              "autotune"):
                out.append(node)
                break
    return out


def _decorators(kernel: ast.FunctionDef, path: str):
    """Parse @triton.autotune(...) and @triton.jit(...) keyword arguments."""
    jit_kwargs: Dict[str, object] = {}
    autotune_configs: List[AutotuneConfig] = []
    autotune_key: Tuple[str, ...] = ()
    for dec in kernel.decorator_list:
        target = dec.func if isinstance(dec, ast.Call) else dec
        name = _dotted_name(target)
        if name == "triton.jit" and isinstance(dec, ast.Call):
            jit_kwargs = _literal_kwargs(dec, path)
        elif name == "triton.autotune" and isinstance(dec, ast.Call):
            autotune_configs, autotune_key = _parse_autotune(dec, path)
    return jit_kwargs, tuple(autotune_configs), autotune_key


def _dotted_name(node) -> Optional[str]:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        base = _dotted_name(node.value)
        return f"{base}.{node.attr}" if base else node.attr
    return None


def _literal_kwargs(call: ast.Call, path: str) -> Dict[str, object]:
    out: Dict[str, object] = {}
    for kw in call.keywords:
        try:
            out[kw.arg] = ast.literal_eval(kw.value)
        except (ValueError, SyntaxError):
            out[kw.arg] = None
    return out


def _parse_autotune(dec: ast.Call, path: str):
    """Parse configs=[triton.Config({...}, num_warps=..), ...] and key=[..]."""
    configs: List[AutotuneConfig] = []
    key: Tuple[str, ...] = ()
    for kw in dec.keywords:
        if kw.arg == "configs":
            for element in getattr(kw.value, "elts", ()):  # type: ignore[attr-defined]
                if not (isinstance(element, ast.Call)
                        and _dotted_name(element.func) == "triton.Config"):
                    raise FrontendError(
                        path, getattr(element, "lineno", dec.lineno),
                        getattr(element, "col_offset", dec.col_offset) + 1,
                        "triton.autotune(configs)",
                        f"config entry {_ast_repr(element)} is not a "
                        "triton.Config(...) call")
                if not element.args:
                    raise FrontendError(
                        path, element.lineno, element.col_offset + 1,
                        "triton.Config",
                        "triton.Config requires a leading constexpr dict")
                try:
                    constexprs = ast.literal_eval(element.args[0])
                except (ValueError, SyntaxError):
                    raise FrontendError(
                        path, element.lineno, element.col_offset + 1,
                        "triton.Config",
                        "the constexpr dict of a triton.Config must be a "
                        "literal") from None
                kwargs = _literal_kwargs(element, path)
                configs.append(AutotuneConfig(
                    constexprs=dict(constexprs),
                    num_warps=kwargs.get("num_warps"),
                    num_stages=kwargs.get("num_stages")))
        elif kw.arg == "key":
            try:
                key = tuple(ast.literal_eval(kw.value))
            except (ValueError, SyntaxError):
                key = ()
    return configs, key


def _ast_repr(node) -> str:
    try:
        return ast.unparse(node)
    except Exception:  # pragma: no cover - python < 3.9
        return type(node).__name__


def _kernel_params(kernel: ast.FunctionDef, path: str,
                   module_constants: Dict[str, object]
                   ) -> Tuple[KernelParam, ...]:
    out: List[KernelParam] = []
    args = kernel.args
    if args.vararg or args.kwarg or args.kwonlyargs or args.posonlyargs:
        raise FrontendError(
            path, kernel.lineno, kernel.col_offset + 1, kernel.name,
            "kernel parameters must be plain positional arguments")
    defaults: List[Optional[ast.expr]] = \
        [None] * (len(args.args) - len(args.defaults)) + list(args.defaults)
    for a, default in zip(args.args, defaults):
        annotation = _dotted_name(a.annotation) if a.annotation else None
        is_constexpr = annotation in ("tl.constexpr", "constexpr")
        if default is not None:
            if not is_constexpr:
                raise FrontendError(
                    path, a.lineno, a.col_offset + 1, a.arg,
                    "only tl.constexpr parameters may carry defaults "
                    "(the runner would re-pass a runtime default every "
                    "launch)")
            try:
                value = _resolve_literal(default, module_constants)
            except FrontendError:
                raise
            out.append(KernelParam(name=a.arg, is_constexpr=True,
                                   annotation=annotation, default=value,
                                   has_default=True))
        else:
            out.append(KernelParam(name=a.arg, is_constexpr=is_constexpr,
                                   annotation=annotation))
    return tuple(out)


def _module_constants(tree: ast.Module) -> Tuple[Dict[str, object],
                                                 Dict[str, object]]:
    """Module-level constants, in two tables:

    ``constants`` -- plain literal assignments (usable as parameter
    defaults; the pinned tracer refuses *reading* them from a kernel body
    because they are not constexpr);

    ``constexpr_globals`` -- ``tl.constexpr``-annotated globals (possibly
    wrapped in ``tl.constexpr(...)``), the only globals a kernel body may
    read (pinned ``_is_constexpr_global``).
    """
    constants: Dict[str, object] = {}
    constexpr_globals: Dict[str, object] = {}

    def unwrap(value: ast.expr):
        # tl.constexpr(<literal>) wraps module-level constexpr values
        if (isinstance(value, ast.Call)
                and _dotted_name(value.func) in ("tl.constexpr",
                                                 "constexpr")
                and len(value.args) == 1):
            value = value.args[0]
        try:
            return ast.literal_eval(value)
        except (ValueError, SyntaxError):
            return None

    def is_constexpr_call(value: ast.expr) -> bool:
        # ``X = tl.constexpr(<literal>)``: the assignment itself makes the
        # global a constexpr instance the kernel body may read (the pinned
        # ``_is_constexpr_global``; the corpus's _MAX_FLOAT32_VAL form)
        return (isinstance(value, ast.Call)
                and _dotted_name(value.func) in ("tl.constexpr",
                                                 "constexpr")
                and len(value.args) == 1)

    for node in tree.body:
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)):
            value = unwrap(node.value)
            if value is not None:
                constants[node.targets[0].id] = value
                if is_constexpr_call(node.value):
                    constexpr_globals[node.targets[0].id] = value
        elif (isinstance(node, ast.AnnAssign)
                and isinstance(node.target, ast.Name) and node.value is not None
                and _dotted_name(node.annotation) in ("tl.constexpr",
                                                      "constexpr")):
            value = unwrap(node.value)
            if value is not None:
                constexpr_globals[node.target.id] = value
                constants[node.target.id] = value
    return constants, constexpr_globals


def _resolve_literal(node: ast.expr, module_constants: Dict[str, object]):
    """A default value: a literal or a module-level constant name."""
    if isinstance(node, ast.Name):
        if node.id in module_constants:
            return module_constants[node.id]
        raise FrontendError(
            "<default>", getattr(node, "lineno", 0),
            (getattr(node, "col_offset", 0) or 0) + 1, node.id,
            "default references a name that is not a module-level literal "
            "constant")
    try:
        return ast.literal_eval(node)
    except (ValueError, SyntaxError):
        raise FrontendError(
            "<default>", getattr(node, "lineno", 0),
            (getattr(node, "col_offset", 0) or 0) + 1, "default",
            "constexpr default must be a literal or a module-level constant"
        ) from None


def _check_kernel_body(kernel: ast.FunctionDef, path: str) -> None:
    """No imports on the execution path (the kernel body)."""
    for node in ast.walk(kernel):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            raise FrontendError(
                path, node.lineno, node.col_offset + 1, "import",
                "an import on the kernel execution path is a foreign "
                "dependency (FE-SOURCE-CONTRACT)")


def _case_literals(tree: ast.Module, path: str) -> Dict[str, object]:
    """The case-layer literal tables (SHAPES, DTYPES, FIXED_META,
    LAUNCH_META) read by AST; the payload itself comes from the case."""
    wanted = ("SHAPES", "DTYPES", "FIXED_META", "LAUNCH_META")
    out: Dict[str, object] = {}
    for node in tree.body:
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id in wanted):
            try:
                out[node.targets[0].id] = ast.literal_eval(node.value)
            except (ValueError, SyntaxError):
                raise FrontendError(
                    path, node.lineno, node.col_offset + 1,
                    node.targets[0].id,
                    "case-layer table must be a literal (FE-SOURCE-CONTRACT)"
                ) from None
    return out


def _normalize_dns(value, params: Tuple[KernelParam, ...], path: str,
                   kernel: ast.FunctionDef) -> Tuple[str, ...]:
    """Normalize a do_not_specialize argument (names or indices) to names."""
    if value is None:
        return ()
    if isinstance(value, (str, int)):
        value = [value]
    if not isinstance(value, (list, tuple)):
        raise FrontendError(
            path, kernel.lineno, kernel.col_offset + 1, "@triton.jit",
            f"do_not_specialize must be a name, index or list, got {value!r}")
    names = [p.name for p in params]
    out: List[str] = []
    for item in value:
        if isinstance(item, bool):
            raise FrontendError(
                path, kernel.lineno, kernel.col_offset + 1, "@triton.jit",
                f"do_not_specialize entry {item!r} is not a name or index")
        if isinstance(item, int):
            if not (0 <= item < len(names)):
                raise FrontendError(
                    path, kernel.lineno, kernel.col_offset + 1,
                    "@triton.jit",
                    f"do_not_specialize index {item} out of range")
            out.append(names[item])
        elif isinstance(item, str):
            if item not in names:
                raise FrontendError(
                    path, kernel.lineno, kernel.col_offset + 1,
                    "@triton.jit",
                    f"do_not_specialize names unknown parameter {item!r}")
            out.append(item)
        else:
            raise FrontendError(
                path, kernel.lineno, kernel.col_offset + 1, "@triton.jit",
                f"do_not_specialize entry {item!r} is not a name or index")
    return tuple(out)
