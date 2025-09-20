import sys
sys.path.insert(1,'src/')
from distals import distals

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

plt.style.use('scripts/rob.mplstyle')
fig, ax = plt.subplots(figsize=(8,5), dpi=300)

scores = {}
for line in open('2.out'):
    if line.startswith('loading') or 'tensor' in line or line[0] == ' ':
        continue
    tok = line.strip().split(' ')
    if len(tok) != 3 or line[0] == ' ' or line.startswith('torch'):#hacky
        continue
    print(line)
    src = tok[0]
    tgt = tok[1]
    val = abs(float(tok[2]))
    if src not in scores:
        scores[src] = {}
    if tgt not in scores[src]:
        scores[src][tgt] = val


all_dists = [x[1] for x in distals.classes if not x[1].startswith('gb_')]
data = []
for src in all_dists:
    data.append([])
    for tgt in all_dists:
        if src == tgt:
            data[-1].append(1.0)
        elif src in scores and tgt in scores[src]:
            data[-1].append(scores[src][tgt])
        elif tgt in scores and src in scores[tgt]:
            data[-1].append(scores[tgt][src])
        else:
            data[-1].append(0.0)

fig, ax = plt.subplots(figsize=(20,12), dpi=300)
im = ax.imshow(data)

for i in range(len(data)):
    for j in range(len(data[i])):
        text = ax.text(j, i, '{:.2f}'.format(data[i][j]),
                ha="center", va="center", fontsize=12, color='white')


plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
        rotation_mode="anchor")
fig.colorbar(im);
#ax.text(15.5,-.5,embeds[1])
#ax.text(15.5,14,embeds[0])
ax.grid(False)

ax.set_xticks(range(len(all_dists)))
ax.set_yticks(range(len(all_dists)))
ax.set_xticklabels(all_dists)
ax.set_yticklabels(all_dists)

fig.savefig('confusion.pdf', bbox_inches='tight')



