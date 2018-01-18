#!/usr/bin/env python
#-*- coding:utf-8 -*-

import datetime
import pony.orm as pny
from database import PonyDatabase

db = PonyDatabase()

########################################################################
class Artist(db.Entity):
    """
    Pony ORM model of the Artist table
    """
    #set是被外键关联
    name = pny.Required(unicode)
    albums = pny.Set("Album")

########################################################################
class Album(db.Entity):
    """
    Pony ORM model of album table
    """
    #创建外键时两个表都要写，外键默认index=True
    artist = pny.Required(Artist)
    title = pny.Required(unicode)
    release_date = pny.Required(datetime.date)
    publisher = pny.Required(unicode)
    media_type = pny.Required(unicode)
