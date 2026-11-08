#!/usr/bin/env bash
# Re-run the T042 compare-legality probe (results in results.txt).
set -euo pipefail
here="$(cd "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
root="$(cd "$here/../../../../.." && pwd)"
set -a; . "$root/.env"; set +a
for src in "$here"/v*.S; do
  name=$(basename "$src" .S)
  "$A100_CROSS_PREFIX"as -march=rv64gcv "$src" -o "$here/$name.o"
  "$A100_CROSS_PREFIX"gcc -nostdlib -static "$here/$name.o" -o "$here/$name"
  set +e
  timeout 30 "$A100_QEMU" -L "$A100_SYSROOT" -cpu "$A100_QEMU_CPU" \
    "$here/$name" >/dev/null 2>&1
  rc=$?
  set -e
  echo "$name -> exit $rc"
done
