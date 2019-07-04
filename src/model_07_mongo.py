import sys
import corpora
import utility
import path
import patterns_extraction

import lexicon
import scorer
import os

######################################
## MODEL 07 DB
######################################

OUTPUT_DIR = path.GHIGLIOTTINA_BASE_FILE_PATH + "model_07_db/"

LEX_FREQ_FILE = OUTPUT_DIR + "lex_freq.txt"
SOLUTION_LEX_FREQ_FILE = OUTPUT_DIR + "lex_freq_solution.txt"
LEX_INDEX_FILE = OUTPUT_DIR + "lex_index.pkl"

MATRIX_FILE = OUTPUT_DIR + "matrix.pkl" # clues in keys
MATRIX_REVERSED_FILE = OUTPUT_DIR + 'matrix_reversed.pkl' #solution in keys

MATRIX_FILE_SPLIT_DIR = os.path.join(OUTPUT_DIR, 'matrix_split')
COVERAGE_WORD_GAME100_FILE = OUTPUT_DIR + "game_word_100_coverage.txt"

EVAL_WORD_GAME100_FILE = OUTPUT_DIR + "game_word_100_eval.txt"

EVAL_NLP4FUN_DEV_ALL_FILE = OUTPUT_DIR + "game_word_NP4FUN_DEV_ALL_eval.txt"
EVAL_NLP4FUN_DEV_TV_FILE = OUTPUT_DIR + "game_word_NP4FUN_DEV_TV_eval.txt"
EVAL_NLP4FUN_DEV_BG_FILE = OUTPUT_DIR + "game_word_NP4FUN_DEV_BG_eval.txt"

EVAL_NLP4FUN_TEST_TV_FILE = OUTPUT_DIR + "game_word_NP4FUN_TEST_TV_eval.txt"
EVAL_NLP4FUN_TEST_BG_FILE = OUTPUT_DIR + "game_word_NP4FUN_TEST_BG_eval.txt"
EVAL_NLP4FUN_TEST_ALL_FILE = OUTPUT_DIR + "game_word_NP4FUN_TEST_ALL_eval.txt"
EVAL_NLP4FUN_GOLD_TEST_ALL_FILE = OUTPUT_DIR + "game_word_NP4FUN_GOLD+TEST_ALL_eval.txt"

TEST_RESULTS_TSV_1 = OUTPUT_DIR + 'NLP4FUN_TEST_v2_ALL_results_1.tsv'
TEST_RESULTS_TSV_2 = OUTPUT_DIR + 'NLP4FUN_TEST_v2_ALL_results_2.tsv'
TEST_RESULTS_SUBMIT_1 = OUTPUT_DIR + 'nlp4fun2018.orientale.run1'
TEST_RESULTS_SUBMIT_2 = OUTPUT_DIR + 'nlp4fun2018.orientale.run2'

DE_MAURO_WEIGHT = 200
PROVERBI_WEIGHT = 100
WIKI_IT_WEIGHT = 50
COMPOUNDS_WEIGHT = 50

LOWEST_SCORE = -8.254895446396917
#LOWEST_SCORE = -8.69121046025845


def build():
    utility.make_dir(OUTPUT_DIR)

    print('Building lexicon')

    poli_lexicon = list(lexicon.loadLexiconFromFile(corpora.DIZ_POLI_WORD_SORTED_FILE))
    sost_lexicon = list(lexicon.loadLexiconFromFile(corpora.DIZIONARIO_SOSTANTIVI_AUGMENTED_PAISA_FILE))
    agg_lexicon = list(lexicon.loadLexiconFromFile(corpora.DIZIONARIO_AGGETTIVI_AUGMENTED_PAISA_FILE))
    lex_set = set(poli_lexicon+sost_lexicon+agg_lexicon)
    lex_solution_set =  set(sost_lexicon+agg_lexicon)

    lexicon.printLexiconToFile(lex_set, LEX_FREQ_FILE)
    lexicon.printLexiconToFile(lex_solution_set, SOLUTION_LEX_FREQ_FILE)

    def add_patterns_from_corpus(corpus_info):
        lines_extractor = corpora.extract_lines(corpus_info)
        source = corpus_info['name']
        patterns_count = 0
        print("Adding patterns from source: {}".format(source))
        tot_lines = corpus_info['lines']
        for n,line in enumerate(lines_extractor,1):            
            patterns_count += patterns_extraction.addPatternsFromLineInMongo(line, lex_set, source)    
            if n%1000==0:
                sys.stdout.write("Progress: {0:.1f}%\r".format(float(n)*100/tot_lines))
                sys.stdout.flush()
        print('Extracted patterns: {}'.format(patterns_count))


    # print('Computing lex coverage')
    # scorer.computeCoverageOfGameWordLex(lex_set, lex_solution_set, corpora.GAME_SET_100_FILE, COVERAGE_WORD_GAME100_FILE)
    
    print('Adding patterns in db')
    # add_patterns_from_corpus(corpora.DE_MAURO_POLIREMATICHE_INFO)
    # add_patterns_from_corpus(corpora.PAISA_RAW_INFO)    
    # add_patterns_from_corpus(corpora.PROVERBI_INFO)    
    add_patterns_from_corpus(corpora.ITWAC_RAW_INFO)
    # add_patterns_from_corpus(corpora.WIKI_IT_TITLES_INFO)        
    # # add_patterns_from_corpus(corpora.WIKI_IT_TEXT_INFO, weight=1)        
    # corpora.addBigramFromPolirematicheInMatrix(matrix)    
    # corpora.addBigramFromCompunds(matrix, lex_set, min_len=4)


def build_and_eval():
    build()    
    
    print('Eval')
    scorer.evaluate_kbest_MeanReciprocalRank(matrix, corpora.GAME_SET_100_FILE, EVAL_WORD_GAME100_FILE) 

def eval():
    from convert_xml import output_results
    print('Loading association matrix')
    matrix = Matrix_Split(MATRIX_FILE_SPLIT_DIR, LOWEST_SCORE)    
    #matrix = Matrix_Dict()
    #matrix.read_matrix_from_file(MATRIX_FILE)
    #matrix.read_matrix_from_file(MATRIX_REVERSED_FILE)
    #print('Number of rows: {}'.format(matrix.size()))
    print('Evaluating')
    
    
    # 100 GAMES    
    #scorer.evaluate_kbest_MeanReciprocalRank(matrix, corpora.GAME_SET_100_FILE, EVAL_WORD_GAME100_FILE)        
    
    
    # DEV SET    
    #scorer.evaluate_kbest_MeanReciprocalRank(matrix, corpora.NLP4FUN_DEV_TSV_v2_ALL_FILE, EVAL_NLP4FUN_DEV_ALL_FILE)
    # scorer.evaluate_kbest_MeanReciprocalRank(matrix, corpora.NLP4FUN_DEV_TSV_v2_tv_FILE, EVAL_NLP4FUN_DEV_TV_FILE)
    # scorer.evaluate_kbest_MeanReciprocalRank(matrix, corpora.NLP4FUN_DEV_TSV_v2_bg_FILE, EVAL_NLP4FUN_DEV_BG_FILE)


    '''
    # GOLD SET (BLIND)
    scorer.batch_solver(matrix, corpora.NLP4FUN_TEST_TSV_v2_ALL_FILE, TEST_RESULTS_TSV_1, extra_search=False)
    scorer.batch_solver(matrix, corpora.NLP4FUN_TEST_TSV_v2_ALL_FILE, TEST_RESULTS_TSV_2, extra_search=True)
    output_results(corpora.NLP4FUN_TEST_XML_v2_FILE, TEST_RESULTS_TSV_1, TEST_RESULTS_SUBMIT_1)
    output_results(corpora.NLP4FUN_TEST_XML_v2_FILE, TEST_RESULTS_TSV_2, TEST_RESULTS_SUBMIT_2)
    '''

    # GOLD SET
    #scorer.evaluate_kbest_MeanReciprocalRank(matrix, corpora.NLP4FUN_GOLD_TSV_v2_tv_FILE, EVAL_NLP4FUN_TEST_TV_FILE)
    #scorer.evaluate_kbest_MeanReciprocalRank(matrix, corpora.NLP4FUN_GOLD_TSV_v2_bg_FILE, EVAL_NLP4FUN_TEST_BG_FILE)
    scorer.evaluate_kbest_MeanReciprocalRank(matrix, corpora.NLP4FUN_GOLD_TSV_v2_ALL_FILE, EVAL_NLP4FUN_TEST_ALL_FILE)

    # DEV + GOLD
    #scorer.evaluate_kbest_MeanReciprocalRank(matrix, corpora.NLP4FUN_DEV_GOLD_TSV_ALL_FILE, EVAL_NLP4FUN_GOLD_TEST_ALL_FILE)

def correlation_score_match():
    from convert_xml import output_results
    print('Loading association matrix')
    matrix = Matrix_Dict()
    matrix.read_matrix_from_file(MATRIX_FILE)
    print('Computing Correlation')
    input_file = corpora.NLP4FUN_DEV_GOLD_TSV_ALL_FILE
    output_file_clues_matched = OUTPUT_DIR + 'nlp4fun_dev+test_all_scores_clues_matched.txt'
    output_file_solutions_matched = OUTPUT_DIR + 'nlp4fun_dev+test_all_scores_solutions_guessed.txt'
    scorer.compute_correlation_score_match(matrix, input_file, output_file_clues_matched, output_file_solutions_matched)    


def interactive_solver():
    print('Loading association matrix')
    #matrix = Matrix_Dict()
    #matrix.read_matrix_from_file(MATRIX_FILE)
    matrix = Matrix_Split(MATRIX_FILE_SPLIT_DIR, LOWEST_SCORE)    
    scorer.interactive_solver(matrix)

def get_pair_score(w1, w2):
    matrix = Matrix_Split(MATRIX_FILE_SPLIT_DIR, LOWEST_SCORE)    
    return matrix.get_association_score(w1, w2, LOWEST_SCORE)

def split_matrix():
    print('Loading association matrix')
    matrix = Matrix_Dict()
    matrix.read_matrix_from_file(MATRIX_FILE)
    print('Lowest score: {}'.format(matrix.get_min_association_score()))
    print('Splitting matrix in {} files in {}'.format(matrix.size(), MATRIX_FILE_SPLIT_DIR))
    matrix.split_matrix_dict(MATRIX_FILE_SPLIT_DIR)

def print_row_column_sets():
    print('Loading association matrix')
    row_file = OUTPUT_DIR + 'set_row.txt'
    col_file = OUTPUT_DIR + 'set_col.txt'
    matrix = Matrix_Dict()
    matrix.read_matrix_from_file(MATRIX_FILE)
    matrix.print_row_column_sets(row_file, col_file)    

def reverse_matrix():    
    matrix = Matrix_Dict()
    matrix.read_matrix_from_file(MATRIX_FILE)
    reversed_matrix = matrix.reverse_matrix()
    reversed_matrix.write_matrix_to_file(MATRIX_REVERSED_FILE)

def generate_games():
    import game_generator
    matrix = Matrix_Dict()
    matrix.read_matrix_from_file(MATRIX_REVERSED_FILE)
    print('Number of rows: {}'.format(matrix.size()))
    game_generator.interactive_generator(matrix)

if __name__=='__main__':  
    build()
    #build_and_eval()
    #interactive_solver()
    #correlation_score_match()
    # eval()
    #split_matrix()  
    #print_row_column_sets()
    #reverse_matrix()
    