#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import defaultdict
import math
import utility
from matrix_base import Matrix_Base

class Matrix_Dict(Matrix_Base):
    
    def __init__(self, lex_set=None, lex_solution_set=None):
        super().__init__(lex_set, lex_solution_set) # initialize lex_set and lex_solution_set
        if lex_set:
            self.table = defaultdict(lambda: defaultdict(int))

    def read_matrix_from_file(self, file_input):
        self.table = utility.loadObjFromPklFile(file_input)

    def write_matrix_to_file(self, file_output):
        self.table = utility.default_to_regular(self.table)
        utility.dumpObjToPklFile(self.table, file_output)

    def size(self):
        return len(self.table)
    ##############################
    # Defined in base class
    ##############################
    # def add_patterns_from_corpus(self, corpus_info, weight=1)
    # def increase_association_score(self, w1, w2, weight=1)

    def increase_weight(self, w1, w2, weight):
        self.table[w1][w2] += weight        

    def compute_association_scores(self):
        print("Computing association scores")
        # word_prob = {w:sum(self.table[w].values())/total_pairs_freq_sum for w in self.table.keys()}
        # pointwise mutual information f(A,B) / (f(A)·f(B))  //leaving out proportional factor sum
        total_pairs_freq_sum = sum([sum(d.values()) for d in self.table.values()])/2
        print('Total pairs freq sum: {}'.format(total_pairs_freq_sum))
        if self.symmetric:
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
                x_friends[y] = math.log(total_pairs_freq_sum * f/(word_freq_in_pairs[x]*word_freq_in_pairs[y]))

    def get_min_association_score(self):    
        return min(score for sub_table in self.table.values() for score in sub_table.values())

    def get_max_association_score(self):    
        return max(score for sub_table in self.table.values() for score in sub_table.values())

    def get_association_score(self, w1, w2, unfound_score):
        if w1 not in self.table:
            return unfound_score
        sub_table = self.table.get(w1)    
        return sub_table.get(w2, unfound_score)

    def get_solution_set(self, clues):
        union = set()
        for c in clues:
            if c in self.table.keys():
                row = self.table[c]
                associated_words = row.keys()
                union = union.union(associated_words)
        for c in clues:
            if c in union:
                union.remove(c)
        return union

    def get_solutions_table(self, clues, update_x_table):
        '''
        clues may have spaces
        update_x_table(x_key, clue_index, x_clue_score)
        only if matches
        '''
        for i,c in enumerate(clues):
            cw_list = c.split()
            multi_tokens = len(cw_list)>1
            for j, cw in enumerate(cw_list):
                last_multi_tokens = j == len(cw_list)-1
                clue_subtable = self.table.get(cw, None)
                if clue_subtable is None:
                    continue
                for solution,score in clue_subtable.items():
                    if solution not in clues:                        
                        update_x_table(solution, i, score, multi_tokens, last_multi_tokens)

    def split_matrix_dict(self, ouput_dir):
        import os
        for w,d in self.table.items():
            file_pkl = os.path.join(ouput_dir, '{}.pkl'.format(w))
            utility.dumpObjToPklFile(d, file_pkl)

    def print_row_column_sets(self, row_output_file, column_output_file):
        import lexicon
        row_set = set(self.table.keys())
        column_set = set()
        for subtable in self.table.values():
            column_set.update(subtable.keys())
        lexicon.printLexiconToFile(row_set, row_output_file)
        lexicon.printLexiconToFile(column_set, column_output_file)

    def reverse_matrix(self):
        matrix = Matrix_Dict()
        matrix.table = defaultdict(lambda: defaultdict(int))
        for clue, clue_subtable in self.table.items():
            for solution, weight in clue_subtable.items():
                matrix.table[solution][clue] = weight        
        return matrix

    def genererate_game(self):
        import random
        lex_file = "./diz_base_sorted.txt"  # "./lex_freq_1000.txt" 
        with open(lex_file) as f_in:
            lex = set(w.strip() for w in f_in.readlines())
        solution_lex = lex.intersection(self.table.keys())
        solution = random.choice(list(solution_lex))
        clues_table = {clue:score for clue,score in self.table[solution].items() if clue in lex}
        clues_scores = sorted(clues_table.items(), key=lambda x: -x[1])
        best_clues_scores = clues_scores[:5]
        #clues = random.sample(acceptable_clues, 5)
        clues = [x[0] for x in best_clues_scores]
        scores = [x[1] for x in best_clues_scores]
        #scores = [solution_clues_subtable[c] for c in clues]
        return clues, solution, scores