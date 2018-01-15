#!/usr/bin/env python
#-*- coding:utf-8 -*-

'''
默认情况下，redis-py每次在执行请求时都会创建和断开一次连接操作(连接池申请连接，归还连接池),
如果想要在一次请求中执行多个命令，则可以使用pipline实现一次请求执行多个命令，并且默认
情况下pipline是原子性操作。

原子性操作：语句全部成功才成功，好比你给别人转钱，要么转钱失败，要么成功，不会存在你扣钱，但别人没加钱。
redis的每个指令都是原子性的。
'''

import redis

pool = redis.ConnectionPool(host='192.168.138.135',port=6379)
rsock = redis.Redis(connection_pool=pool)

# pipe = rsock.pipeline(transaction=False)
pipe = rsock.pipeline(transaction=True)

rsock.set('name','Tony')
rsock.set('hobby','haircut')

pipe.execute()

print(rsock.get('hobby'))