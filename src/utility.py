#! /usr/bin/env python3

import os
from collections import defaultdict
import gzip
import pickle

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
