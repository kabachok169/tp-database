from ..models import *
from src.DataBase import DataBase
import tornado.escape
from datetime import datetime



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
        self.check_thread = '''SELECT  
                             CASE WHEN ( 
                             SELECT slug FROM thread 
                             WHERE thread.id = {id})
                             IS NOT NULL THEN TRUE ELSE FALSE END AS "found_thread"'''

    def create_post(self, id, datetime, data):
        author = data['author']
        db = DataBase()
        db_cur = db.get_cursor()
        db_cur.execute(self.check_thread.format(id=id))
        thread_status = db_cur.fetchall()

        if not thread_status[0][0]:
            db.close()
            return tornado.escape.json_encode({
                "message": "Can`t find thread with id #42\n"
            }), '404'

        db_cur.execute('''INSERT INTO message (created_on, message, author_name, thread_id)
                          VALUES ('{datetime}','{message}','{username}', {thread});'''
                       .format(datetime=datetime, message=data['message'], username=author, thread=id))
        # db_cur = db.reconnect(True)
        # db_cur.execute('''SELECT * FROM message WHERE message. = '{slug}';'''
        #                .format(slug=slug))
        # forum = db_cur.fetchall()
        # forum = ForumModel(forum[0][1], forum[0][2], forum[0][3])
        db.close()
        post = PostModel(author, datetime, data['message'], id)
        return post.read(), '201'

    def create_posts(self, id, data):
        result = []
        date = datetime.now()
        for post in data:
            post, status = self.create_post(id, date, post)
            if status == '404':
                return post, status
            result.append(post)

        return tornado.escape.json_encode(result), '201'

    def get_thread(self, id):
        db = DataBase()
        db_cur = db.get_cursor()
        db_cur.execute(self.check_thread.format(id=id))
        thread_status = db_cur.fetchall()

        if not thread_status[0][0]:
            db.close()
            return tornado.escape.json_encode({
                "message": "Can`t find thread with id #42\n"
            }), '404'

        db_cur.execute('''SELECT users.nickname, thread.created_on, forum.title, thread.id, thread.message, thread.slug, thread.title
                          FROM thread 
                          JOIN users ON users.id = thread.author_id
                          JOIN forum ON forum.slug = thread.slug
                          WHERE thread.id = {id}'''
                       .format(id=id))
        thread = db_cur.fetchall()


        thread_model = SlugModel(thread[0][5], thread[0][1], thread[0][4], thread[0][6], thread[0][0], thread[0][2],
                                 thread[0][3])


        db.close()
        return tornado.escape.json_encode(thread_model.read()), '200'

    def update_thread(self, id, data):
        if 'title' not in data.keys():
            title = None
        else:
            title = data['title']

        if 'message' not in data.keys():
            message = None
        else:
            message = data['message']

        db = DataBase()
        db_cur = db.get_cursor()
        db_cur.execute(self.check_thread.format(id=id))
        thread_status = db_cur.fetchall()

        if not thread_status[0][0]:
            db.close()
            return tornado.escape.json_encode({
                "message": "Can`t find thread with id #42\n"
            }), '404'

        if not title and not message:
            db_cur.execute('''SELECT users.nickname, thread.created_on, forum.title, thread.id, thread.message, thread.slug, thread.title
                                      FROM thread 
                                      JOIN users ON users.id = thread.author_id
                                      JOIN forum ON forum.slug = thread.slug
                                      WHERE thread.id = {id}'''
                           .format(id=id))
            thread = db_cur.fetchall()

            thread_model = SlugModel(thread[0][5], thread[0][1], thread[0][4], thread[0][6], thread[0][0], thread[0][2],
                                     thread[0][3])

            db.close()
            return tornado.escape.json_encode(thread_model.read()), '200'

        db_cur.execute(self.create_update_request(id, title, message))
        db_cur.execute('''SELECT users.nickname, thread.created_on, forum.title, thread.id, thread.message, thread.slug, thread.title
                                              FROM thread 
                                              JOIN users ON users.id = thread.author_id
                                              JOIN forum ON forum.slug = thread.slug
                                              WHERE thread.id = {id}'''
                       .format(id=id))
        thread = db_cur.fetchall()

        thread_model = SlugModel(thread[0][5], thread[0][1], thread[0][4], thread[0][6], thread[0][0], thread[0][2],
                                 thread[0][3])

        db.close()
        return tornado.escape.json_encode(thread_model.read()), '200'

    def create_update_request(self, id, title, message):
        request = '''UPDATE thread SET '''
        if title != None:
            request += '''title='{title}','''.format(title=title)
        if message != None:
            request += '''message='{message}','''.format(message=message)

        request = request[:-1]
        request += ' '
        request += '''WHERE id = {id};'''.format(id=id)
        return request
