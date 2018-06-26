#! /usr/bin/env python3

import core
import resources
import util

######################################
## MODEL 02 DE MAURO POLIREMATICHE
######################################

OUTPUT_DIR = core.GHIGLIOTTINA_BASE_FILE_PATH + "model_02_de_mauro_poli/"

LEX_FREQ_FILE = OUTPUT_DIR + "lex_freq.txt"
LEX_INDEX_FILE = OUTPUT_DIR + "lex_index.pkl"
MATRIX_FILE = OUTPUT_DIR + "matrix.pkl"
COVERAGE_WORD_GAME100_FILE = OUTPUT_DIR + "game_word_100_coverage.txt"
EVAL_WORD_GAME100_FILE = OUTPUT_DIR + "game_word_100_eval.txt"

def addBigramFromPolirematicheInMatrix(matrix):
    with open(resources.POLIREMATICHE_SORTED_FILE, 'r') as f_in:
        for line in f_in:
            words = line.split()
            if len(words)==2:
                core.increaseAssociationScore(words[0], words[1], matrix)

def build_and_eval():
    util.make_dir(OUTPUT_DIR)
    print('Building lexicon')
    lexicon = core.loadLexiconFromFile(resources.DIZ_POLI_WORD_SORTED_FILE)
    lexicon_freq = {w:1 for w in lexicon}
    print('Lex size: {}'.format(len(lexicon)))
    core.printLexFreqToFile(lexicon_freq, LEX_FREQ_FILE)
    print('Computing coverage')
    core.computeCoverageOfGameWordLex(lexicon_freq, resources.GAME_SET_100_FILE, COVERAGE_WORD_GAME100_FILE)
    print('Building association matrix')
    matrix = core.buildAssociationMatrix(resources.DE_MAURO_POLIREMATICHE_INFO, lexicon)
    addBigramFromPolirematicheInMatrix(matrix)
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
    build_and_eval()
    #solver()
    #eval()
    