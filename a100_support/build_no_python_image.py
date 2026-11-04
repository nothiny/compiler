#!/usr/bin/env python3
"""Build a minimal native QEMU execution image containing no Python runtime."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PREFIX = Path.home()/'.local/opt/a100'
CONTEXT = ROOT/'a100_support/build/no-python'
IMAGE = os.environ.get('A100_NO_PYTHON_IMAGE', 'a100-qemu-functional:'+ROOT.name)


def copy_file(source, destination):
    destination.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(source,destination,follow_symlinks=True)


def main():
    if CONTEXT.exists():
        owned=CONTEXT/'Dockerfile'
        if not owned.is_file() or not owned.read_text().startswith('FROM scratch\nCOPY . /'):
            raise RuntimeError('Refusing to replace an unknown build context')
        shutil.rmtree(CONTEXT)
    CONTEXT.mkdir(parents=True,exist_ok=True)
    qemu = PREFIX/'jdsk-qemu-10.0.2/bin/qemu-riscv64'
    copy_file(qemu,CONTEXT/'usr/local/bin/qemu-riscv64')
    libraries = subprocess.check_output(['ldd',str(qemu)],text=True)
    for line in libraries.splitlines():
        match = re.search(r'(?:=>\s*)?(/[^\s]+)',line)
        if match:
            path = Path(match[1])
            copy_file(path,CONTEXT/path.relative_to('/'))
    # glibc loads the host unwinder lazily during pthread cancellation/exit;
    # this dependency is therefore not listed by ldd(qemu-riscv64).
    unwinder=Path(subprocess.check_output(['gcc','-print-file-name=libgcc_s.so.1'],text=True).strip())
    copy_file(unwinder,CONTEXT/'lib/x86_64-linux-gnu/libgcc_s.so.1')
    for path in (PREFIX/'toolchain-1.1.2/sysroot/lib').glob('*.so*'):
        if path.is_file() and path.suffix not in ('.py','.pyc'):
            copy_file(path,CONTEXT/'target/lib'/path.name)
    gcc = PREFIX/'toolchain-1.1.2/bin/riscv64-unknown-linux-gnu-gcc'
    for name in ('libgcc_s.so.1','libstdc++.so.6'):
        path = Path(subprocess.check_output([str(gcc),'-print-file-name='+name],text=True).strip())
        if not path.is_file():
            raise RuntimeError(f'Missing target runtime library: {name}')
        copy_file(path,CONTEXT/'target/lib'/name)
    for name in ('matrix_probe','threads_probe','io_fixture'):
        copy_file(ROOT/'a100_support/build'/name,CONTEXT/'probes'/name)
    dockerfile = '''FROM scratch
COPY . /
ENTRYPOINT ["/usr/local/bin/qemu-riscv64","-L","/target","-cpu","max,vlen=1024,elen=64,vext_spec=v1.0"]
'''
    (CONTEXT/'Dockerfile').write_text(dockerfile)
    rows=[]
    for path in CONTEXT.rglob('*'):
        if path.is_file():
            assert 'python' not in path.name.lower() and path.suffix not in ('.py','.pyc'),path
            rows.append({'path':str(path.relative_to(CONTEXT)),
                         'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    subprocess.run(['docker','build','--network=none','-t',IMAGE,str(CONTEXT)],check=True)
    image_id=subprocess.check_output(['docker','image','inspect',IMAGE,'--format','{{.Id}}'],text=True).strip()
    tests=[]
    for count in (1,2,4,8):
        command=['docker','run','--rm','--network=none','--read-only',IMAGE,'/probes/threads_probe',str(count)]
        result=subprocess.run(command,text=True,capture_output=True,timeout=30)
        if result.returncode:raise RuntimeError(result.stderr)
        row = json.loads(result.stdout)
        row.pop('samples_ns', None)
        tests.append(row)
    report={'schema':'a100-no-python-image/v1','image':IMAGE,'image_id':image_id,
            'files':rows,'thread_tests':tests,'python_files_present':False,
            'scope':'environment probes only, not generated compiler results'}
    (ROOT/'docs/compiler-agent/NO_PYTHON_EXECUTION.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'image':IMAGE,'image_id':image_id,'tests_passed':len(tests),'python_files_present':False}))


if __name__=='__main__':main()
