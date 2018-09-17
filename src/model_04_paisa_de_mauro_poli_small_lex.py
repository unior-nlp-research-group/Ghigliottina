#! /usr/bin/env python3
# -*- coding: utf-8 -*-


import corpora
import utility
import path
import matrix_dict
import lexicon
import scorer

######################################
## MODEL 04 PAISA + DE MAURO POLIREMATICHE small lex
######################################

OUTPUT_DIR = path.GHIGLIOTTINA_BASE_FILE_PATH + "model_04_paisa_de_mauro_poli_small_lex_dict/"

LEX_FREQ_FILE = OUTPUT_DIR + "lex_freq.txt"
LEX_INDEX_FILE = OUTPUT_DIR + "lex_index.pkl"
MATRIX_FILE = OUTPUT_DIR + "matrix.pkl"
COVERAGE_WORD_GAME100_FILE = OUTPUT_DIR + "game_word_100_coverage.txt"
EVAL_WORD_GAME100_FILE = OUTPUT_DIR + "game_word_100_eval.txt"

DE_MAURO_WEIGHT = 50

def build_and_eval():
    utility.make_dir(OUTPUT_DIR)
    print('Building lexicon')
    poli_lexicon = list(lexicon.loadLexiconFromFile(corpora.DIZ_POLI_WORD_SORTED_FILE))
    sost_lexicon = list(lexicon.loadLexiconFromFile(corpora.DIZIONARIO_SOSTANTIVI_AUGMENTED_PAISA_FILE))
    agg_lexicon = list(lexicon.loadLexiconFromFile(corpora.DIZIONARIO_AGGETTIVI_AUGMENTED_PAISA_FILE))
    lex_set = set(poli_lexicon+sost_lexicon+agg_lexicon)
    lexicon_freq = {w:1 for w in lex_set}   
    lex_solution_set =  set(sost_lexicon+agg_lexicon)
    print('Lex size: {}'.format(len(lex_set)))
    print('Solution Lex size: {}'.format(len(lex_solution_set)))
    lexicon.printLexFreqToFile(lexicon_freq, LEX_FREQ_FILE)
    solution_lexicon_freq = {w:1 for w in lex_solution_set}   
    print('Computing lex_set coverage')
    scorer.computeCoverageOfGameWordLex(lexicon_freq, corpora.GAME_SET_100_FILE, COVERAGE_WORD_GAME100_FILE, solution_lexicon_freq)
    print('Building association matrix')
    matrix = matrix_dict.Matrix_Dict(lex_set, lex_solution_set)
    matrix.add_patterns_from_corpus(corpora.PAISA_RAW_INFO)
    matrix.add_patterns_from_corpus(corpora.DE_MAURO_POLIREMATICHE_INFO, weight=DE_MAURO_WEIGHT)
    corpora.addBigramFromPolirematicheInMatrix(matrix, DE_MAURO_WEIGHT)
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

def interactive_solver():
    print('Loading association matrix')
    matrix = matrix_dict.Matrix_Dict()
    matrix.read_matrix_from_file(MATRIX_FILE)
    scorer.interactive_solver(matrix)

if __name__=='__main__':  
    build_and_eval()
    #interactive_solver()
    #eval()
    