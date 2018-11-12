# -*- coding: utf-8 -*-

from parameters import UNFOUND_PAIR_SCORE, HIGH_CONFIDENCE_SCORE, GOOD_CONFIDENCE_SCORE, AVERAGE_CONFIDENCE_SCORE
import ui
import logging
from ndb_ghigliottina import NDB_Ghigliottina

def tokenize_clues(text):
    return [x.strip() for x in text.split(',')] if ',' in text else text.split()


def get_solution_from_image(user, clues_list):
    if len(clues_list)==5:
        clues_list_str = ','.join(clues_list)
        reply_text, correct = get_solution(user, clues_list_str)    
        return reply_text, correct        
    else:
        return ui.getImgProblemText(), False
    

def get_solution(user, text):

    text = text.lower()
    from_twitter = user.from_twitter()

    if any(x in text for x in ui.INFO_QUESTIONS_LOWER):
        reply_text = ui.intro(from_twitter)
        return reply_text, True

    clues = tokenize_clues(text)
    
    if len(clues)!=5:
        reply_text = ui.wrong_input(from_twitter, text)
        logging.debug('No 5 clues detected: {}'.format(clues))
        return reply_text, False

    x_table = get_solution_table(clues)
        
    clues_str = ', '.join(clues)
    if len(x_table)==0:
        reply_text = ui.no_solution_found(from_twitter, clues_str)
        NDB_Ghigliottina(user, clues, None)
        return reply_text, True
    
    sorted_x_table_sum = sorted(x_table.items(),key=lambda k:(-k[1]['sum'], k[0]))
    best_solution, scores_table = sorted_x_table_sum[0]
    NDB_Ghigliottina(user, clues, best_solution)
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
        reply_text = '```' + '\n'.join(result) + '\n```'
        return reply_text, True
    else:        
        score_sum = scores_table['sum']
        if score_sum > HIGH_CONFIDENCE_SCORE:
            reply_text = ui.high_confidence_solution(from_twitter, clues_str, best_solution)
        if score_sum > GOOD_CONFIDENCE_SCORE:
            reply_text = ui.good_confidence_solution(from_twitter, clues_str, best_solution)
        if score_sum > AVERAGE_CONFIDENCE_SCORE:
            reply_text = ui.average_confidence_solution(from_twitter, clues_str, best_solution)
        else:
            reply_text = ui.low_confidence_solution(from_twitter, clues_str, best_solution)
        
        logging.debug('Solution detected. Clues: {} Solution: {}'.format(clues, best_solution))        
        return reply_text, True

def get_solution_table(clues):
    from cloud_operations import get_clue_subtable
    
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
            if x not in clues:
                update_x_table(x, i, s)
    return x_table

def get_best_solution(clues):
    clues = [c.lower() for c in clues]
    x_table = get_solution_table(clues)
    sorted_x_table_sum = sorted(x_table.items(),key=lambda k:(-k[1]['sum'], k[0]))
    if len(sorted_x_table_sum)==0:
        return 'casa'
    best_solution, _ = sorted_x_table_sum[0]    
    return best_solution

# if __name__ == "__main__":
#      solution = get_best_solution("giardino lago foresta legge elefante".split())
#      print(solution)