from json import load
from urllib2 import urlopen


class Commit(object):
    def __init__(self,name='',date='',commiter_id=''):
        pass

class User(object):
    pass


class Repo(object):
    def __init__(self,name='',full_name=''):
        self.name = name
        self.full_name = full_name
        self.created = ''
        self.url = ''
        self.is_fork = False
        self.language = ''
