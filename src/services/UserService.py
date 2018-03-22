from ..models import *
# from src.services import *
import psycopg2


class UserService:

    def create_user(self, nickname, about, email, fullname):
        connection = psycopg2.connect(database="anton", user="anton", password="12345", host="127.0.0.1", port="5432")
        db_cur = connection.cursor()

        try:
            db_cur.execute('''INSERT INTO "user" (nickname, about, email, fullname) VALUES ('{nickname}', '{about}', '{email}', '{fullname}');'''
                           .format(nickname=nickname, about=about, email=email, fullname=fullname))
            connection.commit()
            connection.close()
            return 'Successfully created an user'
        except:
            connection.close()
            connection = psycopg2.connect(database="anton", user="anton", password="12345", host="127.0.0.1",
                                          port="5432")
            db_cur = connection.cursor()
            db_cur.execute('''SELECT * FROM "user" WHERE "user".nickname = '{nickname}';'''.format(nickname=nickname))
            user = db_cur.fetchall()
            connection.commit()
            connection.close()
            user_model = UserModel(user[0][1], user[0][2], user[0][3], user[0][4])
            return user_model.read()
