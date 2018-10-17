#! /usr/bin/env python3
# -*- coding: utf-8 -*-

#import xml.etree.ElementTree as ET
#from lxml import etree

import corpora
import pandas as pd

def xml2csv_old(xml_data, csv_out, gioco_tag = 'gioco', clu_tag_prefix = 'def', solution_tag = 'sol'):    
    root = ET.XML(xml_data) # element tree
    data_dict = []
    giochi = root.findall(gioco_tag)    
    for g in giochi:
        data_dict.append({
            'clue1': g.find('{}1'.format(clu_tag_prefix)).text, 
            'clue2': g.find('{}2'.format(clu_tag_prefix)).text, 
            'clue3': g.find('{}3'.format(clu_tag_prefix)).text, 
            'clue4': g.find('{}4'.format(clu_tag_prefix)).text, 
            'clue5': g.find('{}5'.format(clu_tag_prefix)).text, 
            'solution': g.find(solution_tag).text,
        })
    df = pd.DataFrame.from_dict(data_dict)
    df = df[['clue1','clue2','clue3','clue4','clue5','solution']]
    df.to_csv(csv_out, index=False)

def old_convert():
    xml_data_tv = open('./ghigliottina_tv.xml').read()
    xml_data_board = open('./ghigliottine_board.xml').read()
    csv_data_tv_file = './ghigliottina_tv.csv'
    csv_data_board_file = './ghigliottine_board.csv'
    xml2csv_old(xml_data_tv, csv_data_tv_file)
    xml2csv_old(xml_data_board, csv_data_board_file)

def convertDataSetXmlToTsv_manual(file_in_xml, file_out_bg_csv, file_out_tv_csv, file_out_all_csv): 
    games = {
        'TV': [],
        'boardgame': [],
        'ALL': []
    }
    current_game = []
    clue_tag_open, clue_tag_close = '<clue>', '</clue>'
    solution_tag_open, solution_tag_close = '<solution>', '</solution>'
    type_tag_open, type_tag_close = '<type>', '</type>'
    with open(file_in_xml) as f_in:
        for line in f_in:
            if clue_tag_open in line:
                line = line.replace(clue_tag_close, clue_tag_open)
                clue = line.split(clue_tag_open)[1]
                current_game.append(clue)
            elif solution_tag_open in line:
                line = line.replace(solution_tag_close, solution_tag_open)
                solution = line.split(solution_tag_open)[1]
                current_game.append(solution)
            elif type_tag_open in line:
                line = line.replace(type_tag_close, type_tag_open)
                type = line.split(type_tag_open)[1]
                games[type].append(current_game)
                games['ALL'].append(current_game)
                current_game = []

    with open(file_out_tv_csv, 'w') as f_out:
        for g in games['TV']:
            f_out.write('\t'.join(g) + '\n')
    with open(file_out_bg_csv, 'w') as f_out:
        for g in games['boardgame']:
            f_out.write('\t'.join(g) + '\n')
    with open(file_out_all_csv, 'w') as f_out:
        for g in games['ALL']:
            f_out.write('\t'.join(g) + '\n')


def convert_dev_xml_to_csv_manual():
    file_in_xml = corpora.NLP4FUN_DEV_XML_v2_FILE
    file_out_bg_csv = corpora.NLP4FUN_DEV_TSV_v2_bg_FILE
    file_out_tv_csv = corpora.NLP4FUN_DEV_TSV_v2_tv_FILE
    file_out_all_csv = corpora.NLP4FUN_DEV_TSV_v2_ALL_FILE
    convertDataSetXmlToTsv(file_in_xml, file_out_bg_csv, file_out_tv_csv, file_out_all_csv)

def xml2csv(file_in_xml, file_out_bg_csv, file_out_tv_csv, file_out_all_csv):
    import xml.etree.ElementTree as etree
    gioco_tag = 'game'
    clu_tag = 'clue'
    solution_tag = 'solution'
    type_tag = 'type'    
    root = etree.parse(file_in_xml,etree.XMLParser(encoding='utf-8')) # element tree
    data_dict = {
        'boardgame': {
            'entries': [],
            'file_output': file_out_bg_csv
        },
        'tv': {
            'entries': [],
            'file_output': file_out_tv_csv
        },
        'all': {
            'entries': [],
            'file_output': file_out_all_csv
        }
    }
    data_dict_bg = []
    data_dict_tv = []
    data_dict_all = []
    giochi = root.findall(gioco_tag)    
    for g in giochi:
        type = g.find(type_tag).text.lower()
        clues = [c.text for c in g.findall(clu_tag)]
        if len(set(clues)) != 5:
            print("Duplicates in {}".format(clues))
        new_entry = {
            'solution': g.find(solution_tag).text
        }
        data_dict[type]['entries'].append(new_entry)
        data_dict['all']['entries'].append(new_entry)
        for n,c in enumerate(clues,1):
            new_entry['clue{}'.format(n)] = c
    for entries_fileout in data_dict.values():
        df = pd.DataFrame.from_dict(entries_fileout['entries'])
        df = df[['clue1','clue2','clue3','clue4','clue5','solution']]
        df.to_csv(entries_fileout['file_output'], index=False, sep='\t', header=False)

def convert_dev_xml_to_csv_et():
    file_in_xml = corpora.NLP4FUN_DEV_XML_v2_FILE
    file_out_bg_csv = corpora.NLP4FUN_DEV_TSV_v2_bg_FILE
    file_out_tv_csv = corpora.NLP4FUN_DEV_TSV_v2_tv_FILE
    file_out_all_csv = corpora.NLP4FUN_DEV_TSV_v2_ALL_FILE
    xml2csv(file_in_xml, file_out_bg_csv, file_out_tv_csv, file_out_all_csv)

def convert_test_xml_to_csv_et():
    file_in_xml = corpora.NLP4FUN_TEST_XML_v2_FILE
    file_out_bg_csv = corpora.NLP4FUN_TEST_TSV_v2_bg_FILE
    file_out_tv_csv = corpora.NLP4FUN_TEST_TSV_v2_tv_FILE
    file_out_all_csv = corpora.NLP4FUN_TEST_TSV_v2_ALL_FILE
    xml2csv(file_in_xml, file_out_bg_csv, file_out_tv_csv, file_out_all_csv)

def convert_gold_xml_to_csv_et():
    file_in_xml = corpora.NLP4FUN_GOLD_XML_v2_FILE
    file_out_bg_csv = corpora.NLP4FUN_GOLD_TSV_v2_bg_FILE
    file_out_tv_csv = corpora.NLP4FUN_GOLD_TSV_v2_tv_FILE
    file_out_all_csv = corpora.NLP4FUN_GOLD_TSV_v2_ALL_FILE
    xml2csv(file_in_xml, file_out_bg_csv, file_out_tv_csv, file_out_all_csv)


def output_results(file_in_xml, file_in_csv, file_out):
    import xml.etree.ElementTree as etree
    import model_05_all_corpora_small_lex as model05
    import csv
    
    #file_in_csv = model05.TEST_RESULTS_CSV
    #file_out = model05.TEST_RESULTS_SUBMIT
    result_entries = []
    tsvin = csv.reader(open(file_in_csv, 'r'), delimiter='\t')    
    for row in tsvin:
        result_entries.append({
            'sorted_clues': sorted(row[:5]),
            'solutions': [row[5]] + (row[9].split(', ') if len(row)>9 and row[9] else []),
            'time': row[10]
        })

    #file_in_xml = corpora.NLP4FUN_TEST_XML_v2_FILE    
    root = etree.parse(file_in_xml,etree.XMLParser(encoding='utf-8')) # element tree
    giochi = root.findall('game')    
    output_lines = []
    for g in giochi:
        id = g.find('id').text
        sorted_clues = sorted([c.text for c in g.findall('clue')])
        result_entry = next(e for e in result_entries if e['sorted_clues']==sorted_clues)
        solutions = result_entry['solutions']
        time =  result_entry['time']
        for rank,solution in enumerate(solutions,1):
            score = 1. - rank * 0.005            
            output_lines.append(' '.join([id, solution, str(score), str(rank), str(time)])) # id solution score rank time

    with open(file_out, 'w') as fout:
        fout.write('\n'.join(output_lines))

    
        

if __name__=='__main__':      
    #convert_test_xml_to_csv_et()
    #output_results()
    convert_gold_xml_to_csv_et()
    

    