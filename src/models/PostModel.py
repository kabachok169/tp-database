import json
from datetime import datetime

class PostModel:
    def __init__(self, author = '', created = datetime.now(), message = '', thread='', forum = '',  id=''):
        self.created = created
        self.message = message
        self.author = author
        self.forum = forum
        self.id = id
        self.thread=thread

    def read(self):
        return {'author': self.author,
                'created': datetime.isoformat(self.created),
                'forum': self.forum,
                'id': self.id,
                'message': self.message,
                'thread': self.thread}