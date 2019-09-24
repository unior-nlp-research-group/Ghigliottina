import corpora
import lexicon
from patterns_extraction import get_patterns, UNK_WORD_CAT
import sys
from collections import defaultdict
import random
import utility
import path

OUTPUT_DIR = path.GHIGLIOTTINA_BASE_FILE_PATH + "generator_demauro/"
MATRIX_REVERSED_FILE_PKL = OUTPUT_DIR + 'matrix_generator.pkl'
MATRIX_REVERSED_FILE_JSON = OUTPUT_DIR + 'matrix_generator.json'

def convert_defaultdict_to_dict(matrix):
    result = {}
    for w, d in matrix.items():
        result[w] = dict(d)
    return result

def get_polirematiche_patrix():
    poli_lexicon = list(lexicon.loadLexiconFromFile(corpora.DIZ_POLI_WORD_SORTED_FILE))
    sost_lexicon = list(lexicon.loadLexiconFromFile(corpora.DIZIONARIO_SOSTANTIVI_AUGMENTED_PAISA_FILE))
    agg_lexicon = list(lexicon.loadLexiconFromFile(corpora.DIZIONARIO_AGGETTIVI_AUGMENTED_PAISA_FILE))
    lex_set = set(poli_lexicon+sost_lexicon+agg_lexicon)

    corpus_info = corpora.DE_MAURO_POLIREMATICHE_INFO
    lines_extractor = corpora.extract_lines(corpus_info)

    print("Adding patterns from DE MAURO")
    tot_lines = corpus_info['lines']
    patterns_count = 0
    pattern_with_unk = 0
    words_with_one_association = []
    word_with_less_than_five_association = []
    matrix = defaultdict(lambda: defaultdict(dict))   
    exclude_words = ['avere', 'più', 'che']     
    excluded_patterns = 0
    lines_too_long = 0
    for n,line in enumerate(lines_extractor,1):            
        line = line.strip()
        tokens = line.split()
        if len(tokens)>4:
            print('Line too long: {}'.format(line))
            lines_too_long += 1
            continue
        patterns = get_patterns(line, lex_set)
        for p in patterns:
            # if len(tokens) != len(p):
            #     continue
            w1, w2 = p['w1'], p['w2']
            if w1 in exclude_words or w2 in exclude_words:
                print('Excluding {}'.format(line))
                excluded_patterns +=1 
                continue
            if UNK_WORD_CAT in [w1, w2]:
                pattern_with_unk += 1 
                continue
            matrix[w1][w2] = line
            matrix[w2][w1] = line
        # if len(patterns)==0:
            # patterns such as word PREP
        patterns_count += len(patterns)
    print("Lines too long: {}".format(lines_too_long))
    print("Excluded patterns: {}".format(excluded_patterns))
    for w, d in matrix.items():
        if len(d)==1:
            words_with_one_association.append(w)
    print('Words in matrix before before removal one associations: {}'.format(len(matrix)))
    for d in matrix.values():
        for w in words_with_one_association:
            d.pop(w,None)                
    for w in words_with_one_association:
        matrix.pop(w,None)
    print('Words in matrix after removal one associations: {}'.format(len(matrix)))
    for w, d in matrix.items():
        if len(d)<5:
            word_with_less_than_five_association.append(w)
    print('Words in matrix with less than five associations: {}'.format(len(word_with_less_than_five_association)))
    for w in word_with_less_than_five_association:
        matrix.pop(w,None)
    
    print('Total Lines: {}'.format(tot_lines))
    print('Extracted patterns: {}'.format(patterns_count))
    print('Patterns with unk: {}'.format(pattern_with_unk))
    print('Words with one association: {}'.format(len(words_with_one_association)))
    print('Words in matrix: {}'.format(len(matrix)))

    # utility.dumpObjToPklFile(self.table, file_output)
    matrix = utility.default_to_regular(matrix)
    for d in matrix:
        assert len(matrix[d])>=5
    return matrix

def save_matrix_to_file(matrix):
    import json    
    utility.dumpObjToPklFile(matrix, MATRIX_REVERSED_FILE_PKL)
    with open(MATRIX_REVERSED_FILE_JSON, 'w') as f_out:
        json.dump(matrix, f_out, indent=3, ensure_ascii=False)

def get_matrix_from_file():
    return utility.loadObjFromPklFile(MATRIX_REVERSED_FILE_PKL)

def interactive_generator(matrix):
    while True:
        solution = random.choice(list(matrix.keys()))
        clues = random.sample(list(matrix[solution].keys()), 5)        
        print('\nEcco la prossima ghigliottina:')
        print('\n'.join([c.upper() for c in clues]))
        text = input('\nProva a indovinare --> ')
        guess = text.strip().lower()
        if not guess:
            print('exitig')
            return        
        if guess.lower() == solution.lower():
            print('\nIndovinato!\n')        
        else:
            print('\nSbagliato. La soluzione è {}:\n'.format(solution.upper()))
        for c in clues:
            print('- {}'.format(matrix[solution][c]))
        print()
        text = input('\nVuoi continuare? (y/n) ')
        if not text or text!='y':
            print('exitig')
            return  

if __name__ == "__main__":
    matrix = get_polirematiche_patrix()
    save_matrix_to_file(matrix)
    # matrix = get_matrix_from_file()
    # interactive_generator(matrix)