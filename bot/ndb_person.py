# -*- coding: utf-8 -*-

from google.appengine.ext import ndb

class Person(ndb.Model):
    application = ndb.StringProperty() # 'telegram', 'twitter'
    serial_number = ndb.NumberProperty()    
    fist_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    username = ndb.StringProperty()
    state = ndb.IntegerProperty()
    enabled = ndb.BooleanProperty(default=True)
    debug_mode = ndb.BooleanProperty(default=False)

def get_id(application, serial_number):
    return "{}:{}".format(application, serial_number)

def get_person(application, serial_number):
    id = get_id(application, serial_number)
    return Person.get_by_id(id)

def register_person(application, serial_number, fist_name=None, last_name=None, username=None):
    p = get_person(application, serial_number)
    if not p:
        p = Person(
            id = get_id(application, serial_number),
            application = application,
            serial_number = serial_number,        
            fist_name=fist_name, 
            last_name=last_name, 
            username=username
        )
    p.put()
    return p
    
