#! /usr/bin/env python3
# -*- coding: utf-8 -*-


import corpora
import utility
import path
import matrix_dict
import lexicon
import scorer

###################
## MODEL 01 BASE
###################

OUTPUT_DIR = path.GHIGLIOTTINA_BASE_FILE_PATH + "model_01_paisa_dict/"

LEX_FREQ_FILE = OUTPUT_DIR + "paisa_lex_freq.txt"
SOLUTION_LEX_FREQ_FILE = OUTPUT_DIR + "lex_freq_solution.txt"
LEX_INDEX_FILE = OUTPUT_DIR + "paisa_lex_index.pkl"
MATRIX_FILE = OUTPUT_DIR + "matrix.pkl"
COVERAGE_WORD_GAME100_FILE = OUTPUT_DIR + "game_word_100_coverage.txt"
EVAL_WORD_GAME100_FILE = OUTPUT_DIR + "game_word_100_eval.txt"
EVAL_WORD_NLP4FUN_DEV_TV_FILE = OUTPUT_DIR + "game_word_NP4FUN_DEV_TV_eval.txt"
EVAL_WORD_NLP4FUN_DEV_BG_FILE = OUTPUT_DIR + "game_word_NP4FUN_DEV_BG_eval.txt"

def coverage():
    lexicon_freq = lexicon.loadLexFreqFromFile(LEX_FREQ_FILE)
    scorer.computeCoverageOfGameWordLex(lexicon_freq, corpora.GAME_SET_100_FILE, COVERAGE_WORD_GAME100_FILE)

def build_and_eval():
    utility.make_dir(OUTPUT_DIR)

    print('Building lexicon')
    poli_lexicon = list(lexicon.loadLexiconFromFile(corpora.DIZ_POLI_WORD_SORTED_FILE))
    sost_lexicon = list(lexicon.loadLexiconFromFile(corpora.DIZIONARIO_SOSTANTIVI_AUGMENTED_PAISA_FILE))
    agg_lexicon = list(lexicon.loadLexiconFromFile(corpora.DIZIONARIO_AGGETTIVI_AUGMENTED_PAISA_FILE))
    lex_set = set(poli_lexicon+sost_lexicon+agg_lexicon)
    lex_solution_set =  set(sost_lexicon+agg_lexicon)
    
    lexicon.printLexiconToFile(lex_set, LEX_FREQ_FILE)
    lexicon.printLexiconToFile(lex_solution_set, SOLUTION_LEX_FREQ_FILE)

    print('Computing coverage')
    scorer.computeCoverageOfGameWordLex(lex_set, lex_solution_set, corpora.GAME_SET_100_FILE, COVERAGE_WORD_GAME100_FILE)

    print('Building association matrix')    
    matrix = matrix_dict.Matrix_Dict(lex_set, lex_solution_set)
    matrix.add_patterns_from_corpus(corpora.PAISA_RAW_INFO)
    matrix.compute_association_scores()
    matrix.write_matrix_to_file(MATRIX_FILE)

    print('Eval')
    scorer.evaluate_kbest_MeanReciprocalRank(matrix, corpora.GAME_SET_100_FILE, EVAL_WORD_GAME100_FILE)
    scorer.evaluate_kbest_MeanReciprocalRank(matrix, corpora.NLP4FUN_DEV_TSV_v2_tv_FILE, EVAL_WORD_NLP4FUN_DEV_TV_FILE)
    scorer.evaluate_kbest_MeanReciprocalRank(matrix, corpora.NLP4FUN_DEV_TSV_v2_bg_FILE, EVAL_WORD_NLP4FUN_DEV_BG_FILE)

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
    #coverage()
    build_and_eval()
    #interactive_solver()
    #eval()
    