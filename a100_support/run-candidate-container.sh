#!/usr/bin/env bash
set -euo pipefail
source "$(dirname -- "${BASH_SOURCE[0]}")/env.sh"
if [[ -z "${A100_COMPILER_FACTORY:-}" ]]; then
  echo 'Candidate compiler is not implemented/configured; infrastructure remains unverified.' >&2
  exit 2
fi
question="$(realpath -- "${1:?usage: run-candidate-container.sh QUESTION.json}")"
image='python@sha256:5560e9ab8709f459489e5b8aa696eda8a07ef821e14bb122be62d91234bfa98b'
site="$A100_PREFIX/venvs/triton-cpu/lib/python3.12/site-packages"
source_tree="$HOME/.cache/a100-prep/triton-cpu-src"
question_target=/question.json
if [[ "$question" == *.py ]]; then question_target=/question.py; fi
exec python3 "$A100_PROJECT_ROOT/a100_support/checked_question.py" --mode candidate -- \
  docker run --rm --network=none --read-only --cap-drop=ALL \
  --user "$(id -u):$(id -g)" \
  --security-opt=no-new-privileges --pids-limit=256 --memory=6g --cpus=8 \
  --tmpfs /tmp:rw,exec,size=2g --tmpfs /root:rw,exec,mode=1777,size=128m \
  --mount "type=bind,source=$A100_PROJECT_ROOT,target=$A100_PROJECT_ROOT,readonly" \
  --mount "type=bind,source=$A100_TOOLCHAIN,target=$A100_TOOLCHAIN,readonly" \
  --mount "type=bind,source=$A100_PREFIX/qemu-container-runtime,target=$A100_PREFIX/qemu-container-runtime,readonly" \
  --mount "type=bind,source=$A100_PREFIX/jdsk-qemu-10.0.2,target=$A100_PREFIX/jdsk-qemu-10.0.2,readonly" \
  --mount "type=bind,source=$site,target=/reference-packages,readonly" \
  --mount "type=bind,source=$source_tree,target=$source_tree,readonly" \
  --mount "type=bind,source=$question,target=$question_target,readonly" \
  -e "PYTHONPATH=$A100_PROJECT_ROOT:$A100_PROJECT_ROOT/ops/harness:/reference-packages:$source_tree/python" \
  -e "PATH=$A100_TOOLCHAIN/bin:/usr/local/bin:/usr/bin:/bin" \
  -e "A100_PREFIX=$A100_PREFIX" -e "A100_COMPILER_FACTORY=$A100_COMPILER_FACTORY" \
  -e "A100_COMPUTE_THREADS=${A100_COMPUTE_THREADS:-1}" \
  -e "A100_QEMU_LOADER=$A100_PREFIX/qemu-container-runtime/lib64/ld-linux-x86-64.so.2" \
  -e "A100_QEMU_HOST_LIB=$A100_PREFIX/qemu-container-runtime/lib/x86_64-linux-gnu" \
  -e TRITON_INTERPRET=0 -e TRITON_F32_DEFAULT=ieee -e OPENBLAS_NUM_THREADS=1 \
  -e A100_QUESTION_ISOLATED=1 \
  "$image" python "$A100_PROJECT_ROOT/a100_support/question_runner.py" --mode candidate --case "$question_target"
