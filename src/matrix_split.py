#! /usr/bin/env python3
# -*- coding: utf-8 -*-

from collections import defaultdict
import math
import utility
#from matrix_base import Matrix_Base
import os

class Matrix_Split():
    
    def __init__(self, split_dir, unfound_score):
        # split_dir is the dir for one file per word in the solution set
        self.split_dir = split_dir
        self.unfound_score = unfound_score

    def get_pkl_file_path(self, word):
        return os.path.join(self.split_dir, word) + '.pkl'

    def get_min_association_score(self):    
        return self.unfound_score

    def get_row_subtable(self, w1):
        pkl_file = self.get_pkl_file_path(w1)
        if not os.path.isfile(pkl_file):
            return None
        return utility.loadObjFromPklFile(pkl_file)  

    def get_association_score(self, w1, w2, unfound_score):
        sub_table = self.get_row_subtable(w1)
        if sub_table:
            return sub_table.get(w2, unfound_score)
        return unfound_score

    def get_solutions_table(self, clues, update_x_table):
        '''
        update_x_table(x_key, clue_index, x_clue_score)
        only if matches
        '''
        for i,c in enumerate(clues):
            clue_subtable = self.get_row_subtable(c)
            if clue_subtable is None:
                continue
            for x,s in clue_subtable.items():
                if s not in clues:
                    update_x_table(x, i, s)

    def get_solution_set(self, clues):
        union = set()
        for c in clues:
            pkl_file = self.get_pkl_file_path(c)
            if os.path.isfile(pkl_file):
                row = utility.loadObjFromPklFile(pkl_file)  
                associated_words = row.keys()
                union = union.union(associated_words)
        for c in clues:
            if c in union:
                union.remove(c)
        return union