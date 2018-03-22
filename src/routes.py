import tornado.web
from src.handlers import *


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/user/(?P<nickname>[^/]+?)/create", UserHandler),
    ])