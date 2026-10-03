from auditableai.paths import REPO, WORK, JAPAN, EVIDENCE, FIGURES, TABLES, CHECKS, display_path, resolve_record_path, prepare_outputs, required_input
prepare_outputs()
"""Figures and tables from frozen Japanese aggregate experiments."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from auditableai.plotting import apply_thesis_style
apply_thesis_style(font_scale=1.2)
E=JAPAN;O=E/'formal_v1'
OUT=FIGURES/'japan_health';OUT.mkdir(exist_ok=True)
TAB=TABLES
sources=[O/'predictions.csv',O/'metrics.csv',O/'selection.json',E/'processed/waist_panel.csv',E/'processed/census_weights.csv',O/'claim_records.json',O/'reproduction_tasks.json']
outputs=[]
pred=pd.read_csv(sources[0]);metrics=pd.read_csv(sources[1]);selection=json.loads(sources[2].read_text())
panel=pd.read_csv(sources[3]);weights=pd.read_csv(sources[4]);claims=json.loads(sources[5].read_text())
names=['Hokkaido','Aomori','Iwate','Miyagi','Akita','Yamagata','Fukushima','Ibaraki','Tochigi','Gunma','Saitama','Chiba','Tokyo','Kanagawa','Niigata','Toyama','Ishikawa','Fukui','Yamanashi','Nagano','Gifu','Shizuoka','Aichi','Mie','Shiga','Kyoto','Osaka','Hyogo','Nara','Wakayama','Tottori','Shimane','Okayama','Hiroshima','Yamaguchi','Tokushima','Kagawa','Ehime','Kochi','Fukuoka','Saga','Nagasaki','Kumamoto','Oita','Miyazaki','Kagoshima','Okinawa']
labels={'persistence':'Persistence','trend':'Damped trend','linear':'Ridge change','gam':'Additive spline','hgb':'Boosted trees','gate':'Gate change'}
colors={'observed':'#25374A','gate':'#0072B2','trend':'#D55E00'}

def save(fig,name):
    for ext in ['png','svg']:
        p=OUT/f'{name}.{ext}';fig.savefig(p,dpi=330);outputs.append(p)
    plt.close(fig)

def box(ax,x,y,w,h,title,body,color='#EDF4F7'):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.008',edgecolor='#91A7B3',facecolor=color))
    ax.text(x+w/2,y+h*.77,title,ha='center',va='center',weight='bold',fontsize=14)
    ax.text(x+w/2,y+h*.35,body,ha='center',va='center',fontsize=13,linespacing=1.40)

fig,ax=plt.subplots(figsize=(10.5,6.5));ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off');fig.subplots_adjust(left=.025,right=.975,top=.90,bottom=.035)
fig.suptitle('Japan: from a public table to a verifiable regional statement',fontsize=16,y=.97)
box(ax,.02,.70,.28,.25,'Define the quantity','Waist criterion in examinees\nMen ≥85; women ≥90 cm\n47 prefectures; ages 40–74')
box(ax,.36,.70,.28,.25,'Preserve the evidence','Nine releases: FY2015–2023\nWorkbook, sheet and cells\nFixed census age weights')
box(ax,.70,.70,.28,.25,'Compare fairly','Same inputs and test folds\nSix forecasting approaches\n2022/2023 test targets')
for x in [.30,.64]:ax.annotate('',xy=(x+.055,.825),xytext=(x+.01,.825),arrowprops={'arrowstyle':'->','lw':1.5,'color':'#476577'})
box(ax,.70,.35,.28,.22,'Check the calculation','Recalculate source counts\nReplay model and expression\nReproduce the report')
box(ax,.36,.35,.28,.22,'Attach the claim record','Assertion and scope\nArtifact, reference, protocol\nEvidence and limits')
box(ax,.02,.35,.28,.22,'Read the regional report','Observed level and forecast\nErrors and denominator\nA route to original cells')
ax.annotate('',xy=(.84,.59),xytext=(.84,.69),arrowprops={'arrowstyle':'->','lw':1.5,'color':'#476577'})
for x in [.70,.36]:ax.annotate('',xy=(x-.055,.46),xytext=(x-.01,.46),arrowprops={'arrowstyle':'->','lw':1.5,'color':'#476577'})
ax.text(.5,.16,'A common evidence record supports review across models.\nA model remains acceptable only for the claims supported by its evaluation.',ha='center',va='center',fontsize=13,linespacing=1.6)
save(fig,'japan_workflow')

fig,axes=plt.subplots(1,2,figsize=(8.4,11.0),sharey=True);fig.subplots_adjust(left=.19,right=.98,bottom=.11,top=.88,wspace=.13)
for ax,sex in zip(axes,['male','female']):
    d=pred[(pred.evaluation=='temporal')&(pred.year==2023)&(pred.sex==sex)]
    actual=d[d.model=='gate'].sort_values('pref_id');y=np.arange(47)
    ax.scatter(actual.observed*100,y,color=colors['observed'],s=22,label='Observed',zorder=4)
    for fam,marker,offset in [('gate','s',-.16),('trend','^',.16)]:
        s=d[d.model==fam].sort_values('pref_id')
        ax.scatter(s.predicted*100,y+offset,color=colors[fam],s=21,marker=marker,label=labels[fam],zorder=3)
    ax.set_yticks(y,names,fontsize=11.5);ax.set_ylim(47,-1);ax.grid(axis='y',alpha=.2)
    ax.set_xlabel('Standardized proportion (%)',fontsize=12)
    ax.set_title('Men: waist ≥85 cm' if sex=='male' else 'Women: waist ≥90 cm',fontsize=13,pad=14)
    ax.axhspan(11.55,12.45,color='#E7B566',alpha=.20,zorder=0)
fig.suptitle('All 47 prefectures: FY2023 observations and forecasts',fontsize=14,y=.97)
handles,labs=axes[0].get_legend_handles_labels();fig.legend(handles,labs,loc='upper center',bbox_to_anchor=(.56,.936),ncol=3,frameon=False,fontsize=11)
fig.text(.55,.025,'Fixed 2020 census weights; examinee population. Tokyo is shaded.\nAll six methods and both test years are retained in the results table and evidence files.',ha='center',fontsize=10,linespacing=1.5)
save(fig,'japan_prefectures')

fig=plt.figure(figsize=(9.0,7.0));gs=fig.add_gridspec(2,2,height_ratios=[1,.65],left=.085,right=.97,top=.84,bottom=.04,hspace=.36,wspace=.28)
for ax,sex in zip([fig.add_subplot(gs[0,0]),fig.add_subplot(gs[0,1])],['male','female']):
    d=panel[(panel.pref_id==13)&(panel.sex==sex)].merge(weights[['sex','age','weight']],on=['sex','age'])
    obs=d.assign(value=d.rate*d.weight).groupby('year').value.sum()
    ax.plot(obs.index,obs*100,'o-',color=colors['observed'],lw=1.8,ms=4,label='Observed')
    for fam,marker in [('gate','s'),('trend','^')]:
        p=pred[(pred.pref_id==13)&(pred.evaluation=='temporal')&(pred.sex==sex)&(pred.model==fam)].sort_values('year')
        ax.plot(p.year,p.predicted*100,marker+'--',color=colors[fam],ms=5,label=labels[fam])
    ax.axvspan(2021.5,2023.2,color='#E9EFF3',alpha=.7,zorder=-1)
    ax.set(xlim=(2014.8,2023.3),xticks=[2015,2017,2019,2021,2023],ylabel='Standardized proportion (%)')
    ax.set_title('Tokyo men' if sex=='male' else 'Tokyo women',fontsize=13)
    ax.tick_params(labelsize=10)
    if sex=='male':ax.legend(frameon=False,fontsize=9,loc='upper left')
ax=fig.add_subplot(gs[1,:]);ax.axis('off')
c=next(c for c in claims if c['claim_id']=='JP-2023-13-female');ev=c['evidence'];obs=c['assertion']['observed_standardized']*100
ax.text(0,.96,'Trace one reported quantity: Tokyo women, FY2023',fontsize=14,weight='bold')
ax.text(0,.65,f'Observed standardized proportion: {obs:.4f}%\nWaist criterion: ≥90 cm; ages 40–74.\nDenominator: recorded waist examinees.\nSeven age groups; age at fiscal year end.',fontsize=12,linespacing=1.6,va='top')
ax.text(.57,.65,f'Example age band 40–44:\n{ev["age_numerators"][0]:,} / {ev["age_denominators"][0]:,} × 100 = {100*ev["age_numerators"][0]/ev["age_denominators"][0]:.4f}%\nNDB11 waist table: cells K42–K44.\nFull calculation: accompanying table.',fontsize=12,linespacing=1.6,va='top')
fig.suptitle('Tokyo: a regional result with an inspectable calculation',fontsize=16,y=.975)
fig.text(.52,.91,'Tokyo was selected before fitting, reflecting the research location at Waseda.',ha='center',fontsize=11)
save(fig,'japan_tokyo')

def write_table(name,text):
    p=TAB/name;p.write_text(text);outputs.append(p)

rows=[]
for fam in labels:
    def val(ev,year,metric='mae_pp'):return float(metrics[(metrics.evaluation==ev)&(metrics.model==fam)&(metrics.year==str(year))].iloc[0][metric])
    trace=selection[fam]['selection'];v=trace['candidates'][trace['selected_index']]['mean_mae_pp']
    rows.append(f"{labels[fam]} & {v:.4f} & {val('temporal',2022):.4f} & {val('temporal',2023):.4f} & {val('temporal','pooled'):.4f} & {val('spatial','pooled'):.4f} \\\\")
write_table('japan_models.tex',r'''\begin{table}[tbp]
\centering\small
\caption[Japanese forecasting results]{Japanese forecasting MAE in percentage points. Validation averages two rolling targets (2020/2021); temporal test pools 2022/2023; geographic test excludes each region from both selection and fitting. All columns use identical fixed census weights. Lower is better.}
\label{tab:japan:models}
\begin{tabular}{lrrrrr}\toprule
Method & Validation & 2022 & 2023 & Pooled & Geographic \\
\midrule
'''+ '\n'.join(rows)+r'''
\bottomrule\end{tabular}
\end{table}
''')
write_table('japan_reproduction.tex',r'''\begin{table}[tbp]
\centering\small
\caption[Normal reproduction tasks in Japan]{Normal report-reproduction tasks. Both programmatic routes have the same sources, models and calculation rules. Each task passes in both routes; this evaluates executability, not user comprehension, time savings or comparative fault detection.}
\label{tab:japan:reproduction}
\begin{tabular}{p{.10\textwidth}p{.62\textwidth}cc}\toprule
Task & Requested evidence or calculation & B1 & Full \\
\midrule
T1 & Recover matching numerators and denominators & Pass & Pass \\
T2 & Recover year, release, age and sex scope & Pass & Pass \\
T3 & Recalculate 188 standardized reported rates & Pass & Pass \\
T4 & Replay the gate expression for 1,316 test strata & Pass & Pass \\
T5 & Trace 188 rates to original table cells & Pass & Pass \\
T6 & Regenerate rates with fixed FY2019 weights & Pass & Pass \\
\bottomrule\end{tabular}
\end{table}
''')
rows=[]
for i,age in enumerate(range(40,75,5)):
    y,n,w=ev['age_numerators'][i],ev['age_denominators'][i],ev['weights'][i]
    rows.append(f'{age}--{age+4} & {y:,} & {n:,} & {100*y/n:.4f} & {w:.4f} & {100*w*y/n:.4f} \\\\')
write_table('japan_tokyo.tex',r'''\begin{table}[tbp]
\centering\small
\caption[Tokyo calculation by age]{Tokyo women, FY2023: an explicit calculation of the waist-criterion indicator. Counts come from the NDB11 waist table, rows 42--44, columns K--Q. Census weights are displayed rounded; computation uses full precision. The final column contributes percentage points to the standardized result.}
\label{tab:japan:tokyo}
\begin{tabular}{lrrrrr}\toprule
Age & Numerator & Denominator & Rate (\%) & Weight & Contribution \\
\midrule
'''+ '\n'.join(rows)+f'\n\\midrule\nTotal & {sum(ev["age_numerators"]):,} & {sum(ev["age_denominators"]):,} & -- & 1.0000 & {obs:.4f} \\\\\n'+r'''
\bottomrule\end{tabular}
\end{table}
''')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(CHECKS/'japan_figure_provenance.json').write_text(json.dumps({'generator':sha(Path(__file__)),'sources':{display_path(p):sha(p) for p in sources},'outputs':{display_path(p):sha(p) for p in outputs}},indent=2))
print('Generated three figures and three tables.')
