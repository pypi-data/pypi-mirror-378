import sys
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
plt.style.use('scripts/rob.mplstyle')

import myutils
sys.path.insert(1,'src/')
from distals import distals

distals_model = distals.Distals()

counts = distals_model.get_coverage()
keys = []
values = []
for key in counts:
    if key.startswith('gb_'):
        continue
    keys.append(key)
    values.append(counts[key])

print(keys)
fig, ax = plt.subplots(figsize=(8,5), dpi=300)
ax.bar(range(len(keys)), values)
ax.set_xticks(range(len(keys)))
ax.set_xticklabels(keys, rotation=45, ha="right", rotation_mode="anchor")
ax.set_xlim((-0.5,16.5))
ax.set_ylabel('# Languages')
ax.set_xlabel('Features')
fig.savefig('lang_support.pdf', bbox_inches='tight')







