import tornado.web
from src.handlers import *


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),

        (r"/api/user/(?P<nickname>[^/]+?)/create", UserCreationHandler),
        (r"/api/user/(?P<nickname>[^/]+?)/profile", UserProfileHandler),

        (r"/api/forum/create", ForumCreationHandler),
        (r"/api/forum/(?P<slug>[^/]+?)/create", ForumSlugCreationHandler),
    ])