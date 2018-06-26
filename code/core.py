#! /usr/bin/env python3

import gzip
import re
from collections import defaultdict
import pickle
import math

GHIGLIOTTINA_BASE_FILE_PATH = "/Users/fedja/scratch/Ghigliottina/"

###################
## PATTERN EXTRACTION
###################

DET_SET = ('lo', 'la', 'l', 'il', 'le', 'i', 'gli', 'un', 'uno', 'una')
PREP_SET = ('d', 'di', 'a', 'ad', 'da', 'in', 'con', 'su', 'per', 'tra', 'fra')
CONG_SET = ('e', 'ed', 'o')
PREP_ART_SET = [
    'del', 'dello', 'della', 'dell', 'dei', 'degli', 'delle', 
    'al', 'allo', 'alla', 'all', 'ai', 'agli', 'alle', 
    'dal', 'dallo', 'dalla', 'dall', 'dai', 'dagli', 'dalle', 
    'nel', 'nello', 'nella', 'nell', 'nei', 'negli', 'nelle', 
    'col', 'collo', 'colla', 'coi', 'cogli', 'colle', 
    'sul', 'sullo', 'sulla', 'sull', 'sui', 'sugli', 'sulle'
]

ALL_SET_WORDS = []
for s in [DET_SET, PREP_SET, CONG_SET, PREP_ART_SET]:
    ALL_SET_WORDS.extend(s)

DET_CAT = "<<<DET>>>"
PREP_CAT = "<<<PREP>>>"
CONG_CAT = "<<<CONG>>>"
PREP_ART_CAT = "<<<PREP_ART>>>"
NON_WORD_CAT = "<<<NON_WORD>>>"
PUNCT_CAT = "<<<PUNCT>>>"
UNK_WORD_CAT = "<<<UNK_WORD>>>"

CAT_SET_DICT = {
    DET_CAT: DET_SET,
    PREP_CAT: PREP_SET,
    CONG_CAT: CONG_SET,
    PREP_ART_CAT: PREP_ART_SET,    
}

ALL_PATTERN_CATS = CAT_SET_DICT.keys()
ALL_CATS = (DET_CAT, PREP_CAT, CONG_CAT, PREP_ART_CAT, PUNCT_CAT, NON_WORD_CAT, UNK_WORD_CAT)

#VALID_WORD_PATTERN = re.compile("^[A-ZÀÈÉÌÒÙ]+$")
VALID_WORD_PATTERN = re.compile("^[a-zàèéìòù]+$")

def tokenizeLine(line):
    line = line.strip()
    line = line.lower()
    line = re.sub(r'[;.,:!?…()‹›«»"”“]', ' {} '.format(PUNCT_CAT), line)
    line = re.sub(r"(['’`‘\-])", r' ', line) # apostrophe and dashes are replaced with spaces          
    tokens = line.split()
    return tokens

def replacePrepDetCatWithPrepArt(tokens):
    found_indexes = [i for i in range(len(tokens)-1) if tokens[i]==PREP_CAT and tokens[i+1]==DET_CAT]
    for i in reversed(found_indexes):
        tokens.pop(i)
        tokens[i] = PREP_ART_CAT
    return found_indexes

def replaceWordCats(tokens, lexicon=None, inplace=True):
    tokens_cat = tokens if inplace else list(tokens)
    for i,w in enumerate(tokens_cat):
        if not VALID_WORD_PATTERN.match(w):
            tokens_cat[i] = NON_WORD_CAT
    for i,w in enumerate(tokens_cat):
        if w in ALL_SET_WORDS:
            tokens_cat[i] = substituteWordsWithWordClass(w)    
        elif lexicon and w not in lexicon:
            tokens_cat[i] = UNK_WORD_CAT    
    return tokens_cat

def tokenizeLineReplaceWordCats(line, lexicon=None):        
    tokens = tokenizeLine(line)
    if tokens == None:
        return None
    tokens_cat = replaceWordCats(tokens, lexicon)
    replacePrepDetCatWithPrepArt(tokens_cat)
    return tokens_cat

def substituteWordsWithWordClass(word):
    for c,s in CAT_SET_DICT.items():
        if word in s:
            return c
    return None


'''
Patterns:
A B
A det B
A prep B
A conj B
A prepart B
A prep det B
# ... (A è det B) -- do we want to add this?
'''
def addPatternsFromLine(line, matrix, lexicon, weight=1, solution_lexicon = None, debug=False):        
    if debug:
        print(line.strip())
    tokens = tokenizeLineReplaceWordCats(line, lexicon)
    if tokens is None:
        return 0
    if debug:
        print('line: ' + line)
        print('tokens: ' + ' '.join(tokens))
    patterns_count = 0
    bigrams=ngrams(tokens,2)
    trigrams=ngrams(tokens,3)    
    for w in bigrams:
        # both tokens need to be valid words in dictionary
        if w[0] not in ALL_CATS and w[1] not in ALL_CATS: 
            increaseAssociationScore(w[0], w[1], matrix, weight, solution_lexicon)
            patterns_count += 1
            if debug:
                print("\t{} - {}".format(w[0],w[1]))
    for w in trigrams:
        # first and last tokens need to be valid words in dictionary while middle tokens needs to be a cat (det, prep, ...)
        if w[0] not in ALL_CATS and w[1] in ALL_PATTERN_CATS and w[2] not in ALL_CATS:
            increaseAssociationScore(w[0], w[2], matrix, weight, solution_lexicon)
            patterns_count += 1
            if debug:
                print("\t{} - {}".format(t[0],t[2]))            
    return patterns_count

def increaseAssociationScore(w1, w2, matrix, weight=1, solution_lexicon=None):
    if solution_lexicon:
        if w1 in solution_lexicon:
            matrix[w1][w2] += weight
        if w2 in solution_lexicon:
            matrix[w2][w1] += weight
    else:        
        matrix[w1][w2] += weight
        matrix[w2][w1] += weight



def getLinesConfirmingSolution(clues, solution):
    clues = [x.lower() for x in clues]
    solution = solution.lower()
    lexicon_freq = loadLexFreqFromFile()
    lexicon = lexicon_freq.keys()
    result = defaultdict(list)
    with gzip.open(PAISA_ROW_INPUT, 'rt') as f_in:        
        line_count = 0        
        for line in f_in:            
            line_count += 1
            if line_count%500000==0:
                print(str(line_count))
            tokens = tokenizeLine(line)
            if tokens == None:
                continue
            tokens_cat = replaceWordCats(tokens, lexicon, inplace=False)            
            prep_det_indexes = replacePrepDetCatWithPrepArt(tokens_cat)
            for i in reversed(prep_det_indexes):
                tokens[i] = '{} {}'.format(tokens[i], tokens[i+1])
                tokens.pop(i+1)
            #print("{} {}".format(line_count, line))          
            bigrams, trigrams = None, None
            if solution in tokens_cat:
                for c in clues:
                    if c in tokens_cat:
                        if bigrams==None:
                            bigrams=ngrams(tokens_cat,2)
                            trigrams=ngrams(tokens_cat,3)   
                        for i, b in enumerate(bigrams):
                            if c in b and solution in b:
                                fragment = ' '.join(tokens[i-5:i+7])
                                result[c].append(fragment)
                                #print("{} {}\n\t{}".format(c,s,line))
                        for i, t in enumerate(trigrams):
                            if t[1] in ALL_PATTERN_CATS and c in t and solution in t:
                                fragment = ' '.join(tokens[i-5:i+5])
                                result[c].append(fragment)
                                #print("{} {}\n\t{}".format(c,s,line))
    for c,lines in result.items():
        print("{}\n\t{}".format(c,'\n\t'.join(lines))) 


def ngrams(input, n):
  return [input[i:i+n] for i in range(len(input)-n+1)]

###################
## UTILITY
###################

# convert defaultdict to regular dictionary
def default_to_regular(d):
    if isinstance(d, defaultdict):
        d = {k: default_to_regular(v) for k, v in d.items()}
    return d

def loadObjFromPklFile(pkl_file):
    with gzip.open(pkl_file, "rb") as pkl_in:        
        return pickle.load(pkl_in)

def dumpObjToPklFile(obj, pkl_file):
    with gzip.open(pkl_file, "wb") as pkl_out:  
        pickle.dump(obj, pkl_out)      

###################
## CORPORA
###################

def extract_lines(corpus_info, report_every=100000):
    import re    
    name = corpus_info['name']
    file = corpus_info['file']
    compressed = corpus_info['compressed']
    encoding = corpus_info['encoding']
    exclude_pattern = corpus_info['exlude_pattern']
    print("extracting lines from {}".format(name))
    pattern = re.compile(exclude_pattern) if exclude_pattern else None
    line_count = 0
    opener = gzip.open if compressed else open
    with opener(file, 'rt', encoding=encoding) as f:
        for l in f:
            if pattern and pattern.match(l):
                continue
            line_count += 1
            if line_count%report_every==0:
                print(line_count)
            yield l
        print("extracted lines: {}".format(line_count))
        

def countLinesInCompressedFile(file_in, encoding):
    with gzip.open(file_in, 'rt', encoding=encoding) as f:
        for i,l in enumerate(f, 1):
            pass
        return i

def countWordsInCompressedFile(file_in, encoding):
    with gzip.open(file_in, 'rt', encoding=encoding) as f:
        words = 0
        for i,l in enumerate(f, 1):
            if i%500000==0:
                print(i)
            words += len(l.split())
    return words

###################
## LEXICON
###################

def buildLexicon(corpus_info, lexicon_freq=defaultdict(int)):
    lines_extractor = extract_lines(corpus_info)
    for line in lines_extractor:            
        tokens = tokenizeLineReplaceWordCats(line)
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

def printLexiconToFile(lexicon, lex_file_out):
   print("Saving lex to file to {}".formmat(lex_file_out))
   with open(lex_file_out, 'w') as f_out:    
       for w in sorted(lexicon):
           f_out.write('{}\n'.format(w))    

def loadLexFreqFromFile(lex_file_in):
    lexicon_freq = {}
    with open(lex_file_in, 'rt') as f_in:
        for line in f_in:
            f,w = line.split()
            lexicon_freq[w] = int(f)
    return lexicon_freq

def loadLexiconFromFile(inputFile):
    lexicon = set()
    with open(inputFile, 'r') as f_in:
        for word in f_in:  
            lexicon.add(word.strip())
    return lexicon

def buildLexIndex(corpora_dict_list, lex_file_in, lex_index_file_out):
    print('Building lex index...')
    lexicon_freq = loadLexFreqFromFile(lex_file_in)
    lex = lexicon_freq.keys()
    # file_name -> w line_number
    lexicon_index = defaultdict(lambda: defaultdict(list))
    for corpus_file in corpora_dict_list:
        print("reading {}".format(corpus_file))
        with gzip.open(corpus_file, 'rt') as f_in:        
            for line_count, line in enumerate(f_in, 1):            
                tokens = tokenizeLineReplaceWordCats(line)
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

def computeCoverageOfGameWordLex(lexicon_freq, game_set_file, output_file, solution_lex_freq=None):
    if solution_lex_freq == None:
        solution_lex_freq = lexicon_freq
    game_set = read_game_set_tab(game_set_file)
    game_words_lex = set()
    solution_game_words = set()
    for game_words in game_set:
        solution_game_words.add(game_words[-1])
        for w in game_words:
            game_words_lex.add(w)            
    #print(game_words_lex)
    covered, not_covered = {}, set()
    solution_covered, solution_not_covered = {}, set()
    for w in game_words_lex: 
        if w in lexicon_freq:
            covered[w] = lexicon_freq[w]
        else:
            not_covered.add(w)
    for s in solution_game_words: 
        if s in solution_lex_freq:
            solution_covered[s] = solution_lex_freq[s]
        else:
            solution_not_covered.add(s)
    with open(output_file, 'w') as f_out:
        ## solution coverage
        f_out.write('SOLUTION WORDS COVERED {}/{}\n-------------\n'.format(len(solution_covered), len(solution_game_words)))
        solution_sorted_covered = sorted(solution_covered.items(), key=lambda x: x[1])
        f_out.write(', '.join(["{} {}".format(f,w) for w,f in solution_sorted_covered]))
        f_out.write('\n\nSOLUTION WORDS NOT COVERED {}/{}\n-------------\n'.format(len(solution_not_covered), len(solution_game_words)))
        f_out.writelines(', '.join([w for w in sorted(solution_not_covered)]))
        ## all words coverage
        f_out.write('\n\nALL WORDS COVERAGE {}/{}\n-------------\n'.format(len(covered), len(game_words_lex)))
        sorted_covered = sorted(covered.items(), key=lambda x: x[1])
        f_out.write(', '.join(["{} {}".format(f,w) for w,f in sorted_covered]))
        f_out.write('\n\nALL WORDS NOT COVERED {}/{}\n-------------\n'.format(len(not_covered), len(game_words_lex)))
        f_out.writelines(', '.join([w for w in sorted(not_covered)]))

###################
## MATRIX
###################

def buildAssociationMatrix(corpus_info, lexicon, matrix = defaultdict(lambda: defaultdict(int)), 
    weight=1, solution_lexicon=None):        
    # extract lines from corpus
    lines_extractor = extract_lines(corpus_info)
    patterns_count = 0
    for line in lines_extractor:            
        patterns_count += addPatternsFromLine(line, matrix, lexicon, weight, solution_lexicon=solution_lexicon)    
    print('Extracted patterns: {}'.format(patterns_count))
    return matrix    

def computeAssociationScores(matrix, simmetric=True):
    print("Computing association scores")
    # word_prob = {w:sum(matrix[w].values())/total_pairs for w in matrix.keys()}
    # pointwise mutual information f(A,B) / (f(A)·f(B))  //leaving out proportional factor sum
    total_pairs = sum([sum(d.values()) for d in matrix.values()])/2
    print('Total pairs: {}'.format(total_pairs))
    if simmetric:
        word_freq_in_pairs = {w:sum(matrix[w].values()) for w in matrix.keys()}                        
    else:
        word_freq_in_pairs = defaultdict(int)
        rows = matrix.keys()
        for w in matrix.keys():
            word_freq_in_pairs[w] = sum(matrix[w].values())
        for sub_table in matrix.values():
            for w,f in sub_table.items():
                if w not in rows:
                    word_freq_in_pairs[w] += f
    for x,x_friends in matrix.items():
        for y,f in x_friends.items():
            x_friends[y] = math.log(total_pairs * f/(word_freq_in_pairs[x]*word_freq_in_pairs[y]))

def getAssociationScore(w1, w2, matrix):
    if w1 not in matrix:
        return None
    sub_table = matrix.get(w1)    
    return sub_table.get(w2, None)

def getMinAssociationScore(matrix):    
    return min(score for sub_table in matrix.values() for score in sub_table.values())

def getMaxAssociationScore(matrix):    
    return max(score for sub_table in matrix.values() for score in sub_table.values())


def printAssociationMatrix(matrix_file_in, output_file):
    matrix = loadObjFromPklFile(matrix_file_in)
    with open(output_file, 'w') as f_out:        
        for w1,d in matrix.items():
            f_out.write('{}\n'.format(w1))
            for w2, f in d.items():
                f_out.write('\t{} ({})\n'.format(w2, f))

###################
## SOLVING
###################

def computeBestWordAssociation(matrix, clues, unfound_pair_score, debug=False, nBest=10):
    if debug:
        print('Input clues: {}'.format(clues))        
    word_rows = []
    union = None
    intersection = None
    for w in clues:
        if w in matrix.keys():
            row = matrix[w]
            associated_words = row.keys()
            word_rows.append(row)
            if union is None:
                union = set(associated_words)
                intersection = set(associated_words)
            else:
                union = union.union(associated_words)
                intersection = intersection.intersection(associated_words)
    
    for c in clues:
        if c in union:
            union.remove(c)
        if c in intersection:
            intersection.remove(c)
    '''
    if debug:
        print('{}/{} clues found in structure'.format(len(word_rows),len(clues)))
        print('Union: {}'.format(union))
        print('Intersection: {}'.format(intersection))    
    '''
    x_table = {}
    for x in union:
        association_scores = []        
        for w in clues:
            association_scores.append(getAssociationScore(x, w, matrix))
        association_none_replaced = [unfound_pair_score if x==None else x for x in association_scores]
        x_table[x] = {
            'scores': association_none_replaced,
            'sum': sum(association_none_replaced),
            'clues_matched_info': ['X' if x!=None else '_' for x in association_scores],
            'clues_matched_count': sum([1 for x in association_scores if x!=None])            
        }    
    sorted_x_table_groups = sorted(x_table.items(),key=lambda k:(-k[1]['clues_matched_count'],-k[1]['sum']))
    sorted_x_table_sum = sorted(x_table.items(),key=lambda k:-k[1]['sum'])
    if debug:
        for key,value in sorted_x_table_groups[:nBest]:
            print('{}: {} -> sum({}) = {}'.format(key,value['clues_matched_count'], value['scores'], value['sum']))
    else:
        return x_table, sorted_x_table_sum, sorted_x_table_groups

def reportBestWordAssociationGroups(matrix, clues, unfound_pair_score, sets=[5,4], nBest=10):
    x_table, sorted_x_table_sum, sorted_x_table_groups = computeBestWordAssociation(matrix, clues, unfound_pair_score)
    print('\n-------------------------------------')
    print('Absolute best in score')
    print('-------------------------------------')
    for key,value in sorted_x_table_sum[:nBest]:
            scores = ', '.join(['{0:.1f}'.format(s) for s in value['scores']])
            scores_sum = '{0:.1f}'.format(value['sum'])
            print('{}: {} -> sum({}) = {}'.format(key,value['clues_matched_count'], scores, scores_sum))
    for s in sets:
        print('\n-------------------------------------')
        print('Best of {}'.format(s))
        print('-------------------------------------')
        sorted_x_table_set = [x for x in sorted_x_table_groups if x[1]['clues_matched_count'] == s]
        for key,value in sorted_x_table_set[:nBest]:
            scores = ', '.join(['{0:.1f}'.format(s) for s in value['scores']])
            scores_sum = '{0:.1f}'.format(value['sum'])
            print('{}: {} -> sum({}) = {}'.format(key,value['clues_matched_count'], scores, scores_sum))

###################
## EVALUATION
###################

def read_game_set_tab(game_set_file):
    game_set = []
    with open(game_set_file, 'r') as f_in:
        for line in f_in:
            tokens = [x.strip() for x in line.lower().split('\t')]
            if len(tokens)!=6:
                continue
            game_set.append(tokens)
    return game_set

def getSolutionRank(matrix, clues, solution, unfound_pair_score):    
    x_table, sorted_x_table_sum, sorted_x_table_groups = computeBestWordAssociation(matrix, clues, unfound_pair_score)    
    sorted_table_sum_keys = [i[0] for i in sorted_x_table_sum]
    sorted_table_groups_keys = [i[0] for i in sorted_x_table_groups]    
    if solution not in sorted_table_sum_keys:
        WORST_RANK_DEFAULT = 9999
        return WORST_RANK_DEFAULT, WORST_RANK_DEFAULT, 0, WORST_RANK_DEFAULT, [unfound_pair_score]*5, ['_']*5
    abs_rank = sorted_table_sum_keys.index(solution)+1
    group_rank = sorted_table_groups_keys.index(solution)+1
    sorted_x_table_matched = {}    
    for s in [5,4,3,2,1,0]:
        sorted_x_table_matched[s] = [x[0] for x in sorted_x_table_groups if x[1]['clues_matched_count'] == s ]
    group = x_table[solution]['clues_matched_count']
    scores = x_table[solution]['scores']
    clues_matched_info = x_table[solution]['clues_matched_info']
    rank_in_group = sorted_x_table_matched[group].index(solution)+1
    return abs_rank, group_rank, group, rank_in_group, scores, clues_matched_info

def evaluate_kbest_MeanReciprocalRank(matrix, game_set_file, output_file):  
    unfound_pair_score = getMinAssociationScore(matrix)
    print("Min association score: {0:.1f}".format(unfound_pair_score)) 
    game_set = read_game_set_tab(game_set_file)
    kbest_list = [1,10,25,50,75,100]
    kbest_dict_abs_rank, kbest_dict_group_rank = defaultdict(int), defaultdict(int)
    eval_details = []
    MRR_score_abs_rank, MRR_score_group_rank = 0, 0
    for game_words in game_set:
        clues = game_words[:5]
        solution = game_words[5]
        abs_rank, group_rank, group, rank_in_group, scores, clues_matched_info = getSolutionRank(
            matrix, clues, solution, unfound_pair_score)
        spaced_clues_matched_info = ' '.join(clues_matched_info)
        spaced_scores = ' '.join(['{0:.1f}'.format(x) for x in scores])
        score_sum_str = '{0:.1f}'.format(sum(scores))
        report_fields = clues + [solution, abs_rank, group_rank, group, rank_in_group, spaced_clues_matched_info, spaced_scores, score_sum_str]
        eval_report = '\t'.join([str(x) for x in report_fields])
        print(eval_report)
        eval_details.append(eval_report)
        if abs_rank<=100:
            MRR_score_abs_rank += 1./abs_rank
        if group_rank<=100:
            MRR_score_group_rank += 1./group_rank
        for t in kbest_list:
            if abs_rank<=t:
                kbest_dict_abs_rank[t] += 1
            if group_rank<=t:
                kbest_dict_group_rank[t] += 1
    total = len(game_set) 
    kbest_scores_abs_rank = sorted(kbest_dict_abs_rank.items())
    kbest_scores_group_rank = sorted(kbest_dict_group_rank.items())        
    summary = [
        'total games: {}'.format(total),
        '\nk-best scores abs rank:',
        '\t'.join([str(k) for k,score in kbest_scores_abs_rank]),
        '\t'.join([str(score) for k,score in kbest_scores_abs_rank]),
        '\nMean Reciprocal Rank score abs rank: {0:.1f}'.format(MRR_score_abs_rank),
        '\nk-best scores group rank:',
        '\t'.join([str(k) for k,score in kbest_scores_group_rank]),
        '\t'.join([str(score) for k,score in kbest_scores_group_rank]),        
        '\nMean Reciprocal Rank score group rank: {0:.1f}'.format(MRR_score_group_rank),

    ]
    print('\n'.join(summary))
    with open(output_file, 'w') as f_out:
        f_out.write('\n'.join(summary))
        f_out.write('\n\nPosition Details:\n\n')
        f_out.write('\n'.join(eval_details))

def solver(matrix):
    unfound_pair_score = getMinAssociationScore(matrix)
    print("Min association score: {0:.1f}".format(unfound_pair_score)) 
    while True:
        text = input('\nInserisci le 5 parole divise da virgole/tab o premi invio per uscire\n--> ')
        text = text.strip().lower()
        if not text:
            print('exitig')
            return
        sep = ',' if ',' in text else '\t'
        clues = [w.strip() for w in text.split(sep)]
        if len(clues)!=5:
            print('Hai inserito {} parole, riprova.\n'.format(len(clues)))
            continue
        reportBestWordAssociationGroups(matrix, clues, unfound_pair_score, sets=[5,4,3], nBest=5)
        solution = input('\nInserisci la parola corretta o premi invio per testare nuove parole\n--> ')
        solution = solution.strip().lower()
        if not solution:
            continue
        if solution not in matrix:
            print('La parola "{}" non presente nel dizionario\n'.format(solution))
            continue
        abs_rank, group_rank, group, rank_in_group, scores, clues_matched_info = getSolutionRank(
            matrix, clues, solution, unfound_pair_score)
        print("\nScores: " + ', '.join(['{0:.1f}'.format(s) for s in scores]))
        print("\nAbs rank:{}\nGroup rank:{}\nGROUP (matched clues):{}\nPosition in group:{}\nClues matched:{}\n".format(
            abs_rank, group_rank, group, rank_in_group, clues_matched_info))

###################
## main
###################

if __name__=='__main__':  
    import argparse
    parser = argparse.ArgumentParser()    
    parser.add_argument("-m", "--model", help="the path to the model file")    
    args = parser.parse_args()
    print('Loading association matrix')
    matrix = loadObjFromPklFile(args.model)
    solver(matrix)

