# -*- coding: utf-8 -*-

from google.cloud import datastore
import datetime
from ndb_base import NDB_Base

CLIENT = datastore.Client()
KIND = 'User'

class NDB_User(NDB_Base):

    def __init__(self, application, serial_number, first_name=None, last_name=None, username=None):
        id_str = "{}:{}".format(application, serial_number)
        self.key = CLIENT.key(KIND, id_str)
        self.entry = CLIENT.get(self.key)
        if not self.entry:
            self.entry = datastore.Entity(key=self.key)
            self.entry.update(
                application = application,
                serial_number = serial_number,
                debug = False
            )
        self.update_info(first_name, last_name, username)

    def update_info(self, first_name, last_name, username):
        self.entry.update(
            first_name=first_name, 
            last_name=last_name, 
            username=username,
            last_update = datetime.datetime.now()
        )
        CLIENT.put(self.entry)
    
    
