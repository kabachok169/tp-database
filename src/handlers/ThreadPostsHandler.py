import tornado.web
import tornado.escape
from ..services import ThreadService


class ThreadPostsHandler(tornado.web.RequestHandler):

    def get(self, slug_or_id):
        service = ThreadService()
        self.set_header("Content-type", "application/json")

        data = {}

        try:
            id = int(slug_or_id)
            slug = None
        except:
            id = None
            slug = slug_or_id

        try:
            data['limit'] = self.get_argument('limit')
        except:
            data['limit'] = None

        try:
            data['since'] = self.get_argument('since')
        except:
            data['since'] = None

        try:
            data['sort'] = self.get_argument('sort')
        except:
            data['sort'] = None

        try:
            data['desc'] = self.get_argument('desc')
        except:
            data['desc'] = None

        result, status = service.get_posts(id, slug, data)

        self.set_status(int(status))
        self.write(result)

