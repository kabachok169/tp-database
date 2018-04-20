import tornado.web
import tornado.escape
from ..services import ThreadService


class ThreadDetailsHandler(tornado.web.RequestHandler):

    def get(self, slug_or_id):
        service = ThreadService()
        self.set_header("Content-type", "application/json")

        try:
            id = int(slug_or_id)
            slug = None
        except:
            id = None
            slug = slug_or_id

        result, status = service.get_thread(id, slug)

        self.set_status(int(status))
        self.write(result)

    def post(self, slug_or_id):
        service = ThreadService()
        self.set_header("Content-type", "application/json")

        data = tornado.escape.json_decode(self.request.body)

        try:
            id = int(slug_or_id)
            slug = None
        except:
            id = None
            slug = slug_or_id

        result, status = service.update_thread(id, slug, data)

        self.set_status(int(status))
        self.write(result)


