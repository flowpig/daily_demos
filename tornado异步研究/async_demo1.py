#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
Tornado默认在函数处理返回时关闭客户端的连接。在通常情况下，这正是你想要的。
但是当我们处理一个需要回调函数的异步请求时，我们需要连接保持开启状态直到回调函数执行完毕。
你可以在你想改变其行为的方法上面使用 @tornado.web.asynchronous装饰器来告诉Tornado保持连接开启.

class IndexHandler(tornado.web.RequestHandler):
        @tornado.web.asynchronous
        def get(self):
            query = self.get_argument('q')
            fetch() ----- 异步回调
            [... other request handler code here...]     
            
记住当你使用 @tornado.web.asynchonous装饰器时，Tornado永远不会自己关闭连接。
你必须在你的RequestHandler对象中调用 finish方法来显式地告诉Tornado关闭连接。
（否则，请求将可能挂起(夯住)，浏览器可能不会显示我们已经发送给客户端的数据。）
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
        res1 = client.fetch("https://www.python.org", callback=self.on_response)
        print res1

    def on_response(self,res):
        count = len(res.body)
        print count
        self.write(str(count))
        self.finish()   #立即返回http请求结果，但代码往下继续执行,下面代码不能有self.write,因为self.finish是关闭tornado连接(请求连接)
        print 1111

if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[(r"/", IndexHandler)])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

'''
执行结果:

48860
1111
HTTPResponse(_body='<!doctype html>...)
'''