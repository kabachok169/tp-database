from models import *
from DataBase import DataBase
import tornado.escape
import datetime


class PostService:

    def get_post(self, id, related):
        db = DataBase()
        db_cur = db.get_object_cur()
        db_cur.execute('''SELECT * FROM messages WHERE id = {id}'''.format(id=id))
        post = db_cur.fetchone()
        if not post:
            db.close()
            return {"message": "Can`t find thread with id #42"}, '404'

        result = {}
        # post['created'] = datetime.datetime.isoformat(post['created'])
        post['isEdited'] = post['isedited']
        result['post'] = post

        if related == None:
            return result, '200'

        if 'user' in related:
            db_cur.execute('''SELECT * FROM users WHERE LOWER(users.nickname) = LOWER('{author}');'''
                           .format(author=post['author']))
            author = db_cur.fetchone()
            result['author'] = author

        if 'forum' in related:
            db_cur.execute('''SELECT * FROM forum WHERE forum.slug = '{slug}';'''
                           .format(slug=post['forum']))
            forum = db_cur.fetchone()
            forum['user'] = forum['author']
            db_cur.execute('''SELECT COUNT(*) FROM thread
                              WHERE LOWER(thread.forum) = LOWER('{slug}');'''.format(slug=post['forum']))
            forum.update({'threads': db_cur.fetchone()['count']})

            db_cur.execute('''SELECT COUNT(*) FROM messages
                              WHERE LOWER(messages.forum) = LOWER('{slug}');'''.format(slug=post['forum']))
            forum.update({'posts': db_cur.fetchone()['count']})
            result['forum'] = forum

        if 'thread' in related:
            db_cur.execute('''SELECT * FROM thread WHERE thread.id = {thread};'''
                           .format(thread=post['thread']))
            thread = db_cur.fetchone()
            thread['created'] = datetime.datetime.isoformat(thread['created'])
            result['thread'] = thread

        db.close()
        return result, '200'

    def update_post(self, id, data):
        db = DataBase()
        db_cur = db.get_object_cur()
        db_cur.execute('''SELECT * FROM messages WHERE id = {id}'''.format(id=id))
        post = db_cur.fetchone()

        if not post:
            db.close()
            return {"message": "Can`t find thread with id #42"}, '404'
        if not 'message' in data or data['message'] == post['message']:
            # post['created'] = datetime.datetime.isoformat(post['created'])
            # post['isEdited'] = post['isedited']
            return post, '200'

        db_cur.execute('''UPDATE messages SET isEdited=TRUE, message='{message}' WHERE id = {id} RETURNING *;'''
                       .format(message=data['message'], id=id))
        post = db_cur.fetchone()
        # post['created'] = datetime.datetime.isoformat(post['created'])
        post['isEdited'] = post['isedited']
        db.close()
        return post, '200'

    def create_post_request(self, id, related):
        request = '''SELECT * AS post FROM messages'''

        if 'author' in related:
            request += '''JOIN users AS user ON LOWER(users.nickname) = LOWER(messages.author) '''
        if 'forum' in related:
            request += '''JOIN forum AS forum ON LOWER(forum.slug) = LOWER(messages.forum) '''
        if 'thread' in related:
            request += '''JOIN thread ON thread.id = messages.thread '''
        request += '''WHERE messages.id = {id}'''

        request.format(id=id)
        return request


