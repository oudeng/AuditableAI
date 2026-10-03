"""Refresh release hashes after reviewed edits; never changes scientific results."""
import hashlib
import json
from pathlib import Path
from verify_release import REPO, source_files

def main():
    path=REPO/'provenance/source_map.json';rows=json.loads(path.read_text())
    for row in rows:row['packaged_sha256']=hashlib.sha256((REPO/row['destination']).read_bytes()).hexdigest()
    path.write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    files=[]
    for p in sorted(source_files()):
        if p==REPO/'provenance/release_manifest.json':continue
        files.append({'path':str(p.relative_to(REPO)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    result={'format_version':1,'package_version':'1.0.0rc1','manuscript_basis':'v1.0',
            'scope':'Curated public code snapshot; manifest is content identity, not an external timestamp.',
            'files':files}
    (REPO/'provenance/release_manifest.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('Updated',len(files),'file identities. Run reproduce.py check next.')

if __name__=='__main__':main()
