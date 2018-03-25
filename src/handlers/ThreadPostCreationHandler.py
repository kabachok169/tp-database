import tornado.web
import tornado.escape
from ..services import ThreadService


class ThreadPostCreationHandler(tornado.web.RequestHandler):

    def post(self, id):
        service = ThreadService()
        self.set_header("Content-type", "application/json")

        data = tornado.escape.json_decode(self.request.body)

        result, status = service.create_posts(id, data)

        self.set_status(int(status))
        self.write(result)


