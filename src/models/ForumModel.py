import json


class ForumModel:
    def __init__(self, slug = '', title = '', user_name = ''):
        self.slug = slug
        self.title = title
        self.username = user_name

    def read(self):
        return {'slug': self.slug,
               'title': self.title,
               'user': self.username}