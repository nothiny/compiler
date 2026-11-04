"""Argument-layout binding: kernel parameters -> bundle records (F046/F047).

The bundle carries views and scalars in the sorted-argument-name order the
host packer declares (``a100_support/native_io.pack_case``); the binary
carries no names.  This module derives, from the case payload and the
specialization, the *layout* both sides share:

  - per pointer kernel parameter: its view index and pointee type;
  - per scalar kernel parameter: its scalar-record index and the record's
    (dtype, width, signedness) -- mirroring ``native_io.scalar`` exactly, so
    the emitted load reads the record the packer wrote.

The layout digest enters the artifact cache key: two cases whose *argument
layout* differs (different record kinds, different view sets) are different
artifacts even at equal specialization identity -- shapes, grid values,
buffer contents and scalar values never enter it.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from a100c.frontend.specialize import Specialization
from a100c.ir import tir

__all__ = ["ScalarBinding", "ViewBinding", "ArgumentLayout",
           "scalar_record_kind", "argument_layout"]


def scalar_record_kind(value) -> Tuple[str, int, bool]:
    """Mirror ``a100_support/native_io.scalar``: the on-disk record of a value.

    Returns (dtype-name, width-bits, signed).  Only the *kind* is used -- the
    value itself is runtime and never baked.
    """
    import numpy as np
    if isinstance(value, np.generic):
        name = np.asarray(value).dtype.name
    elif isinstance(value, bool):
        name = "bool"
    elif isinstance(value, int):
        name = "uint64" if value >= 2 ** 63 else "int64"
    elif isinstance(value, float):
        name = "float64"
    else:
        raise ValueError(
            f"unsupported runtime scalar of type {type(value).__name__}")
    import numpy as _np
    width = _np.dtype(name).itemsize * 8
    signed = name.startswith("int") or name == "bool"
    if name == "bool":
        signed = False
    return name, width, signed


@dataclass
class ViewBinding:
    name: str                 # kernel parameter name
    view_index: int           # index in the sorted view order
    pointee: tir.Type         # the pointee type the kernel computes with
    record_dtype: str         # the bundle view dtype (device dtype)


@dataclass
class ScalarBinding:
    name: str                 # kernel parameter name
    record_index: int         # index in the sorted scalar order
    record_dtype: str
    width: int                # record width in bits
    signed: bool
    tir_type: tir.Type        # the TIR scalar type


@dataclass
class ArgumentLayout:
    views: List[ViewBinding]
    scalars: List[ScalarBinding]
    #: every bundle-visible name in the sorted order (views then scalars)
    view_order: List[str]
    scalar_order: List[str]
    digest: str

    def view_of(self, name: str) -> Optional[ViewBinding]:
        for v in self.views:
            if v.name == name:
                return v
        return None

    def scalar_of(self, name: str) -> Optional[ScalarBinding]:
        for s in self.scalars:
            if s.name == name:
                return s
        return None

    def describe(self) -> dict:
        return {
            "views": [{"name": v.name, "index": v.view_index,
                       "dtype": v.record_dtype,
                       "pointee": repr(v.pointee)} for v in self.views],
            "scalars": [{"name": s.name, "index": s.record_index,
                         "dtype": s.record_dtype, "width": s.width,
                         "tir": repr(s.tir_type)} for s in self.scalars],
            "view_order": list(self.view_order),
            "scalar_order": list(self.scalar_order),
            "digest": self.digest,
        }


def argument_layout(case: dict, spec: Specialization) -> ArgumentLayout:
    """Derive the argument layout of one case payload (pack_case's order)."""
    host: Dict[str, object] = {**case.get("allocations", {}),
                               **case.get("args", {})}
    import numpy as np
    arrays = {n: v for n, v in host.items() if isinstance(v, np.ndarray)}
    view_order = sorted(arrays)
    scalar_order = sorted(n for n in host if n not in arrays)
    view_index = {n: i for i, n in enumerate(view_order)}
    scalar_index = {n: i for i, n in enumerate(scalar_order)}
    overrides = case.get("pointer_dtypes") or {}

    views: List[ViewBinding] = []
    for name, pointee in sorted(spec.pointer_types.items()):
        if name not in view_index:
            raise ValueError(
                f"pointer parameter {name!r} has no array argument in the "
                "case payload (FE-SOURCE-CONTRACT)")
        record_dtype = overrides.get(name) or str(arrays[name].dtype)
        views.append(ViewBinding(name=name, view_index=view_index[name],
                                 pointee=pointee,
                                 record_dtype=record_dtype))

    scalars: List[ScalarBinding] = []
    for name, ty in sorted(spec.scalar_types.items()):
        if name not in scalar_index:
            raise ValueError(
                f"scalar parameter {name!r} has no scalar argument in the "
                "case payload")
        value = host[name]
        dtype, width, signed = scalar_record_kind(value)
        scalars.append(ScalarBinding(name=name,
                                     record_index=scalar_index[name],
                                     record_dtype=dtype, width=width,
                                     signed=signed, tir_type=ty))

    blob = hashlib.sha256()
    for name in view_order:
        record_dtype = overrides.get(name) or str(arrays[name].dtype)
        ndim = len(arrays[name].shape)
        blob.update(f"view:{name}:{record_dtype}:{ndim}\n".encode())
    for name in scalar_order:
        dtype, width, signed = scalar_record_kind(host[name])
        blob.update(f"scalar:{name}:{dtype}:{width}:{signed}\n".encode())
    return ArgumentLayout(views=views, scalars=scalars,
                          view_order=view_order, scalar_order=scalar_order,
                          digest=blob.hexdigest()[:16])
