"""Direct rounding at halfway points and extremes, including double-round traps."""
import ctypes
import math
import os
from pathlib import Path
import struct
import pytest

LIBRARY=Path(os.environ.get('A100_PREFIX',Path.home()/'.local/opt/a100'))/'reference-support/liba100_reference_support.so'


@pytest.mark.parametrize('value,expected',[
    (0.0,0x0000),(-0.0,0x8000),(1.0,0x3f80),(-2.5,0xc020),
    (math.inf,0x7f80),(-math.inf,0xff80),
    (2.0**-133,0x0001),(2.0**-134,0x0000),
    (math.nextafter(2.0**-134,math.inf),0x0001),
    (2.0**-126,0x0080),(3*2.0**-134,0x0002),
    (1+2.0**-8,0x3f80),
    (math.nextafter(1+2.0**-8, math.inf),0x3f81),
    (1+3*2.0**-8,0x3f82),
    ((2-2.0**-8)*2.0**127,0x7f80),
])
def test_direct_binary64_bf16_rounding(value,expected):
    lib=ctypes.CDLL(str(LIBRARY))
    function=lib.a100_reference_f64_bits_to_bf16
    function.argtypes=[ctypes.c_uint64];function.restype=ctypes.c_uint16
    bits=struct.unpack('<Q',struct.pack('<d',value))[0]
    assert function(bits)==expected


def test_nan_remains_nan():
    lib=ctypes.CDLL(str(LIBRARY))
    function=lib.a100_reference_f64_bits_to_bf16
    function.argtypes=[ctypes.c_uint64];function.restype=ctypes.c_uint16
    for bits in (0x7ff0000000000001,0x7ff8123456789abc,0xfff0000000000001):
        result=function(bits)
        assert result&0x7f80==0x7f80 and result&0x7f
