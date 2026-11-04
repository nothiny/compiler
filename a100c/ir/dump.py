"""Textual dump of a TIR module with source attribution (IR-OBSERVABILITY).

Every op prints with the source location of the construct that produced it,
so a wrong result can be attributed to its source position by comparing the
dump against expectation, never by guessing from the final symptom.
"""
from __future__ import annotations

from typing import Optional

from a100c.ir import tir

__all__ = ["dump_module", "dump_function", "dump_op"]


def _ext(e: tir.Extent) -> str:
    return f"{e.value}{'b' if e.broadcast else ''}"


def _shape(shape: tir.Shape) -> str:
    return "[" + ", ".join(_ext(e) for e in shape) + "]"


def _type(t: tir.Type) -> str:
    return repr(t)


def _value(v: tir.Value) -> str:
    return f"{v.name}:{_type(v.type)}{_shape(v.shape)}"


def _operands(op: tir.Op) -> str:
    return ", ".join(o.name for o in op.operands)


def _loc(loc: Optional[tir.SrcLoc]) -> str:
    return f"  ; {loc}" if loc is not None else ""


def dump_op(op: tir.Op, indent: str = "  ") -> str:
    attrs = op.attrs
    parts = []
    if op.results:
        results = ", ".join(_value(r) for r in op.results)
        parts.append(f"{results} =")
    name = op.op
    detail = ""
    if name == "const":
        detail = f" {attrs.get('value')!r}"
    elif name == "program_id":
        detail = f" axis={attrs.get('axis')}"
    elif name == "arange":
        detail = f" start={attrs.get('start')}, end={attrs.get('end')}"
    elif name == "full":
        detail = f" value={attrs.get('value')!r}"
    elif name in ("convert", "bitcast"):
        detail = f" -> {_type(op.results[0].type)}"
    elif name == "broadcast":
        src = attrs.get("from_shape")
        detail = (f" to{_shape(op.results[0].shape)}"
                  f" from[{', '.join(_ext(e) for e in src)}]")
    elif name == "load":
        if "masked_default" in attrs:
            detail = f" default={attrs['masked_default']}"
        else:
            detail = " unmasked"
    elif name == "store":
        if "masked_default" in attrs:
            detail = f" default={attrs['masked_default']}"
        else:
            detail = " unmasked"
    head = f"{indent}{parts[0] + ' ' if parts else ''}{name}{detail}" \
           f"({_operands(op)})"
    return head + _loc(op.loc)


def dump_block(block: tir.Block, out: list, indent: str = "  ") -> None:
    for stmt in block.statements:
        if isinstance(stmt, tir.If):
            out.append(f"{indent}if {stmt.cond.name}:{_loc(stmt.loc)}")
            dump_block(stmt.then, out, indent + "  ")
            out.append(f"{indent}else")
            dump_block(stmt.els, out, indent + "  ")
            if stmt.join_names:
                joined = ", ".join(
                    f"{n} -> {_value(v)}"
                    for n, v in zip(stmt.join_names, stmt.join_results))
                out.append(f"{indent}join {joined}")
        elif isinstance(stmt, tir.Loop):
            bounds = ", ".join(b.name for b in
                               (stmt.lower, stmt.upper, stmt.step)
                               if b is not None)
            carried = ", ".join(f"{n}={v.name}" for n, v in stmt.carried)
            out.append(f"{indent}loop ({bounds}) carried({carried})"
                       f"{_loc(stmt.loc)}")
            dump_block(stmt.body, out, indent + "  ")
        else:
            out.append(dump_op(stmt, indent))


def dump_function(fn: tir.Function) -> str:
    out: list = []
    params = ", ".join(_value(p) for p in fn.params)
    out.append(f"fn {fn.name}({params}){'  ; ' + str(fn.loc) if fn.loc else ''}")
    out.append("{")
    dump_block(fn.body, out)
    out.append("}")
    return "\n".join(out)


def dump_module(module: tir.Module) -> str:
    """Dump a whole module; the header carries the source path."""
    out = [f"// tir/v1 module {module.name} source={module.source_path}"]
    for fn in module.functions:
        out.append(dump_function(fn))
    return "\n".join(out) + "\n"
