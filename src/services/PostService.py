from ..models import *
from src.DataBase import DataBase
import tornado.escape
import datetime


class PostService:

    def get_post(self, id, related):
        db = DataBase()
        db_cur = db.get_object_cur()
        db_cur.execute('''SELECT * FROM messages WHERE id = {id}'''.format(id=id))
        post = db_cur.fechone()
        if not post:
            db.close()
            return tornado.escape.json_encode({
                "message": "Can`t find thread with id #42\n"
            }), '404'

        if related == None:
            return tornado.escape.json_encode(post), '200'

        db_cur.execute(self.create_post_request(id, related))
        post_info = db_cur.fechone()
        db.close()
        return tornado.escape.json_encode(post_info), '200'

    def update_post(self, id, data):
        db = DataBase()
        db_cur = db.get_object_cur()
        db_cur.execute('''SELECT * FROM messages WHERE id = {id}'''.format(id=id))
        post = db_cur.fechone()
        if not post:
            db.close()
            return tornado.escape.json_encode({
                "message": "Can`t find thread with id #42\n"
            }), '404'
        db_cur.execute('''UPDATE messages SET isEdited=TRUE, message='{message}' WHERE id = {id} RETURNING *;'''
                       .format(message=data['message'], id=id))
        post = db_cur.fechone()
        db.close()
        return tornado.escape.json_encode(post), '200'

    def create_post_request(self, id, related):
        request = '''SELECT * FROM messages'''

        if 'author' in related:
            request += '''JOIN users ON LOWER(users.nickname) = LOWER(messages.author) '''
        if 'forum' in related:
            request += '''JOIN forum ON LOWER(forum.slug) = LOWER(messages.forum) '''
        if 'thread' in related:
            request += '''JOIN thread ON thread.id = messages.thread '''
        request += '''WHERE messages.id = {id}'''

        request.format(id=id)
        return request


