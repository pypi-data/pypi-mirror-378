import pickle
import sys
from scipy.stats import pearsonr
import math
import myutils

sys.path.insert(1,'src/')
from distals import distals

distals_model = distals.Distals()


data = pickle.load(open('precalculated/' + myutils.lms[0].split('/')[-1] + '.UPOS.iso.pickle', 'rb'))
distals_distances = {}
for src_lang in data:
    if src_lang not in distals_distances:
        distals_distances[src_lang] = {}
    for tgt_lang in data[src_lang]:
        if tgt_lang not in distals_distances[src_lang]:
            distals_distances[src_lang][tgt_lang] = distals_model.get_dists(src_lang, tgt_lang, aslist=True)[0]


totals = []
totalsP = []
for lm in myutils.lms:
    print(lm)
    print(' & '.join(['', 'UPOS', 'LAS', 'UFeats', 'Lemmas']) + ' \\\\')
    results = []
    resultsP = []
    for task in ['UPOS', 'LAS', 'UFeats', 'Lemmas']:
        results.append([])
        resultsP.append([])
        data = pickle.load(open('precalculated/' + lm.split('/')[-1] + '.' + task + '.iso.pickle', 'rb'))
        # subtract the baseline (in-language) score, we are mainly interested in tranfer differences
        for src_lang in data:
            for tgt_lang in data[src_lang]:
                data[src_lang][tgt_lang] -= data[src_lang][src_lang]

        for key_idx, key in enumerate(distals.keys):
            feature = []
            target = []
            for src_lang in data:
                for tgt_lang in data[src_lang]:
                    dist = distals_distances[src_lang][tgt_lang][key_idx]
                    if type(dist) == float and dist != -1 and not math.isnan(dist):
                        if type( data[src_lang][tgt_lang]) == float:
                            feature.append(dist)
                            target.append(data[src_lang][tgt_lang])
            pearson = pearsonr(target, feature)
            results[-1].append(pearson[0])
            resultsP[-1].append(pearson[1])

    transposed = list(map(list, zip(*results)))
    transposedP = list(map(list, zip(*resultsP)))
    totals.append(transposed)
    totalsP.append(transposedP)
    for key_idx, values in enumerate(transposed):
        print(' & '.join([distals.keys[key_idx]] + ['{:.2f}'.format(x) for x in values]) + ' \\\\')
    print()

print('average')
for x in range(len(totals[0])):
    for y in range(len(totals[0][x])):
        totals[0][x][y] = (totals[0][x][y] + totals[1][x][y])/2
        totalsP[0][x][y] = (totalsP[0][x][y] + totalsP[1][x][y])/2

for key_idx, values in enumerate(totals[0]):
    row = [distals.keys[key_idx]]
    for val, p in zip(totals[0][key_idx], totalsP[0][key_idx]):
        text = '{:.2f}'.format(val)
        if p < .05:
            text += '$^*$'
        row.append(text)
    print(' & '.join(row) + ' \\\\')
print()

