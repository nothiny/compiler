#!/usr/bin/env bash
# Build tools/profiling/full_instruction_counts.so with the same include
# flags a100_support/probes.py uses for the stock plugin (QEMU 10 plugin
# API + the host-runtime glib headers), derived from the project .env.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
root="$(cd "$here/../.." && pwd)"
# shellcheck disable=SC1091
[ -f "$root/.env" ] && . "$root/.env"
: "${A100_PREFIX:?A100_PREFIX not set (source the project .env)}"
gcc -O2 -Wall -Wextra -shared -fPIC -pthread \
    -I"$A100_PREFIX/jdsk-qemu-10.0.2/include" \
    -I"$A100_PREFIX/host-runtime-bookworm/include/glib-2.0" \
    -I"$A100_PREFIX/host-runtime-bookworm/lib/glib-2.0/include" \
    "$here/full_instruction_counts.c" \
    -o "$here/full_instruction_counts.so"
echo "built $here/full_instruction_counts.so"
