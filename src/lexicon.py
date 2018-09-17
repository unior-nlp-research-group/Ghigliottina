#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import defaultdict
import corpora

def printLexFreqToFile(lex_freq, lex_file_out):
   print("Saving lex to file")
   with open(lex_file_out, 'w') as f_out:    
       for w,f in sorted(lex_freq.items(), key=lambda x: -x[1]):
           f_out.write('{}\t{}\n'.format(f,w))    

def printLexiconToFile(lex_set, lex_file_out):
   print("Saving lex to file to {}".format(lex_file_out))
   with open(lex_file_out, 'w') as f_out:    
       for w in sorted(lex_set):
           f_out.write('{}\n'.format(w))    

def loadLexFreqFromFile(lex_file_in):
    lexicon_freq = {}
    with open(lex_file_in, 'rt') as f_in:
        for line in f_in:
            f,w = line.split()
            lexicon_freq[w] = int(f)
    return lexicon_freq

def loadLexiconFromFile(inputFile):
    lex_set = set()
    with open(inputFile, 'r') as f_in:
        for word in f_in:  
            lex_set.add(word.strip())
    return lex_set

def buildLexIndex(corpora_dict_list, lex_file_in, lex_index_file_out):
    import patterns_extraction
    print('Building lex index...')
    lexicon_freq = loadLexFreqFromFile(lex_file_in)
    lex_set = lexicon_freq.keys()
    # file_name -> w line_number
    lexicon_index = defaultdict(lambda: defaultdict(list))
    for corpus_file in corpora_dict_list:
        print("reading {}".format(corpus_file))
        with gzip.open(corpus_file, 'rt') as f_in:        
            for line_count, line in enumerate(f_in, 1):            
                tokens = patterns_extraction.tokenizeLineReplaceWordCats(line)
                if tokens is None:
                    continue            
                for w in tokens:
                    if w in lex_set:
                        lexicon_index[corpus_file][w].append(line_count)
                if line_count % 500000 == 0:
                    print(line_count)     
    print("Saving lex index to file")
    lexicon_index = default_to_regular(lexicon_index)
    dumpObjToPklFile(lexicon_index, lex_index_file_out)     

def morph_normalize_word(c, lex_freq_dict):
    trans = {
        'i': ['o','a','e'],
        'e': ['a']
    }
    '''
    trans = {
        'i': [
            'o', # casi -> caso
            'a', # problemi -> problema
            'e', # forbici -> forbice
            'ie', # superfici -> superficie
            'io' # figli -> figlio
        ], 
        'e': [
            'a' # perle -> perla
            'ia' # province -> provincia
        ],
        'a': [
            'o' # uova -> uovo
        ],
        'hi': [
            'o', # luoghi -> luogo
            'a' # colleghi -> collega
        ],
        'trice': [
            'tore' # isruttrice -> istruttore
        ]
    }
    '''
    result_freq = {}
    for k, vlist in trans.items():
        if c.endswith(k):
            for v in vlist:
                morphed = c[:-len(k)]+v
                if morphed in lex_freq_dict:
                    result_freq[morphed]=lex_freq_dict[morphed]
    return [item[0] for item in sorted(result_freq.items(), key=lambda x: -x[1])][0] if result_freq else c
