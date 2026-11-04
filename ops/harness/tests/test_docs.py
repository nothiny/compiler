"""The documentation is read by agents, so it must not rot silently.

Three mechanical checks over every tracked Markdown file:

1. every relative link points at a file or directory that exists, and none
   carries a ``file.py:NN`` line number (those rot whenever a file gains a line);
2. every ``python3 <script>.py ...`` / ``python3 -m opslib <cmd> ...`` line in a
   ``bash`` code block only uses flags that the command's ``--help`` lists;
3. no document hard-codes a test count (``372 passed``) -- such numbers are
   stale the next time a test is added; write "全绿" / "all green" instead.
"""
from __future__ import annotations

import os
import re
import shlex
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parents[1]     # <root>/harness
ROOT = HARNESS.parent                               # the corpus root


def _docs() -> list[Path]:
    listed = subprocess.run(["git", "-C", str(ROOT), "ls-files", "*.md"],
                            capture_output=True, text=True)
    if listed.returncode == 0 and listed.stdout.strip():
        found = {ROOT / p for p in listed.stdout.split()}
    else:  # not a git checkout: every markdown file under the root
        found = {p for p in ROOT.rglob("*.md")
                 if ".git" not in p.parts and "opslib" not in p.parts
                 and "__pycache__" not in p.parts}
    extra = [p for p in ROOT.glob("*.md")]
    return sorted(found | set(extra))


DOCS = _docs()
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
FENCE = re.compile(r"```bash\n(.*?)```", re.S)
ANY_FENCE = re.compile(r"```.*?```", re.S)
CODE_SPAN = re.compile(r"`[^`\n]*`")


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


@pytest.mark.parametrize("doc", DOCS, ids=_rel)
def test_relative_links_resolve(doc):
    prose = CODE_SPAN.sub("", ANY_FENCE.sub("", doc.read_text()))
    broken = []
    for target in LINK.findall(prose):
        if re.match(r"[a-z]+://", target) or target.startswith(("#", "mailto:")):
            continue
        path = target.split("#", 1)[0]
        if re.search(r"\.py:\d+$", path):
            broken.append(f"{target} (line-number link)")
        elif path and not (doc.parent / path).exists():
            broken.append(target)
    assert not broken, f"{_rel(doc)}: broken links {broken}"


def _commands(text: str):
    """Yield (argv-prefix, flags) for runnable corpus commands in bash blocks."""
    for block in FENCE.findall(text):
        for raw in block.splitlines():
            line = raw.split("#", 1)[0].strip()
            if "&&" in line:                      # `cd X && python3 run.py` runs elsewhere
                continue
            if not line.startswith("python3 ") or "<" in line or "$" in line:
                continue
            try:
                words = shlex.split(line)
            except ValueError:
                continue
            if len(words) < 2:
                continue
            if words[1] == "-m":
                if len(words) < 4 or words[2] != "opslib":
                    continue
                prefix = (sys.executable, "-m", "opslib", words[3])
                rest = words[4:]
            elif words[1].endswith(".py"):
                if not (ROOT / words[1]).is_file():
                    yield (words[1],), None           # reported as missing below
                    continue
                prefix = (sys.executable, str(ROOT / words[1]))
                rest = words[2:]
            else:
                continue
            flags = {w.split("=", 1)[0] for w in rest if w.startswith("--")}
            if flags:                             # nothing to check otherwise (and some
                yield prefix, flags               # scripts have no --help: they just run)


@lru_cache(maxsize=None)
def _help(prefix: tuple) -> str:
    # documented commands run from the corpus root with PYTHONPATH=harness
    env = dict(os.environ, PYTHONPATH=str(HARNESS))
    result = subprocess.run([*prefix, "--help"], cwd=ROOT, env=env, capture_output=True,
                            text=True, timeout=180)
    return result.stdout + result.stderr


@pytest.mark.parametrize("doc", DOCS, ids=_rel)
def test_documented_commands_use_existing_flags(doc):
    problems = []
    for prefix, flags in _commands(doc.read_text()):
        if flags is None:
            problems.append(f"{prefix[0]}: no such script")
            continue
        text = _help(prefix)
        if "usage:" not in text:
            problems.append(f"{' '.join(prefix[1:])}: --help failed: {text[-200:]}")
            continue
        missing = sorted(f for f in flags if f not in text)
        if missing:
            problems.append(f"{' '.join(prefix[1:])}: unknown flags {missing}")
    assert not problems, f"{_rel(doc)}:\n  " + "\n  ".join(problems)


@pytest.mark.parametrize("doc", DOCS, ids=_rel)
def test_no_hardcoded_test_counts(doc):
    hits = re.findall(r"\b\d+ (?:passed|tests? passed)\b", doc.read_text())
    assert not hits, f"{_rel(doc)} hard-codes test counts {hits}; say 'all green' instead"
