"""Exercise the native loader used inside isolated candidate processes."""
import json
import os
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[2]
PREFIX=Path(os.environ.get('A100_PREFIX',Path.home()/'.local/opt/a100'))
IMAGE='python@sha256:5560e9ab8709f459489e5b8aa696eda8a07ef821e14bb122be62d91234bfa98b'


def test_candidate_container_native_loader_runs_all_workers():
    mounts=[ROOT,PREFIX/'toolchain-1.1.2',PREFIX/'jdsk-qemu-10.0.2',PREFIX/'qemu-container-runtime']
    command=['docker','run','--rm','--network=none','--read-only','--cap-drop=ALL',
             '--security-opt=no-new-privileges','--user',f'{os.getuid()}:{os.getgid()}']
    for path in mounts:
        command+=['--mount',f'type=bind,source={path},target={path},readonly']
    command+=['-e','A100_PREFIX='+str(PREFIX),
              '-e','A100_QEMU_LOADER='+str(PREFIX/'qemu-container-runtime/lib64/ld-linux-x86-64.so.2'),
              '-e','A100_QEMU_HOST_LIB='+str(PREFIX/'qemu-container-runtime/lib/x86_64-linux-gnu'),
              IMAGE,'bash',str(ROOT/'a100_support/run-riscv.sh'),str(ROOT/'a100_support/build/threads_probe'),'8']
    result=subprocess.run(command,text=True,capture_output=True,timeout=30)
    assert result.returncode==0,(result.stdout,result.stderr)
    row=json.loads(result.stdout)
    assert row['passed'] and row['threads']==8 and len(row['workers'])==8
    assert sum(w['items'] for w in row['workers'])==32771
