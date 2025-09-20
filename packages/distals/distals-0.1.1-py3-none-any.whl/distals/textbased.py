import os
import unicodedata
from scipy.spatial import distance
from collections import defaultdict

def toDistr(probs1, probs2):
    keys = set(sorted(list(probs1.keys()) + list(probs2.keys())))
    distr1 = [0.0] * len(keys)
    distr2 = [0.0] * len(keys)
    for key_idx, key in enumerate(keys):
        if key in probs1:
            distr1[key_idx] = probs1[key]
        if key in probs2:
            distr2[key_idx] = probs2[key]
    return distr1, distr2

def get_character_ngrams(sentence:str, beg, end):
    char_ngrams = []
    for i in range(beg,end+1):
        for j in range(len(sentence)-end+1):
            char_ngrams.append(sentence[j:j+i])
    return char_ngrams


def _is_whitespace(char):
    """Checks whether `char` is a whitespace character."""
    # \t, \n, and \r are technically control characters but we treat them
    # as whitespace since they are generally considered as such.
    if char == " " or char == "\t" or char == "\n" or char == "\r":
        return True
    cat = unicodedata.category(char)
    if cat == "Zs":
        return True
    return False

def _is_punctuation(char):
    """Checks whether `char` is a punctuation character."""
    cp = ord(char)
    # We treat all non-letter/number ASCII as punctuation.
    # Characters such as "^", "$", and "`" are not in the Unicode
    # Punctuation class but we treat them as punctuation anyways, for
    # consistency.
    if (cp >= 33 and cp <= 47) or (cp >= 58 and cp <= 64) or (cp >= 91 and cp <= 96) or (cp >= 123 and cp <= 126):
        return True
    cat = unicodedata.category(char)
    if cat.startswith("P"):
        return True
    return False

def collect(all_data, data_folder, langname_utils):
    
    print('counting character based metrics')
    for lang_code in sorted(os.listdir(data_folder + '/text/')):
        iso_code = langname_utils.toISO(lang_code)
        if iso_code == None:
            continue
        character_counts = {}
        whitespace_count = 0
        punctuation_count = 0
        total_count = 0
        ngram_dict = defaultdict(int)

        sources = os.listdir(data_folder + '/text/' + lang_code)
        scripts = [x.split('_')[1] for x in sources]
        for source, script in zip(sources, scripts):
            script_count = scripts.count(script)
            size = int(1000/script_count)
            for lineIdx, line in enumerate(open(data_folder + '/text/' + lang_code + '/' + source, errors='ignore', encoding='utf-8')):
                if lineIdx > size:
                    break
                # normalize
                line = line.strip()
                line = unicodedata.normalize('NFC', line)
    
                # First get character counts
                for char in line:
                    if _is_whitespace(char):
                        whitespace_count += 1
                    elif _is_punctuation(char):
                        punctuation_count += 1
    
                    if char not in character_counts:
                        character_counts[char] = 1
                    else:
                        character_counts[char] += 1
                total_count += len(line)

                # now get n-gram counts for textcat distance
                ngrams = get_character_ngrams(line, 1, 5)
                for ngram in ngrams:
                    ngram_dict[ngram] += 1

        # for character counts: normalize to prob, and sort
        for char in character_counts:
            character_counts[char] /= total_count
        character_counts = dict(sorted(character_counts.items(), key=lambda item: item[1], reverse=True))

        # for textcat, sort, and keep only top-400
        ranked_ngrams = []
        for item in dict(sorted(ngram_dict.items(), key=lambda item: item[1], reverse=True)):
            if len(ranked_ngrams) == 400:
                break
            else:
                ranked_ngrams.append(item)
        
        # save all
        all_data[iso_code]['whitespace'] = whitespace_count/total_count
        all_data[iso_code]['punctuation'] = punctuation_count/total_count
        all_data[iso_code]['char_JSD'] = character_counts
        all_data[iso_code]['textcat'] = ranked_ngrams
    return all_data

def distance_metric(lang1_data, lang2_data, key):
    if key in ['whitespace', 'punctuation']:
        if lang1_data + lang2_data == 0.0:
            return 0.0
        return 1- min(lang1_data, lang2_data)/max(lang1_data, lang2_data)
    if key == 'char_JSD':
        distr1, distr2 = toDistr(lang1_data, lang2_data)
        return distance.jensenshannon(distr1, distr2) 
        # Below is TVD
        return sum([abs(x-y) for x, y in zip(distr1, distr2)]) / len(distr1)
    if key == 'textcat':
        max_dist = 400* 400
        dist_score = 0
        for ngr1_idx, ngr1 in enumerate(lang1_data):
            if ngr1 in lang2_data:
                dist_score += abs(ngr1_idx - lang2_data.index(ngr1))
            else:
                dist_score += 400
        return dist_score / max_dist

        

