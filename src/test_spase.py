#! /usr/bin/env python3

import numpy as np
from scipy.sparse import dok_matrix
import corpora
from random import randint
import lexicon

'''
poli_lexicon = list(lexicon.loadLexiconFromFile(corpora.DIZ_POLI_WORD_SORTED_FILE))
sost_lexicon = list(lexicon.loadLexiconFromFile(corpora.DIZIONARIO_SOSTANTIVI_AUGMENTED_PAISA_FILE))
agg_lexicon = list(lexicon.loadLexiconFromFile(corpora.DIZIONARIO_AGGETTIVI_AUGMENTED_PAISA_FILE))

lex = sorted(list(set(poli_lexicon+sost_lexicon+agg_lexicon)))
lex_indexes = {}
for l in lex:
    lex_indexes.setdefault(l, len(lex_indexes))

lex_size = len(lex)
print('Lexicon size: {}'.format(lex_size))

S = dok_matrix((len(lex), len(lex)), dtype=np.float32)

for i in range(100000):
    rnd_1 = randint(0, len(lex)-1)
    rnd_2 = randint(0, len(lex)-1)
    S[rnd_1,rnd_1] += 1

print('Non zero count: {}'.format(S.count_nonzero()))
print('Zero count: {}'.format(lex_size*lex_size - S.count_nonzero()))
# getnnz([axis])
# S.size()
print('Max: {}'.format(S.max()))
'''

#data_csr_size = data_csr.data.size/(1024**2)
#print('Size of sparse csr_matrix: '+ '%3.2f' %data_csr_size + ' MB')

S = dok_matrix((5, 5), dtype=np.float32)
for i in range(10):
    rnd_1 = randint(0, 4)
    rnd_2 = randint(0, 4)
    S[rnd_1,rnd_1] += 1
print(S)
S_csr = S.tocsr()
print('{}'.format(S_csr.size))

'''
print('---')
S_csr = S.tocsr()
print(S_csr)
print("Max: {}".format(S_csr.max()))
print("Min: {}".format(S_csr.min()))

S_csr_log1p = S_csr.log1p()
print('--- S_csr_log1p')
print(S_csr_log1p)

print('---')
S_csr_sqrt = S_csr.sqrt()
print('--- S_csr_sqrt')
print(S_csr_sqrt)
print('--- S_csr')
print(S_csr)

'''
