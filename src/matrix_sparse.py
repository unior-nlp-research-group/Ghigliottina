#! /usr/bin/env python3
# -*- coding: utf-8 -*-


from collections import defaultdict
import math
import utility
from matrix_base import Matrix_Base
import numpy as np
import scipy.sparse
from scipy.sparse import dok_matrix

class Matrix_Sparse(Matrix_Base):
    
    def __init__(self, lex_set=None, lex_solution_set=None):
        super().__init__(lex_set, lex_solution_set) # initialize lex_set and lex_solution_set
        self.lex_indexes = {} # word -> index of word
        self.indexes_lex = {} # index -> word
        if lex_set:
            self.table = dok_matrix((len(lex_set), len(lex_set)), dtype=np.float32)
            for l in lex_set:
                l_index = self.lex_indexes.setdefault(l, len(self.lex_indexes)) 
                self.indexes_lex[l_index] = l

    # read from .npz file
    def read_matrix_from_file(self, file_input):
        csf_matrix = scipy.sparse.load_npz(file_input)
        self.table = csf_matrix.todok()

    # save to .npz file
    def write_matrix_to_file(self, file_output):
        csf_matrix = self.table.tocsr()
        scipy.sparse.save_npz(file_output, csf_matrix)

    ##############################
    # Defined in base class
    ##############################
    # def add_patterns_from_corpus(self, corpus_info, weight=1, lex_solution_set=None)
    # def increase_association_score(self, w1, w2, weight=1, lex_solution_set=None)

    def get_word_index(self, w):
        return self.lex_indexes.get(w, None)

    def increase_weight(self, w1, w2, weight):
        i1 = self.get_word_index(w1)
        i2 = self.get_word_index(w2)
        self.table[i1,i2] += weight

    def compute_association_scores(self):
        print("Computing association scores")
        # word_prob = {w:sum(self.table[w].values())/total_pairs for w in self.table.keys()}
        # pointwise mutual information f(A,B) / (f(A)·f(B))  //leaving out proportional factor sum
        total_pairs_freq_sum = self.table.sum()
        print('Total pairs sum: {}'.format(total_pairs_freq_sum))

        #nonzero_cols = self.table.nonzero[2]
        #rows_sum = self.table.sum(1) # n x 1 vector with sums across rows
        word_freq_in_pairs = self.table.sum(0) # 1 x n vector with sums across columns

        for x_index, y_index in self.table.keys():   
            # pair = (x_index, y_index)
            self.table[x_index, y_index] = math.log(
                total_pairs_freq_sum * self.table[x_index, y_index] / 
                (word_freq_in_pairs[0,x_index] * word_freq_in_pairs[0,y_index])
            )

    def get_association_score(self, w1, w2, unfound_score):
        i1 = self.get_word_index(w1)
        i2 = self.get_word_index(w2)
        if i1 is None or i2 is None:
            return unfound_score
        return self.table[i1,i2]      

    def get_min_association_score(self):    
        return min(self.table.values())

    def get_max_association_score(matrix):    
        return max(self.table.values())

    def get_union_intersection(self, clues):
        union_idx = None
        intersection_idx = None
        for c in clues:
            i = self.get_word_index(c)
            if i is None:
                continue
            non_zero_in_row = self.table.getrow(i).nonzero() # (array with x-values, array with y-values)
            associated_word_indexes = non_zero_in_row[1]
            if len(associated_word_indexes)==0:
                continue            
            if union_idx is None:
                union_idx = set(associated_word_indexes)
                intersection_idx = set(associated_word_indexes)
            else:
                union_idx = union_idx.union(associated_word_indexes)
                intersection_idx = intersection_idx.intersection(associated_word_indexes)        
        union_lex = set([self.indexes_lex[i] for i in union_idx])
        intersection_lex = set([self.indexes_lex[i] for i in intersection_idx])
        for c in clues:
            if c in union_lex:
                union_lex.remove(c)
            if c in intersection_lex:
                intersection_lex.remove(c)
        return union_lex, intersection_lex


 