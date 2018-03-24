from ..models import *
from src.DataBase import DataBase
import json


class UserService:
    def __init__(self):
        self.check_user = '''SELECT 
                             CASE WHEN ( 
                             SELECT nickname FROM users 
                             WHERE LOWER(nickname) <> LOWER('{nickname}') AND LOWER(email) = LOWER('{email}') 
                             ) 
                             IS NOT NULL THEN TRUE ELSE FALSE END AS "conflict", 
                             CASE WHEN ( 
                             SELECT nickname FROM users 
                             WHERE LOWER(nickname) = LOWER('{nickname}')) 
                             IS NOT NULL THEN TRUE ELSE FALSE END AS "found"'''

    def create_user(self, nickname, about, email, fullname):
        db = DataBase()
        db_cur = db.get_cursor()
        db_cur.execute(self.check_user.format(nickname=nickname, email=email))
        user_status = db_cur.fetchall()

        if not user_status[0][0] and not user_status[0][1]:
            db_cur.execute('''INSERT INTO users (nickname, about, email, fullname) VALUES 
                           ('{nickname}', '{about}', '{email}', '{fullname}');'''
                           .format(nickname=nickname, about=about, email=email, fullname=fullname))
            db_cur.execute('''SELECT * FROM users WHERE users.nickname = '{nickname}';'''
                           .format(nickname=nickname))
            user = db_cur.fetchall()
            db.close()
            user_model = UserModel(user[0][1], user[0][2], user[0][3], user[0][4])
            return user_model.read(), '201'

        elif user_status[0][1] or user_status[0][0]:
            db_cur = db.reconnect()
            result = []
            if user_status[0][1]:
                db_cur.execute('''SELECT * FROM users WHERE users.nickname = '{nickname}';'''
                               .format(nickname=nickname))
                user = db_cur.fetchall()
                db.close()
                user_model = UserModel(user[0][1], user[0][2], user[0][3], user[0][4])
                result.append(user_model.read())

            if user_status[0][0]:
                db_cur.execute('''SELECT * FROM users WHERE users.email = '{email}';'''
                               .format(email=email))
                user = db_cur.fetchall()
                db.close()
                user_model = UserModel(user[0][1], user[0][2], user[0][3], user[0][4])
                result.append(user_model.read())

            return result.__str__(), '409'

    def update_user(self, nickname, about, email, fullname):
        db = DataBase()
        db_cur = db.get_cursor()
        db_cur.execute(self.check_user.format(nickname=nickname, email=email))
        user_status = db_cur.fetchall()

        if not user_status[0][0] and user_status[0][1]:
            db_cur.execute('''UPDATE users SET about = '{about}', email = '{email}', fullname = '{fullname}' WHERE nickname = '{nickname}';'''
                           .format(nickname=nickname, about=about, email=email, fullname=fullname))
            db_cur.execute('''SELECT * FROM users WHERE users.nickname = '{nickname}';'''
                           .format(nickname=nickname))
            user = db_cur.fetchall()
            db.close()
            user_model = UserModel(user[0][1], user[0][2], user[0][3], user[0][4])
            return user_model.read(), '200'

        elif user_status[0][0] or not user_status[0][1]:
            db_cur = db.reconnect()
            result = []
            if not user_status[0][1]:
                return json.dumps({
                    "message": "Can`t find user with id #42\n"
                }), '404'

            if user_status[0][0]:
                return json.dumps({
                    "message": "Can`t change #42\n"
                }), '409'

    def get_user(self, nickname):
        db = DataBase()
        db_cur = db.get_cursor()
        db_cur.execute('''SELECT * FROM users WHERE users.nickname = '{nickname}';'''
                       .format(nickname=nickname))
        user = db_cur.fetchall()
        if len(user) == 0:
            return json.dumps({
                "message": "Can`t find user with id #42\n"
            }), '404'
        else:
            user_model = UserModel(user[0][1], user[0][2], user[0][3], user[0][4])
            return user_model.read(), '200'



