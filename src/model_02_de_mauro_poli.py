#! /usr/bin/env python3
# -*- coding: utf-8 -*-


import corpora
import utility
import path
import matrix_dict
import lexicon
import scorer

from matrix_dict import Matrix_Dict as Matrix
#from matrix_sparse import Matrix_Sparse as Matrix

######################################
## MODEL 02 DE MAURO POLIREMATICHE
######################################

OUTPUT_DIR = path.GHIGLIOTTINA_BASE_FILE_PATH + "model_02_de_mauro_poli_dict/"

LEX_FREQ_FILE = OUTPUT_DIR + "lex_freq.txt"
LEX_INDEX_FILE = OUTPUT_DIR + "lex_index.pkl"
MATRIX_FILE = OUTPUT_DIR + "matrix.pkl"
COVERAGE_WORD_GAME100_FILE = OUTPUT_DIR + "game_word_100_coverage.txt"
EVAL_WORD_GAME100_FILE = OUTPUT_DIR + "game_word_100_eval.txt"

def build_and_eval():    
    utility.make_dir(OUTPUT_DIR)
    print('\nBuilding lexicon')
    
    lex_set = lexicon.loadLexiconFromFile(corpora.DIZ_POLI_WORD_SORTED_FILE)
    lex_solution_set = lex_set

    '''
    poli_lexicon = list(lexicon.loadLexiconFromFile(corpora.DIZ_POLI_WORD_SORTED_FILE))
    sost_lexicon = list(corpora.getSostantiviSetFromPaisa(min_freq=100, inflected=True))
    print('\nSize of sostantivi lex: {}'.format(len(sost_lexicon)))
    agg_lexicon = list(corpora.getAggettiviSetFromPaisa(min_freq=100, inflected=True))
    print('\nSize of agg lex: {}'.format(len(agg_lexicon)))
    lex_set = set(poli_lexicon + sost_lexicon + agg_lexicon)
    lex_solution_set =  set(sost_lexicon+agg_lexicon)
    #lex_solution_set = lex_set
    '''

    print('\nComputing lex coverage')
    scorer.computeCoverageOfGameWordLex(lex_set, lex_solution_set, corpora.GAME_SET_100_FILE, COVERAGE_WORD_GAME100_FILE)

    print('\nBuilding association matrix')
    matrix = Matrix(lex_set, lex_solution_set)
    matrix.add_patterns_from_corpus(corpora.DE_MAURO_POLIREMATICHE_INFO)
    corpora.addBigramFromPolirematicheInMatrix(matrix, weight=1)
    #corpora.addBigramFromCompunds(matrix, lex_set, min_len=4, weight=10)
    matrix.compute_association_scores()
    matrix.write_matrix_to_file(MATRIX_FILE)
    
    print('\nEval')
    scorer.evaluate_kbest_MeanReciprocalRank(matrix, corpora.GAME_SET_100_FILE, EVAL_WORD_GAME100_FILE)

def eval():    
    print('Loading association matrix')
    matrix = Matrix()    
    matrix.read_matrix_from_file(MATRIX_FILE)
    print('Evaluating')
    scorer.evaluate_kbest_MeanReciprocalRank(matrix, corpora.GAME_SET_100_FILE, EVAL_WORD_GAME100_FILE)

def interactive_solver():
    print('Loading association matrix')
    matrix = Matrix()
    matrix.read_matrix_from_file(MATRIX_FILE)
    scorer.interactive_solver(matrix)

if __name__=='__main__':  
    #build_and_eval()
    #interactive_solver()
    eval()
    