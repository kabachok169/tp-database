import tornado.ioloop
import tornado.web
from src.routes import make_app

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
