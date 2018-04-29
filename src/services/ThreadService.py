from models import *
from DataBase import DataBase
import tornado.escape
import datetime


class ThreadService:
    def __init__(self):
        self.check_user = '''SELECT nickname FROM users 
                             WHERE LOWER(nickname) = LOWER('{nickname}');'''
        self.check_forum = '''SELECT  
                              CASE WHEN ( 
                              SELECT slug FROM forum 
                              WHERE LOWER(slug) = LOWER('{slug}')) 
                              IS NOT NULL THEN TRUE ELSE FALSE END AS "found_forum"'''
        self.check_thread = '''SELECT * 
                               FROM thread 
                               {cond}'''
        self.check_parent = '''SELECT * FROM messages 
                               WHERE messages.id = {id} AND messages.thread = {thread}'''


    def create_post(self, id, forum, date, data):
        author = data['author']

        if 'parent' not in data:
            data['parent'] = 0

        db = DataBase()
        db_cur = db.get_object_cur()

        db_cur.execute(self.check_user.format(nickname=author))
        user = db_cur.fetchone()

        if not user:
            db.close()
            return {
                "message": "Can`t find thread with id #42\n"
            }, '404'

        db_cur.execute(self.check_parent.format(id=data['parent'], thread=id))
        parent = db_cur.fetchone()

        if data['parent'] != 0:
            if not parent:
                db.close()
                return {
                    "message": "Can`t find parent with id #42\n"
                }, '409'

        db_cur.execute('''INSERT INTO usersForums (author, forum) 
                          SELECT '{author}', '{forum}' 
                          WHERE NOT EXISTS 
                          (SELECT forum FROM usersForums
                          WHERE LOWER(author) = LOWER('{author}') AND forum = '{forum}')'''
                       .format(author=author, forum=forum))
        db_cur = db.obj_reconnect(True)

        if parent:
            data['path'] = parent['path']
            data['path'].append(parent['id'])
        else:
            data['path'] = []

        path = ''
        for x in data['path']:
            path += str(x) + ','
        if len(path) > 1:
            path = path[:-1]

        db_cur.execute('''SELECT nextval(pg_get_serial_sequence('messages', 'id'))''')
        mid = db_cur.fetchone()

        db_cur.execute('''INSERT INTO messages (id, created, message, author, thread, forum, parent, path)
                          VALUES ({mid}, '{datetime}','{message}','{username}', {thread}, '{forum}', {parent},
                          array_append(ARRAY[{path}]::integer[], {mid})) RETURNING *;'''
                       .format(datetime=date, message=data['message'], username=author, thread=id,
                               parent=data['parent'], forum=forum, path=path, mid=mid['nextval']))
        post = db_cur.fetchone()
        # post['created'] = datetime.datetime.isoformat(post['created'])
        db.close()

        return post, '201'


    def create_posts(self, id, slug, datetime, data):

        db = DataBase()
        db_cur = db.get_object_cur()
        db_cur.execute(self.check_thread
                       .format(cond=' WHERE ' + 'thread.id = ' + id.__str__() if id != None else ' WHERE ' + 'LOWER(thread.slug) = ' + "LOWER('" + slug + "')"))
        thread = db_cur.fetchone()

        if not thread:
            db.close()
            return {
                "message": "Can`t find thread with id #42\n"
            }, '404'

        result = []

        for post in data:
            post, status = self.create_post(thread['id'], thread['forum'], datetime, post)
            if status == '404' or status == '409':
                return post, status
            result.append(post)

        return result, '201'


    def get_thread(self, id, slug):
        db = DataBase()
        db_cur = db.get_object_cur()
        db_cur.execute(self.check_thread
            .format(
            cond=' WHERE ' + 'thread.id = ' + id.__str__() if id != None else ' WHERE ' + 'LOWER(thread.slug) = ' + "LOWER('" + slug + "')"))
        thread = db_cur.fetchone()
        if not thread:
            db.close()
            return tornado.escape.json_encode({
                "message": "Can`t find thread with id #42\n"
            }), '404'
        db.close()
        thread['created'] = datetime.datetime.isoformat(thread['created'])
        return tornado.escape.json_encode(thread), '200'


    def update_thread(self, id, slug, data):
        if 'title' not in data.keys():
            title = None
        else:
            title = data['title']

        if 'message' not in data.keys():
            message = None
        else:
            message = data['message']

        db = DataBase()
        db_cur = db.get_object_cur()
        db_cur.execute(self.check_thread
            .format(
            cond=' WHERE ' + 'thread.id = ' + id.__str__() if id != None else ' WHERE ' + 'LOWER(thread.slug) = ' + "LOWER('" + slug + "')"))
        thread = db_cur.fetchone()
        if not thread:
            db.close()
            return tornado.escape.json_encode({
                "message": "Can`t find thread with id #42\n"
            }), '404'

        if not title and not message:
            db.close()
            thread['created'] = datetime.datetime.isoformat(thread['created'])
            return tornado.escape.json_encode(thread), '200'

        db_cur.execute(self.create_update_request(thread['id'], title, message))

        thread = db_cur.fetchone()

        db.close()
        thread['created'] = datetime.datetime.isoformat(thread['created'])
        return tornado.escape.json_encode(thread), '200'


    def vote(self, id, slug, data):
        db = DataBase()
        db_cur = db.get_object_cur()

        db_cur.execute(self.check_user.format(nickname=data['nickname']))
        user = db_cur.fetchone()

        if not user:
            db.close()
            return tornado.escape.json_encode({
                "message": "Can`t find thread with id #42\n"
            }), '404'


        db_cur.execute(self.check_thread
                       .format(
            cond=' WHERE ' + 'thread.id = ' + id.__str__() if id != None else ' WHERE ' + 'LOWER(thread.slug) = ' + "LOWER('" + slug + "')"))
        thread = db_cur.fetchone()
        if not thread:
            db.close()
            return tornado.escape.json_encode({
                "message": "Can`t find thread with id #42\n"
            }), '404'

        db_cur.execute('''SELECT * FROM votes
                       WHERE votes.thread={thread} AND votes.nickname='{nickname}';'''
                       .format(thread=thread['id'], nickname=data['nickname']))
        vote = db_cur.fetchone()

        if vote:
            if vote['voice'] + data['voice'] == 2 or vote['voice'] + data['voice'] == -2:
                db.close()
                thread['created'] = datetime.datetime.isoformat(thread['created'])
                return tornado.escape.json_encode(thread), '200'
            elif vote['voice'] + data['voice'] == 0:
                db_cur.execute('''UPDATE votes SET voice={voice}
                               WHERE votes.thread={thread} AND votes.nickname='{nickname}';'''
                               .format(thread=thread['id'], nickname=data['nickname'], voice=data['voice']))
                db.close()
                return self.update_vote_thread(thread['id'], 2 * data['voice']), 200
            else:
                db_cur.execute('''UPDATE votes SET voice={voice}
                               WHERE votes.thread={thread} AND votes.nickname='{nickname}';'''
                               .format(thread=thread['id'], nickname=data['nickname'], voice=data['voice']))
                db.close()
                return self.update_vote_thread(thread['id'], -vote['voice']), 200

        db_cur.execute('''INSERT INTO votes (voice, nickname, thread) VALUES ({voice}, '{nickname}', {thread})'''
                       .format(voice=data['voice'], nickname=data['nickname'], thread=thread['id']))
        db_cur = db.obj_reconnect(True)
        return self.update_vote_thread(thread['id'], data['voice']), 200


    def get_posts(self, id, slug, data):
        db = DataBase()
        db_cur = db.get_object_cur()
        db_cur.execute(self.check_thread
            .format(
            cond=' WHERE ' + 'thread.id = ' + id.__str__() if id != None else ' WHERE ' + 'LOWER(thread.slug) = ' + "LOWER('" + slug + "')"))
        thread = db_cur.fetchone()
        if not thread:
            db.close()
            return {"message": "Can`t find thread with id #42"}, '404'

        if data['sort'] == 'flat':
            db_cur.execute(self.create_flat_posts_request(thread['id'], data['since'], data['desc'], data['limit']))
            posts = db_cur.fetchall()
            # for post in posts:
            #     post['created'] = datetime.datetime.isoformat(post['created'])
            return posts, '200'
        elif data['sort'] == 'tree':
            db_cur.execute(self.create_tree_posts_request(thread['id'], data['since'], data['desc'], data['limit']))
            posts = db_cur.fetchall()
            # for post in posts:
            #     post['created'] = datetime.datetime.isoformat(post['created'])
            return posts, '200'
        elif data['sort'] == 'parent_tree':
            db_cur.execute(self.get_parents(thread['id'], data['since'], data['desc'], data['limit']))
            posts = []
            parents = db_cur.fetchall()
            for parent in parents:
                print(parent)
                db_cur.execute(
                    self.create_parent_tree_posts_request(thread['id'], data['since'],
                                                          data['desc'], parent['id']))
                children = db_cur.fetchall()
                print(children)
                posts.extend(children)

            # for post in posts:
            #     post['created'] = datetime.datetime.isoformat(post['created'])
            return posts, '200'


    def create_flat_posts_request(self, thread, since, desc, limit):
        request = '''SELECT * FROM messages 
                     WHERE thread = {thread} '''\
                    .format(thread=thread)

        if desc == 'false':
            request += '''{since}''' \
                .format(since=' AND id > ' + since if since != None else '')
        else:
            request += '''{since}''' \
                .format(since=' AND id < ' + since if since != None else '')

        request += ''' ORDER BY created {desk_or_ask} ,id {desk_or_ask}{limit}''' \
            .format(limit=' LIMIT ' + limit if limit != None else '',
                    desk_or_ask='ASC' if desc == 'false' else 'DESC')
        return request


    def create_tree_posts_request(self, thread, since, desc, limit):
        request = '''SELECT * FROM messages 
                     WHERE thread = {thread} '''\
                    .format(thread=thread)

        if desc == 'false':
            request += '''{since}''' \
                .format(since=' AND path > (SELECT path FROM messages WHERE id = ' + since + ')' if since != None else '')
        else:
            request += '''{since}''' \
                .format(since=' AND path < (SELECT path FROM messages WHERE id = ' + since + ')' if since != None else '')

        request += ''' ORDER BY path {desk_or_ask} {limit}''' \
            .format(limit='LIMIT ' + limit if limit != None else '',
                    desk_or_ask='ASC' if desc == 'false' else 'DESC')
        return request


    def create_parent_tree_posts_request(self, thread, since, desc, parent):
        request = '''SELECT * FROM messages 
                     WHERE thread = {thread} AND path[1] = {parent} '''\
                    .format(thread=thread, parent=parent)

        if desc == 'false':
            request += '''{since}''' \
                .format(since=' AND path[1] > (SELECT path[1] FROM messages WHERE id = ' + since + ')' if since != None else '')
        else:
            request += '''{since}''' \
                .format(since=' AND path[1] < (SELECT path[1] FROM messages WHERE id = ' + since + ')' if since != None else '')

        request += ''' ORDER BY path, id;''' \
            .format(desk_or_ask='ASC' if desc == 'false' else 'DESC')
        return request


    def get_parents(self, thread, since, desc, limit):
        request = '''SELECT id FROM messages 
                     WHERE thread = {thread} AND parent = 0 '''\
                    .format(thread=thread)

        if desc == 'false':
            request += '''{since}''' \
                .format(since=' AND path[1] > (SELECT path[1] FROM messages WHERE id = ' + since + ')' if since != None else '')
        else:
            request += '''{since}''' \
                .format(since=' AND path[1] < (SELECT path[1] FROM messages WHERE id = ' + since + ')' if since != None else '')

        request += ''' ORDER BY id {desk_or_ask} {limit}''' \
            .format(limit='LIMIT ' + limit if limit != None else '',
                    desk_or_ask='ASC' if desc == 'false' else 'DESC')
        return request


    def update_vote_thread(self, thread, vote):
        db = DataBase()
        db_cur = db.get_object_cur()
        db_cur.execute('''UPDATE thread SET votes=votes+{voice}
                       WHERE thread.id={thread} RETURNING *;'''
                       .format(thread=thread, voice=vote))
        thread = db_cur.fetchone()
        thread['created'] = datetime.datetime.isoformat(thread['created'])
        db.close()
        return thread


    def create_update_request(self, id, title, message):
        request = '''UPDATE thread SET '''
        if title != None:
            request += '''title='{title}','''.format(title=title)
        if message != None:
            request += '''message='{message}','''.format(message=message)

        request = request[:-1]
        request += ' '
        request += '''WHERE id = {id} RETURNING *;'''.format(id=id)
        return request


