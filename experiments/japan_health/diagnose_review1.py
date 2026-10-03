from auditableai.paths import REPO, WORK, JAPAN, EVIDENCE, FIGURES, TABLES, CHECKS, display_path, resolve_record_path, prepare_outputs, required_input
"""Post-hoc v0.5 forecast diagnosis; frozen inputs/models/results are read-only.

Run with the original environment. No model is retuned. Rolling validation
models use the already-selected configurations and are checked against the
saved selection scores. All new results live in review1_v1.
"""
from pathlib import Path
import copy, hashlib, json, sys
import numpy as np
import pandas as pd
from scipy.special import expit, logit

from run_formal import WS, E, P, FEATURES, FAMILIES, make_panel, fit, predict, aggregate, metrics

O = E / 'formal_v1'
D = E / 'review1_v1'
TAB = TABLES
FIG = FIGURES / 'japan_health'
LABELS = dict(persistence='Persistence', trend='Damped trend', linear='Ridge change',
              gam='Additive spline', hgb='Boosted trees', gate='Gate change')

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name, obj):
    (D/name).write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False)+'\n')
def csv(name, d): d.to_csv(D/name, index=False)

def table(name, caption, label, columns, heading, rows):
    (TAB/name).write_text('\\begin{table}[tbp]\n\\centering\\small\\setlength{\\tabcolsep}{4pt}\n'
        + '\\caption{'+caption+'}\n\\label{'+label+'}\n'
        + '\\begin{tabular}{'+columns+'}\\toprule\n'+heading+' \\\\\n\\midrule\n'
        + '\n'.join(' & '.join(r)+' \\\\' for r in rows)
        + '\n\\bottomrule\\end{tabular}\n\\end{table}\n')

def main():
    prepare_outputs()
    D.mkdir(exist_ok=False)
    frozen={p.name:sha(p) for p in O.iterdir() if p.is_file()}
    source={display_path(p):sha(p) for p in list(O.glob('*')) if p.is_file()}
    source.update({display_path(p):sha(p) for p in [P/'waist_panel.csv',P/'census_weights.csv',Path(__file__)]})
    d=make_panel();x=d[FEATURES].to_numpy()
    ex=json.loads((O/'gate_expression.json').read_text())
    terms={'intercept':np.full(len(d),ex['intercept'])}
    activations={}
    for i,(j,alpha,tau,beta) in enumerate(ex['terms'],1):
        name=f'{FEATURES[j]}_gate_{i}'
        g=expit(alpha*(x[:,j]-tau))
        terms[name]=beta*g;activations[name]=g
    for j,beta in ex['linear']:
        if j<len(FEATURES):terms[f'{FEATURES[j]}_linear']=beta*x[:,j]
        else:assert beta==0
    f=np.sum(list(terms.values()),axis=0)
    offset=logit(d.lag1.to_numpy());pr=expit(offset+f)
    true=logit(d.rate.to_numpy())-offset
    # Exact straight-path allocation on the probability scale, baseline f=0.
    # This is algebraic bookkeeping, not a causal or unique feature attribution.
    link_scale=np.divide(pr-d.lag1.to_numpy(),f,out=expit(offset)*(1-expit(offset)),where=np.abs(f)>1e-14)
    detail=d[['year','pref_id','prefecture','sex','age','weight','rate','lag1','lag2','delta']].copy()
    detail['observed_logit_change']=true;detail['predicted_logit_change']=f
    detail['gate_prediction']=pr;detail['persistence_error_pp']=100*(d.lag1-d.rate)
    detail['gate_error_pp']=100*(pr-d.rate)
    for name,t in terms.items():
        detail[name+'_logit']=t;detail[name+'_pp']=100*link_scale*t
    for name,g in activations.items():detail[name+'_activation']=g
    assert np.max(np.abs(np.sum([detail[k+'_pp'] for k in terms],axis=0)-100*(pr-d.lag1)))<1e-12
    csv('gate_stratum_decomposition.csv',detail)
    pred=pd.read_csv(O/'predictions.csv');saved=pred.query("model=='gate' and evaluation=='temporal'")
    rec=aggregate(d[d.year>=2022],pr[d.year>=2022])
    paired=rec.merge(saved,on=['year','pref_id','prefecture','sex'],suffixes=('_new','_old'))
    replay_error=float(np.max(np.abs(paired.predicted_new-paired.predicted_old)))
    assert replay_error<1e-12
    cols=['persistence_error_pp','gate_error_pp']+[k+'_pp' for k in terms]
    ag=detail[['year','pref_id','sex']].copy()
    for c in cols:ag[c]=detail[c]*detail.weight
    ag=ag.groupby(['year','pref_id','sex'],as_index=False)[cols].sum()
    csv('gate_claim_decomposition.csv',ag)
    annual=ag.groupby('year')[cols].mean().reset_index()
    annual['predicted_increment_pp']=annual[[k+'_pp' for k in terms]].sum(axis=1)
    annual['age_terms_pp']=annual[[k+'_pp' for k in terms if k.startswith('age_')]].sum(axis=1)
    annual['lag1_terms_pp']=annual[[k+'_pp' for k in terms if k.startswith('lag1_')]].sum(axis=1)
    annual['delta_terms_pp']=annual[[k+'_pp' for k in terms if k.startswith('delta_')]].sum(axis=1)
    annual['evaluation']=np.where(annual.year<=2021,'apparent_fit_of_final_model','held_out_temporal')
    csv('gate_yearly_decomposition.csv',annual)

    # Empirical activation summaries with an explicitly stated low-activation rule.
    activity=[]
    for i,(j,a,t,b) in enumerate(ex['terms'],1):
        if j!=3:continue
        name=f'delta_gate_{i}'
        for period,mask in [('train_2017_2021',d.year<=2021),('test_2022',d.year==2022),('test_2023',d.year==2023)]:
            v=activations[name][mask]
            activity.append(dict(term=name,period=period,n=int(mask.sum()),alpha=a,tau=t,beta=b,
                transition_width_10_90_pp=100*2*np.log(9)/a,
                activation_q10=float(np.quantile(v,.1)),activation_median=float(np.median(v)),
                activation_q90=float(np.quantile(v,.9)),fraction_below_0_1=float((v<.1).mean()),
                mean_contribution_logit=float((b*v).mean())))
    activity=pd.DataFrame(activity);csv('delta_gate_activity.csv',activity)
    regimes=[]
    for year,z in detail.groupby('year'):
        regimes.append(dict(year=int(year),n=len(z),input_delta_median=float(z.delta.median()),
            input_delta_negative_fraction=float((z.delta<0).mean()),
            true_logit_change_mean=float(z.observed_logit_change.mean()),
            predicted_logit_change_mean=float(z.predicted_logit_change.mean()),
            predicted_logit_change_positive_fraction=float((z.predicted_logit_change>0).mean())))
    csv('yearly_regimes.csv',pd.DataFrame(regimes))

    # Actual time path and validation/test comparisons (no post-test reselection).
    raw=pd.read_csv(P/'waist_panel.csv').merge(pd.read_csv(P/'census_weights.csv')[['sex','age','weight']],on=['sex','age'])
    raw['wr']=raw.rate*raw.weight
    yearly=raw.groupby(['year','pref_id','sex']).wr.sum().reset_index(name='observed')
    yearly=yearly.sort_values(['pref_id','sex','year'])
    yearly['change_pp']=100*yearly.groupby(['pref_id','sex'])['observed'].diff()
    csv('observed_yearly_changes.csv',yearly)
    selection=json.loads((O/'selection.json').read_text()); scores=[];validation=[]
    for fam in FAMILIES:
        chosen=selection[fam];cand=chosen['selection']['candidates'][chosen['selection']['selected_index']]
        for i,year in enumerate([2020,2021]):
            tr=d[d.year<year];va=d[d.year==year]
            m=fit(fam,chosen['params'],tr);a=aggregate(va,predict(fam,chosen['params'],m,va))
            mtr=metrics(a);assert abs(mtr['mae_pp']-cand['mae_by_year'][i])<1e-10
            scores.append(dict(model=fam,year=year,phase='rolling_validation',overpredicted=int((a.error_pp>0).sum()),**mtr))
            a['model']=fam;validation.append(a)
        for year in [2022,2023]:
            a=pred[(pred.model==fam)&(pred.evaluation=='temporal')&(pred.year==year)]
            scores.append(dict(model=fam,year=year,phase='held_out_temporal',overpredicted=int((a.error_pp>0).sum()),**metrics(a)))
    scores=pd.DataFrame(scores);csv('yearly_model_metrics.csv',scores)
    csv('selected_rolling_validation_predictions.csv',pd.concat(validation,ignore_index=True))

    # Versioned seven-field records: original evidence/results remain unchanged.
    original=json.loads((O/'claim_records.json').read_text());records=[]
    mapping={'clm':'assertion','scp':'scope','art':'artifact','ref':'reference','pro':'protocol','evd':'evidence'}
    for old in original:
        c={'claim_id':old['claim_id'],'record_version':'v0.6-review1'}
        c.update({k:copy.deepcopy(old[v]) for k,v in mapping.items()})
        c['pro']['features']=FEATURES
        c['pro']['information']='Age, sex and the preceding two years of the same stratum; final fit through FY2021.'
        c['pro']['validation_targets']=[2020,2021];c['pro']['final_training_targets']=[2017,2018,2019,2020,2021]
        c['pro']['test_targets']=[2022,2023]
        c['pro']['interpretation']='Retrospective next-release forecast; 2023 uses observed 2022 history. No retuning after testing.'
        c['bnd']={'population_boundary':old['boundary'],
            'forecast_assumption':'The fitted training-period conditional change relation remains adequate in the target period; transfer to a declining change regime is not assured.',
            'selection_boundary':'Configuration selection uses only FY2020/FY2021, spanning a direction reversal and the COVID-19 period; no pre-pandemic-only selection sensitivity was run.',
            'diagnostic_disposition':'Post-hoc review of frozen models: systematic upward forecasts and uneven low activation of previous-change gates; use annual error and term decomposition when interpreting this forecast.',
            'causal_boundary':'Aggregate trends and documented pandemic-period participation changes do not identify a causal COVID-19 effect on waist circumference.',
            'diagnostic_evidence':'review1_v1/diagnostic_summary.json; review1_v1/gate_claim_decomposition.csv',
            'revision_provenance':'Boundary added after internal review; v0.5 observed values, forecasts, source evidence and models are unchanged.'}
        assert c['clm']==old['assertion'] and c['evd']==old['evidence']
        records.append(c)
    save('claim_records_v0.6.json',records)
    save('tokyo_2023_female_record.json',next(c for c in records if c['claim_id']=='JP-2023-13-female'))
    pooled={}
    for fam in FAMILIES:
        a=pred[(pred.model==fam)&(pred.evaluation=='temporal')]
        pooled[fam]={'overpredicted':int((a.error_pp>0).sum()),**metrics(a)}
    summary={'analysis_status':'Post-hoc diagnosis triggered by internal review; no retuning or replacement of confirmatory comparisons.',
        'replay_max_abs_error':replay_error,'pooled_temporal':pooled,
        'negative_input_fraction_training':float((d.loc[d.year<=2021,'delta']<0).mean()),
        'negative_input_fraction_testing':float((d.loc[d.year>=2022,'delta']<0).mean()),
        'mean_training_target_logit_change':float(true[d.year<=2021].mean()),
        'mean_test_target_logit_change':float(true[d.year>=2022].mean()),
        'exact_decomposition':'gate error = persistence error + sum of term increments; term increment = 100*weight*term*[expit(offset+f)-expit(offset)]/f, continuous extension at f=0.',
        'attribution_boundary':'Fixed native-coordinate terms and a straight path from zero change; algebraic accounting, not unique or causal attribution.',
        'low_activation_rule':'g < 0.1 is a descriptive diagnostic threshold, not proof of zero derivative or zero effect.',
        'claim_records':len(records),'original_fields_preserved':['assertion','scope','artifact','reference','evidence'],
        'sources':source}
    save('diagnostic_summary.json',summary)

    # Reader-facing tables, four decimals; full precision remains in CSV/JSON.
    table('japan_yearly_selection.tex','Annual MAE (percentage points) for the configurations chosen by the original rolling validation. Validation models are fitted only to earlier years; the fixed final models supply both test years.',
        'tab:japan:yearly-selection','lrrrr','Method & Val. 2020 & Val. 2021 & Test 2022 & Test 2023',
        [[LABELS[f]]+[f'{scores[(scores.model==f)&(scores.year==y)].iloc[0].mae_pp:.4f}' for y in [2020,2021,2022,2023]] for f in FAMILIES])
    rows=[]
    for _,z in annual[annual.year>=2022].iterrows():
        rows.append([str(z.year)]+[f'{z[k]:.4f}' for k in ['persistence_error_pp','intercept_pp','age_terms_pp','male_linear_pp','lag1_terms_pp','delta_terms_pp','gate_error_pp']])
    table('japan_error_decomposition.tex','Exact mean signed-error decomposition of the fixed gate model over 94 standardized prefecture--sex quantities per year, in percentage points. Add the persistence error and five model contributions to obtain the final error. Contributions use the common link scale in Equation~\\ref{eq:japan:decomposition}; full-precision sums precede rounding.',
        'tab:japan:decomposition','lrrrrrrr','FY & Persist. & Intercept & Age & Sex & Lagged level & Change & Final',rows)
    rows=[]
    for name,g in activity.groupby('term',sort=True):
        a=g.set_index('period');z=g.iloc[0]
        rows.append([f'{z.tau:.4f}',f'{z.beta:.4f}']+[f'{a.loc[v].activation_median:.4f}' for v in ['train_2017_2021','test_2022','test_2023']]
                    +[f'{100*a.loc[v].fraction_below_0_1:.4f}' for v in ['test_2022','test_2023']])
    table('japan_gate_activity.tex','Previous-change gates: native proportion locations, coefficients and empirical activity. Median activations refer to all age strata in each period. The last two columns give percentages with activation below 0.1; this descriptive threshold does not imply an exactly inactive gate.',
        'tab:japan:gate-activity','rrrrrrr','$\\tau$ & $\\beta$ & Med. train & Med. 2022 & Med. 2023 & Low 2022 (\\%) & Low 2023 (\\%)',rows)
    assert frozen=={p.name:sha(p) for p in O.iterdir() if p.is_file()}
    save('integrity.json',{p.name:sha(p) for p in D.iterdir() if p.is_file()})
    print(json.dumps({k:v for k,v in summary.items() if k!='sources'},indent=2))

if __name__=='__main__':main()
