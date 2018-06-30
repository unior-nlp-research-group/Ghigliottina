#! /usr/bin/env python3
from collections import defaultdict

def buildLexicon(corpus_info, lexicon_freq=defaultdict(int)):
    import patterns_extraction
    lines_extractor = extract_lines(corpus_info)
    for line in lines_extractor:            
        tokens = patterns_extraction.tokenizeLineReplaceWordCats(line)
        if tokens is None:
            continue            
        for w in tokens:
            if w not in ALL_CATS:
                lexicon_freq[w] += 1 
    return lexicon_freq

def pruneLexicon(lexicon_freq, prune_ge_freq):
    original_size = len(lexicon_freq)    
    pruned_lexicon_freq = { w:f for w,f in lexicon_freq.items() if f >= prune_ge_freq }  
    new_size = len(pruned_lexicon_freq)  
    print('Pruned lex: {} -> {}'.format(original_size, new_size))
    return pruned_lexicon_freq  

def printLexFreqToFile(lex_freq, lex_file_out):
   print("Saving lex to file")
   with open(lex_file_out, 'w') as f_out:    
       for w,f in sorted(lex_freq.items(), key=lambda x: -x[1]):
           f_out.write('{}\t{}\n'.format(f,w))    

def printLexiconToFile(lex, lex_file_out):
   print("Saving lex to file to {}".formmat(lex_file_out))
   with open(lex_file_out, 'w') as f_out:    
       for w in sorted(lex):
           f_out.write('{}\n'.format(w))    

def loadLexFreqFromFile(lex_file_in):
    lexicon_freq = {}
    with open(lex_file_in, 'rt') as f_in:
        for line in f_in:
            f,w = line.split()
            lexicon_freq[w] = int(f)
    return lexicon_freq

def loadLexiconFromFile(inputFile):
    lex = set()
    with open(inputFile, 'r') as f_in:
        for word in f_in:  
            lex.add(word.strip())
    return lex

def buildLexIndex(corpora_dict_list, lex_file_in, lex_index_file_out):
    import patterns_extraction
    print('Building lex index...')
    lexicon_freq = loadLexFreqFromFile(lex_file_in)
    lex = lexicon_freq.keys()
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
                    if w in lex:
                        lexicon_index[corpus_file][w].append(line_count)
                if line_count % 500000 == 0:
                    print(line_count)     
    print("Saving lex index to file")
    lexicon_index = default_to_regular(lexicon_index)
    dumpObjToPklFile(lexicon_index, lex_index_file_out)     