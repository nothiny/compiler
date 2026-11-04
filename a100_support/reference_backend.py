"""Explicit compatibility choices for the pinned x86 reference backend.

Use its balanced reduction lowering rather than sequential low-precision LLVM
reductions. Use its existing portable BF16 lowering to avoid the observed native
BF16 shuffle selection failure. Both paths retain BF16 storage and operation
rounding; neither changes the question, expected answers or comparison policy.
"""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
_configured=False


def configuration():
    lock=json.loads((ROOT/'a100_support/lock.json').read_text())
    return dict(reduction='balanced-low-precision-tree', bf16_lowering='portable-RNE',
                source_patch_sha256=lock['reference_patch']['sha256'],
                configuration_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())


def configure():
    global _configured
    if _configured:
        return
    import triton.backends as backends
    from triton.backends.cpu.compiler import CPUBackend
    config=json.dumps(configuration(),sort_keys=True)
    class ReferenceBackend(CPUBackend):
        def __init__(self,target):
            super().__init__(target)
            self.cpu_features.discard('avx512bf16')
        def hash(self):
            return super().hash()+':a100-reference:'+config
    backends.backends['cpu']=backends.Backend(ReferenceBackend,backends.backends['cpu'].driver)
    _configured=True
