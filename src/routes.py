import tornado.web
from handlers import *


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),

        (r"/api/user/(?P<nickname>[^/]+?)/create", UserCreationHandler),
        (r"/api/user/(?P<nickname>[^/]+?)/profile", UserProfileHandler),

        (r"/api/forum/create", ForumCreationHandler),
        (r"/api/forum/(?P<slug>[^/]+?)/create", ForumSlugCreationHandler),
        (r"/api/forum/(?P<slug>[^/]+?)/details", ForumInfoHandler),
        (r"/api/forum/(?P<slug>[^/]+?)/threads", ForumThreadsHandler),
        (r"/api/forum/(?P<slug>[^/]+?)/users", ForumUsersHandler),

        (r"/api/thread/(?P<slug_or_id>[^/]+?)/create", ThreadPostCreationHandler),
        (r"/api/thread/(?P<slug_or_id>[^/]+?)/details", ThreadDetailsHandler),
        (r"/api/thread/(?P<slug_or_id>[^/]+?)/posts", ThreadPostsHandler),
        (r"/api/thread/(?P<slug_or_id>[^/]+?)/vote", ThreadVoteHandler),

        (r"/api/post/(?P<id>[^/]+?)/details", PostDetailsHandler),

        (r"/api/service/clear", ServiceClearHandler),
        (r"/api/service/status", ServiceStatusHandler),


    ])