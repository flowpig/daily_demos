#!/usr/bin/env python
#-*- coding:utf-8 -*-
import time

class TimeSpendCount(object):
    """
    时间统计上下文管理器
    """

    def __init__(self, msg, logger, console=False):
        self.msg = msg
        self.logger = logger
        self.console = console

    def __enter__(self):
        self.begin = time.clock()

    def __exit__(self, e_t, _e_v, t_b):
        self.end = time.clock()
        success = "false" if e_t else "true"
        self.logger.info("[%s] cost:%.4fs, func:%s, success:%s" % (self.msg, self.end - self.begin, "none", success))
        if self.console:
            print("[%s] cost:%.4fs, func:%s, success:%s" % (self.msg, self.end - self.begin, "none", success))