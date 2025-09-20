import os
import myutils
import conll18_ud_eval
import pickle
import sys

sys.path.insert(1,'src/')
from distals import distals

distals_model = distals.Distals()

trains = []
tests = []
for ud_treebank in os.listdir(myutils.ud_folder):
    lang = ud_treebank.replace('UD_', '').split('-')[0]
    iso_code = distals_model.name_to_iso(lang)
    if iso_code == None:
        continue


    treebank_info = myutils.treebankInfo(myutils.ud_folder + ud_treebank)
    if treebank_info['Includes text'] != 'yes':
        continue
    train, dev, test = myutils.getTrainDevTest(myutils.ud_folder + ud_treebank)
    if train != '':
        trains.append(ud_treebank)
    tests.append(ud_treebank)

metrics = ['LAS', 'Lemmas', 'UPOS', 'UFeats']
for lm in myutils.lms:
    print(lm)
    matrix = {}
    for src_idx, src_treebank in enumerate(trains):
        print(src_treebank, str(src_idx) + '/' + str(len(trains)), flush=True)
        matrix[src_treebank] = {}
        src_name = lm.split('/')[-1] + '-' + src_treebank
        for tgt_treebank in tests:
            out_path = 'preds/' + src_name + '-' + tgt_treebank
            _, _, test_path = myutils.getTrainDevTest('data/ud-treebanks-v2.15/' + tgt_treebank)
            gold_file = conll18_ud_eval.load_conllu_file(test_path)
            pred_file = conll18_ud_eval.load_conllu_file(out_path)
            scores = conll18_ud_eval.evaluate(gold_file, pred_file)
            scores = {x: scores[x].f1 for x in scores}
            matrix[src_treebank][tgt_treebank] = scores
            
    pickle.dump(matrix, open(lm.split('/')[-1] + '.scores.pickle', 'wb'))

