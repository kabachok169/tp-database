import json
from datetime import datetime

class SlugModel:
    def __init__(self, forum = '', created = datetime.now(), message = '', title = '', author = '', id = '', votes = ''):
        self.title = title
        self.created = created
        self.message = message
        self.author = author
        self.forum = forum
        self.id = id

    def read(self):
        return {'author': self.author,
                           'created': datetime.isoformat(self.created),
                           'forum': self.forum,
                           'id': self.id,
                           'message': self.message,
                           'title': self.title,
                           # 'votes': 0
                }