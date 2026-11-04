"""Executed semantic probes for the x86 reference compatibility repairs."""
import numpy as np
import triton
import triton.language as tl
import pytest
from a100_support.reference_device import TritonCpuReferenceDevice


def test_missing_support_library_points_to_existing_preparation_provenance(tmp_path, monkeypatch):
    monkeypatch.setenv('A100_PREFIX', str(tmp_path))
    with pytest.raises(RuntimeError, match='EXPERIMENT_ORIGIN.json') as error:
        TritonCpuReferenceDevice()
    from pathlib import Path
    root = Path(__file__).resolve().parents[2]
    assert (root/'docs/compiler-agent/EXPERIMENT_ORIGIN.json').is_file()
    assert 'install_reference.py' not in str(error.value)


@triton.jit
def scalar_masks(A,O,S,flag):
    x=tl.load(A,mask=flag>0,other=float('nan'))
    tl.store(O,x)
    tl.store(S,77,mask=flag>0)


@triton.jit
def repeated_cas(Claim,Old):
    i=tl.arange(0,16)
    previous=tl.atomic_cas(Claim+i%4,tl.full((16,),0,tl.int32),tl.full((16,),1,tl.int32))
    tl.store(Old+i,previous)


@triton.jit
def gather_columns(A,O):
    rows=tl.arange(0,4)[:,None]
    columns=tl.arange(0,8)[None,:]
    values=tl.load(A+rows*8+columns)
    indices=tl.broadcast_to((columns*3)%8,(4,8))
    result=tl.gather(values,indices,axis=1)
    tl.store(O+rows*8+columns,result)


@triton.jit
def sum_ones(A,O,B:tl.constexpr):
    values=tl.load(A+tl.arange(0,B))
    result=tl.sum(values,0).to(tl.float32)
    tl.store(O,result)


@triton.jit
def cast_to_bf16(A,O):
    i=tl.arange(0,16)
    tl.store(O+i,tl.load(A+i))


@triton.jit
def sum_columns(A,O,B:tl.constexpr):
    row=tl.arange(0,B)[:,None]
    col=tl.arange(0,4)[None,:]
    values=tl.load(A+row*4+col)
    tl.store(O+tl.arange(0,4),tl.sum(values,axis=0).to(tl.float32))


def test_dynamic_false_scalar_masks_preserve_other_and_store():
    device=TritonCpuReferenceDevice()
    a=device.upload(np.array([42],np.float32))
    out=device.upload(np.array([0],np.float32))
    stored=device.upload(np.array([7],np.int32))
    device.launch(scalar_masks,(1,),[a,out,stored,-3],{})
    assert np.isnan(device.download(out)[0])
    assert device.download(stored)[0]==7


def test_repeated_atomic_cas_returns_observed_values():
    device=TritonCpuReferenceDevice()
    claims=device.upload(np.zeros(4,np.int32));old=device.upload(np.full(16,-7,np.int32))
    device.launch(repeated_cas,(1,),[claims,old],{})
    observed=device.download(old)
    assert np.count_nonzero(observed==0)==4
    assert np.count_nonzero(observed==1)==12
    np.testing.assert_array_equal(device.download(claims),np.ones(4,np.int32))


def test_gather_multidimensional_runtime_indices():
    device=TritonCpuReferenceDevice()
    values=np.arange(32,dtype=np.float32).reshape(4,8)
    a=device.upload(values);out=device.upload(np.zeros_like(values))
    device.launch(gather_columns,(1,),[a,out],{})
    np.testing.assert_array_equal(device.download(out),values[:,np.arange(8)*3%8])


@pytest.mark.parametrize('dtype,count',[('bfloat16',1024),('float16',8192)])
def test_low_precision_balanced_sum(dtype,count):
    device=TritonCpuReferenceDevice()
    storage=np.float32 if dtype=='bfloat16' else np.float16
    a=device.upload(np.ones(count,storage),dtype=dtype)
    out=device.upload(np.zeros(1,np.float32))
    device.launch(sum_ones,(1,),[a,out],{'B':count})
    assert device.download(out)[0]==count


def test_portable_bf16_cast_uses_nearest_even_and_preserves_nan():
    device=TritonCpuReferenceDevice()
    bits=np.array([0,0x80000000,0x3f800000,0x3f808000,0x3f808001,0x3f818000,
                   0x7f7f8000,0x7f800000,0xff800000,0x00008000,0x00008001,
                   0x00018000,0x007f8000,0x80008001,0x7f800001,0xff800001],np.uint32)
    expected=np.array([0,0x8000,0x3f80,0x3f80,0x3f81,0x3f82,0x7f80,0x7f80,
                       0xff80,0,1,2,0x0080,0x8001,0x7fc0,0xffc0],np.uint16)
    a=device.upload(bits.view(np.float32));out=device.upload(np.zeros(16,np.uint16),dtype='bfloat16')
    device.launch(cast_to_bf16,(1,),[a,out],{})
    np.testing.assert_array_equal(device.download(out),expected)


@pytest.mark.parametrize('dtype,count',[('bfloat16',512),('float16',4096)])
def test_low_precision_leading_axis_sum(dtype,count):
    device=TritonCpuReferenceDevice()
    storage=np.float32 if dtype=='bfloat16' else np.float16
    a=device.upload(np.ones((count,4),storage),dtype=dtype)
    out=device.upload(np.zeros(4,np.float32))
    device.launch(sum_columns,(1,),[a,out],{'B':count})
    np.testing.assert_array_equal(device.download(out),np.full(4,count,np.float32))
