import numpy as np
from pathlib import Path
import pytest
from a100_support.native_device import ExecutableArtifact,NativeExecutableDevice,make_device
from opslib.device import stage_case
ROOT=Path(__file__).resolve().parents[2]


class TransportFixtureCompiler:
    def __init__(self):self.calls=0
    def compile_case(self,case):
        self.calls+=1
        assert 'expected' not in case and 'oracle_args' not in case
        return ExecutableArtifact(ROOT/'a100_support/build/io_fixture',('{bundle}','bf16'),
                                  provenance='transport-fixture-not-a-compiler')


def test_actual_harness_stages_and_runs_one_complete_native_case():
    values=np.array([1,-2,0.5,4],dtype=np.float32)
    case={'kernel':object(),'args':{'a':values},'outputs':['a'],
          'expected':{'a':-values}, 'oracle_args':{'private':values.copy()},
          'pointer_dtypes':{'a':'bfloat16'}}
    compiler=TransportFixtureCompiler()
    device=NativeExecutableDevice(compiler,threads=4)
    staged=stage_case(case,device)
    staged.launch()
    np.testing.assert_array_equal(staged.outputs()['a'],-values)
    assert compiler.calls==1
    assert staged.measurement['artifact_provenance']=='transport-fixture-not-a-compiler'
    assert staged.measurement['threads']==4
    assert set(staged.measurement)=={'environment','artifact_sha256','artifact_provenance','threads'}


def test_unimplemented_compiler_is_not_substituted_by_reference(monkeypatch):
    monkeypatch.delenv('A100_COMPILER_FACTORY',raising=False)
    with pytest.raises(RuntimeError,match='after the compiler is implemented'):
        make_device()
