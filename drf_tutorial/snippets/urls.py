#!/usr/bin/env python
#-*- coding:utf-8 -*-

from django.conf.urls import url, include
from snippets import views, testview1, testview2, testview3, testview4, testview5


urlpatterns = [
    # url(r'^snippets/$', views.snippet_list),
    # url(r'^snippets/(?P<pk>[0-9]+)/$', views.snippet_detail),
    # url(r'^snippets/$', testview1.snippet_list),
    # url(r'^snippets/(?P<pk>[0-9]+)/$', testview1.snippet_detail),
    url(r'^snippets/$', testview5.SnippetList.as_view()),
    url(r'^snippets/(?P<pk>[0-9]+)/$', testview5.SnippetDetail.as_view()),
    url(r'^users/$', testview5.UserList.as_view()),
    url(r'^users/(?P<pk>[0-9]+)/$', testview5.UserDetail.as_view()),
]

urlpatterns += [
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]