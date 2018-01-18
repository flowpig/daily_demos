#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
# print bytes(BASE_DIR).decode(encoding='gbk')


#tornado配置
TORNADO_SETTING = {
    'debug': True,
    "cookie_secret": "asdkaskkdaksk",  # Cookie secret
    "xsrf_cookies": False,  # 跨域安全
    "gzip": False,  # 关闭gzip输出
}
