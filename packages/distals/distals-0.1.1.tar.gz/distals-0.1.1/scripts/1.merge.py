import pickle
import torch
import myutils
import sys
import os
import csv
sys.path.insert(1,'src/')
from distals import distals 
main_model = distals.Distals()

matrix = torch.full((len(main_model.all_data), len(main_model.all_data), len(distals.classes)), -100, dtype=torch.float)

for i in range(63):
    start = 125 * i
    end = start + 125

    if end == 7875:
        end = 7856
    out_path = '1.matrix.' + str(start) + '-' + str(end) + '.pt'
    print(out_path)
    it_matrix = torch.load(out_path)
    matrix[start:end, :, :] = it_matrix

out_path = 'precalculated/matrix.pt'
torch.save(matrix, open(out_path, 'wb'))

folder = 'precalculated/'
if not os.path.isdir(folder):
    os.mkdir(folder)
names = [x[1] for x in distals.classes]
langs = list(sorted(main_model.langname_utils.iso639))
for name_idx, name in enumerate(names):
    out_path = folder + name + '.csv'
    with open(out_path, 'w') as file:
        writer = csv.writer(file)
        writer.writerow([''] + langs)
        for lang_idx, lang in enumerate(langs):
            writer.writerow([lang] + [x.item() for x in matrix[lang_idx,:,name_idx]])


    


