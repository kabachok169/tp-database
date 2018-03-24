import json

class UserModel:
    def __init__(self, nickname = '', about = '', email = '', fullname = ''):
        self.about = about
        self.email = email
        self.fullname = fullname
        self.nickname = nickname

    def write(self, nickname = '', about = '', email = '', fullname = ''):
        self.about = about
        self.email = email
        self.fullname = fullname
        self.nickname = nickname

    def read(self):
        return json.dumps({'about': self.about,
                           'email': self.email,
                           'fullname': self.fullname,
                           'nickname': self.nickname})