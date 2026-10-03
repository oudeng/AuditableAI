from auditableai.paths import REPO, WORK, JAPAN, EVIDENCE, FIGURES, TABLES, CHECKS, display_path, resolve_record_path, prepare_outputs, required_input
prepare_outputs()
"""Generate one source-reported chart and two analytical LGO figures.

No model fitting, clinical data, or published-study correction is performed.
"""
from pathlib import Path
import hashlib,json,re,os,sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from matplotlib.ticker import FuncFormatter
from auditableai.plotting import apply_thesis_style

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
outdir=FIGURES
records=[]
def save(fig,name,kind,sources,details):
    paths=[]
    for ext in ['png','svg']:
        p=outdir/f'{name}.{ext}'
        fig.savefig(p,dpi=400,bbox_inches='tight')
        paths.append({'path':display_path(p),'sha256':sha(p)})
    plt.close(fig)
    records.append({'name':name,'kind':kind,'sources':[{'path':display_path(p),'sha256':sha(p)} for p in sources],
      'details':details,'outputs':paths,'generator':display_path(Path(__file__)),'generator_sha256':sha(Path(__file__))})

apply_thesis_style(font_scale=1.25)
rps=EVIDENCE/'papers/rps/family_means.json'
data=[(x['family'],x['mean_score']) for x in json.loads(rps.read_text())['values']]
assert len(data)==18 and data[0]==('RNN_v2',7955.5)
fig,ax=plt.subplots(figsize=(8.0,6.7))
y=np.arange(len(data));values=np.array([r[1] for r in data])
ax.barh(y,values,color=np.where(values>=0,'#337B95','#AA6070'),height=.72)
ax.set_yticks(y,[r[0] for r in data]);ax.invert_yaxis()
ax.axvline(0,color='#6c7477',lw=.8)
for yi,v in zip(y,values):
    ax.text(v+(350 if v < -5000 else (250 if v>=0 else -250)),yi,f'{v:,.4f}',va='center',
            ha='left' if v>=0 or v < -5000 else 'right',fontsize=9.5,
            color='white' if v < -5000 else '#222222')
ax.set_xlim(-23000,14500)
ax.xaxis.set_major_formatter(FuncFormatter(lambda x,p:f'{x:,.0f}'))
ax.set_xlabel('Reported mean cumulative net score')
ax.set_title('Core-54: descriptive family means',loc='left',pad=12)
ax.grid(axis='x',alpha=.16);ax.set_axisbelow(True)
sns.despine(ax=ax,left=True)
fig.tight_layout()
save(fig,'rps_family_means','redraw of published aggregate values',[rps],
     {'locator':'tab:type_summary','values':[{'family':n,'mean_score':v} for n,v in data],
      'uncertainty':'No error bars; not a new statistical test or tournament run.'})

z=np.linspace(-2.5,2.5,1201)
sig=lambda v:1/(1+np.exp(-v))
fig,axes=plt.subplots(1,3,figsize=(9,3.2),layout='constrained')
palette=sns.color_palette('colorblind',3)
for a,c,ls in zip([1,4,16],palette,['-','--',':']):
    h=sig(a*z)
    axes[0].plot(z,h,color=c,ls=ls,label=rf'$\alpha = {a}$',lw=1.7)
    axes[1].plot(z,z*h,color=c,ls=ls,lw=1.7)
    axes[2].plot(z,a*h*(1-h),color=c,ls=ls,lw=1.7)
for ax,t in zip(axes,['Pure gate g(z)','Magnitude-weighted m(z)','Pure-gate derivative']):
    ax.set_title(t,fontsize=11);ax.set_xlabel('Standardized input z')
    ax.axvline(0,color='#666666',lw=.6,ls=':');ax.grid(alpha=.12)
    ax.tick_params(labelsize=9)
axes[0].axhline(.5,color='#666666',lw=.6,ls=':')
axes[0].legend(frameon=False,fontsize=9,loc='upper left')
axes[0].set_ylim(-.03,1.04)
save(fig,'lgo_operator_family','analytical function illustration',
     [EVIDENCE/'papers/lgo/exemplar.json'],
     {'tau':0,'alpha':[1,4,16],'equations':['sigmoid(a*z)','z*sigmoid(a*z)','a*h*(1-h)'],
      'data':'No fitted curves, patient data or empirical uncertainty.'})

lgo=EVIDENCE/'papers/lgo/exemplar.json'
parameters=json.loads(lgo.read_text())
assert parameters['GCS']=={'slope':1.313,'midpoint':0.5767}
assert parameters['RR']=={'slope':3.9457,'midpoint':-1.4398}
fig,axes=plt.subplots(1,2,figsize=(7.4,3.1),layout='constrained')
for ax,label,curve,b,c in [
 (axes[0],'GCS component',sig(1.313*(-z+.5767)),.5767,palette[0]),
 (axes[1],'Respiratory-rate component',sig(3.9457*(z+1.4398)),-1.4398,palette[1])]:
    ax.plot(z,curve,color=c,lw=2)
    ax.axhline(.5,color='#777777',ls=':',lw=.8)
    ax.axvline(b,color='#777777',ls='--',lw=.8)
    ax.scatter([b],[.5],color=c,s=28,zorder=3)
    ax.text(b+.13,.56,f'z* = {b:.4f}',fontsize=10)
    ax.set(title=label,xlabel='Standardized feature coordinate',ylabel='Gate value',ylim=(-.03,1.04))
    ax.grid(alpha=.12)
save(fig,'lgo_published_components','evaluation of published standardized expression components',[lgo],
     {'locator':'eq:eicu-exemplar','components':{'GCS':{'slope':1.313,'argument':'-z+0.5767','half_gate_z':.5767},
      'RR':{'slope':3.9457,'argument':'z+1.4398','half_gate_z':-1.4398}},
      'data':'No patient records or natural-unit transformation; no performance claim.'})
(CHECKS/'ch04_ch05_figure_provenance.json').write_text(json.dumps(records,indent=2)+'\n')
print('Generated three figures with source fingerprints; 18 RPS means parsed from the published source.')
