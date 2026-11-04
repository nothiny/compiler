"""Corpus invariants: one JIT, public tl only, no torch import, case layer.

Operators still awaiting a case layer are listed explicitly in
KNOWN_UNCASED; the test asserts the list only ever shrinks (files listed
there really lack ``make_case``; files not listed really have the layer).
"""
from __future__ import annotations

import ast
from pathlib import Path

import pytest

HARNESS = Path(__file__).resolve().parents[1]     # <root>/harness
ROOT = HARNESS.parent                               # the corpus root
GROUPS = ("suite/dev", "suite/perf")

# Explicit, shrinking allow-list: operators without a case layer yet
# (another agent is adding them).  Do not add names here without removing
# others; the point is that this list trends to empty.
KNOWN_UNCASED = {
    
}


def _operator_files():
    files = []
    for group in GROUPS:
        directory = ROOT / group
        for path in sorted(directory.glob("*.py")):
            if path.name in {"case_utils.py", "mathref.py", "operator_catalog.py",
                             "operator_entry.py", "runner.py", "run.py", "validate.py"}:
                continue
            files.append(path)
    return files


def _has_case_layer(text: str) -> bool:
    return "def make_case" in text or "def _make_case" in text


@pytest.mark.parametrize("path", _operator_files(), ids=str)
def test_one_jit_public_tl_no_torch(path):
    text = path.read_text()
    tree = ast.parse(text)
    kernels = [n for n in tree.body if isinstance(n, ast.FunctionDef)
               and any("triton.jit" in ast.unparse(d) for d in n.decorator_list)]
    assert len(kernels) == 1, f"expected exactly one @triton.jit in {path}"
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert alias.name.split(".")[0] != "torch", f"torch import in {path}"
        if isinstance(node, ast.ImportFrom):
            assert not (node.module or "").startswith("torch"), f"torch import in {path}"
    forbidden = {"math", "extra", "libdevice", "cuda"}
    for node in ast.walk(kernels[0]):
        if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name) \
                and node.value.id == "tl":
            assert node.attr not in forbidden, \
                f"forbidden namespace tl.{node.attr} in {path}"


@pytest.mark.parametrize("path", _operator_files(), ids=str)
def test_no_dot_precision_knob(path):
    """The declared subset has exactly two dot semantics (bf16/fp16 -> fp32,
    fp32 -> IEEE); no operator may pass a reduced-mantissa vendor knob."""
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        if node.func.attr != "dot":
            continue
        passed = {kw.arg for kw in node.keywords}
        assert not (passed & {"input_precision", "allow_tf32"}), \
            f"{path} passes a dot precision knob {sorted(passed)}"


@pytest.mark.parametrize("path", _operator_files(), ids=str)
def test_case_layer_presence(path):
    text = path.read_text()
    rel = str(path.relative_to(ROOT))
    if rel in KNOWN_UNCASED:
        assert not _has_case_layer(text), \
            f"{rel} has a case layer; remove it from KNOWN_UNCASED"
    else:
        assert _has_case_layer(text), \
            f"{rel} lacks a case layer; add a case layer (do not extend KNOWN_UNCASED)"


def test_known_uncased_list_only_shrinks():
    for rel in KNOWN_UNCASED:
        assert (ROOT / rel).is_file(), f"{rel} listed but missing"
