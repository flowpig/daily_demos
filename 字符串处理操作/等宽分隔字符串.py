#!/usr/bin/env python
#-*- coding:utf-8 -*-

#-------------------------------------------------------------------------------
# str = "桃花坞里桃花庵，桃花庵里桃花仙。桃花仙人种桃树，又摘桃花换酒钱。"
# li = list(str)
# tmp = map(lambda x:x + '\r\n' if x in '，；。；' else x,li)
# print("".join(list(tmp)))

#-------------------------------------------------------------------------------
# str = "桃花坞里桃花庵，桃花庵里桃花仙。桃花仙人种桃树，又摘桃花换酒钱。"
# li = list(str)
# for i in range(1,len(li)):
#     if (i+1) % 8 == 0:
#         li[i] += '\r\n'
# print("".join(li))

#-------------------------------------------------------------------------------
'''
textwrap按照等宽分隔字符串需要注意的是当内容中有空格时候将会按照空格+等宽
'''
import textwrap
str = "桃花坞里桃花庵，桃花庵里桃花仙。桃花仙人种桃树，又摘桃花换酒钱。"
res = textwrap.fill(str,width=8)
print(type(res))