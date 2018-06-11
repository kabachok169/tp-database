from ..models import *
from src.DataBase import DataBase, db_cur, db
import tornado.escape
import datetime


class ThreadService:
    def __init__(self, db_cur=db_cur):
        self.db_cur = db_cur
        self.check_user = '''SELECT nickname FROM users 
                             WHERE LOWER(nickname) = LOWER('{nickname}') LIMIT 1;'''
        self.check_forum = '''SELECT  
                              CASE WHEN ( 
                              SELECT slug FROM forum 
                              WHERE LOWER(slug) = LOWER('{slug}') LIMIT 1)
                              IS NOT NULL THEN TRUE ELSE FALSE END AS "found_forum"'''
        self.check_thread = '''SELECT * 
                               FROM thread 
                               {cond} LIMIT 1'''
        self.check_slug_thread = '''SELECT * 
                                    FROM thread 
                                    WHERE LOWER(thread.slug) = "{slug}"
                                    LIMIT 1'''
        self.check_id_thread = '''SELECT * 
                                  FROM thread 
                                  WHERE thread.id = {id}
                                  LIMIT 1'''
        self.check_parent = '''SELECT * FROM messages 
                               WHERE messages.id = {id} AND messages.thread = {thread} LIMIT 1'''


    def create_post(self, id, forum, date, data):
        author = data['author']

        if 'parent' not in data:
            data['parent'] = 0

        self.db_cur.execute(self.check_user.format(nickname=author))
        user = self.db_cur.fetchone()

        if not user:
            db.close()
            return tornado.escape.json_encode({
                "message": "Can`t find thread with id #42\n"
            }), '404'

        self.db_cur.execute(self.check_parent.format(id=data['parent'], thread=id))
        parent = self.db_cur.fetchone()

        if data['parent'] != 0:
            if not parent:
                db.close()
                return tornado.escape.json_encode({
                    "message": "Can`t find parent with id #42\n"
                }), '409'

        self.db_cur.execute('''INSERT INTO usersForums (author, forum) 
                          SELECT '{author}', '{forum}' 
                          WHERE NOT EXISTS 
                          (SELECT forum FROM usersForums
                          WHERE LOWER(author) = LOWER('{author}') AND forum = '{forum}')'''
                       .format(author=author, forum=forum))
        db.obj_reconnect(True)

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

        self.db_cur.execute('''SELECT nextval(pg_get_serial_sequence('messages', 'id'))''')
        mid = self.db_cur.fetchone()

        self.db_cur.execute('''INSERT INTO messages (id, created, message, author, thread, forum, parent, path)
                          VALUES ({mid}, '{datetime}','{message}','{username}', {thread}, '{forum}', {parent},
                          array_append(ARRAY[{path}]::integer[], {mid})) RETURNING *;'''
                       .format(datetime=date, message=data['message'], username=author, thread=id,
                               parent=data['parent'], forum=forum, path=path, mid=mid['nextval']))
        post = self.db_cur.fetchone()
        post['created'] = datetime.datetime.isoformat(post['created'])

        return post, '201'


    def create_posts(self, id, slug, datetime, data):

        self.db_cur.execute(self.check_thread
                       .format(cond=' WHERE ' + 'thread.id = ' + id.__str__() if id != None else ' WHERE ' + 'LOWER(thread.slug) = ' + "LOWER('" + slug + "')"))
        thread = self.db_cur.fetchone()

        if not thread:
            return tornado.escape.json_encode({
                "message": "Can`t find thread with id #42\n"
            }), '404'

        result = []

        for post in data:
            post, status = self.create_post(thread['id'], thread['forum'], datetime, post)
            if status == '404' or status == '409':
                return post, status
            result.append(post)

        return tornado.escape.json_encode(result), '201'


    def get_thread(self, id, slug):
        self.db_cur.execute(self.check_thread
            .format(
            cond=' WHERE ' + 'thread.id = ' + id.__str__() if id != None else ' WHERE ' + 'LOWER(thread.slug) = ' + "LOWER('" + slug + "')"))
        thread = self.db_cur.fetchone()
        if not thread:
            return tornado.escape.json_encode({
                "message": "Can`t find thread with id #42\n"
            }), '404'
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

        self.db_cur.execute(self.check_thread
            .format(
            cond=' WHERE ' + 'thread.id = ' + id.__str__() if id != None else ' WHERE ' + 'LOWER(thread.slug) = ' + "LOWER('" + slug + "')"))
        thread = self.db_cur.fetchone()
        if not thread:
            return tornado.escape.json_encode({
                "message": "Can`t find thread with id #42\n"
            }), '404'

        if not title and not message:
            thread['created'] = datetime.datetime.isoformat(thread['created'])
            return tornado.escape.json_encode(thread), '200'

        self.db_cur.execute(self.create_update_request(thread['id'], title, message))

        thread = self.db_cur.fetchone()

        thread['created'] = datetime.datetime.isoformat(thread['created'])
        return tornado.escape.json_encode(thread), '200'


    def vote(self, id, slug, data):

        self.db_cur.execute(self.check_user.format(nickname=data['nickname']))
        user = self.db_cur.fetchone()

        if not user:
            return tornado.escape.json_encode({
                "message": "Can`t find thread with id #42\n"
            }), '404'

        if id:
            self.db_cur.execute(self.check_id_thread.format(id=id))
        else:
            self.db_cur.execute(self.check_slug_thread.format(slug=slug))

        thread = self.db_cur.fetchone()
        if not thread:
            return tornado.escape.json_encode({
                "message": "Can`t find thread with id #42\n"
            }), '404'

        self.db_cur.execute('''SELECT * FROM votes
                               WHERE votes.thread={thread} AND votes.nickname='{nickname}' LIMIT 1;'''
                               .format(thread=thread['id'], nickname=data['nickname']))
        vote = self.db_cur.fetchone()

        if not vote:
            self.db_cur.execute(
                '''INSERT INTO votes (voice, nickname, thread) VALUES ({voice}, '{nickname}', {thread})'''
                .format(voice=data['voice'], nickname=data['nickname'], thread=thread['id']))
            db.obj_reconnect(True)
            return self.update_vote_thread(thread['id'], data['voice']), 200

        sum = vote['voice'] + data['voice']

        if sum == 2 or sum == -2:
            thread['created'] = datetime.datetime.isoformat(thread['created'])
            return tornado.escape.json_encode(thread), '200'
        elif not sum:
            self.db_cur.execute('''UPDATE votes SET voice={voice}
                           WHERE votes.thread={thread} AND votes.nickname='{nickname}';'''
                           .format(thread=thread['id'], nickname=data['nickname'], voice=data['voice']))
            return self.update_vote_thread(thread['id'], 2 * data['voice']), 200
        else:
            self.db_cur.execute('''UPDATE votes SET voice={voice}
                           WHERE votes.thread={thread} AND votes.nickname='{nickname}';'''
                           .format(thread=thread['id'], nickname=data['nickname'], voice=data['voice']))
            return self.update_vote_thread(thread['id'], -vote['voice']), 200


    def get_posts(self, id, slug, data):

        self.db_cur.execute(self.check_thread
            .format(
            cond=' WHERE ' + 'thread.id = ' + id.__str__() if id != None else ' WHERE ' + 'LOWER(thread.slug) = ' + "LOWER('" + slug + "')"))
        thread = self.db_cur.fetchone()
        if not thread:
            return tornado.escape.json_encode({
                "message": "Can`t find thread with id #42\n"
            }), '404'

        if data['sort'] == 'flat':
            self.db_cur.execute(self.create_flat_posts_request(thread['id'], data['since'], data['desc'], data['limit']))
            posts = self.db_cur.fetchall()
            for post in posts:
                post['created'] = datetime.datetime.isoformat(post['created'])
            return tornado.escape.json_encode(posts), '200'
        elif data['sort'] == 'tree':
            self.db_cur.execute(self.create_tree_posts_request(thread['id'], data['since'], data['desc'], data['limit']))
            posts = self.db_cur.fetchall()
            for post in posts:
                post['created'] = datetime.datetime.isoformat(post['created'])
            return tornado.escape.json_encode(posts), '200'
        elif data['sort'] == 'parent_tree':
            self.db_cur.execute(self.get_parents(thread['id'], data['since'], data['desc'], data['limit']))
            posts = []
            parents = self.db_cur.fetchall()
            for parent in parents:
                print(parent)
                self.db_cur.execute(
                    self.create_parent_tree_posts_request(thread['id'], data['since'],
                                                          data['desc'], parent['id']))
                children = db_cur.fetchall()
                print(children)
                posts.extend(children)

            for post in posts:
                post['created'] = datetime.datetime.isoformat(post['created'])
            return tornado.escape.json_encode(posts), '200'


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
        self.db_cur.execute('''UPDATE thread SET votes=votes+{voice}
                       WHERE thread.id={thread} RETURNING *;'''
                       .format(thread=thread, voice=vote))
        thread = self.db_cur.fetchone()
        thread['created'] = datetime.datetime.isoformat(thread['created'])
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


