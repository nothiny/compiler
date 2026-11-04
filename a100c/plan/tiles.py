"""Dot tiling plan: the IME tile families as data (COMPILER_ARCHITECTURE.md 5,
"dot tiling plan"; module responsibility per ARCHITECTURE_CONSTRAINTS.json).

The plan is the *form* of one ``tl.dot`` lowering; every runtime quantity (M,
N, K extents, strides) stays runtime -- it is read from the bundle views by
the emitted program, never baked.  The plan decides, as data:

  * the IME family that serves the operand dtypes (F030: A100 LMUL=1 tiles
    INT8 8x16x8 -> INT32, FP16 8x8x8 -> FP32; F037: the corpus dtype surface
    binds the applicable families to INT8 and FP16/BF16);
  * the mnemonic signedness variant from the operand signedness (F031: the
    accumulator is always signed; none/u/us/su select A/B interpretation);
  * the operand slot mapping: vs1 = the A tile row-major, vs2 = the B tile
    column-major -- the geometric layout statement of C <- C + A x B^T, which
    needs no software transpose when the memory layout already provides
    columns (F031);
  * the staging tiles: compiler-written, zero-padded on the M/N/K tails (the
    compiler never reads out-of-range memory to construct a nominally neutral
    term), materialised in the worker-private workspace;
  * the vector-FP32 path for BF16 operands (F010/F034: the pinned emulator's
    BF16 IME format selection has not passed; BF16 IME execution is not
    claimable and is never inferred from FP16 success).

Negative decisions are data too: int4/sparse/scale families, fp8, mixed
operand dtypes and out_dtype narrowing are refused with located diagnostics
(MECH-DIAGNOSTIC-REFUSAL), never approximated by a nearby family.

Pure models (``tile_grid``, ``k_steps``, ``expected_tile_ops``) are the
independent prediction the tests verify the emitted program against.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

__all__ = [
    "ImeFamily", "FAMILIES", "REFUSED_DOT_FORMS", "DotDescription",
    "DotPlan", "plan_dot", "tile_grid", "k_steps", "expected_tile_ops",
    "BF16_IME_GAP", "TilePlanError",
]


class TilePlanError(Exception):
    """A located refusal from the tile planner (never a silent guess)."""

    def __init__(self, construct: str, message: str):
        super().__init__(f"tile plan: {construct}: {message}")
        self.construct = construct
        self.message = message


#: The recorded BF16 IME gap (F010/F034): the statement every BF16 dot plan
#: carries so the gap is recorded wherever the plan is described.
BF16_IME_GAP = (
    "the pinned QEMU emulator's BF16 IME format selection has not passed "
    "(F010: the bf16 matrix probe fails while its executed smt.vfwmadot "
    "selects the MCPM float16 format; F034); BF16 IME execution is not "
    "claimable and FP16 or vector success never proves it -- BF16 dot lowers "
    "to the vector FP32 path (BF16->FP32 conversion is exact) and the gap is "
    "recorded separately"
)


@dataclass(frozen=True)
class ImeFamily:
    """One A100 IME tile family (F030, LMUL=1 tiles, data not branches)."""

    key: str                    # "i8" | "fp16"
    tile_m: int                 # 8
    tile_n: int                 # 8
    tile_k: int                 # 16 (i8) | 8 (fp16)
    in_width: int               # operand element bits (8 | 16)
    in_kind: str                # "int" (int/uint by signedness) | "float"
    acc_sew: int                # 32 (F030: SEW=32 for both families)
    acc_kind: str               # "int" | "float"
    mul_c: int                  # 2 (F030/F040: vd/vd+1 the group)
    lambda_: int                # 4 (F030)
    widening: int               # W = 4 (i8) | 2 (fp16)
    #: signedness (a_signed, b_signed) -> mnemonic suffix (F031/F029 4.2)
    suffixes: Tuple[Tuple[Tuple[bool, bool], str], ...] = ()
    mnemonic_base: str = ""     # "smt.vmadot" | "smt.vfwmadot"
    assembly_suffix: str = ""   # ", i8" for the integer family
    evidence: Tuple[str, ...] = ()

    def suffix_for(self, a_signed: bool, b_signed: bool) -> str:
        for (a_s, b_s), suffix in self.suffixes:
            if a_s == a_signed and b_s == b_signed:
                return suffix
        raise TilePlanError(
            f"family {self.key}",
            f"no signedness variant for a_signed={a_signed}, "
            f"b_signed={b_signed}")

    def mnemonic_for(self, a_signed: bool, b_signed: bool) -> str:
        return f"{self.mnemonic_base}{self.suffix_for(a_signed, b_signed)}"

    def describe(self) -> dict:
        return {
            "key": self.key, "tile": [self.tile_m, self.tile_n, self.tile_k],
            "in_width": self.in_width, "in_kind": self.in_kind,
            "acc_sew": self.acc_sew, "acc_kind": self.acc_kind,
            "mul_c": self.mul_c, "lambda": self.lambda_,
            "widening": self.widening,
            "mnemonic_base": self.mnemonic_base,
            "suffixes": {f"a{'s' if a else 'u'}_b{'s' if b else 'u'}": sfx
                         for (a, b), sfx in self.suffixes},
            "evidence": list(self.evidence),
        }


#: The applicable families on the input path (F037: the corpus dtype surface
#: is bfloat16/bool/float16/float32/int16/int32/int64/int8 -- no int4/fp8).
FAMILIES: Dict[str, ImeFamily] = {
    "i8": ImeFamily(
        key="i8", tile_m=8, tile_n=8, tile_k=16,
        in_width=8, in_kind="int", acc_sew=32, acc_kind="int",
        mul_c=2, lambda_=4, widening=4,
        suffixes=(
            ((True, True), ""),          # smt.vmadot   s x s -> i32
            ((False, False), "u"),        # smt.vmadotu  u x u -> i32
            ((False, True), "us"),        # smt.vmadotus u x s -> i32
            ((True, False), "su"),        # smt.vmadotsu s x u -> i32
        ),
        mnemonic_base="smt.vmadot", assembly_suffix=", i8",
        evidence=("F030", "F031", "F033", "F037", "F040", "F051"),
    ),
    "fp16": ImeFamily(
        key="fp16", tile_m=8, tile_n=8, tile_k=8,
        in_width=16, in_kind="float", acc_sew=32, acc_kind="float",
        mul_c=2, lambda_=4, widening=2,
        suffixes=(((True, True), ""),),   # smt.vfwmadot fp16 x fp16 -> fp32
        mnemonic_base="smt.vfwmadot", assembly_suffix="",
        evidence=("F030", "F031", "F033", "F034", "F040", "F051"),
    ),
}

#: Declared refusals of the dot lane (data: construct -> reason).  Each is a
#: located diagnostic at plan time, never a nearest-family approximation.
REFUSED_DOT_FORMS: Dict[str, str] = {
    "int4": ("int4 source-level dot is outside the declared surface "
             "(SUBSET.md 6 exclusion; F037: no corpus dtype exercises the "
             "int4 families)"),
    "sparse": ("4:2 structured-sparse dot forms (smt.vmadot.sp*) are not "
               "exercised by corpus dtypes (F037) and are refused"),
    "scale": ("block-scaled dot forms (smt.vmadot.hp*) are not exercised by "
              "corpus dtypes (F037) and are refused"),
    "fp8": ("fp8 is excluded by the declared subset (SUBSET.md 6); no IME "
            "family serves it"),
    "mixed-dtypes": ("tl.dot operands of different dtypes have no IME family "
                     "(F032: mixed FP16/BF16 inputs are not defined; mixed "
                     "widths are outside tl.dot's contract)"),
    "fp32-ieee": ("fp32 IEEE tl.dot is exact and takes the vector FP32 path "
                  "of the matrix-breadth lane (T014); the IME slice "
                  "implements int8/fp16 IME and the bf16 vector path"),
    "integer-non-i8": ("int16/int32/int64 dot operands have no IME family "
                       "(F030) and their vector path is matrix breadth "
                       "(T014)"),
    "out-dtype-narrow": ("out_dtype narrower than the accumulator (fp16/bf16 "
                         "results of a dot) is the matrix-breadth lane "
                         "(T014); the slice stores the accumulator width"),
    "bf16-vector-strides": ("the BF16 vector-FP32 path of the slice requires "
                            "unit-stride B rows and C rows (the corpus "
                            "output form); general strides arrive with "
                            "matrix breadth (T014)"),
}


@dataclass(frozen=True)
class DotDescription:
    """The input-side contract of one dot kernel (the slice's kernel form).

    ``a_view``/``b_view``/``c_view`` name the bundle views (sorted-argument
    order gives their indices); shapes and strides are runtime view data.
    ``acc_mode``: ``zero`` (C = A x B) or ``read_c`` (C = C_in + A x B, the
    accumulator-chaining form of tl.dot's ``acc`` parameter).
    """

    a_dtype: str                # "int8" | "uint8" | "float16" | "bfloat16" | ...
    b_dtype: str
    out_dtype: str              # the C view's element dtype
    acc_mode: str = "zero"      # "zero" | "read_c"
    a_view: str = "a_ptr"
    b_view: str = "b_ptr"
    c_view: str = "c_ptr"
    source: str = "ime-slice"   # attribution carried onto every MIR op

    def validate(self) -> None:
        if self.acc_mode not in ("zero", "read_c"):
            raise TilePlanError("acc", f"acc_mode {self.acc_mode!r} is not "
                                       "declared (zero | read_c)")


@dataclass(frozen=True)
class DotPlan:
    """The tiling plan one dot lowers under (COMPILER_ARCHITECTURE.md 5)."""

    family: Optional[ImeFamily]         # None on the vector path
    path: str                           # "ime" | "vector-fp32"
    a_signed: bool = True
    b_signed: bool = True
    acc_mode: str = "zero"
    #: staging tile byte offsets in the worker-private workspace
    a_stage_off: int = 0
    b_stage_off: int = 0
    c_stage_off: int = 0
    conv_stage_off: int = 0             # bf16->fp32 conversion staging
    workspace_private: int = 0
    #: the vector path's output chunk (lanes per fp32 pass)
    vector_chunk: int = 16
    bf16_gap: Optional[str] = None
    source: str = "ime-slice"
    #: the operand slot mapping (F031) -- recorded, not re-derived
    slot_map: Dict[str, str] = field(default_factory=dict)

    @property
    def k_step(self) -> int:
        return self.family.tile_k if self.family else 8

    @property
    def mnemonic(self) -> str:
        """The tile instruction this plan emits (the signedness variant)."""
        if self.family is None:
            return ""
        return self.family.mnemonic_for(self.a_signed, self.b_signed)

    def describe(self) -> dict:
        out = {
            "path": self.path,
            "acc_mode": self.acc_mode,
            "workspace_private": self.workspace_private,
            "source": self.source,
            "slot_map": dict(self.slot_map),
        }
        if self.family is not None:
            out["family"] = self.family.describe()
            out["mnemonic"] = self.mnemonic
        if self.bf16_gap:
            out["bf16_gap"] = self.bf16_gap
        return out


#: dtype name -> (family key, signed) for the integer/float input surface
_DTYPE_TABLE: Dict[str, Tuple[Optional[str], bool]] = {
    "int8": ("i8", True), "uint8": ("i8", False),
    "float16": ("fp16", True),
    "bfloat16": (None, True),          # vector-FP32 path (the emulator gap)
}


def _refuse(form: str, detail: str = "") -> None:
    reason = REFUSED_DOT_FORMS.get(form, form)
    raise TilePlanError(form, f"{reason}{(' | ' + detail) if detail else ''}")


def plan_dot(desc: DotDescription) -> DotPlan:
    """Plan one dot: family selection, slot mapping, staging layout.

    Refusals are located (TilePlanError carries the construct); the plan
    itself is data the lowering consumes.
    """
    desc.validate()
    a = _DTYPE_TABLE.get(desc.a_dtype)
    b = _DTYPE_TABLE.get(desc.b_dtype)
    if a is None or b is None:
        dtype = desc.a_dtype if a is None else desc.b_dtype
        if dtype == "int4":
            _refuse("int4", dtype)
        elif "float8" in dtype:
            _refuse("fp8", dtype)
        elif dtype in ("int16", "int32", "int64", "uint16", "uint32",
                       "uint64"):
            _refuse("integer-non-i8", dtype)
        elif dtype == "float32":
            _refuse("fp32-ieee", "operand dtype float32")
        else:
            raise TilePlanError(
                dtype, f"dtype {dtype!r} is not a declared dot operand")
    fam_key, a_signed = a
    _, b_signed = b
    # mixed operand dtypes: int8/uint8 combine freely (the u/us/su signedness
    # variants, F031); fp16/bf16 do not (F032: mixed 16-bit float input
    # formats within one instruction are not defined)
    compatible = ((fam_key is not None and fam_key == b[0])
                  or (fam_key is None and b[0] is None
                      and desc.a_dtype == desc.b_dtype))
    if not compatible or (fam_key == "fp16" and
                          desc.a_dtype != desc.b_dtype):
        _refuse("mixed-dtypes", f"{desc.a_dtype} x {desc.b_dtype}")

    source = desc.source

    if fam_key == "i8":
        family = FAMILIES["i8"]
        if desc.out_dtype != "int32":
            _refuse("out-dtype-narrow",
                    f"int8 dot accumulates i32 (F051); out {desc.out_dtype}")
        return DotPlan(
            family=family, path="ime", a_signed=a_signed, b_signed=b_signed,
            acc_mode=desc.acc_mode,
            a_stage_off=0, b_stage_off=128, c_stage_off=256,
            workspace_private=512, source=source,
            slot_map={"vs1": "A tile, row-major (8x16 bytes)",
                      "vs2": "B tile, column-major (8 columns x 16 bytes)",
                      "vd": "C tile accumulator (MUL_C=2 group, i32)"},
        )

    if fam_key == "fp16":
        family = FAMILIES["fp16"]
        if desc.out_dtype != "float32":
            _refuse("out-dtype-narrow",
                    f"fp16 dot accumulates f32 (F051); out {desc.out_dtype}")
        return DotPlan(
            family=family, path="ime", a_signed=True, b_signed=True,
            acc_mode=desc.acc_mode,
            a_stage_off=0, b_stage_off=128, c_stage_off=256,
            workspace_private=512, source=source,
            slot_map={"vs1": "A tile, row-major (8x8 halfwords)",
                      "vs2": "B tile, column-major (8 columns x 8 halfwords)",
                      "vd": "C tile accumulator (MUL_C=2 group, f32)"},
        )

    # bfloat16: the vector FP32 path with the recorded emulator gap
    if desc.out_dtype != "float32":
        _refuse("out-dtype-narrow",
                f"bf16 dot accumulates f32; out {desc.out_dtype}")
    return DotPlan(
        family=None, path="vector-fp32", a_signed=True, b_signed=True,
        acc_mode=desc.acc_mode,
        conv_stage_off=0, workspace_private=64,
        vector_chunk=16, bf16_gap=BF16_IME_GAP, source=source,
        slot_map={"path": "ordinary RVV FMA at e32 (no IME instruction)"},
    )


# ---------------------------------------------------------------------------
# Pure models (the independent prediction the tests verify against)
# ---------------------------------------------------------------------------


def tile_grid(m: int, n: int, tile_m: int = 8, tile_n: int = 8
              ) -> Tuple[int, int]:
    """Output tile counts (runtime quantities; the pure model of the loop)."""
    return ((m + tile_m - 1) // tile_m, (n + tile_n - 1) // tile_n)


def k_steps(k: int, k_step: int) -> int:
    """K steps of one output tile (full and tail steps alike)."""
    return (k + k_step - 1) // k_step


def expected_tile_ops(m: int, n: int, k: int, plan: DotPlan) -> int:
    """The dynamic count of tile instructions one execution performs.

    The instruction-count plugin's expected value: output tiles x K steps
    (every step -- full or tail -- executes exactly one tile instruction).
    The vector path performs none.
    """
    if plan.path != "ime":
        return 0
    mt, nt = tile_grid(m, n, plan.family.tile_m, plan.family.tile_n)
    return mt * nt * k_steps(k, plan.k_step)
