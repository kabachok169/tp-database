import psycopg2

f = open('./drop.sql', 'r')

connection = psycopg2.connect(database="anton", user="anton", password="12345", host="127.0.0.1", port="5432")
db_cur = connection.cursor()
db_cur.execute(f.read())

connection.commit()
connection.close()


f = open('./schema.sql', 'r')

connection = psycopg2.connect(database="anton", user="anton", password="12345", host="127.0.0.1", port="5432")
db_cur = connection.cursor()
db_cur.execute(f.read())

connection.commit()
connection.close()

print('success')