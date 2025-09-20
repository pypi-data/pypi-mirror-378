import torch
import pickle
from scipy.stats import pearsonr
import sys
import myutils
sys.path.insert(1,'src/')
from distals import distals

distals_model = distals.Distals()

data = torch.load('matrix.pt')

#langs = list(sorted(pickle.load(open('database.pickle', 'rb')).keys()))

for key_idx, key in enumerate(distals.keys):
    print(key, data[0, :10, key_idx])

for src_clas_idx, src_clas in enumerate(distals.keys):
    if src_clas.startswith('gb_'):
        continue
    for tgt_clas_idx, tgt_clas in enumerate(distals.keys):
        if tgt_clas.startswith('gb_'):
            continue

        # remove duplicates and distances to self
        if src_clas_idx == tgt_clas_idx or tgt_clas_idx > src_clas_idx:
            continue
        for i in range(len(data)):
            data[i][i:] = -1

        data1 = torch.flatten(data[:,:,src_clas_idx])
        data2 = torch.flatten(data[:,:,tgt_clas_idx])
        data1 = torch.nan_to_num(data1, nan=-1)
        data2 = torch.nan_to_num(data2, nan=-1)
        
        indices_to_remove = (data1 == -1) | (data2 == -1)

        filtered_tensor1 = data1[~indices_to_remove]
        filtered_tensor2 = data2[~indices_to_remove]

        if len(filtered_tensor1) < 3:
            print(src_clas, tgt_clas, 0.0)
        else:
            pearson = pearsonr(filtered_tensor1, filtered_tensor2)
            print(src_clas, tgt_clas, pearson[0])



