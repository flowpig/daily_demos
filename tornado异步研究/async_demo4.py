#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
tornado.concurrent.run_on_executor  让tornado多线程(异步无阻塞)方法执行耗时任务,
和async_demo3里面的tornado.httpclient.AsyncHTTPClient()一样的都是异步执行。
主要是这个handler执行耗时任务时，其它handler的访问不受影响。
可以把 装饰器  @tornado.concurrent.run_on_executor注释掉测试其它访问是否不受影响。
'''

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient
import tornado.gen
import time
import requests
from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor

from tornado.options import define, options

define("port", default=8000, help="run on the given port", type=int)


class IndexHandler(tornado.web.RequestHandler):
    executor = ThreadPoolExecutor(5)

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        begin = time.clock()
        res1 = yield self.fetch("https://www.python.org")
        res2 = yield self.fetch("https://github.com")
        print time.clock() - begin
        self.write('success')
        self.finish()
        result_count1 = len(res1.text)
        result_count2 = len(res2.text)
        print '%s %s' % (result_count1, result_count2)

    @tornado.concurrent.run_on_executor
    def fetch(self, url):
        time.sleep(5)
        res = requests.get(url)
        return res


class HelloHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("hello world!")


if __name__ == '__main__':
    tornado.options.parse_command_line()
    app = tornado.web.Application(handlers=[(r"/", IndexHandler), (r"/hello", HelloHandler)])
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()