import tornado.web
from src.handlers import *


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),

        (r"/user/(?P<nickname>[^/]+?)/create", UserCreationHandler),
        (r"/user/(?P<nickname>[^/]+?)/profile", UserProfileHandler),

        (r"/forum/create", ForumCreationHandler),
        (r"/forum/(?P<slug>[^/]+?)/create", ForumSlugCreationHandler),
        (r"/forum/(?P<slug>[^/]+?)/details", ForumInfoHandler),
        (r"/forum/(?P<slug>[^/]+?)/threads", ForumThreadsHandler),

        (r"/thread/(?P<id>[^/]+?)/create", ThreadPostCreationHandler),
        (r"/thread/(?P<id>[^/]+?)/details", ThreadDetailsHandler),

    ])