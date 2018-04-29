import tornado.web
import tornado.escape
from services import ForumService


class ForumThreadsHandler(tornado.web.RequestHandler):

    def get(self, slug):
        service = ForumService()
        self.set_header("Content-type", "application/json")

        try:
            limit = self.get_argument('limit')
        except:
            limit = None

        try:
            since = self.get_argument('since')
        except:
            since = None

        try:
            desk = self.get_argument('desc')
        except:
            desk = 'false'

        result, status = service.get_threads(slug, limit, since, desk)

        self.set_status(int(status))
        self.write(result)


