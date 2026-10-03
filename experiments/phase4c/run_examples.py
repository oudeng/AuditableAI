from auditableai.paths import REPO, WORK, JAPAN, EVIDENCE, FIGURES, TABLES, CHECKS, display_path, resolve_record_path, prepare_outputs, required_input
"""Explanatory extensions using locked Phase4B fits; no fitting or model selection."""
from pathlib import Path
import hashlib,json,pickle,sys,time
import numpy as np
import pandas as pd
ROOT=WORK;CODE=Path(__file__).parent
sys.path.insert(0,str(CODE.parent/'phase4b'))
from models import native_predict
from run_formal import load_nhanes,metric,measures,sha
from audit_challenges import inspect,digest,canonical
OUT=ROOT/'runs/phase4c_examples_v1';OUT.mkdir(exist_ok=False)
P=json.loads((CODE/'example_protocol.json').read_text())
protocol=json.loads((CODE.parent/'phase4b/protocol.json').read_text())
def save(name,value):(OUT/name).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
save('freeze.json',{'utc':pd.Timestamp.now(tz='UTC').isoformat(),'protocol':P,'protocol_sha256':sha(CODE/'example_protocol.json'),'source_sha256':sha(__file__)})
run=ROOT/'runs/clinical_formal_v1'
with open(run/'model_6201_gate.pkl','rb') as f:m=pickle.load(f)
dev=pd.read_pickle(ROOT/'data/derived/clinical_v1/mimic_strict.pkl');features=protocol['clinical']['features'];sp=np.load(run/'split_6201.npz');v=sp['validation']
cutoff=float(np.quantile(m.predict(dev[features].to_numpy(float)[v]),.7))
save('subset_threshold_locked.json',{'threshold':cutoff,'derived_from':'MIMIC development validation predictions only','external_labels_read_for_this_threshold':False})
ext=pd.read_pickle(ROOT/'data/derived/clinical_v1/eicu_strict.pkl');y=ext.y.to_numpy(float);p=m.predict(ext[features].to_numpy(float));keep=p<=cutoff
assert np.max(np.abs(p-np.load(run/'predictions_6201.npz')['gate']))==0
subset=[]
for label,mask in [('all',np.ones(len(y),bool)),('retained',keep),('not_retained',~keep)]:
    subset.append({'group':label,'n':int(mask.sum()),'coverage':float(mask.mean()),'events':int(y[mask].sum()),'event_prevalence':float(y[mask].mean()),'brier':metric('clinical',y[mask],p[mask]),'mean_prediction':float(p[mask].mean())})
assert np.isclose(subset[0]['brier'],sum(r['coverage']*r['brier'] for r in subset[1:]))

run2=ROOT/'runs/nhanes_formal_v1'
with open(run2/'model_6201_gate.pkl','rb') as f:n=pickle.load(f)
nh,nhsources=load_nhanes(['J']);f=protocol['nhanes']['features'];X=nh[f].to_numpy(float);yy=nh.y.to_numpy(float);original=n.predict(X)
j=f.index('waist_cm');mm=X.copy();mm[:,j]*=10;wrong=n.predict(mm);normalized=mm.copy();normalized[:,j]/=10;fixed=n.predict(normalized)
export=json.loads((run2/'export_6201.json').read_text());probes=np.load(run2/'probes_6201.npz');scope={'target':'measured_HbA1c','outcome_unit':'percent','data_scope':'NHANES2017_18_adult'}
reference={'export':export,'model_id':digest(canonical(export)),'scope':scope}
bundle={'export':export,'model_id':reference['model_id'],'scope':scope,'host_predictions':probes['host']}
findings=inspect(bundle,reference,probes['X'],'Full')
assert findings==[]
rows=[]
for label,pred,declared_unit in [('original_cm',original,'cm'),('mm_without_conversion',wrong,'mm'),('mm_correctly_converted',fixed,'cm'),('silent_mm_declared_cm',wrong,'cm')]:
    rows.append({'case':label,'n':len(yy),'declared_input_unit':declared_unit,'declared_unit_mismatch':declared_unit!='cm','retained_artifact_audit_findings':findings,'rmse':metric('nhanes',yy,pred),'mae':float(np.mean(np.abs(yy-pred))),'mean_abs_prediction_change':float(np.mean(np.abs(pred-original))),'max_abs_prediction_change':float(np.max(np.abs(pred-original)))})
assert np.max(np.abs(fixed-original))<1e-12
summary={'status':P['status'],'seed':6201,'cohort_subset':{'cutoff':cutoff,'rows':subset,'interpretation':'Changing the evaluated population changes the estimand; lower subset loss is not an all-person improvement.'},'unit_conversion':{'feature':'waist circumference','valid_identity':'90 cm = 900 mm (arithmetic illustration, not a patient record)','rows':rows,'interpretation':'Declared unit comparison can trigger normalization. A retained model/probe audit cannot authenticate a false unit label on a new input batch; no hidden fault identity was passed to Full.'},'retained_sources':{'clinical_summary_sha256':sha(run/'summary.json'),'clinical_model_sha256':sha(run/'model_6201_gate.pkl'),'nhanes_summary_sha256':sha(run2/'summary.json'),'nhanes_model_sha256':sha(run2/'model_6201_gate.pkl')},'checks':{'clinical_prediction_matches_phase4b':True,'subset_weighted_decomposition':True,'correct_unit_conversion_replays_host':True,'no_refitting':True},'nhanes_sources':nhsources,'restricted_rows_exported':False}
save('summary.json',summary);print(json.dumps(summary,indent=2))
