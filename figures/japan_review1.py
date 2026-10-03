from auditableai.paths import REPO, WORK, JAPAN, EVIDENCE, FIGURES, TABLES, CHECKS, display_path, resolve_record_path, prepare_outputs, required_input
prepare_outputs()
"""Figures and complete seven-field record from the post-hoc review evidence."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.special import expit

from auditableai.plotting import apply_thesis_style
apply_thesis_style(font_scale=1.25)
D=JAPAN/'review1_v1'
O=FIGURES/'japan_health'
T=TABLES
outputs=[]

def save(fig,name):
    for ext in ['png','svg']:
        p=O/f'{name}.{ext}';fig.savefig(p,dpi=330,bbox_inches='tight');outputs.append(p)
    plt.close(fig)

def esc(s):
    s=str(s).replace('東京都','Tokyo').replace('腹囲','waist circumference (Japanese sheet name retained in JSON)')
    s=s.replace('–','--').replace('≥',r'$\geq$')
    for a,b in [('&',r'\&'),('%',r'\%'),('_',r'\_'),('#',r'\#')]:s=s.replace(a,b)
    return s

yearly=pd.read_csv(D/'observed_yearly_changes.csv')
scores=pd.read_csv(D/'yearly_model_metrics.csv')
labels=dict(persistence='Persistence',trend='Damped trend',linear='Ridge',gam='Spline',hgb='Boosting',gate='Gate')
colors=dict(zip(labels,sns.color_palette('colorblind',6)))
fig,axes=plt.subplots(1,2,figsize=(11.5,4.5))
fig.subplots_adjust(bottom=.23,wspace=.28,top=.84)
for sex,color,label in [('male','#0072B2','Men'),('female','#D55E00','Women')]:
    s=yearly[yearly.sex==sex].groupby('year').change_pp.mean()
    axes[0].plot(s.index,s,marker='o',color=color,label=label,lw=2)
axes[0].axhline(0,color='.45',lw=.8)
axes[0].axvspan(2019.5,2021.5,color='#F2E4CF',alpha=.5,zorder=-1)
axes[0].set(title='A  Observed annual change',xlabel='Fiscal year (target)',ylabel='Mean standardized change (pp)',xticks=[2016,2018,2020,2021,2022,2023])
axes[0].legend(frameon=False,loc='lower left',fontsize=10)
for fam in labels:
    s=scores[scores.model==fam].sort_values('year')
    axes[1].plot(s.year,s.mae_pp,marker='o',lw=2 if fam in ['gate','trend'] else 1.2,
                 color=colors[fam],ls='--' if fam in ['persistence','trend'] else '-',label=labels[fam])
axes[1].axvspan(2019.8,2021.5,color='#F2E4CF',alpha=.5,zorder=-1)
axes[1].set(title='B  Selected configurations, by year',xlabel='Fiscal year (target)',ylabel='MAE (pp)',xticks=[2020,2021,2022,2023],xlim=(2019.8,2023.2))
axes[1].legend(frameon=False,ncol=3,loc='upper center',bbox_to_anchor=(.5,-.20),fontsize=9)
fig.suptitle('Direction reversal and the validation-to-test comparison',fontsize=16)
fig.text(.02,.025,'Shading: the two selection years. Panel A averages 47 prefectures within sex.\nPanel B uses rolling fits for 2020/2021 and the frozen final model for 2022/2023.',fontsize=10)
save(fig,'japan_review_time')

z=pd.read_csv(D/'gate_stratum_decomposition.csv')
fig,axes=plt.subplots(1,2,figsize=(11.5,4.5));fig.subplots_adjust(bottom=.22,wspace=.28,top=.83)
bins=np.linspace(-1.5,2.5,45)
for m,label,color in [(z.year<=2021,'Fit inputs 2017-2021','#0072B2'),(z.year>=2022,'Test inputs 2022-2023','#D55E00')]:
    sns.histplot(x=100*z.loc[m,'delta'],bins=bins,stat='density',element='step',fill=False,
                 common_norm=False,color=color,label=label,ax=axes[0],linewidth=1.7)
axes[0].axvline(0,color='.5',lw=.8);axes[0].set(xlabel='Previous annual change (pp)',ylabel='Density',title='A  Observed input distributions')
axes[0].legend(frameon=False,fontsize=10)
ex=json.loads((JAPAN/'formal_v1/gate_expression.json').read_text())
grid=np.linspace(-1.5,2.5,501)
for color,(j,a,t,b) in zip(['#0072B2','#009E73','#D55E00'],[t for t in ex['terms'] if t[0]==3]):
    axes[1].plot(grid,expit(a*(grid/100-t)),color=color,lw=2,label=f'Location {100*t:.4f} pp')
    axes[1].plot([100*t],[.5],marker='o',color=color,ms=4)
axes[1].axhline(.1,color='.5',ls=':',lw=1);axes[1].axvspan(-1.5,0,color='#E6EDF1',zorder=-1)
axes[1].set(xlabel='Previous annual change (pp)',ylabel='Gate activation',title='B  Three retained change gates',ylim=(-.025,1.025))
axes[1].legend(frameon=False,fontsize=9,loc='upper left')
fig.suptitle('A declared gate can be weakly active on the inputs that matter',fontsize=16)
fig.text(.02,.025,'Panel A uses recorded strata. Panel B shows the gate functions on an artificial input grid.\nThe dotted line marks the descriptive low-activation rule, g < 0.1; negative change is shaded.',fontsize=10)
save(fig,'japan_review_activity')

# Render every populated leaf of the example record, including all source hashes
# and count/weight vectors. Only presentation rounding and Japanese-name glosses
# differ from the linked full-precision JSON.
c=json.loads((D/'tokyo_2023_female_record.json').read_text())
lines=[r'\begingroup\small',r'\setlength{\tabcolsep}{4pt}',
       r'\begin{longtable}{@{}p{.27\textwidth}p{.69\textwidth}@{}}',
       r'\caption[Complete Tokyo seven-field record]{Complete populated record JP-2023-13-female, version v0.6-review1. Every leaf of the seven fields is displayed. Counts and hashes are exact; calculated decimals are rounded to four places, with full precision in \texttt{tokyo\_2023\_female\_record.json}. Tokyo and the waist worksheet are translated for the printed English record. Paths below are relative to the Japanese evidence directory. Persistence and trend have identical hashes because both serialized model files contain a \texttt{None} placeholder, not a fitted estimator. Their distinct prediction rules are defined in \texttt{}\allowbreak\texttt{experiments/}\allowbreak\texttt{japan\_health/}\allowbreak\texttt{run\_formal.py} (relative to this repository); \path{formal_v1/selection.json} records the trend damping value 0.25. The hash alone does not identify either baseline rule.}\label{tab:app:japan:complete-record}\\',
       r'\toprule Field / entry & Recorded value \\ \midrule\endfirsthead',
       r'\multicolumn{2}{l}{\textit{Tokyo record (continued)}}\\\toprule Field / entry & Recorded value\\\midrule\endhead',
       r'\midrule\multicolumn{2}{r}{\textit{Continued on next page}}\\\endfoot',
       r'\bottomrule\endlastfoot']
def value(v):
    if isinstance(v,float):return f'{v:.4f}'
    if isinstance(v,list):return '['+', '.join(value(i) for i in v)+']'
    s=str(v)
    if len(s)==64 and all(a in '0123456789abcdef' for a in s):return r'\nolinkurl{'+s+'}'
    return esc(s)
def leaves(obj,prefix=''):
    for k,v in obj.items():
        key=prefix+k
        if isinstance(v,dict):yield from leaves(v,key+'.')
        else:yield key,v
fieldnames={'clm':'Assertion','scp':'Scope and estimand','art':'Inspectable artifact','ref':'Reference','pro':'Protocol','evd':'Evidence','bnd':'Boundary and disposition'}
leafcount=0
for field,label in fieldnames.items():
    lines.append(r'\multicolumn{2}{@{}l}{\textbf{'+label+r' ($\mathsf{'+field+r'}$)}}\\*')
    for key,v in leaves(c[field]):
        rendered = (r';\newline'.join(r'\path{'+x.strip()+'}' for x in v.split(';'))
                    if key == 'diagnostic_evidence' else value(v))
        lines.append(esc(key.replace('.', ': ').replace('_', ' '))+' & '+rendered+r' \\')
        leafcount+=1
    lines.append(r'\addlinespace')
lines += [r'\end{longtable}',r'\endgroup']
p=T/'japan_complete_record.tex';p.write_text('\n'.join(lines)+'\n');outputs.append(p)
# Short list-of-tables captions keep the navigation pages concise.
for name,short in {
    'japan_yearly_selection.tex':'Annual Japanese forecasting errors',
    'japan_error_decomposition.tex':'Exact decomposition of Japanese forecast error',
    'japan_gate_activity.tex':'Empirical activity of previous-change gates',
}.items():
    p=T/name
    text=p.read_text()
    if r'\caption{' in text:text=text.replace(r'\caption{',r'\caption['+short+']{',1)
    p.write_text(text);outputs.append(p)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(CHECKS/'japan_review1_figure_provenance.json').write_text(json.dumps({'generator_sha256':sha(Path(__file__)),'record_leaf_count':leafcount,'sources':{display_path(p):sha(p) for p in D.glob('*') if p.is_file()},'outputs':{display_path(p):sha(p) for p in outputs}},indent=2)+'\n')
print('Generated two figures and the complete record:',leafcount,'leaf entries.')
