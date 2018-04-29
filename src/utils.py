from datetime import datetime, date
from tzlocal import get_localzone
import pytz
import json


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        local_tz = get_localzone()
        if isinstance(o, datetime):
            return o.replace(tzinfo=pytz.utc).astimezone(local_tz).isoformat()
        elif isinstance(o, date):
            return o.isoformat()
        elif isinstance(o, str):
            return o
        else:
            return super(DateTimeEncoder, self).default(o)


def get_local_time():
    local_tz = get_localzone()
    return datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(local_tz).isoformat()
