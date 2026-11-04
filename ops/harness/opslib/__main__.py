"""``python3 -m opslib <command>`` entry point.

Commands:
    catalog [--check|--rebuild]     build / validate the operator index
    golden --prune [--cache-dir D]  drop golden-cache entries whose operator
                                    file changed (see opslib.golden)
    golden --stats                  cache size / entry counts
    golden --build ...              pre-build cases in parallel (see --help)
"""
from __future__ import annotations

import sys


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        print(__doc__)
        return 2
    command, rest = argv[0], argv[1:]
    if command == "golden":
        from opslib import golden
        return golden.main(rest)
    if command == "catalog":
        from opslib import catalog
        return catalog.main(rest)
    print(f"unknown command {command!r}\n{__doc__}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
