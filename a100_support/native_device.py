"""Whole-case native executable adapter; compiler implementation is supplied later.

The host compiles once, stages a complete case, then launches one native process.
There is no Python traversal or dispatch of individual Triton programs.
"""
from dataclasses import dataclass
import hashlib
import importlib
import os
from pathlib import Path
import subprocess
import tempfile

from opslib.device import Device
from a100_support.native_io import pack_case, unpack_outputs

ROOT = Path(__file__).resolve().parents[1]


@dataclass
class ExecutableArtifact:
    executable: Path
    arguments: tuple = ('--bundle', '{bundle}', '--threads', '{threads}')
    provenance: str = 'compiler-generated'


@dataclass
class OutputBuffer:
    directory: Path
    name: str


class NativeStagedCase:
    def __init__(self, case, compiler, threads):
        if threads not in (1,2,4,8):
            raise ValueError('compute threads must be 1, 2, 4 or 8')
        self.threads = threads
        # The compiler needs the execution contract, never oracle result arrays.
        compile_case={name:value for name,value in case.items()
                      if name not in ('expected','oracle_args')}
        self.artifact = compiler.compile_case(compile_case)
        self.artifact.executable = Path(self.artifact.executable).resolve()
        if not self.artifact.executable.is_file():
            raise RuntimeError('compiler did not produce an executable')
        elf = self.artifact.executable.read_bytes()
        if elf[:6] != b'\x7fELF\x02\x01' or elf[18:20] != b'\xf3\x00':
            raise ValueError('expected a little-endian 64-bit RISC-V executable')
        self.artifact_sha256 = hashlib.sha256(elf).hexdigest()
        self._temporary = tempfile.TemporaryDirectory(prefix='a100-native-case-')
        self.directory = Path(self._temporary.name)
        self.metadata = pack_case(case,self.directory)
        self.measurement = None

    def launch(self):
        substitutions = {'bundle':str(self.directory/'bundle.bin'),'threads':str(self.threads)}
        arguments = [part.format(**substitutions) for part in self.artifact.arguments]
        command = [str(ROOT/'a100_support/run-riscv.sh'),str(self.artifact.executable),*arguments]
        result = subprocess.run(command,capture_output=True,text=True,
                                timeout=float(os.environ.get('A100_EXECUTION_TIMEOUT','120')))
        if result.returncode:
            raise RuntimeError(f'native process exit {result.returncode}: {result.stderr[-1200:]}')
        self.measurement = {'environment':'qemu-functional','artifact_sha256':self.artifact_sha256,
                            'artifact_provenance':self.artifact.provenance,
                            'threads':self.threads}

    def outputs(self):
        return unpack_outputs(self.directory)

    def buffer(self,name):
        return OutputBuffer(self.directory,name)


class NativeExecutableDevice(Device):
    name='a100-native-executable-qemu'

    def __init__(self,compiler,threads=1):
        self.compiler=compiler
        self.threads=threads

    def stage_case(self,case,kernel=None):
        if kernel is not None and kernel is not case.get('kernel'):
            case=dict(case,kernel=kernel)
        return NativeStagedCase(case,self.compiler,self.threads)

    def download(self,buffer):
        return unpack_outputs(buffer.directory)[buffer.name]


def make_device():
    factory=os.environ.get('A100_COMPILER_FACTORY','')
    if ':' not in factory:
        raise RuntimeError('Set A100_COMPILER_FACTORY=module:factory after the compiler is implemented; no reference fallback exists')
    module,name=factory.split(':',1)
    compiler=getattr(importlib.import_module(module),name)()
    return NativeExecutableDevice(compiler,int(os.environ.get('A100_COMPUTE_THREADS','1')))
