import tornado.web
import tornado.escape
from ..services import ThreadService
import datetime


class ThreadPostCreationHandler(tornado.web.RequestHandler):

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

        result, status = service.create_posts(id, slug, datetime.datetime.now(), data)

        self.set_status(int(status))
        self.write(result)


