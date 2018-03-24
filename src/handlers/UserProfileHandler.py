import tornado.web
import tornado.escape
from ..services import UserService


class UserProfileHandler(tornado.web.RequestHandler):

    def get(self, nickname):
        service = UserService()
        self.set_header("Content-type", "application/json")

        result, status = service.get_user(nickname)

        self.set_status(int(status))
        self.write(result)

    def post(self, nickname):
        service = UserService()
        self.set_header("Content-type", "application/json")

        data = tornado.escape.json_decode(self.request.body)

        result, status = service.update_user(nickname,
                                             data['about'],
                                             data['email'],
                                             data['fullname'])
        self.set_status(int(status))
        self.write(result)


