from tzlocal import get_localzone
import datetime
import json
import pytz

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        local_tz = get_localzone()
        if isinstance(o, datetime.datetime):
            return o.replace(tzinfo=pytz.utc).astimezone(local_tz).isoformat()
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, str):
            return o
        else:
            return super(DateTimeEncoder, self).default(o)