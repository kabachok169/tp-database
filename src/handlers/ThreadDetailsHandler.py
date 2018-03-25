import tornado.web
import tornado.escape
from ..services import ThreadService


class ThreadDetailsHandler(tornado.web.RequestHandler):

    def get(self, id):
        service = ThreadService()
        self.set_header("Content-type", "application/json")

        result, status = service.get_thread(id)

        self.set_status(int(status))
        self.write(result)

    def post(self, id):
        service = ThreadService()
        self.set_header("Content-type", "application/json")

        data = tornado.escape.json_decode(self.request.body)

        result, status = service.update_thread(id, data)

        self.set_status(int(status))
        self.write(result)


