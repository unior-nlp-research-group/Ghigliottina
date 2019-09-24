# -*- coding: utf-8 -*-

from parameters import DEFAULT_SOLUTION, UNFOUND_PAIR_SCORE, HIGH_CONFIDENCE_SCORE, GOOD_CONFIDENCE_SCORE, AVERAGE_CONFIDENCE_SCORE
import response_formatter
import logging
from ndb_ghigliottina import NDB_Ghigliottina

def tokenize_clues(text):
    return [x.strip() for x in text.split(',')] if ',' in text else text.split()


def get_solution_from_image(user, clues_list):
    if len(clues_list)==5:
        clues_list_str = ','.join(clues_list)
        reply_text, correct = get_solution_from_text(user, clues_list_str)    
        return reply_text, correct        
    else:
        return response_formatter.getImgProblemText(), False
    

def get_solution_from_text(user, text):
    text = text.lower()
    from_twitter = user.from_twitter()

    if any(x in text for x in response_formatter.INFO_QUESTIONS_LOWER):
        reply_text = response_formatter.intro(from_twitter)
        return reply_text, True

    clues = tokenize_clues(text)
    
    if len(clues)!=5:
        reply_text = response_formatter.wrong_input(from_twitter, text)
        logging.debug('No 5 clues detected: {}'.format(clues))
        return reply_text, False

    _, reply_text, success = get_solution_from_clues(user, clues)
    return reply_text, success


def get_solution_from_clues(user, clues):
    from ndb_ghigliottina import get_past_solution_score
    clues = [c.lower() for c in clues]
    clues_str = ', '.join(clues)
    from_twitter = user.from_twitter()
    best_solution, best_score = get_past_solution_score(clues)
    if not user.debug and best_solution:
        reply_text = get_reply_based_on_score(from_twitter, clues_str, best_solution, best_score)
        logging.debug('Old solution detected. Clues: {} Solution: {}'.format(clues, best_solution))        
    else:
        x_table = compute_solution_table(clues)                
        if len(x_table)==0:
            reply_text = response_formatter.no_solution_found(from_twitter, clues_str, DEFAULT_SOLUTION)
            best_solution = DEFAULT_SOLUTION
            best_score = UNFOUND_PAIR_SCORE
        else:    
            sorted_x_table_sum = sorted(x_table.items(),key=lambda k:(-k[1]['sum'], k[0]))
            best_solution, scores_table = sorted_x_table_sum[0]
            best_score = scores_table['sum']
            if user.debug:
                result = []                
                for s in [5,4,3]:                    
                    result.append('\n-------------------------------------')
                    result.append('Best of {}'.format(s))
                    result.append('-------------------------------------')
                    sorted_x_table_set = [x for x in sorted_x_table_sum if x[1]['clues_matched_count'] == s]
                    for key,value in sorted_x_table_set[:5]:
                        scores = ', '.join(['{0:.1f}'.format(s) for s in value['scores']])
                        scores_sum = '{0:.1f}'.format(value['sum'])
                        result.append('{}: {} -> sum({}) = {}'.format(key,value['clues_matched_count'], scores, scores_sum))
                result.append('\nBest solution: {}'.format(best_solution))
                reply_text = '```' + '\n'.join(result) + '\n```'
            else:                
                reply_text = get_reply_based_on_score(from_twitter, clues_str, best_solution, best_score)
        logging.debug('New solution computed. Clues: {} Solution: {}'.format(clues, best_solution))        
    NDB_Ghigliottina(user, clues, best_solution, best_score)
    return best_solution, reply_text, True

def get_reply_based_on_score(from_twitter, clues_str, best_solution, best_score):
    if best_score > HIGH_CONFIDENCE_SCORE:
        return response_formatter.high_confidence_solution(from_twitter, clues_str, best_solution)
    if best_score > GOOD_CONFIDENCE_SCORE:
        return response_formatter.good_confidence_solution(from_twitter, clues_str, best_solution)
    if best_score > AVERAGE_CONFIDENCE_SCORE:
        return response_formatter.average_confidence_solution(from_twitter, clues_str, best_solution)
    return response_formatter.low_confidence_solution(from_twitter, clues_str, best_solution)  


def compute_solution_table(clues, exclude_blacklist_words = True):
    from cloud_operations import get_clue_subtable
    
    blacklist_words = []
    if exclude_blacklist_words:
        from it_blacklist import blacklist_words
    
    x_table = {}
    
    def update_x_table(x_key, clue_index, x_clue_score):
        if x_key in x_table:
            entry = x_table[x_key]
        else:
            x_table[x_key] = entry = {
                'scores': [UNFOUND_PAIR_SCORE] * 5,
                'sum': UNFOUND_PAIR_SCORE * 5,
                'clues_matched_info': ['_'] * 5,
                'clues_matched_count': 0
            }      
        entry['scores'][clue_index] = x_clue_score
        entry['sum'] += x_clue_score - UNFOUND_PAIR_SCORE
        entry['clues_matched_info'][clue_index] = 'X'
        entry['clues_matched_count'] += 1

    for i,c in enumerate(clues):
        clue_subtable = get_clue_subtable(c)
        if clue_subtable is None:
            continue
        for x,s in clue_subtable.items():
            if x in blacklist_words:
                continue
            if x not in clues:
                update_x_table(x, i, s)
    return x_table

# if __name__ == "__main__":
#      solution = get_best_solution_score("giardino lago foresta legge elefante".split())
#      print(solution)