"""Public cache artifacts are reusable; new question artifacts stay private."""
import json
from triton import knobs
from a100_support.reference_cache import PublicReadThroughCache


def test_public_reads_and_private_writes(tmp_path,monkeypatch):
    public=tmp_path/'public';entry=public/'key';entry.mkdir(parents=True)
    baseline=entry/'kernel.so';baseline.write_bytes(b'public artifact')
    (entry/'__grp__kernel.json').write_text(json.dumps({'child_paths':{'so':str(baseline)}}))
    own=tmp_path/'private'
    monkeypatch.setattr(knobs.cache,'dir',str(own))
    monkeypatch.setenv('A100_PUBLIC_REFERENCE_CACHE',str(public))
    manager=PublicReadThroughCache('key')
    assert manager.get_file('kernel.so')==str(baseline)
    assert manager.get_group('kernel.json')=={'so':str(baseline)}
    output=manager.put(b'new question artifact','new.so')
    assert str(own) in output
    assert not (entry/'new.so').exists()
    assert baseline.read_bytes()==b'public artifact'


def test_public_group_cannot_reference_a_path_outside_public_snapshot(tmp_path,monkeypatch):
    public=tmp_path/'public';entry=public/'key';entry.mkdir(parents=True)
    outside=tmp_path/'outside';outside.write_text('not a public artifact')
    (entry/'__grp__kernel.json').write_text(json.dumps({'child_paths':{'so':str(outside)}}))
    monkeypatch.setattr(knobs.cache,'dir',str(tmp_path/'private'))
    monkeypatch.setenv('A100_PUBLIC_REFERENCE_CACHE',str(public))
    assert PublicReadThroughCache('key').get_group('kernel.json') is None
