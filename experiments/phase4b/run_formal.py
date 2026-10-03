from auditableai.paths import REPO, WORK, JAPAN, EVIDENCE, FIGURES, TABLES, CHECKS, display_path, resolve_record_path, prepare_outputs, required_input
"""Fit on development only, lock all fits, then evaluate untouched external data.

Patient/participant records, split IDs and prediction arrays stay in the local working directory.
Only explicitly selected aggregate fields belong in a public release; see docs/DATA.md.
"""
import argparse, hashlib, json, pickle, platform, time, warnings
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.special import expit, logit
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score,average_precision_score,log_loss,mean_squared_error,mean_absolute_error
from models import Model,candidates,native_predict

ROOT=WORK; CODE=Path(__file__).parent
P=json.loads((CODE/'protocol.json').read_text()); FAMILIES=['constant','linear','hgb','gate','single_gate']

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(8388608),b''):h.update(b)
    return h.hexdigest()
def save(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def metric(task,y,p):return float(mean_squared_error(y,p) if task=='clinical' else np.sqrt(mean_squared_error(y,p)))
def measures(task,y,p):
    if task=='nhanes':return {'rmse':metric(task,y,p),'mae':float(mean_absolute_error(y,p))}
    x=logit(np.clip(p,1e-8,1-1e-8));A=np.column_stack([np.ones(len(x)),x])
    loss=lambda b:np.mean(np.logaddexp(0,A@b)-y*(A@b))
    jac=lambda b:A.T@(expit(A@b)-y)/len(y)
    fit=minimize(loss,np.array([0.,1.]),jac=jac,method='BFGS')
    return {'brier':metric(task,y,p),'auroc':float(roc_auc_score(y,p)) if len(np.unique(y))==2 else None,'auprc':float(average_precision_score(y,p)) if np.sum(y)>0 else None,'log_loss':float(log_loss(y,np.clip(p,1e-8,1-1e-8),labels=[0,1])),'calibration_intercept':float(fit.x[0]),'calibration_slope':float(fit.x[1]),'calibration_fit_converged':bool(fit.success)}

def boot(task,y,preds,groups,rep=1000,seed=6299):
    # Resample groups jointly across models; optimize by group sums of squared error.
    keys,g=np.unique(groups,return_inverse=True);n=len(keys);counts=np.bincount(g)
    sums=np.column_stack([np.bincount(g,weights=(preds[k]-y)**2,minlength=n) for k in FAMILIES])
    rng=np.random.default_rng(seed);draws=[]
    for _ in range(rep):
        ix=rng.integers(0,n,n);v=sums[ix].sum(axis=0)/counts[ix].sum()
        draws.append(np.sqrt(v) if task=='nhanes' else v)
    draws=np.array(draws);result={}
    for j,k in enumerate(FAMILIES):
        result[k]={'estimate':metric(task,y,preds[k]),'ci95':np.quantile(draws[:,j],[.025,.975]).tolist()}
    delta={}
    gi=FAMILIES.index('gate')
    for j,k in enumerate(FAMILIES):
        if k!='gate':delta['gate_minus_'+k]={'estimate':metric(task,y,preds['gate'])-metric(task,y,preds[k]),'ci95':np.quantile(draws[:,gi]-draws[:,j],[.025,.975]).tolist()}
    return {'resampling_units':n,'replicates':rep,'metric':'brier' if task=='clinical' else 'rmse','models':result,'paired_differences':delta}

def load_nhanes(cycles):
    frames=[];sources=[]
    for cycle in cycles:
        letter,year={'H':('H',2013),'I':('I',2015),'J':('J',2017)}[cycle]
        root=ROOT/f'data/public/nhanes_{year}_{year+1}'
        ext='xpt'
        data={}
        for module in ['DEMO','BMX','GHB']:
            path=root/f'{module}_{letter}.{ext}';data[module]=pd.read_sas(path,format='xport');sources.append({'path':str(path),'sha256':sha(path)})
        x=data['DEMO'].merge(data['BMX'],on='SEQN',validate='1:1',suffixes=('','_bmx')).merge(data['GHB'],on='SEQN',validate='1:1')
        x=x.loc[x.RIDAGEYR.ge(18)&x.LBXGH.notna()].copy()
        x=x.rename(columns={'RIDAGEYR':'age','BMXBMI':'bmi','BMXWAIST':'waist_cm','INDFMPIR':'income_poverty_ratio','LBXGH':'y'})
        x['female']=x.RIAGENDR.map({1.:0.,2.:1.});x['patient_id']=x.SEQN.astype(int).astype(str);x['cycle']=cycle;x['hospital']=cycle
        frames.append(x[['patient_id','cycle','hospital','y','WTMEC2YR','SDMVSTRA','SDMVPSU']+P['nhanes']['features']])
    frame=pd.concat(frames,ignore_index=True);assert not frame.patient_id.duplicated().any()
    return frame,sources

def calibration_bins(y,p):
    bins=np.array([0,.025,.05,.1,.2,.3,.5,1.0000001]);ix=np.digitize(p,bins)-1;rows=[]
    for i in range(len(bins)-1):
        take=ix==i
        if take.sum()>=20:rows.append({'bin_left':float(bins[i]),'bin_right':float(min(1,bins[i+1])),'n':int(take.sum()),'mean_predicted':float(p[take].mean()),'observed':float(y[take].mean())})
    return rows

def main(task,runid):
    out=ROOT/'runs'/runid;out.mkdir(parents=True,exist_ok=False)
    save(out/'freeze.json',{'utc':pd.Timestamp.now(tz='UTC').isoformat(),'release_run':'Portable reproduction, not the original historical freeze','protocol':P,'code_sha256':{display_path(p):sha(p) for p in [*CODE.glob('*.py'),REPO/'src/auditableai/models.py']},'protocol_sha256':sha(CODE/'protocol.json')})
    started=time.monotonic();feat=P[task]['features'];models={};records=[];selection=[];splits={};sources=[]
    if task=='clinical':
        path=ROOT/'data/derived/clinical_v1/mimic_strict.pkl';dev=pd.read_pickle(path);sources=[{'path':str(path),'sha256':sha(path)}]
    else:dev,sources=load_nhanes(['H','I'])
    X=dev[feat].to_numpy(float);Y=dev.y.to_numpy(float)
    for seed in P['seeds']:
        strata=dev.y if task=='clinical' else dev.cycle
        tr,other=train_test_split(np.arange(len(dev)),train_size=.6,random_state=seed,stratify=strata)
        va,te=train_test_split(other,train_size=.5,random_state=seed+100,stratify=strata.iloc[other])
        splits[seed]={'train':tr,'validation':va,'internal_test':te}
        assert len(set(tr)&set(va))==len(set(tr)&set(te))==len(set(va)&set(te))==0
        for family in FAMILIES:
            best=None;bestvalue=np.inf
            for ci,params in enumerate(candidates(family)):
                t=time.monotonic();model=Model(task,family,params,seed).fit(X[tr],Y[tr]);v=metric(task,Y[va],model.predict(X[va]))
                selection.append({'seed':seed,'family':family,'candidate':ci,'params':params,'validation_loss':v,'fit_seconds':time.monotonic()-t})
                if v<bestvalue:bestvalue=v;best=model
            models[(seed,family)]=best
            with open(out/f'model_{seed}_{family}.pkl','wb') as f:pickle.dump(best,f)
            print(task,seed,family,'selected',best.params,'validation',bestvalue,flush=True)
        np.savez_compressed(out/f'split_{seed}.npz',patient_id=dev.patient_id.to_numpy(str),**splits[seed])
    save(out/'selection.json',selection)
    save(out/'locked_models.json',{'utc':pd.Timestamp.now(tz='UTC').isoformat(),'all_models_frozen_before_external_read':True,'sha256':{p.name:sha(p) for p in out.glob('model_*.pkl')}})
    if task=='clinical':
        path=ROOT/'data/derived/clinical_v1/eicu_strict.pkl';external=pd.read_pickle(path);sources.append({'path':str(path),'sha256':sha(path)})
        alt={k:pd.read_pickle(ROOT/f'data/derived/clinical_v1/{k}_measurement_only.pkl') for k in ['mimic','eicu']}
    else:external,src=load_nhanes(['J']);sources+=src;alt={}
    E=external[feat].to_numpy(float);EY=external.y.to_numpy(float);seed_summaries=[]
    for seed in P['seeds']:
        si=splits[seed];tr,va,te=si['train'],si['validation'],si['internal_test'];preds={}
        for family in FAMILIES:
            m=models[(seed,family)];internal=m.predict(X[te]);pred=m.predict(E);preds[family]=pred
            records.append({'seed':seed,'model':family,'split':'internal','n':len(te),**measures(task,Y[te],internal)})
            records.append({'seed':seed,'model':family,'split':'external','n':len(EY),**measures(task,EY,pred)})
        gate=models[(seed,'gate')];export=gate.export(feat)
        diff=max(float(np.max(np.abs(native_predict(export,E)-preds['gate']))),float(np.max(np.abs(native_predict(export,X[te])-gate.predict(X[te])))))
        assert diff<1e-10,('native export mismatch',diff)
        save(out/f'export_{seed}.json',export)
        np.savez_compressed(out/f'predictions_{seed}.npz',patient_id=external.patient_id.to_numpy(str),hospital=external.hospital.to_numpy(str),y=EY,**preds)
        # Unlabeled probes are drawn only from the development validation set.
        rng=np.random.default_rng(seed);probe=va[rng.choice(len(va),size=min(256,len(va)),replace=False)]
        np.savez_compressed(out/f'probes_{seed}.npz',X=X[probe],host=gate.predict(X[probe]))
        summary={'seed':seed,'n_train':len(tr),'n_validation':len(va),'n_internal':len(te),'n_external':len(EY),'native_host_max_abs_error':diff,'gate_terms':len(export['terms']),'linear_terms':len(export['linear']),'selected':{k:models[(seed,k)].params for k in FAMILIES}}
        if seed==P['primary_seed']:
            summary['primary_bootstrap']=boot(task,EY,preds,external.hospital.to_numpy() if task=='clinical' else external.patient_id.to_numpy(),P['bootstrap_replicates'])
            if task=='clinical':summary['patient_bootstrap_sensitivity']=boot(task,EY,preds,external.patient_id.to_numpy(),P['bootstrap_replicates'])
            sub=[]
            masks={'age18_64':external.age.lt(65).to_numpy(),'age65plus':external.age.ge(65).to_numpy(),'complete_features':external[feat].notna().all(axis=1).to_numpy(),'any_missing':external[feat].isna().any(axis=1).to_numpy()}
            for name,mask in masks.items():
                if mask.sum()>=20:
                    for k in FAMILIES:sub.append({'subgroup':name,'model':k,'n':int(mask.sum()),**measures(task,EY[mask],preds[k][mask])})
            summary['subgroups']=sub
            if task=='clinical':
                summary['calibration']={k:calibration_bins(EY,preds[k]) for k in FAMILIES}
                hospitals=[]
                for hospital,idx in external.groupby('hospital').groups.items():
                    if len(idx)>=100:
                        for k in FAMILIES:hospitals.append({'hospital':str(hospital),'n':len(idx),'model':k,'brier':metric(task,EY[idx],preds[k][idx])})
                summary['hospitals_n100']=hospitals
                sensitivity=[]
                for name,data,ix,base in [('mimic',dev,te,gate.predict(X[te])),('eicu',external,np.arange(len(EY)),preds['gate'])]:
                    assert np.array_equal(alt[name].patient_id,data.patient_id)
                    ap=gate.predict(alt[name][feat].to_numpy(float)[ix]);yy=data.y.to_numpy(float)[ix]
                    sensitivity.append({'dataset':name,'n':len(ix),'strict_brier':metric(task,yy,base),'measurement_only_brier':metric(task,yy,ap),'mean_abs_prediction_change':float(np.mean(np.abs(ap-base))),'fraction_prediction_change_over_001':float(np.mean(np.abs(ap-base)>.01))})
                summary['availability_sensitivity']=sensitivity
            else:
                w=external.WTMEC2YR.to_numpy(float);take=np.isfinite(w)&(w>0)
                summary['weighted_descriptive']={k:{'rmse':float(np.sqrt(np.average((EY[take]-preds[k][take])**2,weights=w[take]))),'mae':float(np.average(np.abs(EY[take]-preds[k][take]),weights=w[take]))} for k in FAMILIES}
                summary['weighting_scope']='descriptive MEC weighted observed-adult cohort; no national inference or survey-design CI'
        seed_summaries.append(summary)
    result={'task':task,'protocol_sha256':sha(CODE/'protocol.json'),'run_id':runid,'python':platform.python_version(),'sources':sources,'metrics':records,'seeds':seed_summaries,'elapsed_fit_evaluation_seconds':time.monotonic()-started,'finished_utc':pd.Timestamp.now(tz='UTC').isoformat(),'restricted_records_exported':False,'inference':'primary seed paired uncertainty; other seeds are robustness checks, not independent subjects or experiments'}
    save(out/'summary.json',result)
    print(json.dumps({'completed':task,'run':runid,'elapsed_seconds':result['elapsed_fit_evaluation_seconds']}),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('task',choices=['clinical','nhanes']);parser.add_argument('runid');args=parser.parse_args();main(args.task,args.runid)
