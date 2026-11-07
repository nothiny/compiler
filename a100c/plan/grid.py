"""Compatibility shim: the grid model lives in the frontend
(``a100c/frontend/gridmodel.py``, COMPILER_ARCHITECTURE.md section 3 "Grid
model" and the ARCHITECTURE_CONSTRAINTS module table).  This module keeps
the import surface the vertical slice (T007) wired up -- ``extract_grid``,
``GridError``, ``GridModel``, the expression nodes -- forwarding to the
general multi-axis model.
"""
from __future__ import annotations

from a100c.frontend.gridmodel import (  # noqa: F401
    Bin, GridError, GridExpr, GridModel, Ind, Lit, Ref, SumLoop, census,
    evaluate_expr, extract_grid, grid_of_case, linear_pid_root,
    apply_linear_flattening)

__all__ = ["GridError", "GridExpr", "Lit", "Ref", "Bin", "GridModel",
           "Ind", "SumLoop", "extract_grid", "evaluate_expr", "census",
           "grid_of_case", "linear_pid_root", "apply_linear_flattening"]
