#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import corpora
import patterns_extraction

class Matrix_Base:
    
    def __init__(self, lex_set=None, lex_solution_set=None):
        self.lex_set = lex_set
        self.lex_solution_set = lex_solution_set
        self.symmetric = lex_solution_set == lex_set
        # non symmetric matrix -> keys are only those in lex_solution_set

    def add_patterns_from_corpus(self, corpus_info, weight=1):
        lines_extractor = corpora.extract_lines(corpus_info)
        patterns_count = 0
        for line in lines_extractor:            
            patterns_count += patterns_extraction.addPatternsFromLine(line, self, self.lex_set, weight)    
        print('Extracted patterns: {}'.format(patterns_count))

    def increase_association_score(self, w1, w2, weight=1):
        if self.symmetric:
            # symmetric matrix
            self.increase_weight(w1,w2,weight)
            self.increase_weight(w2,w1,weight)            
        else:        
            # non symmetric matrix -> keys are only those in lex_solution_set
            if w1 in self.lex_solution_set:
                self.increase_weight(w1,w2,weight)
            if w2 in self.lex_solution_set:
                self.increase_weight(w2,w1,weight)


    ##################################  
    # subclasses shouold implement:       
    ##################################
    #def read_matrix_from_file(self, file_input)
    #def write_matrix_to_file(self, file_output)
    #def increase_weight(self, w1, w2, weight)
    #def compute_association_scores(self, symmetric=True)
    #def get_association_score(self, w1, w2)
    #def get_min_association_score(self)
    #def get_max_association_score(matrix)
    #def get_solution_set(self, clues)
