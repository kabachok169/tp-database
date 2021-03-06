import psycopg2
import psycopg2.extras

class DataBase:
    def __init__(self):
        self.db = psycopg2.connect(database="anton", user="anton", password="12345", host="127.0.0.1", port="5432")

    def get_cursor(self):
        return self.db.cursor()

    def reconnect(self, need_commit=False):
        if need_commit:
            self.db.commit()
        # self.db.close()
        # self.db = psycopg2.connect(database="anton", user="anton", password="12345", host="127.0.0.1", port="5432")
        return self.get_cursor()

    def obj_reconnect(self, need_commit=False):
        if need_commit:
            self.db.commit()
        # self.db.close()
        # self.db = psycopg2.connect(database="anton", user="anton", password="12345", host="127.0.0.1", port="5432")
        # return self.db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)


    def close(self):
        self.db.commit()
        # self.db.close()

    def get_object_cur(self):
        return self.db.cursor(cursor_factory = psycopg2.extras.RealDictCursor)


db = DataBase()
db_cur = db.get_object_cur()

