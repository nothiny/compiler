#!/usr/bin/env bash
set -euo pipefail
source "$(dirname -- "${BASH_SOURCE[0]}")/env.sh"
if [ "$#" -eq 0 ]; then
  echo 'usage: run-riscv.sh ./operator_exec [arguments...]' >&2
  exit 2
fi
if [[ -n "${A100_QEMU_LOADER:-}" ]]; then
  exec "$A100_QEMU_LOADER" --library-path "${A100_QEMU_HOST_LIB:?native loader library path required}" \
    "$A100_QEMU" -L "$A100_SYSROOT" -cpu "$A100_QEMU_CPU" "$@"
fi
exec "$A100_QEMU" -L "$A100_SYSROOT" -cpu "$A100_QEMU_CPU" "$@"
