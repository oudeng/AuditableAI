"""Retrieve the ten pinned official workbooks, including one selected ZIP member."""
import hashlib
import json
from urllib.request import Request, urlopen
from urllib.parse import urlparse
import zipfile
from auditableai.paths import REPO, JAPAN

ALLOWED={'www.mhlw.go.jp','www.e-stat.go.jp'}

def main():
    records=json.loads((REPO/'data_manifests/japan_sources.json').read_text())['files']
    records=[r for r in records if r['group']=='core']
    raw=JAPAN/'raw';raw.mkdir(parents=True,exist_ok=True)
    report=[]
    for r in sorted(records,key=lambda x:x['kind']=='zip_member'):
        p=raw/r['name']
        if p.exists():data=p.read_bytes()
        elif r['kind']=='zip_member':
            with zipfile.ZipFile(raw/r['archive']) as z:data=z.read(r['member'])
        else:
            if urlparse(r['url']).hostname not in ALLOWED:raise ValueError('Unexpected source host')
            with urlopen(Request(r['url'],headers={'User-Agent':'Academic public-data reproduction'}),timeout=90) as response:
                if urlparse(response.geturl()).hostname not in ALLOWED:raise ValueError('Unexpected redirect')
                data=response.read()
        actual=hashlib.sha256(data).hexdigest()
        if actual!=r['sha256']:
            if not p.exists():p.with_suffix(p.suffix+'.changed').write_bytes(data)
            raise SystemExit(f'Source changed: {r["name"]}. Inspect a new data version; do not overwrite the study snapshot.')
        if not p.exists():p.write_bytes(data)
        report.append({'file':r['name'],'url':r['url'],'sha256':actual,'matches_study_snapshot':True})
        (JAPAN/'retrieval_report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
        print(r['name'],'verified',flush=True)

if __name__=='__main__':main()
