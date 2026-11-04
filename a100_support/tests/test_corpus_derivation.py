"""The active corpus must preserve all prepared operator and comparison bytes."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

def test_active_corpus_preserves_all_prepared_operator_bytes():
    data=json.loads((ROOT/'docs/compiler-agent/A100_CORPUS_DERIVATION.json').read_text())
    assert len(data['operators'])==500
    for row in data['operators']:
        assert hashlib.sha256((ROOT/'ops'/row['path']).read_bytes()).hexdigest()==row['derived_sha256']
