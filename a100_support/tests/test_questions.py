"""The admission runner separates invalid data from unverified execution."""
import json
import sys
import os
from pathlib import Path
import subprocess
import numpy as np
import pytest
from a100_support import question_runner


def question(tmp_path,monkeypatch,mode='reference',**overrides):
    data=dict(schema='a100-question/v1',operator='suite/dev/absolute_kernel.py',
              shape=[17],dtype='float32',seed=30)
    data.update(overrides)
    path=tmp_path/'question.json';path.write_text(json.dumps(data))
    monkeypatch.setattr(sys,'argv',['question-runner','--mode',mode,'--case',str(path)])
    return path


def test_real_compiled_cpu_question_is_executed_and_compared(tmp_path,monkeypatch):
    question(tmp_path,monkeypatch)
    assert question_runner.main()==0


@pytest.mark.parametrize('overrides',[{'dtype':'nonexistent'},
                                    {'operator':'../../README.py'},
                                    {'shape':[True]},
                                    {'expected':[1,2,3]}])
def test_invalid_question_data_is_rejected(tmp_path,monkeypatch,overrides):
    question(tmp_path,monkeypatch,**overrides)
    assert question_runner.main()==1


def test_reference_mismatch_is_unverified_not_invalid(tmp_path,monkeypatch):
    from a100_support import reference_device
    class WrongDevice:
        def stage_case(self,case,kernel=None):
            class Staged:
                def launch(self):pass
                def outputs(self):return {name:np.zeros_like(value) for name,value in case['expected'].items()}
            return Staged()
    monkeypatch.setattr(reference_device,'make_device',WrongDevice)
    question(tmp_path,monkeypatch)
    assert question_runner.main()==2


def test_missing_candidate_is_infrastructure(tmp_path,monkeypatch):
    monkeypatch.delenv('A100_COMPILER_FACTORY',raising=False)
    question(tmp_path,monkeypatch,mode='candidate')
    assert question_runner.main()==2


def test_original_map_contains_all_cases_with_unique_stable_ids():
    first=question_runner.original_map()
    assert len(first)==2734
    assert first==question_runner.original_map()


def test_standalone_source_is_not_imported_on_trusted_host(tmp_path,monkeypatch):
    path=tmp_path/'question.py';path.write_text('raise RuntimeError("must not import")')
    monkeypatch.delenv('A100_QUESTION_ISOLATED',raising=False)
    monkeypatch.setattr(sys,'argv',['question-runner','--case',str(path)])
    assert question_runner.main()==2


def test_real_standalone_composition_executes_all_cases_in_container():
    root=Path(__file__).resolve().parents[2]
    result=subprocess.run([str(root/'a100_support/run-reference-container.sh'),
                str(root/'a100_support/probes/standalone_question.py')],text=True,capture_output=True,timeout=120)
    assert result.returncode==0,(result.stdout,result.stderr)
    report=json.loads(result.stdout.splitlines()[-1])
    assert report['format']=='standalone-python' and report['cases']==4


def test_standalone_reference_mismatch_remains_unverified(tmp_path):
    root=Path(__file__).resolve().parents[2]
    source=(root/'a100_support/probes/standalone_question.py').read_text()
    path=tmp_path/'bad_question.py'
    path.write_text(source.replace("np.abs(args['x'])*2+1","np.zeros_like(args['x'])"))
    result=subprocess.run([str(root/'a100_support/run-reference-container.sh'),str(path)],
                           text=True,capture_output=True,timeout=120)
    assert result.returncode==2,(result.stdout,result.stderr)
    assert 'UNVERIFIED_INFRASTRUCTURE' in result.stderr


def test_standalone_early_success_exit_does_not_count_as_comparison(tmp_path):
    root=Path(__file__).resolve().parents[2]
    path=tmp_path/'early_exit.py';path.write_text('raise SystemExit(0)\n')
    result=subprocess.run([str(root/'a100_support/run-reference-container.sh'),str(path)],
                           text=True,capture_output=True,timeout=60)
    assert result.returncode==2
    assert 'without an executed comparison result' in result.stderr
