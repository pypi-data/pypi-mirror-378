import os
import json
import _jsonnet

seeds = ['1']

lms = ['FacebookAI/xlm-roberta-large', 'cis-lmu/glot500-base']#, 'microsoft/infoxlm-large']#, 'microsoft/mdeberta-v3-base']

ud_folder = 'data/ud-treebanks-v2.15/'


def load_json(path: str):
    """
    Loads a jsonnet file through the json package and returns a dict.
    
    Parameters
    ----------
    path: str
        the path to the json(net) file to load
    """
    return json.loads(_jsonnet.evaluate_snippet("", '\n'.join(open(path).readlines())))

def getModel(name):
    modelDir = 'machamp/logs/'
    nameDir = modelDir + name + '/'
    if os.path.isdir(nameDir):
        for modelDir in reversed(os.listdir(nameDir)):
            modelPath = nameDir + modelDir + '/model.pt'
            if os.path.isfile(modelPath):
                return modelPath
    return ''

def getTrainDevTest(path):
    train = ''
    dev = ''
    test = ''
    for conlFile in os.listdir(path):
        if conlFile.endswith('conllu'):
            if 'train' in conlFile:
                train = path + '/' + conlFile
            if 'dev' in conlFile:
                dev = path + '/' + conlFile
            if 'test' in conlFile:
                test = path + '/' + conlFile
    return train, dev, test

def treebankInfo(path):
    info = {}
    readme_path = path + '/README.md'
    if not os.path.isfile(readme_path):
        readme_path = path + '/README.txt'
    for line in reversed(open(readme_path).readlines()):
        line=line.strip()
        if 'Machine' in line and 'readable' in line:
            break
        if len(line) == 0 or line[0] in '<=':
            continue
        line = line.replace('\t', ' ')
        tok = line.strip().split(': ')
        if len(tok) != 2:
            continue
        info[tok[0]] = tok[1]
    return info

