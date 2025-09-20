# we combine different sources into the same file structure, 
#standardize language/script ISO codes
# and limit the size to 10,000 for each source/lang. combination

import json
import os
from distals import distals
import csv
import myutils
import script_classifier

run = True
tgt_dir = 'data/all/'
if not os.path.isdir(tgt_dir):
    os.makedirs(tgt_dir)

distals_model = distals.Distals()

unicode_scripts = set()
for line in open('scripts/Scripts.txt'):
    tok = line.strip().split(';')
    if len(tok) == 2:
        unicode_scripts.add(tok[1].split('#')[0].strip().lower())

code2script = {}
script2code = {}
for line in open('scripts/iso15924.txt'):
    if line[0] != '#' and len(line) > 3:
        tok = line.strip().lower().split(';')
        iso_code = tok[0]
        unicode_name = tok[4]
        if unicode_name == '' or unicode_name not in unicode_scripts:
            #code2script[iso_code] = None
            continue
        code2script[iso_code] = unicode_name
        script2code[unicode_name] = iso_code


print('cleaning glotlid')
script_conversion = {'han': 'hani', 'hans': 'hani', 'hant': 'hani', 'rom': 'latn', 'pnyn': 'latn', 'kore': 'hang' , 'zxxx': 'latn', 'jpan': 'hani', 'kana': 'hani', 'hira': 'hani'}
lang_conversion = {'toki': 'tok'}

glot_folder = 'data/glotlid-corpus/v3.1/'
for language_folder in os.listdir(glot_folder):
    lang_code = language_folder.split('_')[0]
    iso_code = distals_model.langname_utils.toISO(lang_code, False)
    if iso_code == None:
        print(lang_code + ' does not exist1', language_folder)
        continue
    script_code = language_folder.split('_')[1]
    if script_code.lower() in script_conversion:
        script_code = script_conversion[script_code.lower()]

    if script_code.lower() not in code2script:
        print(script_code + ' script does not exist1')
        continue

    # Now get the first 100,000 lines of each file
    lang_tgt_dir = os.path.join('data/all/' + lang_code)
    if not os.path.isdir(lang_tgt_dir):
        os.makedirs(lang_tgt_dir)
    for lang_file in os.listdir(os.path.join(glot_folder, language_folder)):
        domain = lang_file.split('_')[2].split('.')[0]
        source = 'glotlid'
        name = '_'.join([iso_code, script_code, source, domain])
        src_path = os.path.join(glot_folder, language_folder, lang_file)
        tgt_path = os.path.join(lang_tgt_dir, name) + '.txt'
        cmd = 'head -10000 ' + src_path + ' > ' + tgt_path
        #print(cmd)
        if run:
            os.system(cmd)
        
# Merge MILTALE into it
print('cleaning MILTALE')

mil_dir = 'data/MIL-TALE/5/data/'
train_files = os.listdir(mil_dir + 'train')
dev_files = os.listdir(mil_dir + 'devtest')
test_files = os.listdir(mil_dir + 'test')

for trainFile in train_files:
    trainPath = mil_dir + 'train/' + trainFile
    devPath = ''
    devFile = trainFile.replace('-train.utf8', '-devtest.utf8')
    if devFile in dev_files:
        devPath = mil_dir + 'devtest/' + devFile
    testFile = trainFile.replace('-train.utf8', '-test.utf8')
    if testFile in test_files:
        testPath = mil_dir + 'test/' + testFile
    lang_code = trainFile.split('_')[0].split('-')[0]

    if lang_code in lang_conversion: # For toki only, other conversion are handled by distals
        lang_code = lang_conversion[lang_code]
    script_code = trainFile.split('.')[1]
    domain = trainFile.split('.')[3].split('-')[0]
    if domain == 'utf8':
        domain = 'bible'
    iso_code = distals_model.langname_utils.toISO(lang_code, False)
    
    if script_code.lower() in script_conversion:
        script_code = script_conversion[script_code.lower()]
    if iso_code == None:
        print(lang_code + ' does not exist2', trainFile)
        continue
    if script_code.lower() not in code2script:
        print(script_code + ' script does not exist2')
        continue
    source = 'MILTALE'
    tgt_lang_dir = os.path.join(tgt_dir, iso_code)
    if not os.path.isdir(tgt_lang_dir):
        os.makedirs(tgt_lang_dir)
    name = '_'.join([iso_code, script_code, source, domain])
    cmd = 'head -10000 -q ' + trainPath + ' ' + devPath + ' ' + testPath + ' > ' + os.path.join(tgt_lang_dir, name) + '.txt'
    cmd = cmd.replace('(', '\\(').replace(')', '\\)').replace('\'', '\\\'')
    print(cmd)
    if run:
        os.system(cmd)

sample_files = os.listdir(mil_dir + 'samples')
for sample_file in sample_files:
    if not sample_file.endswith('utf8'):
        continue
    lang_code = sample_file.split('_')[0].split('-')[0]
    script_code = sample_file.split('.')[1]
    domain = sample_file.split('.')[3].split('-')[0]
    if domain == 'utf8':
        domain = 'bible'
    iso_code = distals_model.langname_utils.toISO(lang_code, False)
    
    if script_code.lower() in script_conversion:
        script_code = script_conversion[script_code.lower()]
    if iso_code == None:
        print(lang_code + ' does not exist2', trainFile)
        continue
    if script_code.lower() not in code2script:
        print(script_code + ' script does not exist2')
        continue
    source = 'MILTALE'
    tgt_lang_dir = os.path.join(tgt_dir, iso_code)
    if not os.path.isdir(tgt_lang_dir):
        os.makedirs(tgt_lang_dir)
    name = '_'.join([iso_code, script_code, source, domain])
    cmd = 'cp ' + mil_dir + 'samples/' + sample_file + ' ' + os.path.join(tgt_lang_dir, name) + '.txt'
    print(cmd)
    if run:
        os.system(cmd)
    

