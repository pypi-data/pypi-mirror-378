import os
import myutils
import sys

sys.path.insert(1,'src/')
from distals import distals

distals_model = distals.Distals()

if not os.path.isdir('preds'):
    os.mkdir('preds')

tgt_treebanks = []
for tgt_treebank in os.listdir(myutils.ud_folder):
    lang = tgt_treebank.replace('UD_', '').split('-')[0]
    iso_code = distals_model.langname_utils.toISO(lang)
    if iso_code == None:
        continue
    tgt_info = myutils.treebankInfo(myutils.ud_folder + tgt_treebank)
    if tgt_info['Includes text'] != 'yes':
        continue
    tgt_treebanks.append(tgt_treebank)

for lm in myutils.lms:
    for src_treebank in os.listdir(myutils.ud_folder):
        name = lm.split('/')[-1] + '-' + src_treebank
        src_info = myutils.treebankInfo(myutils.ud_folder + src_treebank)
        if src_info['Includes text'] != 'yes':
            continue
        model_path = myutils.getModel(name)
        if model_path != '':
            cmd = 'python3 predict.py ' + model_path.replace('machamp/', '')
            for tgt_treebank in tgt_treebanks:
                train, dev, test = myutils.getTrainDevTest(myutils.ud_folder + tgt_treebank)
                out_path = '../preds/' + name + '-' + tgt_treebank
                if not os.path.isfile(out_path[3:]):
                    cmd += ' ../' + test + ' ' + out_path
            if cmd != 'python3 predict.py ' + model_path.replace('machamp/', ''):
                print(cmd)



