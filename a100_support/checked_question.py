#!/usr/bin/env python3
"""Require the runner's comparison result, including when an import exits early."""
import argparse
import json
import subprocess
import sys


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--mode',required=True,choices=('reference','candidate'))
    parser.add_argument('command',nargs=argparse.REMAINDER)
    args=parser.parse_args()
    command=args.command[1:] if args.command[:1]==['--'] else args.command
    if not command:parser.error('a container command is required')
    result=subprocess.run(command,text=True,stdout=subprocess.PIPE)
    sys.stdout.write(result.stdout)
    if result.returncode:return result.returncode
    try:
        row=json.loads(result.stdout.strip().splitlines()[-1])
        valid=row.get('status')=='EXECUTED_AND_COMPARED_PASS' and row.get('mode')==args.mode
        if row.get('format')=='standalone-python':
            valid &= type(row.get('cases')) is int and row['cases']>0
        else:
            valid &= all(name in row for name in ('operator','shape','dtype'))
    except (ValueError,IndexError,AttributeError):
        valid=False
    if not valid:
        print('UNVERIFIED_INFRASTRUCTURE: question runner exited without an executed comparison result',file=sys.stderr)
        return 2
    return 0


if __name__=='__main__':raise SystemExit(main())
