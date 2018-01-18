#!/usr/bin/env python
#-*- coding:utf-8 -*-

import handler

_url_handler_dic = {
    "base":[
        (r'^/index',handler.IndexHandler),
    ]
}


def init():
    url = []
    for k in _url_handler_dic:
        url += _url_handler_dic[k]
    return url


url_handler = init()