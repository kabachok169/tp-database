import tornado.web
import tornado.escape
from services import ThreadService
from utils import DateTimeEncoder
import json


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
            data['sort'] = 'flat'

        try:
            data['desc'] = self.get_argument('desc')
        except:
            data['desc'] = 'false'

        result, status = service.get_posts(id, slug, data)

        self.set_status(int(status))
        self.write(json.dumps(result, cls=DateTimeEncoder))


