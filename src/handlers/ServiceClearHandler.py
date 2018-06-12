import tornado.web
import tornado.escape
from DataBase import DataBase



class ServiceClearHandler(tornado.web.RequestHandler):

    def post(self):
        db = DataBase()
        db_cur = db.get_object_cur()
        db_cur.execute('''TRUNCATE TABLE users, forum, thread, messages, votes, usersForums''')
        db.obj_reconnect(True)

        self.set_header("Content-type", "application/json")
        self.set_status(200)

    get = post


