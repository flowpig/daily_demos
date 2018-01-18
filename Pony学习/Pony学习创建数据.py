#!/usr/bin/env python
#-*- coding:utf-8 -*-

import datetime
import pony.orm as pny
from models import db


# 路径建议写绝对路径。我这边开始写相对路径报错 unable to open database file
db.bind("sqlite","D:\日常python学习PY2\Pony学习\music.sqlite",create_db=True)


# turn on debug mode
pny.sql_debug(True)

# map the models to the database
# and create the tables, if they don't exist
db.generate_mapping(create_tables=True)