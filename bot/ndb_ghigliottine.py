# -*- coding: utf-8 -*-

from google.appengine.ext import ndb

class Ghigliottina(ndb.Model): #ndb.Expando    
    application = ndb.StringProperty() # 'telegram', 'twitter'
    serial_number = ndb.NumberProperty()
    clues = ndb.StringProperty(repeated=True)
    solution = ndb.StringProperty()

def add_ghigliottina(application, serial_number, clues, solution):
    g = Ghigliottina(
        serial_number = serial_number,
        application = application,
        clues = clues,
        solution = solution
    )
    g.put()
    return g