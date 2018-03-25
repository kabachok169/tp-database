import tornado.web
import tornado.escape
from ..services import ForumService


class ForumThreadsHandler(tornado.web.RequestHandler):

    def get(self, slug):
        service = ForumService()
        self.set_header("Content-type", "application/json")

        result, status = service.get_threads(slug,
                                             self.get_argument('limit'),
                                             self.get_argument('since'))
                                             # self.get_argument('sort'))
        self.set_status(int(status))
        self.write(result)


