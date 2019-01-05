# -*- coding: utf-8 -*-

from google.cloud import datastore
import datetime
from ndb_base import NDB_Base

CLIENT = datastore.Client()
KIND = 'User'


class NDB_User(NDB_Base):

    def __init__(self, application, serial_number,
                 name=None, username=None,
                 update=True):
        id_str = "{}:{}".format(application, serial_number)
        self.key = CLIENT.key(KIND, id_str)
        self.entry = CLIENT.get(self.key)
        if not self.entry:
            self.entry = datastore.Entity(key=self.key)
            self.entry.update(
                application=application,
                serial_number=int(serial_number),
                debug=False
            )
        if update:
            self.update_info(name, username)

    def update_info(self, name, username):
        self.entry.update(
            name=name,
            username=username,
            last_update=datetime.datetime.now()
        )
        self.put()

    def from_twitter(self):
        return self.application == 'twitter'
    
    def needs_a_reply(self):
        return self.application in ['twitter', 'telegram']

def get_quiztime_user():
    user = NDB_User('quiztime', 0)
    return user

def get_webhook_solver_user():
    user = NDB_User('webhook_solver', 0)
    return user