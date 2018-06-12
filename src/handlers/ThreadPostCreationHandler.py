import tornado.web
import tornado.escape
from services import ThreadService
from utils.date_utils import DateTimeEncoder
from tzlocal import get_localzone
import pytz
import datetime
import json



class ThreadPostCreationHandler(tornado.web.RequestHandler):

    def post(self, slug_or_id):
        local_tz = get_localzone()
        cur_time = datetime.datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(local_tz).isoformat()

        service = ThreadService()
        self.set_header("Content-type", "application/json")


        data = tornado.escape.json_decode(self.request.body)

        try:
            id = int(slug_or_id)
            slug = None
        except:
            id = None
            slug = slug_or_id

        result, status = service.create_posts(id, slug, cur_time, data)

        self.set_status(int(status))
        self.write(json.dumps(result, cls=DateTimeEncoder))


