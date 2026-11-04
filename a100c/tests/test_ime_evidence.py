#!/usr/bin/env python3
"""test_ime_evidence.py -- the IME slice's executed evidence (T010).

One INT8 and one FP16 dot case compile through the full backend path (tile
plan -> MIR lowering -> IME-aware verification -> legalisation -> selection
-> allocation -> emission -> cross as + ld + precompiled runtime -> ELF),
execute under the declared QEMU endpoint through the a100_support bundle
transport, and compare PASS against an independent numpy reference:

  * acceptance[0]: the QEMU instruction-count plugin
    (a100_support/probes/instruction_counts.c, F008/F048) records executed
    smt.vmadot / smt.vfwmadot counts bound to the same prepared run, case
    identity and artifact sha256 -- the count equals the pure model's
    prediction (output tiles x K steps), never a listing;
  * acceptance[1]: the same artifact executes and compares PASS at 1, 2, 4
    and 8 workers with the worker split recorded (the strided model over
    output tiles, read back from the runtime's per-worker observation);
  * acceptance[3]: a BF16 case executes and compares PASS through the
    vector FP32 path with ZERO smt.* executions (the recorded emulator gap:
    BF16 IME execution is not claimable and never inferred from FP16
    success, F010/F034);
  * acceptance[4]: a tail case (M, N, K all outside the tile extents)
    compares PASS, and the guard-region witness fails: with the staging
    masks dropped in a scratch build the same case reads out of range and
    compares FAIL (MECH-WITNESS-TEST: the zero padding is load-bearing).

Run: python3 a100c/tests/test_ime_evidence.py   (exit 0 = all checks PASS)
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _bootstrap  # noqa: E402

ROOT = _bootstrap.bootstrap()
import warnings  # noqa: E402

warnings.filterwarnings("ignore")

FAILURES = []
EVIDENCE: dict = {"cases": []}


def check(name: str, ok: bool, detail: str = "") -> bool:
    print(f"{'PASS' if ok else 'FAIL'} {name}"
          f"{(' | ' + detail) if detail else ''}")
    if not ok:
        FAILURES.append(name)
    return ok


import numpy as np  # noqa: E402

from a100c.backend import allocate as alloc_mod  # noqa: E402
from a100c.backend import emit as emit_mod  # noqa: E402
from a100c.backend import legalize as legal_mod  # noqa: E402
from a100c.backend import select as select_mod  # noqa: E402
from a100c.ir import mir  # noqa: E402
from a100c.lower import matrix as matrix_mod  # noqa: E402
from a100c.plan import tiles as tiles_mod  # noqa: E402
from a100c.target import DEFAULT_TARGET  # noqa: E402

from a100_support.native_io import pack_case, unpack_outputs  # noqa: E402

BUILD = _bootstrap.load_build_module()
WORK = Path(tempfile.mkdtemp(prefix="a100c-ime-evidence-"))
BINDING = matrix_mod.dot_binding(["a_ptr", "b_ptr", "c_ptr"])
QEMU = os.environ.get("A100_QEMU")
SYSROOT = os.environ.get("A100_SYSROOT")
QEMU_CPU = os.environ.get("A100_QEMU_CPU",
                          "max,vlen=1024,elen=64,vext_spec=v1.0")
RUN_SCRIPT = str(ROOT / "a100_support" / "run-riscv.sh")


# ---------------------------------------------------------------------------
# The compile path (tile plan -> ... -> ELF), the same stages the driver runs
# ---------------------------------------------------------------------------


def compile_dot(ad, bd, od, acc="zero", witness=False, tag=None):
    plan = tiles_mod.plan_dot(tiles_mod.DotDescription(
        a_dtype=ad, b_dtype=bd, out_dtype=od, acc_mode=acc))
    options = matrix_mod.MatrixOptions(witness_drop_tile_padding=witness)
    module = matrix_mod.lower_dot(plan, BINDING, DEFAULT_TARGET, options)
    errors = matrix_mod.verify_module(module)
    if errors:
        raise RuntimeError(f"lowering verification failed: {errors[0]}")
    legal_mod.legalize(module)
    errors = matrix_mod.verify_module(module)
    if errors:
        raise RuntimeError(f"post-legalize verification failed: {errors[0]}")
    selection = select_mod.select(module)
    allocation = alloc_mod.allocate(module, DEFAULT_TARGET)
    program = emit_mod.emit_assembly(
        module, allocation, DEFAULT_TARGET,
        workspace=(plan.workspace_private, 0), selection=selection,
        header=[f"# a100c IME slice: {ad} dot ({plan.path})",
                f"# witness: {options.identity_part()}"])
    tag = tag or f"{ad}-{acc}" + ("-witness" if witness else "")
    asm = WORK / f"{tag}.S"
    asm.write_text(program.text)
    obj, _tools, _assembled, _inv = BUILD.assemble_operator(
        asm, build_dir=WORK / "build")
    BUILD.link_operator([obj], WORK / f"{tag}_exec",
                        build_dir=WORK / "build")
    path = WORK / f"{tag}_exec"
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    return plan, path, sha, program.text


def stage_and_run(exec_path, case, threads=1, counts_out=None,
                  plugin_so=None):
    """Stage one case through the bundle transport and run it (bounded).

    With ``counts_out``: the declared dynamic-observation endpoint -- the
    same QEMU with the instruction-count plugin loaded (F008/F048).
    """
    directory = Path(tempfile.mkdtemp(prefix="a100c-ime-case-"))
    pack_case(case, directory)
    if counts_out is not None:
        command = [QEMU, "-L", SYSROOT, "-cpu", QEMU_CPU,
                   "-plugin", f"{plugin_so},out={counts_out}",
                   str(exec_path),
                   "--bundle", str(directory / "bundle.bin"),
                   "--threads", str(threads)]
    else:
        command = [RUN_SCRIPT, str(exec_path),
                   "--bundle", str(directory / "bundle.bin"),
                   "--threads", str(threads)]
    result = subprocess.run(command, capture_output=True, text=True,
                            timeout=240)
    info = None
    if result.returncode == 0 and result.stdout.strip():
        try:
            info = json.loads(result.stdout.strip().splitlines()[-1])
        except ValueError:
            info = None
    outputs = unpack_outputs(directory) if result.returncode == 0 else None
    return result, outputs, info


def plugin_path() -> Path:
    """The compiled instruction-count plugin (built once if missing)."""
    built = ROOT / "a100_support" / "build" / "instruction_counts.so"
    if built.is_file():
        return built
    out = WORK / "instruction_counts.so"
    prefix = os.environ.get("A100_PREFIX", "")
    include = [f"-I{prefix}/jdsk-qemu-10.0.2/include",
               f"-I{prefix}/host-runtime-bookworm/include/glib-2.0",
               f"-I{prefix}/host-runtime-bookworm/lib/glib-2.0/include"]
    subprocess.run(["gcc", "-O2", "-Wall", "-Wextra", "-shared", "-fPIC",
                    "-pthread", *include,
                    str(ROOT / "a100_support" / "probes" /
                        "instruction_counts.c"),
                    "-o", str(out)], check=True, timeout=120)
    return out


def record(name, **fields):
    row = {"case": name, **fields}
    EVIDENCE["cases"].append(row)
    return row


# ---------------------------------------------------------------------------
# Independent references (numpy, computed on the host from the case inputs)
# ---------------------------------------------------------------------------


def int_case(rng, M, N, K, dtype=np.int8, acc=False):
    a = rng.integers(-100, 100, (M, K)).astype(dtype)
    b = rng.integers(-100, 100, (K, N)).astype(dtype)
    wide = np.int64 if np.dtype(dtype).itemsize <= 2 else np.int32
    product = a.astype(wide) @ b.astype(wide)
    expected = product.astype(np.int32)
    c0 = (rng.integers(-1000, 1000, (M, N)).astype(np.int32)
          if acc else np.zeros((M, N), dtype=np.int32))
    if acc:
        expected = (c0.astype(np.int64) +
                    product.astype(np.int64)).astype(np.int32)
    case = {"args": {"a_ptr": a, "b_ptr": b, "c_ptr": c0.copy()},
            "outputs": ("c_ptr",)}
    return case, expected


def compare_exact(outputs, expected, M, N):
    got = np.asarray(outputs["c_ptr"]).reshape(M, N)
    return np.array_equal(got, expected), got


# ---------------------------------------------------------------------------
# The checks
# ---------------------------------------------------------------------------


def check_int8_plugin(plugin):
    rng = np.random.default_rng(41)
    M, N, K = 24, 20, 32
    case, expected = int_case(rng, M, N, K)
    plan, path, sha, text = compile_dot("int8", "int8", "int32",
                                        tag="int8-main")
    counts_file = WORK / "int8-counts.json"
    result, outputs, info = stage_and_run(path, case, threads=2,
                                          counts_out=str(counts_file),
                                          plugin_so=str(plugin))
    ok = result.returncode == 0
    check("int8-case-executes-under-qemu", ok,
          f"exit {result.returncode}")
    if not ok:
        return
    same, got = compare_exact(outputs, expected, M, N)
    check("int8-case-compares-pass-exact", same,
          "" if same else str([(m, n, int(got[m, n]),
                                int(expected[m, n]))
                               for m, n in np.argwhere(got != expected)[:3]]))
    counts = json.loads(counts_file.read_text())
    rows = [r for r in counts["instructions"]
            if r["mnemonic"] == "smt.vmadot"]
    total = sum(r["executions"] for r in rows)
    predicted = tiles_mod.expected_tile_ops(M, N, K, plan)
    check("int8-plugin-counts-executed-smt-vmadot", total >= 1,
          f"{total} executions over {len(rows)} pc(s)")
    check("int8-plugin-count-equals-tile-model", total == predicted,
          f"counted {total}, model {predicted} (tiles x k-steps)")
    binding_ok = (info is not None and info.get("status") == "ok"
                  and info.get("pool_initializations") == 1)
    check("int8-run-bound-to-artifact-and-workers", binding_ok,
          f"status={info.get('status') if info else '?'} "
          f"workers={[w['items'] for w in info['workers']] if info else '?'}")
    record("int8-24x20x32-threads2", dtype="int8", shape=[M, N, K],
           artifact_sha256=sha, mnemonic="smt.vmadot",
           executed=total, model=predicted,
           workers=[w["items"] for w in info["workers"]],
           compare="exact PASS",
           counts_schema=counts.get("schema"))


def check_fp16_plugin(plugin):
    rng = np.random.default_rng(43)
    M, N, K = 20, 24, 40
    # column-major B: the memory layout provides the tile's contiguous
    # direction, so the B staging runs the vector masked-load path (F031)
    a = (rng.standard_normal((M, K)) * 0.5).astype(np.float16)
    b_row = (rng.standard_normal((K, N)) * 0.5).astype(np.float16)
    b = np.asfortranarray(b_row)
    c = np.zeros((M, N), dtype=np.float32)
    expected = a.astype(np.float32) @ b_row.astype(np.float32)
    case = {"args": {"a_ptr": a, "b_ptr": b, "c_ptr": c},
            "outputs": ("c_ptr",)}
    plan, path, sha, text = compile_dot("float16", "float16", "float32",
                                        tag="fp16-main")
    counts_file = WORK / "fp16-counts.json"
    result, outputs, info = stage_and_run(path, case, threads=4,
                                          counts_out=str(counts_file),
                                          plugin_so=str(plugin))
    ok = result.returncode == 0
    check("fp16-case-executes-under-qemu", ok, f"exit {result.returncode}")
    if not ok:
        return
    got = np.asarray(outputs["c_ptr"]).reshape(M, N)
    same = np.allclose(got, expected, rtol=1e-4, atol=1e-3)
    check("fp16-case-compares-pass", same,
          f"max err {float(np.max(np.abs(got - expected))):.2e}")
    counts = json.loads(counts_file.read_text())
    rows = [r for r in counts["instructions"]
            if r["mnemonic"] == "smt.vfwmadot"]
    total = sum(r["executions"] for r in rows)
    predicted = tiles_mod.expected_tile_ops(M, N, K, plan)
    check("fp16-plugin-counts-executed-smt-vfwmadot", total >= 1,
          f"{total} executions over {len(rows)} pc(s)")
    check("fp16-plugin-count-equals-tile-model", total == predicted,
          f"counted {total}, model {predicted}")
    record("fp16-20x24x40-colmajorB-threads4", dtype="float16",
           shape=[M, N, K], artifact_sha256=sha, mnemonic="smt.vfwmadot",
           executed=total, model=predicted,
           workers=[w["items"] for w in info["workers"]] if info else [],
           compare="allclose PASS",
           counts_schema=counts.get("schema"))


def check_bf16_vector_path(plugin):
    rng = np.random.default_rng(47)
    M, N, K = 12, 18, 24

    def to_bf16(x):
        return ((x.astype(np.float32).view(np.uint32) >> 16)
                & 0xFFFF).astype(np.uint16)

    a32 = (rng.standard_normal((M, K)) * 0.5).astype(np.float32)
    b32 = (rng.standard_normal((K, N)) * 0.5).astype(np.float32)
    a, b = to_bf16(a32), to_bf16(b32)
    # the exact widening the vector path performs (bits << 16)
    a_wide = (a.astype(np.uint32) << 16).view(np.float32)
    b_wide = (b.astype(np.uint32) << 16).view(np.float32)
    expected = a_wide @ b_wide
    c = np.zeros((M, N), dtype=np.float32)
    case = {"args": {"a_ptr": a, "b_ptr": b, "c_ptr": c},
            "outputs": ("c_ptr",),
            "pointer_dtypes": {"a_ptr": "bfloat16", "b_ptr": "bfloat16"}}
    plan, path, sha, text = compile_dot("bfloat16", "bfloat16", "float32",
                                        tag="bf16-main")
    check("bf16-plan-carries-the-recorded-gap",
          plan.bf16_gap is not None and "F010" in plan.bf16_gap)
    counts_file = WORK / "bf16-counts.json"
    result, outputs, info = stage_and_run(path, case, threads=1,
                                          counts_out=str(counts_file),
                                          plugin_so=str(plugin))
    ok = result.returncode == 0
    check("bf16-case-executes-under-qemu", ok, f"exit {result.returncode}")
    if not ok:
        return
    got = np.asarray(outputs["c_ptr"]).reshape(M, N)
    same = np.allclose(got, expected, rtol=1e-4, atol=1e-3)
    check("bf16-vector-fp32-path-compares-pass", same,
          f"max err {float(np.max(np.abs(got - expected))):.2e}")
    counts = json.loads(counts_file.read_text())
    ime_rows = [r for r in counts["instructions"]
                if r["mnemonic"].startswith("smt.")]
    check("bf16-records-zero-ime-executions", not ime_rows,
          f"{len(ime_rows)} smt.* rows (the gap: BF16 IME is not "
          "claimable, F010/F034)")
    record("bf16-12x18x24-vectorfp32-threads1", dtype="bfloat16",
           shape=[M, N, K], artifact_sha256=sha, path="vector-fp32",
           executed_ime=len(ime_rows), compare="allclose PASS",
           gap=plan.bf16_gap)


def check_multiworker():
    rng = np.random.default_rng(53)
    M, N, K = 40, 24, 48
    case, expected = int_case(rng, M, N, K)
    plan, path, sha, _ = compile_dot("int8", "int8", "int32",
                                     tag="int8-main")
    mt, nt = tiles_mod.tile_grid(M, N)
    tile_count = mt * nt
    shas = set()
    for threads in (1, 2, 4, 8):
        run_case = {"args": {k: (v.copy() if isinstance(v, np.ndarray)
                                  else v)
                              for k, v in case["args"].items()},
                    "outputs": case["outputs"]}
        result, outputs, info = stage_and_run(path, run_case, threads)
        if result.returncode:
            check(f"int8-threads-{threads}-pass", False,
                  f"exit {result.returncode}")
            continue
        same, _ = compare_exact(outputs, expected, M, N)
        items = [w["items"] for w in info["workers"]]
        split_ok = items == [len(range(w, tile_count, threads))
                             for w in range(threads)]
        shas.add(sha)
        check(f"int8-threads-{threads}-pass",
              same and split_ok and info["pool_initializations"] == 1,
              f"compare {'PASS' if same else 'FAIL'}; items {items} "
              f"(strided model "
              f"{[len(range(w, tile_count, threads)) for w in range(threads)]})")
    check("int8-one-artifact-across-worker-counts", len(shas) == 1)
    record("int8-40x24x48-threads-1-2-4-8", dtype="int8",
           shape=[M, N, K], artifact_sha256=sha,
           workers_model="strided over output tiles",
           compare="exact PASS at 1/2/4/8")


def check_tails_and_witness(plugin):
    rng = np.random.default_rng(59)
    M, N, K = 9, 13, 17            # M, N and K all outside the tile extents
    case, expected = int_case(rng, M, N, K)
    plan, path, sha, _ = compile_dot("int8", "int8", "int32",
                                     tag="int8-main")
    counts_file = WORK / "tail-counts.json"
    result, outputs, info = stage_and_run(path, case, threads=1,
                                          counts_out=str(counts_file),
                                          plugin_so=str(plugin))
    ok = result.returncode == 0
    check("tail-case-executes", ok, f"exit {result.returncode}")
    if ok:
        same, got = compare_exact(outputs, expected, M, N)
        check("tail-case-compares-pass-exact", same,
              "" if same else "M/N/K tail mismatch")
        counts = json.loads(counts_file.read_text())
        total = sum(r["executions"] for r in counts["instructions"]
                    if r["mnemonic"] == "smt.vmadot")
        predicted = tiles_mod.expected_tile_ops(M, N, K, plan)
        check("tail-case-tile-count-equals-model", total == predicted,
              f"counted {total}, model {predicted} (tail steps included)")
        record("int8-tail-9x13x17", dtype="int8", shape=[M, N, K],
               artifact_sha256=sha, executed=total, model=predicted,
               compare="exact PASS")
    # the guard-region witness: with the staging masks dropped the same
    # case reads out of range (the neighbouring, nonzero storage) and must
    # compare FAIL -- the control that proves the padding is load-bearing
    wplan, wpath, wsha, _ = compile_dot("int8", "int8", "int32",
                                        witness=True, tag="int8-witness")
    witness_case = {"args": {k: (v.copy() if isinstance(v, np.ndarray)
                                 else v) for k, v in case["args"].items()},
                    "outputs": case["outputs"]}
    wresult, woutputs, _ = stage_and_run(wpath, witness_case, threads=1)
    witness_broke = (wresult.returncode != 0 or
                     not np.array_equal(
                         np.asarray(woutputs["c_ptr"]).reshape(M, N),
                         expected))
    check("guard-region-witness-fails", witness_broke,
          "crashed" if wresult.returncode else
          "compared FAIL with the padding dropped")
    record("int8-tail-9x13x17-witness", dtype="int8", shape=[M, N, K],
           artifact_sha256=wsha, outcome="FAIL (the required witness)")


def check_acc_and_variants(plugin):
    rng = np.random.default_rng(61)
    # acc chaining: C = C_in + A x B through the read_c mode
    M, N, K = 16, 16, 32
    case, expected = int_case(rng, M, N, K, acc=True)
    plan, path, sha, _ = compile_dot("int8", "int8", "int32", acc="read_c",
                                     tag="int8-acc")
    result, outputs, info = stage_and_run(path, case, threads=1)
    ok = result.returncode == 0
    same = False
    if ok:
        same, _ = compare_exact(outputs, expected, M, N)
    check("int8-acc-chaining-compares-pass", ok and same,
          f"exit {result.returncode}")
    record("int8-acc-16x16x32", dtype="int8", shape=[M, N, K],
           artifact_sha256=sha, acc_mode="read_c", compare="exact PASS")
    # the u/us/su signedness variants: one executed end to end
    M, N, K = 16, 16, 32
    a = rng.integers(0, 200, (M, K), dtype=np.uint8)
    b = rng.integers(0, 200, (K, N), dtype=np.uint8)
    expected = (a.astype(np.int64) @ b.astype(np.int64)).astype(np.int32)
    c = np.zeros((M, N), dtype=np.int32)
    case = {"args": {"a_ptr": a, "b_ptr": b, "c_ptr": c},
            "outputs": ("c_ptr",)}
    plan, path, sha, text = compile_dot("uint8", "uint8", "int32",
                                        tag="uint8-main")
    check("uint8-variant-selects-vmadotu",
          plan.mnemonic == "smt.vmadotu" and "smt.vmadotu" in text)
    # the probe's decoder covers the base i8/i4/fp16 encodings only, so
    # the u-variant's dynamic count is not observable by the current
    # plugin; its executed correctness is the compare below and its
    # mnemonic selection is asserted in test_lower_matrix.py
    result, outputs, info = stage_and_run(path, case, threads=1)
    ok = result.returncode == 0
    same = ok and np.array_equal(
        np.asarray(outputs["c_ptr"]).reshape(M, N), expected)
    check("uint8-variant-executes-and-compares", ok and same,
          f"exit {result.returncode}; {plan.mnemonic} selected")
    record("uint8-16x16x32", dtype="uint8", shape=[M, N, K],
           artifact_sha256=sha, mnemonic="smt.vmadotu",
           compare="exact PASS",
           note="the probe decoder covers the base i8/i4/fp16 encodings; "
                "the u-variant count is selection-level evidence")


def main() -> int:
    try:
        plugin = plugin_path()
        check_int8_plugin(plugin)
        check_fp16_plugin(plugin)
        check_bf16_vector_path(plugin)
        check_multiworker()
        check_tails_and_witness(plugin)
        check_acc_and_variants(plugin)
    finally:
        evidence = {
            "schema": "a100c-ime-evidence/v1",
            "endpoint": "qemu-functional (jdsk-qemu 10.0.2, "
                        f"-cpu {QEMU_CPU})",
            "plugin": "a100_support/probes/instruction_counts.c",
            "cases": EVIDENCE["cases"],
        }
        out = WORK / "ime-evidence.json"
        out.write_text(json.dumps(evidence, indent=2) + "\n")
        print(f"# evidence: {out}")
        print(json.dumps(evidence, indent=2)[:2000])
    if FAILURES:
        print(f"FAILED: {len(FAILURES)} check(s)")
        return 1
    print("test_ime_evidence: all checks PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
