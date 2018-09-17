#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
import html


DE_MAURO_PATH = '/Users/fedja/scratch/CORPORA/DE_MAURO/'
CERCA_ALPHA = DE_MAURO_PATH + 'cerca_alpha'
PAROLE_DIZIONARIO = DE_MAURO_PATH + 'dizionario.internazionale.it/parola'
POLIREMATICHE_FILE = DE_MAURO_PATH + 'polirematiche.txt'
POLIREMATICHE_SORTED_FILE = DE_MAURO_PATH + 'polirematiche_sorted.txt'
DIZIONARIO_BASE_FILE = DE_MAURO_PATH + 'diz_base.txt'
DIZIONARIO_BASE_SOSTANTIVI_FILE = DE_MAURO_PATH + 'diz_base_sostantivi.txt'
DIZIONARIO_BASE_AGGETTIVI_FILE = DE_MAURO_PATH + 'diz_base_aggettivi.txt'
DIZIONARIO_BASE_SORTED_FILE = DE_MAURO_PATH + 'diz_base_sorted.txt'
DIZ_POLI_WORD_SORTED_FILE = DE_MAURO_PATH + 'diz_poli_sorted.txt'    

def splitComma(string):
    # tenere i piedi a , in , per terra -> ['tenere i piedi a terra','tenere i piedi in terra','tenere i piedi per terra']    
    if ',' not in string:
        return [string]
    string = string.replace(',',' ,')
    string_split = string.split()
    comma_index = string_split.index(',')
    comma_indices = [i for i, j in enumerate(string_split) if j == ',']
    prep = [ x for x in string_split[comma_indices[0]-1:comma_indices[-1]+2] if x != ',']
    result = []
    for p in prep:
        result.append(string_split[:comma_indices[0]-1] + [p] + string_split[comma_indices[-1]+2:])
    return [' '.join(x) for x in result]

def sub_string(line, start_delimiter, end_delimiter):
    start_index = line.index(start_delimiter) + len(start_delimiter)
    end_index = line.index(end_delimiter, start_index)
    return line[start_index:end_index].strip()

def buildPolirematiche():
    alpha_files = [os.path.join(CERCA_ALPHA,f) for f in sorted(os.listdir(CERCA_ALPHA)) if f.endswith('.html')]
    polirematiche_set = set()
    for f in alpha_files:
        with open(f,'r') as f_in:
            print('Reading file: {}'.format(f))
            for line in f_in:
                if 'serp-poli-title' in line:
                    poli_string = sub_string(line, 'title >', '</a>')
                    pos = sub_string(line, "'text_15'>(", ")</em>")
                    for p in splitComma(poli_string):
                        entry = "{}\t{}".format(p, pos)
                        polirematiche_set.add(entry)
    with open(POLIREMATICHE_FILE,'w') as f_out:
        for p in sorted(polirematiche_set):
            f_out.write(p + '\n')

def readPolirematicheFromFile(lowercase = True, pos=False):
    polirematiche_set = set()
    with open(POLIREMATICHE_FILE,'r') as f_in:
        for line in f_in:
            poli = line.strip() if pos else line.split()[0].strip()
            if lowercase:
                poli = poli.lower()
            polirematiche_set.add(poli) 
    return polirematiche_set

def getTitlesFromParolaFile(file_path):
    # <title>Flauto a becco >
    with open(file_path, 'r') as file_in:
        for line in file_in:
            if '<title>' in line:
                start_index = line.index('<title>') + len('<title>')
                end_index = line.index('>', start_index)
                substring = line[start_index:end_index]
                substring = substring.lower()
                substring = html.unescape(substring)
                substring = re.sub('\(\d+\)','',substring)
                substring = substring.replace("’","'")
                substring = substring.strip()
                if ',' in substring:
                    return splitComma(substring)
                else:
                    return [substring]
                #return [x.strip() for x in substring.split(',')]

def checkParoleDizionario():
    polirematiche = readPolirematicheFromFile()
    parole_files = [f for f in sorted(os.listdir(PAROLE_DIZIONARIO)) if f.endswith('.html')]
    for f in parole_files:
        f_path = os.path.join(PAROLE_DIZIONARIO,f)
        titles = getTitlesFromParolaFile(f_path)
        for t in titles:
            number_words = len(t.split())
            if number_words>1 and t not in polirematiche:
                print("{} -> '{}'".format(f, t))

def checkDizionarioBase():
    current_ord = ord('a')
    previous_line = '_'
    with open(DIZIONARIO_BASE_FILE, 'r') as f_in:
        for num,line in enumerate(f_in,1):            
            words = line.lower().split()
            if not words or line.startswith('#'):
                continue
            word = words[0]
            if word < previous_line:
                print('Warning in line {}: "{}"'.format(num,word))
            previous_line = word       
            char = word[0]
            ord_car = ord(char)
            if ord_car == current_ord:
                continue
            if ord_car == current_ord+1:
                current_ord = ord_car
                continue
            else:
                if word in ['yogurt']:
                    current_ord = ord_car
                    continue
                print('Error in line {}: "{}"'.format(num,word))
                return            

def get_dizionario_base_set(write_to_file=False):
    dizionario = set()
    with open(DIZIONARIO_BASE_FILE, 'r') as f_in:
        for num,line in enumerate(f_in,1):  
            words = line.lower().split()
            if not words or line.startswith('#'):
                continue
            word = words[0]
            dizionario.add(word)
    if write_to_file:
        write_lexicon_to_file(sorted(dizionario), DIZIONARIO_BASE_SORTED_FILE)
    return dizionario      

def get_polirematiche_set(write_to_file=False):
    polirematiche = set()    
    with open(POLIREMATICHE_FILE, 'r') as f_in:
        for num,line in enumerate(f_in,1):  
            poli = line.lower().split('\t')[0]            
            polirematiche.add(poli)
    if write_to_file:
        write_lexicon_to_file(sorted(polirematiche), POLIREMATICHE_SORTED_FILE)
    return polirematiche      

def extractSostantiviFromDizionarioBase():
    sostantivi = set()
    with open(DIZIONARIO_BASE_FILE, 'r') as f_in:
        for num,line in enumerate(f_in,1):  
            words_pos = line.lower().split()
            if not words_pos or line.startswith('#'):
                continue
            word = words_pos[0]
            if any([x for x in words_pos[1:] if x in ['s.m.','s.f.','s.m.inv.','s.f.inv.',]]):
                sostantivi.add(word)
    write_lexicon_to_file(sorted(sostantivi), DIZIONARIO_BASE_SOSTANTIVI_FILE)

def extractAggettiviFromDizionarioBase():
    aggettivi = set()
    with open(DIZIONARIO_BASE_FILE, 'r') as f_in:
        for num,line in enumerate(f_in,1):  
            words_pos = line.lower().split()
            if not words_pos or line.startswith('#'):
                continue
            word = words_pos[0]
            if any([x for x in words_pos[1:] if x == 'agg.']):
                aggettivi.add(word)
    write_lexicon_to_file(sorted(aggettivi), DIZIONARIO_BASE_AGGETTIVI_FILE)


def write_lexicon_to_file(sorted_list, file_out):
    with open(file_out, 'w') as f_out:
        for w in sorted_list:
            f_out.write(w + '\n')

def check_dizionario_polirematiche_base_coverage():
    import corpora
    import scorer
    import patterns_extraction
    dizionario = get_dizionario_base_set(False)
    polirematiche = get_polirematiche_set(True)
    for p in polirematiche:
        p = patterns_extraction.tokenizeLine(p)
        for w in p.split():
            dizionario.add(w)
    write_lexicon_to_file(sorted(dizionario), DIZ_POLI_WORD_SORTED_FILE)
    report_coverage_file = DE_MAURO_PATH + 'diz_poli_game_coverage.txt'    
    lexicon_freq = {w:1 for w in dizionario}
    scorer.computeCoverageOfGameWordLex(lexicon_freq, corpora.GAME_SET_100_FILE, report_coverage_file) 

def check_dizionario_base_base_coverage():
    import corpora
    import scorer
    dizionario = get_dizionario_base_set(False)
    lexicon_freq = {w:1 for w in dizionario}
    report_coverage_file = DE_MAURO_PATH + 'diz_base_game_coverage.txt'    
    scorer.computeCoverageOfGameWordLex(lexicon_freq, corpora.GAME_SET_100_FILE, report_coverage_file) 


if __name__=='__main__':
    #checkParoleDizionario()
    #checkDizionarioBase()
    check_dizionario_polirematiche_base_coverage()
            
                    