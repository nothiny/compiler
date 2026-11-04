from pathlib import Path
import json
import struct
import subprocess
import numpy as np
import pytest
from a100_support.native_io import pack_case, unpack_outputs

ROOT=Path(__file__).resolve().parents[2]


def run(directory,mode,expected=0):
    command=[str(ROOT/'a100_support/run-riscv.sh'),str(ROOT/'a100_support/build/io_fixture'),
             str(directory/'bundle.bin'),mode]
    result=subprocess.run(command,capture_output=True,text=True,timeout=20)
    assert result.returncode==expected,(result.returncode,result.stdout,result.stderr)


def test_strided_aliases_and_guest_pointer_relocation(tmp_path):
    array=np.arange(12,dtype=np.int32)
    view=array[1::2]
    table=np.zeros(1,dtype=np.uint64)
    case={'args':{'a':array,'b':view,'table':table},'outputs':['a','b'],
          'pointer_table_relocations':[{'table':'table','entry':0,'allocation':'b','byte_offset':0}]}
    info=pack_case(case,tmp_path)
    assert info['views']['a']['storage']==info['views']['b']['storage']
    assert info['expected_outputs_included'] is False
    original=(tmp_path/'bundle.bin').read_bytes()
    run(tmp_path,'alias')
    actual=unpack_outputs(tmp_path)
    assert np.shares_memory(actual['a'],actual['b'])
    expected=array.copy();expected[1::2]+=100
    np.testing.assert_array_equal(actual['a'],expected)
    np.testing.assert_array_equal(actual['b'],expected[1::2])
    tableview=info['views']['table'];storage=info['storages'][tableview['storage']]
    offset=storage['offset']+tableview['offset']
    assert (tmp_path/'bundle.bin').read_bytes()[offset:offset+8]==original[offset:offset+8]


def test_bfloat16_value_storage_and_output_decoding(tmp_path):
    array=np.array([1.0,-2.5,0.125,4.0],dtype=np.float32)
    pack_case({'args':{'a':array},'outputs':['a'],'pointer_dtypes':{'a':'bfloat16'}},tmp_path)
    run(tmp_path,'bf16')
    np.testing.assert_array_equal(unpack_outputs(tmp_path)['a'],-array)


def test_bfloat16_raw_storage_and_negative_stride(tmp_path):
    raw=np.array([0x3f80,0xc020,0x3e00],dtype=np.uint16)[::-1]
    pack_case({'args':{'a':raw},'outputs':['a'],'pointer_dtypes':{'a':'bfloat16'}},tmp_path)
    run(tmp_path,'bf16')
    np.testing.assert_array_equal(unpack_outputs(tmp_path)['a'],raw^np.uint16(0x8000))


def test_decoded_bfloat16_outputs_preserve_aliases(tmp_path):
    values=np.array([1.0,-2.5,0.125,4.0],dtype=np.float32)
    case={'args':{'a':values,'b':values[1::2]},'outputs':['a','b'],
          'pointer_dtypes':{'a':'bfloat16','b':'bfloat16'}}
    pack_case(case,tmp_path)
    actual=unpack_outputs(tmp_path)
    assert np.shares_memory(actual['a'],actual['b'])
    actual['b'][0]=8.0
    assert actual['a'][1]==8.0


def test_runtime_scalar_widths_and_bits(tmp_path):
    values={'a':np.float32(1.25),'b':np.int32(-7),'c':np.uint64(2**63+3)}
    pack_case({'args':{**values,'out':np.zeros(3,np.uint64)},'outputs':['out']},tmp_path)
    run(tmp_path,'scalars')
    expected=[int.from_bytes(np.asarray(value).tobytes(),'little') for value in values.values()]
    np.testing.assert_array_equal(unpack_outputs(tmp_path)['out'],np.array(expected,np.uint64))


def test_native_loader_rejects_truncated_metadata(tmp_path):
    pack_case({'args':{'a':np.arange(4,dtype=np.int32)},'outputs':['a']},tmp_path)
    path=tmp_path/'bundle.bin';path.write_bytes(path.read_bytes()[:35])
    run(tmp_path,'roundtrip',expected=3)


def test_native_loader_rejects_out_of_bounds_views(tmp_path):
    info=pack_case({'args':{'a':np.arange(4,dtype=np.int32)},'outputs':['a']},tmp_path)
    path=tmp_path/'bundle.bin';image=bytearray(path.read_bytes())
    struct.pack_into('<q',image,32+16+16,2**62)
    path.write_bytes(image)
    run(tmp_path,'roundtrip',expected=3)
