"""Regenerate KNOWN_UNCASED in test_normalized_corpus.py.

Run this while the casing agent is still adding case layers; once every
operator has a layer the list stays empty and this script becomes a no-op.
"""
from pathlib import Path
import re

HARNESS = Path(__file__).resolve().parents[1]     # <root>/harness
ROOT = HARNESS.parent                               # the corpus root
SHIMS = {"case_utils.py", "mathref.py", "operator_catalog.py",
         "operator_entry.py", "runner.py", "run.py", "validate.py", "__init__.py"}
uncased = []
for group in ("suite/dev", "suite/perf"):
    for p in sorted((ROOT / group).glob("*.py")):
        if p.name in SHIMS:
            continue
        text = p.read_text()
        if "def make_case" not in text and "def _make_case" not in text:
            uncased.append(str(p.relative_to(ROOT)))
target = ROOT / "tests" / "test_normalized_corpus.py"
text = target.read_text()
text = re.sub(r"KNOWN_UNCASED = \{[^}]*\}",
              "KNOWN_UNCASED = {\n    " + "\n    ".join(f'"{u}",' for u in uncased) + "\n}",
              text, count=1)
target.write_text(text)
print(f"KNOWN_UNCASED refreshed: {len(uncased)} entries")
