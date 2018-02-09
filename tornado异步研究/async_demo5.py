#!/usr/bin/env python
#-*- coding:utf-8 -*-

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient
import tornado.gen
import time


from tornado.options import define, options
define("port", default=8000, help="run on the given port", type=int)


class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        begin = time.clock()
        self.write('success')
        self.finish()
        http_client = tornado.httpclient.AsyncHTTPClient()
        res_dict = yield {"python":http_client.fetch("https://www.python.org")\
            , "github":http_client.fetch("https://github.com")}
        print time.clock() - begin
        result_count1 = len(res_dict["python"].body)
        result_count2 = len(res_dict["github"].body)
        print '%s %s' % (result_count1, result_count2)


if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[(r"/", IndexHandler)])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()