# Environment analysis — SpacemiT K3 A100, QEMU functional development

Task T001 (gate G0), acceptance scope `correctness_only`. All probes below were
executed on 2026-11-04 on this host inside `/home/i_yinzida/compiler-a100-experiment-001`
after `set -a; . ./.env; set +a`. Every command was bounded (`timeout`); no command
hung. Prep-time executed probe history is recorded in
`docs/compiler-agent/TOOLCHAIN_PROBES.json` and
`docs/compiler-agent/REFERENCE_ENVIRONMENT.json`; this task re-verified the
capabilities live and reproduces the relevant rows.

## Single source of truth

The project `.env` at the repository root is the single source of truth for the
installed tool paths. The project reads tool locations from it (and from
`a100_support/env.sh`, which derives the same `A100_PREFIX`):

| Variable | Value |
|---|---|
| `A100_PREFIX` | `/home/i_yinzida/.local/opt/a100` |
| `A100_TOOLCHAIN` | `/home/i_yinzida/.local/opt/a100/toolchain-1.1.2` |
| `A100_SYSROOT` | `/home/i_yinzida/.local/opt/a100/toolchain-1.1.2/sysroot` |
| `A100_CROSS_PREFIX` | `/home/i_yinzida/.local/opt/a100/toolchain-1.1.2/bin/riscv64-unknown-linux-gnu-` |
| `A100_QEMU` | `/home/i_yinzida/.local/opt/a100/jdsk-qemu-10.0.2/bin/qemu-riscv64` |
| `A100_QEMU_CPU` | `max,vlen=1024,elen=64,vext_spec=v1.0` |
| `A100_REFERENCE_PYTHON` | `/home/i_yinzida/.local/opt/a100/venvs/triton-cpu/bin/python` |
| `PYTHONPATH` | project root : `ops/harness` : workflow home |
| `A100_PUBLIC_REFERENCE_CACHE` | `/home/i_yinzida/.cache/a100-prep/public-reference-cache-a100-zcode-002` |
| `A100_NO_PYTHON_IMAGE` | `a100-qemu-functional:compiler-a100-experiment-001` |
| `COMPILER_WORKFLOW_ATTACK_BROKER` | `/home/i_yinzida/.local/share/a100-prep/experiments/compiler-a100-experiment-001/broker.sh` |

Note: `.env` declares **no measurement/profiling tool and no benchmark workload
entrypoint**. Under `correctness_only` none is required; the required correctness
observation capabilities (dynamic instruction counts, multi-worker activity) were
probed instead (below).

## Capability classification

| # | Capability | Tool (resolved path) | Classification |
|---|---|---|---|
| 1 | Cross-compile (cc) | `.../toolchain-1.1.2/bin/riscv64-unknown-linux-gnu-gcc` 14.3.0 | present + usable |
| 2 | Assemble (as) | `.../toolchain-1.1.2/bin/riscv64-unknown-linux-gnu-as` (Binutils 2.43.1.20250119) | present + usable |
| 3 | Link (ld) | `.../toolchain-1.1.2/bin/riscv64-unknown-linux-gnu-ld` (Binutils 2.43.1.20250119) | present + usable |
| 4 | Object inspection | `.../toolchain-1.1.2/bin/riscv64-unknown-linux-gnu-objdump` (Binutils 2.43.1.20250119) | present + usable |
| 5 | Sysroot (libc, dynamic loader) | `.../toolchain-1.1.2/sysroot` | present + usable |
| 6 | QEMU execution endpoint | `.../jdsk-qemu-10.0.2/bin/qemu-riscv64` 10.0.2, `-cpu max,vlen=1024,elen=64,vext_spec=v1.0` | present + usable |
| 7 | RVV 1.0 VLEN=1024 under declared CPU model | declared `A100_QEMU_CPU` | present + usable |
| 8 | Native runtime transport | `a100_support/native_io.py` + `a100_support/native_bundle.c` + `a100_support/run-riscv.sh` | present + usable |
| 9 | Dynamic instruction observation | QEMU 10 plugin API + `a100_support/probes/instruction_counts.c` | present + usable |
| 10 | Multi-worker execution/observation | `a100_support/probes/threads.c` persistent pool, 1/2/4/8 | present + usable |
| 11 | IME matrix instructions (int8/int4/fp16) | `smt.vmadot` / `smt.vfwmadot` under declared QEMU | present + usable |
| 12 | BF16 IME format selection | pinned QEMU 10.0.2 | present + unusable (known gap, see below) |
| 13 | MCPM control CSR from userspace | pinned QEMU 10.0.2 | present + unusable (userspace access denied) |
| 14 | SpacemiT LLVM | `/home/i_yinzida/.local/opt/a100/llvm-spacemit-f6ded0be` | present + unusable (host glibc too old; not on the declared build path) |
| 15 | x86 Triton CPU reference env | `.../venvs/triton-cpu/bin/python` 3.12.16, triton 3.8.0, numpy 2.5.4, torch 2.15.0+cpu | present + usable |
| 16 | Reference compiler-rt support | `.../reference-support/liba100_reference_support.so` | present + usable (loaded by the reference probe) |
| 17 | Host Python driver | `python3` 3.10.12 + `.env` PYTHONPATH | present + usable |
| 18 | Public reference cache | `A100_PUBLIC_REFERENCE_CACHE` directory | present (has content) |
| 19 | Attack broker script | `COMPILER_WORKFLOW_ATTACK_BROKER` | present (executable, controller-owned) |
| 20 | No-Python execution image | docker image `a100-qemu-functional:compiler-a100-experiment-001` | present + usable (docker CLI works; round trip not yet exercised, see A002) |

## Probe evidence (exact commands and outputs)

Load the environment first: `set -a; . ./.env; set +a` (all commands below assume it).

### Tool versions

```
$ ${A100_CROSS_PREFIX}gcc --version | head -1
riscv64-unknown-linux-gnu-gcc (g56971dcbea2) 14.3.0
$ ${A100_CROSS_PREFIX}as --version | head -1
GNU assembler (GNU Binutils) 2.43.1.20250119
$ ${A100_CROSS_PREFIX}ld --version | head -1
GNU ld (GNU Binutils) 2.43.1.20250119
$ ${A100_CROSS_PREFIX}objdump --version | head -1
GNU objdump (GNU Binutils) 2.43.1.20250119
$ $A100_QEMU --version | head -1
qemu-riscv64 version 10.0.2
$ python3 --version
Python 3.10.12
$ $A100_REFERENCE_PYTHON --version
Python 3.12.16
```

These match `docs/compiler-agent/TOOLCHAIN_PROBES.json` `tools` and
`docs/compiler-agent/REFERENCE_ENVIRONMENT.json` (python 3.12.16, triton 3.8.0,
numpy 2.5.4, torch 2.15.0+cpu).

### Sysroot

```
$ ls $A100_SYSROOT/lib/libc.so.6 $A100_SYSROOT/lib/ld-linux-riscv64-lp64d.so.1
/home/i_yinzida/.local/opt/a100/toolchain-1.1.2/sysroot/lib/libc.so.6
/home/i_yinzida/.local/opt/a100/toolchain-1.1.2/sysroot/lib/ld-linux-riscv64-lp64d.so.1
```

### End-to-end smoke 1 — C program, cross gcc, declared QEMU endpoint (acceptance[1])

Source `a100_support/build/smoke_c.c`: `printf("A100-C-SMOKE-OK\n"); return 0;`

```
$ ${A100_CROSS_PREFIX}gcc -O2 -Wall -march=rv64gcv -mabi=lp64d \
    a100_support/build/smoke_c.c -o a100_support/build/smoke_c         # exit 0
$ ${A100_CROSS_PREFIX}objdump -f a100_support/build/smoke_c | head -2
a100_support/build/smoke_c:     file format elf64-littleriscv
architecture: riscv:rv64, flags 0x00000112:
$ timeout 60 $A100_QEMU -L $A100_SYSROOT -cpu "$A100_QEMU_CPU" ./a100_support/build/smoke_c
A100-C-SMOKE-OK
exit=0
```

### End-to-end smoke 2 — hand-written assembly, as + ld, declared QEMU endpoint

Source `a100_support/build/smoke_asm.S`: raw `write`/`exit` syscalls from `_start`
(no libc). This is the path the compiler's program-level assembly emitter will use.

```
$ ${A100_CROSS_PREFIX}as -march=rv64gcv a100_support/build/smoke_asm.S -o a100_support/build/smoke_asm.o   # exit 0
$ ${A100_CROSS_PREFIX}ld a100_support/build/smoke_asm.o -o a100_support/build/smoke_asm                     # exit 0
$ timeout 60 $A100_QEMU -L $A100_SYSROOT -cpu "$A100_QEMU_CPU" ./a100_support/build/smoke_asm
A100-ASM-SMOKE-OK
exit=42                      # the guest exit code is preserved exactly
```

### End-to-end smoke 3 — RVV 1.0 VLEN=1024 under the declared CPU model

Source `a100_support/build/smoke_rvv.S`: reads `vlenb`, requires 128 (VLEN=1024
bits), then executes `vsetvli/vmv.v.x/vadd.vv/vmv.x.s` and requires lane 0 == 42;
exits 0 only if both hold.

```
$ ${A100_CROSS_PREFIX}as -march=rv64gcv a100_support/build/smoke_rvv.S -o a100_support/build/smoke_rvv.o    # exit 0
$ ${A100_CROSS_PREFIX}ld a100_support/build/smoke_rvv.o -o a100_support/build/smoke_rvv                     # exit 0
$ timeout 60 $A100_QEMU -L $A100_SYSROOT -cpu "$A100_QEMU_CPU" ./a100_support/build/smoke_rvv
exit=0
# control: same binary under a different CPU model must fail the check
$ timeout 60 $A100_QEMU -L $A100_SYSROOT -cpu max,vlen=256,elen=64,vext_spec=v1.0 ./a100_support/build/smoke_rvv
exit=1
```

The control fails as expected, so the check observes the CPU model rather than
passing vacuously.

### Native runtime transport (capability 8)

Built exactly as `a100_support/probes.py` does (into the gitignored
`a100_support/build/`):

```
$ ${A100_CROSS_PREFIX}gcc -O2 -Wall -Wextra -march=rv64gcv -mabi=lp64d \
    -I a100_support a100_support/probes/io_fixture.c a100_support/native_bundle.c \
    -o a100_support/build/io_fixture                                                # exit 0
```

Probe `a100_support/build/transport_probe.py` (host python3, `.env` PYTHONPATH)
packs a case with `a100_support.native_io.pack_case`, launches
`a100_support/run-riscv.sh a100_support/build/io_fixture <dir>/bundle.bin <mode>`
(QEMU, declared CPU model), then unpacks with `unpack_outputs` and compares:

```
$ timeout 300 python3 a100_support/build/transport_probe.py
alias: returncode 0 | {"fixture":"native-io","passed":true}
alias comparison: PASS        # strided views, shared storage, guest pointer relocation
bf16: returncode 0 | {"fixture":"native-io","passed":true}
bf16 comparison: PASS         # bfloat16 value storage + host-side output decoding
```

This exercises the complete transport the compiler must integrate with
(`A100_COMPILER_FACTORY` is not yet set; `a100_support.native_device.make_device`
correctly refuses until the compiler exists — no reference fallback).

### Dynamic instruction observation (capability 9)

```
$ gcc -O2 -Wall -Wextra -shared -fPIC -pthread \
    -I$A100_PREFIX/jdsk-qemu-10.0.2/include \
    -I$A100_PREFIX/host-runtime-bookworm/include/glib-2.0 \
    -I$A100_PREFIX/host-runtime-bookworm/lib/glib-2.0/include \
    a100_support/probes/instruction_counts.c -o a100_support/build/instruction_counts.so   # exit 0
$ ${A100_CROSS_PREFIX}gcc -O2 -Wall -Wextra -march=rv64gcv -mabi=lp64d -pthread \
    a100_support/probes/matrix.c a100_support/probes/vector_matrix.S \
    -o a100_support/build/matrix_probe                                                   # exit 0
$ timeout 90 $A100_QEMU -L $A100_SYSROOT -cpu "$A100_QEMU_CPU" \
    -plugin a100_support/build/instruction_counts.so,out=a100_support/build/ime-int8-counts.json \
    a100_support/build/matrix_probe int8
{"probe":"int8","passed":true,"vlenb":128,"mcpm_control":"default-no-userspace-access"}
exit=0
$ cat a100_support/build/ime-int8-counts.json
{"schema":"qemu-dynamic-instructions/v1","instructions":[{"mnemonic":"smt.vmadot","operand_format":"i8","pc":68508,"executions":1}]}
# control: the same plugin on a binary with no matrix instructions counts nothing
$ timeout 60 $A100_QEMU -L $A100_SYSROOT -cpu "$A100_QEMU_CPU" \
    -plugin a100_support/build/instruction_counts.so,out=a100_support/build/smoke-counts.json \
    a100_support/build/smoke_asm        # prints A100-ASM-SMOKE-OK, exit=42
$ cat a100_support/build/smoke-counts.json
{"schema":"qemu-dynamic-instructions/v1","instructions":[]}
```

The int8 row reproduces the prep-time `TOOLCHAIN_PROBES.json` matrix int8 entry
(`EXECUTED_AND_COMPARED_PASS`, `smt.vmadot` executions 1) with a fresh execution.

### Multi-worker execution/observation (capability 10)

```
$ ${A100_CROSS_PREFIX}gcc -O2 -Wall -Wextra -march=rv64gcv -mabi=lp64d -pthread \
    a100_support/probes/threads.c a100_support/probes/vector_matrix.S \
    -o a100_support/build/threads_probe                                  # exit 0
$ for n in 1 2 4 8; do timeout 120 $A100_QEMU -L $A100_SYSROOT -cpu "$A100_QEMU_CPU" \
    a100_support/build/threads_probe $n; done     # each exit=0
```

Parsed results (fresh run, JSON saved under `a100_support/build/threads-<n>.json`):

| threads | passed | distinct guest_tids | items sum | pool initializations |
|---|---|---|---|---|
| 1 | true | 1 | 32771 | 1 |
| 2 | true | 2 | 32771 | 1 |
| 4 | true | 4 | 32771 | 1 |
| 8 | true | 8 | 32771 | 1 |

Worker units are QEMU guest threads, **not** physical A100 cores (see A001).
This reproduces the prep-time `threads` rows of `TOOLCHAIN_PROBES.json`.

### IME matrix instructions and the BF16 gap (capabilities 11–12)

Fresh int8 probe above: passed. Fresh bf16 probe (same command with `bf16`):

```
$ timeout 90 $A100_QEMU -L $A100_SYSROOT -cpu "$A100_QEMU_CPU" \
    -plugin a100_support/build/instruction_counts.so,out=a100_support/build/ime-bf16-counts.json \
    a100_support/build/matrix_probe bf16
{"probe":"bf16","passed":false,"vlenb":128,"mcpm_control":"default-no-userspace-access"}
exit=1
$ cat a100_support/build/ime-bf16-counts.json
{"schema":"qemu-dynamic-instructions/v1","instructions":[{"mnemonic":"smt.vfwmadot","operand_format":"MCPM-selected-float16","pc":68582,"executions":1}]}
```

So the BF16 IME probe still fails on the pinned emulator exactly as recorded at
prep time (`TOOLCHAIN_PROBES.json`: bf16 `UNSUPPORTED_OR_FAILED`, returncode 1;
the executed `smt.vfwmadot` selects the float16 operand format). The gap is
current: **the pinned emulator's BF16 IME format selection has not passed; FP16
or ordinary vector success cannot prove BF16 IME execution.** BF16 cases must be
retained and the gap recorded separately (chip.md UNKNOWN). Prep-time rows int4
and fp16 are `EXECUTED_AND_COMPARED_PASS` in `TOOLCHAIN_PROBES.json`.

### MCPM control CSR (capability 13)

The recorded csr probe in `TOOLCHAIN_PROBES.json` returned `-4` (killed by
signal) with zero matrix instruction executions, and every fresh matrix probe
above reports `"mcpm_control":"default-no-userspace-access"`: the MCPM control
CSR is not accessible from userspace under this pinned QEMU.

### SpacemiT LLVM (capability 14)

```
$ timeout 20 /home/i_yinzida/.local/opt/a100/llvm-spacemit-f6ded0be/bin/llc --version
/home/i_yinzida/.local/opt/a100/llvm-spacemit-f6ded0be/bin/llc: /lib/x86_64-linux-gnu/libc.so.6:
version `GLIBC_2.38' not found (required by .../llc)
version `GLIBC_2.36' not found (required by .../llc)
```

Same error for `opt`, `llvm-mc`, `llvm-as`, `llvm-dis`, `ld.lld`; the package
contains no `clang` binary. Host glibc is older than the package requires, so the
SpacemiT LLVM tools are **present + unusable on this host**. This is not a
blocker: the declared build path (chip.md section 5, `.env`, `lock.json`) is the
cross GCC/binutils toolchain, which is present + usable. `A100_LLVM` is exported
by `a100_support/env.sh` but is not declared in `.env`; nothing in the declared
build/execution path requires it.

### x86 Triton CPU reference environment (capability 15)

```
$ timeout 420 a100_support/run-reference.sh a100_support/build/reference_probe.py
versions: python-ok triton 3.8.0 | numpy 2.5.4 | torch 2.15.0+cpu
device: x86-triton-cpu-reference | threads: 1
masked vector-add comparison: PASS
exit=0
```

The probe compiles and runs a Triton kernel (1000 elements, BLOCK 128 — the tail
is masked) through `TritonCpuReferenceDevice` and `a100_support/run-reference.sh`
(the declared launch path: `TRITON_DEFAULT_BACKEND=cpu`, `TRITON_INTERPRET=0`,
`TRITON_F32_DEFAULT=ieee`, `TRITON_CPU_FAST_MATH=0`, single reference thread).
Versions match `REFERENCE_ENVIRONMENT.json`. Purpose: x86 question validation
only; it never substitutes for candidate target execution.

### Host Python driver (capability 17)

```
$ timeout 120 python3 -m compiler_agent --root . --json status | head -3     # exit 0
{
  "project": "compiler-a100-experiment-001",
  ...
$ timeout 120 python3 -c "import opslib.device, a100_support.native_device, a100_support.native_io, a100_support.reference_device, a100_support.probes; print('imports ok')"
imports ok
$ timeout 120 python3 -c "import numpy, triton, sys; print(sys.version.split()[0], '| numpy', numpy.__version__, '| triton', triton.__version__)"
3.10.12 | numpy 2.2.6 | triton 3.8.0
```

Host python3 3.10.12 has numpy 2.2.6 and triton 3.8.0 (user site), runs the
workflow engine and imports the ops harness plus the transport. Host python3 has
no `pytest` (the a100_support test-suite runs are not required by this task and
were not executed; the equivalent transport behavior was probed directly above).

### Auxiliary declared paths (capabilities 18–20)

```
$ ls -d $A100_PUBLIC_REFERENCE_CACHE
/home/i_yinzida/.cache/a100-prep/public-reference-cache-a100-zcode-002     # contains cached entries
$ ls -la $COMPILER_WORKFLOW_ATTACK_BROKER
-rwx------ 1 i_yinzida i_yinzida 311 Nov  4 10:44 .../broker.sh           # present, controller-owned
$ timeout 60 docker image inspect a100-qemu-functional:compiler-a100-experiment-001 --format '{{.Id}}'
sha256:abe85106d90d6ede14eeebe0d501e5e1b6b81101142f56dc5286463b2db7e49e
```

## Correctness-only scope notes

- No timing, speedup, benchmark rate or performance measurement was recorded or
  required by this task. The `phase*_interval_ns` fields inside the threads probe
  JSON are the probe's own worker-activity intervals used to observe overlapping
  useful work; no performance conclusion is drawn from them.
- `.env` declares no measurement/profiling tool and no benchmark workload
  entrypoint; none is required under `correctness_only`.
- Required correctness observation capabilities were verified instead: dynamic
  instruction counts (plugin, with an empty-count control) and multi-worker
  activity (distinct guest tids, full item coverage, one pool init).

## Assumptions

- **A001 — no physical A100 board in this environment.** All target execution is
  the pinned QEMU functional emulator; QEMU guest threads do not establish
  physical A100 core identities, topology, affinity, cache behaviour or timing
  (chip.md UNKNOWN). Validation: on-board discovery during the porting step.
  Risk: any topology/timing conclusion drawn from QEMU would be wrong.
- **A002 — containerized no-Python execution round trip not yet exercised.** The
  image is present and the docker CLI works, but
  `a100_support/run-candidate-container.sh` has not been run with a real
  generated `operator_exec` (no compiler output exists yet). Validation: run it
  with the first generated operator executable. Risk: low (image present;
  candidate path untested).

## Recorded facts

The Facts/Assumptions for this analysis are recorded in
`docs/compiler-agent/PROJECT_STATE.json`. Each fact's source names the probe
command recorded above.

| ID | Statement (abridged) | Confidence |
|---|---|---|
| F001 | `.env` is the single source of truth for tool paths; no measurement stack declared | EMPIRICAL |
| F002 | Cross gcc 14.3.0 present + usable (C smoke built and run) | RUNTIME_PROBE |
| F003 | Cross as/ld/objdump binutils 2.43.1.20250119 present + usable (asm smoke) | RUNTIME_PROBE |
| F004 | Sysroot present + usable (libc + lp64d loader, dynamic smoke) | RUNTIME_PROBE |
| F005 | QEMU endpoint 10.0.2 with declared CPU model present + usable (3 smokes) | RUNTIME_PROBE |
| F006 | RVV 1.0 VLEN=1024 under declared CPU model (vlenb=128, control fails) | RUNTIME_PROBE |
| F007 | Native runtime transport round trip PASS (alias/relocation, bf16) | RUNTIME_PROBE |
| F008 | Dynamic instruction observation plugin usable (counts + empty control) | RUNTIME_PROBE |
| F009 | IME int8 executed and compared PASS (int4/fp16 recorded at prep time) | RUNTIME_PROBE |
| F010 | BF16 IME format selection gap: probe fails, remains unverified | RUNTIME_PROBE |
| F011 | MCPM control CSR not userspace-accessible under pinned QEMU | RUNTIME_PROBE |
| F012 | SpacemiT LLVM present + unusable (host glibc; not on declared build path) | RUNTIME_PROBE |
| F013 | x86 Triton CPU reference environment usable (masked vector-add PASS) | RUNTIME_PROBE |
| F014 | Host Python driver 3.10.12 usable (engine + harness + transport imports) | RUNTIME_PROBE |
| F015 | Auxiliary declared paths present (cache, broker, no-Python image) | RUNTIME_PROBE |

| ID | Assumption | Risk |
|---|---|---|
| A001 | No physical A100 board reachable; QEMU guest threads are not board topology/timing | high |
| A002 | Containerized no-Python candidate round trip not yet exercised with a real artifact | low |
