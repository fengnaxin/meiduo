from django.shortcuts import render
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView
from .models import SKU
from .serializers import SKUSerializer, SKUIndexSerializer


# Create your views here.
# /categories/(?P<category_id>\d+)/skus
class SKUListAPIView(ListAPIView):
    """
    商品列表视图
    """
    # 排序
    filter_backends = [OrderingFilter]
    ordering_fields = ('create_time', 'price', 'sales')

    # 指定查询集
    def get_queryset(self):

        category_id = self.kwargs.get('category_id')

        return SKU.objects.filter(category_id=category_id, is_launched=True)

    # 指定序列化器
    serializer_class = SKUSerializer

from drf_haystack.viewsets import HaystackViewSet

class SKUSearchViewSet(HaystackViewSet):
    """
    SKU搜索
    """
    index_models = [SKU]

    serializer_class = SKUIndexSerializer
