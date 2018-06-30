#! /usr/bin/env python3

from collections import defaultdict
import math
import utility
from matrix_base import Matrix_Base

class Matrix_Dict(Matrix_Base):
    
    def __init__(self, lex=None):
        super().__init__(lex) # initialize lex
        if lex:
            self.table = defaultdict(lambda: defaultdict(int))

    def read_matrix_from_file(self, file_input):
        self.table = utility.loadObjFromPklFile(file_input)

    def write_matrix_to_file(self, file_output):
        self.table = utility.default_to_regular(self.table)
        utility.dumpObjToPklFile(self.table, file_output)

    ##############################
    # Defined in base class
    ##############################
    # def add_patterns_from_corpus(self, corpus_info, weight=1, solution_lexicon=None)
    # def increase_association_score(self, w1, w2, weight=1, solution_lexicon=None)

    def increase_weight(self, w1, w2, weight):
        self.table[w1][w2] += weight        

    def compute_association_scores(self, simmetric=True):
        print("Computing association scores")
        # word_prob = {w:sum(self.table[w].values())/total_pairs for w in self.table.keys()}
        # pointwise mutual information f(A,B) / (f(A)·f(B))  //leaving out proportional factor sum
        total_pairs = sum([sum(d.values()) for d in self.table.values()])/2
        print('Total pairs: {}'.format(total_pairs))
        if simmetric:
            word_freq_in_pairs = {w:sum(self.table[w].values()) for w in self.table.keys()}                        
        else:
            word_freq_in_pairs = defaultdict(int)
            rows = self.table.keys()
            for w in self.table.keys():
                word_freq_in_pairs[w] = sum(self.table[w].values())
            for sub_table in self.table.values():
                for w,f in sub_table.items():
                    if w not in rows:
                        word_freq_in_pairs[w] += f
        for x,x_friends in self.table.items():
            for y,f in x_friends.items():
                x_friends[y] = math.log(total_pairs * f/(word_freq_in_pairs[x]*word_freq_in_pairs[y]))

    def get_association_score(self, w1, w2):
        if w1 not in self.table:
            return None
        sub_table = self.table.get(w1)    
        return sub_table.get(w2, None)

    def get_min_association_score(self):    
        return min(score for sub_table in self.table.values() for score in sub_table.values())

    def get_max_association_score(matrix):    
        return max(score for sub_table in self.table.values() for score in sub_table.values())

    def get_union_intersection(self, clues):
        union = None
        intersection = None
        word_rows = []
        for w in clues:
            if w in self.table.keys():
                row = self.table[w]
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
        return union, intersection


    def printAssociationMatrix(matrix_file_in, output_file):
        matrix = loadObjFromPklFile(matrix_file_in)
        with open(output_file, 'w') as f_out:        
            for w1,d in matrix.items():
                f_out.write('{}\n'.format(w1))
                for w2, f in d.items():
                    f_out.write('\t{} ({})\n'.format(w2, f))