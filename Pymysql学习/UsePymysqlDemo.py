#!/usr/bin/env python
#-*- coding:utf-8 -*-
import pymysql
#�������ݿ�
conn = pymysql.connect(host='127.0.0.1',port=3306,user='root',passwd='',db='books')
#�����α�
cur = conn.cursor()

#����һ������
# ret = cur.execute('insert into app01_book(title,price,publish_id) VALUE(%s,%s,%s)',("PHP",25.00,2))

#�����������
# ret = cur.executemany('insert into app01_book(title,price,publish_id) VALUE(%s,%s,%s)',[('C++',52.00,2),('Ruby',36.00,1)])

#��ѯapp01_book���д��ڵ�����
# cur.execute('select * from app01_book')

#fetchall:��ȡapp01_book�������е�����
# ret1 = cur.fetchall()
# print(ret1)
# print('----------------------')

#��ȡapp01_book����ǰ��������
# ret2 = cur.fetchmany(3)
# print(ret2)
# print('---------------------------')

#��ȡapp01_book���е�һ������
# ret3 =cur.fetchone()
# print(ret3)

#ɾ��app01_book��������
# cur.execute("delete * from app01_book")

#�޸ı��е�����
# ret = cur.execute("UPDATE app01_book set title='Java' WHERE id=6")

#���α���������Ϊ�ֵ���ʽ
# cur = conn.cursor(cursor=pymysql.cursors.DictCursor)
# cur.execute('select * from app01_book')
# ret = cur.fetchall()    #[{'id': 1, 'title': 'python', 'price': Decimal('100.00'), 'publish_id': 2}, {'id': 2, 'title': 'linux', 'price': Decimal('9.90'), 'publish_id': 1}]

#�ύ
conn.commit()
#�ر�ָ�����
cur.close()
#�ر����Ӷ���
conn.close()
# print(ret)   #��ӡ�ɹ�������޸Ļ�ɾ����������

#fetch��������
'''
����Ĭ�ϻ�ȡ��������Ԫ�����ͣ������Ҫ�����ֵ����͵�����:

#���α���������Ϊ�ֵ���ʽ
cur = conn.cursor(cursor=pymysql.cursor.DictCursor)
ret = cur.fetchall()
print(ret)      #[{'id': 1, 'title': 'python', 'price': Decimal('100.00'), 'publish_id': 2}, {'id': 2, 'title': 'linux', 'price': Decimal('9.90'), 'publish_id': 1}]

'''