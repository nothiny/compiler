"""Native, process-local pointer ABI for complete single-operator executables.

The binary carries storage, strided views, typed scalars and explicit pointer
relocations. NumPy addresses never cross the process boundary. No expected
outputs are sent to the executable. JSON is host-side compile/binding metadata.
"""
from __future__ import annotations
import ctypes
import json
from pathlib import Path
import struct
import numpy as np
from opslib.device import _overlap_groups
from a100_support.reference_device import TritonCpuReferenceDevice, byte_bounds, dtype_name

HEADER = struct.Struct('<8s6I')
STORAGE = struct.Struct('<QQ')
VIEW = struct.Struct('<IIIIq')
SCALAR = struct.Struct('<IIQ')
RELOCATION = struct.Struct('<IIQq')
MAGIC = b'A100IO01'
DTYPES = {'bool': 1, 'int8': 2, 'uint8': 3, 'int16': 4, 'uint16': 5,
          'int32': 6, 'uint32': 7, 'int64': 8, 'uint64': 9,
          'float16': 10, 'bfloat16': 11, 'float32': 12, 'float64': 13}


def aligned(n):
    return (n+63)//64*64


def scalar(value):
    if isinstance(value, np.generic):
        array = np.asarray(value)
    elif isinstance(value, bool):
        array = np.asarray(value, dtype=np.bool_)
    elif isinstance(value, int):
        array = np.asarray(value, dtype=np.int64 if value < 2**63 else np.uint64)
    elif isinstance(value, float):
        array = np.asarray(value, dtype=np.float64)
    else:
        raise TypeError(f'Unsupported runtime scalar: {type(value).__name__}')
    name = array.dtype.name
    if name not in DTYPES:
        raise TypeError(f'Unsupported runtime scalar dtype: {name}')
    bits = int.from_bytes(array.astype(array.dtype.newbyteorder('<')).tobytes(), 'little')
    return SCALAR.pack(DTYPES[name], array.itemsize, bits), name


def pack_case(case, directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    host = {**case.get('allocations', {}), **case.get('args', {})}
    arrays = {name: value for name, value in host.items() if isinstance(value, np.ndarray)}
    outputs = set(case['outputs'])
    pointers = case.get('pointer_dtypes', {})
    converter = TritonCpuReferenceDevice.__new__(TritonCpuReferenceDevice)
    storage_rows, payloads, views = [], [], {}
    for group in _overlap_groups(arrays):
        members = {name: arrays[name] for name in group}
        converted = converter.upload_aliased(members, pointers)
        bounds = [byte_bounds(buffer.array) for buffer in converted.values()]
        low, high = min(b[0] for b in bounds), max(b[1] for b in bounds)
        payload = ctypes.string_at(low, high-low) if high>low else b''
        storage_id = len(payloads)
        payloads.append(payload)
        for name, buffer in converted.items():
            array = buffer.array
            target = dtype_name(buffer.dtype)
            views[name] = {'storage': storage_id, 'dtype': target,
                           'host_dtype': arrays[name].dtype.name,
                           'offset': int(array.ctypes.data-low) if payload else 0,
                           'shape': list(array.shape), 'strides': list(array.strides),
                           'output': name in outputs}
    names = sorted(views)
    view_bytes = b''
    for name in names:
        v = views[name]
        ndim = len(v['shape'])
        view_bytes += VIEW.pack(v['storage'], DTYPES[v['dtype']], ndim, int(v['output']), v['offset'])
        view_bytes += struct.pack('<'+'q'*(2*ndim), *v['shape'], *v['strides'])
    scalar_names = sorted(name for name in host if name not in arrays)
    scalar_bytes = b''
    scalar_types = {}
    for name in scalar_names:
        encoded, scalar_types[name] = scalar(host[name])
        scalar_bytes += encoded
    relocations = list(case.get('pointer_table_relocations', ()) or ())
    legacy = case.get('pointer_relocations', ()) or ()
    if legacy:
        if isinstance(legacy, dict):
            for table, entries in legacy.items():
                for entry in entries:
                    allocation = entry.get('allocation', entry.get('allocation_arg'))
                    relocations.append({'table': table, 'entry': entry.get('index', entry.get('element_index')),
                                        'allocation': allocation,
                                        'byte_offset': entry.get('byte_offset', 0) + entry.get('element_offset', 0)*arrays[allocation].itemsize})
        else:
            relocations.extend(legacy)
    relocation_bytes = b''
    for item in relocations:
        table = item.get('table', item.get('table_arg'))
        target = item.get('allocation', item.get('allocation_arg'))
        entry = item.get('entry', item.get('element_index'))
        if table in outputs:
            raise ValueError('Pointer tables are process-local inputs, not portable address outputs')
        if views[table]['dtype'] not in ('int64', 'uint64'):
            raise ValueError('Pointer table requires 64-bit entries')
        relocation_bytes += RELOCATION.pack(names.index(table), names.index(target), int(entry), int(item.get('byte_offset', 0)))
    header = HEADER.pack(MAGIC, 1, len(payloads), len(names), len(scalar_names), len(relocations), 0)
    metadata_size = len(header)+len(payloads)*STORAGE.size+len(view_bytes)+len(scalar_bytes)+len(relocation_bytes)
    cursor = aligned(metadata_size)
    for payload in payloads:
        storage_rows.append({'offset': cursor, 'size': len(payload)})
        cursor = aligned(cursor+max(1,len(payload)))
    image = bytearray(cursor)
    metadata = header + b''.join(STORAGE.pack(v['offset'],v['size']) for v in storage_rows) + view_bytes + scalar_bytes + relocation_bytes
    image[:len(metadata)] = metadata
    for row, payload in zip(storage_rows,payloads):
        image[row['offset']:row['offset']+len(payload)] = payload
    (directory/'bundle.bin').write_bytes(image)
    info = {'schema': 'a100-native-io/v1', 'views': {name: views[name] for name in names},
            'view_order': names, 'scalar_order': scalar_names, 'scalar_types': scalar_types,
            'storages': storage_rows, 'outputs': list(case['outputs']),
            'relocations': relocations, 'expected_outputs_included': False}
    (directory/'bundle.json').write_text(json.dumps(info, indent=2)+'\n')
    return info


def unpack_outputs(directory):
    directory = Path(directory)
    info = json.loads((directory/'bundle.json').read_text())
    # Keep one owner for all returned views: aliases are observable semantics.
    image = bytearray((directory/'bundle.bin').read_bytes())
    result = {}
    decoded_bf16 = {}
    for name in info['outputs']:
        view = info['views'][name]
        row = info['storages'][view['storage']]
        dtype = np.uint16 if view['dtype']=='bfloat16' else np.dtype(view['dtype'])
        array = np.ndarray(view['shape'], dtype=dtype, buffer=image,
                           offset=row['offset']+view['offset'], strides=view['strides'])
        if view['dtype']=='bfloat16' and view['host_dtype']!='uint16':
            storage=view['storage']
            if storage not in decoded_bf16:
                raw=np.ndarray((row['size']//2,), dtype=np.uint16, buffer=image, offset=row['offset'])
                decoded_bf16[storage]=(raw.astype(np.uint32)<<16).view(np.float32)
            array=np.ndarray(view['shape'],dtype=np.float32,buffer=decoded_bf16[storage],
                             offset=view['offset']*2,strides=tuple(s*2 for s in view['strides']))
        result[name] = array
    return result
