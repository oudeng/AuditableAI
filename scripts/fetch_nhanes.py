"""Download and validate all nine CDC modules required by the thesis application."""
import hashlib
import json
from urllib.request import Request, urlopen
from urllib.parse import urlparse
import pandas as pd
from auditableai.paths import REPO, WORK

def main():
    manifest=json.loads((REPO/'data_manifests/nhanes_sources.json').read_text())
    report=[]
    for r in manifest['files']:
        p=WORK/'data/public'/r['directory']/r['file'];p.parent.mkdir(parents=True,exist_ok=True)
        if p.exists():data=p.read_bytes()
        else:
            with urlopen(Request(r['url'],headers={'User-Agent':'Academic public-data reproduction'}),timeout=90) as response:
                if urlparse(response.geturl()).hostname!='wwwn.cdc.gov':raise ValueError('Unexpected redirect')
                data=response.read()
        if not data.startswith(b'HEADER RECORD'):raise ValueError(f'Not SAS XPORT: {r["file"]}')
        actual=hashlib.sha256(data).hexdigest()
        if r.get('sha256') and actual!=r['sha256']:
            if not p.exists():p.with_suffix('.changed').write_bytes(data)
            raise SystemExit(f'CDC bytes differ from the thesis input: {r["file"]}')
        if not p.exists():p.write_bytes(data)
        frame=pd.read_sas(p,format='xport')
        assert 'SEQN' in frame and not frame.SEQN.duplicated().any()
        report.append({'file':r['file'],'url':r['url'],'sha256':actual,'rows':len(frame)})
        print(r['file'],len(frame),'rows; verified',flush=True)
    (WORK/'data/public/nhanes_download_manifest.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
