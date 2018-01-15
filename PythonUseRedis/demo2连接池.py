#!/usr/bin/env python
#-*- coding:utf-8 -*-

import redis

pool = redis.ConnectionPool(host='192.168.138.135',port=6379)
rsock = redis.Redis(connection_pool=pool)
rsock.set('key2','value2')
print(rsock.get('key2'))