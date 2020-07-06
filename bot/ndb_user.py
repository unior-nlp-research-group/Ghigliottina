from google.cloud import datastore
import datetime
from ndb_base import NDB_Base
import key

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
            self.update_user(name, username)

    def update_user(self, name, username):
        self.entry.update(
            name=name,
            username=username,
            last_update=datetime.datetime.now()
        )
        if self.variables == None:
            self.variables = {}
        self.put()

    def is_admin(self):
        return str(self.serial_number) == key.TELEGRAM_BOT_MASTER_ID

    def set_state(self, state):
        self.state = state
        self.put()

    def set_keyboard(self, value, put=True):
        self.keyboard = {str(i):v for i,v in enumerate(value)}
        if put: self.put()

    def set_empy_keyboard(self, put=True):
        self.keyboard = {}
        if put: self.put()

    def get_keyboard(self):
        if self.keyboard:
            return [self.keyboard[str(i)] for i in range(len(self.keyboard))] 
        return []

    def set_var(self, var_name, var_value, put=False):
        self.variables[var_name] = var_value
        if put: self.put()

    def get_var(self, var_name):
        return self.variables.get(var_name,None)

    def from_twitter(self):
        return self.application == 'twitter'
    
    def needs_a_reply(self):
        return self.application in ['twitter', 'telegram']

def get_quiztime_user():
    user = NDB_User('quiztime', 0)
    return user

def get_ghigliottinai_user():
    user = NDB_User('ghigliottinai', 0)
    return user

def get_webhook_solver_user():
    user = NDB_User('webhook_solver', 0)
    return user

def get_user_count(application):
    q = CLIENT.query(kind=KIND)
    q.add_filter('application', '=', application)
    q.keys_only()
    return len(list(q.fetch()))

def stats():
    telegram_count = get_user_count('telegram')
    twitter_count = get_user_count('twitter')
    print('Telegram users: {}'.format(telegram_count))
    print('Twitter users: {}'.format(twitter_count))

if __name__ == '__main__':
    stats()
    