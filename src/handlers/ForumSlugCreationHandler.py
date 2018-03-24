import tornado.web
import tornado.escape
from ..services import ForumService


class ForumSlugCreationHandler(tornado.web.RequestHandler):

    def post(self, slug):
        service = ForumService()
        self.set_header("Content-type", "application/json")

        data = tornado.escape.json_decode(self.request.body)

        result, status = service.create_slug(slug,
                                             data['author'],
                                             data['created'],
                                             data['message'],
                                             data['title'])
        self.set_status(int(status))
        self.write(result)


