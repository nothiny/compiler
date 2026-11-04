"""Generate ``docs/API_INVENTORY.md``: every ``tl.*`` / ``triton.*`` construct the
corpus's kernels use, with how many operator files use it in each group.

Scans the ``@triton.jit`` function (and its decorators) of every operator in the
four input directories by AST only -- nothing is imported.  The inventory is a
*sample* of the source language (what this corpus happens to call), not its
specification; it is regenerated whenever operators change, so it cannot go
stale the way a hand-written list does.

    python3 harness/compiler_api/api_inventory.py            # writes docs/API_INVENTORY.md
    python3 harness/compiler_api/api_inventory.py --check    # exit 1 if it is stale
"""
from __future__ import annotations

import argparse
import ast
import collections
import sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parents[1]     # <root>/harness
ROOT = HARNESS.parent                               # the corpus root
GROUPS = ("suite/dev", "suite/perf")
OUT = ROOT / "docs" / "API_INVENTORY.md"


def _chain(node: ast.AST) -> str | None:
    parts = []
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
        return ".".join(reversed(parts))
    return None


def _kernel(tree: ast.Module) -> ast.FunctionDef | None:
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and any(
                "jit" in ast.unparse(d) for d in node.decorator_list):
            return node
    return None


def constructs(path: Path) -> tuple[set[str], set[str]]:
    """(calls, attributes) under ``tl.`` / ``triton.`` used by the kernel."""
    kernel = _kernel(ast.parse(path.read_text(errors="ignore")))
    calls, attrs = set(), set()
    if kernel is None:
        return calls, attrs
    called = set()
    # the body and signature only: decorators are recorded separately below
    scope = [n for stmt in kernel.body for n in ast.walk(stmt)] + list(ast.walk(kernel.args))
    for node in scope:
        if isinstance(node, ast.Call):
            name = _chain(node.func)
            if name and name.split(".")[0] in ("tl", "triton"):
                calls.add(name)
                called.add(id(node.func))
    for node in scope:
        if isinstance(node, ast.Attribute) and id(node) not in called:
            name = _chain(node)
            if name and name.split(".")[0] == "tl" and name.count(".") == 1:
                attrs.add(name)            # dtypes and constants: tl.float32, tl.constexpr
    for decorator in kernel.decorator_list:
        target = decorator.func if isinstance(decorator, ast.Call) else decorator
        name = _chain(target)
        if name:
            calls.add(f"@{name}")
    return calls, attrs - {c for c in calls}


def build(groups=GROUPS) -> str:
    groups = tuple(groups)
    calls = collections.defaultdict(collections.Counter)
    attrs = collections.defaultdict(collections.Counter)
    sizes = collections.Counter()
    for group in groups:
        directory = Path(group) if Path(group).is_absolute() else ROOT / group
        for path in sorted(directory.glob("*.py")):
            sizes[group] += 1
            c, a = constructs(path)
            for name in c:
                calls[name][group] += 1
            for name in a:
                attrs[name][group] += 1

    def table(rows):
        head = "| 构造 | " + " | ".join(groups) + " | 合计 |\n|---|" + "---:|" * (len(groups) + 1)
        lines = [head]
        for name, counts in sorted(rows.items(), key=lambda kv: (-sum(kv[1].values()), kv[0])):
            cells = " | ".join(str(counts.get(g, "")) for g in groups)
            lines.append(f"| `{name}` | {cells} | {sum(counts.values())} |")
        return "\n".join(lines)

    total = sum(sizes.values())
    return f"""# tl API 清单(生成物)

由 `python3 harness/compiler_api/api_inventory.py` 从两个输入目录(suite/dev、suite/perf)的 kernel AST 生成,**不要手改**;
算子变了就重新生成。表中数字是**使用该构造的算子文件数**(每个文件最多计一次)。

这是语料**用到了什么**(语言的一个样本),不是语言的规范:一个构造没出现在这里,不代表编译器
可以不支持它;出现在这里的每一个,编译器都必须支持或明确拒绝。

扫描范围:{", ".join(f"{g} {sizes[g]}" for g in groups)},共 {total} 个算子文件。

## 调用与装饰器(`tl.*(...)`、`triton.*(...)`、`@...`)

{table(calls)}

## dtype 与常量(`tl.float16`、`tl.constexpr` 等非调用属性)

{table(attrs)}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--check", action="store_true",
                        help="exit 1 if docs/API_INVENTORY.md is stale (writes nothing)")
    parser.add_argument("--dir", action="append", default=None,
                        help="scan this directory instead of suite/dev+suite/perf "
                             "(repeatable; used for docs/SUBSET.md's pool inventory)")
    parser.add_argument("--out", default=str(OUT))
    args = parser.parse_args()
    groups = tuple(args.dir) if args.dir else GROUPS
    out = Path(args.out)
    text = build(groups)
    if args.check:
        current = OUT.read_text() if OUT.is_file() else ""
        if current == text:
            print("API_INVENTORY.md is up to date")
            return 0
        print("API_INVENTORY.md is stale: rerun harness/compiler_api/api_inventory.py")
        return 1
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text)
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
