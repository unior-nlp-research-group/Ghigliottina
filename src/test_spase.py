#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
from scipy.sparse import dok_matrix
import corpora
from random import randint
import lexicon
import math

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

'''
S = dok_matrix((5, 5), dtype=np.float32)
for i in range(10):
    rnd_1 = randint(0, 4)
    rnd_2 = randint(0, 4)
    S[rnd_1,rnd_2] += randint(0, 10)
'''

S = dok_matrix((3, 4), dtype=np.float32)
S[0,0] = 1
S[2,0] = 2
S[2,1] = 3
S[0,2] = 4
#S[1,2] = 5
S[2,2] = 6
S[2,3] = 7

print(S)
print(S.todense())
print('size: {}'.format(S.size))
print('values: {}'.format(S.values()))
print('items: {}'.format(S.items()))
print('min value: {}'.format(min(S.values())))
print('row 2: {}'.format(S.getrow(2)))

sum_over_cols = S.sum(0)
sum_over_rows = S.sum(1)

print("Sum over cols: {}".format(sum_over_cols))
print("Sum over rows: {}".format(sum_over_rows))
print(type(sum_over_rows))

row_matrix = S.getrow(1)
print('row 1: {} type:{}'.format(row_matrix, type(row_matrix)))
print("row_matrix size: {}".format(len(row_matrix.nonzero()[0])))
associated_word_indexes = [k[1] for k in row_matrix.nonzero()]
#print('associated_word_indexes: {}'.format(associated_word_indexes))

'''
S_sums = dok_matrix((3, 4), dtype=np.float32)

#sparse_product_rows_cols = dok_matrix((3, 4), dtype=np.float32)

product_rows_cols =  np.matmul(sum_over_rows, sum_over_cols)
print('product_rows_cols')
print(product_rows_cols)

product_rows_cols_pow_minus_one = np.power(product_rows_cols, -1)
print('product_rows_cols_pow_minus_one')
print(product_rows_cols_pow_minus_one)

#S = S.multiply(product_rows_cols)
#print('S multiply product_rows_cols')
#print(S.todense())

S = S.multiply(product_rows_cols_pow_minus_one)
print('S multiply product_rows_cols_pow_minus_one')
print(S.todense())
'''



'''
print('Shape: {}'.format(S.shape))
#print('Keys: {}'.format(S.keys()))
nonzero = S.nonzero()
print('Non zeros: {}'.format(nonzero))
nonzero_rows = nonzero[0]
nonzero_cols = nonzero[1]
print('Non zeros rows: {} of type {}'.format(nonzero_rows, type(nonzero_rows)))
print('Non zeros cols: {} of type {}'.format(nonzero_cols, type(nonzero_cols)))
sum_over_cols = S.sum(0)
print(sum_over_cols)
print(type(sum_over_cols))
#S_csr = S.tocsr()
#print('{}'.format(S_csr.size))
'''

#S = S.power(-1)
#print(S.todense())
#print(S.size)


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
