#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from gensim.models import Word2Vec
from corpora import WORD_TO_VEC_GLOVE_MODEL


#model = Word2Vec.load('/Users/fedja/scratch/CORPORA/Word2Vec/hlt.isti.cnr/glove/glove_WIKI')
model = Word2Vec.load('/Users/fedja/scratch/CORPORA/Word2Vec/hlt.isti.cnr/word2vec/models/wiki_iter=5_algorithm=skipgram_window=10_size=300_neg-samples=10.m')

vector = model.wv['casa']  # numpy vector of a word
most_similar = model.wv.most_similar('casa')
#most_similar = model.wv.most_similar('amico	rosso	lente	cintura	terra'.split('\t'))

print(most_similar)

