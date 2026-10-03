"""Small aggregate-only view of the Japanese result; no panel is bundled."""
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from auditableai.paths import EVIDENCE, FIGURES, prepare_outputs
from auditableai.plotting import apply_thesis_style

prepare_outputs();apply_thesis_style(font_scale=1.2)
root=EVIDENCE/'japan_health'
d=pd.read_csv(root/'metrics.csv');d=d[(d.evaluation=='temporal')&(d.year=='pooled')]
order=['persistence','trend','linear','gam','hgb','gate']
labels=['Persistence','Damped trend','Ridge change','Additive spline','Boosted trees','Gate change']
fig,ax=plt.subplots(figsize=(8.0,4.8),layout='constrained')
values=d.set_index('model').loc[order,'mae_pp'].to_numpy()
ax.barh(labels,values,color=sns.color_palette('colorblind',6));ax.invert_yaxis()
for i,v in enumerate(values):ax.text(v+.012,i,f'{v:.4f}',va='center')
ax.set(xlabel='MAE (percentage points; lower is better)',xlim=(0,float(max(values)*1.22)),title='Japan: held-out FY2022–2023 regional forecasts')
ax.grid(axis='x',alpha=.2);ax.set_axisbelow(True)
for ext in ['png','svg']:fig.savefig(FIGURES/f'japan_aggregate_comparison.{ext}',dpi=330)
plt.close(fig)
