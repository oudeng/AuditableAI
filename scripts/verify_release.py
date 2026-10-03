"""Verify a curated release tree and its reported aggregate relationships."""
import hashlib
import json
from pathlib import Path
import re
import sys

REPO=Path(__file__).resolve().parents[1]

def source_files():
    for p in REPO.rglob('*'):
        if not p.is_file():continue
        rel=p.relative_to(REPO)
        if any(x in {'.git','.venv','__pycache__','work','build','dist','.pytest_cache'} or x.endswith('.egg-info') for x in rel.parts):continue
        if p.name=='.DS_Store':continue
        yield p

def main():
    manifest=json.loads((REPO/'provenance/release_manifest.json').read_text())
    actual={str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files()
            if str(p.relative_to(REPO))!='provenance/release_manifest.json'}
    expected={r['path']:r['sha256'] for r in manifest['files']}
    if actual!=expected:
        missing=sorted(set(expected)-set(actual));extra=sorted(set(actual)-set(expected))
        changed=sorted(k for k in actual.keys()&expected.keys() if actual[k]!=expected[k])
        raise SystemExit(f'Release inventory mismatch. Missing={missing}; extra={extra}; changed={changed}. Review intentional edits before regenerating the manifest.')
    forbidden={'.pkl','.pickle','.parquet','.npz','.npy','.xpt','.xlsx','.zip','.pt','.pth','.pem','.key'}
    for name in actual:
        p=REPO/name
        assert not p.is_symlink(),f'Symlink: {name}'
        assert p.suffix.lower() not in forbidden,f'Data/model/key file in release: {name}'
        if p.suffix in {'.py','.md','.json','.toml','.yml','.yaml','.txt','.cff'}:
            text=p.read_text()
            assert not re.search(r'/(?:Users|home)/[A-Za-z0-9_.-]+/',text),f'Private absolute path: {name}'
            assert not re.search(r'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY-----)',text),f'Credential-like text: {name}'
    # Frozen engineering benchmark: totals and mechanism attribution, separately
    # for the clinical and NHANES applications. No independent-trial inference.
    for task in ['clinical','nhanes']:
        d=json.loads((REPO/f'evidence/phase4b/{task}_formal_v1/audit_v1/summary.json').read_text())
        totals={a:sum(x['n']-x['rejected'] for x in d['aggregates'] if x['arm']==a and x['invalid_truth']) for a in d['freeze']['arms']}
        assert list(totals.values())==[630,0,90,0,180,0,0,90]
        misses={a:[x['family'] for x in d['aggregates'] if x['arm']==a and x['invalid_truth'] and x['n']>x['rejected']] for a in totals}
        assert misses['minus_scope']==['scope_target','scope_unit']
        assert misses['minus_dependency']==['reference_mismatch']
        assert all(sum(x['n']-x['rejected'] for x in d['aggregates'] if x['arm']==a and not x['invalid_truth'])==270 for a in totals)
    diag=json.loads((REPO/'evidence/japan_health/diagnostic_summary.json').read_text())
    assert diag['pooled_temporal']['gate']['overpredicted']==187
    assert diag['claim_records']==188
    assert abs(diag['pooled_temporal']['gate']['mae_pp']-.701776)<1e-6
    # Check that every source-derived file still corresponds to its listed view.
    for row in json.loads((REPO/'provenance/source_map.json').read_text()):
        assert actual[row['destination']]==row['packaged_sha256'],row['destination']
    print(f'PASS: {len(actual)} release files verified; aggregate counts and diagnosis agree.')
    print('No bundled raw data, model pickle/weight files, private absolute paths or recognized credential patterns.')

if __name__=='__main__':main()
