#!/usr/bin/env python
#-*- coding:utf-8 -*-

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient
import tornado.gen

from tornado.options import define, options

define("port", default=8000, help="run on the given port", type=int)


class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        http_client = tornado.httpclient.AsyncHTTPClient()
        res1 = yield http_client.fetch("https://www.python.org")
        res2 = yield http_client.fetch("https://github.com")
        self.write('success')
        self.finish()
        result_count1 = len(res1.body)
        result_count2 = len(res2.body)
        print '%s %s' % (result_count1, result_count2)


class HelloHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("hello world!")


if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[(r"/", IndexHandler), (r"/hello", HelloHandler)])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()