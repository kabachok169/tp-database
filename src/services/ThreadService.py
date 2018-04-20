from ..models import *
from src.DataBase import DataBase
import tornado.escape
import datetime



class ThreadService:
    def __init__(self):
        self.check_user = '''SELECT  
                             CASE WHEN ( 
                             SELECT nickname FROM users 
                             WHERE LOWER(nickname) = LOWER('{nickname}')) 
                             IS NOT NULL THEN TRUE ELSE FALSE END AS "found"'''
        self.check_forum = '''SELECT  
                              CASE WHEN ( 
                              SELECT slug FROM forum 
                              WHERE LOWER(slug) = LOWER('{slug}')) 
                              IS NOT NULL THEN TRUE ELSE FALSE END AS "found_forum"'''
        self.check_thread = '''SELECT * 
                               FROM thread 
                               {cond}'''
        self.check_parent = '''SELECT id FROM messages 
                               WHERE messages.id = {id}'''

    def create_post(self, id, forum, date, data):
        author = data['author']

        if 'parent' not in data:
            data['parent'] = 0

        db = DataBase()
        db_cur = db.get_object_cur()

        db_cur.execute(self.check_parent.format(id=data['parent']))
        parent_status = db_cur.fetchall()

        if data['parent'] != 0:
            if not len(parent_status):
                db.close()
                return tornado.escape.json_encode({
                    "message": "Can`t find parent with id #42\n"
                }), '409'

        db_cur.execute('''INSERT INTO messages (created, message, author, thread, forum, parent)
                          VALUES ('{datetime}','{message}','{username}', {thread}, '{forum}', {parent}) RETURNING *;'''
                       .format(datetime=date, message=data['message'], username=author, thread=id,
                               parent=data['parent'], forum=forum))
        post = db_cur.fetchone()
        post['created'] = datetime.datetime.isoformat(post['created'])
        db.close()

        return post, '201'

    def create_posts(self, id, slug, datetime, data):

        db = DataBase()
        db_cur = db.get_object_cur()
        db_cur.execute(self.check_thread
                       .format(cond=' WHERE ' + 'thread.id = ' + id.__str__() if id != None else ' WHERE ' + 'LOWER(thread.slug) = ' + "LOWER('" + slug + "')"))
        thread = db_cur.fetchall()

        if not thread[0]:
            db.close()
            return tornado.escape.json_encode({
                "message": "Can`t find thread with id #42\n"
            }), '404'

        result = []

        for post in data:
            post, status = self.create_post(thread[0]['id'], thread[0]['forum'], datetime, post)
            if status == '404' or status == '409':
                return post, status
            result.append(post)

        return tornado.escape.json_encode(result), '201'

    def get_thread(self, id, slug):
        db = DataBase()
        db_cur = db.get_object_cur()
        db_cur.execute(self.check_thread
            .format(
            cond=' WHERE ' + 'thread.id = ' + id.__str__() if id != None else ' WHERE ' + 'LOWER(thread.slug) = ' + "LOWER('" + slug + "')"))
        thread = db_cur.fetchone()
        if not thread:
            db.close()
            return tornado.escape.json_encode({
                "message": "Can`t find thread with id #42\n"
            }), '404'
        db.close()
        thread['created'] = datetime.datetime.isoformat(thread['created'])
        return tornado.escape.json_encode(thread), '200'

    def update_thread(self, id, slug, data):
        if 'title' not in data.keys():
            title = None
        else:
            title = data['title']

        if 'message' not in data.keys():
            message = None
        else:
            message = data['message']

        db = DataBase()
        db_cur = db.get_object_cur()
        db_cur.execute(self.check_thread
            .format(
            cond=' WHERE ' + 'thread.id = ' + id.__str__() if id != None else ' WHERE ' + 'LOWER(thread.slug) = ' + "LOWER('" + slug + "')"))
        thread = db_cur.fetchone()
        if not thread:
            db.close()
            return tornado.escape.json_encode({
                "message": "Can`t find thread with id #42\n"
            }), '404'

        if not title and not message:
            db.close()
            thread['created'] = datetime.datetime.isoformat(thread['created'])
            return tornado.escape.json_encode(thread), '200'

        db_cur.execute(self.create_update_request(thread['id'], title, message))

        thread = db_cur.fetchone()

        db.close()
        thread['created'] = datetime.datetime.isoformat(thread['created'])
        return tornado.escape.json_encode(thread), '200'

    def vote(self, id, slug, data):
        db = DataBase()
        db_cur = db.get_object_cur()
        db_cur.execute(self.check_thread
                       .format(
            cond=' WHERE ' + 'thread.id = ' + id.__str__() if id != None else ' WHERE ' + 'LOWER(thread.slug) = ' + "LOWER('" + slug + "')"))
        thread = db_cur.fetchone()
        if not thread:
            db.close()
            return tornado.escape.json_encode({
                "message": "Can`t find thread with id #42\n"
            }), '404'

        db_cur.execute('''SELECT * FROM votes
                       WHERE votes.thread={thread} AND votes.nickname='{nickname}';'''
                       .format(thread=thread['id'], nickname=data['nickname']))
        vote = db_cur.fetchone()
        # if vote['voice'] <= -1 or vote['voice'] >= 1:
        #     db.close()
        #     return tornado.escape.json_encode({
        #         "message": "Can`t find thread with id #42\n"
        #     }), '404'

        if vote:
            if vote['voice'] + data['voice'] == 2 or vote['voice'] + data['voice'] == -2:
                db.close()
                thread['created'] = datetime.datetime.isoformat(thread['created'])
                return tornado.escape.json_encode(thread), '200'
            elif vote['voice'] + data['voice'] == 0:
                db_cur.execute('''UPDATE votes SET voice={voice}
                               WHERE votes.thread={thread} AND votes.nickname='{nickname}';'''
                               .format(thread=thread['id'], nickname=data['nickname'], voice=data['voice']))
                db.close()
                return self.update_thread(thread['id'], 2 * data['voice']), 200
            else:
                db_cur.execute('''UPDATE votes SET voice={voice}
                               WHERE votes.thread={thread} AND votes.nickname='{nickname}';'''
                               .format(thread=thread['id'], nickname=data['nickname'], voice=data['voice']))
                db.close()
                return self.update_thread(thread['id'], -vote['voice']), 200

        db_cur.execute('''INSERT INTO votes (voice, nickname, thread) VALUES ({voice}, '{nickname}', {thread})'''
                       .format(voice=data['voice'], nickname=data['nickname'], thread=thread['id']))
        db_cur = db.obj_reconnect(True)
        return self.update_thread(thread['id'], data['voice']), 200


    def update_thread(self, thread, vote):
        db = DataBase()
        db_cur = db.get_object_cur()
        db_cur.execute('''UPDATE thread SET votes=votes+{voice}
                       WHERE thread.id={thread} RETURNING *;'''
                       .format(thread=thread, voice=vote))
        thread = db_cur.fetchone()
        thread['created'] = datetime.datetime.isoformat(thread['created'])
        db.close()
        return thread

    def create_update_request(self, id, title, message):
        request = '''UPDATE thread SET '''
        if title != None:
            request += '''title='{title}','''.format(title=title)
        if message != None:
            request += '''message='{message}','''.format(message=message)

        request = request[:-1]
        request += ' '
        request += '''WHERE id = {id} RETURNING *;'''.format(id=id)
        return request


