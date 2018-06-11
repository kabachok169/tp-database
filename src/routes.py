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
        (r"/forum/(?P<slug>[^/]+?)/users", ForumUsersHandler),

        (r"/thread/(?P<slug_or_id>[^/]+?)/create", ThreadPostCreationHandler),
        (r"/thread/(?P<slug_or_id>[^/]+?)/details", ThreadDetailsHandler),
        (r"/thread/(?P<slug_or_id>[^/]+?)/posts", ThreadPostsHandler),
        (r"/thread/(?P<slug_or_id>[^/]+?)/vote", ThreadVoteHandler),

        (r"/post/(?P<id>[^/]+?)/details", PostDetailsHandler),

        (r"/service/clear", ServiceClearHandler),
        (r"/service/status", ServiceStatusHandler),
    ])