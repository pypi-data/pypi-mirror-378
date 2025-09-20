import torch
import sys
import pickle
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
plt.style.use('scripts/rob.mplstyle')

import myutils
sys.path.insert(1,'src/')
from distals import distals

#distals_model = distals.Distals()

matrix = torch.load('precalculated/matrix.pt')

fig, ax = plt.subplots(figsize=(8,5), dpi=300)

categories = [x[2] for x in distals.classes]
feat_names = [x[1] for x in distals.classes]


for feat_idx, category in enumerate(categories):
    if feat_names[feat_idx] not in distals.average_positives[category]:
        continue
    if distals.keys[feat_idx].startswith('gb_'):
        continue
    all_scores = []
    data = matrix[:,:,feat_idx]
    # mask one triangle as our features are not directional
    for i in range(len(data)):
        data[i][i:] = -1
    
    filtered_data = data[data!=-1]
    filtered_data = filtered_data#[:100000]
    
    x = torch.sort(filtered_data).values
    y = torch.arange(len(filtered_data))/1000000

    ax.plot(y, x, label = distals.keys[feat_idx])

ax.get_xaxis().get_major_formatter().set_useOffset(False)
ax.ticklabel_format(useOffset=False, style='plain')


#ax.set_ylim((0,1))
ax.set_ylabel('Distance score')
ax.set_xlabel('# language-pairs')
ax.set_xticks([0,5,10,15,20,25,30])
ax.set_xticklabels(['0','5M','10M','15M','20M','25M','30M'])


leg = ax.legend(bbox_to_anchor=(1, 1.02), ncol=1)
leg.get_frame().set_linewidth(1.5)

fig.savefig('feat_scoreranges.pdf', bbox_inches='tight')

