import tornado.web
import tornado.escape
from ..services import UserService


class UserCreationHandler(tornado.web.RequestHandler):

    def post(self, nickname):
        service = UserService()
        self.set_header("Content-type", "application/json")

        data = tornado.escape.json_decode(self.request.body)

        result, status = service.create_user(nickname, data)
        self.set_status(int(status))
        self.write(result)


