from auditableai.paths import REPO, WORK, JAPAN, EVIDENCE, FIGURES, TABLES, CHECKS, display_path, resolve_record_path, prepare_outputs, required_input
"""Independent artifact replay and numerical/statistical consistency checks."""
import json,pickle,hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from models import native_predict
from run_formal import ROOT,load_nhanes,measures,FAMILIES,sha

def main(task):
    run=ROOT/'runs'/f'{task}_formal_v1';out=ROOT/'runs'/f'{task}_verification_v1';out.mkdir(exist_ok=False)
    summary=json.loads((run/'summary.json').read_text());feat=summary['seeds'][0]
    p=json.loads((Path(__file__).parent/'protocol.json').read_text());features=p[task]['features']
    if task=='clinical':
        dev=pd.read_pickle(ROOT/'data/derived/clinical_v1/mimic_strict.pkl');ext=pd.read_pickle(ROOT/'data/derived/clinical_v1/eicu_strict.pkl')
    else:dev,_=load_nhanes(['H','I']);ext,_=load_nhanes(['J'])
    records=[]
    for seed in p['seeds']:
        split=np.load(run/f'split_{seed}.npz');ids=split['patient_id'];sets=[set(ids[split[k]]) for k in ['train','validation','internal_test']]
        assert all(not(sets[i]&sets[j]) for i in range(3) for j in range(i+1,3));assert sum(map(len,sets))==len(dev)
        expected=np.load(run/f'predictions_{seed}.npz');assert np.array_equal(expected['patient_id'],ext.patient_id.to_numpy(str));assert np.array_equal(expected['y'],ext.y)
        for family in FAMILIES:
            with open(run/f'model_{seed}_{family}.pkl','rb') as f:m=pickle.load(f)
            tr=split['train'];trainmedian=np.nanmedian(dev[features].to_numpy(float)[tr],axis=0)
            assert np.allclose(np.nan_to_num(trainmedian),m.pre.median_)
            pred=m.predict(ext[features].to_numpy(float));delta=float(np.max(np.abs(pred-expected[family])));assert delta==0
            actual=measures(task,expected['y'],pred);record=next(r for r in summary['metrics'] if r['seed']==seed and r['model']==family and r['split']=='external')
            key='brier' if task=='clinical' else 'rmse';assert abs(actual[key]-record[key])<1e-14
            candidates=[r for r in json.loads((run/'selection.json').read_text()) if r['seed']==seed and r['family']==family]
            assert min(candidates,key=lambda r:r['validation_loss'])['params']==m.params
            records.append({'seed':seed,'family':family,'external_replay_max_error':delta,'train_only_imputer':True,'selected_validation_minimum':True})
        export=json.loads((run/f'export_{seed}.json').read_text());assert np.max(np.abs(native_predict(export,ext[features].to_numpy(float))-expected['gate']))<1e-10
    # Calibration slope is unidentifiable for a constant predictor; preserve raw
    # v1 summaries but prohibit those optimizer outputs from scientific reporting.
    adjusted=[]
    for row in summary['metrics']:
        row=dict(row)
        if task=='clinical' and row['model']=='constant':
            row.update(calibration_intercept=None,calibration_slope=None,calibration_fit_converged=None,calibration_note='not identifiable for constant predictions')
        adjusted.append(row)
    report={'task':task,'verified_utc':pd.Timestamp.now(tz='UTC').isoformat(),'checks':records,'all_passed':True,'patient_disjoint_splits':True,'unchanged_external_replay':True,'raw_run_preserved':True,'analysis_note':'Constant-model joint calibration slope and intercept are not identifiable and are suppressed. This reporting correction changes no prediction, selection, primary endpoint or confidence interval.','reportable_metrics':adjusted,'output_sha256':{str(x.relative_to(run)):sha(x) for x in sorted(run.rglob('*')) if x.is_file()}}
    (out/'verification.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'task':task,'checks':len(records),'passed':True}))

if __name__=='__main__':
    import sys
    main(sys.argv[1])
