#!/usr/bin/env python
#-*- coding:utf-8 -*-

import pony.orm as pny

from models import Artist
from database import PonyDatabase

db = PonyDatabase()
db.bind("sqlite", "D:\日常python学习PY2\Pony学习\music.sqlite", create_db=True)
db.generate_mapping(create_tables=True)

with pny.db_session:
    band = Artist.get(name="MXPX")
    band.delete()