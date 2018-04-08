#!/usr/bin/env python
#-*- coding:utf-8 -*-

from django.conf.urls import url
from snippets import views, testview1, testview2, testview3


urlpatterns = [
    # url(r'^snippets/$', views.snippet_list),
    # url(r'^snippets/(?P<pk>[0-9]+)/$', views.snippet_detail),
    # url(r'^snippets/$', testview1.snippet_list),
    # url(r'^snippets/(?P<pk>[0-9]+)/$', testview1.snippet_detail),
    url(r'^snippets/$', testview3.SnippetList.as_view()),
    url(r'^snippets/(?P<pk>[0-9]+)/$', testview3.SnippetDetail.as_view()),
]