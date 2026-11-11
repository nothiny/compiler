#!/usr/bin/env bash
# Baseline metric sweep for the softmax round (human-guided).
# One metrics run per (case, threads); resume-safe (skips existing
# metrics.json).  Evidence under
# docs/compiler-agent/optimizations/softmax/baseline/metrics/.
set -uo pipefail
cd /home/i_yinzida/compiler-a100-experiment-001
set -a; . ./.env; set +a

# usage: sweep.sh [metrics-root]   (default: the baseline root)
METRICS=${1:-docs/compiler-agent/optimizations/softmax/baseline/metrics}
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

# -- full family coverage at 1 worker (25 operators; the larger declared
#    shape; fp32 base + fp16/bf16 on the exp-heavy cores) -----------------
run softmax-f32            suite/perf/softmax.py                                4,97       float32
run softmax-f16            suite/perf/softmax.py                                4,97       float16
run softmax-bf16           suite/perf/softmax.py                                4,97       bfloat16
run softmax-log-f32        suite/perf/softmax_log.py                            4,97       float32
run softmax-mul-f16        suite/perf/softmax_mul.py                            4,97       float16
run logsumexp-f32          suite/perf/logsumexp.py                              4,97       float32
run logsumexp-f16          suite/perf/logsumexp.py                              4,97       float16
run log-softmax-linear-f16 suite/perf/log_softmax_linear.py                     17,33      float16
run inner-f32              suite/dev/softmax_kernel_inner.py                    97         float32
run inner-f16              suite/dev/softmax_kernel_inner.py                    97         float16
run single-block-f32       suite/dev/softmax_single_block_forward_kernel.py     20,17      float32
run multi-block-f32        suite/dev/softmax_multi_block_forward_kernel.py      18,17      float32
run multi-block2-f32       suite/dev/softmax_multi_block_forward_kernel_16feef5d77276b9f.py 5,97 float32
run fused-ce-ls-f32        suite/perf/fused_cross_entropy_log_softmax.py        11,35      float32
run fused-ce-ls-f16        suite/perf/fused_cross_entropy_log_softmax.py        11,35      float16
run repeat-interleave-f32  suite/perf/fused_repeat_interleave_log_softmax.py    4,5        float32
run grpo-sel-ls-f32        suite/dev/grpo_loss__selective_log_softmax_kernel.py 3,11,67    float32
run grpo-sel-ls-f16        suite/dev/grpo_loss__selective_log_softmax_kernel.py 3,11,67    float16
run ascend-grpo-f16        suite/dev/backends__ascend__ops__grpo_loss__selective_log_softmax_kernel.py 3,7,17 float16
run small-n-ls-f32         suite/dev/small_n_log_softmax_kernel.py              97         float32
run logsumexp-noninner-f32 suite/dev/logsumexp__logsumexp_kernel_non_inner.py   104        float32
run cross-entropy-f32      suite/dev/cross_entropy_kernel.py                    17,97      float32
run ce-plain-f32           suite/dev/cross_entropy_forward_kernel_plain.py      13,17      float32
run dropout-softmax-f32    suite/dev/dropout_softmax_fwd_kernel.py              33,100     float32
run dropout-softmax-f16    suite/dev/dropout_softmax_fwd_kernel.py              33,100     float16
run linear-dropout-f16     suite/dev/linear_dropout_softmax_kernel.py           16,128,128 float16
run bias-scale-sigmoid-f16 suite/dev/softmax_bias_scale_sigmoid_fused_nchw_inplace.py 2,64,128 float16
run bce-f32                suite/dev/binary_cross_entropy_elementwise_kernel.py 97         float32
run soft-margin-f32        suite/dev/soft_margin_loss_partial_sum_kernel.py     118        float32
run logit-f32              suite/dev/logit_kernel.py                            109        float32
run logit2-f32             suite/dev/logit_kernel_2.py                          110        float32
run perf-logit-f16         suite/perf/logit.py                                  128        float16

# -- worker-count spread (cross-worker totals + per-worker distribution) --
for t in 1 2 4 8; do
  run softmax-f16            suite/perf/softmax.py                         4,97       float16 "$t"
  run inner-f16              suite/dev/softmax_kernel_inner.py             97         float16 "$t"
  run linear-dropout-f16     suite/dev/linear_dropout_softmax_kernel.py    16,128,128 float16 "$t"
  run fused-ce-ls-f32        suite/perf/fused_cross_entropy_log_softmax.py 11,35      float32 "$t"
done

echo "sweep done"
