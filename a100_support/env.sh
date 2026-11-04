#!/usr/bin/env bash
# Source this file from the project or use the explicit launcher paths.
A100_PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
A100_PREFIX="${A100_PREFIX:-$HOME/.local/opt/a100}"
A100_TOOLCHAIN="$A100_PREFIX/toolchain-1.1.2"
A100_SYSROOT="$A100_TOOLCHAIN/sysroot"
A100_QEMU="$A100_PREFIX/jdsk-qemu-10.0.2/bin/qemu-riscv64"
A100_QEMU_CPU='max,vlen=1024,elen=64,vext_spec=v1.0'
A100_LLVM="$A100_PREFIX/llvm-spacemit-f6ded0be"
A100_CROSS_PREFIX="$A100_TOOLCHAIN/bin/riscv64-unknown-linux-gnu-"
A100_REFERENCE_PYTHON="$A100_PREFIX/venvs/triton-cpu/bin/python"
A100_PUBLIC_REFERENCE_CACHE="${A100_PUBLIC_REFERENCE_CACHE:-$HOME/.cache/a100-prep/public-reference-cache-a100-zcode-002}"
COMPILER_WORKFLOW_HOME=/home/i_yinzida/compiler-agent-workflow
export A100_PROJECT_ROOT A100_PREFIX A100_TOOLCHAIN A100_SYSROOT A100_QEMU
export A100_QEMU_CPU A100_LLVM A100_CROSS_PREFIX A100_REFERENCE_PYTHON COMPILER_WORKFLOW_HOME
export A100_PUBLIC_REFERENCE_CACHE
# Do not add reference Python or private compatibility libraries to global PATH.
export PATH="$A100_TOOLCHAIN/bin:$PATH"
