from ..models import *
from src.DataBase import DataBase
import tornado.escape


class ForumService:
    def __init__(self):
        self.check_user = '''SELECT nickname FROM users 
                             WHERE LOWER(nickname) = LOWER('{nickname}');'''
        self.check_forum = '''SELECT  
                              CASE WHEN ( 
                              SELECT slug FROM forum 
                              WHERE LOWER(slug) = LOWER('{slug}')) 
                              IS NOT NULL THEN TRUE ELSE FALSE END AS "found_forum"'''
        self.check_slug = '''SELECT  
                             CASE WHEN ( 
                             SELECT slug FROM thread 
                             WHERE LOWER(slug) = LOWER('{slug}') AND LOWER(title) = LOWER('{title}')) 
                             IS NOT NULL THEN TRUE ELSE FALSE END AS "found_forum"'''

    def create_forum(self, slug, title, user_name):
        db = DataBase()
        db_cur = db.get_cursor()
        db_cur.execute(self.check_user.format(nickname=user_name))
        user_status = db_cur.fetchall()

        if not len(user_status):
            db.close()
            return tornado.escape.json_encode({
                "message": "Can`t find user with id #42\n"
            }), '404'
        else:
            user_name = user_status[0][0]

        db_cur.execute(self.check_forum.format(slug=slug))
        forum_status = db_cur.fetchall()

        if forum_status[0][0]:
            db_cur.execute('''SELECT * FROM forum WHERE forum.slug = '{slug}';'''
                           .format(slug=slug))
            forum = db_cur.fetchall()
            forum = ForumModel(forum[0][1], forum[0][2], forum[0][3])
            db.close()
            return tornado.escape.json_encode(forum.read()), '409'

        db_cur.execute('''INSERT INTO forum (slug, title, author) VALUES ('{slug}','{title}', '{username}');'''
                       .format(slug=slug, title=title, username=user_name))
        db_cur = db.reconnect(True)
        db_cur.execute('''SELECT * FROM forum WHERE forum.slug = '{slug}';'''
                       .format(slug=slug))
        forum = db_cur.fetchall()
        forum = ForumModel(forum[0][1], forum[0][2], forum[0][3])
        db.close()
        return tornado.escape.json_encode(forum.read()), '201'

    def create_thread(self, slug, author, created, message, title):
        db = DataBase()
        db_cur = db.get_cursor()
        db_cur.execute('''SELECT id FROM users WHERE LOWER(users.nickname) = LOWER('{author}');'''
                       .format(author=author))
        author_id = db_cur.fetchall()

        db_cur.execute(self.check_forum.format(slug=slug))
        forum_status = db_cur.fetchall()
        if len(author_id) == 0 or not forum_status[0][0]:
            db.close()
            return tornado.escape.json_encode({
                "message": "Can`t find user with id #42\n"
            }), '404'

        db_cur.execute(self.check_slug.format(slug=slug, title=title))
        thread_status = db_cur.fetchall()
        if thread_status[0][0]:
            db_cur.execute('''SELECT users.nickname, thread.created, forum.title, thread.id, thread.message, thread.slug, thread.title
                              FROM thread 
                              JOIN users ON users.id = thread.author_id
                              JOIN forum ON forum.slug = thread.slug
                              WHERE LOWER(thread.slug) = LOWER('{slug}') AND LOWER(thread.title) = LOWER('{title}');'''
                           .format(slug=slug, title=title))
            thread = db_cur.fetchall()
            thread = SlugModel(thread[0][5], thread[0][1], thread[0][4], thread[0][6], thread[0][0], thread[0][2],
                               thread[0][3])
            db.close()
            return tornado.escape.json_encode(thread.read()), '409'

        db_cur.execute('''INSERT INTO thread (slug, created, message, title, author_id)
                       VALUES ('{slug}', '{created_on}', '{message}', '{title}', {author_id})'''
                       .format(slug=slug, created_on=created, message=message, title=title, author_id=author_id[0][0]))
        db_cur = db.obj_reconnect(True)
        db_cur.execute('''SELECT users.nickname, thread.created, forum.title, thread.id, thread.message, thread.slug, thread.title
                          FROM thread 
                          JOIN users ON users.id = thread.author_id
                          JOIN forum ON forum.slug = thread.slug
                          WHERE LOWER(thread.slug) = LOWER('{slug}') AND LOWER(thread.title) = LOWER('{title}');'''
                       .format(slug=slug, title=title))
        thread = db_cur.fetchone()
        print(thread)
        thread['created'] = datetime.isoformat(thread['created'])
        # thread = SlugModel(thread[0][5], thread[0][1], thread[0][4], thread[0][6], thread[0][0], thread[0][3],
        #                    thread[0][3])
        db.close()
        return tornado.escape.json_encode(thread), '201'

    def get_forum(self, slug):
        db = DataBase()
        db_cur = db.get_cursor()
        db_cur.execute('''SELECT * FROM forum WHERE forum.slug = '{slug}';'''.format(slug=slug))
        forum = db_cur.fetchall()
        if len(forum) == 0:
            db.close()
            return tornado.escape.json_encode({
                "message": "Can`t find user with id #42\n"
            }), '404'

        forum = ForumModel(forum[0][1], forum[0][2], forum[0][3])
        db.close()
        return tornado.escape.json_encode(forum.read()), '200'

    def get_threads(self, slug, limit, since):
        db = DataBase()
        db_cur = db.get_cursor()
        result = []
        db_cur.execute(self.check_forum.format(slug=slug))
        forum_status = db_cur.fetchall()
        if not forum_status[0][0] :
            db.close()
            return tornado.escape.json_encode({
                "message": "Can`t find user with id #42\n"
            }), '404'

        db_cur.execute('''SELECT users.nickname, thread.created, forum.title, thread.id, thread.message, thread.slug, thread.title
                          FROM thread 
                          JOIN users ON users.id = thread.author_id
                          JOIN forum ON forum.slug = thread.slug
                          WHERE LOWER(thread.slug) = LOWER('{slug}') AND thread.created_on >= '{since}'
                          ORDER BY thread.created_on
                          LIMIT {limit}'''
                       .format(slug=slug, limit=limit, since=since))
        threads = db_cur.fetchall()

        for thread in threads:
            thread_model = SlugModel(thread[5], thread[1], thread[4], thread[6], thread[0], thread[2],
                               thread[3])
            result.append(thread_model.read())

        db.close()
        return tornado.escape.json_encode(result), '200'



