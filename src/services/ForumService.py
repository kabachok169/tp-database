from ..models import *
from src.DataBase import DataBase
import json


class ForumService:
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

        if not user_status[0][0]:
            db.close()
            return json.dumps({
                "message": "Can`t find user with id #42\n"
            }), '404'

        db_cur.execute(self.check_forum.format(slug=slug))
        forum_status = db_cur.fetchall()

        if forum_status[0][0]:
            db_cur.execute('''SELECT * FROM forum WHERE forum.slug = '{slug}';'''
                           .format(slug=slug))
            forum = db_cur.fetchall()
            forum = ForumModel(forum[0][1], forum[0][2], forum[0][3])
            db.close()
            return forum.read(), '409'

        db_cur.execute('''INSERT INTO forum (slug, title, user_name) VALUES ('{slug}','{title}','{username}');'''
                       .format(slug=slug, title=title, username=user_name))
        db_cur = db.reconnect(True)
        db_cur.execute('''SELECT * FROM forum WHERE forum.slug = '{slug}';'''
                       .format(slug=slug))
        forum = db_cur.fetchall()
        forum = ForumModel(forum[0][1], forum[0][2], forum[0][3])
        db.close()
        return forum.read(), '201'

    def create_slug(self, slug, author, created, message, title):
        db = DataBase()
        db_cur = db.get_cursor()
        db_cur.execute('''SELECT id FROM users WHERE LOWER(users.nickname) = LOWER('{author}');'''
                       .format(author=author))
        author_id = db_cur.fetchall()

        db_cur.execute(self.check_forum.format(slug=slug))
        forum_status = db_cur.fetchall()
        if len(author_id) == 0 or not forum_status[0][0]:
            db.close()
            return json.dumps({
                "message": "Can`t find user with id #42\n"
            }), '404'

        db_cur.execute(self.check_slug.format(slug=slug, title=title))
        thread_status = db_cur.fetchall()
        if thread_status[0][0]:
            db_cur.execute('''SELECT users.nickname, thread.created_on, forum.title, thread.id, thread.message, thread.slug, thread.title
                              FROM thread 
                              JOIN users ON users.id = thread.author_id
                              JOIN forum ON forum.slug = thread.slug
                              WHERE LOWER(thread.slug) = LOWER('{slug}') AND LOWER(thread.title) = LOWER('{title}');'''
                           .format(slug=slug, title=title))
            thread = db_cur.fetchall()
            thread = SlugModel(thread[0][5], thread[0][1], thread[0][4], thread[0][6], thread[0][0], thread[0][2],
                               thread[0][3])
            db.close()
            return thread.read(), '409'

        db_cur.execute('''INSERT INTO thread (slug, created_on, message, title, author_id)
                       VALUES ('{slug}', '{created_on}', '{message}', '{title}', {author_id})'''
                       .format(slug=slug, created_on=created, message=message, title=title, author_id=author_id[0][0]))
        db_cur = db.reconnect(True)
        db_cur.execute('''SELECT users.nickname, thread.created_on, forum.title, thread.id, thread.message, thread.slug, thread.title
                          FROM thread 
                          JOIN users ON users.id = thread.author_id
                          JOIN forum ON forum.slug = thread.slug
                          WHERE LOWER(thread.slug) = LOWER('{slug}') AND LOWER(thread.title) = LOWER('{title}');'''
                       .format(slug=slug, title=title))
        thread = db_cur.fetchall()
        thread = SlugModel(thread[0][5], thread[0][1], thread[0][4], thread[0][6], thread[0][0], thread[0][2],
                           thread[0][3])
        db.close()
        return thread.read(), '201'





