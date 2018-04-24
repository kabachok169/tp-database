import tornado.web
import tornado.escape
from ..services import PostService


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
        self.write(result)

    def post(self, id):
        service = PostService()
        self.set_header("Content-type", "application/json")

        data = tornado.escape.json_decode(self.request.body)

        result, status = service.get_post(id, data)

        self.set_status(int(status))
        self.write(result)


