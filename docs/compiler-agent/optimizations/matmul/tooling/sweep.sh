#!/usr/bin/env bash
# Baseline metric sweep for the matmul round (human-guided).
# One metrics run per (case, threads); resume-safe (skips existing
# metrics.json).  Evidence under
# docs/compiler-agent/optimizations/matmul/baseline/metrics/.
set -uo pipefail
cd /home/i_yinzida/compiler-a100-experiment-001
set -a; . ./.env; set +a

# usage: sweep.sh [metrics-root]   (default: the baseline root)
METRICS=${1:-docs/compiler-agent/optimizations/matmul/baseline/metrics}
mkdir -p "$METRICS"

run() {  # run <name> <operator> <shape> <dtype> [threads]
  local name=$1 op=$2 shape=$3 dtype=$4 threads=${5:-1}
  local out="$METRICS/$name-t$threads"
  if [ -f "$out/metrics.json" ]; then
    echo "[skip] $name-t$threads (exists)"
    return 0
  fi
  echo "[run ] $name-t$threads"
  if ! timeout 900 python3 tools/profiling/collect_metrics.py \
      --operator "$op" --shape "$shape" --dtype "$dtype" \
      --threads "$threads" --steady-repeats 5 --out "$out" \
      > "$out.log" 2>&1; then
    echo "[FAIL] $name-t$threads (see $out.log)"
  fi
}

# -- representative subset, 1 worker --------------------------------------
run plain-128-f16      suite/dev/matmul_kernel.py            128,128,128 float16
run plain-128-f32      suite/dev/matmul_kernel.py            128,128,128 float32
run plain-128-bf16     suite/dev/matmul_kernel.py            128,128,128 bfloat16
run plain-ragged-f16   suite/dev/matmul_kernel.py            17,33,100   float16
run k64-f16            suite/dev/matmul_k64_kernel_0ab65594.py 128       float16
run atb-f16            suite/dev/matmul_at_b_kernel_043f2a05.py 128      float16
run abt-f16            suite/dev/matmul_abt_kernel.py        128,96,100  float16
run grouped-f16        suite/dev/grouped_gemm_kernel.py      3,17,19,13  float16
run batched-f16        suite/perf/batched_vecmat_mult.py     32,32,32    float16
run batched-tail-f16   suite/perf/batched_vecmat_mult.py     33,33,33    float16
run fusedgn-f32        suite/dev/fused_gemm_gn_min_kernel.py 64,128,128  float32
run rms-f16            suite/dev/rms_matmul_rbe.py           1,64,64,64  float16
run linact-f16         suite/perf/triton_linear_activation.py 32,32,32   float16
run tril-f16           suite/dev/tril_matmul_kernel_6d320d58.py 128      float16
run triton2-f16        suite/perf/matmul_triton2.py          32,32,32    float16

# -- worker-count spread (cross-worker totals + per-worker distribution) --
for t in 1 2 4 8; do
  run plain-128-f16    suite/dev/matmul_kernel.py            128,128,128 float16 "$t"
  run batched-f16      suite/perf/batched_vecmat_mult.py     32,32,32    float16 "$t"
  run fusedgn-f32      suite/dev/fused_gemm_gn_min_kernel.py 64,128,128  float32 "$t"
done

echo "sweep done"
