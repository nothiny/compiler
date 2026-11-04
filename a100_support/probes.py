#!/usr/bin/env python3
"""Build and execute environment probes, preserving unsupported-path evidence."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import resource
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
PREFIX = Path(os.environ.get('A100_PREFIX', Path.home()/'.local/opt/a100'))
BUILD = ROOT/'a100_support/build'
STATE = ROOT/'docs/compiler-agent'
CPU = 'max,vlen=1024,elen=64,vext_spec=v1.0'


def no_core():
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))


def run(command, **kwargs):
    return subprocess.run(list(map(str, command)), check=True, **kwargs)


def build():
    BUILD.mkdir(parents=True, exist_ok=True)
    gcc = PREFIX/'toolchain-1.1.2/bin/riscv64-unknown-linux-gnu-gcc'
    common = [gcc, '-O2', '-Wall', '-Wextra', '-march=rv64gcv', '-mabi=lp64d']
    probe = ROOT/'a100_support/probes'
    for name in ('matrix', 'threads'):
        run([*common, '-pthread', probe/(name+'.c'), probe/'vector_matrix.S', '-o', BUILD/(name+'_probe')])
    run([*common, '-I'+str(ROOT/'a100_support'), probe/'io_fixture.c',
         ROOT/'a100_support/native_bundle.c', '-o', BUILD/'io_fixture'])
    runtime = PREFIX/'host-runtime-bookworm'
    run(['gcc', '-O2', '-Wall', '-Wextra', '-shared', '-fPIC', '-pthread',
         '-I'+str(PREFIX/'jdsk-qemu-10.0.2/include'),
         '-I'+str(runtime/'include/glib-2.0'), '-I'+str(runtime/'lib/glib-2.0/include'),
         probe/'instruction_counts.c', '-o', BUILD/'instruction_counts.so'])
    run([*common, '-nostdlib', '-ffreestanding', '-fno-builtin', '-fno-pie', '-no-pie',
         '-march=rv64gcv_zfh',
         '-mcmodel=medany', '-static', '-Wl,-T,'+str(probe/'bare.ld'),
         probe/'bare_start.S', probe/'bare_matrix.c', probe/'vector_matrix.S',
         '-o', BUILD/'bare_matrix_probe'])


def execute():
    qemu = PREFIX/'jdsk-qemu-10.0.2/bin/qemu-riscv64'
    sysroot = PREFIX/'toolchain-1.1.2/sysroot'
    base = [qemu, '-L', sysroot, '-cpu', CPU]
    rows = []
    for kind in ('int8', 'int4', 'fp16', 'bf16', 'csr'):
        counts = BUILD/('ime-'+kind+'-counts.json')
        counts.unlink(missing_ok=True)
        command = [*base, '-plugin', str(BUILD/'instruction_counts.so')+',out='+str(counts),
                   BUILD/'matrix_probe', kind]
        result = subprocess.run(list(map(str, command)), capture_output=True, text=True,
                                timeout=30, preexec_fn=no_core)
        observed = json.loads(counts.read_text()) if counts.is_file() else {}
        count = sum(r['executions'] for r in observed.get('instructions', []))
        passed = result.returncode == 0 and kind != 'csr' and count > 0
        rows.append(dict(probe=kind, command=list(map(str,command)), returncode=result.returncode,
                         stdout=result.stdout, stderr=result.stderr,
                         matrix_instruction_executions=count, instruction_counts=observed,
                         status='EXECUTED_AND_COMPARED_PASS' if passed else 'UNSUPPORTED_OR_FAILED'))
    threads = []
    for count in (1, 2, 4, 8):
        result = run([*base, BUILD/'threads_probe', str(count)], capture_output=True, text=True, timeout=30)
        row=json.loads(result.stdout)
        assert len({w['guest_tid'] for w in row['workers']})==count
        assert sum(w['items'] for w in row['workers'])==32771
        for worker in row['workers']:
            assert worker['items']>0
            assert worker['phase1_interval_ns'][0]<=worker['phase1_interval_ns'][1]
            assert worker['phase2_interval_ns'][0]<=worker['phase2_interval_ns'][1]
        row.pop('samples_ns', None)
        threads.append(row)
    tools = {}
    cross = PREFIX/'toolchain-1.1.2/bin/riscv64-unknown-linux-gnu-'
    for name, path in [('qemu', qemu), *[(name, str(cross)+name) for name in ('gcc','as','ld','objdump')]]:
        tools[name] = subprocess.check_output([path, '--version'], text=True).splitlines()[0]
    artifacts = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in BUILD.iterdir() if p.is_file() and p.name in ('instruction_counts.so', 'matrix_probe', 'threads_probe', 'io_fixture', 'bare_matrix_probe')}
    report = dict(schema='a100-environment-probes/v1', cpu=CPU, tools=tools, artifacts=artifacts,
                  matrix=rows, threads=threads, compiler_results=False, board_performance_measured=False,
                  bf16_note='This pinned emulator does not expose a working BF16 IME mode in these probes; retain BF16 cases and record the validation gap.')
    (STATE/'TOOLCHAIN_PROBES.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(tools=tools, matrix={r['probe']:r['status'] for r in rows},
                          thread_configurations_passed=len(threads)), indent=2))
    if not all(r['status']=='EXECUTED_AND_COMPARED_PASS' for r in rows[:3]):
        raise SystemExit('Required int8/int4/fp16 environment probe regressed')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--build-only', action='store_true')
    args = parser.parse_args()
    build()
    if not args.build_only:
        execute()
