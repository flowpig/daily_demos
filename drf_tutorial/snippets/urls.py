#!/usr/bin/env python
#-*- coding:utf-8 -*-

# from django.conf.urls import url, include
# from snippets import views, testview1, testview2, testview3, testview4, testview5, testview6, testview7
#
#
# urlpatterns = [
#     # url(r'^snippets/$', views.snippet_list),
#     # url(r'^snippets/(?P<pk>[0-9]+)/$', views.snippet_detail),
#     # url(r'^snippets/$', testview1.snippet_list),
#     # url(r'^snippets/(?P<pk>[0-9]+)/$', testview1.snippet_detail),
#     url(r'^snippets/$', testview7.SnippetList.as_view(), name='snippet-list'),
#     url(r'^snippets/(?P<pk>[0-9]+)/$', testview7.SnippetDetail.as_view(), name='snippet-detail'),
#     url(r'^users/$', testview7.UserList.as_view(), name='user-list'),
#     url(r'^users/(?P<pk>[0-9]+)/$', testview7.UserDetail.as_view(), name='user-detail'),
#     url(r'^$', testview7.api_root),
# ]
#
# urlpatterns += [
#     url(r'^api-auth/', include('rest_framework.urls',
#                                namespace='rest_framework')),
# ]

# ---------------------------------------------------------------------
# viewsets自动生成路由

from django.conf.urls import url, include
from snippets import testview8,testview9
from rest_framework.routers import DefaultRouter

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'snippets', testview9.SnippetViewSet)
router.register(r'users', testview9.UserViewSet)

# The API URLs are now determined automatically by the router.
# Additionally, we include the login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]