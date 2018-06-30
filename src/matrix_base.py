#! /usr/bin/env python3

import corpora
import patterns_extraction

class Matrix_Base:
    
    def __init__(self, lex=None):
        self.lex = lex

    def add_patterns_from_corpus(self, corpus_info, weight=1, solution_lexicon=None):
        lines_extractor = corpora.extract_lines(corpus_info)
        patterns_count = 0
        for line in lines_extractor:            
            patterns_count += patterns_extraction.addPatternsFromLine(
                line, self, self.lex, weight, solution_lexicon=solution_lexicon)    
        print('Extracted patterns: {}'.format(patterns_count))

    def increase_association_score(self, w1, w2, weight=1, solution_lexicon=None):
        if solution_lexicon:
            if w1 in solution_lexicon:
                self.increase_weight(w1,w2,weight)
            if w2 in solution_lexicon:
                self.increase_weight(w2,w1,weight)
        else:        
            self.increase_weight(w1,w2,weight)
            self.increase_weight(w2,w1,weight)


    ##################################  
    # subclasses shouold implement:       
    ##################################
    #def read_matrix_from_file(self, file_input)
    #def write_matrix_to_file(self, file_output)
    #def increase_weight(self, w1, w2, weight)
    #def compute_association_scores(self, simmetric=True)
    #def get_association_score(self, w1, w2)
    #def get_min_association_score(self)
    #def get_max_association_score(matrix)
    #def get_union_intersection(self, clues)
    #def printAssociationMatrix(matrix_file_in, output_file)