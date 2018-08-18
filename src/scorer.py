#! /usr/bin/env python3

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
    union, intersection = matrix.get_union_intersection(clues)        
    x_table = {}
    for x in union:
        association_scores = []        
        for w in clues:
            association_scores.append(matrix.get_association_score(x, w))
        association_none_replaced = [unfound_pair_score if x==None else x for x in association_scores]
        x_table[x] = {
            'scores': association_none_replaced,
            'sum': sum(association_none_replaced),
            'clues_matched_info': ['X' if x!=None else '_' for x in association_scores],
            'clues_matched_count': sum([1 for x in association_scores if x!=None])            
        }    
    # k[0] stand for alphabetical order (breaking tie with alphabetical order)
    sorted_x_table_groups = sorted(x_table.items(),key=lambda k:(-k[1]['clues_matched_count'],-k[1]['sum'], k[0]))
    sorted_x_table_sum = sorted(x_table.items(),key=lambda k:(-k[1]['sum'], k[0]))
    if debug:
        for key,value in sorted_x_table_groups[:nBest]:
            print('{}: {} -> sum({}) = {}'.format(key,value['clues_matched_count'], value['scores'], value['sum']))
    else:
        return x_table, sorted_x_table_sum, sorted_x_table_groups

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

def getSolutionRank(matrix, clues, solution, unfound_pair_score):    
    x_table, sorted_x_table_sum, sorted_x_table_groups = computeBestWordAssociation(matrix, clues, unfound_pair_score)    
    sorted_table_sum_keys = [i[0] for i in sorted_x_table_sum]
    sorted_table_groups_keys = [i[0] for i in sorted_x_table_groups]    
    if solution not in sorted_table_sum_keys:
        WORST_RANK_DEFAULT = 9999
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
    print('\n'.join(summary))
    if output_file:
        with open(output_file, 'w') as f_out:
            print_write(f_out, '\n'.join(summary))
            print_write(f_out, '\n\nPosition Details:\n\n')
            print_write(f_out, '\n'.join(eval_details))

def solver(matrix):
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
        if solution not in matrix:
            print('La parola "{}" non presente nel dizionario\n'.format(solution))
            continue
        abs_rank, group_rank, group, rank_in_group, scores, clues_matched_info = getSolutionRank(
            matrix, clues, solution, unfound_pair_score)
        print("\nScores: " + ', '.join(['{0:.1f}'.format(s) for s in scores]))
        print("\nAbs rank:{}\nGroup rank:{}\nGROUP (matched clues):{}\nPosition in group:{}\nClues matched:{}\n".format(
            abs_rank, group_rank, group, rank_in_group, clues_matched_info))