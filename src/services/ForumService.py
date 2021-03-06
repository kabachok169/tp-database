from DataBase import DataBase, db_cur, db
import tornado.escape
from models import *


class ForumService:
    def __init__(self, db_cur=db_cur):
        self.db_cur = db_cur
        self.check_user = '''SELECT * FROM users 
                             WHERE LOWER(nickname) = LOWER('{nickname}');'''
        self.check_forum = '''SELECT * FROM forum 
                              WHERE LOWER(slug) = LOWER('{slug}')'''
        self.check_slug = '''SELECT *
                             FROM thread 
                             WHERE LOWER(thread.slug) = LOWER('{slug}');'''

    def create_forum(self, slug, title, user_name):
        self.db_cur.execute(self.check_user.format(nickname=user_name))
        user_status = self.db_cur.fetchone()

        if not user_status:
            return tornado.escape.json_encode({
                "message": "Can`t find user with id #42\n"
            }), '404'
        else:
            user_name = user_status['nickname']

        self.db_cur.execute(self.check_forum.format(slug=slug))
        forum_status = self.db_cur.fetchone()

        if forum_status:
            db.close()
            forum_status['user'] = forum_status['author']
            return tornado.escape.json_encode(forum_status), '409'

        self.db_cur.execute('''INSERT INTO forum (slug, title, author) VALUES ('{slug}','{title}', '{username}') RETURNING *;'''
                       .format(slug=slug, title=title, username=user_name))
        forum = self.db_cur.fetchone()
        forum['user'] = forum['author']
        db.obj_reconnect(True)
        return tornado.escape.json_encode(forum), '201'

    def create_thread(self, forum, author, created, message, title, slug):
        # db = DataBase()
        # db_cur = db.get_object_cur()
        self.db_cur.execute('''SELECT nickname FROM users WHERE LOWER(users.nickname) = LOWER('{author}');'''
                       .format(author=author))
        author = self.db_cur.fetchone()

        self.db_cur.execute(self.check_forum.format(slug=forum))
        forum_status = db_cur.fetchone()
        if not author or not forum_status:
            db.close()
            return tornado.escape.json_encode({
                "message": "Can`t find user with id #42\n"
            }), '404'

        self.db_cur.execute('''INSERT INTO usersForums (author, forum) 
                      SELECT '{author}', '{forum}' 
                      WHERE NOT EXISTS 
                      (SELECT forum FROM usersForums
                      WHERE LOWER(author) = LOWER('{author}') AND forum = '{forum}')'''
                   .format(author=author['nickname'], forum=forum_status['slug']))
        db.obj_reconnect(True)

        if slug != None:
            self.db_cur.execute(self.check_slug.format(slug=slug))
            thread_status = self.db_cur.fetchall()
            if len(thread_status):
                thread_status[0]['created'] = datetime.isoformat(thread_status[0]['created'])
                return tornado.escape.json_encode(thread_status[0]), '409'

        self.db_cur.execute('''INSERT INTO thread (created, message, title, author, forum{is_slug})
                       VALUES ('{created_on}', '{message}', '{title}', '{author}', '{forum}'{slug}) RETURNING *;'''
                       .format(is_slug=', slug' if slug != None else '',
                               created_on=created, message=message, title=title, author=author['nickname'],
                               forum=forum_status['slug'],
                               slug=", '" + slug + "'" if slug != None else ''))
        thread = self.db_cur.fetchone()
        thread['created'] = datetime.isoformat(thread['created'])
        db.obj_reconnect(True)

        return tornado.escape.json_encode(thread), '201'

    def get_forum(self, slug):
        self.db_cur.execute('''SELECT * FROM forum WHERE LOWER(forum.slug) = LOWER('{slug}');'''.format(slug=slug))
        forum = self.db_cur.fetchone()
        if not forum:
            db.close()
            return tornado.escape.json_encode({
                "message": "Can`t find user with id #42\n"
            }), '404'
        self.db_cur.execute('''SELECT COUNT(*) FROM thread
                          WHERE LOWER(thread.forum) = LOWER('{slug}');'''.format(slug=slug))
        forum.update({'threads': db_cur.fetchone()['count']})

        self.db_cur.execute('''SELECT COUNT(*) FROM messages
                                  WHERE LOWER(messages.forum) = LOWER('{slug}');'''.format(slug=slug))
        forum.update({'posts': self.db_cur.fetchone()['count']})
        forum['user'] = forum['author']

        return tornado.escape.json_encode(forum), '200'

    def get_threads(self, slug, limit, since, desk):
        self.db_cur.execute(self.check_forum.format(slug=slug))
        forum_status = self.db_cur.fetchall()
        if not len(forum_status) :
            return tornado.escape.json_encode({
                "message": "Can`t find user with id #42\n"
            }), '404'

        db.obj_reconnect()
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

        self.db_cur.execute(request)
        threads = self.db_cur.fetchall()
        for thread in threads:
            thread['created'] = datetime.isoformat(thread['created'])

        return tornado.escape.json_encode(threads), '200'

    def get_users(self, slug, limit, since, desk):
        self.db_cur.execute(self.check_forum.format(slug=slug))
        forum_status = self.db_cur.fetchall()
        if not len(forum_status):
            db.close()
            return tornado.escape.json_encode({
                "message": "Can`t find user with id #42\n"
            }), '404'

        db.obj_reconnect()
        request = '''SELECT nickname, fullname, about, email FROM users u
                     JOIN usersForums t ON LOWER(u.nickname) = LOWER(t.author)
                     WHERE LOWER(t.forum) = LOWER('{slug}')'''\
                     .format(slug=slug)

        if desk == 'true':
            request += '''{since}'''\
                .format(since=' AND LOWER(u.nickname) < ' + "LOWER('" + since + "')" if since != None else '')
        else:
            request += '''{since}''' \
                .format(since=' AND LOWER(u.nickname) > ' + "LOWER('" + since + "')" if since != None else '')

        request += ''' ORDER BY LOWER(u.nickname){desk_or_ask}{limit}'''\
            .format(limit=' LIMIT ' + limit if limit != None else '',
                    desk_or_ask=' DESC' if desk == 'true' else ' ASC')

        self.db_cur.execute(request)
        users = self.db_cur.fetchall()

        return tornado.escape.json_encode(users), '200'



