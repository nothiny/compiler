"""A torch-free CUDA device built directly on cuda-python.

Stock Triton 3.8 launches a kernel with any object that exposes
``data_ptr()`` and a ``dtype`` whose ``str()`` is the plain type name
(verified by probe: a ``CudaBuffer`` with ``str(dtype) == "float32"``
launches ``basic/add.py`` and produces the right sum).  So the
whole corpus runs with raw ``cudaMalloc`` pointers and **no torch anywhere**:

  - ``alloc`` / ``free``: ``cudaMalloc`` / ``cudaFree`` (``release`` frees a
    whole staged case's buffers explicitly instead of waiting for GC);
  - ``upload``: host-side dtype conversion (including fp32 -> bf16 round to
    nearest even, and the uint16 bit-pattern view), then a copy through a
    **pinned staging buffer** (``cudaMallocHost``, grown on demand) via
    ``cudaMemcpyAsync`` + stream sync -- visibly faster than pageable
    copies at benchmark sizes;
  - ``download``: the symmetric direction (bf16 buffers view back to the
    host dtype they were uploaded from);
  - ``launch``: the native Triton launch (``kernel[grid]``);
  - ``synchronize``: ``cudaDeviceSynchronize``; ``timer()``: CUDA-event
    timing context (device-anchored, no host launch overhead);
  - ``compare``: on-device allclose bit-compatible with the host path;
  - ``properties``: name, L2 size (``llc_bytes``), SM count, driver.

``--device cuda`` selects it; ``--device torch-gpu`` remains the reference
baseline.
"""
from __future__ import annotations

import numpy as np
from cuda.bindings import runtime as cudart

from opslib.device import Buffer, Device


def _check(result, what):
    err, *rest = result
    if int(err) != 0:
        raise RuntimeError(f"cuda error in {what}: {cudart.cudaGetErrorString(err)[1]}")
    return rest[0] if len(rest) == 1 else tuple(rest)


class _TypeName:
    """A dtype marker whose ``str()`` is the plain name Triton expects.

    Instances MUST be singletons (``_type_name`` below): triton 3.8's
    native argument specialization caches by object identity, and a
    short-lived marker whose address gets recycled makes the next buffer
    with a *different* dtype inherit a stale specialization -- an fp16
    cubin then runs on fp32 pointers and silently writes half the buffer.
    """

    __slots__ = ("_name",)

    def __init__(self, name):
        self._name = name

    def __repr__(self):
        return self._name


_TYPE_NAMES: dict[str, _TypeName] = {}


def _type_name(name: str) -> _TypeName:
    marker = _TYPE_NAMES.get(name)
    if marker is None:
        marker = _TYPE_NAMES[name] = _TypeName(name)
    return marker


class CudaBuffer(Buffer):
    """A raw device allocation.

    ``host_dtype`` records the numpy dtype the buffer was uploaded from (or
    ``None`` for bare ``alloc``): the download direction is symmetric with
    the upload -- bf16 buffers view back to uint16 bit patterns for uint16
    hosts and widen to float32 otherwise (matching the torch reference).
    """

    def __init__(self, ptr, dtype, shape, device, nbytes=None, host_dtype=None):
        self.ptr = int(ptr)
        self._dtype = dtype
        self._shape = tuple(int(v) for v in shape)
        self._device = device
        self.host_dtype = host_dtype
        items = 1
        for dim in self._shape:
            items *= dim
        self.nbytes = int(nbytes if nbytes is not None
                          else items * np.dtype(_storage_dtype(dtype)).itemsize)

    def data_ptr(self):
        return self.ptr

    @property
    def dtype(self):
        return self._dtype

    @property
    def shape(self):
        return self._shape

    def free(self):
        if self.ptr:
            try:
                cudart.cudaFree(self.ptr)
            finally:
                self.ptr = 0

    def __del__(self):  # interpreter teardown may race the CUDA context
        try:
            self.free()
        except Exception:  # noqa: BLE001
            pass


def _storage_dtype(dtype):
    """The numpy dtype backing one element of ``dtype`` on the host."""
    name = str(dtype).rsplit(".", 1)[-1]
    if name == "bfloat16":
        return np.dtype("uint16")
    return np.dtype(name)


def _to_bf16_bits(array):
    """float32 -> bf16 bit patterns, round to nearest even (NaN-preserving)."""
    bits = array.view(np.uint32)
    rounded = (bits + np.uint32(0x7FFF) + ((bits >> 16) & np.uint32(1))) & np.uint32(0xFFFF0000)
    rounded = np.where(np.isnan(array), bits | np.uint32(0x00400000), rounded)
    return (rounded >> np.uint32(16)).astype(np.uint16)


def _from_bf16_bits(bits):
    """bf16 bit patterns -> float32 (exact widening)."""
    return (bits.astype(np.uint32) << np.uint32(16)).view(np.float32)


class CudaEventTimer:
    """Device-anchored timing between two CUDA events.

    ``with device.timer() as t: launch(); device.synchronize()`` then
    ``t.seconds`` is the GPU time between the events, without host launch
    overhead (unlike ``perf_counter`` around an async launch).
    """

    def __init__(self):
        self._start = _check(cudart.cudaEventCreate(), "event create")
        self._end = _check(cudart.cudaEventCreate(), "event create")
        self._seconds = None

    def __enter__(self):
        _check(cudart.cudaEventRecord(self._start, 0), "event record")
        return self

    def __exit__(self, *exc):
        _check(cudart.cudaEventRecord(self._end, 0), "event record")
        _check(cudart.cudaEventSynchronize(self._end), "event sync")
        milliseconds = _check(cudart.cudaEventElapsedTime(self._start, self._end),
                              "event elapsed")
        self._seconds = milliseconds / 1000.0
        return False

    @property
    def seconds(self):
        if self._seconds is None:
            raise RuntimeError("timer read before its context exited")
        return self._seconds


class CudaDevice(Device):
    """Raw CUDA device: cuda-python runtime, pinned staging, no torch."""

    name = "cuda"

    def __init__(self, device_id: int = 0):
        self.device_id = int(device_id)
        _check(cudart.cudaSetDevice(self.device_id), "set device")
        self._pinned = None      # (ptr, nbytes) staging allocation
        self._pinned_bytes = 0

    # ------------------------------------------------------------ lifecycle
    def alloc(self, shape, dtype):
        target = _type_name(str(dtype).rsplit(".", 1)[-1])
        storage = _storage_dtype(target)
        items = int(np.prod(shape, dtype=np.int64)) if len(tuple(shape)) else 1
        nbytes = max(1, items * storage.itemsize)
        ptr = _check(cudart.cudaMalloc(nbytes), "malloc")
        return CudaBuffer(ptr, target, shape, self, nbytes=nbytes)

    def release(self, buffers):
        """Explicitly free staged buffers (benchmarks call this per entry)."""
        for buffer in buffers.values():
            if isinstance(buffer, CudaBuffer):
                buffer.free()

    def _staging(self, nbytes):
        if self._pinned is None or self._pinned_bytes < nbytes:
            if self._pinned is not None:
                _check(cudart.cudaFreeHost(self._pinned), "free host")
            self._pinned = _check(cudart.cudaMallocHost(nbytes), "malloc host")
            self._pinned_bytes = nbytes
        return self._pinned

    def _copy_to_device(self, buffer, host_bytes, nbytes):
        pinned = self._staging(nbytes)
        import ctypes
        ctypes.memmove(pinned, host_bytes, nbytes)
        _check(cudart.cudaMemcpyAsync(buffer.ptr, pinned, nbytes,
                                      cudart.cudaMemcpyKind.cudaMemcpyHostToDevice,
                                      0), "memcpy H2D")
        _check(cudart.cudaStreamSynchronize(0), "stream sync")

    # ------------------------------------------------------------ transfers
    def upload(self, array, dtype=None):
        array = np.ascontiguousarray(array)
        host_dtype = array.dtype
        target_name = str(array.dtype if dtype is None else dtype).rsplit(".", 1)[-1]
        storage = _storage_dtype(target_name)
        if target_name == "bfloat16":
            if array.dtype == np.uint16:
                payload = array                        # bit patterns as stored
            elif array.dtype == np.float32:
                payload = _to_bf16_bits(array)         # cast, RN, NaN-preserving
            else:
                raise TypeError(f"bfloat16 upload needs float32/uint16 host data,"
                                f" got {array.dtype}")
        elif array.dtype != storage:
            payload = array.astype(storage)
        else:
            payload = array
        target = _type_name(target_name)
        items = int(np.prod(array.shape, dtype=np.int64)) if len(tuple(array.shape)) else 1
        nbytes = max(1, items * np.dtype(_storage_dtype(target)).itemsize)
        ptr = _check(cudart.cudaMalloc(nbytes), "malloc")
        buffer = CudaBuffer(ptr, target, array.shape, self, nbytes=nbytes,
                            host_dtype=host_dtype)
        self._copy_to_device(buffer, payload.ctypes.data, payload.nbytes)
        return buffer

    def download(self, buffer):
        import ctypes
        name = str(buffer.dtype).rsplit(".", 1)[-1]
        storage = _storage_dtype(name)
        out = np.empty(buffer.shape, dtype=storage)
        _check(cudart.cudaMemcpy(out.ctypes.data, buffer.ptr, out.nbytes,
                                 cudart.cudaMemcpyKind.cudaMemcpyDeviceToHost),
               "memcpy D2H")
        if name != "bfloat16":
            return out
        # symmetric with the upload: uint16 hosts get the bit patterns back,
        # everything else (and bare alloc) gets the widened float32 values
        if buffer.host_dtype == np.dtype("uint16"):
            return out
        return _from_bf16_bits(out)

    # ------------------------------------------------------------ execution
    def pointer(self, buffer):
        return buffer.ptr

    def synchronize(self):
        _check(cudart.cudaDeviceSynchronize(), "device sync")

    def launch(self, kernel, grid, positional, keywords):
        # Device-side tensor descriptors need Triton's temporary global memory.
        # Keep this in the reference runtime, never in operator make_case/ref.
        import triton
        triton.set_allocator(self._allocate_scratch)
        kernel[grid](*positional, **keywords)

    def _allocate_scratch(self, size, alignment, stream):
        buffer = self.alloc((int(size) + int(alignment),), "uint8")
        # CUDA allocations are normally sufficiently aligned; support larger
        # alignments without losing the owning allocation returned to Triton.
        class AlignedScratch:
            def __init__(self, owner):
                self.owner = owner

            def data_ptr(self):
                ptr = self.owner.data_ptr()
                return (ptr + alignment - 1) // alignment * alignment

        return AlignedScratch(buffer)

    def timer(self):
        return CudaEventTimer()

    def compare(self, buffer, expected, policy):
        """On-device allclose, bit-compatible with the host comparison.

        Float32 only: python-float kernel arguments arrive as fp32, which
        mirrors numpy's weak-scalar promotion for fp32 exactly; other dtypes
        return ``None`` and the caller compares on the host.
        """
        if not isinstance(buffer, CudaBuffer):
            return None
        reference = np.ascontiguousarray(expected)
        if not reference.flags.writeable:
            reference = reference.copy()
        name = str(buffer.dtype).rsplit(".", 1)[-1]
        if reference.dtype != np.dtype("float32") or name != "float32":
            return None
        rtol = float(policy["rtol"])
        atol = float(policy["atol"])
        equal_nan = bool(policy.get("equal_nan", False))
        count = int(reference.size)
        if count == 0:                      # empty buffers: trivially close
            return True, 0.0

        from opslib.devices._cuda_compare import _allclose_kernel
        bad = self.upload(np.zeros(1, dtype=np.int32))
        maxerr = self.upload(np.zeros(1, dtype=np.int64))
        desired = self.upload(reference)
        try:
            grid = ((count + 1023) // 1024,)
            # pass the buffer objects: Triton derives pointer types from
            # data_ptr()/dtype, unlike raw ints which arrive as int64 scalars
            _allclose_kernel[grid](buffer, desired, count,
                                   bad, maxerr, rtol, atol,
                                   equal_nan, BLOCK=1024)
            self.synchronize()
            bad_count = int(self.download(bad)[0])
            error = float(np.array(self.download(maxerr)[0], np.int64)
                          .view(np.float64))
        finally:
            for scratch in (bad, maxerr, desired):
                scratch.free()
        return bad_count == 0, error

    def properties(self):
        props = _check(cudart.cudaGetDeviceProperties(self.device_id),
                       "device properties")
        driver = _check(cudart.cudaDriverGetVersion(), "driver version")
        name = props.name
        if isinstance(name, bytes):           # cuda-python returns bytes
            name = name.decode(errors="replace")
        return {
            "name": name,
            "llc_bytes": int(props.l2CacheSize),
            "sm_count": int(props.multiProcessorCount),
            "driver": int(driver),
            "device": f"cuda:{self.device_id}",
        }

    def __del__(self):
        try:
            if self._pinned is not None:
                cudart.cudaFreeHost(self._pinned)
                self._pinned = None
        except Exception:  # noqa: BLE001
            pass
