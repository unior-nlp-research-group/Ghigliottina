#! /usr/bin/env python3

import gzip
import re
from collections import defaultdict
import pickle
import math
#import pprint

PRUNE_LEX_LEVEL = 5

#ROW_INPUT = '/Users/fedja/scratch/PAISA/paisa.row.utf8_guanti.gz'
ROW_INPUT = '/Users/fedja/scratch/PAISA/paisa.raw.utf8.gz'
# 7,943,592 lines
WORD_ASSOCIATION_FILE = "/Users/fedja/scratch/Ghigliottina/word_association.pkl"
LEX_FREQ_FILE = "/Users/fedja/scratch/Ghigliottina/paisa_lex_freq.txt"
WORD_ASSOCIATION_PRINT = "/Users/fedja/scratch/Ghigliottina/association_matrix.txt"

DET_SET = ('LO','LA','L','IL','LE','I','GLI','UN','UNO','UNA')
PREP_SET = ('DI','A','DA','IN','CON','SU','PER','TRA','FRA')
CONG_SET = ('E', 'ED', 'O')
PREP_ART_SET = [
    'DEL', 'DELLO', 'DELLA', 'DELL', 'DEI', 'DEGLI', 'DELLE', 
    'AL', 'ALLO', 'ALLA', 'ALL', 'AI', 'AGLI', 'ALLE', 
    'DAL', 'DALLO', 'DALLA', 'DALL', 'DAI', 'DAGLI', 'DALLE', 
    'NEL', 'NELLO', 'NELLA', 'NELL', 'NEI', 'NEGLI', 'NELLE', 
    'COL', 'COLLO', 'COLLA', 'COI', 'COGLI', 'COLLE', 
    'SUL', 'SULLO', 'SULLA', 'SULL', 'SUI', 'SUGLI', 'SULLE'
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

PREP_DET_CAT_BIGRAM = "{} {}".format(PREP_CAT, DET_CAT)

CAT_SET_DICT = {
    DET_CAT: DET_SET,
    PREP_CAT: PREP_SET,
    CONG_CAT: CONG_SET,
    PREP_ART_CAT: PREP_ART_SET,    
}

ALL_PATTERN_CATS = CAT_SET_DICT.keys()
ALL_CATS = (DET_CAT, PREP_CAT, CONG_CAT, PREP_ART_CAT, PUNCT_CAT, NON_WORD_CAT, UNK_WORD_CAT)

VALID_WORD_PATTERN = re.compile("^[A-ZÀÈÉÌÒÙ]+$")
#VALID_WORD_PATTERN = re.compile("^[A-Zàèéìòù]+$")


def dd():
    return defaultdict(int)

def default_to_regular(d):
    if isinstance(d, defaultdict):
        d = {k: default_to_regular(v) for k, v in d.items()}
    return d

def tokenizeLine(line, lexicon=None):    
    line = line.strip()
    if line.startswith('<text') or line.startswith('#'):
        return None
    line = line.upper()
    line = re.sub(r'[;.,:!?…()‹›«»"”“]', ' {} '.format(PUNCT_CAT), line)
    line = re.sub(r"(['’`‘\-])", r' ', line) # apostrophe and dashes are replaced with spaces          
    words = line.split()
    for i,w in enumerate(words):
        if not VALID_WORD_PATTERN.match(w):
            words[i] = NON_WORD_CAT
    for i,w in enumerate(words):
        if w in ALL_SET_WORDS:
            words[i] = substituteWordsWithWordClass(w)    
        elif lexicon and w not in lexicon:
            words[i] = UNK_WORD_CAT
    words_str = ' '.join(words)
    if PREP_DET_CAT_BIGRAM in words_str:
        words_str = words_str.replace(PREP_DET_CAT_BIGRAM, PREP_ART_CAT)
        words = words_str.split()
    return words

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
'''
def addPatternsFromLine(line, association_table, lexicon, debug=False):        
    if debug:
        print(line.strip())
    words = tokenizeLine(line, lexicon)
    if words is None:
        return False
    if debug:
        print(str(words))
    bigrams=ngrams(words,2)
    trigrams=ngrams(words,3)    
    for b in bigrams:
        if b[0] not in ALL_CATS and b[1] not in ALL_CATS:            
            increaseAssociationScore(b[0], b[1], association_table)
            if debug:
                print("\t{} - {}".format(b[0],b[1]))
    for t in trigrams:
        if t[0] not in ALL_CATS and t[2] not in ALL_CATS and t[1] in ALL_PATTERN_CATS:
            increaseAssociationScore(t[0], t[2], association_table)
            if debug:
                print("\t{} - {}".format(t[0],t[2]))            
    return True

def ngrams(input, n):
  return [input[i:i+n] for i in range(len(input)-n+1)]

def increaseAssociationScore(w1, w2, association_table):
    association_table[w1][w2] += 1
    association_table[w2][w1] += 1    

def getAssociationScore(w1, w2, association_table):
    #return association_table[w1][w2]
    subDict = association_table.get(w1, None)    
    return 0 if subDict==None else subDict.get(w2, 0)

def buildLexicon():
    print('Building lexicon...')
    lexicon_freq = defaultdict(int)
    with gzip.open(ROW_INPUT, 'rt') as f_in:        
        line_count = 0
        for line in f_in:            
            words = tokenizeLine(line)
            if words is None:
                continue            
            for w in words:
                if w not in ALL_CATS:
                    lexicon_freq[w] += 1 
            line_count += 1 
            if line_count % 500000 == 0:
                print(line_count)            
            #if line_count == 1000:
            #    break
    print('Read {} lines'.format(line_count))
    pruned_lexicon_freq = pruneLexicon(lexicon_freq)
        
    print("Saving lex to file")
    with open(LEX_FREQ_FILE, 'w') as f_out:    
        for w,f in sorted(pruned_lexicon_freq.items()):
            f_out.write('{}\t{}\n'.format(w,f))    

    return pruned_lexicon_freq

def pruneLexicon(lexicon_freq):
    original_size = len(lexicon_freq)    
    new_lexicon_freq = { w:f for w,f in lexicon_freq.items() if f >= PRUNE_LEX_LEVEL }  
    new_size = len(new_lexicon_freq)  
    print('Pruned lex: {} -> {}'.format(original_size, new_size))
    return new_lexicon_freq  


def buildPaisaAssociationMatrix():    
    lexicon_freq = buildLexicon()
    association_table = defaultdict(dd)
    print("Extracting patterns from sentences")
    with gzip.open(ROW_INPUT, 'rt') as f_in:        
        line_count = 0
        for line in f_in:            
            if addPatternsFromLine(line, association_table, lexicon_freq.keys()):
                line_count += 1 
                if line_count % 500000 == 0:
                    print(line_count)            
                #if line_count == 1000:
                #    break
    computeAssociationScores(association_table)
    association_table = default_to_regular(association_table)
    print("Saving association matrix to file")
    with gzip.open(WORD_ASSOCIATION_FILE, "wb") as pkl_out:
        pickle.dump( association_table, pkl_out )
    return association_table

def computeAssociationScores(association_table):
    print("Computing association scores")
    #total_pairs = sum([sum(d.values()) for d in association_table.values()])/2
    #print('Total pairs: {}'.format(total_pairs))
    #word_prob = {w:sum(association_table[w].values())/total_pairs for w in association_table.keys()}
    word_pairs = {w:sum(association_table[w].values()) for w in association_table.keys()}                    
    for x,d in association_table.items():
        for y,f in d.items():
            d[y] = math.log(f/(word_pairs[x]*word_pairs[y]))

def openPaisaAssociationMatrix():
    with gzip.open(WORD_ASSOCIATION_FILE, "rb") as pkl_in:        
        association_table = pickle.load(pkl_in)
    #print(association_table['BIANCA'])
    return association_table

def printAssociationMatrix():
    association_table = openPaisaAssociationMatrix()
    with open(WORD_ASSOCIATION_PRINT, 'w') as f_out:        
        for w1,d in association_table.items():
            f_out.write('{}\n'.format(w1))
            for w2, f in d.items():
                f_out.write('\t{} ({})\n'.format(w2, f))

def getPaisaLexiconFreq():
    lexicon_freq = {}
    with open(LEX_FREQ_FILE, 'rt') as f_in:
        for line in f_in:
            w,f = line.split()
            lexicon_freq[w] = int(f)
    return lexicon_freq


def computeCoverageOfGameWordLex():
    paisa_lexicon_freq = getPaisaLexiconFreq()
    paisa_lex = paisa_lexicon_freq.keys()
    game_words_lex = set()
    with open('game_words.txt', 'rt') as f_in:
        for line in f_in:
            line = line.strip()
            line = line.upper()
            words = line.split('\t')
            for w in words:
                game_words_lex.add(w)
    #print(game_words_lex)
    covered, not_covered = '', ''
    covered_count, not_covered_count = 0, 0
    for w in game_words_lex: 
        if w in paisa_lex:
            covered_count += 1
            covered += '{} ({})\n'.format(w, paisa_lexicon_freq[w])
        else:
            not_covered_count += 1
            not_covered += '{}\n'.format(w)
    total = covered_count + not_covered_count
    with open('coverage.txt', 'w') as f_out:
        f_out.write('COVERED {}/{}\n-------------\n'.format(covered_count, total))
        f_out.write(covered)
        f_out.write('\n\nNOT COVERED {}/{}\n-------------\n'.format(not_covered_count, total))
        f_out.write(not_covered)

def getBestWordAssociation(association_table, words, debug=False, nBest=10):
    if debug:
        print('Input words: {}'.format(words))        
    at = {}
    word_rows = []
    union = None
    intersection = None
    for w in words:
        if w in association_table.keys():
            row = association_table[w]
            associated_words = row.keys()
            word_rows.append(row)
            if union is None:
                union = set(associated_words)
                intersection = set(associated_words)
            else:
                union = union.union(associated_words)
                intersection = intersection.intersection(associated_words)
    '''
    if debug:
        print('{}/{} words found in structure'.format(len(word_rows),len(words)))
        print('Union: {}'.format(union))
        print('Intersection: {}'.format(intersection))    
    '''
    x_table = {}
    for x in union:
        association_scores = []
        for w in words:
            association_scores.append(getAssociationScore(x, w, association_table))
        x_table[x] = {
            'scores': association_scores,
            'sum': sum(association_scores),
            'elements': sum([1 for x in association_scores if x!=0])
        }
    #for key,value in sorted(x_table.items(),key=lambda i:sum(i[1]),reverse=True):
    #    print('{} {}'.format(key,value))
    sorted_x_table = sorted(x_table.items(),key=lambda k:(-k[1]['elements'],-k[1]['sum']))
    if debug:
        for key,value in sorted_x_table[:nBest]:
            print('{}: {} -> sum({}) = {}'.format(key,value['elements'], value['scores'], value['sum']))
    else:
        return x_table, sorted_x_table

def getBestWordAssociation54(association_table, words, debug=False, sets=[5,4], nBest=10):
    x_table, sorted_x_table = getBestWordAssociation(association_table, words)
    for s in sets:
        print('\n-------------------------------------')
        print('Best of {} words'.format(s))
        print('-------------------------------------')
        sorted_x_table_set = [x for x in sorted_x_table if x[1]['elements'] == s]
        for key,value in sorted_x_table_set[:nBest]:
            print('{}: {} -> sum({}) = {}'.format(key,value['elements'], value['scores'], value['sum']))

def evaluatePosition(association_table, clues, unknown, debug=False, nBest=20):
    x_table, sorted_x_table = getBestWordAssociation(association_table, clues)
    sorted_guess_keys = [i[0] for i in sorted_x_table]
    index = sorted_guess_keys.index(unknown)+1 if unknown in sorted_guess_keys else -1
    if debug:
        print("{} | {} -> {}".format(clues, unknown, index))
    if debug and index!=1:
        for key,value in sorted_x_table[:nBest]:
            print('{}: {} -> sum({}) = {}'.format(key,value['elements'], value['scores'], value['sum']))
        if index>nBest:
            print('...')
            for key,value in sorted_x_table[index-5:index+6]:
                print('{}: {} -> sum({}) = {}'.format(key,value['elements'], value['scores'], value['sum']))
    return index

def evaluate(association_table):    
    with open('game_words.txt', 'rt') as f_in:
        nBest_threshold = [1,10,25,50,100]
        freq_dict = defaultdict(int)
        total = 0
        for line in f_in:
            words = line.upper().split()
            if len(words)!=6:
                continue
            total+= 1
            clues = words[:5]
            unknown = words[5]
            index = evaluatePosition(association_table, clues, unknown)
            for t in nBest_threshold:
                if index<=t:
                    freq_dict[t] += 1
    freq_dict = {k:"{0:.2f}".format(f/total*100) for k,f in freq_dict.items()}
    print(sorted(freq_dict.items()))

def evalute516():
    import pandas as pd    
    from collections import Counter
    print('Loading association table...')
    association_table = openPaisaAssociationMatrix()
    print('Loaded')
    df = pd.read_csv("../data/ghigliottina.csv")
    df = df.dropna()
    results = Counter({False:0, True:0})
    for i in range(len(df)):
        words = [w.upper() for w in set(df.iloc[i,0:5].values)]
        x_table, sorted_x_table = getBestWordAssociation(association_table, words)
        topn = 10
        guesses = [g[0] for g in sorted_x_table[:topn]]
        solution = df.solution[i].upper()
        correct = solution in guesses
        print('{}: words: {} guessed: {} solution: {} correct: {}'.format(i+1, words, guesses, solution, correct))
        results.update({correct:1})
    print(results)
    # Counter({True: 332, False: 185})

def evalute_basile_2016(method56=False):
    import pandas as pd    
    from collections import Counter
    print('Loading association table...')
    association_table = openPaisaAssociationMatrix()
    print('Loaded')
    files = ["../data/ghigliottina_tv.csv", "../data/ghigliottine_board.csv"]
    for f in files:
        df = pd.read_csv(f)
        df = df.dropna()
        results = {
            1: Counter({False:0, True:0}),
            5: Counter({False:0, True:0}),
            10: Counter({False:0, True:0}),
            100: Counter({False:0, True:0}),
        }
        for i in range(len(df)):
            words = [w.upper() for w in set(df.iloc[i,0:5].values)]
            x_table, sorted_x_table = getBestWordAssociation(association_table, words)
            sorted_x_table_5 = [x for x in sorted_x_table if x[1]['elements'] == 5]
            sorted_x_table_4 = [x for x in sorted_x_table if x[1]['elements'] == 4]
            for topn in results.keys():                
                if method56 and topn!=1:
                    half = topn//2
                    guesses = [g[0] for g in sorted_x_table_5[:half]] + [g[0] for g in sorted_x_table_4[:half]]
                else:
                    guesses = [g[0] for g in sorted_x_table[:topn]]
                solution = df.solution[i].upper()
                correct = solution in guesses
                #if topn==10:
                #    print('{}: words: {} guessed: {} solution: {} correct: {}'.format(i+1, words, guesses, solution, correct))
                results[topn].update({correct:1})
        print('File: {}'.format(f))
        for k in results:            
            c = results[k]
            correct, wrong, total = c[True], c[False], sum(c.values())
            p = float(correct)/total
            print('P@{}: {} --> Correct: {} Wrong: {} Total: {}'.format(k, p, correct, wrong, total))

def run():
    #buildPaisaAssociationMatrix()
    #print('Built Association Matrix')
    #printAssociationMatrix()
    #computeCoverageOfGameWordLex()

    association_table = openPaisaAssociationMatrix()
    print('Loaded association table')


    #words = 'Donna Lana Portiere Trattare Gialli'.upper().split()
    #words = 'Scadenza	Amore	Essere	Fine	Passato PROSSIMO'.upper().split()
    #words = 'auto ragazza andare militare coda'.upper().split()
    #words = 'mano pugno sotto invito sabbia'.upper().split() -> scritto #(sottoscritto parola sola)
    #getBestWordAssociation(association_table, words, debug=True, nBest=20)

    #words = ['PICCOLO', 'SCOPRIRE', 'IDENTITÀ', 'ABITAZIONE', 'PRECEDENTI', 'FURTO'] # 'scoprire un furto' not found
    #words = ['GIARDINO', 'INSETTI', 'CENSURA', 'ANELLI', 'PAIO', 'FORBICI'] # 'insetti forbici' not found
    #clues = words[:5]
    #unknown = words[5]
    #evaluatePosition(association_table, clues, unknown, debug=True)


    #evaluate(association_table)


if __name__=='__main__':
    run()

# import engine
# association_table = engine.openPaisaAssociationMatrix()
# engine.getBestWordAssociation54(association_table,'cinema gran comune battere coda'.upper().split(), debug=True, sets=[5,4], nBest=20)