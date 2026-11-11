"""Diagnostic adapter: unchanged compiler files, comment-only MIR identities.

PC-level subtraction is restricted to the stable non-PIE program image.
Whole-process categories are subtracted as aggregate counters, so relocated
shared-library PCs never masquerade as steady-state work.
"""
from __future__ import annotations

import argparse
import bisect
from collections import Counter
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time
import warnings

ROOT = Path(os.environ.get('A100_REVIEW_ROOT', Path(__file__).resolve().parents[1])).resolve()
ADAPTER_SHA256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
for raw in (ROOT / '.env').read_text().splitlines():
    key, sep, value = raw.partition('=')
    if sep:
        os.environ[key] = value
os.environ.update(PYTHONDONTWRITEBYTECODE='1', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1',
                  XDG_CACHE_HOME=str(ROOT / 'host-cache'), TRITON_CACHE_DIR=str(ROOT / 'triton-cache'))
sys.path[:0] = [str(ROOT), str(ROOT / 'ops/harness'), str(ROOT / 'tools/profiling')]
warnings.filterwarnings('ignore')

from a100c.driver import CompileOptions, compiler_revision
from a100c.factory import FactoryCompiler
from a100c.backend import emit as emit_mod
from a100_support.native_device import NativeExecutableDevice
from a100_support.native_io import unpack_outputs
from opslib.compare import compare_case
from insn_manifest import Manifest, origin_of_opcode
from a100c.passes import mir_optimize
sys.path.insert(0, str(Path(__file__).resolve().parent))

LAST_MAP = {}
ORIGINAL_EMIT = emit_mod.emit_assembly
ORIGINAL_COMMENT = emit_mod._Emitter.comment
ORIGINAL_MIR_RUN = mir_optimize.run
ORIGINAL_OPTIONS_IDENTITY = CompileOptions.identity_part


def _options_identity(self):
    base = ORIGINAL_OPTIONS_IDENTITY(self)
    return base + ',diagnostic-pristine-' + ADAPTER_SHA256[:16]


CompileOptions.identity_part = _options_identity


def _jsonable(value):
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return repr(value)


def _annotated_emit(module, *args, **kwargs):
    global LAST_MAP
    identities, records = {}, {}
    for fn in module.functions:
        for block in fn.blocks:
            for op in block.ops:
                uid = len(identities)
                identities[id(op)] = uid
                records[str(uid)] = {'index': op.index, 'opcode': op.opcode,
                                     'block': block.name, 'function': fn.name,
                                     'attrs': _jsonable(op.attrs), 'loc': str(op.loc),
                                     'result_types': [repr(r.type) for r in op.results]}
    def comment(self, op):
        return ORIGINAL_COMMENT(self, op) + f' [miruid={identities[id(op)]}]'
    emit_mod._Emitter.comment = comment
    try:
        result = ORIGINAL_EMIT(module, *args, **kwargs)
    finally:
        emit_mod._Emitter.comment = ORIGINAL_COMMENT
    LAST_MAP = records
    return result


emit_mod.emit_assembly = _annotated_emit


def stable_map(entry, executable, directory):
    manifest = Manifest(entry)
    sparse, region, diagnostics = manifest.build_pc_map(executable, directory)
    # Expand source-line ranges over actual instruction starts. This includes
    # every instruction of a multi-instruction li or relaxed branch.
    prefix = os.environ['A100_CROSS_PREFIX']
    disassembly = subprocess.check_output([prefix + 'objdump', '-d', '--no-show-raw-insn', str(executable)], text=True)
    (directory / 'disassembly.txt').write_text(disassembly)
    pcs = []
    for line in disassembly.splitlines():
        match = re.match(r'^\s*([0-9a-f]+):\s+(\S+)', line)
        if match and region[0] <= int(match.group(1), 16) < region[1]:
            pcs.append(int(match.group(1), 16))
    starts = sorted(sparse)
    uid_map = json.loads((entry / 'diagnostic.mir-uids.json').read_text())
    mapping = {}
    for pc in pcs:
        k = bisect.bisect_right(starts, pc) - 1
        if k < 0:
            raise RuntimeError('instruction precedes first source mapping')
        record = dict(sparse[starts[k]])
        match = re.search(r'\[miruid=(\d+)\]', record['text'])
        uid = match.group(1) if match else None
        if uid is not None:
            current = uid_map[uid]
            record.update(current, uid=int(uid), origin=origin_of_opcode(current['opcode']))
        else:
            record.update(opcode=None, origin='frame/service', block='program-services', uid=None)
        record['expanded_from_pc'] = starts[k]
        mapping[pc] = record
    diagnostics.update(actual_instruction_starts=len(pcs), source_start_rows=len(starts),
                       uid_mapping='live MIR object identity captured before emission; no positional inference')
    return mapping, region, diagnostics


def categories(counts):
    result = Counter()
    for row in counts['instructions']:
        result[row['category']] += row['executions']
    return result


def run_one(executable, pristine_bundle, directory, threads, repeats, case):
    directory.mkdir(parents=True, exist_ok=True)
    shutil.copytree(pristine_bundle, directory / 'bundle', dirs_exist_ok=True)
    counts_path = directory / 'counts.json'
    command = [os.environ['A100_QEMU'], '-L', os.environ['A100_SYSROOT'],
               '-cpu', os.environ['A100_QEMU_CPU'], '-plugin',
               f'{ROOT / "tools/profiling/full_instruction_counts.so"},out={counts_path}',
               str(executable), '--bundle', str(directory / 'bundle/bundle.bin'),
               '--threads', str(threads), '--repeats', str(repeats)]
    if os.environ.get('A100_QEMU_LOADER'):
        command = [os.environ['A100_QEMU_LOADER'], '--library-path', os.environ['A100_QEMU_HOST_LIB'], *command]
    start = time.monotonic()
    result = subprocess.run(command, capture_output=True, text=True, timeout=180)
    elapsed = time.monotonic() - start
    (directory / 'stdout.log').write_text(result.stdout)
    (directory / 'stderr.log').write_text(result.stderr)
    if result.returncode:
        raise RuntimeError(f'QEMU exit {result.returncode}: {result.stderr[-500:]}')
    verdict = compare_case(case, unpack_outputs(directory / 'bundle'))
    if verdict.get('status')!='PASS':
        raise RuntimeError('original comparison failed: '+repr(verdict))
    runtime = json.loads(result.stdout.strip().splitlines()[-1])
    if not runtime.get('repeats_all_equal'):
        raise RuntimeError('repeat consistency failed')
    counts = json.loads(counts_path.read_text())
    if sum(row['executions'] for row in counts['instructions']) != counts['total_dynamic_instructions']:
        raise RuntimeError('raw counter checksum failed')
    record = {'command': command, 'raw_sha256': hashlib.sha256(counts_path.read_bytes()).hexdigest(),
              'raw_path': str(counts_path), 'runtime': runtime, 'comparison': verdict,
              'elapsed_qemu_wall_s_auxiliary_only': elapsed, 'repeats': repeats}
    (directory / 'run.json').write_text(json.dumps(record, indent=2))
    return counts, record


def collect(case_record, variant, threads, repeats, pairs, out_root):
    name, rel, shape, dtype = (case_record[k] for k in ['name', 'operator', 'shape', 'dtype'])
    directory = out_root / variant / f'{name}-t{threads}'
    directory.mkdir(parents=True, exist_ok=True)
    print(json.dumps({'starting': name, 'variant': variant, 'threads': threads}), flush=True)
    spec = importlib.util.spec_from_file_location('profile_' + name.replace('-', '_'), ROOT / 'ops' / rel)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    case = module.make_case(shape=tuple(shape), dtype=dtype, seed=30)
    options = CompileOptions(cache_dir=str(ROOT / 'annotated-cache'))
    compiler = FactoryCompiler(options=options)
    staged = NativeExecutableDevice(compiler, threads).stage_case(case)
    entry = Path(staged.artifact.executable).parent
    map_path = entry / 'diagnostic.mir-uids.json'
    if not map_path.exists():
        if not LAST_MAP:
            raise RuntimeError('cache entry exists without diagnostic mapping')
        map_path.write_text(json.dumps(LAST_MAP, indent=2))
    pristine = directory / 'pristine'
    shutil.copytree(staged.directory, pristine, dirs_exist_ok=True)
    pc_map, region, diagnostics = stable_map(entry, staged.artifact.executable, directory / 'asm')
    measurements = []
    for pair in range(pairs):
        a, ar = run_one(staged.artifact.executable, pristine, directory / f'pair-{pair}/r1', threads, 1, case)
        b, br = run_one(staged.artifact.executable, pristine, directory / f'pair-{pair}/r2', threads, 1 + repeats, case)
        am = {r['pc']: r for r in a['instructions']}
        bm = {r['pc']: r for r in b['instructions']}
        signed_cat = {k: (categories(b)[k] - categories(a)[k]) / repeats
                      for k in set(categories(a)) | set(categories(b))}
        total = (b['total_dynamic_instructions'] - a['total_dynamic_instructions']) / repeats
        if abs(sum(signed_cat.values()) - total) > 1e-6:
            raise RuntimeError('aggregate category difference does not sum to total')
        by_origin, by_block, by_mnemonic, by_pc = Counter(), Counter(), Counter(), {}
        negatives = []
        for pc in sorted(set(am) | set(bm)):
            if not region[0] <= pc < region[1]:
                continue
            delta = (bm.get(pc, {}).get('executions', 0) - am.get(pc, {}).get('executions', 0)) / repeats
            if not delta:
                continue
            if pc not in pc_map:
                raise RuntimeError(f'executed program PC missing mapping: {pc:#x}')
            if delta < 0:
                negatives.append([pc, delta])
            record = pc_map[pc]
            by_origin[record['origin']] += delta
            by_block[record['block']] += delta
            by_mnemonic[bm.get(pc, am.get(pc))['mnemonic']] += delta
            by_pc[str(pc)] = {'per_call': delta, 'uid': record['uid'], 'block': record['block'],
                              'opcode': record['opcode'], 'origin': record['origin']}
        program_total = sum(by_origin.values())
        measurement = {'pair': pair, 'total_process_guest_instructions_per_call': total,
                       'aggregate_categories_per_call': signed_cat,
                       'program_guest_instructions_per_call': program_total,
                       'outside_program_guest_instructions_per_call': total - program_total,
                       'program_origins_per_call': dict(by_origin), 'program_blocks_per_call': dict(by_block),
                       'program_mnemonics_per_call': dict(by_mnemonic), 'negative_program_deltas': negatives,
                       'raw_runs': [ar, br]}
        (directory / f'pair-{pair}/program-pcs.json').write_text(json.dumps(by_pc, indent=2))
        measurements.append(measurement)
    metadata = json.loads((entry / 'artifact.json').read_text())
    result = {'schema': 'a100-isolated-profile/v1', 'case': case_record, 'variant': variant,
              'compiler_revision': compiler_revision(), 'threads': threads, 'repeat_delta': repeats,
              'artifact': str(entry), 'artifact_sha256': staged.artifact_sha256,
              'diagnostic_note': 'Only emitted assembly comments are annotated at runtime; compiler files unchanged.',
              'adapter_sha256': ADAPTER_SHA256,
              'prototype_sha256': hashlib.sha256(b'').hexdigest(),
              'plugin_sha256': hashlib.sha256((ROOT / 'tools/profiling/full_instruction_counts.so').read_bytes()).hexdigest(),
              'asm_join': diagnostics, 'allocation': metadata['stages']['allocation'],
              'measurements': measurements, 'scope': 'Current compiler baseline c8ade47 frozen at the manifest root; comment-only MIR attribution and diagnostic cache tag; no prototype imports; QEMU counts are not board timing.'}
    (directory / 'profile.json').write_text(json.dumps(result, indent=2))
    print(json.dumps({'completed': name, 'variant': variant, 'threads': threads,
                      'program_per_call': [r['program_guest_instructions_per_call'] for r in measurements],
                      'process_per_call': [r['total_process_guest_instructions_per_call'] for r in measurements],
                      'allocation': result['allocation']}), flush=True)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--cases', type=Path, required=True)
    parser.add_argument('--variants', nargs='+', choices=['pristine'], default=['pristine'])
    parser.add_argument('--threads', nargs='+', type=int, choices=[1, 2, 4, 8], default=[1])
    parser.add_argument('--repeat-delta', type=int, default=5)
    parser.add_argument('--pairs', type=int, default=2)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--case-timeout', type=int, default=240)
    parser.add_argument('--max-wall', type=int, default=3600)
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    summary_path = args.out / 'campaign.jsonl'
    start_campaign = time.monotonic()
    def alarm_handler(*_):
        raise TimeoutError('bounded case profile timed out')
    signal.signal(signal.SIGALRM, alarm_handler)
    for record in json.loads(args.cases.read_text()):
        for variant in args.variants:
            for threads in args.threads:
                if time.monotonic() - start_campaign > args.max_wall:
                    print(json.dumps({'campaign_stopped': 'wall budget reached'}), flush=True)
                    return
                profile_path = args.out / variant / f'{record["name"]}-t{threads}' / 'profile.json'
                if args.resume and profile_path.is_file():
                    continue
                try:
                    signal.alarm(args.case_timeout)
                    result = collect(record, variant, threads, args.repeat_delta, args.pairs, args.out)
                    row = {'name': record['name'], 'variant': variant, 'threads': threads, 'status': 'collected',
                           'profile': str(args.out / variant / f'{record["name"]}-t{threads}' / 'profile.json')}
                except Exception as exc:
                    row = {'name': record['name'], 'variant': variant, 'threads': threads,
                           'status': 'collection_error', 'error': repr(exc)}
                    print(json.dumps(row), flush=True)
                finally:
                    signal.alarm(0)
                with summary_path.open('a') as stream:
                    stream.write(json.dumps(row) + '\n')


if __name__ == '__main__':
    main()
