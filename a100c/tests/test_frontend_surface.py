#!/usr/bin/env python3
"""test_frontend_surface.py -- the declared surface (T006, acceptance[0]).

The declared-surface enumeration test walks all 107 constructs and 280
parameters of the recorded ``workload.api_spec`` and asserts each is
implemented, ignorable with a recorded reason, or refused with a located
diagnostic (FE-UNSUPPORTED-SURFACE, IR-DECLARED-SPACE-COVERAGE).  The
control -- a semantic parameter marked ignorable -- must fail a correctness
test (MECH-WITNESS-TEST): the classification the lowering consults is
load-bearing, not documentation.

Run: python3 a100c/tests/test_frontend_surface.py   (exit 0 = all PASS)
"""
from __future__ import annotations

import json
import sys
import tempfile
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap  # noqa: E402

ROOT = _bootstrap.bootstrap()
OPS = ROOT / "ops"

warnings.filterwarnings("ignore")

FAILURES = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    print(f"{'PASS' if ok else 'FAIL'} {name}"
          f"{(' | ' + detail) if detail else ''}")
    if not ok:
        FAILURES.append(name)
    return ok


import numpy as np  # noqa: E402

from a100c.frontend import lower_tir, source, specialize  # noqa: E402
from a100c.frontend.source import FrontendError  # noqa: E402
from a100c.frontend.surface import (CLASS_IGNORABLE, CLASS_IMPLEMENTED,  # noqa: E402
                                    CLASS_REFUSED, DEFAULT_SURFACE,
                                    EXCLUDED_CONSTRUCTS, SURFACE)
from a100c.ir import dump, tir  # noqa: E402

# ---------------------------------------------------------------------------
# Synthetic operator fixtures (the frontend reads the AST and the case
# payload; it never imports the operator module)
# ---------------------------------------------------------------------------

TEMPLATE = '''\
"""probe operator"""
OPERATOR = {{"name": "probe", "group": "probe", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": []}}
import triton
import triton.language as tl

@triton.jit
def probe_kernel({params}):
{body}
'''


def compile_snippet(params, body, args, meta=None, pointer_dtypes=None,
                    surface=None, decorators="@triton.jit"):
    text = TEMPLATE.format(params=params, body=_indent(body))
    text = text.replace("@triton.jit", decorators, 1)
    src = source.load_operator_text(text, "<probe>", "probe.py")
    case = {"args": args, "meta": meta or {}, "launch_meta": {}}
    if pointer_dtypes:
        case["pointer_dtypes"] = pointer_dtypes
    spec = specialize.specialize(src, case)
    lowering = lower_tir.Lowering(src, spec, surface=surface)
    module = lowering.lower()
    return module, spec, src, lowering


def _indent(body):
    return "\n".join("    " + line for line in body.splitlines()) or "    pass"


def fp32_arg(n=8):
    return np.zeros(n, dtype=np.float32)


def canonical_tir(module):
    """A location- and name-independent structural form of a TIR module:
    ops in order with operand references by definition index, plus result
    types, extent values (with broadcast flags) and attributes."""
    index = {}
    counter = [0]
    out = []

    def vid(value):
        if value.producer is None:
            return ("param", value.name)
        if id(value) not in index:
            index[id(value)] = ("v", counter[0])
            counter[0] += 1
        return index[id(value)]

    for st in module.functions[0].body.statements:
        if not isinstance(st, tir.Op):
            out.append(("region", type(st).__name__))
            continue
        entry = (st.op,
                 tuple(vid(o) for o in st.operands),
                 tuple(repr(r.type) for r in st.results),
                 tuple(tuple((e.value, e.broadcast) for e in r.shape)
                       for r in st.results),
                 tuple(sorted((k, repr(v)) for k, v in st.attrs.items()
                              if k != "from_shape")))
        out.append(entry)
    return repr(out)


def underlying_const(value):
    """Follow broadcast/realize producers down to a const (or None)."""
    seen = 0
    while value.producer is not None and seen < 8:
        if value.producer.op == "const":
            return value.producer
        if value.producer.op in ("broadcast", "realize", "convert"):
            value = value.producer.operands[0]
            seen += 1
            continue
        return None
    return None


BASE_PARAMS = "x_ptr, y_ptr, n, BLOCK: tl.constexpr"
BASE_ARGS = {"x_ptr": fp32_arg(), "y_ptr": fp32_arg(), "n": 17}


def find_ops(module, op_name):
    return [st for st in module.functions[0].body.statements
            if isinstance(st, tir.Op) and st.op == op_name]


# ---------------------------------------------------------------------------
# 1. The table equals the recorded api_spec
# ---------------------------------------------------------------------------

def check_table_matches_api_spec():
    with open(ROOT / "docs/compiler-agent/PROJECT_STATE.json") as fh:
        state = json.load(fh)
    api = state["workload"]["api_spec"]["items"]
    ok = len(SURFACE) == len(api) == 107
    ok &= sum(len(c.parameters) for c in SURFACE) == \
        sum(len(i["parameters"]) for i in api) == 280
    for recorded, embedded in zip(api, SURFACE):
        ok &= recorded["name"] == embedded.name
        ok &= tuple(recorded["parameters"]) == embedded.parameters
        ok &= recorded["tier"] == embedded.tier
        ok &= recorded["corpus_calls"] == embedded.corpus_calls
        ok &= recorded.get("out_of_scope") == embedded.out_of_scope
    check("surface-table-equals-workload-api-spec", ok,
          f"{len(SURFACE)} constructs, "
          f"{sum(len(c.parameters) for c in SURFACE)} parameters")


def check_classification_walk():
    ok = True
    ignorable = refused = implemented = 0
    for construct in SURFACE:
        if not construct.param_classifications:
            continue
        for p in construct.param_classifications:
            if p.classification == CLASS_IGNORABLE:
                ignorable += 1
                ok &= bool(p.reason.strip())
            elif p.classification == CLASS_REFUSED:
                refused += 1
                ok &= bool(p.reason.strip())
            elif p.classification == CLASS_IMPLEMENTED:
                implemented += 1
            else:
                ok = False
    total = ignorable + refused + implemented
    check("every-parameter-classified", ok and total == 280,
          f"implemented={implemented} ignorable={ignorable} "
          f"refused={refused}")
    # every construct-level status is consistent with the parameter table:
    # an implemented construct has a lowering handler (or is a decorator or a
    # dtype constant); a refused construct has none
    check("construct-status-table-consistent",
          all((DEFAULT_SURFACE.is_implemented(c.name)
               and _has_implemented_handler(c.name))
              or (not DEFAULT_SURFACE.is_implemented(c.name))
              for c in SURFACE))


def _refused_param_set():
    from a100c.frontend.surface import REFUSED_PARAMS
    return set(REFUSED_PARAMS)


def _impl_set():
    from a100c.frontend.surface import IMPLEMENTED_CONSTRUCTS
    return IMPLEMENTED_CONSTRUCTS


def _has_implemented_handler(name):
    return name in lower_tir._CONSTRUCT_HANDLERS or \
        name in ("triton.jit", "triton.autotune") or \
        name in ("tl.range", "tl.static_range") or \
        name.startswith("tl.float") or name.startswith("tl.int") or \
        name.startswith("tl.uint") or name.startswith("tl.bfloat") or \
        name == "tl.tensor"


# ---------------------------------------------------------------------------
# 2. Implemented constructs actually lower
# ---------------------------------------------------------------------------

def check_implemented_constructs():
    ok, detail = True, []

    def ok_lower(name, params, body, args, meta):
        nonlocal ok
        try:
            module, _, _, _ = compile_snippet(params, body, args, meta)
            errs = tir.verify_module(module)
            if errs:
                ok = False
                detail.append(f"{name}: verify {errs[0]}")
        except Exception as exc:  # noqa: BLE001
            ok = False
            detail.append(f"{name}: {type(exc).__name__}: {exc}")

    load_body = """
offs = tl.arange(0, BLOCK)
m = offs < n
v = tl.load(x_ptr + offs, mask=m, other=0.0)
tl.store(y_ptr + offs, v, mask=m)
"""
    ok_lower("tl.load/tl.store/tl.arange/tl.program_id/tl.where",
             BASE_PARAMS,
             "pid = tl.program_id(0)\n" + load_body +
             "w = tl.where(v > 0.0, v, v)\n"
             "tl.store(y_ptr + offs, w, mask=m)\n",
             BASE_ARGS, {"BLOCK": 8})
    ok_lower("tl.zeros", BASE_PARAMS,
             "z = tl.zeros([BLOCK], tl.float32)\n"
             "tl.store(y_ptr + tl.arange(0, BLOCK), z)", BASE_ARGS,
             {"BLOCK": 8})
    ok_lower("tl.full", BASE_PARAMS,
             "f = tl.full([BLOCK], 1.5, tl.float32)\n"
             "tl.store(y_ptr + tl.arange(0, BLOCK), f)", BASE_ARGS,
             {"BLOCK": 8})
    ok_lower("tl.zeros_like", BASE_PARAMS,
             "v = tl.load(x_ptr + tl.arange(0, BLOCK))\n"
             "z = tl.zeros_like(v)\n"
             "tl.store(y_ptr + tl.arange(0, BLOCK), z)", BASE_ARGS,
             {"BLOCK": 8})
    ok_lower("tl.constexpr-call", BASE_PARAMS,
             "c = tl.constexpr(8)\n"
             "tl.store(y_ptr + tl.arange(0, c), 1.0)", BASE_ARGS,
             {"BLOCK": 8})
    ok_lower("tl.multiple_of/tl.max_contiguous", BASE_PARAMS,
             "offs = tl.multiple_of(tl.arange(0, BLOCK), 16)\n"
             "offs2 = tl.max_contiguous(offs, 16)\n"
             "tl.store(y_ptr + offs2, 1.0)", BASE_ARGS, {"BLOCK": 8})
    for dtype in ("tl.float32", "tl.float16", "tl.bfloat16", "tl.float64",
                  "tl.int1", "tl.int8", "tl.int16", "tl.int32", "tl.int64",
                  "tl.uint8", "tl.uint16", "tl.uint32", "tl.uint64"):
        ok_lower(dtype, BASE_PARAMS,
                 f"v = tl.zeros([2], {dtype})\n"
                 "tl.store(y_ptr + tl.arange(0, 2), 1.0)", BASE_ARGS,
                 {"BLOCK": 8})
    check("implemented-constructs-lower", ok, "; ".join(detail[:4]))


def check_decorator_constructs():
    # triton.jit with do_not_specialize / do_not_specialize_on_alignment
    text = TEMPLATE.format(
        params="x_ptr, n, k, BLOCK: tl.constexpr",
        body="    tl.store(x_ptr + tl.arange(0, BLOCK), 1.0)").replace(
        "@triton.jit",
        "@triton.jit(do_not_specialize=['n'], "
        "do_not_specialize_on_alignment=['k'])", 1)
    src = source.load_operator_text(text, "<probe>", "probe.py")
    ok = src.do_not_specialize == ("n",) and \
        src.do_not_specialize_on_alignment == ("k",)
    # triton.autotune: deterministic first-config choice
    auto_text = '''\
"""probe"""
OPERATOR = {"name": "probe", "group": "probe", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": []}
import triton
import triton.language as tl

@triton.autotune(
    configs=[
        triton.Config({'BLOCK': 64}, num_warps=4),
        triton.Config({'BLOCK': 128}, num_warps=8),
    ],
    key=['n'],
)
@triton.jit
def probe_kernel(x_ptr, n, BLOCK: tl.constexpr):
    tl.store(x_ptr + tl.arange(0, BLOCK), 1.0)
'''
    src2 = source.load_operator_text(auto_text, "<probe>", "probe.py")
    ok &= len(src2.autotune_configs) == 2
    ok &= src2.autotune_configs[0].constexprs == {"BLOCK": 64}
    ok &= src2.autotune_configs[0].num_warps == 4
    spec = specialize.specialize(src2, {
        "args": {"x_ptr": fp32_arg(), "n": 17}, "meta": {},
        "launch_meta": {}})
    ok &= spec.chosen_config is src2.autotune_configs[0]
    ok &= spec.param_constexprs == {"BLOCK": 64}
    ok &= spec.constexpr_values.get("config.BLOCK") == 64
    # the autotune kernel lowers with the chosen config
    module = lower_tir.lower(src2, spec)
    ok &= not tir.verify_module(module)
    check("decorator-constructs-triton.jit-autotune", ok)


# ---------------------------------------------------------------------------
# 3. Refused constructs produce located diagnostics; excluded constructs
#    are refused as outside the declared surface
# ---------------------------------------------------------------------------

def check_refused_constructs():
    refused = [c for c in SURFACE if not DEFAULT_SURFACE.is_implemented(c.name)]
    failures = []
    for construct in refused:
        name = construct.name
        if name in ("triton.jit", "triton.autotune"):
            continue                      # decorators: checked above
        nargs = max(len(construct.parameters), 1)
        args = ", ".join("a%d" % i for i in range(nargs))
        body = f"tl_result = {name}({args})\n" \
               f"tl.store(y_ptr + tl.arange(0, BLOCK), 1.0)"
        try:
            compile_snippet(BASE_PARAMS, body, BASE_ARGS, {"BLOCK": 8})
            failures.append(f"{name}: lowered (should have been refused)")
        except FrontendError as exc:
            if name not in str(exc):
                failures.append(f"{name}: diagnostic names {exc.construct!r}")
            if not (exc.line and exc.col):
                failures.append(f"{name}: no source location")
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{name}: {type(exc).__name__}: {exc}")
    check("refused-constructs-diagnosed-with-location", not failures,
          f"{len(refused) - 2} refused constructs; "
          + "; ".join(failures[:4]))


def check_excluded_constructs():
    failures = []
    for name in sorted(EXCLUDED_CONSTRUCTS):
        body = (f"v = {name}(1.0)\n"
                "tl.store(y_ptr + tl.arange(0, BLOCK), 1.0)")
        try:
            compile_snippet(BASE_PARAMS, body, BASE_ARGS, {"BLOCK": 8})
            failures.append(f"{name}: lowered")
        except FrontendError as exc:
            if "outside the declared surface" not in str(exc) and \
                    name not in str(exc):
                failures.append(f"{name}: {exc}")
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{name}: {type(exc).__name__}: {exc}")
    # also a plain unknown construct and a dtype that does not exist
    for name, body in (("tl.flibberty", "v = tl.flibberty(1)"),
                       ("tl.float8e5", "v = tl.zeros([2], tl.float8e5)")):
        try:
            compile_snippet(BASE_PARAMS, body + "\n"
                            "tl.store(y_ptr + tl.arange(0, BLOCK), 1.0)",
                            BASE_ARGS, {"BLOCK": 8})
            failures.append(f"{name}: lowered")
        except FrontendError as exc:
            if not exc.line or not exc.col:
                failures.append(f"{name}: no location")
        except Exception as exc:  # noqa: BLE001
            failures.append(f"{name}: {type(exc).__name__}: {exc}")
    check("excluded-constructs-refused-with-location", not failures,
          "; ".join(failures[:4]))


# ---------------------------------------------------------------------------
# 4. Ignorable parameters: accepted, recorded, semantics unchanged
# ---------------------------------------------------------------------------

def check_ignorable_params():
    plain = """
offs = tl.arange(0, BLOCK)
m = offs < n
v = tl.load(x_ptr + offs, mask=m, other=0.0)
tl.store(y_ptr + offs, v, mask=m)
"""
    hinted = """
offs = tl.arange(0, BLOCK)
m = offs < n
v = tl.load(x_ptr + offs, mask=m, other=0.0,
            cache_modifier='.ca', eviction_policy='evict_first')
tl.store(y_ptr + offs, v, mask=m,
         cache_modifier='.wb', eviction_policy='evict_last')
"""
    mod_plain, _, _, lowering_plain = compile_snippet(
        BASE_PARAMS, plain, BASE_ARGS, {"BLOCK": 8})
    mod_hint, _, _, lowering_hint = compile_snippet(
        BASE_PARAMS, hinted, BASE_ARGS, {"BLOCK": 8})
    same = canonical_tir(mod_plain) == canonical_tir(mod_hint)
    ignored = {(i.construct, i.param) for i in lowering_hint.ignored
               if "hint" in i.reason}
    check("ignorable-params-accepted-and-semantic-neutral",
          same and not lowering_plain.ignored
          and {("tl.load", "cache_modifier"), ("tl.load", "eviction_policy"),
               ("tl.store", "cache_modifier"),
               ("tl.store", "eviction_policy")} <= ignored,
          f"ignored={sorted(ignored)}")


# ---------------------------------------------------------------------------
# 5. THE CONTROL: a semantic parameter marked ignorable fails correctness
# ---------------------------------------------------------------------------

def load_ops_of(module):
    return [st for st in module.functions[0].body.statements
            if isinstance(st, tir.Op) and st.op == "load"]


def store_ops_of(module):
    return [st for st in module.functions[0].body.statements
            if isinstance(st, tir.Op) and st.op == "store"]


def masked_load_semantics(module):
    """Correctness check: a masked load with other=0.0 must declare
    default=value and carry a 0.0 constant of the pointee type at its
    disabled positions."""
    loads = load_ops_of(module)
    if len(loads) != 1:
        return False, f"expected one load, got {len(loads)}"
    load = loads[0]
    if load.attrs.get("masked_default") != tir.MaskedDefault.VALUE:
        return False, "default is not 'value'"
    if len(load.operands) != 3:
        return False, "no other operand"
    other = load.operands[2]
    const = underlying_const(other)
    if const is None or const.attrs.get("value") != 0.0:
        return False, "other is not the constant 0.0"
    if other.type != load.results[0].type:
        return False, "other type is not the pointee type"
    return True, "masked load yields 0.0 at disabled positions"


def masked_store_semantics(module):
    """Correctness check: the store must be masked with no-access semantics
    at disabled positions (it must not touch out-of-range positions)."""
    stores = store_ops_of(module)
    if len(stores) != 2:
        return False, f"expected two stores, got {len(stores)}"
    for store in stores:
        if len(store.operands) != 3:
            return False, "store is not masked"
        if store.attrs.get("masked_default") != tir.MaskedDefault.NO_ACCESS:
            return False, "no no-access default"
    return True, "stores are masked with no-access semantics"


def check_control_semantic_param_marked_ignorable():
    body = """
offs = tl.arange(0, BLOCK)
m = offs < n
v = tl.load(x_ptr + offs, mask=m, other=0.0)
tl.store(y_ptr + offs, v, mask=m)
tl.store(y_ptr + offs, 0.0, mask=m)
"""
    # the honest surface: both correctness checks pass
    mod, _, _, _ = compile_snippet(BASE_PARAMS, body, BASE_ARGS, {"BLOCK": 8})
    ok_load, why_load = masked_load_semantics(mod)
    ok_store, why_store = masked_store_semantics(mod)
    check("control-baseline-correctness-passes", ok_load and ok_store,
          f"{why_load}; {why_store}")

    # control 1: tl.load.other marked ignorable -> the masked-load
    # correctness check must FAIL (the disabled positions lose their
    # declared 0.0 and become undefined)
    surface = DEFAULT_SURFACE.with_param_classification(
        "tl.load", "other", CLASS_IGNORABLE, "control: semantic param lied")
    mod2, _, _, _ = compile_snippet(BASE_PARAMS, body, BASE_ARGS,
                                    {"BLOCK": 8}, surface=surface)
    bad_load, why = masked_load_semantics(mod2)
    check("control-load-other-ignorable-fails-correctness", not bad_load, why)

    # control 2: tl.store.mask marked ignorable -> the masked-store
    # correctness check must FAIL (stores become unmasked)
    surface2 = DEFAULT_SURFACE.with_param_classification(
        "tl.store", "mask", CLASS_IGNORABLE, "control: semantic param lied")
    mod3, _, _, _ = compile_snippet(BASE_PARAMS, body, BASE_ARGS,
                                    {"BLOCK": 8}, surface=surface2)
    bad_store, why2 = masked_store_semantics(mod3)
    check("control-store-mask-ignorable-fails-correctness", not bad_store,
          why2)


# ---------------------------------------------------------------------------
# 6. Source-contract refusals carry source locations (FE-SOURCE-CONTRACT)
# ---------------------------------------------------------------------------

def check_source_contract_refusals():
    ok = True
    # two @triton.jit functions
    text = TEMPLATE.format(params="x_ptr", body="    pass") + '''

@triton.jit
def second_kernel(y_ptr):
    pass
'''
    try:
        source.load_operator_text(text, "<probe>", "probe.py")
        ok = False
    except FrontendError as exc:
        ok &= "two @triton.jit functions" in str(exc) and exc.line > 0
    # import torch anywhere
    text = TEMPLATE.format(params="x_ptr", body="    pass").replace(
        "import triton\n", "import torch\nimport triton\n")
    try:
        source.load_operator_text(text, "<probe>", "probe.py")
        ok = False
    except FrontendError as exc:
        ok &= "torch" in str(exc) and exc.line > 0
    # an import on the execution path (inside the kernel body)
    text = TEMPLATE.format(params="x_ptr", body="    import numpy as np\n"
                                              "    pass")
    try:
        source.load_operator_text(text, "<probe>", "probe.py")
        ok = False
    except FrontendError as exc:
        ok &= "execution path" in str(exc) and exc.line == 10
    # missing OPERATOR literal
    text = TEMPLATE.format(params="x_ptr", body="    pass").replace(
        'OPERATOR = {"name": "probe", "group": "probe", "channel": "local",\n'
        '            "execution": "triton_kernel", "verification": '
        '"correctness",\n'
        '            "tags": []}\n', "")
    try:
        source.load_operator_text(text, "<probe>", "probe.py")
        ok = False
    except FrontendError as exc:
        ok &= "OPERATOR" in str(exc)
    # non-literal case-layer table
    text = TEMPLATE.format(params="x_ptr", body="    pass") + \
        "\nSHAPES = ((17,), compute_shapes())\n"
    try:
        source.load_operator_text(text, "<probe>", "probe.py")
        ok = False
    except FrontendError as exc:
        ok &= "literal" in str(exc) and exc.line > 0
    check("source-contract-refusals-located", ok)


def main() -> int:
    check_table_matches_api_spec()
    check_classification_walk()
    check_implemented_constructs()
    check_decorator_constructs()
    check_refused_constructs()
    check_excluded_constructs()
    check_ignorable_params()
    check_control_semantic_param_marked_ignorable()
    check_source_contract_refusals()
    if FAILURES:
        print(f"test_frontend_surface: {len(FAILURES)} check(s) FAILED: "
              f"{FAILURES}")
        return 1
    print("test_frontend_surface: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
