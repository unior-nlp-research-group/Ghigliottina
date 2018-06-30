#! /usr/bin/env python3

import corpora
import utility
import path
import matrix_dict
import lexicon
import scorer
import patterns_extraction

######################################
## MODEL 05 ALL CORPORA small lex
######################################

OUTPUT_DIR = path.GHIGLIOTTINA_BASE_FILE_PATH + "model_05_all_corpora_small_lex/"

LEX_FREQ_FILE = OUTPUT_DIR + "lex_freq.txt"
LEX_INDEX_FILE = OUTPUT_DIR + "lex_index.pkl"
MATRIX_FILE = OUTPUT_DIR + "matrix.pkl"
COVERAGE_WORD_GAME100_FILE = OUTPUT_DIR + "game_word_100_coverage.txt"
EVAL_WORD_GAME100_FILE = OUTPUT_DIR + "game_word_100_eval.txt"

DE_MAURO_WEIGHT = 200
PROVERBI_WEIGHT = 100
WIKI_IT_WEIGHT = 50

def addBigramFromPolirematicheInMatrix(matrix, weight, solution_lexicon=None):
    with open(corpora.POLIREMATICHE_SORTED_FILE, 'r') as f_in:
        for line in f_in:
            words = line.split()
            if len(words)==2:
                matrix.increase_association_score(words[0], words[1], weight, solution_lexicon)

def build_and_eval():
    utility.make_dir(OUTPUT_DIR)
    print('Building lexicon')
    poli_lexicon = list(lexicon.loadLexiconFromFile(corpora.DIZ_POLI_WORD_SORTED_FILE))
    sost_lexicon = list(lexicon.loadLexiconFromFile(corpora.DIZIONARIO_SOSTANTIVI_AUGMENTED_PAISA_FILE))
    agg_lexicon = list(lexicon.loadLexiconFromFile(corpora.DIZIONARIO_AGGETTIVI_AUGMENTED_PAISA_FILE))
    #sost_lex_freq_paisa = lexicon.loadLexFreqFromFile(corpora.PAISA_SOSTANTIVI_FREQ_FILE)
    #agg_lex_freq_paisa = lexicon.loadLexFreqFromFile(corpora.PAISA_AGGETTIVI_FREQ_FILE)
    #sost_lexicon = list(w for w,f in sost_lex_freq_paisa.items() if f>100)
    #agg_lexicon = list(w for w,f in agg_lex_freq_paisa.items() if f>100)
    lex = set(poli_lexicon+sost_lexicon+agg_lexicon)
    lexicon_freq = {w:1 for w in lex}   
    solution_lexicon =  set(sost_lexicon+agg_lexicon)
    print('Lex size: {}'.format(len(lex)))
    print('Solution Lex size: {}'.format(len(solution_lexicon)))
    lexicon.printLexFreqToFile(lexicon_freq, LEX_FREQ_FILE)
    solution_lexicon_freq = {w:1 for w in solution_lexicon}   
    print('Computing coverage of solution lexicon')
    scorer.computeCoverageOfGameWordLex(lexicon_freq, corpora.GAME_SET_100_FILE, COVERAGE_WORD_GAME100_FILE, solution_lexicon_freq)
    print('Building association matrix')
    matrix = matrix_dict.Matrix_Dict(lex=lex)
    matrix.add_patterns_from_corpus(corpora.PAISA_RAW_INFO, solution_lexicon=solution_lexicon)
    matrix.add_patterns_from_corpus(corpora.DE_MAURO_POLIREMATICHE_INFO, weight=DE_MAURO_WEIGHT,solution_lexicon=solution_lexicon)
    matrix.add_patterns_from_corpus(corpora.PROVERBI_INFO, weight=PROVERBI_WEIGHT,solution_lexicon=solution_lexicon)    
    matrix.add_patterns_from_corpus(corpora.ITWAC_RAW_INFO, weight=1,solution_lexicon=solution_lexicon)
    matrix.add_patterns_from_corpus(corpora.WIKI_IT_TITLES_INFO, weight=WIKI_IT_WEIGHT,solution_lexicon=solution_lexicon)    
    matrix.add_patterns_from_corpus(corpora.WIKI_IT_TEXT_INFO, weight=1,solution_lexicon=solution_lexicon)        
    addBigramFromPolirematicheInMatrix(matrix, DE_MAURO_WEIGHT, solution_lexicon=solution_lexicon)    
    matrix.compute_association_scores(simmetric=False)
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
    #build_and_eval()
    #solver()
    eval()
    