#!/usr/bin/env bash
set -euo pipefail
source "$(dirname -- "${BASH_SOURCE[0]}")/env.sh"
original_id="${1:?usage: run-original-container.sh ORIGINAL_ID}"
temporary="$(mktemp --suffix=.json)"
trap 'rm -f -- "$temporary"' EXIT
"$A100_PROJECT_ROOT/a100_support/run-reference.sh" - "$original_id" "$temporary" <<'PY'
import json,sys
from a100_support.question_runner import original_map
question=original_map().get(sys.argv[1])
if question is None:
    print('Unknown frozen original ID; remains unverified',file=sys.stderr)
    raise SystemExit(2)
with open(sys.argv[2],'w') as stream:json.dump(question,stream)
PY
"$A100_PROJECT_ROOT/a100_support/run-candidate-container.sh" "$temporary"
