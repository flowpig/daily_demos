#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
如下代码是为了引出tornado2.1版本后的tornado.gen模块，
这个模块能够使的异步代码更加整洁，而不像下面这样。请参考async_demo3
'''

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient
import time

from tornado.options import define, options

define("port", default=8000, help="run on the given port", type=int)


class IndexHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        begin = time.clock()
        client = tornado.httpclient.AsyncHTTPClient()
        res1 = client.fetch("https://www.python.org", callback=self.on_response1)
        res1 = client.fetch("https://github.com", callback=self.on_response2)


    def on_response1(self,res):
        count = len(res.body)
        print count
        self.write(str(count) + '\r\n')

    def on_response2(self,res):
        count = len(res.body)
        print count
        self.write(str(count) + '\r\n')
        print time.clock()
        self.finish()

if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[(r"/", IndexHandler)])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

'''
时间花费（比sync_demo花费短）：
1.24427765577
'''