#! /usr/bin/env python3

import corpora
import utility
import path
import matrix_dict
import lexicon
import scorer
import patterns_extraction

######################################
## MODEL 03 PAISA + DE MAURO POLIREMATICHE (only lex from poli)
######################################

OUTPUT_DIR = path.GHIGLIOTTINA_BASE_FILE_PATH + "model_03_paisa_de_mauro_poli/"

LEX_FREQ_FILE = OUTPUT_DIR + "lex_freq.txt"
LEX_INDEX_FILE = OUTPUT_DIR + "lex_index.pkl"
MATRIX_FILE = OUTPUT_DIR + "matrix.pkl"
COVERAGE_WORD_GAME100_FILE = OUTPUT_DIR + "game_word_100_coverage.txt"
EVAL_WORD_GAME100_FILE = OUTPUT_DIR + "game_word_100_eval.txt"

DE_MAURO_WEIGHT = 50

def addBigramFromPolirematicheInMatrix(matrix, weight, solution_lexicon=None):
    with open(corpora.POLIREMATICHE_SORTED_FILE, 'r') as f_in:
        for line in f_in:
            words = line.split()
            if len(words)==2:
                matrix.increase_association_score(words[0], words[1], weight, solution_lexicon)

def build_and_eval():
    utility.make_dir(OUTPUT_DIR)
    print('Building lexicon')
    lex = lex.loadLexiconFromFile(corpora.DIZ_POLI_WORD_SORTED_FILE)
    lexicon_freq = {w:1 for w in lex}   
    #solution_lexicon =  lexicon.loadLexiconFromFile(corpora.DIZIONARIO_BASE_SOSTANTIVI_FILE)
    print('Lex size: {}'.format(len(lex)))
    lexicon.printLexFreqToFile(lexicon_freq, LEX_FREQ_FILE)
    print('Computing coverage')
    scorer.computeCoverageOfGameWordLex(lexicon_freq, corpora.GAME_SET_100_FILE, COVERAGE_WORD_GAME100_FILE)
    print('Building association matrix')
    matrix = matrix_dict.Matrix_Dict(lex=lex)
    matrix.add_patterns_from_corpus(corpora.PAISA_RAW_INFO) #solution_lexicon
    matrix.add_patterns_from_corpus(corpora.DE_MAURO_POLIREMATICHE_INFO, weight=DE_MAURO_WEIGHT) #solution_lexicon
    addBigramFromPolirematicheInMatrix(matrix, DE_MAURO_WEIGHT) #solution_lexicon
    matrix.compute_association_scores() # simmetric=False
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
    