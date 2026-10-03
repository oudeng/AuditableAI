from auditableai.paths import REPO, WORK, JAPAN, EVIDENCE, FIGURES, TABLES, CHECKS, display_path, resolve_record_path, prepare_outputs, required_input
prepare_outputs()
"""Mechanism figures for the thesis. All numerical examples are labeled illustrations."""
from pathlib import Path
import hashlib
import json
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
from auditableai.plotting import apply_thesis_style

OUT = FIGURES/'mechanisms'
OUT.mkdir(parents=True, exist_ok=True)
apply_thesis_style()
plt.rcParams.update({'font.size':15, 'axes.labelsize':15, 'xtick.labelsize':13, 'ytick.labelsize':13, 'mathtext.fontset':'dejavusans'})
COL = {'scope':'#0072B2','artifact':'#009E73','reference':'#D55E00','protocol':'#56A4AF','evidence':'#8562A9','ink':'#233444','light':'#EFF4F7'}
records = []


def canvas(height=6.8):
    fig, ax = plt.subplots(figsize=(11.8,height))
    fig.subplots_adjust(left=.015,right=.985,bottom=.02,top=.985)
    ax.set_xlim(0,12); ax.set_ylim(0,height); ax.axis('off')
    return fig, ax


def box(ax, x,y,w,h,title,body='',color='scope',size=15):
    c=COL.get(color,color)
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.045,rounding_size=0.10',facecolor='white',edgecolor=c,linewidth=1.7,zorder=3))
    ax.plot([x+.1,x+w-.1],[y+h-.43,y+h-.43],color=c,lw=1.1,zorder=4)
    ax.text(x+w/2,y+h-.22,title,ha='center',va='center',fontsize=size,fontweight='bold',color=c,zorder=5)
    if body:ax.text(x+w/2,y+(h-.45)/2,body,ha='center',va='center',fontsize=size-1,color=COL['ink'],linespacing=1.45,zorder=5)


def arrow(ax,start,end,color='ink',style='-',rad=0):
    ax.add_patch(FancyArrowPatch(start,end,arrowstyle='-|>',mutation_scale=17,lw=1.6,color=COL.get(color,color),linestyle=style,connectionstyle=f'arc3,rad={rad}',zorder=2))


def text(ax,x,y,value,size=15,**kw):
    ax.text(x,y,value,fontsize=size,color=COL['ink'],ha='center',va='center',**kw)


def save(fig,name,sources,meaning):
    outputs=[]
    for ext in ['png','svg']:
        p=OUT/(name+'.'+ext);fig.savefig(p,dpi=400,facecolor='white')
        outputs.append({'path':display_path(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    records.append({'figure':name,'kind':'original mechanism illustration','meaning':meaning,'thesis_source_locators':sources,'source_note':'Original manuscript locators, not files distributed in this repository; see docs/FRAMEWORK.md','outputs':outputs,'generator':display_path(Path(__file__).resolve()),'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
    plt.close(fig)


fig,ax=canvas()
text(ax,6,6.42,'From a proposed claim to an examinable result',21,fontweight='bold')
positions=[(.55,4.15),(4.5,4.15),(8.45,4.15),(8.45,1.12),(4.5,1.12)]
titles=['R1  Specify','R2  Expose','R3  Choose a reference','R4  Evaluate','R5  Preserve and revise']
bodies=['Target, population, time\nand allowed information','Model, expression, readout\nor retrieval candidates','Meaning-matched truth,\ncontrol or behavioral test','Matched information;\npaired units; uncertainty','Bind inputs to outputs;\nrecord limits and changes']
colors=['scope','artifact','reference','protocol','evidence']
for (x,y),title,body,color in zip(positions,titles,bodies,colors):box(ax,x,y,3,1.55,title,body,color)
for start,end in [((3.6,4.92),(4.43,4.92)),((7.56,4.92),(8.39,4.92)),((9.95,4.09),(9.95,2.73)),((8.39,1.9),(7.56,1.9)),((4.44,1.9),(3.61,1.9))]:arrow(ax,start,end)
box(ax,.55,1.12,3,1.55,'Evidence-bearing result','Supported, narrowed,\nunsupported or unresolved','evidence')
# One directed feedback path, attached to the two box boundaries.
arrow(ax,(2.05,2.74),(2.05,4.08),'evidence','--')
text(ax,.94,3.38,'Revise\nif needed',13)
text(ax,6,3.38,'The record travels with the task; an unsupported link triggers revision.',14)
text(ax,6,.42,'An audit may retain the model while changing what can be claimed about it.',14)
save(fig,'audit_execution_loop',['Thesis_workspace/02_outline/framework_spec.md'],'Operational framework, not measured effectiveness.')

fig,ax=canvas(7.4)
text(ax,6,7.03,'Study-specific adapters, shared evidence interfaces',21,fontweight='bold')
for i,(title,body,c) in enumerate([('RPS','Actions, histories,\nroster and rewards','scope'),('LGO','Expression, gates,\ntraining transform','artifact'),('VERA','Readout, fixed host,\nperturbation reference','reference'),('CaST','Query, candidates,\nprotocol and scores','evidence')]):
    x=.3+i*3;box(ax,x,5.1,2.4,1.4,title,body,c);arrow(ax,(x+1.2,5.04),(x+1.2,4.65))
box(ax,.3,3.38,11.4,1.23,'Common claim record','clm | scp | art | ref | pro | evd | bnd','protocol',17)
for x,title,body,c in [(.3,'Semantic checks','Units, roles, time window\nand admissible information','scope'),(4.45,'Empirical checks','Same-host references;\npaired effects and intervals','reference'),(8.6,'Dependency checks','Version, input lineage\nand executable replay','evidence')]:
    box(ax,x,1.38,3.1,1.35,title,body,c,14.5);arrow(ax,(x+1.55,3.31),(x+1.55,2.79))
text(ax,6,.58,'Checks exchange identified artifacts and declared conditions, not interchangeable scores.',14)
save(fig,'audit_interfaces',['Thesis_workspace/02_outline/framework_spec.md'],'Study adapters are alternatives or complements, not a compulsory four-algorithm cascade.')

fig,ax=canvas(7.3)
text(ax,6,6.98,'One adaptive encounter inside a population-dependent tournament',20,fontweight='bold')
box(ax,.25,4.64,2.55,1.45,'Roster and schedule','Who interacts, when,\nand for how long','scope',14)
box(ax,3.3,4.64,2.55,1.45,'Agent state','History-dependent\ndecision information','artifact',14)
box(ax,6.35,4.64,2.55,1.45,'Action and payoff',r'$a_t,\;a_t^{\rm opp}$'+'\n'+r'$M[a_t,a_t^{\rm opp}]$','reference',14)
box(ax,9.4,4.64,2.3,1.45,'Update state','Carry state to\nnext encounter','protocol',14)
for x in [2.86,5.91,8.96]:arrow(ax,(x,5.36),(x+.37,5.36))
arrow(ax,(10.55,6.15),(4.55,6.15),'protocol',rad=.10)
text(ax,7.45,6.57,'Continual learning across opponents',13)
box(ax,.4,1.4,3.35,1.6,'Reference window',r'Observed opponent actions $\to p_t$'+'\n'+r'Window length $L_{\rm win}$','scope',14)
box(ax,4.33,1.4,3.35,1.6,'Decision log',r'Expose $\widehat p_t$, played action'+'\nand the reference procedure','artifact',14)
box(ax,8.26,1.4,3.35,1.6,'Two different summaries','Local regret certificate\nSeed-level tournament result','evidence',14)
arrow(ax,(4.58,4.57),(5.65,3.06),'artifact');arrow(ax,(7.62,4.57),(2.08,3.06),'scope')
arrow(ax,(3.81,2.2),(4.27,2.2));arrow(ax,(7.74,2.2),(8.2,2.2))
text(ax,6,.6,'Changing the population can change both accumulated state and the ranking.',14)
save(fig,'rps_operation',['Paper_published/RPS/RPS_v5_13.tex','Paper_published/RPS/RPS_SI_v5_13.tex'],'Mechanism schematic; no new tournament outputs.')

p=np.array([.55,.30,.15]);q=np.array([.30,.50,.20]);M=np.array([[0,-1,1],[1,0,-1],[-1,1,0]])
u=M@p;uh=M@q;ap=int(np.argmax(u));aq=int(np.argmax(uh));distance=float(abs(p-q).sum());regret=float(u[ap]-u[aq]);assert regret<=2*distance
fig,axes=plt.subplots(1,3,figsize=(11.8,4.9),gridspec_kw={'width_ratios':[1.1,1.1,1]})
fig.subplots_adjust(left=.07,right=.97,bottom=.19,top=.78,wspace=.55)
x=np.arange(3)
axes[0].bar(x-.18,p,.34,color=COL['scope'],label=r'Reference $p$');axes[0].bar(x+.18,q,.34,color=COL['artifact'],label=r'Exposed $\widehat p$');axes[0].set_xticks(x,['R','P','S']);axes[0].set_ylim(0,.7);axes[0].set_ylabel('Probability');axes[0].legend(fontsize=11,frameon=False,loc='upper right');axes[0].set_title('1  Compare distributions',fontsize=15,pad=17)
axes[1].bar(x,u,color=[COL['light'],COL['scope'],COL['artifact']],edgecolor=COL['ink']);axes[1].axhline(0,color=COL['ink'],lw=.7);axes[1].set_xticks(x,['R','P','S']);axes[1].set_ylim(-.38,.61);axes[1].set_ylabel(r'$U(a;p)$');axes[1].set_title('2  Compare best responses',fontsize=15,pad=17)
axes[1].annotate(r'$a_p$',(1,u[1]),xytext=(1,.51),ha='center',fontsize=15);axes[1].annotate(r'$a_{\widehat p}$',(2,u[2]),xytext=(2,-.35),ha='center',fontsize=15)
axes[2].barh([1,0],[regret,2*distance],color=[COL['reference'],COL['evidence']],height=.45);axes[2].set_yticks([1,0],['Local\nregret','Upper\nbound']);axes[2].set_xlim(0,1.2);axes[2].set_ylim(-.7,1.7);axes[2].set_xlabel('Payoff units');axes[2].set_title('3  Check the certificate',fontsize=15,pad=17)
for yi,value in [(1,regret),(0,2*distance)]:axes[2].text(value+.025,yi,f'{value:g}',va='center',fontsize=14)
fig.suptitle(r'Illustration: $\|p-\widehat p\|_1=0.5$, $\Delta^{\mathrm{cert}}=0.65\leq1$',fontsize=19,y=.96)
fig.text(.5,.045,'Chosen distributions illustrate the mechanism; these are not tournament measurements.',ha='center',fontsize=13)
save(fig,'rps_certificate',['Paper_published/RPS/RPS_v5_13.tex'],'Explicit artificial RPS distributions, used only to explain the bound.')

fig,ax=canvas(7.2)
text(ax,6,6.83,'Construct, select and interpret an executable gate model',20,fontweight='bold')
box(ax,.4,4.56,3.3,1.55,'1  Fit the transformation',r'$z=(x-\mu_{\rm train})/s_{\rm train}$'+'\nKeep the fitted coordinates','scope',14)
box(ax,4.35,4.56,3.3,1.55,'2  Build an expression','Typed feature / slope / location\nroles constrain the grammar','artifact',14)
box(ax,8.3,4.56,3.3,1.55,'3  Refine parameters','Propose gate locations/slopes\nEvaluate a fixed criterion','protocol',14)
arrow(ax,(3.76,5.34),(4.29,5.34));arrow(ax,(7.71,5.34),(8.24,5.34))
text(ax,6,3.67,r'$g(z;\alpha,\tau)=\sigma\{\alpha(z-\tau)\},\qquad m(z;\alpha,\tau)=z\,g(z;\alpha,\tau)$',21)
box(ax,8.3,1.33,3.3,1.52,'4  Select and evaluate','Select on validation only;\nretain independent test data','reference',14)
box(ax,4.35,1.33,3.3,1.52,'5  Bind and export','Expression + fitted transform\n+ protected arithmetic','evidence',14)
box(ax,.4,1.33,3.3,1.52,'6  Interpret conditionally',r'$\tau_x=\mu_{\rm train}+s_{\rm train}\tau$'+'\nDirect feature gate only','artifact',14)
arrow(ax,(9.95,4.49),(9.95,2.92));arrow(ax,(8.24,2.09),(7.71,2.09));arrow(ax,(4.29,2.09),(3.76,2.09))
text(ax,6,.52,'An algebraically defined gate location still needs empirical and domain validation.',14)
save(fig,'lgo_operation',['Paper_published/LGO/LGO_R3.tex','Paper_published/LGO/Supplemental_Information_R3.tex'],'Thesis construction and evaluation workflow; validation separation is a requirement, not a retrospective certification of all published runs.')

fig,ax=canvas(7.4)
text(ax,6,7.05,'Evaluate the meaning of a readout on a fixed host',21,fontweight='bold')
box(ax,.4,5.19,3.3,1.24,'Masked training data','Same observed information','scope',14)
box(ax,4.35,5.19,3.3,1.24,'Frozen host '+r'$\mathsf{H}$','Same parameters and completion','artifact',14)
arrow(ax,(3.76,5.81),(4.29,5.81))
box(ax,.4,2.76,3.3,1.58,'Candidate readouts',r'$D[j,k]$: attention aggregation'+'\n'+r'$\mathrm{TAP}_0[j,k]$: association','artifact',14)
box(ax,4.35,2.76,3.3,1.58,'Behavioral reference','Perturb source k; re-run '+r'$\mathsf{H}$'+'\nMeasure change at target j','reference',14)
box(ax,8.3,2.76,3.3,1.58,'Shared scoring conditions','Same target cells and loss;\nfixed perturbation law '+r'$\nu$','protocol',14)
arrow(ax,(5.22,5.12),(2.65,4.4),'artifact')
text(ax,4.25,4.73,r'$D$',13)
arrow(ax,(1.25,5.12),(1.25,4.4),'scope')
text(ax,1.87,4.79,r'$\mathrm{TAP}_0$',12)
arrow(ax,(6,5.12),(6,4.4),'reference');arrow(ax,(8.23,3.54),(7.72,3.54),'protocol')
box(ax,2.36,.58,7.26,1.36,'Paired evidence, preserved units','Within-target ranking agreement -> seed-level paired contrast\nStability, structural recovery and cost remain separate axes','evidence',14)
arrow(ax,(2.06,2.69),(4.4,2.01));arrow(ax,(6,2.69),(6,2.01))
text(ax,10,5.7,'Scoring truth is not\na candidate input.',14)
save(fig,'vera_same_host',['Paper_under_review/VERA/main/paperY_main.tex','Paper_under_review/VERA/esm/sec_esm_recovery.tex'],'Reference and candidate information roles; no numerical efficacy claim.')

fig,axes=plt.subplots(1,3,figsize=(11.8,5.5));fig.subplots_adjust(left=.025,right=.975,bottom=.15,top=.83,wspace=.20)
points={'q':(.5,.10),'p1':(.2,.59),'p2':(.8,.59),'g':(.5,.91),'v1':(.10,.13),'v2':(.90,.13)}
edges=[('p1','g'),('p2','g'),('v1','p1'),('v2','p2'),('q','p1'),('q','p2')]
for ax,protocol,title in zip(axes,['full','edge','inductive'],['Full: known concept','Edge holdout: hidden links','Inductive: unseen concept']):
    ax.set_xlim(-.07,1.07);ax.set_ylim(-.2,1.06);ax.axis('off');ax.set_title(title,fontsize=15,pad=15)
    for child,parent in edges:
        hidden=child=='q' and protocol!='full'
        ax.add_patch(FancyArrowPatch(points[child],points[parent],arrowstyle='-|>',mutation_scale=14,shrinkA=18,shrinkB=18,color=COL['reference'] if hidden else COL['ink'],linestyle='--' if hidden else '-',lw=1.4))
    for node,(x,y) in points.items():
        excluded=node=='q' and protocol=='inductive';color='#DCE2E7' if excluded else (COL['scope'] if node=='q' else COL['artifact'])
        ax.add_patch(Circle((x,y),.077,facecolor=color,edgecolor=COL['ink'],lw=1.2));ax.text(x,y,node,ha='center',va='center',color=COL['ink'] if excluded else 'white',fontsize=14,fontweight='bold')
    ax.text(.5,-.12,{'full':'q and its links are visible','edge':'q is indexed; its parent links are hidden','inductive':'q is absent from graph and index'}[protocol],ha='center',fontsize=12.5)
fig.suptitle('One conceptual relation, three different information protocols',fontsize=20,y=.97)
fig.text(.5,.045,'Solid arrows: visible child-to-parent edges. Dashed arrows: evaluator-only relations.',ha='center',fontsize=13,color=COL['reference'])
save(fig,'cast_protocols',['Paper_under_review/CaST/SM/sections/A1_protocol.tex'],'Artificial six-node ontology explains information visibility; not an experimental ontology subset.')

fig,ax=canvas(7.1)
text(ax,6,6.78,'Four candidate sources become five score features',21,fontweight='bold')
for i,(title,body) in enumerate([('Dense text','Semantic similarity'),('Lexical','BM25 matching'),('Structure','Embedding distance'),('Traversal','Visible parent links')]):
    x=.3+i*3;box(ax,x,5.08,2.4,1.08,title,body,'scope',14);arrow(ax,(x+1.2,5.02),(x+1.2,4.59))
box(ax,.3,3.56,11.4,.98,'Candidate union '+r'$\mathcal{C}_q$','Deduplicate concept IDs; retain source membership','artifact',16)
for i,(title,body) in enumerate([('den','Dense score'),('lex','Lexical score'),('str','Structure score'),('max','Traversal maximum'),('vote','Traversal vote')]):
    x=.3+i*2.32;box(ax,x,1.93,2.1,1.06,title,body,'protocol',13);arrow(ax,(x+1.05,3.5),(x+1.05,3.05));arrow(ax,(x+1.05,1.87),(x+1.05,1.42))
box(ax,.3,.32,11.4,1.04,'Normalize, combine, rank and retain the protocol',r'$F^{(\mathcal{P})}(q,v)=\sum_k w_k^{(\mathcal{P})} z_{qk}(F_k(q,v))$'+'     ->     Top-K candidates + evidence record','evidence',16)
save(fig,'cast_fusion',['Code/CaST-main/exp_basic/t816_engine.py','Paper_under_review/CaST/SM/sections/A2_system.tex'],'Final four-source/five-feature architecture; weights and eligibility remain protocol specific.')

(CHECKS/'integration_mechanism_figure_provenance.json').write_text(json.dumps(records,indent=2)+'\n')
print('Generated',len(records),'mechanism figures')
