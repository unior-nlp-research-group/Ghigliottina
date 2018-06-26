#! /usr/bin/env python3

import core
import resources
import util

######################################
## MODEL 03 PAISA + DE MAURO POLIREMATICHE (only lex from poli)
######################################

OUTPUT_DIR = core.GHIGLIOTTINA_BASE_FILE_PATH + "model_03_paisa_de_mauro_poli/"

LEX_FREQ_FILE = OUTPUT_DIR + "lex_freq.txt"
LEX_INDEX_FILE = OUTPUT_DIR + "lex_index.pkl"
MATRIX_FILE = OUTPUT_DIR + "matrix.pkl"
COVERAGE_WORD_GAME100_FILE = OUTPUT_DIR + "game_word_100_coverage.txt"
EVAL_WORD_GAME100_FILE = OUTPUT_DIR + "game_word_100_eval.txt"

DE_MAURO_WEIGHT = 50

def addBigramFromPolirematicheInMatrix(matrix, weight, solution_lexicon=None):
    with open(resources.POLIREMATICHE_SORTED_FILE, 'r') as f_in:
        for line in f_in:
            words = line.split()
            if len(words)==2:
                core.increaseAssociationScore(words[0], words[1], matrix, weight, solution_lexicon)

def build_and_eval():
    util.make_dir(OUTPUT_DIR)
    print('Building lexicon')
    lexicon = core.loadLexiconFromFile(resources.DIZ_POLI_WORD_SORTED_FILE)
    lexicon_freq = {w:1 for w in lexicon}   
    #solution_lexicon =  core.loadLexiconFromFile(resources.DIZIONARIO_BASE_SOSTANTIVI_FILE)
    print('Lex size: {}'.format(len(lexicon)))
    core.printLexFreqToFile(lexicon_freq, LEX_FREQ_FILE)
    print('Computing coverage')
    core.computeCoverageOfGameWordLex(lexicon_freq, resources.GAME_SET_100_FILE, COVERAGE_WORD_GAME100_FILE)
    print('Building association matrix')
    matrix = core.buildAssociationMatrix(resources.PAISA_RAW_INFO, lexicon) #solution_lexicon
    core.buildAssociationMatrix(resources.DE_MAURO_POLIREMATICHE_INFO, lexicon, matrix=matrix, weight=DE_MAURO_WEIGHT) #solution_lexicon
    addBigramFromPolirematicheInMatrix(matrix, DE_MAURO_WEIGHT) #solution_lexicon
    core.computeAssociationScores(matrix) # simmetric=False
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
    