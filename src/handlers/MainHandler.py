import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('<html><body><form action="/user/kabachok/create" method="post">'
                       '<input type="text" name="message">'
                       '<input type="submit" value="Submit">'
                       '</form></body></html>')


