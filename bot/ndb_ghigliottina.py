# -*- coding: utf-8 -*-

from google.cloud import datastore
from ndb_base import NDB_Base
from ndb_user import NDB_User, get_quiztime_user
import datetime

# class Ghigliottina(ndb.Model):
#     application = ndb.StringProperty()
#     serial_number = ndb.NumberProperty()
#     clues = ndb.StringProperty(repeated=True)
#     solution = ndb.StringProperty()

CLIENT = datastore.Client()
KIND = 'Ghigliottina'

class NDB_Ghigliottina(NDB_Base):
    def __init__(self, user, clues, solution, score):
        self.key = CLIENT.key(KIND, parent=user.key)
        self.entry = datastore.Entity(key=self.key)
        self.entry.update(
            clues = clues,
            clues_str = ','.join(sorted(clues)),
            solution = solution,        
            dt = datetime.datetime.now(),
            score = score
        )
        CLIENT.put(self.entry)

def get_past_solution_score(clues):
    clues_str = ','.join(sorted(clues))
    query = CLIENT.query(kind=KIND)
    query.add_filter('clues_str', '=', clues_str)
    matched_list = list(query.fetch(limit=1))
    if matched_list:
        entry = matched_list[0]
        return entry['solution'], entry.get('score',0)
    return None, None

def get_last_quizgame():    
    from datetime import datetime
    now = datetime.now()
    quizgame_user = get_quiztime_user()
    query = CLIENT.query(kind=KIND, ancestor=quizgame_user.key)
    query.order = ['-dt']
    entry = list(query.fetch(limit=1))[0]
    entry_dt = entry['dt']
    today = entry_dt.year == now.year and entry_dt.month == now.month and entry_dt.day == now.day
    return entry['clues'], entry['solution'], entry['score'], entry['dt'], today

def get_last_clues_solution_score():
    query = CLIENT.query(kind=KIND)
    query.order = ['-dt']
    last_list = list(query.fetch(limit=1))
    if last_list:
        entry = last_list[0]
        return entry['clues'], entry['solution'], entry['score']
    return None, None, None

def iter_ghigliottine():
    query = CLIENT.query(kind=KIND)
    def get_next_page(cursor):
        query_iter = query.fetch(start_cursor=cursor, limit=5)
        page = next(query_iter.pages)
        entries = list(page)
        next_cursor = query_iter.next_page_token
        return entries, next_cursor
    cursor = None
    while(True):    
        entries, cursor = get_next_page(cursor)
        print("{} {}".format(len(entries),cursor))
        if cursor == None:
            break