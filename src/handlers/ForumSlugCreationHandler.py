import tornado.web
import tornado.escape
from ..services import ForumService
import datetime


class ForumSlugCreationHandler(tornado.web.RequestHandler):

    def post(self, slug):
        service = ForumService()
        self.set_header("Content-type", "application/json")

        data = tornado.escape.json_decode(self.request.body)
        if 'created' not in data.keys():
            data['created'] = datetime.datetime.now()
        if 'slug' not in data.keys():
            data['slug'] = None

        result, status = service.create_thread(slug,
                                               data['author'],
                                               data['created'],
                                               data['message'],
                                               data['title'],
                                               data['slug'])
        self.set_status(int(status))
        self.write(result)


