import tornado.web
from ..services import UserService


class UserHandler(tornado.web.RequestHandler):

    # def __init__(self):
    #     self.service = UserService()

    def post(self, nickname):
        service = UserService()
        self.set_header("Content-type", "text/plain")
        result = service.create_user(nickname, self.get_argument('about'), self.get_argument('email'), self.get_argument('fullname'))
        self.write(result)


