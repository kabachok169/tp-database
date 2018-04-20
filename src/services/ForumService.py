from ..models import *
from src.DataBase import DataBase
import tornado.escape


class ForumService:
    def __init__(self):
        self.check_user = '''SELECT * FROM users 
                             WHERE LOWER(nickname) = LOWER('{nickname}');'''
        self.check_forum = '''SELECT * FROM forum 
                              WHERE LOWER(slug) = LOWER('{slug}')'''
        self.check_slug = '''SELECT *
                             FROM thread 
                             WHERE LOWER(thread.slug) = LOWER('{slug}');'''

    def create_forum(self, slug, title, user_name):
        db = DataBase()
        db_cur = db.get_object_cur()
        db_cur.execute(self.check_user.format(nickname=user_name))
        user_status = db_cur.fetchall()
        print(user_status)

        if not len(user_status):
            db.close()
            return tornado.escape.json_encode({
                "message": "Can`t find user with id #42\n"
            }), '404'
        else:
            user_name = user_status[0]['nickname']

        db_cur.execute(self.check_forum.format(slug=slug))
        forum_status = db_cur.fetchall()

        if len(forum_status):
            db.close()
            forum_status[0]['user'] = forum_status[0]['author']
            return tornado.escape.json_encode(forum_status[0]), '409'

        db_cur.execute('''INSERT INTO forum (slug, title, author) VALUES ('{slug}','{title}', '{username}') RETURNING *;'''
                       .format(slug=slug, title=title, username=user_name))
        forum = db_cur.fetchone()
        forum['user'] = forum['author']
        db.close()
        return tornado.escape.json_encode(forum), '201'

    def create_thread(self, forum, author, created, message, title, slug):
        db = DataBase()
        db_cur = db.get_object_cur()
        db_cur.execute('''SELECT nickname FROM users WHERE LOWER(users.nickname) = LOWER('{author}');'''
                       .format(author=author))
        author = db_cur.fetchall()

        db_cur.execute(self.check_forum.format(slug=forum))
        forum_status = db_cur.fetchall()
        if len(author) == 0 or not len(forum_status):
            db.close()
            return tornado.escape.json_encode({
                "message": "Can`t find user with id #42\n"
            }), '404'

        if slug != None:
            db_cur.execute(self.check_slug.format(slug=slug))
            thread_status = db_cur.fetchall()
            if len(thread_status):
                thread_status[0]['created'] = datetime.isoformat(thread_status[0]['created'])
                return tornado.escape.json_encode(thread_status[0]), '409'

        db_cur.execute('''INSERT INTO thread (created, message, title, author, forum{is_slug})
                       VALUES ('{created_on}', '{message}', '{title}', '{author}', '{forum}'{slug}) RETURNING *;'''
                       .format(is_slug=', slug' if slug != None else '',
                               created_on=created, message=message, title=title, author=author[0]['nickname'], forum=forum_status[0]['slug'],
                               slug=", '" + slug + "'" if slug != None else ''))
        thread = db_cur.fetchone()
        thread['created'] = datetime.isoformat(thread['created'])
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

    def get_threads(self, slug, limit, since, desk):
        db = DataBase()
        db_cur = db.get_object_cur()
        db_cur.execute(self.check_forum.format(slug=slug))
        forum_status = db_cur.fetchall()
        if not len(forum_status) :
            db.close()
            return tornado.escape.json_encode({
                "message": "Can`t find user with id #42\n"
            }), '404'

        db_cur = db.obj_reconnect()
        request = '''SELECT * FROM thread 
                     WHERE LOWER(thread.forum) = LOWER('{slug}') '''.format(slug=slug)

        if desk == 'true':
            request += '''{since}'''\
                .format(since=' AND thread.created <= ' + "'" + since + "'" if since != None else '')
        else:
            request += '''{since}''' \
                .format(since=' AND thread.created >= ' + "'" + since + "'" if since != None else '')

        request += ''' ORDER BY thread.created{desk_or_ask}{limit}'''\
            .format(limit=' LIMIT ' + limit if limit != None else '',
                    desk_or_ask=' DESC' if desk == 'true' else ' ASC')

        db_cur.execute(request)
        threads = db_cur.fetchall()
        for thread in threads:
            thread['created'] = datetime.isoformat(thread['created'])

        db.close()
        return tornado.escape.json_encode(threads), '200'



