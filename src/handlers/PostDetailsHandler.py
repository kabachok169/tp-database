import tornado.web
import tornado.escape
from services import PostService
from utils import DateTimeEncoder
import json


class PostDetailsHandler(tornado.web.RequestHandler):

    def get(self, id):
        service = PostService()
        self.set_header("Content-type", "application/json")

        try:
            related = self.get_argument('related')
        except:
            related = None

        result, status = service.get_post(id, related)

        self.set_status(int(status))
        self.write(json.dumps(result, cls=DateTimeEncoder))

    def post(self, id):
        service = PostService()
        self.set_header("Content-type", "application/json")

        data = tornado.escape.json_decode(self.request.body)

        result, status = service.update_post(id, data)

        self.set_status(int(status))
        self.write(json.dumps(result, cls=DateTimeEncoder))


