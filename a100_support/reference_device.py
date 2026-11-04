"""Compiled x86 Triton CPU reference device for ops-gpu-v3 and attack cases.

The corpus, NumPy oracle and comparison policies are unchanged. Ordinary host
arrays are wrapped directly; BF16 representation conversion preserves aliases.
"""
from __future__ import annotations

import ctypes
import os
from pathlib import Path
import subprocess

import numpy as np
from opslib.device import Device


def dtype_name(dtype):
    if hasattr(dtype, 'name'):
        name = dtype.name
    else:
        try:
            name = np.dtype(dtype).name
        except TypeError:
            name = str(dtype).rsplit('.', 1)[-1]
    return {'bf16': 'bfloat16', 'fp16': 'float16', 'fp32': 'float32',
            'fp64': 'float64'}.get(name, name)


def byte_bounds(array):
    function = getattr(np, 'byte_bounds', None)
    if function is None:
        function = np.lib.array_utils.byte_bounds
    return function(array)


class ReferenceBuffer:
    def __init__(self, array, dtype, host_dtype, owners=()):
        import triton.language as tl
        self.array = array
        self.dtype = tl.bfloat16 if dtype == 'bfloat16' else np.dtype(dtype)
        self.host_dtype = np.dtype(host_dtype)
        self.shape = array.shape
        self.owners = owners

    def data_ptr(self):
        return self.array.ctypes.data


class TritonCpuReferenceDevice(Device):
    name = 'x86-triton-cpu-reference'

    def __init__(self, threads=None):
        if os.environ.get('TRITON_INTERPRET') == '1':
            raise RuntimeError('The reference service requires compiled Triton CPU, not interpreter mode')
        from a100_support.reference_backend import configure
        configure()
        from triton.runtime import driver
        driver.set_active_to_cpu()
        support = Path(os.environ.get('A100_PREFIX', Path.home()/'.local/opt/a100'))/'reference-support/liba100_reference_support.so'
        if not support.is_file():
            raise RuntimeError(
                'The pinned reference compiler-rt support library is missing. '
                'Restore it using the source preparation project recorded in '
                'docs/compiler-agent/EXPERIMENT_ORIGIN.json.')
        self._support = ctypes.CDLL(str(support), mode=ctypes.RTLD_GLOBAL)
        self.threads = int(threads or os.environ.get('A100_REFERENCE_THREADS', '1'))
        if self.threads < 1:
            raise ValueError('reference threads must be positive')

    def properties(self):
        import triton
        from a100_support.reference_backend import configuration
        source = Path.home() / '.cache/a100-prep/triton-cpu-src'
        commit = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
        return {'name': self.name, 'triton': triton.__version__, 'commit': commit,
                'backend_compatibility': configuration(),
                'threads': self.threads, 'role': 'question-validation-only',
                'fast_math': os.environ.get('TRITON_CPU_FAST_MATH', 'default(1)')}

    def alloc(self, shape, dtype):
        target = dtype_name(dtype)
        storage = np.uint16 if target == 'bfloat16' else np.dtype(target)
        return ReferenceBuffer(np.zeros(shape, dtype=storage), target, storage)

    def upload(self, array, dtype=None):
        return self.upload_aliased({'array': array}, {'array': dtype or array.dtype})['array']

    def upload_aliased(self, arrays, pointer_dtypes):
        targets = {name: dtype_name(pointer_dtypes.get(name, array.dtype)) for name, array in arrays.items()}
        convert = any(targets[name] == 'bfloat16' and array.dtype != np.uint16
                      for name, array in arrays.items())
        if not convert:
            result = {}
            for name, array in arrays.items():
                target = targets[name]
                storage = np.dtype('uint16') if target == 'bfloat16' else np.dtype(target)
                if array.dtype != storage:
                    if len(arrays) != 1:
                        raise ValueError('mixed-width aliased conversion needs an explicit layout contract')
                    array = array.astype(storage)
                result[name] = ReferenceBuffer(array, target, arrays[name].dtype, tuple(arrays.values()))
            return result
        if any(array.dtype != np.float32 or targets[name] != 'bfloat16' for name, array in arrays.items()):
            raise ValueError('aliased BF16 value buffers must share a float32 host representation')
        bounds = [byte_bounds(array) for array in arrays.values()]
        low = min(a for a, b in bounds)
        high = max(b for a, b in bounds)
        if low == high:
            raw = np.empty(0, dtype=np.uint16)
        else:
            backing = (ctypes.c_char * (high-low)).from_address(low)
            values = np.frombuffer(backing, dtype=np.float32)
            bits = values.view(np.uint32)
            rounded = bits + np.uint32(0x7fff) + ((bits >> 16) & 1)
            rounded = np.where(np.isnan(values), bits | np.uint32(0x00400000), rounded)
            raw = (rounded >> 16).astype(np.uint16)
        result = {}
        for name, array in arrays.items():
            if (array.ctypes.data-low) % 4 or any(stride % 4 for stride in array.strides):
                raise ValueError('unaligned BF16 host view')
            view = np.ndarray(array.shape, dtype=np.uint16, buffer=raw,
                              offset=(array.ctypes.data-low)//2,
                              strides=tuple(stride//2 for stride in array.strides))
            result[name] = ReferenceBuffer(view, 'bfloat16', array.dtype, (raw, *arrays.values()))
        return result

    def download(self, buffer):
        if dtype_name(buffer.dtype) == 'bfloat16' and buffer.host_dtype != np.uint16:
            return (buffer.array.astype(np.uint32) << 16).view(np.float32)
        return buffer.array

    def release(self, buffers):
        pass

    def launch(self, kernel, grid, positional, keywords):
        options = dict(keywords or {})
        options.setdefault('num_cpu_threads', self.threads)
        return kernel[grid](*positional, **options)


def make_device():
    return TritonCpuReferenceDevice()
