"""Compilation identity: the unit that decides how often a corpus compiles.

These tests pin the semantics the parallel driver and ``gate.py`` rely on:
identity must be deterministic, must ignore shape unless a constexpr makes
shape part of the code, and must honour the device (``bfloat16``) pointer
dtype rather than the ``float32`` host storage.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

HARNESS = Path(__file__).resolve().parents[1]
if str(HARNESS) not in sys.path:
    sys.path.insert(0, str(HARNESS))

from compiler_api import identity  # noqa: E402


def _case(*, m=128, n=128, k=128, dtype="float16", even=None, extra_meta=None,
          scalars=None):
    meta = {"BLOCK_M": 64, "BLOCK_N": 64, "BLOCK_K": 32}
    if even is not None:
        meta["EVEN_M"] = even
    meta.update(extra_meta or {})
    host = {"bfloat16": np.float32, "float16": np.float16, "float32": np.float32}[dtype]
    args = {
        "A_ptr": np.zeros(m * k, dtype=host),
        "B_ptr": np.zeros(k * n, dtype=host),
    }
    for name, value in (scalars or {}).items():
        args[name] = value
    case = {"args": args, "meta": meta, "kernel": _fake_kernel,
            "launch_meta": {"num_warps": 4, "num_stages": 2}}
    if dtype == "bfloat16":
        case["pointer_dtypes"] = {"A_ptr": "bfloat16", "B_ptr": "bfloat16"}
    return case


def _fake_kernel(*args, **kwargs):        # identity only needs __name__
    return None


def test_identity_is_deterministic_and_order_insensitive():
    a = _case()
    b = _case()
    assert identity.case_identity("op.py", a) == identity.case_identity("op.py", b)
    # meta insertion order must not matter
    reordered = _case()
    reordered["meta"] = dict(reversed(list(reordered["meta"].items())))
    assert identity.case_identity("op.py", a) == identity.case_identity("op.py", reordered)
    assert len(identity.case_identity("op.py", a)) == 12


def test_identity_ignores_shape_when_constexprs_do_not_derive_from_it():
    small = _case(m=64, n=64, k=64)
    large = _case(m=2048, n=2048, k=2048)
    assert identity.case_identity("op.py", small) == identity.case_identity("op.py", large)


def test_identity_separates_when_a_constexpr_follows_the_shape():
    # EVEN_M is derived from M: the compiler really emits different code
    even = _case(m=128, even=True)
    odd = _case(m=100, even=False)
    assert identity.case_identity("op.py", even) != identity.case_identity("op.py", odd)


def test_pointer_dtype_is_the_device_dtype_not_host_storage():
    f16 = _case(dtype="float16")
    bf16 = _case(dtype="bfloat16")          # stored as float32, pointer is bf16
    f32 = _case(dtype="float32")
    idents = {identity.case_identity("op.py", c) for c in (f16, bf16, f32)}
    assert len(idents) == 3


def test_int_scalars_follow_triton_specialisation():
    div16 = _case(scalars={"stride": np.int32(32)})
    other_div16 = _case(scalars={"stride": np.int32(64)})
    one = _case(scalars={"stride": np.int32(1)})
    odd = _case(scalars={"stride": np.int32(33)})
    assert identity.case_identity("op.py", div16) == \
        identity.case_identity("op.py", other_div16)
    assert identity.case_identity("op.py", one) != identity.case_identity("op.py", div16)
    assert identity.case_identity("op.py", odd) != identity.case_identity("op.py", div16)
    # ... and at the dtype-only tier even the specialisation disappears
    assert identity.case_identity("op.py", one, tier="dtype") == \
        identity.case_identity("op.py", div16, tier="dtype")


def test_launch_config_is_part_of_the_identity():
    case = _case()
    case["launch_meta"] = {"num_warps": 8, "num_stages": 2}
    assert identity.case_identity("op.py", case) != identity.case_identity("op.py", _case())


def test_source_and_kernel_separate_identities():
    assert identity.case_identity("a.py", _case()) != identity.case_identity("b.py", _case())
    other = _case()
    other["kernel"] = lambda *a, **k: None
    other["kernel"].__name__ = "other_kernel"
    assert identity.case_identity("op.py", other) != identity.case_identity("op.py", _case())


def _entry(shape, dtype="float16", *, m=None, n=None, k=None, kernel=None,
           derived=True):
    extra = {"NUM_K_BLOCKS": -(-(k or shape[2]) // 32)} if derived else {}
    api = _case(m=m or shape[0], n=n or shape[1], k=k or shape[2], dtype=dtype,
                extra_meta=extra)
    if kernel is not None:
        api["kernel"] = kernel
    return {"operator": "op.py", "shape": list(shape), "dtype": dtype,
            "kernel": "k", "case": api}


def test_census_counts_identities_not_cases():
    entries = [_entry((128, 128, 128)), _entry((64, 64, 64), "float32"),
               _entry((256, 256, 256))]
    report = identity.identity_census(entries, tiers=("meta",))
    tier = report["tiers"]["meta"]
    # NUM_K_BLOCKS is derived from K, so the three shapes are three compiles
    assert tier["cases"] == 3
    assert tier["identities"] == 3
    assert tier["ratio"] == 1.0


def test_structural_tier_drops_shape_derived_constexprs():
    entries = [_entry((128, 128, 128)), _entry((256, 256, 256)),
               _entry((512, 512, 512))]
    report = identity.identity_census(entries, tiers=("meta",))
    assert report["tiers"]["meta"]["identities"] == 3
    structural = report["tiers"]["structural"]
    # dropping NUM_K_BLOCKS must collapse the three shapes into one compile
    assert structural["identities"] == 1


def test_census_reports_operators_without_reuse():
    no_reuse = [_entry((128, 128, 128)), _entry((256, 256, 256))]
    report = identity.identity_census(no_reuse, tiers=("meta",))
    assert report["tiers"]["meta"]["no_reuse"] == ["op.py"]


def test_schedule_groups_cases_per_identity_and_orders_by_cost():
    cheap = _entry((128, 128, 128), derived=False)
    cheap["cost_hint_s"] = 0.5
    same = _entry((64, 64, 64), derived=False)        # same identity as cheap
    same["cost_hint_s"] = 0.5
    expensive = _entry((256, 256, 256), "float32", derived=False)
    expensive["cost_hint_s"] = 90.0
    schedule = identity.build_schedule([cheap, same, expensive])
    assert schedule["identities"] == 2        # fp16 identity + fp32 identity
    assert schedule["cases"] == 3
    # longest-processing-time first: the 90 s identity is the first item
    assert schedule["items"][0]["cost_hint_s"] == 90.0
    assert len(schedule["items"][1]["cases"]) == 2


def test_census_rejects_unknown_tier():
    with pytest.raises(ValueError):
        identity.signature("op.py", _case(), tier="nope")


def test_real_operator_is_usable_from_the_corpus():
    """One integration point: the harness and the census agree on a real op."""
    from opslib.runner import load_operator

    op = load_operator(str(HARNESS.parent / "suite" / "dev" / "softsign_kernel.py"))
    case = op.make_case(shape=(128,), dtype="float32", seed=30)
    ident = identity.case_identity("suite/dev/softsign_kernel.py", case)
    assert identity.case_identity("suite/dev/softsign_kernel.py", dict(case)) == ident
