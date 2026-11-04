#!/usr/bin/env python3
"""Question runner for parameter data and isolated standalone operator files.

Exit 0: executed and compared. Exit 1: explicit invalid question, or candidate
mismatch. Exit 2: infrastructure/reference failure (never invalid admission).
"""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import sys

ROOT=Path(__file__).resolve().parents[1]
CORPUS=ROOT/'ops'
SCHEMA='a100-question/v1'


class InvalidQuestion(ValueError):
    pass


def parse_question(data):
    if not isinstance(data,dict) or set(data)-{'schema','operator','shape','dtype','seed'}:
        raise InvalidQuestion('question contains unknown fields')
    if data.get('schema')!=SCHEMA:
        raise InvalidQuestion('unknown question schema')
    name=data.get('operator')
    if not isinstance(name,str) or not name.endswith('.py'):
        raise InvalidQuestion('operator must be a corpus-relative source path')
    path=(CORPUS/name).resolve()
    if not path.is_relative_to(CORPUS.resolve()) or not path.is_file() or path.parent.name not in ('dev','perf'):
        raise InvalidQuestion('operator is outside the declared corpus')
    shape=data.get('shape')
    if not isinstance(shape,list) or not shape or len(shape)>8 or any(type(n) is not int or n<0 for n in shape):
        raise InvalidQuestion('shape must contain nonnegative integer dimensions')
    if math.prod(shape)>2**20 or any(n>2**20 for n in shape):
        raise RuntimeError('question exceeds the configured reference resource envelope; remains unverified')
    if type(data.get('seed',30)) is not int or not -(2**63)<=data.get('seed',30)<2**63:
        raise InvalidQuestion('seed must be a signed 64-bit integer')
    if not isinstance(data.get('dtype'),str):
        raise InvalidQuestion('dtype must be declared')
    return path


def original_map():
    rows=json.loads((ROOT/'docs/compiler-agent/A100_CORPUS_CASES.json.manifest').read_text())
    mapping={}
    for row in rows:
        question=dict(schema=SCHEMA,operator=row['operator'],shape=row['shape'],dtype=row['dtype'],seed=30)
        ident='a100-'+hashlib.sha256(json.dumps(question,sort_keys=True,separators=(',',':')).encode()).hexdigest()[:24]
        if ident in mapping:
            raise RuntimeError('duplicate original case identity')
        mapping[ident]=question
    return mapping


def execute(case,mode):
    from opslib.device import stage_case
    from opslib.compare import compare_case
    if mode=='reference':
        from a100_support.reference_device import make_device
    else:
        from a100_support.native_device import make_device
    device=make_device()
    staged=stage_case(case,device)
    staged.launch()
    try:
        compare_case(case,staged.outputs())
    except AssertionError:
        if mode=='reference':
            raise RuntimeError('reference comparison failed; distinguish backend defect from question defect before rejection')
        return 1
    return 0


def python_question(path,mode):
    # The public CLI refuses to import a question on the trusted host. The
    # broker's wrapper supplies a read-only, network-free container boundary.
    if os.environ.get('A100_QUESTION_ISOLATED')!='1':
        raise RuntimeError('Standalone Python questions require the isolated question wrapper')
    from opslib.runner import load_operator
    from triton.runtime.jit import JITFunction
    from triton.runtime.autotuner import Autotuner,Heuristics
    try:
        op=load_operator(path)
    except SyntaxError as error:
        raise InvalidQuestion('standalone question has invalid Python syntax') from error
    if not callable(getattr(op,'make_case',None)) or not callable(getattr(op,'ref',None)):
        raise InvalidQuestion('standalone question requires make_case and independent ref')
    shapes=getattr(op,'SHAPES',None)
    dtypes=getattr(op,'DTYPES',None)
    if not isinstance(shapes,(tuple,list)) or not shapes or not isinstance(dtypes,(tuple,list)) or not dtypes:
        raise InvalidQuestion('standalone question must declare SHAPES and DTYPES')
    count=0
    for shape in shapes:
        for dtype in dtypes:
            try:
                case=op.make_case(shape=shape,dtype=dtype,seed=30)
            except (ValueError,AssertionError) as error:
                raise InvalidQuestion(str(error)) from error
            kernel=case.get('kernel')
            if kernel is None:
                kernels=[v for v in vars(op).values() if isinstance(v,(JITFunction,Autotuner,Heuristics))]
                if len(kernels)!=1:
                    raise InvalidQuestion('case must bind its compilation entry when multiple kernels/helpers are present')
                case=dict(case,kernel=kernels[0]);kernel=kernels[0]
            for _ in range(16):
                if isinstance(kernel,(Autotuner,Heuristics)):
                    kernel=kernel.fn
                else:
                    break
            if not isinstance(kernel,JITFunction):
                raise InvalidQuestion('case entry must be a compiled Triton JIT function')
            code=execute(case,mode)
            if code:return code
            count+=1
    print(json.dumps(dict(status='EXECUTED_AND_COMPARED_PASS',mode=mode,
                          format='standalone-python',cases=count)))
    return 0


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--mode',choices=('reference','candidate','original'),default='reference')
    parser.add_argument('--case',type=Path)
    parser.add_argument('--original-id')
    parser.add_argument('--write-original-map',action='store_true')
    args=parser.parse_args()
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    if args.write_original_map:
        mapping=original_map()
        (ROOT/'docs/compiler-agent/A100_ORIGINAL_CASE_MAP.json').write_text(json.dumps(mapping,indent=2)+'\n')
        print(json.dumps({'original_cases':len(mapping)}))
        return 0
    try:
        if args.case and args.case.suffix=='.py':
            return python_question(args.case,args.mode)
        if args.original_id:
            data=original_map().get(args.original_id)
            if data is None:
                raise RuntimeError('unknown frozen original id; original mapping is not configured')
        elif args.case:
            try:
                data=json.loads(args.case.read_text())
            except json.JSONDecodeError as error:
                raise InvalidQuestion('question must be JSON data, never executable code') from error
        else:
            raise RuntimeError('provide a case path or frozen original id')
        path=parse_question(data)
        from opslib.runner import load_operator
        op=load_operator(path)
        if data['dtype'] not in op.DTYPES:
            raise InvalidQuestion('dtype is outside the operator contract')
        try:
            case=op.make_case(shape=data['shape'],dtype=data['dtype'],seed=data.get('seed',30))
        except (ValueError,AssertionError) as error:
            raise InvalidQuestion(str(error)) from error
        code=execute(case,args.mode)
        if code:return code
        print(json.dumps(dict(status='EXECUTED_AND_COMPARED_PASS',mode=args.mode,
                              operator=data['operator'],shape=data['shape'],dtype=data['dtype'])))
        return 0
    except InvalidQuestion as error:
        print(json.dumps(dict(status='INVALID_QUESTION',detail=str(error))),file=sys.stderr)
        return 1
    except Exception as error:
        print(json.dumps(dict(status='UNVERIFIED_INFRASTRUCTURE',detail=str(error))),file=sys.stderr)
        return 2


if __name__=='__main__':
    raise SystemExit(main())
