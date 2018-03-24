import tornado.web
from src.handlers import *


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),

        (r"/user/(?P<nickname>[^/]+?)/create", UserCreationHandler),
        (r"/user/(?P<nickname>[^/]+?)/profile", UserProfileHandler),

        (r"/forum/create", ForumCreationHandler),
    ])