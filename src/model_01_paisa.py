#! /usr/bin/env python3

import corpora
import utility
import path
import matrix_dict
import lexicon
import scorer
import patterns_extraction

###################
## MODEL 01 BASE
###################

OUTPUT_DIR = path.GHIGLIOTTINA_BASE_FILE_PATH + "model_01_paisa_dict/"

PRUNE_GE_FREQ = 50

LEX_FREQ_FILE = OUTPUT_DIR + "paisa_lex_freq.txt"
LEX_INDEX_FILE = OUTPUT_DIR + "paisa_lex_index.pkl"
MATRIX_FILE = OUTPUT_DIR + "matrix.pkl"
COVERAGE_WORD_GAME100_FILE = OUTPUT_DIR + "game_word_100_coverage.txt"
EVAL_WORD_GAME100_FILE = OUTPUT_DIR + "game_word_100_eval.txt"

def coverage():
    lexicon_freq = lexicon.loadLexFreqFromFile(LEX_FREQ_FILE)
    scorer.computeCoverageOfGameWordLex(lexicon_freq, corpora.GAME_SET_100_FILE, COVERAGE_WORD_GAME100_FILE)

def build_and_eval():
    utility.make_dir(OUTPUT_DIR)
    print('Building lexicon')
    lexicon_freq = lexicon.buildLexicon(corpora.PAISA_RAW_INFO)    
    pruned_lexicon_freq = lexicon.pruneLexicon(lexicon_freq, PRUNE_GE_FREQ)
    lexicon.printLexFreqToFile(pruned_lexicon_freq, LEX_FREQ_FILE)
    print('Computing coverage')
    scorer.computeCoverageOfGameWordLex(pruned_lexicon_freq, corpora.GAME_SET_100_FILE, COVERAGE_WORD_GAME100_FILE)
    print('Building association matrix')    
    matrix = matrix_dict.Matrix_Dict(lex_set=pruned_lexicon_freq.keys())
    matrix.add_patterns_from_corpus(corpora.PAISA_RAW_INFO)
    matrix.compute_association_scores()
    matrix.write_matrix_to_file(MATRIX_FILE)
    print('Eval')
    scorer.evaluate_kbest_MeanReciprocalRank(matrix, corpora.GAME_SET_100_FILE, EVAL_WORD_GAME100_FILE)

def eval():
    print('Loading association matrix')
    matrix = matrix_dict.Matrix_Dict()
    matrix.read_matrix_from_file(MATRIX_FILE)
    print('Evaluating')
    scorer.evaluate_kbest_MeanReciprocalRank(matrix, corpora.GAME_SET_100_FILE, EVAL_WORD_GAME100_FILE)

def solver():
    print('Loading association matrix')
    matrix = matrix_dict.Matrix_Dict()
    matrix.read_matrix_from_file(MATRIX_FILE)
    scorer.solver(matrix)

if __name__=='__main__':  
    #coverage()
    #build_and_eval()
    #solver()
    eval()
    