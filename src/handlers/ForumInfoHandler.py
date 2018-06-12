import tornado.web
import tornado.escape
from services import ForumService


class ForumInfoHandler(tornado.web.RequestHandler):

    def get(self, slug):
        service = ForumService()
        self.set_header("Content-type", "application/json")

        result, status = service.get_forum(slug)
        self.set_status(int(status))
        self.write(result)


