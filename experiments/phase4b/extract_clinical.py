from auditableai.paths import REPO, WORK, JAPAN, EVIDENCE, FIGURES, TABLES, CHECKS, display_path, resolve_record_path, prepare_outputs, required_input
"""Restricted server-side cohort extraction. Export aggregate summaries only."""
import gzip, hashlib, json, time, zipfile
from pathlib import Path
from collections import Counter
import numpy as np
import pandas as pd

ROOT=WORK
OUT=ROOT/'data/derived/clinical_v1'
P=json.loads((Path(__file__).parent/'protocol.json').read_text())
C=P['clinical']; LABS=C['labs']; FEATURES=C['features']

def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''): h.update(b)
    return h.hexdigest()

def read_member(z,name,**kw):
    with z.open('mimic-iv-3.1/'+name+'.csv.gz') as stream, gzip.GzipFile(fileobj=stream) as f:
        return pd.read_csv(f,low_memory=False,**kw)

def choose(c):
    c=c.copy()
    c['selection_hash']=c.stay_id.map(lambda x:hashlib.sha256(('6201:'+str(x)).encode()).hexdigest())
    return c.sort_values(['selection_hash','stay_id']).drop_duplicates('patient_id').sort_values('patient_id').reset_index(drop=True)

def units_valid(frame,unitcol):
    unit=frame[unitcol].fillna('').str.strip().str.lower()
    ok=np.zeros(len(frame),bool)
    for name,spec in LABS.items():
        aliases=[x.lower() for x in C['unit_aliases'][spec[2]]]
        ok |= (frame.feature.eq(name)&unit.isin(aliases)).to_numpy()
    return ok

def finish(c,records,flow,units,source):
    allrows=pd.concat(records,ignore_index=True).drop_duplicates(['stay_id','feature','measured','available','value'])
    for version in ['strict','measurement_only']:
        r=allrows if version=='measurement_only' else allrows.loc[allrows.available.between(0,1440)]
        wide=r.groupby(['stay_id','feature']).value.median().unstack().reindex(columns=list(LABS))
        output=c[['patient_id','stay_id','hospital','age','female','y']].join(wide,on='stay_id')
        assert not output.patient_id.duplicated().any()
        output.to_pickle(OUT/f'{source}_{version}.pkl')
        flow[version]={'rows':len(output),'patients':int(output.patient_id.nunique()),'hospitals':int(output.hospital.nunique()),'deaths':int(output.y.sum()),'event_prevalence':float(output.y.mean()),'missing_fraction':output[FEATURES].isna().mean().to_dict(),'retained_lab_rows':len(r)}
    flow['unknown_unit_counts']={str(k):v for k,v in units.items()}
    flow['source']=source
    (OUT/f'{source}_flow.json').write_text(json.dumps(flow,indent=2)+'\n')
    print(json.dumps({'finished':source,'flow':flow}),flush=True)

def mimic():
    archive=required_input('MIMIC_IV_ZIP')
    flow={}; units=Counter(); records=[]
    with zipfile.ZipFile(archive) as z:
        s=read_member(z,'icu/icustays',parse_dates=['intime','outtime'])
        a=read_member(z,'hosp/admissions',usecols=['subject_id','hadm_id','dischtime','deathtime','hospital_expire_flag'],parse_dates=['dischtime','deathtime'])
        p=read_member(z,'hosp/patients',usecols=['subject_id','gender','anchor_age','anchor_year'])
        flow['all_icu_stays']=len(s)
        s=s.sort_values(['intime','stay_id']).drop_duplicates('hadm_id')
        flow['first_icu_per_admission']=len(s)
        c=s.merge(a,on=['subject_id','hadm_id'],validate='1:1').merge(p,on='subject_id',validate='m:1')
        c['age']=(c.anchor_age+c.intime.dt.year-c.anchor_year).clip(upper=90)
        c['female']=c.gender.map({'F':1.,'M':0.})
        c['landmark']=c.intime+pd.Timedelta(hours=24)
        c=c.loc[c.age.ge(18)]
        flow['adult_first_stays']=len(c)
        c=c.loc[(c.outtime>c.landmark)&(c.dischtime>c.landmark)&(c.deathtime.isna()|(c.deathtime>c.landmark))&c.hospital_expire_flag.isin([0,1])].copy()
        flow['eligible_admissions']=len(c)
        c['patient_id']=c.subject_id.astype(str); c['hospital']='MIMIC'; c['y']=c.hospital_expire_flag.astype(int)
        c=choose(c); flow['one_eligible_admission_per_patient']=len(c)
        cols=['subject_id','hadm_id','itemid','charttime','storetime','valuenum','valueuom']
        lookup=c[['subject_id','hadm_id','stay_id','intime']].rename(columns={'hadm_id':'cohort_hadm_id'})
        itemmap={v[0]:k for k,v in LABS.items()}
        with z.open('mimic-iv-3.1/hosp/labevents.csv.gz') as st,gzip.GzipFile(fileobj=st) as f:
            for i,x in enumerate(pd.read_csv(f,usecols=cols,chunksize=1000000,low_memory=False)):
                x=x.loc[x.itemid.isin(itemmap)&x.subject_id.isin(c.subject_id)].copy()
                if len(x):
                    x=x.merge(lookup,on='subject_id',validate='m:1')
                    x=x.loc[x.hadm_id.isna()|x.hadm_id.eq(x.cohort_hadm_id)].copy()
                    x['measured']=(pd.to_datetime(x.charttime)-x.intime).dt.total_seconds()/60
                    x['available']=(pd.to_datetime(x.storetime)-x.intime).dt.total_seconds()/60
                    x=x.loc[x.measured.between(0,1440)].copy()
                    x['feature']=x.itemid.map(itemmap); x['value']=pd.to_numeric(x.valuenum,errors='coerce')
                    ok=units_valid(x,'valueuom')
                    units.update(map(tuple,x.loc[~ok,['feature','valueuom']].fillna('MISSING').to_numpy()))
                    x=x.loc[ok&np.isfinite(x.value)&x.value.gt(0)]
                    records.append(x[['stay_id','feature','measured','available','value']])
                if i%10==0: print('MIMIC scanned', (i+1)*1000000,flush=True)
    flow['input_sha256']=sha(archive)
    finish(c,records,flow,units,'mimic')

def eicu():
    root=required_input('EICU_DIR'); units=Counter(); records=[]
    c=pd.read_csv(root/'patient.csv.gz',low_memory=False)
    flow={'all_icu_stays':len(c)}
    # The largest hospitaladmitoffset identifies the earliest unit stay, not the smallest ID.
    c=c.sort_values(['hospitaladmitoffset','patientunitstayid'],ascending=[False,True]).drop_duplicates('patienthealthsystemstayid').copy()
    flow['first_icu_per_admission']=len(c)
    c['age']=pd.to_numeric(c.age.replace('> 89','90'),errors='coerce').clip(upper=90)
    c=c.loc[c.age.ge(18)].copy(); flow['adult_first_stays']=len(c)
    c=c.loc[c.unitdischargeoffset.gt(1440)&c.hospitaldischargeoffset.gt(1440)&c.hospitaldischargestatus.isin(['Alive','Expired'])].copy()
    flow['eligible_admissions']=len(c)
    c['patient_id']=c.uniquepid.astype(str);c['stay_id']=c.patientunitstayid;c['hospital']=c.hospitalid.astype(str)
    c['female']=c.gender.map({'Female':1.,'Male':0.});c['y']=c.hospitaldischargestatus.eq('Expired').astype(int)
    c=choose(c); flow['one_eligible_admission_per_patient']=len(c)
    namemap={v[1]:k for k,v in LABS.items()}
    for i,x in enumerate(pd.read_csv(root/'lab.csv.gz',chunksize=1000000,low_memory=False)):
        x=x.loc[x.patientunitstayid.isin(c.stay_id)&x.labname.isin(namemap)&x.labresultoffset.between(0,1440)].copy()
        x['feature']=x.labname.map(namemap);x['value']=pd.to_numeric(x.labresult,errors='coerce')
        ok=units_valid(x,'labmeasurenamesystem')
        units.update(map(tuple,x.loc[~ok,['feature','labmeasurenamesystem']].fillna('MISSING').to_numpy()))
        x=x.loc[ok&np.isfinite(x.value)&x.value.gt(0)].rename(columns={'patientunitstayid':'stay_id','labresultoffset':'measured','labresultrevisedoffset':'available'})
        records.append(x[['stay_id','feature','measured','available','value']])
        if i%10==0:print('eICU scanned',(i+1)*1000000,flush=True)
    flow['input_sha256']={f:sha(root/f) for f in ['patient.csv.gz','lab.csv.gz']}
    finish(c,records,flow,units,'eicu')

if __name__=='__main__':
    required_input('MIMIC_IV_ZIP'); required_input('EICU_DIR')
    OUT.mkdir(parents=True,exist_ok=False)
    (OUT/'protocol.json').write_text(json.dumps(P,indent=2)+'\n')
    (OUT/'freeze.json').write_text(json.dumps({'started_utc':pd.Timestamp.now(tz='UTC').isoformat(),'protocol_sha256':sha(Path(__file__).parent/'protocol.json'),'extractor_sha256':sha(__file__)},indent=2)+'\n')
    mimic();eicu()
