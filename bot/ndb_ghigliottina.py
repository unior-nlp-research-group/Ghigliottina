# -*- coding: utf-8 -*-

from google.cloud import datastore
from ndb_base import NDB_Base
from ndb_user import NDB_User
import datetime

# class Ghigliottina(ndb.Model):
#     application = ndb.StringProperty()
#     serial_number = ndb.NumberProperty()
#     clues = ndb.StringProperty(repeated=True)
#     solution = ndb.StringProperty()

CLIENT = datastore.Client()
KIND = 'Ghigliottina'

class NDB_Ghigliottina(NDB_Base):
    def __init__(self, user, clues, solution):
        self.key = CLIENT.key(KIND, parent=user.key)
        self.entry = CLIENT.get(self.key)
        if not self.entry:
            self.entry = datastore.Entity(key=self.key)
            self.entry.update(
                clues = clues,
                solution = solution,        
                dt = datetime.datetime.now()
            )
            CLIENT.put(self.entry)
