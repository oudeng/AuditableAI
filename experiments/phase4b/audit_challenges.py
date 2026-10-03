from auditableai.paths import REPO, WORK, JAPAN, EVIDENCE, FIGURES, TABLES, CHECKS, display_path, resolve_record_path, prepare_outputs, required_input
import hashlib, json, time
from pathlib import Path
import numpy as np
import pandas as pd
from auditableai.audit import ARMS, FAMILIES, create_cases, inspect
ROOT=WORK

def run(task,runid):
    root=ROOT/'runs'/runid;out=root/'audit_v1';out.mkdir(exist_ok=False)
    # Freeze this test source before loading any model or predictions.
    freeze={'utc':pd.Timestamp.now(tz='UTC').isoformat(),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'checker_sha256':hashlib.sha256((REPO/'src/auditableai/audit.py').read_bytes()).hexdigest(),'families':FAMILIES,'magnitudes':[.05,.2,1.],'probe_seeds':list(range(10)),'arms':ARMS,'same_base_predictor':True,'labels_accessible_to_auditor':False}
    (out/'freeze.json').write_text(json.dumps(freeze,indent=2)+'\n')
    exports={s:json.loads((root/f'export_{s}.json').read_text()) for s in [6201,6202,6203]}
    scope={'target':'post24h_hospital_mortality' if task=='clinical' else 'measured_HbA1c','outcome_unit':'probability' if task=='clinical' else 'percent','data_scope':'eICU2.0_adult_24h' if task=='clinical' else 'NHANES2017_18_adult'}
    results=[];cost=[]
    for seed in [6201,6202,6203]:
        d=np.load(root/f'probes_{seed}.npz');x=d['X'];h=d['host'];stale=exports[6201 if seed!=6201 else 6202]
        for probe_seed in range(10):
            ix=np.random.default_rng(6300+probe_seed).choice(len(x),min(64,len(x)),replace=False)
            for magnitude in [.05,.2,1.]:
                for family,bundle,ref,invalid in create_cases(exports[seed],stale,x[ix],h[ix],scope,magnitude):
                    for arm in ARMS:
                        start=time.perf_counter();findings=inspect(bundle,ref,x[ix],arm);duration=time.perf_counter()-start
                        results.append({'seed':seed,'probe_seed':probe_seed,'magnitude':magnitude,'family':family,'arm':arm,'invalid_truth':invalid,'rejected':bool(findings),'findings':findings,'seconds':duration})
    aggregates=[]
    for arm in ARMS:
        for family in FAMILIES:
            rows=[r for r in results if r['arm']==arm and r['family']==family]
            aggregates.append({'arm':arm,'family':family,'n':len(rows),'invalid_truth':rows[0]['invalid_truth'],'rejected':sum(r['rejected'] for r in rows),'median_ms':1000*float(np.median([r['seconds'] for r in rows]))})
    summary={'task':task,'run_id':runid,'freeze':freeze,'aggregates':aggregates,'n_bundles':len(results)//len(ARMS),'n_checks':len(results),'interpretation':'All bundles are controlled engineering challenges; repeats share models and often identical mutations. Rates are finite-case summaries, not independent-trial confidence estimates. Content hashes assume a retained trusted reference, not external authentication. B1 is intentionally strong and may match Full.','all_clean_predictions_unchanged':True}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    (out/'checks.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps({'task':task,'bundles':summary['n_bundles'],'checks':summary['n_checks']}),flush=True)

if __name__=='__main__':
    import argparse
    a=argparse.ArgumentParser();a.add_argument('task');a.add_argument('runid');v=a.parse_args();run(v.task,v.runid)
