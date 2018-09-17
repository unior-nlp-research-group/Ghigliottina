#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import corpora
import utility
import path
import matrix_dict


import lexicon
import scorer

######################################
## MODEL 05 ALL CORPORA small lex
######################################

OUTPUT_DIR = path.GHIGLIOTTINA_BASE_FILE_PATH + "model_05_all_corpora_small_lex_dict/"

LEX_FREQ_FILE = OUTPUT_DIR + "lex_freq.txt"
SOLUTION_LEX_FREQ_FILE = OUTPUT_DIR + "lex_freq_solution.txt"
LEX_INDEX_FILE = OUTPUT_DIR + "lex_index.pkl"
MATRIX_FILE = OUTPUT_DIR + "matrix.pkl"
COVERAGE_WORD_GAME100_FILE = OUTPUT_DIR + "game_word_100_coverage.txt"
EVAL_WORD_GAME100_FILE = OUTPUT_DIR + "game_word_100_eval.txt"
EVAL_WORD_NLP4FUN_DEV_TV_FILE = OUTPUT_DIR + "game_word_NP4FUN_DEV_TV_eval.txt"
EVAL_WORD_NLP4FUN_DEV_BG_FILE = OUTPUT_DIR + "game_word_NP4FUN_DEV_BG_eval.txt"

TEST_SET = corpora.GAME_SET_100_FILE
TEST_RESULTS_CSV_1 = OUTPUT_DIR + 'NLP4FUN_TEST_v2_ALL_results_1.tsv'
TEST_RESULTS_CSV_2 = OUTPUT_DIR + 'NLP4FUN_TEST_v2_ALL_results_2.tsv'
TEST_RESULTS_SUBMIT_1 = OUTPUT_DIR + 'nlp4fun2018.orientale.run1'
TEST_RESULTS_SUBMIT_2 = OUTPUT_DIR + 'nlp4fun2018.orientale.run2'

DE_MAURO_WEIGHT = 200
PROVERBI_WEIGHT = 100
WIKI_IT_WEIGHT = 50
COMPOUNDS_WEIGHT = 50

def build_and_eval():
    utility.make_dir(OUTPUT_DIR)

    print('Building lexicon')

    poli_lexicon = list(lexicon.loadLexiconFromFile(corpora.DIZ_POLI_WORD_SORTED_FILE))
    sost_lexicon = list(lexicon.loadLexiconFromFile(corpora.DIZIONARIO_SOSTANTIVI_AUGMENTED_PAISA_FILE))
    agg_lexicon = list(lexicon.loadLexiconFromFile(corpora.DIZIONARIO_AGGETTIVI_AUGMENTED_PAISA_FILE))
    lex_set = set(poli_lexicon+sost_lexicon+agg_lexicon)
    lex_solution_set =  set(sost_lexicon+agg_lexicon)

    '''
    poli_lexicon = list(lexicon.loadLexiconFromFile(corpora.DIZ_POLI_WORD_SORTED_FILE))
    sost_lexicon = list(corpora.getSostantiviSetFromPaisa(min_freq=1000, inflected=True))
    print('\nSize of sostantivi lex: {}'.format(len(sost_lexicon)))
    agg_lexicon = list(corpora.getAggettiviSetFromPaisa(min_freq=1000, inflected=True))
    print('\nSize of agg lex: {}'.format(len(agg_lexicon)))
    lex_set = set(poli_lexicon + sost_lexicon + agg_lexicon)
    '''

    lexicon.printLexiconToFile(lex_set, LEX_FREQ_FILE)
    lexicon.printLexiconToFile(lex_solution_set, SOLUTION_LEX_FREQ_FILE)

    print('Computing lex coverage')
    scorer.computeCoverageOfGameWordLex(lex_set, lex_solution_set, TEST_SET, COVERAGE_WORD_GAME100_FILE)
    
    print('Building association matrix')
    matrix = matrix_dict.Matrix_Dict(lex_set, lex_solution_set)
    matrix.add_patterns_from_corpus(corpora.PAISA_RAW_INFO)
    matrix.add_patterns_from_corpus(corpora.DE_MAURO_POLIREMATICHE_INFO, weight=DE_MAURO_WEIGHT)
    matrix.add_patterns_from_corpus(corpora.PROVERBI_INFO, weight=PROVERBI_WEIGHT)    
    matrix.add_patterns_from_corpus(corpora.ITWAC_RAW_INFO, weight=1)
    matrix.add_patterns_from_corpus(corpora.WIKI_IT_TITLES_INFO, weight=WIKI_IT_WEIGHT)        
    #matrix.add_patterns_from_corpus(corpora.WIKI_IT_TEXT_INFO, weight=1)        
    corpora.addBigramFromPolirematicheInMatrix(matrix, DE_MAURO_WEIGHT)    
    corpora.addBigramFromCompunds(matrix, lex_set, min_len=4, weight=COMPOUNDS_WEIGHT)
    matrix.compute_association_scores()
    matrix.write_matrix_to_file(MATRIX_FILE)
    print('Eval')
    scorer.evaluate_kbest_MeanReciprocalRank(matrix, TEST_SET, EVAL_WORD_GAME100_FILE)

def eval():
    from convert_xml import output_results
    print('Loading association matrix')
    matrix = matrix_dict.Matrix_Dict()
    matrix.read_matrix_from_file(MATRIX_FILE)
    print('Evaluating')
    #scorer.evaluate_kbest_MeanReciprocalRank(matrix, TEST_SET, EVAL_WORD_GAME100_FILE)
    #scorer.evaluate_kbest_MeanReciprocalRank(matrix, corpora.NLP4FUN_DEV_TSV_v2_tv_FILE, EVAL_WORD_NLP4FUN_DEV_TV_FILE)
    #scorer.evaluate_kbest_MeanReciprocalRank(matrix, corpora.NLP4FUN_DEV_TSV_v2_bg_FILE, EVAL_WORD_NLP4FUN_DEV_BG_FILE)
    scorer.batch_solver(matrix, corpora.NLP4FUN_TEST_TSV_v2_ALL_FILE, TEST_RESULTS_CSV_1, extra_search=False)
    scorer.batch_solver(matrix, corpora.NLP4FUN_TEST_TSV_v2_ALL_FILE, TEST_RESULTS_CSV_2, extra_search=True)
    output_results(corpora.NLP4FUN_TEST_XML_v2_FILE, TEST_RESULTS_CSV_1, TEST_RESULTS_SUBMIT_1)
    output_results(corpora.NLP4FUN_TEST_XML_v2_FILE, TEST_RESULTS_CSV_2, TEST_RESULTS_SUBMIT_2)

def interactive_solver():
    print('Loading association matrix')
    matrix = matrix_dict.Matrix_Dict()
    matrix.read_matrix_from_file(MATRIX_FILE)
    scorer.interactive_solver(matrix)

if __name__=='__main__':  
    #build_and_eval()
    #interactive_solver()
    eval()
    