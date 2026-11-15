#!/usr/bin/env python3
"""branch_census.py -- the OPT-BRANCH-FUSE round's accept/decline observatory.

For one (operator, shape, dtype) case this tool compiles through the normal
factory path (caching applies) and reports, from the artifact's own stats and
emitted program:

* ``brc_sites``       conditional branches to a ``.LbrcN_true`` stub form
* ``stub_bare``       stubs containing exactly one ``j`` (eliminable)
* ``stub_with_moves`` stubs carrying argument moves (always declined)
* ``peephole_branch`` the emitter's fired/declined counters (stubs_removed,
                      stubs_declined, cmp_fused, cmp_declined)
* ``forms``           the emitted conditional-branch mnemonic histogram

With ``--off`` the compile runs ``A100C_BRANCH_FUSE=off`` (the control side:
the counters are empty and the stub/bne forms are the pre-round emission).

Usage:
  python3 tools/profiling/branch_census.py --operator suite/perf/matmul.py \
      --shape 16,16,16 --dtype float16 [--off] [--out report.json]
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

_CONDBR_RE = re.compile(r'^\s{4}(bne|beq|blt|bge|bltu|bgeu)\s+(\w+)\s*,\s*'
                        r'(\w+)\s*,\s*(\S+)')
_LABEL_RE = re.compile(r'^(\S+):')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--operator", required=True)
    ap.add_argument("--shape", required=True)
    ap.add_argument("--dtype", required=True)
    ap.add_argument("--off", action="store_true",
                    help="compile with A100C_BRANCH_FUSE=off (control)")
    ap.add_argument("--seed", type=int, default=30)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    if args.off:
        os.environ["A100C_BRANCH_FUSE"] = "off"

    sys.path.insert(0, str(ROOT))
    sys.path.insert(0, str(ROOT / "ops/harness"))
    from a100c.factory import make_compiler   # noqa: E402

    op_path = args.operator
    for prefix in (ROOT, ROOT / "ops"):
        cand = prefix / op_path
        if cand.exists():
            op_path = cand
            break
    spec = importlib.util.spec_from_file_location("op", str(op_path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    shape = tuple(int(x) for x in args.shape.split(","))
    case = module.make_case(shape=shape, dtype=args.dtype, seed=args.seed)

    art = make_compiler().compile_case(case)
    entry = Path(art.executable).parent
    text = (entry / "program.S").read_text()
    artifact = json.load(open(entry / "artifact.json"))

    lines = text.splitlines()
    codes = [l.split("#", 1)[0].strip() for l in lines]
    label_at = {}
    for i, c in enumerate(codes):
        m = _LABEL_RE.match(c)
        if m:
            label_at[m.group(1)] = i

    brc_sites = 0
    stub_bare = 0
    stub_with_moves = 0
    forms = Counter()
    for c in codes:
        m = _CONDBR_RE.match("    " + c) if not c.endswith(":") else None
        if m:
            forms[m.group(1)] += 1
        if m and m.group(4).startswith(".Lbrc") and m.group(4).endswith("_true"):
            brc_sites += 1
            j = label_at.get(m.group(4))
            if j is None:
                continue
            body = []
            k = j + 1
            while k < len(codes):
                t = codes[k]
                if t.endswith(":"):
                    break
                if t:
                    body.append(t)
                k += 1
            if len(body) == 1 and body[0].startswith("j "):
                stub_bare += 1
            else:
                stub_with_moves += 1

    report = {
        "schema": "a100c-branch-census/v1",
        "case": f"{args.operator}#[{args.shape}]#{args.dtype}",
        "switch": "off" if args.off else "on",
        "artifact": {"key": entry.name, "sha256": artifact["sha256"],
                     "identity": artifact["identity"]},
        "brc_sites": brc_sites,
        "stub_bare": stub_bare,
        "stub_with_moves": stub_with_moves,
        "peephole_branch":
            artifact["stages"]["emission"].get("peephole_branch", {}),
        "cond_branch_forms": dict(forms),
        "emitted_lines":
            artifact["stages"]["emission"].get("emitted_lines"),
    }
    out = json.dumps(report, indent=1)
    if args.out:
        Path(args.out).write_text(out + "\n")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
