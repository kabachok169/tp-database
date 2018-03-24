from .UserService import *
from .ForumService import *
import psycopg2


connection = psycopg2.connect(database="anton", user="anton", password="12345", host="127.0.0.1", port="5432")
db_cur = connection.cursor()

    # print("Unable to connect to the database")
