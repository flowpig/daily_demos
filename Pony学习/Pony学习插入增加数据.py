#!/usr/bin/env python
#-*- coding:utf-8 -*-

import datetime
import pony.orm as pny
from models import Album, Artist
from database import PonyDatabase


# ----------------------------------------------------------------------
@pny.db_session
def add_data():
    """"""

    new_artist = Artist(name=u"Newsboys")
    bands = [u"MXPX", u"Kutless", u"Thousand Foot Krutch"]
    for band in bands:
        artist = Artist(name=band)

    album = Album(artist=new_artist,
                  title=u"Read All About It",
                  release_date=datetime.date(1988, 12, 01),
                  publisher=u"Refuge",
                  media_type=u"CD")

    albums = [{"artist": new_artist,
               "title": "Hell is for Wimps",
               "release_date": datetime.date(1990, 07, 31),
               "publisher": "Sparrow",
               "media_type": "CD"
               },
              {"artist": new_artist,
               "title": "Love Liberty Disco",
               "release_date": datetime.date(1999, 11, 16),
               "publisher": "Sparrow",
               "media_type": "CD"
               },
              {"artist": new_artist,
               "title": "Thrive",
               "release_date": datetime.date(2002, 03, 26),
               "publisher": "Sparrow",
               "media_type": "CD"}
              ]

    for album in albums:
        a = Album(**album)


if __name__ == "__main__":
    db = PonyDatabase()
    db.bind("sqlite", "D:\日常python学习PY2\Pony学习\music.sqlite", create_db=True)
    db.generate_mapping(create_tables=True)


    add_data()

    # use db_session as a context manager
    with pny.db_session:
        a = Artist(name="Skillet")


'''
您会注意到我们需要使用一个装饰器db_session来处理数据库。 
它负责打开连接，提交数据并关闭连接。 你也可以把它作为一个上
下文管理器，with pny.db_session
'''