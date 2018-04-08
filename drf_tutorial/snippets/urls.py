#!/usr/bin/env python
#-*- coding:utf-8 -*-

from django.conf.urls import url
from snippets import views, testview1, testview2


urlpatterns = [
    # url(r'^snippets/$', views.snippet_list),
    # url(r'^snippets/(?P<pk>[0-9]+)/$', views.snippet_detail),
    # url(r'^snippets/$', testview1.snippet_list),
    # url(r'^snippets/(?P<pk>[0-9]+)/$', testview1.snippet_detail),
    url(r'^snippets/$', testview2.SnippetList.as_view()),
    url(r'^snippets/(?P<pk>[0-9]+)/$', testview2.SnippetDetail.as_view()),
]