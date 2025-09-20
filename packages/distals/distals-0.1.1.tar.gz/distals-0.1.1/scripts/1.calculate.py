import pickle
import math
import sys
import torch

sys.path.insert(1,'src/')
from distals import distals

main_model = distals.Distals()

start = int(sys.argv[1])
end = int(sys.argv[2])
num_langs = len(main_model.all_data)
if end > num_langs:
    end = num_langs

x_size = end-start
matrix = torch.full((x_size, num_langs, len(distals.classes)), -100, dtype=torch.float) 

# TODO features are non-directional, but we get them twice now..

print(start, end)
for src_lang_idx in range(start, end):
    store_idx = src_lang_idx - start
    src_lang = sorted(main_model.all_data)[src_lang_idx]
    print(src_lang, flush=True)
    for tgt_lang_idx, tgt_lang in enumerate(sorted(main_model.all_data)):
        dists, avgs = main_model.get_dists(src_lang, tgt_lang, aslist=True)
        for feat_idx in range(len(distals.classes)):
            matrix[store_idx][tgt_lang_idx][feat_idx] = dists[feat_idx]



out_path = '2.matrix.' + str(start) + '-' + str(end) + '.pt'
torch.save(matrix, open(out_path, 'wb'))

