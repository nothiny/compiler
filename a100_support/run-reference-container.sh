#!/usr/bin/env bash
# The trusted broker calls this wrapper; workers receive neither Docker access
# nor the private broker directory. Standalone source gets a cache per question.
set -euo pipefail
source "$(dirname -- "${BASH_SOURCE[0]}")/env.sh"
question="$(realpath -- "${1:?usage: run-reference-container.sh QUESTION.json-or-py}")" || exit 2
if [[ ! -r "$question" ]]; then echo 'Question input is unavailable' >&2; exit 2; fi
image='python@sha256:5560e9ab8709f459489e5b8aa696eda8a07ef821e14bb122be62d91234bfa98b'
site="$A100_PREFIX/venvs/triton-cpu/lib/python3.12/site-packages"
source_tree="$HOME/.cache/a100-prep/triton-cpu-src"
cache_name="a100-private-reference-cache-user$(id -u)"
question_target=/question.json
extra=()
if [[ "$question" == *.py ]]; then
  question_target=/question.py
  public_cache="$(python3 "$A100_PROJECT_ROOT/a100_support/public_cache.py" --path)"
  question_hash="$(sha256sum -- "$question")"
  question_hash="${question_hash%% *}"
  cache_name="a100-private-question-${question_hash:0:32}"
  extra=(--mount "type=bind,source=$public_cache,target=$public_cache,readonly"
    -e "A100_PUBLIC_REFERENCE_CACHE=$public_cache"
    -e TRITON_CACHE_MANAGER=a100_support.reference_cache:PublicReadThroughCache
    -e A100_QUESTION_ISOLATED=1)
fi
# The sealed question is mode 0600. Run as its owner, with no DAC override
# capability, rather than weakening permissions on the broker's private file.
docker run --rm --network=none --read-only --cap-drop=ALL \
  --mount "type=volume,source=$cache_name,target=/reference-cache" \
  "$image" python -c 'import os; os.chmod("/reference-cache",0o1777)'
cache=(--mount "type=volume,source=$cache_name,target=/reference-cache")
exec python3 "$A100_PROJECT_ROOT/a100_support/checked_question.py" --mode reference -- \
  docker run --rm --network=none --read-only --cap-drop=ALL \
  --user "$(id -u):$(id -g)" \
  --security-opt=no-new-privileges --pids-limit=256 --memory=6g --cpus=2 \
  --tmpfs /tmp:rw,exec,size=2g --tmpfs /root:rw,exec,mode=1777,size=128m \
  --mount "type=bind,source=$A100_PROJECT_ROOT,target=$A100_PROJECT_ROOT,readonly" \
  --mount "type=bind,source=$A100_PREFIX/reference-support,target=$A100_PREFIX/reference-support,readonly" \
  --mount "type=bind,source=$site,target=/reference-packages,readonly" \
  --mount "type=bind,source=$source_tree,target=$source_tree,readonly" \
  --mount "type=bind,source=$question,target=$question_target,readonly" \
  "${cache[@]}" "${extra[@]}" \
  -e "PYTHONPATH=$A100_PROJECT_ROOT:$A100_PROJECT_ROOT/ops/harness:/reference-packages:$source_tree/python" \
  -e "A100_PREFIX=$A100_PREFIX" -e TRITON_DEFAULT_BACKEND=cpu -e TRITON_INTERPRET=0 \
  -e TRITON_F32_DEFAULT=ieee -e TRITON_CPU_FAST_MATH=0 -e A100_REFERENCE_THREADS=1 \
  -e OMP_NUM_THREADS=1 -e OPENBLAS_NUM_THREADS=1 -e MKL_NUM_THREADS=1 \
  -e TRITON_CACHE_DIR=/reference-cache \
  "$image" python "$A100_PROJECT_ROOT/a100_support/question_runner.py" --mode reference --case "$question_target"
