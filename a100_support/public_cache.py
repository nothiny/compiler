#!/usr/bin/env python3
"""Freeze the public corpus cache before isolated standalone question execution."""
import argparse
import json
import os
from pathlib import Path
import shutil
import sys
ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path.home()/'.cache/a100-prep/reference-cache'
DESTINATION=Path(os.environ.get('A100_PUBLIC_REFERENCE_CACHE',
    Path.home()/'.cache/a100-prep/public-reference-cache-a100-zcode-002'))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--path',action='store_true')
    args=parser.parse_args()
    marker=DESTINATION/'.a100-public-cache.json'
    if args.path:
        if not marker.is_file():
            print('UNVERIFIED_INFRASTRUCTURE: run a100_support/public_cache.py to freeze the public reference cache first',file=sys.stderr)
            raise SystemExit(2)
        print(DESTINATION)
        return
    audit=json.loads((ROOT/'docs/compiler-agent/A100_REFERENCE_AUDIT.json').read_text())
    if not audit.get('all_compared_pass'):
        raise RuntimeError('A complete public-corpus reference run is required before freezing its cache')
    if DESTINATION.exists():
        if not marker.is_file() or json.loads(marker.read_text())['libtriton_sha256']!=audit['libtriton_sha256']:
            raise RuntimeError('An incompatible snapshot exists; preserve it and explicitly select a fresh cache destination')
    else:
        # Cache writes use atomic replacement. Hard links preserve a snapshot
        # without copying the large public compilation artifacts.
        shutil.copytree(SOURCE,DESTINATION,copy_function=os.link)
        for path in DESTINATION.rglob('__grp__*'):
            value=json.loads(path.read_text())
            for key,source in value.get('child_paths',{}).items():
                p=Path(source)
                if p.is_relative_to(SOURCE):
                    value['child_paths'][key]=str(DESTINATION/p.relative_to(SOURCE))
            temporary=path.with_suffix(path.suffix+'.snapshot')
            temporary.write_text(json.dumps(value))
            temporary.replace(path)
        marker.write_text(json.dumps(dict(schema='a100-public-reference-cache/v1',
            source='public corpus audit and public environment probes only',
            reference_run=audit['run_id'],libtriton_sha256=audit['libtriton_sha256'],
            standalone_question_results_included=False),indent=2)+'\n')
    report=dict(json.loads(marker.read_text()),path=str(DESTINATION))
    (ROOT/'docs/compiler-agent/PUBLIC_REFERENCE_CACHE.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))


if __name__=='__main__':main()
