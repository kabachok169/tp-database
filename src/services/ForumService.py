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
                             WHERE LOWER(title) = LOWER('{title}') AND LOWER(user_name) = LOWER('{username}')) 
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
            db_cur.execute('''SELECT * FROM forum WHERE LOWER(forum.title) = LOWER('{title}') AND LOWER(forum.user_name) = LOWER('{username}');'''
                           .format(title=title, username=user_name))
            forum = db_cur.fetchall()
            forum = ForumModel(forum[0][1], forum[0][2], forum[0][3])
            db.close()
            return forum.read(), '409'

        db_cur.execute('''INSERT INTO forum (slug, title, user_name) VALUES ('{slug}','{title}','{username}');'''
                       .format(slug=slug, title=title, username=user_name))
        db.reconnect(True)
        db_cur = db.get_cursor()
        db_cur.execute('''SELECT * FROM forum WHERE LOWER(forum.title) = LOWER('{title}') AND LOWER(forum.user_name) = LOWER('{username}');'''
                       .format(title=title, username=user_name))
        forum = db_cur.fetchall()
        forum = ForumModel(forum[0][1], forum[0][2], forum[0][3])
        db.close()
        return forum.read(), '201'

