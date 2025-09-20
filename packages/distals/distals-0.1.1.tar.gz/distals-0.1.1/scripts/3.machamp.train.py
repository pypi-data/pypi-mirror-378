import os
import sys
import json

import myutils
sys.path.insert(1,'src/')
from distals import distals

distals_model = distals.Distals()

if not os.path.isdir('configs'):
    os.mkdir('configs')

for lm in myutils.lms:
    param_config = myutils.load_json('machamp/configs/params.json')
    param_config['transformer_model'] = lm
    out_path = 'configs/params-' + lm.split('/')[-1] + '.json'
    json.dump(param_config, open(out_path, 'w'), indent=4)

train_treebanks = []
for ud_treebank in os.listdir(myutils.ud_folder):
    treebank_info = myutils.treebankInfo(myutils.ud_folder + ud_treebank)
    if treebank_info['Includes text'] != 'yes':
        continue
    train, dev, test = myutils.getTrainDevTest(myutils.ud_folder + ud_treebank)
    if train == '':
        continue
    lang = ud_treebank.replace('UD_', '').split('-')[0]
    iso_code = distals_model.langname_utils.toISO(lang)
    if iso_code == None:
        continue

    config = {'train_data_path': '../' + train}
    if dev != '':
        config['dev_data_path'] = '../' + dev
    config['word_idx'] = 1
    config['max_words'] = 100000
    config['tasks'] = {}
    config['tasks']['upos'] = {'task_type': 'seq', 'column_idx': 3}
    config['tasks']['dependency'] = {'task_type': 'dependency', 'column_idx': 6}
    if treebank_info['Lemmas'] != 'not available':
        config['tasks']['lemma'] = {'task_type': 'string2string', 'column_idx': 2}
    if treebank_info['Features'] != 'not available':
        config['tasks']['feats'] = {'task_type': 'seq', 'column_idx': 5}

    json_path = 'configs/' + ud_treebank + '.json'
    json.dump({ud_treebank: config}, open(json_path, 'w'), indent=4)
    train_treebanks.append(ud_treebank)

for lm in myutils.lms:
    for ud_treebank in train_treebanks:
        
        json_path = 'configs/' + ud_treebank + '.json'
        name = lm.split('/')[-1] + '-' + ud_treebank
        param_path = '../configs/params-' + lm.split('/')[-1] + '.json'
        if myutils.getModel(name) == '':
            cmd = 'python3 train.py --dataset_configs ../' + json_path + ' --parameters_config ' + param_path + ' --name ' + name
            print(cmd)


