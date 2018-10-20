# -*- coding: utf-8 -*-

from parameters import UNFOUND_PAIR_SCORE, HIGH_CONFIDENCE_SCORE, GOOD_CONFIDENCE_SCORE, AVERAGE_CONFIDENCE_SCORE
import ui

def tokenize_clues(text):
    return [x.strip() for x in text.split(',')] if ',' in text else text.split()

def get_solution_from_image_clues(clues_list, from_twitter):
    if len(clues_list)==5:
        clues_list_str = ','.join(clues_list)
        reply_text, correct = get_solution_from_text(clues_list_str, from_twitter=from_twitter)    
        return reply_text, correct
    else:
        return ui.getImgProblemText(), False

    

def get_solution_from_text(text, from_twitter):

    text = text.lower()

    if any(x in text for x in ui.INFO_QUESTIONS_LOWER):
        reply_text = ui.intro(from_twitter=from_twitter)
        return reply_text, True

    from cloud_operations import get_clue_subtable
    
    clues = tokenize_clues(text)
    
    if len(clues)!=5:
        reply_text = ui.wrong_input(from_twitter, text)
        return reply_text, False

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
            if s not in clues:
                update_x_table(x, i, s)

    sorted_x_table_sum = sorted(x_table.items(),key=lambda k:(-k[1]['sum'], k[0]))
    
    clues_str = ', '.join(clues)
    if len(sorted_x_table_sum)==0:
        reply_text = ui.no_solution_found(from_twitter, clues_str)
        return reply_text, True
    best_solution, scores_table = sorted_x_table_sum[0]
    score_sum = scores_table['sum']
    if score_sum > HIGH_CONFIDENCE_SCORE:
        reply_text = ui.high_confidence_solution(from_twitter, clues_str, best_solution)
    if score_sum > GOOD_CONFIDENCE_SCORE:
        reply_text = ui.good_confidence_solution(from_twitter, clues_str, best_solution)
    if score_sum > AVERAGE_CONFIDENCE_SCORE:
        reply_text = ui.average_confidence_solution(from_twitter, clues_str, best_solution)
    else:
        reply_text = ui.low_confidence_solution(from_twitter, clues_str, best_solution)
    
    return reply_text, True