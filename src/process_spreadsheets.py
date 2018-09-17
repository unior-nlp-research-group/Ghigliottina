#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import csv

GHIGLIOTTINA_DOC_KEY = '1olr-NfRjtQ_vhrtRYS6kh5x_g8d9s3qXBQ0ciAEZ-Z4'
GHIGLIOTTINA_SHEET_URL = "https://docs.google.com/spreadsheets/d/{}/export?format=tsv&gid={}"
GHIGLIOTTINA_SHEET_GID_TABLE = {
    'INFO': '0',
    'BASILE_2016_TV_SET': '494668510',
    'BASILE_2016_BOARD_SET': '927040573',
    'RAI_2018': '1289709868',
    'RAI_2017': '1889368170',
    'RAI_2016': '1270669164',
    'RAI_2015': '1534060035',
    'RAI_2014': '1002039183',
    'RAI_2013': '880814115',
    'RAI_2012': '476345841',
    'RAI_2011': '459917343',
    'RAI_2010': '1155303607',
    'nokioteca': '1060593787'
}

DIACRITICS = 'àèìòùÀÈÌÒÙáéíóúýÁÉÍÓÚÝâêîôûÂÊÎÔÛãñõÃÑÕäëïöüÿÄËÏÖÜŸçÇßØøÅåÆæœ'

url = GHIGLIOTTINA_SHEET_URL.format(GHIGLIOTTINA_DOC_KEY, GHIGLIOTTINA_SHEET_GID_TABLE['RAI_2010'])
print('Reading url: {}'.format(url))
r = requests.get(url)
r.encoding = 'utf-8'
print('Encoding: {}'.format(r.encoding))
spreadsheet_text = r.text
spreadsheet_rows = spreadsheet_text.split('\n')
spreadSheetReader = csv.reader(spreadsheet_rows, delimiter='\t', quoting=csv.QUOTE_NONE)
with open('./transcription_tmp.tsv', 'w', encoding='utf-8') as f_out:
    for n, row in enumerate(spreadSheetReader, 1):
        out_line = row
        if n>1:
            out_line = [x.lower() for x in out_line[1:]]
            for w in out_line:
                if any(c in w for c in DIACRITICS):
                    print("\t{}\t{}".format(n,w))
            f_out.write('\t'.join(out_line) + '\n')

