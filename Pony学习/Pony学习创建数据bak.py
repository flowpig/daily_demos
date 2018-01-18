#!/usr/bin/env python
#-*- coding:utf-8 -*-

import datetime
import pony.orm as pny
import sqlite3

# conn = sqlite3.connect('D:\日常python学习PY2\Pony学习\music.sqlite')
# print conn

# database = pny.Database()
# database.bind("sqlite","music.sqlite",create_db=True)

# 路径建议写绝对路径。我这边开始写相对路径报错 unable to open database file
database = pny.Database("sqlite","D:\日常python学习PY2\Pony学习\music.sqlite",create_db=True)

########################################################################
class Artist(database.Entity):
    """
    Pony ORM model of the Artist table
    """
    name = pny.Required(unicode)
    #被外键关联
    albums = pny.Set("Album")

########################################################################
class Album(database.Entity):
    """
    Pony ORM model of album table
    """
    #外键字段artlist,外键关联表Artist，Artist表必须写Set表示被外键关联
    #这个外键字段默认就是index=True,除非自己指定index=False才不会创建索引，索引名默认为[idx_表名__字段](artist)
    artist = pny.Required(Artist)
    title = pny.Required(unicode)
    release_date = pny.Required(datetime.date)
    publisher = pny.Required(unicode)
    media_type = pny.Required(unicode)

# turn on debug mode
pny.sql_debug(True)

# map the models to the database
# and create the tables, if they don't exist
database.generate_mapping(create_tables=True)