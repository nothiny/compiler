"""The single operator index: explicit metadata, one AST scan, O(1) lookup.

Replaces the string-sniffing inventory (``'OPERATOR_NAME = "G/"' in text``
and friends) and the three duplicated resolver loops
(``operator_entry._entry_for``, ``run_ops._find_operator``).  Every operator
file carries a literal ``OPERATOR`` dict (machine-generated); the index is
built from the AST without importing any operator:

    OPERATOR = {"name": "gelu", "group": "tritonbench", "channel": "T",
                "execution": "triton_kernel", "verification": "correctness",
                "tags": ["elementwise"]}

``catalog.json`` (repo root, generated) stores each file's dict, sha256,
kernel name and literal SHAPES/DTYPES.  Lookup by path / name / ``G/xxx``
alias is a dict hit; stale entries (mtime, then sha) are rebuilt lazily.

    python3 -m opslib catalog                  # (re)build catalog.json
    python3 -m opslib catalog --check          # assert it is up to date
    python3 -m opslib export --group basic DIR # standalone copy of a group

Layout: operator files live directly in ``<group>/`` (``basic/add.py``,
``hard/matmul.py``); only an export puts them in a flat ``operators/``.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

# <corpus root>/harness/opslib/catalog.py: operators live under the corpus root
HARNESS = Path(__file__).resolve().parent.parent
ROOT = HARNESS.parent
INDEX_PATH = ROOT / "catalog.json"
# The two input directories of this corpus, in their declared order:
# ``suite/dev`` is the correctness lane, ``suite/perf`` the performance lane.
LOCAL_GROUPS = ("suite/dev", "suite/perf")   # the dev suite; the upstream pool
                                            # (basic/ ...) is addressed via --group
ALL_GROUPS = LOCAL_GROUPS


def channel_names(channel: str = "all") -> tuple[str, ...]:
    value = channel.lower()
    if value == "all":
        return ("local", "T", "G")
    if value == "both":
        return ("T", "G")
    if value == "local":
        return ("local",)
    if value in {"t", "g"}:
        return (value.upper(),)
    raise ValueError("channel must be T, G, both, local, or all")


# ------------------------------------------------------------------ scanning
def _jit_kernel(tree: ast.Module) -> str | None:
    """Name of the single ``@triton.jit`` kernel (or its autotune wrapper)."""
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        for decorator in node.decorator_list:
            target = decorator.func if isinstance(decorator, ast.Call) else decorator
            if (isinstance(target, ast.Attribute) and target.attr in {"jit", "autotune"}
                    and isinstance(target.value, ast.Name)
                    and target.value.id == "triton"):
                return node.name
            if isinstance(target, ast.Name) and target.id in {"jit", "autotune"}:
                return node.name
    return None


def _literal(node: ast.AST) -> Any:
    try:
        return ast.literal_eval(node)
    except (ValueError, SyntaxError):
        return None


def _operator_dict(tree: ast.Module) -> dict[str, Any] | None:
    for node in tree.body:
        if (isinstance(node, ast.Assign)
                and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and node.targets[0].id == "OPERATOR"):
            value = _literal(node.value)
            return value if isinstance(value, dict) else None
    return None


def _module_literals(tree: ast.Module) -> dict[str, Any]:
    out = {}
    for node in tree.body:
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)):
            name = node.targets[0].id
            if name in ("SHAPES", "DTYPES"):
                out[name] = _literal(node.value)
    return out


def _fallback_metadata(path: Path, text: str, group: str) -> dict[str, Any]:
    """Pre-generation fallback: derive what the old string sniffing did."""
    if group == "tritonbench":
        channel = "G" if 'OPERATOR_NAME = "G/' in text else "T"
        return {"name": path.stem, "group": group, "channel": channel,
                "execution": "triton_kernel", "verification": "correctness",
                "tags": []}
    return {"name": f"{group}/{path.stem}", "group": group, "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": []}


def _scan_file(path: Path, relative: str, group: str) -> dict[str, Any] | None:
    text = path.read_text(errors="ignore")
    if "def make_case" not in text and "def _make_case" not in text:
        return None
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return None
    meta = _operator_dict(tree)
    derived = meta or _fallback_metadata(path, text, group)
    literals = _module_literals(tree)
    return {
        "source": relative,
        "name": str(derived.get("name") or path.stem),
        # the *directory* decides the group: this corpus ships two input
        # directories (suite/dev, suite/perf) and the operators' own OPERATOR
        # metadata still records the upstream tier they were selected from.
        "group": group,
        "channel": str(derived.get("channel") or "local"),
        "execution": str(derived.get("execution") or "triton_kernel"),
        "verification": str(derived.get("verification") or "correctness"),
        "tags": [str(tag) for tag in derived.get("tags", ())],
        "kernel": _jit_kernel(tree),
        "shapes": _jsonable_shapes(literals.get("SHAPES")),
        "dtypes": _jsonable_shapes(literals.get("DTYPES")),
        "sha256": hashlib.sha256(text.encode()).hexdigest(),
        "size": path.stat().st_size,
    }


def _jsonable_shapes(value):
    """Tuples -> lists so a JSON round-trip of the index is stable."""
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        return [_jsonable_shapes(item) for item in value]
    return value


def _collection_name(root: Path) -> str | None:
    """A root with ``collection.json`` is a standalone single-group copy."""
    path = root / "collection.json"
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text()).get("name")
    except ValueError:
        return None


def _scan_root(root: Path) -> list[dict[str, Any]]:
    """One index entry per operator file under ``root`` (AST only)."""
    collection = _collection_name(root)
    operators = []
    if collection:
        directories = [(collection, root / "operators")]
    else:
        # Corpus layout: operator files live directly in ``<group>/``.
        directories = [(group, root / group) for group in ALL_GROUPS]
    for group, directory in directories:
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob("*.py")):
            entry = _scan_file(path, str(path.relative_to(root)), group)
            if entry is not None:
                operators.append(entry)
    operators.sort(key=lambda item: item["source"])
    return operators


def build_index(root: Path | None = None) -> dict[str, Any]:
    """Scan every group directory (AST only, no imports) -> index dict."""
    root = root or ROOT
    operators = _scan_root(root)
    return {"schema": "opslib-catalog/1", "operators": operators}


def _index_stale(index: dict, root: Path | None = None) -> bool:
    """Staleness is content-addressed (size + sha256): touching a file
    without changing it never rewrites the committed catalog.json."""
    root = root or ROOT
    recorded = {item["source"]: item for item in index.get("operators", ())}
    live: set[str] = set()
    for _, directory in _scan_directories(root):
        if not directory.is_dir():
            continue
        for path in directory.glob("*.py"):
            relative = str(path.relative_to(root))
            live.add(relative)
            item = recorded.get(relative)
            if item is None:
                return True
            if path.stat().st_size != item["size"]:
                return True
            if item["sha256"] != hashlib.sha256(
                    path.read_bytes()).hexdigest():
                return True
    return live != set(recorded)


def _scan_directories(root: Path):
    collection = _collection_name(root)
    if collection:
        return [(collection, root / "operators")]
    return [(group, root / group) for group in ALL_GROUPS]


def load_index(root: Path | None = None, *, rebuild: bool = False) -> dict[str, Any]:
    """The current index; rebuilt automatically when any file changed."""
    root = root or ROOT
    path = root / "catalog.json"
    index = None
    if path.is_file() and not rebuild:
        try:
            index = json.loads(path.read_text())
        except ValueError:
            index = None
    if index is None or _index_stale(index, root):
        index = build_index(root)
        try:
            path.write_text(json.dumps(index, indent=1) + "\n")
        except OSError:
            pass  # read-only checkout: the in-memory index is still usable
    return index


# ------------------------------------------------------------------- lookup
def entry_aliases(item: dict[str, Any]) -> set[str]:
    """Accept real file paths and the existing short operator identifiers."""
    path = Path(item["path"])
    source = str(item["source"]).replace("\\", "/")
    group = str(item["group"])
    names = {source, str(item["name"]), f"{group}/{path.name}",
             f"{group}/{path.stem}", f"{group}/operators/{path.name}"}
    if group == "tritonbench":
        names.update({path.name, path.stem})
    if item["channel"] in {"T", "G"}:
        for channel in (item["channel"], item["channel"].lower()):
            names.update({f"{channel}/{path.name}", f"{channel}/{path.stem}"})
    return names


class _Catalog:
    """The loaded index plus its lookup structures."""

    def __init__(self, root: Path | None = None):
        self.root = root or ROOT
        self.collection = _collection_name(self.root)
        self.reload()

    def reload(self) -> None:
        self.index = load_index(self.root)
        self.by_source = {item["source"]: item for item in self.index["operators"]}
        self.by_alias: dict[str, list[dict[str, Any]]] = {}
        for item in self.index["operators"]:
            entry = self._entry(item)
            for alias in entry_aliases(entry):
                self.by_alias.setdefault(alias, []).append(item)
            if self.collection:      # single-group root: bare stems are unique
                self.by_alias.setdefault(Path(item["source"]).stem, []).append(item)

    def _entry(self, item: dict[str, Any]) -> dict[str, Any]:
        return {
            "channel": item["channel"], "group": item["group"],
            "name": item["name"], "source": item["source"],
            "path": self.root / item["source"],
            "execution": item["execution"], "verification": item["verification"],
            "oracle": "numpy", "tags": item.get("tags", ()),
            "kernel": item.get("kernel"), "sha256": item.get("sha256"),
        }

    def entries(self, channel: str = "all") -> Iterator[dict[str, Any]]:
        """Historical enumeration order: local groups in LOCAL_GROUPS order,
        then the T and G channels (source-sorted within each)."""
        wanted = set(channel_names(channel))
        group_order = LOCAL_GROUPS
        channel_order = {"local": 0, "T": 1, "G": 2}

        def rank(item: dict[str, Any]):
            group = item["group"] if item["group"] in group_order else group_order[-1]
            return (channel_order.get(item["channel"], 3),
                    group_order.index(group), item["source"])

        for item in sorted((i for i in self.index["operators"]
                            if i["channel"] in wanted), key=rank):
            yield self._entry(item)

    def find(self, identifier: str | Path) -> dict[str, Any]:
        raw = str(identifier).replace("\\", "/")
        value = Path(identifier)
        matches = list(self.by_alias.get(raw, ()))
        if not matches and value.exists():
            resolved = value.resolve()
            matches = [item for item in self.index["operators"]
                       if (self.root / item["source"]).resolve() == resolved]
        if not matches:
            channel, _, name = raw.partition("/")
            if channel.upper() in {"T", "G"}:
                wanted = f"{channel.upper()}/{Path(name).stem}"
                matches = [item for item in self.index["operators"]
                           if f"{item['channel']}/{item['name']}" == wanted]
        if not matches:
            raise FileNotFoundError(f"operator entry not found: {identifier}")
        if len(matches) > 1:
            raise ValueError("operator entry is ambiguous: " + ", ".join(
                str(item["source"]) for item in matches[:8]))
        return self._entry(matches[0])

    def summary(self, channel: str = "all") -> dict[str, int]:
        result = {"total": 0, "correctness": 0, "baseline": 0,
                  "reference_only": 0}
        for item in self.entries(channel):
            result["total"] += 1
            result[item["verification"]] += 1
        return result


_CACHED: _Catalog | None = None


def _catalog() -> _Catalog:
    global _CACHED
    if _CACHED is None:
        _CACHED = _Catalog()
    return _CACHED


def set_root(path: str | Path) -> None:
    """Point the catalog at a different root.

    The per-group shims (``basic/operator_catalog.py`` etc.) call this with
    their own directory so that running *inside* a group -- ``cd basic &&
    python3 run.py`` -- enumerates only that group's operators (the
    collection-root semantics the pre-opslib copies had), instead of the
    whole repository.  The root must carry a ``collection.json``.
    """
    global _CACHED
    root = Path(path).resolve()
    if not (root / "collection.json").is_file():
        raise ValueError(f"{root} is not a collection root (no collection.json)")
    _CACHED = _Catalog(root)


def entries(channel: str = "all") -> Iterator[dict[str, Any]]:
    return _catalog().entries(channel)


def find(identifier: str | Path) -> dict[str, Any]:
    """Resolve a path / name / ``G/xxx`` alias to one catalog entry."""
    return _catalog().find(identifier)


def summary(channel: str = "all") -> dict[str, int]:
    return _catalog().summary(channel)


# ------------------------------------------------------------------- loader
@dataclass
class OperatorSpec:
    """The compiler-facing loader for one operator source file.

    The source file is the unit of compilation. ``load_operator`` only
    resolves the file; ``make_case`` constructs its inputs and ``test``
    sends the resulting case through the runner.
    """

    entry: dict[str, Any]
    _operator: Any = None

    @property
    def name(self) -> str:
        return str(self.entry["name"])

    @property
    def source(self) -> str:
        return str(self.entry["source"])

    @property
    def path(self) -> Path:
        return Path(self.entry["path"])

    @property
    def channel(self) -> str:
        return str(self.entry["channel"])

    @property
    def execution(self) -> str:
        return str(self.entry["execution"])

    @property
    def verification(self) -> str:
        return str(self.entry["verification"])

    @property
    def oracle(self) -> str:
        return str(self.entry["oracle"])

    @property
    def supported(self) -> bool:
        return not bool(self.entry.get("unsupported"))

    def load(self) -> Any:
        if self._operator is None:
            from opslib import runner
            self._operator = runner.load_operator(self.path)
        return self._operator

    @property
    def source_text(self) -> str:
        return self.path.read_text()

    def make_case(self, shape=None, dtype=None, seed=None) -> dict[str, Any]:
        return self.load().make_case(shape=shape, dtype=dtype, seed=seed)

    def ref(self, args: dict[str, Any], meta: dict[str, Any]) -> dict[str, Any]:
        return self.load().ref(args, meta)

    def test(self, case=None, *, executor=None, device="cuda", shape=None,
             dtype=None, seed=None, rtol=None, atol=None) -> dict[str, Any]:
        from opslib import runner
        return runner.test(self.load(), case=case, shape=shape, dtype=dtype,
                           seed=seed, executor=executor, device=device,
                           rtol=rtol, atol=atol)

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            raise AttributeError(name)
        return getattr(self.load(), name)


def load_operator(identifier: str | Path) -> OperatorSpec:
    return OperatorSpec(find(identifier))


def specs(channel: str = "all") -> Iterator[OperatorSpec]:
    for item in entries(channel):
        yield OperatorSpec(item)


# ---------------------------------------------------------------------- CLI
def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description="the operator index")
    parser.add_argument("--check", action="store_true",
                        help="exit 1 if catalog.json is stale (never rebuilds)")
    parser.add_argument("--rebuild", action="store_true",
                        help="force a full rescan")
    args = parser.parse_args(argv)

    if args.check:
        # read the file as-is and compare against a fresh scan; do NOT go
        # through load_index(), which would rebuild-and-rewrite a stale
        # index before the comparison and make --check vacuously pass
        current = (json.loads(INDEX_PATH.read_text())
                   if INDEX_PATH.is_file() else None)
        if current == build_index():
            print("catalog.json is up to date")
            return 0
        print("catalog.json is stale")
        return 1

    index = load_index(rebuild=args.rebuild)
    channels: dict[str, int] = {}
    for item in index["operators"]:
        channels[item["channel"]] = channels.get(item["channel"], 0) + 1
    missing_meta = [item["source"] for item in index["operators"]
                    if not _operator_dict(ast.parse(
                        (ROOT / item["source"]).read_text(errors="ignore")))]
    print(json.dumps({"operators": len(index["operators"]),
                      "channels": channels,
                      "missing_OPERATOR_metadata": len(missing_meta)},
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
