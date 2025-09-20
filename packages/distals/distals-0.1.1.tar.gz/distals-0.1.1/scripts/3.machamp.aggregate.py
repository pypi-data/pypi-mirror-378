import os
import pickle
import pprint
import sys
import csv
import conll18_ud_eval
import myutils

sys.path.insert(1,'src/')
from distals import distals

distals_model = distals.Distals()

trains = {'LAS': {}, 'Lemmas': {}, 'UPOS': {}, 'UFeats': {}}
tests = {'LAS': {}, 'Lemmas': {}, 'UPOS': {}, 'UFeats': {}}
for ud_treebank in os.listdir(myutils.ud_folder):
    lang = ud_treebank.replace('UD_', '').split('-')[0]
    iso_code = distals_model.name_to_iso(lang)
    if iso_code == None:
        continue


    treebank_info = myutils.treebankInfo(myutils.ud_folder + ud_treebank)
    if treebank_info['Includes text'] != 'yes':
        continue

    for task in trains.keys():
        train, dev, test = myutils.getTrainDevTest(myutils.ud_folder + ud_treebank)
    
        if task == 'Lemmas' and treebank_info["Lemmas"] == "not available":
            continue
        if task == 'UFeats' and treebank_info["Features"] == "not available":
            continue
        if train != '':
            if iso_code not in trains[task]:
                trains[task][iso_code] = []
            trains[task][iso_code].append(ud_treebank)
        if iso_code not in tests[task]:
            tests[task][iso_code] = []
        tests[task][iso_code].append(ud_treebank)

for lm in myutils.lms:
    print(lm)
    matrix = {}
    scores = pickle.load(open(lm.split('/')[-1] + '.scores.pickle', 'rb'))
    for metric in ['LAS', 'Lemmas', 'UPOS', 'UFeats']:
        for src_iso_idx, src_iso in enumerate(sorted(trains[metric])):
            print(src_iso, str(src_iso_idx) + '/' + str(len(trains[metric])))
            matrix[src_iso] = {}
            source_scores = {}
            for src_treebank in trains[metric][src_iso]:
                src_name = lm.split('/')[-1] + '-' + src_treebank
                base = scores[src_treebank][src_treebank][metric]
                for tgt_iso in sorted(tests[metric]):
                    tgt_scores = []
                    for tgt_treebank in tests[metric][tgt_iso]:
                        tgt_scores.append(scores[src_treebank][tgt_treebank][metric])
                    avg_tgt = sum(tgt_scores)/len(tgt_scores)
    
                    if tgt_iso not in source_scores:
                        source_scores[tgt_iso] = []
                    source_scores[tgt_iso].append(avg_tgt-base)
    
            for tgt_iso in source_scores:
                matrix[src_iso][tgt_iso] = sum(source_scores[tgt_iso]) / len(source_scores[tgt_iso])
        pickle.dump(matrix, open(lm.split('/')[-1] + '.' + metric + '.iso.pickle', 'wb'))
        with open('precalculated/' + lm.split('/')[-1] + '.' + metric + '.csv', 'w') as file:
            writer = csv.writer(file)
            writer.writerow([''] + list(sorted(matrix['eng'])))
            for lang in sorted(matrix):
                row = [lang]
                for lang2 in sorted(matrix[lang]):
                    row.append(matrix[lang][lang2])
                writer.writerow(row)
            

