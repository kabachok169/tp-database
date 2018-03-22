import tornado.web


class UserHandler(tornado.web.RequestHandler):
    def get(self, nickname):
        self.write("Hello, {user}!".format(user=nickname))

    def post(self, nickname):
        self.set_header("Content-type", "text/plain")
        self.write('Hello, {user}!You wrote {message}'.format(user=nickname, message=self.get_argument("message")))


