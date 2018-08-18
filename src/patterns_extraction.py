#! /usr/bin/env python3

import re
import utility

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

def replaceWordCats(tokens, lex_set=None, inplace=True):
    tokens_cat = tokens if inplace else list(tokens)
    for i,w in enumerate(tokens_cat):
        if not VALID_WORD_PATTERN.match(w):
            tokens_cat[i] = NON_WORD_CAT
    for i,w in enumerate(tokens_cat):
        if w in ALL_SET_WORDS:
            tokens_cat[i] = substituteWordsWithWordClass(w)    
        elif lex_set and w not in lex_set:
            tokens_cat[i] = UNK_WORD_CAT    
    return tokens_cat

def tokenizeLineReplaceWordCats(line, lex_set=None):        
    tokens = tokenizeLine(line)
    if tokens == None:
        return None
    tokens_cat = replaceWordCats(tokens, lex_set)
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
# ... (A è indef B) -- do we want to add this?
# ... VERB come indef B
'''
def addPatternsFromLine(line, matrix, lex_set, weight=1, debug=False):        
    if debug:
        print(line.strip())
    tokens = tokenizeLineReplaceWordCats(line, lex_set)
    if tokens is None:
        return 0
    if debug:
        print('line: ' + line)
        print('tokens: ' + ' '.join(tokens))
    patterns_count = 0
    bigrams=utility.ngrams(tokens,2)
    trigrams=utility.ngrams(tokens,3)    
    for w in bigrams:
        # both tokens need to be valid words in dictionary
        if w[0] not in ALL_CATS and w[1] not in ALL_CATS: 
            matrix.increase_association_score(w[0], w[1], weight)
            patterns_count += 1
            if debug:
                print("\t{} - {}".format(w[0],w[1]))
    for w in trigrams:
        # first and last tokens need to be valid words in dictionary while middle tokens needs to be a cat (det, prep, ...)
        if w[0] not in ALL_CATS and w[1] in ALL_PATTERN_CATS and w[2] not in ALL_CATS:
            matrix.increase_association_score(w[0], w[2], weight)
            patterns_count += 1
            if debug:
                print("\t{} - {}".format(w[0],w[2]))            
    return patterns_count


def getLinesConfirmingSolution(clues, solution):    
    clues = [x.lower() for x in clues]
    solution = solution.lower()
    lexicon_freq = loadLexFreqFromFile()
    lex_set = lexicon_freq.keys()
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
            tokens_cat = replaceWordCats(tokens, lex_set, inplace=False)            
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
                            bigrams=utility.ngrams(tokens_cat,2)
                            trigrams=utility.ngrams(tokens_cat,3)   
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