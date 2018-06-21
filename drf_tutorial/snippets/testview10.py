from rest_framework import viewsets
from django.contrib.auth.models import User
from snippets.models import Snippet
from snippets.serializers import SnippetSerializer, UserSerializer
from rest_framework import permissions
from snippets.permission import IsOwnerOrReadOnly
from rest_framework.decorators import list_route, detail_route
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.db.models.query import QuerySet
import operator


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    This viewset automatically provides 'list' and 'detail' actions
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer


class SnippetViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    响应自定义动作需要使用detail_route装饰
    """
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          IsOwnerOrReadOnly,)
    filter_backends = (DjangoFilterBackend, OrderingFilter)
    ordering_fields = ('id',)       # ?ordering=id   ?ordering=-id
    # 如果serializer类的SerializerMethod字段可以在返回的response['result']里进行sort排序

    # def filter_queryset(self, queryset):
    #     queryset = super(SnippetViewSet, self).filter_queryset(queryset)
    #     return queryset.order_by('id')

    def list(self, request, *args, **kwargs):
        response = super(SnippetViewSet, self).list(request, *args, **kwargs)
        ordering = request.query_params.get('ordering')    # url
        print(response.data)
        # response.data['results'] = sorted(response.data['results'], key=operator.itemgetter(ordering.replace('-', ''), ))
        x = 1
        if "-" in ordering:
            response.data = sorted(response.data, key=lambda k: (k[ordering.replace('-', '')],), reverse=True)
        else:
            response.data = sorted(response.data, key=lambda k: (k[ordering],))
        return response

    @list_route(methods=['GET'])
    def get_tt(self, request):
        print(request._request.path_info)     # /snippets/get_tt/
        return Response({1: 2, 3: 4})

    # @detail_route(methods=['GET'])
    # def get_tt(self, request, pk=None):
    #     print(pk)
    #     print(request._request.path_info)     # /snippets/1/get_tt/
    #     return Response({1: 2, 3: 4})


    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)