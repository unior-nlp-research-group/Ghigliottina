#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from collections import defaultdict
import gzip
import pickle
import sys

def make_dir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

# convert defaultdict to regular dictionary
def default_to_regular(d):
    if isinstance(d, defaultdict):
        d = {k: default_to_regular(v) for k, v in d.items()}
    return d

def loadObjFromPklFile(pkl_file):
    with gzip.open(pkl_file, "rb") as pkl_in:        
        return pickle.load(pkl_in)

def dumpObjToPklFile(obj, pkl_file):
    with gzip.open(pkl_file, "wb") as pkl_out:  
        pickle.dump(obj, pkl_out)      

def ngrams(input, n):
    return [input[i:i+n] for i in range(len(input)-n+1)]      

def print_write(f_out, string):
    import sys
    sys.stdout.write(string)
    f_out.write(string)

def print_progress_bar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    sys.stdout.write('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix))
    sys.stdout.flush()
    # Print New Line on Complete
    if iteration == total:
        print()