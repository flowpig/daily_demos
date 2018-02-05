#!/usr/bin/env python
#-*- coding:utf-8 -*-
'''
1.在程序创建连接的时候，可以从一个空闲的连接中获取，不需要重新初始化连接，提升获取连接的速度
2.关闭连接的时候，把连接放回连接池，而不是真正的关闭，所以可以减少频繁地打开和关闭连接
'''

import pymysql
from DBUtils.PooledDB import PooledDB
pool = PooledDB(pymysql,5,host="127.0.0.1",user="root",passwd="",db="books",port=3306,charset="utf8")
conn = pool.connection()
cur = conn.cursor()
sql = "select * from app01_book"
cur.execute(sql)
res = cur.fetchall()
print(res)
cur.close()
conn.close()