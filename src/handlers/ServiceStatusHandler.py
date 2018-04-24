import tornado.web
import tornado.escape
from src.DataBase import DataBase


class ServiceStatusHandler(tornado.web.RequestHandler):
    def get(self):
        result = {}
        db = DataBase()
        db_cur = db.get_object_cur()

        db_cur.execute('SELECT COUNT(*) FROM users;')
        result.update({'user': db_cur.fetchone()['count']})

        db_cur.execute('SELECT COUNT(*) FROM forum;')
        result.update({'forum': db_cur.fetchone()['count']})

        db_cur.execute('SELECT COUNT(*) FROM thread;')
        result.update({'thread': db_cur.fetchone()['count']})

        db_cur.execute('SELECT COUNT(*) FROM messages;')
        result.update({'post': db_cur.fetchone()['count']})

        self.set_header("Content-type", "application/json")
        self.set_status(200)
        self.write(result)


