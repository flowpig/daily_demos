#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
程序运行日志记录
"""

import logging
from settings import BASE_DIR
import os
from cloghandler import ConcurrentRotatingFileHandler as LogHandler
import platform
from raven import Client

# windows上ConcurrentRotatingFileHandler这个handler会有导致程序卡死问题，linux上无问题
# 暂时采用这种方法解决windows上因卡死导致的调试不方便问题
if str(platform.system()) == "Windows":
    from logging.handlers import RotatingFileHandler as LogHandler

_log_file_size = 1 * 1024 * 1024 * 1024  # 1G

# -------------------------------运行日志（代码运行记录）-------------------------------
_code_log_file = os.path.join(BASE_DIR, 'logs', 'code.log')

_code_log_handler = LogHandler(_code_log_file, "a", _log_file_size, 1000)
_code_log_formatter = logging.Formatter('%(levelname)s %(asctime)s %(pathname)s->func:%(funcName)s '
                                        'line:%(lineno)d %(message)s')
_code_log_handler.setFormatter(_code_log_formatter)
# 此处设置logger名称，否则默认的会和tornado的logger相同而使得下方设置的错误等级被更新为info
code_log = logging.getLogger('code-log')
code_log.setLevel(logging.INFO)
code_log.addHandler(_code_log_handler)

# -------------------------------Sentry网络日志系统--------------------------------
sentry_log = Client('http://2fc91ef661e2410c979b8b550fc7015d:dada6e7bb70a453a8fb4a4a1d45edc02@10.51.30.4/2')

# -------------------------------数据日志（用于存库异常时，存放已经获取到的原始数据）--------------------------------
_data_log_file = os.path.join(BASE_DIR, 'logs', 'data.log')
_data_log_handler = LogHandler(_data_log_file, "a", _log_file_size, 1000)
_data_log_formatter = logging.Formatter('%(asctime)s:%(module)s->%(filename)s->%(lineno)d\n'
                                        'data:%(message)s')
_data_log_handler.setFormatter(_data_log_formatter)
data_log = logging.getLogger('data-log')
data_log.setLevel(logging.INFO)
data_log.addHandler(_data_log_handler)

# -------------------------------访问日志（记录访问的url和body）----------------------------------------
_access_log_file = os.path.join(BASE_DIR, 'logs', 'access.log')
_access_log_handler = LogHandler(_access_log_file, "a", _log_file_size, 1000)
_access_log_formatter = logging.Formatter('%(asctime)s:%(message)s')
_access_log_handler.setFormatter(_access_log_formatter)
_access_log = logging.getLogger('access-log')
_access_log.setLevel(logging.INFO)
_access_log.addHandler(_access_log_handler)

# -------------------------------文集日志（记录对文件的操作）----------------------------------------
_file_log_file = os.path.join(BASE_DIR, 'logs', 'operation_file.log')
_file_log_handler = LogHandler(_file_log_file, "a", _log_file_size, 1000)
_file_log_formatter = logging.Formatter('[%(asctime)-18s:%(levelname)8s]:%(message)s')
_file_log_handler.setFormatter(_file_log_formatter)
file_operation_log = logging.getLogger('file-operation-log')
file_operation_log.setLevel(logging.INFO)
file_operation_log.addHandler(_file_log_handler)


def log_request(handler):
    if handler.get_status() < 400:
        log_method = _access_log.info
    elif handler.get_status() < 500:
        log_method = _access_log.warning
    else:
        log_method = _access_log.error

    request = handler.request
    request_time = 1000 * request.request_time()

    format_str = "%d %dms %s %s %s"

    # 依次为：status, method, uri, ip, time_spend
    values = (handler.get_status(), request_time, request.method, request.uri, request.remote_ip)
    log_method(format_str % values)