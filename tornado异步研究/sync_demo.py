#!/usr/bin/env python
# -*- coding:utf-8 -*-

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient
import time

from tornado.options import define, options

define("port", default=8000, help="run on the given port", type=int)


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        begin = time.clock()
        client = tornado.httpclient.HTTPClient()
        res1 = client.fetch("https://www.python.org")
        res2 = client.fetch("https://github.com")
        result_count1 = len(res1.body)
        result_count2 = len(res2.body)
        end = time.clock()
        self.write(
            """<div style="text-align: center">
                    <div style="font-size: 72px">%s</div>
                    <div style="font-size: 72px">%s</div>
                    <div style="font-size: 72px">花费%s</div>
                </div>""" % (result_count1, result_count2, end - begin))
if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[(r"/", IndexHandler)])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

'''
48860
51529
花费2.17657208466
'''