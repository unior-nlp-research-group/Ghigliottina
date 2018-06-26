#! /usr/bin/env python3

import core
import resources
import util

######################################
## MODEL 05 ALL CORPORA small lex
######################################

OUTPUT_DIR = core.GHIGLIOTTINA_BASE_FILE_PATH + "model_05_all_corpora_small_lex/"

LEX_FREQ_FILE = OUTPUT_DIR + "lex_freq.txt"
LEX_INDEX_FILE = OUTPUT_DIR + "lex_index.pkl"
MATRIX_FILE = OUTPUT_DIR + "matrix.pkl"
COVERAGE_WORD_GAME100_FILE = OUTPUT_DIR + "game_word_100_coverage.txt"
EVAL_WORD_GAME100_FILE = OUTPUT_DIR + "game_word_100_eval.txt"

DE_MAURO_WEIGHT = 200
PROVERBI_WEIGHT = 100
WIKI_IT_WEIGHT = 50

def addBigramFromPolirematicheInMatrix(matrix, weight, solution_lexicon=None):
    with open(resources.POLIREMATICHE_SORTED_FILE, 'r') as f_in:
        for line in f_in:
            words = line.split()
            if len(words)==2:
                core.increaseAssociationScore(words[0], words[1], matrix, weight, solution_lexicon)

def build_and_eval():
    util.make_dir(OUTPUT_DIR)
    print('Building lexicon')
    poli_lexicon = list(core.loadLexiconFromFile(resources.DIZ_POLI_WORD_SORTED_FILE))
    sost_lexicon = list(core.loadLexiconFromFile(resources.DIZIONARIO_SOSTANTIVI_AUGMENTED_PAISA_FILE))
    agg_lexicon = list(core.loadLexiconFromFile(resources.DIZIONARIO_AGGETTIVI_AUGMENTED_PAISA_FILE))
    #sost_lex_freq_paisa = core.loadLexFreqFromFile(resources.PAISA_SOSTANTIVI_FREQ_FILE)
    #agg_lex_freq_paisa = core.loadLexFreqFromFile(resources.PAISA_AGGETTIVI_FREQ_FILE)
    #sost_lexicon = list(w for w,f in sost_lex_freq_paisa.items() if f>100)
    #agg_lexicon = list(w for w,f in agg_lex_freq_paisa.items() if f>100)
    lexicon = set(poli_lexicon+sost_lexicon+agg_lexicon)
    lexicon_freq = {w:1 for w in lexicon}   
    solution_lexicon =  set(sost_lexicon+agg_lexicon)
    print('Lex size: {}'.format(len(lexicon)))
    print('Solution Lex size: {}'.format(len(solution_lexicon)))
    core.printLexFreqToFile(lexicon_freq, LEX_FREQ_FILE)
    solution_lexicon_freq = {w:1 for w in solution_lexicon}   
    print('Computing coverage of solution lexicon')
    core.computeCoverageOfGameWordLex(lexicon_freq, resources.GAME_SET_100_FILE, COVERAGE_WORD_GAME100_FILE, solution_lexicon_freq)
    print('Building association matrix')
    matrix = core.buildAssociationMatrix(resources.PAISA_RAW_INFO, lexicon, solution_lexicon=solution_lexicon)
    core.buildAssociationMatrix(resources.DE_MAURO_POLIREMATICHE_INFO, lexicon, matrix=matrix, weight=DE_MAURO_WEIGHT,solution_lexicon=solution_lexicon)
    core.buildAssociationMatrix(resources.PROVERBI_INFO, lexicon, matrix=matrix, weight=PROVERBI_WEIGHT,solution_lexicon=solution_lexicon)    
    core.buildAssociationMatrix(resources.ITWAC_RAW_INFO, lexicon, matrix=matrix, weight=1,solution_lexicon=solution_lexicon)
    core.buildAssociationMatrix(resources.WIKI_IT_TITLES_INFO, lexicon, matrix=matrix, weight=WIKI_IT_WEIGHT,solution_lexicon=solution_lexicon)    
    core.buildAssociationMatrix(resources.WIKI_IT_TEXT_INFO, lexicon, matrix=matrix, weight=1,solution_lexicon=solution_lexicon)        
    addBigramFromPolirematicheInMatrix(matrix, DE_MAURO_WEIGHT, solution_lexicon=solution_lexicon)
    core.computeAssociationScores(matrix, simmetric=False)
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
    #build_and_eval()
    solver()
    #eval()
    