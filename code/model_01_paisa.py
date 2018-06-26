#! /usr/bin/env python3

import core
import resources
import util

###################
## MODEL 01 BASE
###################

OUTPUT_DIR = core.GHIGLIOTTINA_BASE_FILE_PATH + "model_01_paisa/"

PRUNE_GE_FREQ = 50

LEX_FREQ_FILE = OUTPUT_DIR + "paisa_lex_freq.txt"
LEX_INDEX_FILE = OUTPUT_DIR + "paisa_lex_index.pkl"
MATRIX_FILE = OUTPUT_DIR + "matrix.pkl"
COVERAGE_WORD_GAME100_FILE = OUTPUT_DIR + "game_word_100_coverage.txt"
EVAL_WORD_GAME100_FILE = OUTPUT_DIR + "game_word_100_eval.txt"

def coverage():
    lexicon_freq = core.loadLexFreqFromFile(LEX_FREQ_FILE)
    core.computeCoverageOfGameWordLex(lexicon_freq, resources.GAME_SET_100_FILE, COVERAGE_WORD_GAME100_FILE)

def build_and_eval():
    util.make_dir(OUTPUT_DIR)
    print('Building lexicon')
    lexicon_freq = core.buildLexicon(resources.PAISA_RAW_INFO)    
    pruned_lexicon_freq = core.pruneLexicon(lexicon_freq, PRUNE_GE_FREQ)
    core.printLexFreqToFile(pruned_lexicon_freq, LEX_FREQ_FILE)
    print('Computing coverage')
    core.computeCoverageOfGameWordLex(pruned_lexicon_freq, resources.GAME_SET_100_FILE, COVERAGE_WORD_GAME100_FILE)
    print('Building association matrix')
    matrix = core.buildAssociationMatrix(resources.PAISA_RAW_INFO, pruned_lexicon_freq.keys())
    core.computeAssociationScores(matrix)
    matrix = core.default_to_regular(matrix)
    core.dumpObjToPklFile(matrix, MATRIX_FILE)
    print('Eval')
    core.evaluate_kbest_MeanReciprocalRank(matrix, resources.GAME_SET_100_FILE, EVAL_WORD_GAME100_FILE)

def eval():
    print('Loading association matrix')
    matrix = core.loadObjFromPklFile(MATRIX_FILE)
    print('Evaluating')
    core.evaluate_kbest_MeanReciprocalRank(matrix, resources.GAME_SET_100_FILE, EVAL_WORD_GAME100_FILE)

def solver():
    print('Loading association matrix')
    matrix = core.loadObjFromPklFile(MATRIX_FILE)
    core.solver(matrix)

if __name__=='__main__':  
    #coverage()
    #build_and_eval()
    #solver()
    eval()
    