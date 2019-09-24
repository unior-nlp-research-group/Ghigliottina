# -*- coding: utf-8 -*-

from google.cloud import datastore
CLIENT = datastore.Client()

class NDB_Base(object):    

    attributes = ['key','entry']

    def __getattr__(self, attr):
        return self.entry.get(attr,None)
    
    def __setattr__(self, key, value):
        if key in self.attributes:
            super().__setattr__(key, value)
        else:
            self.entry[key] = value

    def put(self):
        CLIENT.put(self.entry)

    def delete(self):
        CLIENT.delete(self.key)