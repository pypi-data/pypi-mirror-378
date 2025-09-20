import os
import configparser
import unicodedata

macrolang_fixes = {'chinese': 'cmn', 'estonian': 'ekk', 'latvian': 'lvs', 'guarani': 'gug', 'nepali': 'npi', 'latvia': 'lvs', 'arabic': 'arb', 'oriya': 'ory', 'malay': 'zlm', 'komi': 'kpv'}
macrolang_substitutes = {
    'ara': 'arb',
    'bh': 'bho',
    'est': 'ekk',
    'grn': 'gug',
    'hbs': 'hrv',
    'kom': 'kpv',
    'lav': 'lvs',
    'msa': 'zlm',
    'nep': 'npi',
    'ori': 'ory',
    'zho': 'cmn',
}

class LangnameUtils():
    def __init__(self, info: dict = None, data_folder: str = 'data/'):
    # we load it a bit cumbersome, since the pip package has a package import (distals.langname_utils
    # and the local version has not. Hence we can't just pickle it (class not found error)
        if info != None:
            self.fromdict(info)
        else:
            self.iso639 = {}
            self.two2three = {}
            self.iso_conv = {}
            self.iso639_conv = {}
            self.glot_conv = {}
            self.altname_conv = {}
            self.macros = set()
            self.update(data_folder)
         
    
    def todict(self):
        return {'iso639': self.iso639, 'two2three': self.two2three, 'iso_conv': self.iso_conv, 'glot_conv': self.glot_conv, 'altname_conv': self.altname_conv, 'macros': self.macros, 'iso639_conv': self.iso639_conv}

    def fromdict(self, info):
        self.iso639 = info['iso639']
        self.two2three = info['two2three']
        self.iso_conv = info['iso_conv']
        self.iso639_conv = info['iso639_conv']
        self.glot_conv = info['glot_conv']
        self.altname_conv = info['altname_conv']
        self.macros = info['macros']

    def update(self, data_folder: str = 'data/'):
        # Handling of iso639 codes
        self.iso639 = {}
        self.two2three = {}
        for line in open(data_folder + 'iso-639-3.tab').readlines()[1:]:
            tok = line.strip().split('\t')
            if tok[4] == 'I':
                self.iso639[tok[0]] = tok[6]
            if tok[3] != '':
                self.two2three[tok[3]] = tok[0]

        self.iso639_conv = {}
        for line in open(data_folder + '/iso-639-3_Retirements.tab').readlines()[1:]:
            tok = line.strip().split('\t')
            prev = tok[0]
            new = tok[3]
            if new != '':
                self.iso639_conv[prev] = new

        for line in open(data_folder + 'iso-639-3.tab'):
            tok = line.strip().split('\t')
            name = tok[-1].lower()
            code = tok[0]
            if tok[4] == 'I':
                self.iso_conv[name] = code
            elif tok[4] == 'M':
                self.macros.add(name)
        
        for path, directories, files in os.walk(data_folder + 'glottolog/languoids/tree/', topdown=True):
            for file in files:
                if file.endswith('ini'):
                    config = configparser.ConfigParser(interpolation=None)
                    if True:
                        config.read(path + '/' + file)
        
                        
                        if 'core' not in config or 'iso639-3' not in config['core']:
                            continue
                        iso639_code = self.toISO(config['core']['iso639-3'], False)
                        if not iso639_code: # invalid code used
                            continue
                        
                        glot_name = config['core']['name'].lower()
                        self.glot_conv[glot_name] = iso639_code
                        
                        if 'altnames' in config:
                            for alt_names in config['altnames'].items():
                                for alt_name in alt_names[1].split('\n'):
                                    alt_name = alt_name.lower().strip()
                                    if alt_name == '':
                                        continue

                                    if alt_name not in self.altname_conv:
                                        self.altname_conv[alt_name] = {}
        
                                    if iso639_code not in self.altname_conv[alt_name]:
                                        self.altname_conv[alt_name][iso639_code] = 1
                                    else:
                                        self.altname_conv[alt_name][iso639_code] += 1
        
                    #except:
                    #    print('error in ' + path + '/' + file)
                    #    continue

    def toISO(self, code, also_search_fullnames=True,
              print_macrolang_info=False, disable_macro_conversion=False):
        if code is None:
            return code
        if code in self.iso639:
            return code
        code_orig = code  # keep the original version of name->ISO lookup
        if len(code) == 2:
            if code in self.two2three:
                code = self.two2three[code]
        if code in self.iso639_conv:
            code = self.iso639_conv[code]
        if code in self.iso639:
            return code
        if disable_macro_conversion == False and code in macrolang_substitutes:
            code_replaced = macrolang_substitutes[code]
            if print_macrolang_info:
                print("Replacing macro-language code ("
                      + code + "->" + code_replaced + ")")
            return code_replaced
        if also_search_fullnames:
            code_replaced = self.name_to_iso(code_orig)
            if code_replaced and (len(code_orig) == 2 or len(code_orig) == 3):
                print("Could not find ISO code " + code_orig
                      + ", but found the language "
                      + code_orig[0].upper() + code_orig[1:]
                      + " (ISO code: " + code_replaced + ")")
            return code_replaced
        return None


    def name_to_iso(self, lang_name):
        lang_name = lang_name.lower()
    
        if lang_name in macrolang_fixes:
            return macrolang_fixes[lang_name]
        if lang_name in self.macros:
            return None
    
        if lang_name in self.iso_conv:
            return self.iso_conv[lang_name]
    
        if lang_name in self.glot_conv:
            return self.glot_conv[lang_name]
    
        if lang_name in self.altname_conv:
            return sorted(self.altname_conv[lang_name].items(), key=lambda item: item[1])[-1][0]
    
        return None

