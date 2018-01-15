#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
可能遇到报错: Redis is running in protected mode because protected mode is enabled
解决：  后台的redis服务器配置文件设置 protected-mode no

可能报错：Timeout超时
解决：测试端口连通性，排除网络故障，我这里未配置bind 所有
在redis服务器配置：bind 0.0.0.0

启动redis  指定配置文件：src/redis-server redis.conf

redis里面存储的为bytes格式，如果是python的字典列表等类型需要用json.dumps序列化为bytes再存储
'''

import redis

rsock = redis.Redis(host='192.168.138.135',port=6379)
rsock.set('key1','value1')
print(rsock.get('key1'))

