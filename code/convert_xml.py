#! /usr/bin/env python3

import xml.etree.ElementTree as ET
from lxml import etree
import pandas as pd

xml_data_tv = open('./ghigliottina_tv.xml').read()
xml_data_board = open('./ghigliottine_board.xml').read()

csv_data_tv_file = './ghigliottina_tv.csv'
csv_data_board_file = './ghigliottine_board.csv'

gioco_tag = 'gioco'

def xml2csv(xml_data, csv_out):
    root = ET.XML(xml_data) # element tree
    data_dict = []
    giochi = root.findall(gioco_tag)    
    for g in giochi:
        data_dict.append({
            'word1': g.find('def1').text, 
            'word2': g.find('def2').text, 
            'word3': g.find('def3').text, 
            'word4': g.find('def4').text, 
            'word5': g.find('def5').text, 
            'solution': g.find('sol').text,
        })
    df = pd.DataFrame.from_dict(data_dict)
    df = df[['word1','word2','word3','word4','word5','solution']]
    df.to_csv(csv_out, index=False)

xml2csv(xml_data_tv, csv_data_tv_file)
xml2csv(xml_data_board, csv_data_board_file)