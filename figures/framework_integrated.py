from auditableai.paths import REPO, WORK, JAPAN, EVIDENCE, FIGURES, TABLES, CHECKS, display_path, resolve_record_path, prepare_outputs, required_input
prepare_outputs()
"""Combined framework/study-interface schematic for the second internal review.

This is a conceptual diagram. It contains no experimental performance claims.
"""
from pathlib import Path
import sys,json,hashlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import seaborn as sns

from auditableai.plotting import apply_thesis_style
apply_thesis_style(font_scale=1.1)
fig,ax=plt.subplots(figsize=(10.8,7.0))
fig.subplots_adjust(left=.015,right=.985,bottom=.02,top=.98)
ax.set(xlim=(0,12),ylim=(0,8));ax.axis('off')
colors=sns.color_palette('colorblind',4)
def box(x,y,w,h,title,body,color='#EEF4F7',size=12):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.025',facecolor=color,edgecolor='#728894',linewidth=1))
    ax.text(x+w/2,y+h-.20,title,ha='center',va='top',fontsize=13,fontweight='bold')
    ax.text(x+w/2,y+.20,body,ha='center',va='bottom',fontsize=size,linespacing=1.45)
def arrow(a,b):
    ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'-|>','lw':1.3,'color':'#486272','shrinkA':3,'shrinkB':3})
ax.text(6,7.85,'Four supports expose different objects for a shared examination',ha='center',va='top',fontsize=16,fontweight='bold')
studies=[('RPS  |  R1 / R2','Roster + decision log\nPopulation and local regret'),('LGO  |  R2','Expression + transform\nGate location and activity'),('VERA  |  R3','Readout + fixed host\nMeaning-matched reference'),('CaST  |  R1 / R4','Graph + candidate index\nPermitted information')]
for i,(title,body) in enumerate(studies):
    x=.2+3*i;box(x,5.97,2.65,1.22,title,body,size=10.6);arrow((x+1.325,5.96),(x+1.325,5.55))
box(.2,3.43,11.65,2.10,'One claim record: preserve the identities passed between checks','',color='#F0F5ED')
fields=[('clm','Assertion','What is claimed?'),('scp','Scope','For whom / when?'),('art','Artifact','Which object?'),('ref','Reference','Compared with what?'),('pro','Protocol','How was it tested?'),('evd','Evidence','Which source / run?'),('bnd','Boundary','What follows?')]
for i,(key,title,question) in enumerate(fields):
    x=.32+i*1.64
    ax.text(x+.76,4.87,key,ha='center',va='center',fontsize=13,fontweight='bold',color='#2E5971')
    ax.text(x+.76,4.47,title,ha='center',va='center',fontsize=11)
    ax.text(x+.76,4.10,question,ha='center',va='center',fontsize=9.5)
    if i<6:ax.plot([x+1.57,x+1.57],[3.91,5.02],color='#CDD7CB',lw=.8)
ax.text(6,3.65,'R1: claim + scope     R2: artifact     R3: reference     R4: protocol     R5: evidence + revision',ha='center',fontsize=10.2)
checks=[('Semantic check','Target, population, units\nmatch the stated meaning'),('Empirical check','Model + reference + protocol\nyield the declared comparison'),('Dependency check','Transform, host and source\nbelong to the same version')]
for i,(title,body) in enumerate(checks):
    x=.25+4*i;arrow((x+1.73,3.40),(x+1.73,2.99));box(x,1.72,3.46,1.24,title,body,size=11)
    arrow((x+1.73,1.69),(x+1.73,1.33))
box(.25,.42,11.46,.88,'Recorded disposition','Supported in scope  /  narrowed  /  unsupported by the test  /  unresolved',color='#EDF3F7',size=11.8)
ax.text(6,.12,'A mismatch identifies the object, scope or reference requiring revision',ha='center',fontsize=10.8)
outputs=[]
for ext in ['png','svg']:
    p=FIGURES/('framework_integrated.'+ext);fig.savefig(p,dpi=350,bbox_inches='tight');outputs.append(p)
plt.close(fig)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
(CHECKS/'internal_review2_framework_figure.json').write_text(json.dumps({'kind':'conceptual synthesis; no measured outcomes','generator':display_path(Path(__file__)),'generator_sha256':sha(Path(__file__)),'source':'docs/FRAMEWORK.md','source_sha256':sha(REPO/'docs/FRAMEWORK.md'),'outputs':[{'path':display_path(p),'sha256':sha(p)} for p in outputs]},indent=2)+'\n')
