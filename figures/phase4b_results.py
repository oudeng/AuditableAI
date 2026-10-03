from auditableai.paths import REPO, WORK, JAPAN, EVIDENCE, FIGURES, TABLES, CHECKS, display_path, resolve_record_path, prepare_outputs, required_input
prepare_outputs()
"""Generate all formal Phase 4B figures/tables from verified aggregate evidence."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.ticker import MaxNLocator
import seaborn as sns
from scipy.special import expit
from auditableai.plotting import apply_thesis_style
apply_thesis_style(font_scale=1.3)
plt.rcParams.update({'font.size':12,'axes.labelsize':12,'xtick.labelsize':11,'ytick.labelsize':11})
D=EVIDENCE/'phase4b';OUT=FIGURES/'phase4b';OUT.mkdir(exist_ok=True)
TABLE=TABLES;outputs=[];inputs=[]
def read(path):inputs.append(path);return json.loads(path.read_text())
C=read(D/'clinical_formal_v1/summary.json');N=read(D/'nhanes_formal_v1/summary.json')
CV=read(D/'clinical_verification.json');NV=read(D/'nhanes_verification.json')
CF=read(D/'mimic_flow.json');EF=read(D/'eicu_flow.json')
AUD=read(D/'clinical_formal_v1/audit_v1/summary.json');AUDN=read(D/'nhanes_formal_v1/audit_v1/summary.json')
EXP=read(D/'nhanes_formal_v1/export_6201.json')
names={'constant':'Training constant','linear':'Linear / logistic','hgb':'Gradient boosting','gate':'Additive gates','single_gate':'Single-gate ablation'}
order=list(names);colors={'constant':'#777777','linear':'#0072B2','hgb':'#009E73','gate':'#D55E00','single_gate':'#CC79A7'}
def save(fig,name):
    for ext in ['png','svg']:
        path=OUT/(name+'.'+ext);fig.savefig(path,dpi=400,facecolor='white');outputs.append(path)
    plt.close(fig)
def box(ax,xy,w,h,text,color):
    ax.add_patch(FancyBboxPatch(xy,w,h,boxstyle='round,pad=.008',facecolor=color,edgecolor='#A9BAC8',lw=1))
    ax.text(xy[0]+w/2,xy[1]+h/2,text,ha='center',va='center',fontsize=12,linespacing=1.5)
fig,ax=plt.subplots(figsize=(12,6.8));ax.axis('off');ax.set(xlim=(0,1),ylim=(0,1))
fig.suptitle('Clinical task: what is known at the 24-hour landmark?',fontsize=19,y=.97)
for x,text in [(.02,'ICU admission\nTime 0'),(.27,'First 24 hours\nSampling AND availability'),(.55,'Prediction at 24 hours\nStill in ICU; adult'),(.79,'Subsequent outcome\nHospital mortality')]:box(ax,(x,.73),.19,.16,text,'#EDF4F8')
for x in [.22,.51,.75]:ax.annotate('',xy=(x+.035,.81),xytext=(x,.81),arrowprops={'arrowstyle':'->','color':'#36586F','lw':1.6})
box(ax,(.02,.34),.43,.27,'MIMIC-IV 3.1\n94,458 stays -> 53,439 unique adults\n32,063 train | 10,688 validation | 10,688 test\nOne eligible admission per patient','#EEF6F2')
box(ax,(.55,.34),.43,.27,'eICU-CRD 2.0\n200,859 stays -> 99,441 unique adults\n207 hospitals | 9,278 deaths\nAll models frozen before evaluation','#FFF3E9')
ax.annotate('',xy=(.545,.48),xytext=(.455,.48),arrowprops={'arrowstyle':'->','color':'#36586F'})
ax.text(.5,.65,'Frozen models',ha='center',va='bottom',fontsize=10)
box(ax,(.02,.06),.96,.16,'Shared inputs: age, sex, creatinine, glucose, potassium, sodium, bicarbonate, hemoglobin, platelets, WBC\nTraining-only imputation/scaling; no external fitting or recalibration; 9 candidates per tunable model','#F5F5F5')
fig.subplots_adjust(left=.03,right=.98,top=.90,bottom=.03);save(fig,'clinical_design')

fig,axes=plt.subplots(1,2,figsize=(12,5.7));fig.subplots_adjust(left=.17,right=.97,bottom=.20,top=.80,wspace=.75)
b=C['seeds'][0]['primary_bootstrap']
for i,k in enumerate(order):
    v=b['models'][k];lo,hi=v['ci95'];axes[0].errorbar(v['estimate'],i,xerr=[[v['estimate']-lo],[hi-v['estimate']]],fmt='o',color=colors[k],capsize=4)
axes[0].set_yticks(range(5),[names[k] for k in order]);axes[0].invert_yaxis();axes[0].set_xlabel('External Brier loss (lower is better)');axes[0].set_title('A  eICU performance')
axes[0].xaxis.set_major_locator(MaxNLocator(4))
others=['constant','linear','hgb','single_gate']
for i,k in enumerate(others):
    v=b['paired_differences']['gate_minus_'+k];lo,hi=v['ci95'];axes[1].errorbar(v['estimate'],i,xerr=[[v['estimate']-lo],[hi-v['estimate']]],fmt='o',color=colors[k],capsize=4)
axes[1].axvline(0,color='#777',lw=1,ls='--');axes[1].set_yticks(range(4),['vs '+names[k] for k in others]);axes[1].invert_yaxis();axes[1].set_xlabel('Gate loss minus comparator loss');axes[1].set_title('B  Paired contrasts')
fig.suptitle('External clinical validation: a measurable accuracy trade-off',fontsize=18,y=.96)
fig.text(.5,.075,'99,441 adults in 207 hospitals; seed 6201; 1,000 hospital-cluster bootstrap resamples.',ha='center',fontsize=11)
fig.text(.5,.03,'Unadjusted 95% intervals, conditional on the fitted models. Other seeds are reported separately.',ha='center',fontsize=11)
save(fig,'clinical_external')

fig,axes=plt.subplots(1,2,figsize=(12,5.8));fig.subplots_adjust(left=.08,right=.98,bottom=.23,top=.80,wspace=.35)
for k in ['linear','hgb','gate']:
    bins=C['seeds'][0]['calibration'][k];axes[0].plot([r['mean_predicted'] for r in bins],[r['observed'] for r in bins],marker='o',color=colors[k],label=names[k])
axes[0].plot([0,.7],[0,.7],ls='--',lw=1,color='#888');axes[0].set(xlabel='Mean predicted mortality',ylabel='Observed mortality',xlim=(0,.7),ylim=(0,.7));axes[0].legend(frameon=False,fontsize=10);axes[0].set_title('A  External calibration')
labs=['creatinine','glucose','potassium','sodium','bicarbonate','hemoglobin','platelets','wbc'];y=np.arange(len(labs))
axes[1].barh(y-.17,[100*CF['strict']['missing_fraction'][k] for k in labs],height=.32,color='#0072B2',label='MIMIC')
axes[1].barh(y+.17,[100*EF['strict']['missing_fraction'][k] for k in labs],height=.32,color='#D55E00',label='eICU')
axes[1].set_yticks(y,[k.capitalize() if k!='wbc' else 'WBC' for k in labs]);axes[1].invert_yaxis();axes[1].set_xlabel('Missing in the admissible 24-hour window (%)');axes[1].legend(frameon=False,fontsize=10);axes[1].set_title('B  Observable dataset shift')
fig.suptitle('Transporting a model changes the evidence needed for its claim',fontsize=18,y=.96)
fig.text(.5,.09,'Calibration uses pre-specified bins with at least 20 patients; no external recalibration.',ha='center',fontsize=11)
fig.text(.5,.04,'Missingness differs materially between databases. This plot does not identify its causal mechanism.',ha='center',fontsize=11)
save(fig,'clinical_transport')

fig,axes=plt.subplots(1,2,figsize=(12,5.7));fig.subplots_adjust(left=.17,right=.97,bottom=.21,top=.80,wspace=.35)
b=N['seeds'][0]['primary_bootstrap']
for i,k in enumerate(order):
    v=b['models'][k];lo,hi=v['ci95'];axes[0].errorbar(v['estimate'],i,xerr=[[v['estimate']-lo],[hi-v['estimate']]],fmt='o',color=colors[k],capsize=4)
axes[0].set_yticks(range(5),[names[k] for k in order]);axes[0].invert_yaxis();axes[0].set_xlabel('External RMSE (HbA1c percentage points)');axes[0].set_title('A  Independent 2017-2018 cycle')
x=np.linspace(15,45,250)
for i,(j,a,t,w) in enumerate([r for r in EXP['terms'] if r[0]==2]):axes[1].plot(x,expit(a*(x-t)),label=f'Midpoint {t:.4f}',lw=2)
axes[1].set(xlabel=r'BMI ($\mathrm{kg/m^2}$)',ylabel='Gate activation',ylim=(-.02,1.02));axes[1].legend(frameon=False,fontsize=10);axes[1].set_title('B  Actual fitted gate coordinates')
fig.suptitle('NHANES: external error and directly inspectable model terms',fontsize=18,y=.96)
fig.text(.5,.075,'5,261 external adults; seed 6201; 1,000 participant resamples; conditional empirical-cohort inference.',ha='center',fontsize=11)
fig.text(.5,.03,'The gate midpoints are training quantiles, not discovered clinical thresholds or causal effects.',ha='center',fontsize=11)
save(fig,'nhanes_external')

arms=AUD['freeze']['arms'];faults=AUD['freeze']['families'];mat=np.array([[next(r['rejected']/r['n'] for r in AUD['aggregates'] if r['arm']==a and r['family']==f) for f in faults] for a in arms])
fig,ax=plt.subplots(figsize=(12.4,6.6));fig.subplots_adjust(left=.20,right=.97,bottom=.29,top=.80)
sns.heatmap(mat,annot=True,fmt='.0%',vmin=0,vmax=1,cmap='Blues',cbar=False,linewidths=.5,ax=ax,annot_kws={'size':10})
ax.set_xticklabels(['Clean','Term\norder','Comment','Target\nscope','Outcome\nunit','Gate\nshift','Coefficient\nshift','Reference\nID','Joint\nstale','Remote\ngate'],rotation=0,fontsize=10)
ax.set_yticklabels(['Schema only','Conventional strong','Components, unbound','Full','Without scope','Without transform','Without replay','Without dependency'],rotation=0,fontsize=11)
ax.axvline(3,color='#555',lw=2);ax.text(1.5,-.18,'Valid / equivalent',ha='center',fontsize=11);ax.text(6.5,-.18,'Injected invalid bundles',ha='center',fontsize=11)
fig.suptitle('Controlled audit challenge: fraction of submitted bundles rejected',fontsize=17,y=.96)
fig.text(.5,.14,'The two applications have the same cell counts: 90 variants per column in each application.',ha='center',fontsize=11)
fig.text(.5,.085,'Full and the conventional strong control tie. Removing scope or dependency binding creates specific misses.',ha='center',fontsize=11)
fig.text(.5,.035,'Repeated probes/magnitudes share models; these are finite checks, not population error-detection rates.',ha='center',fontsize=11)
save(fig,'audit_ablation')

def table_file(name,text):
    p=TABLE/name;p.write_text(text);outputs.append(p)
def start(caption,label,cols,header):
    short={'tab:phase4b:clinical':'External clinical performance','tab:phase4b:nhanes':'External NHANES prediction errors','tab:phase4b:audit':'Controlled audit challenge outcomes'}[label]
    return '\\begin{table}[tbp]\n\\centering\\small\n\\caption['+short+']{'+caption+'}\n\\label{'+label+'}\n\\begin{tabular}{'+cols+'}\n\\toprule\n'+header+r'\\'+'\n\\midrule\n'
end='\\bottomrule\n\\end{tabular}\n\\end{table}\n'
t=start('External clinical performance at seed 6201. The additive gate model is a new thesis implementation, not the published LGO GP. Lower Brier loss is better.','tab:phase4b:clinical','@{}lrrr@{}','Model & Brier & AUROC & AUPRC')
for k in order:
    r=next(r for r in CV['reportable_metrics'] if r['seed']==6201 and r['split']=='external' and r['model']==k)
    t+=names[k]+f" & {r['brier']:.4f} & {r['auroc']:.4f} & {r['auprc']:.4f}"+r'\\'+'\n'
table_file('phase4b_clinical.tex',t+end)
t=start('External NHANES prediction errors across three development splits. The same 5,261 external adults are reused, so the columns are robustness checks, not independent replications.','tab:phase4b:nhanes','@{}lrrr@{}','Model & Seed 6201 & Seed 6202 & Seed 6203')
for k in order:t+=names[k]+' & '+' & '.join(f"{next(r['rmse'] for r in N['metrics'] if r['seed']==s and r['split']=='external' and r['model']==k):.4f}" for s in [6201,6202,6203])+r'\\'+'\n'
table_file('phase4b_nhanes.tex',t+end)
t=start('Finite audit challenge outcomes per application: 630 injected invalid and 270 valid/equivalent bundles. Full and the conventional strong control tie; repeated variants do not justify binomial population intervals. Table~\\ref{tab:phase4b:audit-mechanisms} allocates the counts to fault families.','tab:phase4b:audit','@{}lrr@{}','Audit arm & Invalid accepted & Valid retained')
for a,label in zip(arms,['Schema only','Conventional strong','Components, unbound','Full','Without scope','Without transform','Without replay','Without dependency']):
    rows=[r for r in AUD['aggregates'] if r['arm']==a];bad=sum(r['n']-r['rejected'] for r in rows if r['invalid_truth']);valid=sum(r['n']-r['rejected'] for r in rows if not r['invalid_truth'])
    t+=f'{label} & {bad}/630 & {valid}/270'+r'\\'+'\n'
table_file('phase4b_audit.tex',t+end)
manifest={'generator':display_path(Path(__file__)),'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'sources':[{'path':display_path(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(set(inputs))],'outputs':[{'path':display_path(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in outputs],'notes':'Verified aggregates only; no patient-level records; no simulated effect sizes.'}
(CHECKS/'phase4b_figure_provenance.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'figures':5,'table_files':3,'outputs':len(outputs)}))
