from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions import mixins

from .models import Area
from .serializers import AreaSerializer, SubAreaSerializer


# Create your views here.


class AreasViewSet(mixins.CacheResponseMixin,ReadOnlyModelViewSet):
    """
    行政区划信息
    """
    pagination_class = None  # 区划信息不分页

    def get_queryset(self):
        """
        提供数据集
        """
        if self.action == 'list':
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()

    def get_serializer_class(self):
        """
        提供序列化器
        """
        if self.action == 'list':
            return AreaSerializer
        else:
            return SubAreaSerializer