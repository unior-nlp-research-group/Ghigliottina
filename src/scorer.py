#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import matrix_dict
from collections import defaultdict
from utility import print_write

###################
## COVERAGE
###################

def computeCoverageOfGameWordLex(lex_set, lex_solution_set, game_set_file, output_file):
    game_set = read_game_set_tab(game_set_file)
    game_words_lex = set() # clues + solution
    solution_game_words = set() # only solutions
    for game_words in game_set:
        solution_game_words.add(game_words[-1])
        game_words_lex.update(game_words)                        
    game_covered, game_not_covered = set(), set()
    solution_covered, solution_not_covered = set(), set()
    for w in game_words_lex: 
        if w in lex_set:
            game_covered.add(w)
        else:
            game_not_covered.add(w)
    for s in solution_game_words: 
        if s in lex_solution_set:
            solution_covered.add(s)
        else:
            solution_not_covered.add(s)
    with open(output_file, 'w') as f_out:
        ## lex stats
        print_write(f_out, 'Lex size: {}'.format(len(lex_set)))
        print_write(f_out, 'Solution Lex size: {}'.format(len(lex_solution_set)))
        ## solution coverage
        print_write(f_out, '\nSOLUTION WORDS COVERED {}/{}\n-------------'.format(len(solution_covered), len(solution_game_words)))
        f_out.write(', '.join(sorted(solution_covered)))
        print_write(f_out, '\n\nSOLUTION WORDS NOT COVERED {}/{}\n-------------'.format(len(solution_not_covered), len(solution_game_words)))
        print_write(f_out, ', '.join(sorted(solution_not_covered)))
        ## all words coverage
        print_write(f_out, '\n\nALL GAME WORDS COVERAGE {}/{}\n-------------'.format(len(game_covered), len(game_words_lex)))
        f_out.write(', '.join(sorted(game_covered)))
        print_write(f_out, '\n\nALL GAME WORDS NOT COVERED {}/{}\n-------------'.format(len(game_not_covered), len(game_words_lex)))
        print_write(f_out, ', '.join(sorted(game_not_covered)))

###################
## SOLVING
###################

def computeBestWordAssociation(matrix, clues, unfound_pair_score, debug=False, nBest=10):
    if debug:
        print('Input clues: {}'.format(clues))     

    '''
    # variant 2
    x_table = {}

    def update_x_table(x_key, clue_index, x_clue_score, multi_tokens=False, last_multi_tokens=False):
        if x_key in x_table:
            entry = x_table[x_key]
        else:
            entry = x_table[x_key] = {
                'scores': [unfound_pair_score for i in range(5)],
                'multi_token_scores': [[] for i in range(5)],
                'sum': unfound_pair_score * 5,
                'clues_matched_info': ['_' for i in range(5)],
                'clues_matched_count': 0
            }  
        if multi_tokens:
            multi_token_scores = entry['multi_token_scores'][clue_index]
            multi_token_scores.append(x_clue_score)
            if last_multi_tokens:
                entry['clues_matched_count'] += 1
                entry['scores'][clue_index] = avg_x_clue_score = sum(multi_token_scores)/len(multi_token_scores)
                entry['sum'] += avg_x_clue_score - unfound_pair_score
                entry['clues_matched_info'][clue_index] = 'X'
        else:
            entry['clues_matched_count'] += 1
            entry['scores'][clue_index] = x_clue_score
            entry['sum'] += x_clue_score - unfound_pair_score
            entry['clues_matched_info'][clue_index] = 'X'


    matrix.get_solutions_table(clues, update_x_table)        
    # end of variant 2
    '''

    # variant 1
    clues_words = [w for c in clues for w in c.split()]
    union, intersection = matrix.get_union_intersection(clues_words)        
    x_table = {}
    for x in union:
        association_scores = []        
        for c in clues:
            cw = c.split()
            score = sum(matrix.get_association_score(x, w, unfound_pair_score) for w in cw)
            score = score / len(cw)
            association_scores.append(score)
        x_table[x] = {
            'scores': association_scores,
            'sum': sum(association_scores),
            'clues_matched_info': ['X' if x!=unfound_pair_score else '_' for x in association_scores],
            'clues_matched_count': sum([1 for x in association_scores if x!=unfound_pair_score])            
        }    
    # end of variant 1

    # k[0] stand for alphabetical order (breaking tie with alphabetical order)
    sorted_x_table_groups = sorted(x_table.items(),key=lambda k:(-k[1]['clues_matched_count'],-k[1]['sum'], k[0]))
    sorted_x_table_sum = sorted(x_table.items(),key=lambda k:(-k[1]['sum'], k[0]))
    if debug:
        for key,value in sorted_x_table_groups[:nBest]:
            print('{}: {} -> sum({}) = {}'.format(key,value['clues_matched_count'], value['scores'], value['sum']))
    else:
        return x_table, sorted_x_table_sum, sorted_x_table_groups

def getBestWordAssociationGroups(matrix, clues, unfound_pair_score, nBest=10):
    x_table, sorted_x_table_sum, sorted_x_table_groups = computeBestWordAssociation(matrix, clues, unfound_pair_score)
    result = []
    for ranked_solution,value in sorted_x_table_sum[:nBest]:
            scores = ', '.join(['{0:.1f}'.format(s) for s in value['scores']])
            clues_matched_count = value['clues_matched_count']
            scores_sum = '{0:.1f}'.format(value['sum'])
            result.append({
                'ranked_solution': ranked_solution,
                'clues_matched_count': clues_matched_count,
                'scores': scores,
                'scores_sum': scores_sum
            })  
    return result          

def reportBestWordAssociationGroups(matrix, clues, unfound_pair_score, sets=[5,4], nBest=10):
    x_table, sorted_x_table_sum, sorted_x_table_groups = computeBestWordAssociation(matrix, clues, unfound_pair_score)
    print('\n-------------------------------------')
    print('Absolute best in score')
    print('-------------------------------------')
    for key,value in sorted_x_table_sum[:nBest]:
            scores = ', '.join(['{0:.1f}'.format(s) for s in value['scores']])
            scores_sum = '{0:.1f}'.format(value['sum'])
            print('{}: {} -> sum({}) = {}'.format(key,value['clues_matched_count'], scores, scores_sum))
    for s in sets:
        print('\n-------------------------------------')
        print('Best of {}'.format(s))
        print('-------------------------------------')
        sorted_x_table_set = [x for x in sorted_x_table_groups if x[1]['clues_matched_count'] == s]
        for key,value in sorted_x_table_set[:nBest]:
            scores = ', '.join(['{0:.1f}'.format(s) for s in value['scores']])
            scores_sum = '{0:.1f}'.format(value['sum'])
            print('{}: {} -> sum({}) = {}'.format(key,value['clues_matched_count'], scores, scores_sum))

###################
## EVALUATION
###################

def read_game_set_tab(game_set_file):
    game_set = []
    with open(game_set_file, 'r') as f_in:
        for line in f_in:
            tokens = [x.strip() for x in line.lower().split('\t')]
            if len(tokens)!=6:
                continue
            game_set.append(tokens)
    return game_set

WORST_RANK_DEFAULT = -1

def getSolutionRank(matrix, clues, solution, unfound_pair_score):    
    x_table, sorted_x_table_sum, sorted_x_table_groups = computeBestWordAssociation(matrix, clues, unfound_pair_score)    
    sorted_table_sum_keys = [i[0] for i in sorted_x_table_sum]
    sorted_table_groups_keys = [i[0] for i in sorted_x_table_groups]    
    if solution not in sorted_table_sum_keys:        
        return WORST_RANK_DEFAULT, WORST_RANK_DEFAULT, 0, WORST_RANK_DEFAULT, [unfound_pair_score]*5, ['_']*5
    abs_rank = sorted_table_sum_keys.index(solution)+1
    group_rank = sorted_table_groups_keys.index(solution)+1
    sorted_x_table_matched = {}    
    for s in [5,4,3,2,1,0]:
        sorted_x_table_matched[s] = [x[0] for x in sorted_x_table_groups if x[1]['clues_matched_count'] == s ]
    group = x_table[solution]['clues_matched_count']
    scores = x_table[solution]['scores']
    clues_matched_info = x_table[solution]['clues_matched_info']
    rank_in_group = sorted_x_table_matched[group].index(solution)+1
    return abs_rank, group_rank, group, rank_in_group, scores, clues_matched_info

def evaluate_kbest_MeanReciprocalRank(matrix, game_set_file, output_file):  
    unfound_pair_score = matrix.get_min_association_score()
    print("Min association score: {0:.1f}".format(unfound_pair_score)) 
    game_set = read_game_set_tab(game_set_file)
    kbest_list = [1,10,25,50,75,100]
    kbest_dict_abs_rank, kbest_dict_group_rank = defaultdict(int), defaultdict(int)
    eval_details = []
    MRR_score_abs_rank, MRR_score_group_rank = 0, 0
    for game_words in game_set:
        clues = game_words[:5]
        solution = game_words[5]
        abs_rank, group_rank, group, rank_in_group, scores, clues_matched_info = getSolutionRank(
            matrix, clues, solution, unfound_pair_score)
        spaced_clues_matched_info = ' '.join(clues_matched_info)
        spaced_scores = ' '.join(['{0:.1f}'.format(x) for x in scores])
        score_sum_str = '{0:.1f}'.format(sum(scores))
        report_fields = clues + [solution, abs_rank, group_rank, group, rank_in_group, spaced_clues_matched_info, spaced_scores, score_sum_str]
        eval_report = '\t'.join([str(x) for x in report_fields])
        #print(eval_report)
        eval_details.append(eval_report)
        if abs_rank<=100:
            MRR_score_abs_rank += 1./abs_rank
        if group_rank<=100:
            MRR_score_group_rank += 1./group_rank
        for t in kbest_list:
            if abs_rank<=t:
                kbest_dict_abs_rank[t] += 1
            if group_rank<=t:
                kbest_dict_group_rank[t] += 1
    total = len(game_set) 
    kbest_scores_abs_rank = sorted(kbest_dict_abs_rank.items())
    kbest_scores_group_rank = sorted(kbest_dict_group_rank.items())        
    summary = [
        'total games: {}'.format(total),
        '\nk-best scores abs rank:',
        '\t'.join([str(k) for k,score in kbest_scores_abs_rank]),
        '\t'.join([str(score) for k,score in kbest_scores_abs_rank]),
        '\nMean Reciprocal Rank score abs rank: {0:.1f}'.format(MRR_score_abs_rank),
        '\nk-best scores group rank:',
        '\t'.join([str(k) for k,score in kbest_scores_group_rank]),
        '\t'.join([str(score) for k,score in kbest_scores_group_rank]),        
        '\nMean Reciprocal Rank score group rank: {0:.1f}'.format(MRR_score_group_rank),

    ]
    if output_file:
        with open(output_file, 'w') as f_out:
            print_write(f_out, '\n'.join(summary))
            print_write(f_out, '\n\nPosition Details:\n\n')
            print_write(f_out, '\n'.join(eval_details))
    else:
        print('\n'.join(summary))

def batch_solver(matrix, game_set_file, output_file, nBest=100, extra_search=False):
    import time
    import corpora
    import lexicon
    from lexicon import morph_normalize_word
    unfound_pair_score = matrix.get_min_association_score()
    lex_freq_dict = lexicon.loadLexFreqFromFile(corpora.PAISA_LEX_FREQ_FILE)
    #most_freq_words = [item[0] for item in sorted(lex_freq_dict.items(), key=lambda x: -x[1])]
    nouns_lex_freq_dict = lexicon.loadLexFreqFromFile(corpora.PAISA_SOSTANTIVI_FREQ_FILE)
    most_freq_nouns = [item[0] for item in sorted(nouns_lex_freq_dict.items(), key=lambda x: -x[1])]
    game_set = read_game_set_tab(game_set_file)
    output_lines_clues_matched = []
    for game_words in game_set:
        start_time = time.time()
        clues = game_words[:5]
        result = getBestWordAssociationGroups(matrix, clues, unfound_pair_score, nBest)
        if extra_search and len(result)<100:      
            morphed_clues = [morph_normalize_word(c,lex_freq_dict) for c in clues]  
            if morphed_clues != clues:  
                result += getBestWordAssociationGroups(matrix, morphed_clues, unfound_pair_score, nBest)
                # resorting results (omitting if we want to give more relevance to unmorphed clues)
                # result = sorted(result, key=lambda r: r['scores_sum'])
        if len(result)==0:            
            best_solution = most_freq_nouns[0]
            clues_matched_count = 0
            scores = -9999
            scores_sum = -9999
            remaining_solutions = most_freq_nouns[1:nBest]
        else:    
            best_result = result[0]            
            other_results = result[1:]
            best_solution = best_result['ranked_solution']
            clues_matched_count = best_result['clues_matched_count']
            scores = best_result['scores']
            scores_sum = best_result['scores_sum']
            remaining_solutions = [r['ranked_solution'] for r in other_results]
            if len(remaining_solutions)<(nBest-1):
                missing_count = nBest - 1 - len(remaining_solutions)
                missing_nouns = [n for n in most_freq_nouns if n!=best_solution and n not in other_results][:missing_count]
                remaining_solutions += missing_nouns
        remaining_solutions_str = ', '.join(remaining_solutions)
        elapsed_time = int(round(time.time() - start_time) * 1000)
        report_fields = clues + [best_solution, clues_matched_count, scores, scores_sum, remaining_solutions_str, elapsed_time]            
        output_lines_clues_matched.append('\t'.join([str(x) for x in report_fields]))
    print('Input lines: {}'.format(len(game_set)))
    print('Output lines: {}'.format(len(output_lines_clues_matched)))
    with open(output_file, 'w') as f_out:
        print_write(f_out, '\n'.join(output_lines_clues_matched))        

def compute_correlation_score_match(matrix, game_set_file, output_file_clues_matched, output_file_solutions_matched):
    import corpora
    import lexicon
    unfound_pair_score = matrix.get_min_association_score()
    lex_freq_dict = lexicon.loadLexFreqFromFile(corpora.PAISA_LEX_FREQ_FILE)
    nouns_lex_freq_dict = lexicon.loadLexFreqFromFile(corpora.PAISA_SOSTANTIVI_FREQ_FILE)
    most_freq_nouns = [item[0] for item in sorted(nouns_lex_freq_dict.items(), key=lambda x: -x[1])]
    game_set = read_game_set_tab(game_set_file)
    output_lines_clues_matched = []    
    output_lines_clues_matched.append('\t'.join(['Scores', 'Matched']))
    scores_guessed = []
    scores_missed = []
    for game_words in game_set:
        clues = game_words[:5]
        gold_solution = game_words[5]
        result = getBestWordAssociationGroups(matrix, clues, unfound_pair_score, nBest=100)
        if len(result)==0:            
            best_solution = most_freq_nouns[0]
            clues_matched_count = 0
            scores_sum = unfound_pair_score * 5
        else:    
            best_result = result[0]            
            best_solution = best_result['ranked_solution']
            clues_matched_count = best_result['clues_matched_count']
            scores = best_result['scores']
            scores_sum = best_result['scores_sum']
        if best_solution == gold_solution:
            scores_guessed.append(scores_sum)
        else:
            scores_missed.append(scores_sum)        
        output_lines_clues_matched.append('{}\t{}'.format(scores_sum, clues_matched_count))
    with open(output_file_clues_matched, 'w') as f_out:
        print_write(f_out, '\n'.join(output_lines_clues_matched))  
    with open(output_file_solutions_matched, 'w') as f_out:
        print_write(f_out, '\t'.join(['Scores Guessed', 'Scores Missed']) + '\n')
        max_lines = max(len(scores_guessed),len(scores_missed))
        for i in range(max_lines):
            if i < len(scores_guessed):
                print_write(f_out, str(scores_guessed[i]))
            if i < len(scores_missed):
                print_write(f_out, '\t' + str(scores_missed[i]))
            print_write(f_out, '\n')

def interactive_solver(matrix):
    unfound_pair_score = matrix.get_min_association_score()
    print("Min association score: {0:.1f}".format(unfound_pair_score)) 
    while True:
        text = input('\nInserisci le 5 parole divise da virgole/tab o premi invio per uscire\n--> ')
        text = text.strip().lower()
        if not text:
            print('exitig')
            return
        sep = ',' if ',' in text else '\t'
        clues = [w.strip() for w in text.split(sep)]
        if len(clues)!=5:
            print('Hai inserito {} parole, riprova.\n'.format(len(clues)))
            continue            
        reportBestWordAssociationGroups(matrix, clues, unfound_pair_score, sets=[5,4,3], nBest=5)
        solution = input('\nInserisci la parola corretta o premi invio per testare nuove parole\n--> ')
        solution = solution.strip().lower()
        if not solution:
            continue        
        abs_rank, group_rank, group, rank_in_group, scores, clues_matched_info = getSolutionRank(
            matrix, clues, solution, unfound_pair_score)
        if abs_rank == WORST_RANK_DEFAULT:
            print('La parola "{}" non è presente tra le migliori soluzioni\n'.format(solution))
            continue
        print("\nScores: " + ', '.join(['{0:.1f}'.format(s) for s in scores]))
        print("\nAbs rank:{}\nGroup rank:{}\nGROUP (matched clues):{}\nPosition in group:{}\nClues matched:{}\n".format(
            abs_rank, group_rank, group, rank_in_group, clues_matched_info))