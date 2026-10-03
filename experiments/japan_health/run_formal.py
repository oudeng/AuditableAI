from auditableai.paths import REPO, WORK, JAPAN, EVIDENCE, FIGURES, TABLES, CHECKS, display_path, resolve_record_path, prepare_outputs, required_input
"""Frozen retrospective temporal and geographical forecasting evaluation."""
from pathlib import Path
import sys, json, hashlib, pickle, datetime, platform, time
import numpy as np
import pandas as pd
from scipy.special import expit, logit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler, SplineTransformer
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import Ridge
from sklearn.ensemble import HistGradientBoostingRegressor
import sklearn

HERE=Path(__file__).resolve().parent
WS=WORK
E=JAPAN
P=E/'processed'
sys.path.insert(0,str(HERE.parent/'phase4b'))
from models import Model, native_predict

FEATURES=['age','male','lag1','delta']
FAMILIES=['persistence','trend','linear','gam','hgb','gate']

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n')

def make_panel():
    d=pd.read_csv(P/'waist_panel.csv').sort_values(['pref_id','sex','age','year'])
    g=d.groupby(['pref_id','sex','age'])
    d['lag1']=g.rate.shift(1);d['lag2']=g.rate.shift(2)
    d['delta']=d.lag1-d.lag2;d['male']=(d.sex=='male').astype(float)
    d=d[d.year>=2017].copy(); assert d[FEATURES+['rate']].notna().all().all()
    return d.merge(pd.read_csv(P/'census_weights.csv')[['sex','age','weight']],on=['sex','age'],validate='many_to_one')

def grids(family):
    if family=='persistence':return [{}]
    if family=='trend':return [{'damping':x} for x in [0.25,0.5,1.0]]
    if family=='linear':return [{'reg':float(x)} for x in np.logspace(-4,4,9)]
    if family=='gam':return [{'knots':k,'reg':r} for k in [3,5,7] for r in [0.1,1.,10.]]
    if family=='hgb':return [{'learning_rate':a,'max_leaf_nodes':b} for a in [.03,.1,.2] for b in [7,15,31]]
    return [{'slope':a,'reg':r} for a in [.5,1.,2.] for r in [.1,1.,10.]]

def fit(family,params,d):
    if family in ['persistence','trend']:return None
    x=d[FEATURES].to_numpy();y=logit(d.rate.to_numpy())-logit(d.lag1.to_numpy())
    if family=='gate':return Model('japan','gate',params,916).fit(x,y)
    if family=='linear':m=make_pipeline(StandardScaler(),Ridge(alpha=params['reg']))
    elif family=='gam':
        tr=ColumnTransformer([('smooth',SplineTransformer(n_knots=params['knots'],degree=3,include_bias=False,extrapolation='linear'),[0,2,3]),('sex','passthrough',[1])])
        m=make_pipeline(tr,StandardScaler(),Ridge(alpha=params['reg']))
    else:m=HistGradientBoostingRegressor(**params,max_iter=150,l2_regularization=1,early_stopping=False,random_state=916)
    m.fit(x,y);return m

def predict(family,params,m,d):
    if family=='persistence':return d.lag1.to_numpy()
    offset=logit(d.lag1.to_numpy())
    if family=='trend':return expit(offset+params['damping']*(offset-logit(d.lag2.to_numpy())))
    return expit(offset+m.predict(d[FEATURES].to_numpy()))

def aggregate(d,pred):
    z=d[['year','pref_id','prefecture','sex','weight','rate']].copy()
    z['observed']=z.weight*z.rate;z['predicted']=z.weight*pred
    a=z.groupby(['year','pref_id','prefecture','sex'])[['observed','predicted']].sum().reset_index()
    a['error_pp']=100*(a.predicted-a.observed)
    return a

def metrics(a):
    e=a.error_pp.to_numpy()
    return dict(n=len(a),mae_pp=float(np.abs(e).mean()),rmse_pp=float(np.sqrt(np.mean(e**2))),bias_pp=float(e.mean()))

def select(family,d,exclude):
    d=d[~d.pref_id.isin(exclude)]
    candidates=[]
    for params in grids(family):
        scores=[]
        for year in [2020,2021]:
            train=d[d.year<year];val=d[d.year==year]
            m=fit(family,params,train)
            scores.append(metrics(aggregate(val,predict(family,params,m,val)))['mae_pp'])
        candidates.append(dict(params=params,mae_by_year=scores,mean_mae_pp=float(np.mean(scores))))
    best=min(range(len(candidates)),key=lambda k:candidates[k]['mean_mae_pp'])
    return candidates[best]['params'],dict(candidates=candidates,selected_index=best)

def run():
    protocol=json.loads((HERE/'protocol.json').read_text())
    out=E/'formal_v1'
    out.mkdir(parents=True,exist_ok=False)
    paths=[HERE/'protocol.json',HERE/'run_formal.py',HERE/'prepare_data.py',REPO/'src/auditableai/models.py',P/'waist_panel.csv',P/'census_weights.csv',P/'ndb2019_weights.csv']
    save(out/'freeze.json',dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),files={display_path(p):sha(p) for p in paths},
        disclosure='Portable reproduction of the historical retrospective study. This is a new run, not the original freeze or external preregistration. The original test results were already known when this packaging was prepared.',
        environment=dict(python=platform.python_version(),numpy=np.__version__,pandas=pd.__version__,sklearn=sklearn.__version__)))
    panel=make_panel();dev=panel[panel.year<=2021];test=panel[panel.year>=2022]
    allpred=[];selected={};fitted={}
    # Only developer outcomes are passed to selection. All models are saved before test scoring.
    for fam in FAMILIES:
        par,trace=select(fam,dev,[]);selected[fam]=dict(params=par,selection=trace)
        fitted[fam]=fit(fam,par,dev)
        (out/f'{fam}.pkl').write_bytes(pickle.dumps(fitted[fam]))
        print('selected',fam,par,flush=True)
    save(out/'selection.json',selected)
    save(out/'selected_before_scoring.json',dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),models={p.name:sha(p) for p in out.glob('*.pkl')}))
    export=fitted['gate'].export(FEATURES)
    export.update(response='logit change from last published proportion',forecast_link='expit(logit(lag1) + exported expression)')
    save(out/'gate_expression.json',export)
    for fam in FAMILIES:
        pr=predict(fam,selected[fam]['params'],fitted[fam],test)
        a=aggregate(test,pr);a['model']=fam;a['evaluation']='temporal';allpred.append(a)
        q=test[['year','pref_id','sex','age']].copy();q['prediction']=pr;q.to_csv(out/f'{fam}_stratum_predictions.csv',index=False)
    # Regions are excluded from BOTH selection and final fit. Their historical covariates remain allowed.
    spatial_selection={}
    for region,excluded in protocol['spatial_groups'].items():
        spatial_selection[region]={}
        hold=test[test.pref_id.isin(excluded)]
        for fam in FAMILIES:
            par,trace=select(fam,dev,excluded)
            m=fit(fam,par,dev[~dev.pref_id.isin(excluded)])
            (out/f'spatial_{region}_{fam}.pkl').write_bytes(pickle.dumps(m))
            a=aggregate(hold,predict(fam,par,m,hold));a['model']=fam;a['evaluation']='spatial';a['region']=region;allpred.append(a)
            spatial_selection[region][fam]=dict(params=par,selection=trace)
        print('region',region,'complete',flush=True)
    save(out/'spatial_selection.json',spatial_selection)
    pred=pd.concat(allpred,ignore_index=True);pred.to_csv(out/'predictions.csv',index=False)
    metric_rows=[]
    for (evaluation,family),a in pred.groupby(['evaluation','model']):
        for yr in ['pooled',2022,2023]:
            b=a if yr=='pooled' else a[a.year==yr]
            metric_rows.append(dict(evaluation=evaluation,model=family,year=str(yr),**metrics(b)))
        for sex in ['male','female']:
            metric_rows.append(dict(evaluation=evaluation,model=family,year=sex,**metrics(a[a.sex==sex])))
    pd.DataFrame(metric_rows).to_csv(out/'metrics.csv',index=False)
    temporal=pred[pred.evaluation=='temporal'].copy();temporal['ae']=temporal.error_pp.abs()
    losses=temporal.groupby(['pref_id','model']).ae.mean().unstack('model')
    rng=np.random.default_rng(916);idx=rng.integers(0,47,(10000,47))
    cis=[]
    for fam in FAMILIES[:-1]:
        delta=(losses.gate-losses[fam]).to_numpy();samples=delta[idx].mean(axis=1)
        # Seven geographically grouped blocks as a coarse dependence sensitivity.
        regional=[delta[np.array(ids)-1] for ids in protocol['spatial_groups'].values()]
        ridx=rng.integers(0,len(regional),(10000,len(regional)))
        rs=np.array([x.sum() for x in regional]);rn=np.array([len(x) for x in regional])
        rb=rs[ridx].sum(axis=1)/rn[ridx].sum(axis=1)
        cis.append(dict(comparator=fam,gate_minus_comparator_mae_pp=float(delta.mean()),
            prefecture_block_95pct=np.quantile(samples,[.025,.975]).tolist(),
            region_block_95pct=np.quantile(rb,[.025,.975]).tolist()))
    save(out/'paired_intervals.json',cis)
    # Fixed alternative age reference changes only aggregation, never fitting or selection.
    w=pd.read_csv(P/'ndb2019_weights.csv')[['sex','age','weight']]
    alternative=test.drop(columns='weight').merge(w,on=['sex','age'],validate='many_to_one')
    alt=[]
    for fam in FAMILIES:
        a=aggregate(alternative,predict(fam,selected[fam]['params'],fitted[fam],alternative))
        alt.append(dict(model=fam,**metrics(a)))
    save(out/'alternative_weights_metrics.json',alt)
    native=expit(logit(test.lag1.to_numpy())+native_predict(export,test[FEATURES].to_numpy()))
    discrepancy=float(np.max(np.abs(native-predict('gate',selected['gate']['params'],fitted['gate'],test))))
    save(out/'run_summary.json',dict(completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        training_strata=len(dev),test_strata=len(test),test_prefecture_sex_years=188,gate_export_max_abs_error=discrepancy,
        primary_metrics=[m for m in metric_rows if m['evaluation']=='temporal' and m['year']=='pooled']))
    print(json.dumps(json.loads((out/'run_summary.json').read_text()),indent=2))

if __name__=='__main__':run()
