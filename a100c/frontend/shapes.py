"""Rank/extent inference with broadcast extents distinguished from real
extents (FE-SHAPE-AND-BROADCAST).

Shapes align from the right (the pinned Triton 3.8 ``broadcast_impl_value``
prepends singleton axes to the lower-rank operand); an axis expands only
from extent 1; any other disagreement is a *diagnostic*, never a silent
stretch.
"""
from __future__ import annotations

from typing import Optional, Sequence, Tuple

from a100c.ir.tir import Extent, ExtentLike, Shape, Sym, unify_shapes

__all__ = ["ShapeError", "align_rank", "broadcast_to", "unify_pair",
           "same_values"]


class ShapeError(Exception):
    """A shape disagreement the declared rules do not permit."""

    def __init__(self, message: str, loc=None):
        super().__init__(message + (f" (at {loc})" if loc else ""))
        self.message = message
        self.loc = loc


def same_values(a: Shape, b: Shape) -> bool:
    return tuple(e.value for e in a) == tuple(e.value for e in b)


def align_rank(shape: Shape, rank: int) -> Shape:
    """Right-align: prepend singleton axes (the pinned expand_dims-at-0)."""
    if len(shape) >= rank:
        return shape
    return (Extent(1, True),) * (rank - len(shape)) + shape


def broadcast_to(shape: Shape, target: Shape, loc=None) -> Shape:
    """Broadcast ``shape`` to ``target`` (numpy-style per the pinned rules).

    Returns the result shape: an axis is flagged broadcast when the source
    axis was a singleton (or padded) expanded to a larger extent.  Raises
    ShapeError when the extents disagree.
    """
    src = align_rank(shape, len(target))
    out: list = []
    for i, (s, d) in enumerate(zip(src, target)):
        if s.value == d.value:
            if s.is_one() and s.broadcast:
                # a padded/replicated singleton axis stays broadcast even
                # at an equal (extent-1) target: its lanes replicate from
                # the source lane, they are not distinct storage
                out.append(Extent(d.value, True))
            else:
                out.append(Extent(d.value, s.broadcast and d.broadcast))
        elif s.is_one():
            out.append(Extent(d.value, True))
        elif d.is_one():
            out.append(Extent(s.value, s.broadcast))
        else:
            raise ShapeError(
                f"cannot broadcast: extent {s.value} at axis {i} does not "
                f"match the target extent {d.value} and is not 1",
                loc=loc)
    return tuple(out)


def unify_pair(a: Shape, b: Shape, loc=None) -> Tuple[Shape, Shape, Shape]:
    """Unify two operand shapes (pinned broadcast_impl_value).

    Returns ``(target, a_expanded, b_expanded)``: the target extent values
    and each operand's shape after explicit expansion (expanded axes flagged
    broadcast).  A disagreement the rules do not permit raises ShapeError.
    """
    target = unify_shapes(a, b)
    if target is None:
        rank = max(len(a), len(b))
        ra, rb = align_rank(a, rank), align_rank(b, rank)
        bad = [i for i, (x, y) in enumerate(zip(ra, rb))
               if x.value != y.value and not x.is_one() and not y.is_one()]
        raise ShapeError(
            f"cannot unify shapes {list(a)} and {list(b)}: incompatible "
            f"extent(s) at axis/axes {bad}", loc=loc)
    return target, broadcast_to(a, target, loc), broadcast_to(b, target, loc)
