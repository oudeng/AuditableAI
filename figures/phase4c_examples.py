from auditableai.paths import REPO, WORK, JAPAN, EVIDENCE, FIGURES, TABLES, CHECKS, display_path, resolve_record_path, prepare_outputs, required_input
prepare_outputs()
"""Accessible case figures, preserving frozen formal and exploratory provenance."""
from pathlib import Path
import sys,json,hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from auditableai.plotting import apply_thesis_style
apply_thesis_style(font_scale=1.5)
plt.rcParams.update({'font.size':15,'axes.labelsize':14,'xtick.labelsize':13,'ytick.labelsize':13})
D=EVIDENCE;sources=[];outputs=[]
def read(p):sources.append(p);return json.loads(p.read_text())
C=read(D/'phase4b/clinical_formal_v1/summary.json');N=read(D/'phase4b/nhanes_formal_v1/summary.json');E=read(D/'phase4c/summary.json')
OUT=FIGURES/'phase4c';OUT.mkdir(exist_ok=True)
def save(fig,name):
    for ext in ['png','svg']:
        p=OUT/(name+'.'+ext);fig.savefig(p,dpi=400);outputs.append(p)
    plt.close(fig)
def box(ax,x,y,w,h,text,color='#EFF5F8',size=14):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.01',edgecolor='#9DB2C1',facecolor=color))
    ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=size,linespacing=1.5)

fig,axes=plt.subplots(1,2,figsize=(10.5,5.8));fig.subplots_adjust(left=.17,right=.97,bottom=.30,top=.76,wspace=.63)
for ax,d,title,metric in zip(axes,[C,N],['Clinical: 99,441 adults','NHANES: 5,261 adults'],['Brier difference','RMSE difference']):
    contrasts=d['seeds'][0]['primary_bootstrap']['paired_differences']
    for i,(key,label,color) in enumerate([('linear','Linear','#0072B2'),('hgb','Boosting','#009E73'),('single_gate','Single gate','#CC79A7')]):
        r=contrasts['gate_minus_'+key];lo,hi=r['ci95'];v=r['estimate'];ax.errorbar(v,i,xerr=[[v-lo],[hi-v]],fmt='o',color=color,capsize=4,lw=2)
    ax.axvline(0,color='#667',lw=1,ls='--');ax.set_yticks(range(3),['vs linear','vs boosting','vs single gate']);ax.invert_yaxis();ax.set_title(title,fontsize=15,pad=14);ax.set_xlabel(metric+'\n(gates minus comparator)')
axes[1].set_xticks([-.01,-.005,0],['−0.010','−0.005','0'])
fig.suptitle('A representation can be inspectable without being the best predictor',fontsize=17,y=.96)
fig.text(.5,.065,'Left of zero: gates have lower error. Right of zero: comparator has lower error.',ha='center',fontsize=12)
save(fig,'external_comparisons')

time=[r for r in C['seeds'][0]['availability_sensitivity'] if r['dataset']=='eicu'][0]
fig,ax=plt.subplots(figsize=(10.5,5.8));fig.subplots_adjust(left=.025,right=.975,top=.88,bottom=.035);ax.axis('off');ax.set(xlim=(0,1),ylim=(0,1))
fig.suptitle('1  Was the information available at the prediction deadline?',fontsize=17,y=.97)
ax.annotate('',xy=(.95,.64),xytext=(.05,.64),arrowprops={'arrowstyle':'->','lw':2,'color':'#557080'})
ax.axvline(.59,ymin=.49,ymax=.88,color='#D55E00',ls='--',lw=2)
box(ax,.05,.72,.35,.13,'Sample collected within 24 hours')
box(ax,.66,.72,.28,.13,'Result entered later','#FFF0E5')
ax.text(.59,.91,'24-hour deadline',ha='center',color='#A64416',fontsize=14)
ax.text(.08,.55,'ICU admission',ha='left',fontsize=12)
ax.text(.50,.40,'Illustrative timing; no individual patient record is shown.',ha='center',fontsize=12,color='#5C6973')
box(ax,.05,.08,.27,.24,f"Available by deadline\nBrier {time['strict_brier']:.4f}",size=15)
box(ax,.37,.08,.27,.24,f"Sampling time only\nBrier {time['measurement_only_brier']:.4f}",'#FFF0E5',size=15)
box(ax,.69,.08,.26,.24,f"{100*time['fraction_prediction_change_over_001']:.4f}% of predictions\nchange by >1\npercentage point",size=13)
save(fig,'example_time')

ss=E['cohort_subset']['rows'];fig,axes=plt.subplots(1,2,figsize=(10.5,5.6));fig.subplots_adjust(left=.10,right=.97,bottom=.25,top=.76,wspace=.40)
axes[0].barh([0],[ss[1]['coverage']*100],color='#0072B2',height=.46);axes[0].barh([0],[ss[2]['coverage']*100],left=[ss[1]['coverage']*100],color='#D6DDE3',height=.46)
axes[0].text(100*ss[1]['coverage']/2,0,f"Retained\n{ss[1]['n']:,}",ha='center',va='center',color='white',fontsize=14)
axes[0].text(100*ss[1]['coverage']+100*ss[2]['coverage']/2,0,f"Omitted\n{ss[2]['n']:,}",ha='center',va='center',fontsize=12)
axes[0].set(xlim=(0,100),ylim=(-.8,.8),xlabel='Evaluation population (%)',yticks=[]);axes[0].set_title('Who remains in the report?',fontsize=15,pad=16)
vals=[s['brier'] for s in ss];bars=axes[1].bar(range(3),vals,color=['#697A87','#0072B2','#D6DDE3'],width=.58)
for b,v in zip(bars,vals):axes[1].text(b.get_x()+b.get_width()/2,v+.004,f'{v:.4f}',ha='center',fontsize=13)
axes[1].set_xticks(range(3),['Everyone','Retained','Omitted']);axes[1].set(ylabel='Brier loss (lower is better)',ylim=(0,.175));axes[1].set_title('The model itself is unchanged',fontsize=15,pad=16)
fig.suptitle('2  Did the prediction improve, or did the denominator change?',fontsize=17,y=.97)
fig.text(.5,.09,f"Validation-derived cutoff retains {100*ss[1]['coverage']:.4f}% of external adults.",ha='center',fontsize=13)
fig.text(.5,.04,'The lower retained-group loss is valid only with that restricted scope.',ha='center',fontsize=13)
save(fig,'example_population')

u=E['unit_conversion']['rows'];fig,axes=plt.subplots(1,2,figsize=(10.5,5.6));fig.subplots_adjust(left=.04,right=.97,bottom=.23,top=.79,wspace=.35)
axes[0].axis('off');axes[0].set(xlim=(0,1),ylim=(0,1))
box(axes[0],.06,.64,.87,.22,'90 cm = 900 mm',size=21)
box(axes[0],.06,.17,.87,.29,'The model expects centimeters.\nConvert declared millimeters\nback by dividing by ten.',size=14)
axes[0].annotate('',xy=(.5,.48),xytext=(.5,.62),arrowprops={'arrowstyle':'->','lw':2,'color':'#557080'})
vals=[r['rmse'] for r in u[:3]]
axes[1].plot(range(3),vals,marker='o',ms=8,lw=2,color='#0072B2')
for i,v in enumerate(vals):axes[1].text(i,v+.014,f'{v:.4f}',ha='center',fontsize=12)
axes[1].set_xlim(-.35,2.35)
axes[1].set_yticks([1,1.05,1.10,1.15])
axes[1].set_xticks(range(3),['Original\ncentimeters','Millimeters\nunconverted','Correctly\nconverted']);axes[1].set(ylabel='RMSE (HbA1c percentage points)',ylim=(.96,1.16));axes[1].set_title('Same model; all 5,261 adults',fontsize=15,pad=16)
fig.suptitle('3  Do the numbers still represent the same measurement?',fontsize=17,y=.97)
fig.text(.5,.055,'Correct normalization restores the original predictions; no refitting or outcome access.',ha='center',fontsize=13)
save(fig,'example_units')

t=r'''\begin{table}[tbp]
\centering\small
\caption[Three examples and the claims they change]{A reader-facing summary of the three selected illustrations. Their numerical effects measure different quantities and are not pooled. Population and unit examples are exploratory extensions of the frozen primary fits.}
\label{tab:cases:summary}
\begin{tabularx}{\textwidth}{@{}p{.17\textwidth}YY@{}}
\toprule
Dependency & Observable result & Warranted interpretation\\
\midrule
Information time & Brier 0.0806 to 0.0804 using sampling time alone & Slightly better score cannot certify a prediction using only information available by 24 hours.\\
Population & Brier 0.0467 for 66.6586\% retained, versus 0.0806 for everyone & Lower subset error is conditional; the all-person result is unchanged.\\
Input units & RMSE 1.0053 to 1.1034 with unconverted millimeters, then 1.0053 after conversion & Declared-unit normalization restores the same predictor, not an improved fit.\\
\bottomrule
\end{tabularx}
\end{table}
'''
path=TABLES/'phase4c_examples.tex';path.write_text(t);outputs.append(path)
manifest={'generator':display_path(Path(__file__)),'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'sources':[{'path':display_path(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sources],'outputs':[{'path':display_path(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in outputs],'scope':'One formal comparison figure and three editorially selected illustrations. Two are new exploratory extensions; no new model selection.'}
(CHECKS/'phase4c_figure_provenance.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'figures':4,'tables':1}))
