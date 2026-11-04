#!/usr/bin/env python3
"""Audit the complete corpus through isolated compiled x86 reference workers."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import time

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / 'docs/compiler-agent'


def atomic_json(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    temporary.replace(path)


def key(row):
    return json.dumps([row['operator'], row['shape'], row['dtype']], sort_keys=True)


def execute(operator, expected, directory, timeout, corpus, case_timeout):
    name = Path(operator).stem
    report = directory / (name + '.json')
    journal = directory / (name + '.jsonl')
    log = directory / (name + '.log')
    for old in (report, journal):
        old.unlink(missing_ok=True)
    command = [str(ROOT/'a100_support/run-reference.sh'), '-u',
               'harness/compiler_api/run_cases.py', '--device',
               'a100_support.reference_device:make_device', '--operator', operator,
               '--allow-torch', '--no-golden', '--case-timeout', str(case_timeout),
               '--case-memory-mb', '12000', '--case-cpu-seconds', str(int(timeout)),
               '--journal', str(journal), '--report', str(report), '--progress-every', '1']
    began = time.monotonic()
    with log.open('w') as output:
        process = subprocess.Popen(command, cwd=corpus, stdout=output,
                                   stderr=subprocess.STDOUT, start_new_session=True)
        try:
            code = process.wait(timeout=timeout+10)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()
            code = -signal.SIGKILL
    rows = []
    if report.is_file():
        rows = json.loads(report.read_text())
    elif journal.is_file():
        for line in journal.read_text().splitlines():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass  # A killed process may leave its final line incomplete.
    observed = {key(row): row for row in rows}
    result = []
    for case in expected:
        row = observed.get(key(case))
        if row is None:
            row = dict(case, status='REFERENCE_BACKEND_CRASH' if code < 0 else 'REFERENCE_INFRASTRUCTURE_ERROR',
                       detail=f'isolated reference process exit {code}; see {log.relative_to(ROOT)}')
        result.append(row)
    return {'operator': operator, 'returncode': code, 'seconds': time.monotonic()-began,
            'log': str(log.relative_to(ROOT)), 'cases': result}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', type=int, default=8)
    parser.add_argument('--operator', action='append')
    parser.add_argument('--operator-timeout', type=float, default=1800)
    parser.add_argument('--case-timeout', type=float, default=600)
    parser.add_argument('--corpus', choices=('ops',), default='ops')
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_CORE, (0,0))
    if args.workers < 1 or args.operator_timeout <= 0 or args.case_timeout <= 0:
        parser.error('positive worker count and timeout required')
    corpus = ROOT/args.corpus
    prefix = 'A100_'
    if args.operator:
        prefix += 'SELECTED_'
    dry = STATE/(prefix+'CORPUS_CASES.json')
    command = [str(ROOT/'a100_support/run-reference.sh'), 'harness/compiler_api/run_cases.py',
               '--manifest', 'suite/manifest.json', '--dry-run', '--report', str(dry)]
    subprocess.run(command, cwd=corpus, check=True)
    cases = json.loads(Path(str(dry)+'.manifest').read_text())
    groups = {}
    for row in cases:
        if not args.operator or row['operator'] in args.operator:
            groups.setdefault(row['operator'], []).append(row)
    run_id=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-'+str(os.getpid())
    directory = STATE/(prefix+'REFERENCE_AUDIT')/run_id
    directory.mkdir(parents=True)
    from a100_support.reference_backend import configuration
    from a100_support.reference_device import make_device
    properties=make_device().properties()
    source_hashes={operator:hashlib.sha256((corpus/operator).read_bytes()).hexdigest()
                   for operator in groups}
    library=Path.home()/'.cache/a100-prep/triton-cpu-src/python/triton/_C/libtriton.so'
    library_hash=hashlib.sha256(library.read_bytes()).hexdigest()
    began = time.time()
    results = []
    atomic_json(STATE/(prefix+'REFERENCE_AUDIT_PROGRESS.json'), {'pid': os.getpid(), 'started_at': began,
                'operators_total': len(groups), 'operators_done': 0})
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(execute, operator, rows, directory, args.operator_timeout, corpus,args.case_timeout)
                   for operator, rows in groups.items()]
        for future in as_completed(futures):
            result = future.result()
            results.append(result)
            atomic_json(directory/(Path(result['operator']).stem+'.audit.json'), result)
            atomic_json(STATE/(prefix+'REFERENCE_AUDIT_PROGRESS.json'), {'pid': os.getpid(),
                        'started_at': began, 'operators_total': len(groups), 'operators_done': len(results),
                        'last_operator': result['operator'], 'status': 'running'})
            if len(results)%25 == 0:
                print(f'Reference operators audited: {len(results)}/{len(groups)}', flush=True)
    rows = [row for result in results for row in result['cases']]
    counts = {status: sum(row['status']==status for row in rows) for status in sorted({r['status'] for r in rows})}
    payload = {'schema': 'a100-reference-audit/v1', 'environment': 'compiled-x86-triton-cpu',
               'purpose': 'question validation, not candidate compiler execution', 'corpus': args.corpus,
               'run_id':run_id, 'reference_properties':properties,
               'source_hashes':source_hashes, 'libtriton_sha256':library_hash,
               'started_at': began, 'finished_at': time.time(), 'operators': len(groups),
               'case_count': len(rows), 'summary': counts,
               'all_compared_pass': bool(rows) and all(r['status']=='PASS' for r in rows),
               'adapter_sha256': hashlib.sha256((ROOT/'a100_support/reference_device.py').read_bytes()).hexdigest(),
               'results': sorted(results,key=lambda r:r['operator'])}
    payload['inputs_unchanged']=all(hashlib.sha256((corpus/name).read_bytes()).hexdigest()==digest
                                    for name,digest in source_hashes.items())
    payload['backend_unchanged']=hashlib.sha256(library.read_bytes()).hexdigest()==library_hash
    payload['configuration_unchanged']=configuration()==properties['backend_compatibility']
    payload['all_compared_pass'] &= payload['inputs_unchanged'] and payload['backend_unchanged'] and payload['configuration_unchanged']
    atomic_json(directory/'report.json',payload)
    atomic_json(STATE/(prefix+'REFERENCE_AUDIT.json'), payload)
    atomic_json(STATE/(prefix+'REFERENCE_AUDIT_PROGRESS.json'), dict(status='finished',summary=counts,
                operators_total=len(groups),operators_done=len(results),pid=os.getpid()))
    print(json.dumps({k:v for k,v in payload.items() if k!='results'}),flush=True)
    raise SystemExit(0 if payload['all_compared_pass'] else 1)


if __name__ == '__main__':
    main()
