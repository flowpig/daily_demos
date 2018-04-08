#!/usr/bin/env python
#-*- coding:utf-8 -*-

from django.conf.urls import url, include
from snippets import views, testview1, testview2, testview3, testview4, testview5, testview6


urlpatterns = [
    # url(r'^snippets/$', views.snippet_list),
    # url(r'^snippets/(?P<pk>[0-9]+)/$', views.snippet_detail),
    # url(r'^snippets/$', testview1.snippet_list),
    # url(r'^snippets/(?P<pk>[0-9]+)/$', testview1.snippet_detail),
    url(r'^snippets/$', testview6.SnippetList.as_view(), name='snippet-list'),
    url(r'^snippets/(?P<pk>[0-9]+)/$', testview6.SnippetDetail.as_view()),
    url(r'^users/$', testview6.UserList.as_view(), name='user-list'),
    url(r'^users/(?P<pk>[0-9]+)/$', testview6.UserDetail.as_view()),
    url(r'^$', testview6.api_root),
]

urlpatterns += [
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
]