

class UserModel:
    def __init__(self, about = '', email = '', fullname = '', nickname = ''):
        self.about = about
        self.email = email
        self.fullname = fullname
        self.nickname = nickname

    def write(self, about = '', email = '', fullname = '', nickname = ''):
        self.about = about
        self.email = email
        self.fullname = fullname
        self.nickname = nickname

    def read(self):
        return '{nick}, {about}, {email}, {fullname}'.format(nick=self.nickname, about=self.about, email=self.email, fullname=self.fullname)
