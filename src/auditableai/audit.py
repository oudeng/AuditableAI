"""Fixed, label-free controlled fault benchmark, with a strong conventional control.

The auditor has no fault labels, endpoint observations, or scoring-side truth.
This is a finite artifact test, not empirical prevalence or sensitivity estimation.
"""
import copy,hashlib,json,time
from pathlib import Path
import numpy as np
import pandas as pd
from .models import native_predict

ARMS=['B0_schema','B1_conventional','B2_no_binding','Full','minus_scope','minus_transform','minus_replay','minus_dependency']
FAMILIES=['clean','benign_order','benign_comment','scope_target','scope_unit','transform_shift','coefficient_shift','reference_mismatch','joint_stale','remote_tail']

def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def canonical(export):
    e={k:v for k,v in export.items() if k!='comment'}
    return {**e,'terms':sorted(e['terms']),'linear':sorted(e['linear'])}
def schema(export):
    try:
        n=2*len(export['features']);t=np.array(export['terms'],float);lin=np.array(export['linear'],float)
        return bool(t.ndim==2 and t.shape[1]==4 and np.isfinite(t).all() and np.all(t[:,1]>0) and np.all((t[:,0]>=0)&(t[:,0]<n)&(t[:,0]==t[:,0].astype(int))) and np.isfinite(lin).all() and all(0<=j<n and j==int(j) for j,w in lin) and np.isfinite(export['intercept']) and export['link'] in ['identity','logistic'] and np.isfinite(export['preprocessing']['medians']).all())
    except (KeyError,ValueError,TypeError):return False

def inspect(bundle,reference,probes,arm):
    """Reference is registered before challenge creation; no fault truth accepted."""
    e=bundle['export'];findings=[]
    if not schema(e):return ['schema']
    if arm=='B0_schema':return []
    if arm!='minus_scope' and bundle['scope']!=reference['scope']:findings.append('scope')
    if arm=='B1_conventional':
        if digest(canonical(e))!=reference['model_id'] or bundle['model_id']!=reference['model_id']:findings.append('manifest_integrity')
        if np.max(np.abs(native_predict(e,probes)-bundle['host_predictions']))>1e-8:findings.append('replay')
        return findings
    if arm!='minus_transform':
        a=np.asarray(sorted([x[:3] for x in e['terms']]),float);b=np.asarray(sorted([x[:3] for x in reference['export']['terms']]),float)
        if a.shape!=b.shape or not np.allclose(a,b,rtol=1e-10,atol=1e-10) or e['preprocessing']!=reference['export']['preprocessing']:findings.append('transform')
    if arm!='minus_replay' and np.max(np.abs(native_predict(e,probes)-bundle['host_predictions']))>1e-8:findings.append('replay')
    if arm not in ['B2_no_binding','minus_dependency']:
        if bundle['model_id']!=reference['model_id'] or digest(canonical(e))!=bundle['model_id']:findings.append('dependency')
    return findings

def create_cases(export,stale,probes,host,scope,magnitude):
    ref={'export':export,'model_id':digest(canonical(export)),'scope':scope}
    for kind in FAMILIES:
        b={'export':copy.deepcopy(export),'model_id':ref['model_id'],'scope':copy.deepcopy(scope),'host_predictions':host.copy()}
        e=b['export'];term=int(np.argmax(np.abs(np.asarray(e['terms'])[:,3])))
        if kind=='benign_order':e['terms']=list(reversed(e['terms']));e['linear']=list(reversed(e['linear']))
        elif kind=='benign_comment':e['comment']='Formatting-only description of the identical model.'
        elif kind=='scope_target':b['scope']['target']='a different endpoint'
        elif kind=='scope_unit':b['scope']['outcome_unit']='a different outcome unit'
        elif kind=='transform_shift':
            j=int(e['terms'][term][0]);e['terms'][term][2]+=magnitude*e['preprocessing']['scale'][j]
        elif kind=='coefficient_shift':e['terms'][term][3]*=1+magnitude
        elif kind=='reference_mismatch':b['model_id']='0'*64
        elif kind=='joint_stale':b['export']=copy.deepcopy(stale);b['host_predictions']=native_predict(stale,probes);b['model_id']=digest(canonical(stale))
        elif kind=='remote_tail':
            # Valid gate with negligible activation on probes; manifest binding can
            # detect it even if finite behavioral replay cannot.
            j=0;s=e['preprocessing']['scale'][j];t=float(np.nanmax(probes[:,j])+3*s)
            e['terms'].append([j,50/s,t,magnitude])
        yield kind,b,ref,kind not in ['clean','benign_order','benign_comment']
