#!/usr/bin/env python
#-*- coding:utf-8 -*-

import tornado.ioloop
import tornado.web
from tornado.options import define,options
import handler
from urls import url_handler
from settings import TORNADO_SETTING
from utils.logger import log_request,code_log


define("port", default=8010, help="run on the given port", type=int)
define("address", default="", help="run on the given host", type=str)


if __name__ == '__main__':
    options.parse_command_line()

    TORNADO_SETTING["log_function"] = log_request  # 重写访问日志信息
    app = tornado.web.Application(url_handler,**TORNADO_SETTING)
    app.listen(port=options.port,address=options.address)
    code_log.info("start up success")
    tornado.ioloop.IOLoop.instance().start()