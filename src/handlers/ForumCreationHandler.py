import tornado.web
import tornado.escape
from services import ForumService


class ForumCreationHandler(tornado.web.RequestHandler):

    def post(self):
        service = ForumService()
        self.set_header("Content-type", "application/json")

        data = tornado.escape.json_decode(self.request.body)

        result, status = service.create_forum(data['slug'],
                                              data['title'],
                                              data['user'])
        self.set_status(int(status))
        self.write(result)


