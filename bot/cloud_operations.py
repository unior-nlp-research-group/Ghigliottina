# -*- coding: utf-8 -*-

from google.cloud import storage
import pickle
import logging
import gzip

def get_clue_subtable(clue_word):        
    bucket_name = 'ghigliottina'
    filename = 'matrix_split/{}.pkl'.format(clue_word)
    gcs = storage.Client()
    bucket = gcs.bucket(bucket_name)    
    blob = bucket.get_blob(filename)
    if blob is None:
        return None
    content_zipped = blob.download_as_string()    
    content = gzip.decompress(content_zipped)
    clue_subtable = pickle.loads(content)
    return clue_subtable