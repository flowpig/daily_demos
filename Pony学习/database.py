#!/usr/bin/env python
#-*- coding:utf-8 -*-

from functools import wraps
import pony.orm as pny


def singleton(cls):
    instances = {}

    @wraps(cls)
    def getinstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return getinstance


@singleton
class PonyDatabase(pny.Database):
    """
    将pony的Database改为单例
    """

    def __init__(self, *args, **kwargs):
        pny.Database.__init__(self,*args,**kwargs)