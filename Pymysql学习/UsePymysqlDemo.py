#!/usr/bin/env python
#-*- coding:utf-8 -*-
import pymysql
#连接数据库
conn = pymysql.connect(host='127.0.0.1',port=3306,user='root',passwd='',db='books')
#创建游标
cur = conn.cursor()

#插入一条数据
# ret = cur.execute('insert into app01_book(title,price,publish_id) VALUE(%s,%s,%s)',("PHP",25.00,2))

#插入多条数据
# ret = cur.executemany('insert into app01_book(title,price,publish_id) VALUE(%s,%s,%s)',[('C++',52.00,2),('Ruby',36.00,1)])

#查询app01_book表中存在的数据
# cur.execute('select * from app01_book')

#fetchall:获取app01_book表中所有的数据
# ret1 = cur.fetchall()
# print(ret1)
# print('----------------------')

#获取app01_book表中前三行数据
# ret2 = cur.fetchmany(3)
# print(ret2)
# print('---------------------------')

#获取app01_book表中第一行数据
# ret3 =cur.fetchone()
# print(ret3)

#删除app01_book表中数据
# cur.execute("delete * from app01_book")

#修改表中的数据
# ret = cur.execute("UPDATE app01_book set title='Java' WHERE id=6")

#将游标类型设置为字典形式
# cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
# cur.execute('select * from app01_book')
# ret = cur.fetchall()    #[{'id': 1, 'title': 'python', 'price': Decimal('100.00'), 'publish_id': 2}, {'id': 2, 'title': 'linux', 'price': Decimal('9.90'), 'publish_id': 1}]

#提交
conn.commit()
#关闭指针对象
cur.close()
#关闭连接对象
conn.close()
# print(ret)   #打印成功插入或修改或删除数据条数

#fetch数据类型
'''
关于默认获取的数据是元组类型，如果想要或者字典类型的数据:

#将游标类型设置为字典形式
cur = conn.cursor(cursor=pymysql.cursor.DictCursor)
ret = cur.fetchall()
print(ret)      #[{'id': 1, 'title': 'python', 'price': Decimal('100.00'), 'publish_id': 2}, {'id': 2, 'title': 'linux', 'price': Decimal('9.90'), 'publish_id': 1}]

'''