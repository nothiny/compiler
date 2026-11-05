#!/usr/bin/env python3
"""test_scalar_binding.py -- the scalar record/binding and the float
constant rounding (T025).

Two defect classes from the compile census, both owned by the shared
scalar paths (no per-operator branches):

* the record/signature width disagreement (176 census rows: "float scalar
  'eps' width 32 differs from its record width 64"): the bundle record
  holds the host scalar at ITS own width (the packer writes a Python
  float as a float64 record) while the kernel's signature types the
  argument per the pinned mangle_type rules (a Python float is an fp32
  scalar).  The widths are independent by construction, so the binding
  CONVERTS on read under the declared semantics -- RTNE narrowing through
  ``vfncvt.f.f.w`` (the pinned downcast rounding under the default FRM),
  exact widening through ``vfwcvt.f.f.v``, the integer truncation of the
  wide form -- and never refuses on the disagreement.
* the 16-bit float constants (90 census rows: "const: float width 16 is
  not in the scalar core"): fp16 and bf16 constants materialize at their
  OWN width as the raw IEEE bit pattern under the declared constant
  rounding (RTNE -- the same rounding the constprop fold applies and the
  runtime downcast implements), and their consumers splat those bits
  directly (no second rounding).

Checks (each must hold for exit 0):

  record-kind-matches-transport     the compiler's record prediction
                                    (``scalar_record_kind``) and the
                                    transport's own packer
                                    (``a100_support.native_io.scalar``)
                                    agree for every declared scalar record
                                    dtype -- one shared definition -- and
                                    the kernel-signature type either
                                    matches the record width or the pair
                                    has a declared conversion
  record-readback-float64-to-fp32   executed read-back of the Python-float
                                    record (float64) into the declared
                                    fp32 scalar: bit-exact against
                                    numpy's own RTNE conversion, for
                                    inexact, negative, negative-zero and
                                    overflow values, at 1/2/4/8 workers
                                    (the non-vacuity control: the record's
                                    raw low half is NOT the expected bits)
  record-readback-declared-widths   executed read-back at every declared
                                    record width that binds (float16,
                                    float32, int64-record->int32,
                                    int32, int64, uint32, uint64) --
                                    bit-exact against numpy's conversion
  const-bits-declared-rounding      fp16/bf16 constant bits equal the
                                    declared RTNE (numpy fp16; an
                                    independent bf16 reference written
                                    from the IEEE spec), the constprop
                                    fold agrees, and the truncation
                                    control DIFFERS (the check is not
                                    vacuous)
  masked-other-const-executes       the masked-load ``other`` constant is
                                    observable bit-exactly through an
                                    unmasked store (the matmul form) for
                                    fp16/bf16 with inexact values
  full-const-executes               ``tl.full`` at fp16/bf16 stores the
                                    rounded constant bit-exactly
  census-executors                  the class executors run end to end
                                    under their own comparison policies:
                                    leaky_relu_kernel_strided
                                    (negative_slope: a Python float) over
                                    every declared dtype and 1/2/4/8
                                    workers, perf/leaky_relu (slope)

The narrow integer/bool RECORD widths (int8/uint8/bool) are covered at
the record level only: binding them as kernel arguments trips the
separate pre-existing 'scalar widening' census class (the grid wide-view
``smove`` of a sub-32-bit record), which no corpus case exercises and
which this task does not own.

Run: python3 a100c/tests/test_scalar_binding.py   (exit 0 = all PASS)
"""
from __future__ import annotations

import importlib.util
import struct
import sys
import tempfile
import warnings
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap  # noqa: E402

ROOT = _bootstrap.bootstrap()
sys.path.insert(0, str(ROOT / "ops" / "harness"))

warnings.filterwarnings("ignore")

FAILURES = []


def check(name: str, ok: bool, detail: str = "") -> bool:
    print(f"{'PASS' if ok else 'FAIL'} {name}"
          f"{(' | ' + detail) if detail else ''}")
    if not ok:
        FAILURES.append(name)
    return ok


import numpy as np  # noqa: E402

from a100c.driver import Compiler, CompileOptions, PipelineError  # noqa: E402
from a100c.frontend import types as ft  # noqa: E402
from a100c.frontend.types import TypeRuleError  # noqa: E402
from a100c.ir import tir  # noqa: E402
from a100c.lower.binding import scalar_record_kind  # noqa: E402
from a100c.lower.scalar import ScalarLoweringError, float_const_bits  # noqa: E402
from a100c.passes.constprop import _round_float  # noqa: E402

# ---------------------------------------------------------------------------
# the operator-file template and the run helper (the same staging the corpus
# harness uses; every comparison is against an independent numpy reference)
# ---------------------------------------------------------------------------

TEMPLATE = ('"""probe operator %s"""\n'
            'OPERATOR = {"name": "probe/%s", "group": "probe", "channel": "local",\n'
            '            "execution": "triton_kernel", "verification": "correctness",\n'
            '            "tags": []}\n'
            'SHAPES = ((37,),)\n'
            'import numpy as np\n'
            'import triton\n'
            'import triton.language as tl\n'
            '\n'
            '@triton.jit\n'
            'def %s_kernel(out_ptr, n, s, BLOCK: tl.constexpr, OUTD: tl.constexpr):\n'
            '    i = tl.arange(0, BLOCK)\n'
            '    m = i < n\n'
            '    w = tl.full((BLOCK,), 1, OUTD)\n'
            '    v = s * w\n'
            '    tl.store(out_ptr + i, v, mask=m)\n'
            '\n'
            'def ref(args, meta):\n'
            '    n = int(args["n"])\n'
            '    out = np.zeros(__BLOCK__, dtype=args["out_ptr"].dtype)\n'
            '    out[:n] = args["s"]\n'
            '    return {"out_ptr": out}\n'
            '\n'
            '\n'
            'def _make_case(shape=SHAPES[0], dtype="float32", seed=0):\n'
            '    n = int(shape[0])\n'
            '    args = {"out_ptr": np.zeros(__BLOCK__, __OUTNP__), "n": n, "s": __SCALAR__}\n'
            '    meta = {"BLOCK": __BLOCK__, "OUTD": __OUTD__}\n'
            '    grid = ((n + __BLOCK__ - 1) // __BLOCK__,)\n'
            '    return {"args": args, "meta": meta, "grid": grid,\n'
            '            "kernel": %s_kernel, "outputs": ("out_ptr",),\n'
            '            "expected": ref(args, meta),\n'
            '            "comparison": {"out_ptr": {"comparator": "array_equal",\n'
            '                                       "exact": True}}}\n'
            '\n'
            '\n'
            'def make_case(shape=None, dtype=None, seed=None):\n'
            '    return _make_case()\n')


def _operator_file(directory: Path, name: str, out_np: str, outd: str,
                   scalar_expr: str, block: int = 64):
    text = (TEMPLATE % (name, name, name, name)) \
        .replace("__OUTNP__", out_np).replace("__OUTD__", outd) \
        .replace("__SCALAR__", scalar_expr) \
        .replace("__BLOCK__", str(block))
    path = directory / f"{name}.py"
    path.write_text(text)
    return path


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _bits(array) -> np.ndarray:
    """The raw bit view of one array (the bit-exact comparison form)."""
    array = np.asarray(array)
    return array.reshape(-1).view(np.uint32 if array.dtype.itemsize == 4
                                  else np.uint64 if array.dtype.itemsize == 8
                                  else np.uint16)


def _run_case(compiler, module, threads, **make_kwargs):
    import a100_support.native_device as nd
    case = module.make_case(**make_kwargs)
    device = nd.NativeExecutableDevice(compiler, threads)
    staged = device.stage_case(case)
    staged.launch()
    return staged.outputs(), case


# ---------------------------------------------------------------------------
# the record/signature agreement (one shared definition)
# ---------------------------------------------------------------------------

#: every dtype the transport's scalar packer accepts (numpy has no
#: bfloat16 scalar, so the record surface has none; float64 records arise
#: from Python floats, the other widths from numpy scalars)
_RECORD_VALUES = (
    True, np.bool_(True),
    np.int8(-3), np.uint8(200),
    np.int16(-300), np.uint16(60000),
    np.int32(-70000), np.uint32(3000000000),
    np.int64(-(2 ** 40) - 3), np.uint64(2 ** 63 + 9),
    np.float16(0.1), np.float32(0.1), np.float64(0.1),
    7, 2 ** 33 + 5, 0.1, -0.1,
)


def check_record_kind_matches_transport():
    """The compiler's record prediction and the transport's own packer
    agree on (dtype name, width) for every declared scalar record dtype,
    and the kernel-signature type either matches the record width or the
    pair has a declared conversion (floats: the read conversion; ints:
    the wide-form truncation) -- never a width-disagreement refusal."""
    import a100_support.native_io as nio
    bad = []
    for value in _RECORD_VALUES:
        name_mine, width_mine, _signed = scalar_record_kind(value)
        packed, name_transport = nio.scalar(value)
        code, itemsize, _bits_v = struct.unpack("<IIQ", packed)
        if name_mine != name_transport:
            bad.append(f"{value!r}: predicted {name_mine}, packed "
                       f"{name_transport}")
            continue
        if width_mine != itemsize * 8 \
                or code != nio.DTYPES[name_transport]:
            bad.append(f"{value!r}: width {width_mine} vs packed itemsize "
                       f"{itemsize * 8} (code {code})")
        try:
            ty = ft.scalar_arg_type(value)
        except TypeRuleError as exc:
            bad.append(f"{value!r}: cannot type: {exc.message}")
            continue
        if ty.is_float():
            # the declared conversion covers every IEEE binary width pair
            if ty.width not in (16, 32, 64) or ty.name == "bf16":
                bad.append(f"{value!r}: float scalar type {ty!r} has no "
                           "declared record conversion")
        elif ty.width > width_mine:
            bad.append(f"{value!r}: integer scalar type {ty!r} is wider "
                       f"than its record width {width_mine}")
    check("record-kind-matches-transport", not bad, "; ".join(bad[:2]))


# ---------------------------------------------------------------------------
# the executed record read-back (pack a record, read it through the
# generated binding, compare bit-exact)
# ---------------------------------------------------------------------------

def _readback_probe(workdir, compiler, label, out_np, outd, scalar_expr,
                    expected_bits, threads=1):
    path = _operator_file(workdir, f"rb_{label}", out_np, outd, scalar_expr)
    module = _load(path)
    try:
        outputs, _case = _run_case(compiler, module, threads)
        got = np.asarray(outputs["out_ptr"])
        ok = np.array_equal(_bits(got), expected_bits)
        detail = "" if ok else (f"got {got[:4]}, expected bits "
                                f"{expected_bits[:4]}")
        return ok, detail
    except PipelineError as exc:
        return False, f"refused {exc.construct}: {str(exc)[:90]}"
    except Exception as exc:  # noqa: BLE001
        return False, f"{type(exc).__name__}: {str(exc)[:90]}"


def check_readback(workdir, compiler):
    """Executed read-back at the declared record widths.  The Python-float
    probes carry a float64 record into the declared fp32 scalar -- the
    176-row census class -- and must equal numpy's own RTNE conversion
    bit-exactly (including the sign of zero and the overflow to inf).
    The non-vacuity control: the record's raw low half is NOT the
    expected bits, so an implementation that read the record as fp32 bits
    instead of converting would fail."""
    n = 37  # ragged against BLOCK=64 (the mask owns the tail)

    def full_bits(converted, dtype):
        out = np.zeros(64, dtype)
        out[:n] = converted
        return _bits(out)

    probes = [
        # label, out numpy dtype, OUTD constexpr, scalar expr, expected bits
        ("f64rec_to_fp32_inexact", "np.float32", "tl.float32", "0.1",
         full_bits(np.float32(0.1), np.float32)),
        ("f64rec_to_fp32_negative", "np.float32", "tl.float32", "-0.1",
         full_bits(np.float32(-0.1), np.float32)),
        ("f64rec_to_fp32_negzero", "np.float32", "tl.float32", "-0.0",
         full_bits(np.float32(-0.0), np.float32)),
        ("f64rec_to_fp32_overflow", "np.float32", "tl.float32", "1e300",
         full_bits(np.float32(1e300), np.float32)),
        ("f32rec_exact", "np.float32", "tl.float32", "np.float32(0.1)",
         full_bits(np.float32(0.1), np.float32)),
        ("f16rec_exact", "np.float16", "tl.float16", "np.float16(0.1)",
         full_bits(np.float16(0.1), np.float16)),
        ("i64rec_to_i32", "np.int32", "tl.int32", "7",
         full_bits(np.int32(7), np.int32)),
        ("i64rec_i64", "np.int64", "tl.int64", "2 ** 33 + 5",
         full_bits(np.int64(2 ** 33 + 5), np.int64)),
        ("i32rec_i32", "np.int32", "tl.int32", "np.int32(-5)",
         full_bits(np.int32(-5), np.int32)),
        ("i64rec_negative_i64", "np.int64", "tl.int64",
         "np.int64(-(2 ** 40) - 3)",
         full_bits(np.int64(-(2 ** 40) - 3), np.int64)),
        ("u32rec_u32", "np.uint32", "tl.uint32", "np.uint32(3000000000)",
         full_bits(np.uint32(3000000000), np.uint32)),
        ("u64rec_u64", "np.uint64", "tl.uint64", "np.uint64(2 ** 63 + 9)",
         full_bits(np.uint64(2 ** 63 + 9), np.uint64)),
    ]
    bad = []
    for label, out_np, outd, s_expr, expected in probes:
        ok, detail = _readback_probe(workdir, compiler, label, out_np,
                                     outd, s_expr, expected)
        if not ok:
            bad.append(f"{label}: {detail}")
    check("record-readback-declared-widths", not bad, "; ".join(bad[:2]))

    # the worker configurations on the conversion itself (one artifact,
    # every count; the entry binding runs per worker)
    bad = []
    for threads in (1, 2, 4, 8):
        ok, detail = _readback_probe(
            workdir, compiler, "f64rec_to_fp32_inexact", "np.float32",
            "tl.float32", "0.1",
            full_bits(np.float32(0.1), np.float32), threads=threads)
        if not ok:
            bad.append(f"t={threads}: {detail}")
    check("record-readback-float64-to-fp32", not bad, "; ".join(bad[:2]))

    # the non-vacuity control (MECH-WITNESS-TEST): the expected fp32 bits
    # differ from the record's raw low half -- reading the record as fp32
    # bits instead of converting would produce them and fail above
    raw_low = struct.unpack("<I", struct.pack(
        "<I", struct.unpack("<Q", struct.pack("<d", 0.1))[0]
        & 0xFFFFFFFF))[0]
    want = np.float32(0.1).view(np.uint32)
    check("record-readback-conversion-control", raw_low != int(want),
          f"raw low half 0x{raw_low:08x} vs RTNE 0x{int(want):08x} "
          "(the check distinguishes a converted from a re-read record)")


# ---------------------------------------------------------------------------
# the 16-bit float constant bits (the declared rounding)
# ---------------------------------------------------------------------------

def _bf16_reference(value: float) -> int:
    """An independent bf16 encoding written from the IEEE spec in this
    test (not the implementation): the fp32 word's low half rounds
    to-nearest-even into the exponent, overflow past the finite range
    rounds to the infinity."""
    f32 = struct.unpack("<I", struct.pack("<f", value))[0]
    low = f32 & 0xFFFF
    rounded = f32 & 0xFFFF0000
    if low > 0x8000 or (low == 0x8000 and (rounded & 0x10000)):
        rounded += 0x10000
    if 0x7F7F_FFFF < rounded < 0x7F80_0000:
        rounded = 0x7F80_0000
    elif 0xFF7F_FFFF < rounded < 0xFF80_0000:
        rounded = 0xFF80_0000
    return (rounded >> 16) & 0xFFFF


_CONST_VALUES = (0.5, 0.1, -0.1, 1e-3, 1.0 + 2 ** -11, 1.0 + 3 * 2 ** -11,
                 65505.0, 65519.0, 1e30, -1e30, 0.0, -0.0, 1.0, -1.0)


def check_const_bits():
    """fp16 constants: the bits equal numpy's own fp16 RTNE casting
    (overflow values are the IEEE infinity).  bf16 constants: the bits
    equal the independent spec reference, and the constprop fold's
    rounded value re-encodes to the same bits (one declared rounding).
    The truncation control differs, so the checks are not vacuous."""
    bad = []
    for v in _CONST_VALUES:
        got = float_const_bits(v, tir.FLOAT16, None)
        want = int(np.float16(v).view(np.uint16))
        if got != want:
            bad.append(f"fp16 {v!r}: 0x{got:04x} != 0x{want:04x}")
        got = float_const_bits(v, tir.BFLOAT16, None)
        want = _bf16_reference(v)
        if got != want:
            bad.append(f"bf16 {v!r}: 0x{got:04x} != 0x{want:04x}")
        folded = _round_float(v, tir.BFLOAT16)
        if folded is not None and \
                float_const_bits(folded, tir.BFLOAT16, None) != want:
            bad.append(f"bf16 fold {v!r}: the folded value re-encodes "
                       "differently")
        folded16 = _round_float(v, tir.FLOAT16)
        want16 = int(np.float16(v).view(np.uint16))
        if folded16 is not None and \
                float_const_bits(folded16, tir.FLOAT16, None) != want16:
            bad.append(f"fp16 fold {v!r}: the folded value re-encodes "
                       "differently")
    check("const-bits-declared-rounding", not bad, "; ".join(bad[:2]))

    # the truncation control: RTNE and truncation differ on these values
    # (a truncating implementation would fail the checks above)
    f32_01 = struct.unpack("<I", struct.pack("<f", 0.1))[0]
    truncated = f32_01 >> 16
    check("const-bits-rounding-control",
          _bf16_reference(0.1) != truncated
          and int(np.float16(0.1).view(np.uint16))
          != (struct.unpack("<I", struct.pack("<f", 0.1))[0] & 0xFFFF),
          f"bf16 RTNE 0x{_bf16_reference(0.1):04x} vs trunc 0x{truncated:04x}")


# ---------------------------------------------------------------------------
# the executed 16-bit float constants (the masked-load other / tl.full)
# ---------------------------------------------------------------------------

_MASKED_TEMPLATE = ('"""probe operator %s"""\n'
                    'OPERATOR = {"name": "probe/%s", "group": "probe", "channel": "local",\n'
                    '            "execution": "triton_kernel", "verification": "correctness",\n'
                    '            "tags": []}\n'
                    'SHAPES = ((37,),)\n'
                    'import numpy as np\n'
                    'import triton\n'
                    'import triton.language as tl\n'
                    '\n'
                    '@triton.jit\n'
                    'def %s_kernel(x_ptr, y_ptr, n, BLOCK: tl.constexpr):\n'
                    '    i = tl.arange(0, BLOCK)\n'
                    '    m = i < n\n'
                    '    x = tl.load(x_ptr + i, mask=m, other=__OTHER__)\n'
                    '    tl.store(y_ptr + i, x)\n'
                    '\n'
                    'def ref(args, meta):\n'
                    '    n = int(args["n"])\n'
                    '    x = np.asarray(args["x_ptr"])\n'
                    '    out = np.zeros(__BLOCK__, dtype=x.dtype)\n'
                    '    out[:n] = x[:n]\n'
                    '    out[n:] = __OTHER__\n'
                    '    return {"y_ptr": out}\n'
                    '\n'
                    '\n'
                    'def _make_case(shape=SHAPES[0], dtype="float16", seed=0):\n'
                    '    n = int(shape[0])\n'
                    '    rng = np.random.default_rng(seed)\n'
                    '    x = rng.standard_normal(n).astype(__HOST__)\n'
                    '    args = {"x_ptr": x, "y_ptr": np.zeros(__BLOCK__, __HOST__), "n": n}\n'
                    '    meta = {"BLOCK": __BLOCK__}\n'
                    '    grid = ((n + __BLOCK__ - 1) // __BLOCK__,)\n'
                    '    case = {"args": args, "meta": meta, "grid": grid,\n'
                    '            "kernel": %s_kernel, "outputs": ("y_ptr",),\n'
                    '            "expected": ref(args, meta),\n'
                    '            "comparison": {"y_ptr": {"comparator": "array_equal",\n'
                    '                                       "exact": True}}}\n'
                    '    if __BF16__:\n'
                    '        case["pointer_dtypes"] = {"x_ptr": "bfloat16",\n'
                    '                                  "y_ptr": "bfloat16"}\n'
                    '    return case\n'
                    '\n'
                    '\n'
                    'def make_case(shape=None, dtype=None, seed=None):\n'
                    '    return _make_case()\n')


def _masked_probe_file(directory: Path, name: str, other: str,
                       bf16: bool):
    text = (_MASKED_TEMPLATE % (name, name, name, name)) \
        .replace("__OTHER__", other) \
        .replace("__HOST__", "np.float32" if bf16 else "np.float16") \
        .replace("__BF16__", "True" if bf16 else "False") \
        .replace("__BLOCK__", "64")
    path = directory / f"{name}.py"
    path.write_text(text)
    return path


def check_masked_other(workdir, compiler):
    """The masked-load ``other`` constant is observable through an
    UNMASKED store (the disabled lanes carry it into the output): fp16
    and bf16, with values inexact in the format so the declared RTNE is
    what the comparison sees.  The bf16 expected is the spec reference's
    expansion (the transport decodes bf16 outputs as the exact fp32
    expansion of the stored bits)."""
    bad = []
    for label, other, bf16 in (("fp16", "0.1", False),
                               ("fp16_half", "0.5", False),
                               ("bf16", "0.1", True),
                               ("bf16_half", "0.5", True)):
        path = _masked_probe_file(workdir, f"mo_{label}", other, bf16)
        module = _load(path)
        try:
            outputs, case = _run_case(compiler, module, 1)
            got = np.asarray(outputs["y_ptr"])
            if bf16:
                # the transport's bf16 decode is the exact fp32 expansion
                # of the stored 16-bit pattern; the expected bits are the
                # spec reference's rounding of the loaded lanes and the
                # ``other`` tail
                got_bits = (got.view(np.uint32) >> 16).astype(np.uint16)
                want = _bf16_bits_of(
                    np.asarray(case["expected"]["y_ptr"],
                               dtype=np.float32))
                ok = np.array_equal(got_bits, want)
            else:
                exp = np.asarray(case["expected"]["y_ptr"])
                ok = np.array_equal(_bits(got), _bits(exp))
            detail = "" if ok else f"got {got[35:40]}, tail differs"
            if not ok:
                bad.append(f"{label}: {detail}")
        except PipelineError as exc:
            bad.append(f"{label}: refused {exc.construct}: "
                       f"{str(exc)[:80]}")
        except Exception as exc:  # noqa: BLE001
            bad.append(f"{label}: {type(exc).__name__}: {str(exc)[:80]}")
    check("masked-other-const-executes", not bad, "; ".join(bad[:2]))


def _bf16_bits_of(values: np.ndarray) -> np.ndarray:
    """The bf16 bit pattern of one fp32 array (this test's reference)."""
    bits = np.asarray(values, dtype=np.float32).view(np.uint32)
    low = bits & 0xFFFF
    rounded = bits & np.uint32(0xFFFF0000)
    up = (low > 0x8000) | ((low == 0x8000) & ((rounded & 0x10000) != 0))
    rounded = rounded + np.where(up, np.uint32(0x10000), np.uint32(0))
    return (rounded >> 16).astype(np.uint16)


_FULL_TEMPLATE = ('"""probe operator %s"""\n'
                  'OPERATOR = {"name": "probe/%s", "group": "probe", "channel": "local",\n'
                  '            "execution": "triton_kernel", "verification": "correctness",\n'
                  '            "tags": []}\n'
                  'SHAPES = ((37,),)\n'
                  'import numpy as np\n'
                  'import triton\n'
                  'import triton.language as tl\n'
                  '\n'
                  '@triton.jit\n'
                  'def %s_kernel(y_ptr, n, BLOCK: tl.constexpr, OUTD: tl.constexpr):\n'
                  '    i = tl.arange(0, BLOCK)\n'
                  '    v = tl.full((__BLOCK__,), __VALUE__, __OUTD__)\n'
                  '    tl.store(y_ptr + i, v)\n'
                  '\n'
                  'def ref(args, meta):\n'
                  '    return {"y_ptr": np.full(__BLOCK__, __VALUE__, dtype=__OUTNP__)}\n'
                  '\n'
                  '\n'
                  'def _make_case(shape=SHAPES[0], dtype="float16", seed=0):\n'
                  '    n = int(shape[0])\n'
                  '    args = {"y_ptr": np.zeros(__BLOCK__, __OUTNP__), "n": n}\n'
                  '    meta = {"BLOCK": __BLOCK__, "OUTD": __OUTD__}\n'
                  '    grid = (1,)\n'
                  '    return {"args": args, "meta": meta, "grid": grid,\n'
                  '            "kernel": %s_kernel, "outputs": ("y_ptr",),\n'
                  '            "expected": ref(args, meta),\n'
                  '            "comparison": {"y_ptr": {"comparator": "array_equal",\n'
                  '                                       "exact": True}}}\n'
                  '\n'
                  '\n'
                  'def make_case(shape=None, dtype=None, seed=None):\n'
                  '    return _make_case()\n')


def check_full_const(workdir, compiler):
    """``tl.full`` at fp16/bf16 stores the rounded constant bit-exactly
    (the value is inexact in both formats, so the RTNE is observable)."""
    bad = []
    for label, out_np, outd, value in (
            ("fp16", "np.float16", "tl.float16", "0.1"),
            ("bf16", "np.float32", "tl.bfloat16", "0.1")):
        text = (_FULL_TEMPLATE % (label, label, label, label)) \
            .replace("__VALUE__", value).replace("__OUTNP__", out_np) \
            .replace("__OUTD__", outd).replace("__BLOCK__", "64")
        path = workdir / f"fc_{label}.py"
        path.write_text(text)
        module = _load(path)
        try:
            outputs, case = _run_case(compiler, module, 1)
            got = np.asarray(outputs["y_ptr"])
            if label == "bf16":
                got_bits = (got.view(np.uint32) >> 16).astype(np.uint16)
                want = np.full(64, _bf16_reference(0.1), np.uint16)
                ok = np.array_equal(got_bits, want)
            else:
                ok = np.array_equal(
                    _bits(got),
                    _bits(np.asarray(case["expected"]["y_ptr"])))
            if not ok:
                bad.append(f"{label}: bits differ")
        except PipelineError as exc:
            bad.append(f"{label}: refused {exc.construct}: "
                       f"{str(exc)[:80]}")
        except Exception as exc:  # noqa: BLE001
            bad.append(f"{label}: {type(exc).__name__}: {str(exc)[:80]}")
    check("full-const-executes", not bad, "; ".join(bad[:2]))


# ---------------------------------------------------------------------------
# the census executors (the class's own corpus operators, executed and
# compared under the case's own policy)
# ---------------------------------------------------------------------------

def _run_corpus(compiler, path, threads, **make_kwargs):
    module = _load(path)
    case = module.make_case(**make_kwargs)
    import a100_support.native_device as nd
    device = nd.NativeExecutableDevice(compiler, threads)
    staged = device.stage_case(case)
    staged.launch()
    outputs = staged.outputs()
    ok = True
    detail = ""
    for name, policy in case["comparison"].items():
        got = np.asarray(outputs[name])
        exp = np.asarray(case["expected"][name])
        if got.shape != exp.shape and got.size == exp.size:
            got = got.reshape(exp.shape)
        if policy.get("exact") or policy["comparator"] == "array_equal":
            same = np.array_equal(got, exp)
        else:
            same = np.allclose(got, exp, rtol=policy.get("rtol", 0.0),
                               atol=policy.get("atol", 0.0),
                               equal_nan=policy.get("equal_nan", False))
        if not same:
            detail = f"{name}: {int(np.sum(got != exp))} mismatched"
        ok &= same
    return ok, detail


def check_census_executors(compiler):
    """leaky_relu_kernel_strided (the negative_slope executor: a Python
    float scalar, float64 record, fp32 signature) over every declared
    dtype and the 1/2/4/8 worker configurations, on one artifact per
    identity; perf/leaky_relu (the slope executor) besides."""
    p = ROOT / "ops" / "suite" / "dev" / "leaky_relu_kernel_strided.py"
    bad = []
    for threads in (1, 2, 4, 8):
        for shape in ((64, 128), (33, 65)):
            for dtype in ("float32", "float16", "bfloat16"):
                try:
                    ok, detail = _run_corpus(compiler, p, threads,
                                             shape=shape, dtype=dtype)
                except Exception as exc:  # noqa: BLE001
                    ok, detail = False, f"{type(exc).__name__}: {str(exc)[:80]}"
                if not ok:
                    bad.append(f"t={threads} s={shape} d={dtype}: {detail}")
    check("census-executor-leaky-relu-strided", not bad, "; ".join(bad[:2]))

    p = ROOT / "ops" / "suite" / "perf" / "leaky_relu.py"
    bad = []
    for threads in (1, 4):
        try:
            ok, detail = _run_corpus(compiler, p, threads)
        except Exception as exc:  # noqa: BLE001
            ok, detail = False, f"{type(exc).__name__}: {str(exc)[:80]}"
        if not ok:
            bad.append(f"t={threads}: {detail}")
    check("census-executor-perf-leaky-relu", not bad, "; ".join(bad[:2]))


# ---------------------------------------------------------------------------
# the refusal boundary (the conversion never silently narrows an
# undeclared form)
# ---------------------------------------------------------------------------

def check_conversion_refusal_boundary():
    """The read conversion refuses located on the forms outside the
    declared surface (a bf16 scalar parameter cannot arise from the
    argument typing; widths beyond the IEEE binary set), instead of
    guessing bits."""
    from a100c.lower import scalar as scalar_mod

    class _Ctx:  # the smallest ctx float_const_bits/convert never touch
        pass

    ctx = _Ctx()
    bad = []
    for ty, width in ((tir.BFLOAT16, 64), (tir.FLOAT32, 8)):
        try:
            scalar_mod.convert_float_scalar(ctx, None, width, ty, None)
            bad.append(f"{ty!r} from width {width} did not refuse")
        except ScalarLoweringError:
            pass
    check("conversion-refusal-boundary", not bad, "; ".join(bad))


# ---------------------------------------------------------------------------

def main() -> int:
    workdir = Path(tempfile.mkdtemp(prefix="a100c-scalar-binding-"))
    compiler = Compiler(options=CompileOptions(
        cache_dir=str(workdir / "cache")))
    check_record_kind_matches_transport()
    check_readback(workdir, compiler)
    check_const_bits()
    check_masked_other(workdir, compiler)
    check_full_const(workdir, compiler)
    check_conversion_refusal_boundary()
    check_census_executors(compiler)
    if FAILURES:
        print(f"test_scalar_binding: {len(FAILURES)} check(s) FAILED: "
              f"{FAILURES}")
        return 1
    print("test_scalar_binding: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
