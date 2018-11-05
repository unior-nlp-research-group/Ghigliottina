# -*- coding: utf-8 -*-

from google.cloud import datastore
CLIENT = datastore.Client()

class NDB_Base:    

    def __getattr__(self, attr):
        return self.entry[attr]
    
    def __setattr__(self, key, value):
        self.entry[key] = value

    def put(self):
        CLIENT.put(self.entry)

    def delete(self):
        CLIENT.delete(self.key)