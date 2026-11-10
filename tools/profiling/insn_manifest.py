#!/usr/bin/env python3
"""Join guest dynamic per-pc counts with compiler-side instruction origins.

Zero compiler changes: the artifact cache entry (``a100c/cache/<key>/``)
already carries everything the join needs --

* ``program.S``: every emitted instruction is annotated ``# [opN] <loc>``
  with its MIR op index (the emitter's default provenance, not a switch);
* ``stage.mir.allocated.txt``: the final allocated MIR in ``renumber()``
  order (op line order == op.index order), plus the ``// allocation:``
  describe line;
* ``artifact.json``: per-stage stats (frame, spill slots, registers used);
* ``operator_exec``: the linked executable (symbols ``operator_entry`` /
  ``operator_workspace_private`` / ``operator_workspace_shared`` bound the
  program region; ``a100rt_*`` symbols bound the native runtime region).

The pc map is rebuilt by re-assembling ``program.S`` with the project's own
march (``-march=rv64gcv``, a100c/runtime/build.py ASFLAGS) under
``as -alh``: the listing maps every source line (hence every [opN]) to its
section-relative address, including pseudo-instruction expansions (both
halves of an expanded ``li`` carry the same source line).  The result is
accepted only after a byte-identity check: the re-assembled ``.text`` must
equal the shipped executable's program region byte for byte, and the three
program symbols must agree on one affine offset.  A mismatch is a hard
error -- the join refuses rather than guessing.

Byte/width numbers derived here are MODEL values (scalar ld/sd = 8 B;
vector vle/vse = VLEN/8 * lmul, i.e. a full register at vlmax -- the only
form the allocator spills); they are labelled "model" in the output, never
presented as measured traffic.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

#: origin tags for MIR opcodes (the round's compiler-side attribution)
ORIGIN_OF_OPCODE = {
    "sspill": "spill", "vspill": "spill",
    "sreload": "reload", "vreload": "reload",
    "vsetvli": "vec-config",
    "sconst": "const-materialization",
    "sload": "scalar-mem", "sstore": "scalar-mem",
    "br": "branch", "brc": "branch",
    "ret": "control",
}
ORIGIN_PREFIXES = (
    ("vload", "vec-mem"), ("vstore", "vec-mem"),
    ("vbin", "vec-arith"), ("vred", "vec-arith"),
    ("vid", "vec-arith"), ("vsel", "vec-arith"),
    ("vcmp", "vec-arith"), ("vslidedn", "vec-arith"),
    ("vunary", "vec-arith"), ("vmov", "vec-arith"),
    ("vextract", "vec-arith"), ("vwaddx0", "vec-arith"),
    ("s2v", "vec-arith"),
)


def origin_of_opcode(opcode: str) -> str:
    if opcode in ORIGIN_OF_OPCODE:
        return ORIGIN_OF_OPCODE[opcode]
    for prefix, origin in ORIGIN_PREFIXES:
        if opcode.startswith(prefix):
            return origin
    return f"op:{opcode}"


_OP_COMMENT = re.compile(r"#\s*\[op(\d+)\]")
_OP_LINE = re.compile(r"^  (?:(\S+)\s*=\s*)?([a-z][\w.]*)\((.*?)\)\s*(.*)$")
_LOC_SPLIT = re.compile(r"\s*;\s*")
_LISTING_ROW = re.compile(
    r"^\s*(\d+)\s+([0-9a-fA-F]{4,8})\s+([0-9a-fA-F ]+?)\s+(\S.*)$")
_NM_ROW = re.compile(r"^([0-9a-fA-F]+)\s+(?:([0-9a-fA-F]+)\s+)?([A-Za-z])\s+(\S+)$")
_OBJDUMP_S_ROW = re.compile(r"^\s*([0-9a-fA-F]+)\s((?:[0-9a-fA-F]{2,8}\s*)+)$")


def _sh(cmd, timeout=120):
    result = subprocess.run([str(c) for c in cmd], capture_output=True,
                            text=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError(f"command failed ({result.returncode}): "
                           f"{' '.join(str(c) for c in cmd)}\n"
                           f"{result.stdout}\n{result.stderr}")
    return result.stdout


def parse_program_s(text: str):
    """One record per program.S line: kind, text, [opN] if any."""
    records = []
    for lineno, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        op_match = _OP_COMMENT.search(raw)
        op_index = int(op_match.group(1)) if op_match else None
        if not stripped or stripped.startswith("#"):
            kind = "comment"
        elif re.match(r"^[\w.$]+:", stripped):
            # a label (incl. the emitter's .L{block} forms, which start
            # with a dot) is checked before directives
            kind = "label"
        elif stripped.startswith("."):
            kind = "directive"
        else:
            # the emitter's op lines carry no leading indentation (only
            # render()'s workspace/directive lines are indented), so
            # anything that is not comment/directive/label is an emitted
            # instruction
            kind = "instr"
        mnemonic = stripped.split()[0] if kind == "instr" else ""
        records.append({"line": lineno, "kind": kind, "text": raw,
                        "op_index": op_index, "mnemonic": mnemonic})
    return records


def parse_mir_dump(text: str):
    """Ordered op records (index == position among op lines) + allocation."""
    ops = []
    allocation = None
    for raw in text.splitlines():
        if raw.startswith("// allocation:"):
            allocation = json.loads(raw.split(":", 1)[1].strip()
                                    .replace("'", '"'))
            continue
        match = _OP_LINE.match(raw)
        if not match:
            continue
        opcode = match.group(2)
        attrs = {}
        tail = _LOC_SPLIT.split(match.group(4))[0].strip()
        for token in tail.split():
            if "=" in token:
                key, _, value = token.partition("=")
                attrs[key] = value
        loc = match.group(4).split(";", 1)[1].strip() \
            if ";" in match.group(4) else None
        ops.append({"opcode": opcode, "attrs": attrs, "loc": loc})
    return ops, allocation


def parse_listing(listing_text: str):
    """(source line, section-relative address) for each instruction start.

    Continuation rows (same line, more bytes, no address column) carry no
    source text and are filtered by the trailing-source requirement.
    """
    rows = []
    for raw in listing_text.splitlines():
        match = _LISTING_ROW.match(raw)
        if match:
            rows.append((int(match.group(1)), int(match.group(2), 16)))
    return rows


def symbol_table(binary: Path):
    """name -> (addr, size|None) from nm -S (defined symbols only)."""
    out = _sh(["nm", "-S", "--defined-only", str(binary)])
    table = {}
    for raw in out.splitlines():
        match = _NM_ROW.match(raw.strip())
        if match:
            addr = int(match.group(1), 16)
            size = int(match.group(2), 16) if match.group(2) else None
            table[match.group(4)] = (addr, size)
    return table


def _section_bytes(binary: Path, section: str):
    """addr -> bytes for one section, from objdump -s -j <section>."""
    out = _sh(["objdump", "-s", "-j", section, str(binary)])
    blob = {}
    for raw in out.splitlines():
        match = _OBJDUMP_S_ROW.match(raw)
        if match:
            addr = int(match.group(1), 16)
            hexbytes = re.findall(r"[0-9a-fA-F]{2}", match.group(2))
            blob[addr] = bytes(int(h, 16) for h in hexbytes)
    return blob


def _flat(section_blob: dict):
    if not section_blob:
        return b"", 0
    base = min(section_blob)
    end = max(a + len(b) for a, b in section_blob.items())
    data = bytearray(end - base)
    for addr, chunk in section_blob.items():
        data[addr - base:addr - base + len(chunk)] = chunk
    return bytes(data), base


def _cross_prefix() -> str:
    prefix = os.environ.get("A100_CROSS_PREFIX")
    if not prefix:
        for line in (ROOT / ".env").read_text().splitlines():
            if line.startswith("A100_CROSS_PREFIX="):
                prefix = line.split("=", 1)[1].strip()
    if not prefix:
        raise RuntimeError("A100_CROSS_PREFIX not set (source .env)")
    return prefix


PROGRAM_SYMBOLS = ("operator_workspace_private", "operator_workspace_shared",
                   "operator_entry")


class Manifest:
    """Compiler-side instruction manifest for one artifact cache entry."""

    def __init__(self, entry: Path):
        self.entry = entry
        self.program_lines = parse_program_s(
            (entry / "program.S").read_text())
        self.mir_ops, self.allocation = parse_mir_dump(
            (entry / "stage.mir.allocated.txt").read_text())
        meta = json.loads((entry / "artifact.json").read_text())
        self.stats = meta.get("stages", {})
        self.identity = meta.get("identity")
        self.key = meta.get("key")

    def opcode_of(self, op_index):
        if op_index is None or op_index >= len(self.mir_ops):
            return None
        return self.mir_ops[op_index]["opcode"]

    def attrs_of(self, op_index):
        if op_index is None or op_index >= len(self.mir_ops):
            return {}
        return self.mir_ops[op_index].get("attrs") or {}

    def loc_of(self, op_index):
        if op_index is None or op_index >= len(self.mir_ops):
            return None
        return self.mir_ops[op_index].get("loc")

    def build_pc_map(self, executable: Path, workdir: Path):
        """pc -> record for every program instruction; verified by bytes.

        Returns (pc_map, program_region, diagnostics).  program_region is
        (start, end) in executable addresses; pcs outside it belong to the
        runtime/loader and are attributed by symbol elsewhere.
        """
        workdir.mkdir(parents=True, exist_ok=True)
        prefix = _cross_prefix()
        obj = workdir / "program.o"
        listing = _sh([f"{prefix}as", "-march=rv64gcv", "-alh",
                       "-o", str(obj), str(self.entry / "program.S")])
        lrows = parse_listing(listing)
        obj_syms = symbol_table(obj)
        exe_syms = symbol_table(executable)
        missing = [s for s in PROGRAM_SYMBOLS
                   if s not in obj_syms or s not in exe_syms]
        if missing:
            raise RuntimeError(f"program symbols missing: {missing}")
        offsets = {exe_syms[s][0] - obj_syms[s][0] for s in PROGRAM_SYMBOLS}
        if len(offsets) != 1:
            raise RuntimeError(f"program symbols disagree on the affine "
                               f"offset: {sorted(offsets)}")
        offset = offsets.pop()

        # byte identity: the re-assembled .text must equal the shipped
        # executable's program region byte for byte (same march as the
        # project's own ASFLAGS); otherwise the join refuses
        o_bytes, _ = _flat(_section_bytes(obj, ".text"))
        e_bytes, e_base = _flat(_section_bytes(executable, ".text"))
        region_start = exe_syms["operator_workspace_private"][0]
        entry_addr, entry_size = exe_syms["operator_entry"]
        region_end = entry_addr + (entry_size or 0)
        lo = region_start - e_base
        hi = region_end - e_base
        if e_bytes[lo:hi] != o_bytes:
            raise RuntimeError("byte-identity check failed: the re-assembled "
                               "program.S .text differs from the shipped "
                               "executable's program region")

        by_line = {rec["line"]: rec for rec in self.program_lines}
        pc_map = {}
        vtype = None  # (sew, lmul) of the last vsetvli op in program order
        for src_line, addr in lrows:
            record = by_line.get(src_line)
            if record is None or record["kind"] != "instr":
                continue
            op_index = record["op_index"]
            opcode = self.opcode_of(op_index)
            if opcode == "vsetvli":
                attrs = self.attrs_of(op_index)
                try:
                    vtype = (int(attrs.get("sew", "0")),
                             int(str(attrs.get("lmul", "1")).split(",")[0]))
                except ValueError:
                    vtype = None
            origin = ("frame" if opcode is None
                      else origin_of_opcode(opcode))
            pc_map[addr + offset] = {
                "line": src_line, "op_index": op_index, "opcode": opcode,
                "origin": origin, "mnemonic": record["mnemonic"],
                "text": record["text"].strip(),
                "loc": self.loc_of(op_index), "vtype": vtype,
            }
        diagnostics = {
            "listing_instruction_rows": len(lrows),
            "program_instructions": len(pc_map),
            "affine_offset": offset,
            "region": [region_start, region_end],
            "byte_identity": True,
        }
        return pc_map, (region_start, region_end), diagnostics

    @staticmethod
    def symbol_regions(executable: Path):
        """Ordered (start, end, name) intervals for runtime attribution."""
        table = symbol_table(executable)
        items = sorted((addr, size or 0, name)
                       for name, (addr, size) in table.items())
        regions = []
        for i, (addr, size, name) in enumerate(items):
            end = addr + size if size else (
                items[i + 1][0] if i + 1 < len(items) else addr)
            if end > addr:
                regions.append((addr, end, name))
        return regions

    @staticmethod
    def region_of(pc, regions):
        for start, end, name in regions:
            if start <= pc < end:
                return name
        return None

    @staticmethod
    def instruction_bytes(mnemonic: str, vtype, scalar_default=8):
        """MODEL width in bytes for one instruction (never a measurement).

        scalar ld/sd-family: 8 B.  vector vle/vse: VLEN/8 * lmul (a full
        register at vlmax -- the only form the allocator spills; ordinary
        traffic with runtime vl is not modelled and returns None).
        """
        m = mnemonic.split(".")[0]
        if m.startswith("c."):
            m = m[2:]
        if m in ("ld", "sd", "fld", "fsd", "ldsp", "sdsp", "fldsp", "fsdsp"):
            return 8
        if m in ("lw", "sw", "flw", "fsw", "lwsp", "swsp"):
            return 4
        if m in ("lh", "sh", "lhu") or m in ("lb", "sb", "lbu"):
            return 2 if m[0] == "l" and m != "lb" and m != "lbu" else 1
        if m.startswith("vle") or m.startswith("vse") or \
                m.startswith("vl") and m[2:3] in "e1" or \
                m.startswith("vs") and m[2:3] in "e1":
            if vtype and vtype[1] >= 1:
                return 128 * vtype[1]
            return 128
        return None
