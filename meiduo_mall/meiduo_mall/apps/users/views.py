from django.shortcuts import render
from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, UpdateAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from django_redis import get_redis_connection

from goods.models import SKU
from . import serializers, constants
from .models import User
from .serializers import EmailSerializer, UserDetailSerializer, CreateUserSerializer
from .serializers import AddUserBrowsingHistorySerializer
from goods.serializers import SKUSerializer


class AddressViewSet(mixins.CreateModelMixin, mixins.UpdateModelMixin, GenericViewSet):
    """
    用户地址新增与修改
    """
    serializer_class = serializers.UserAddressSerializer
    permissions = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)

    # GET /addresses/
    def list(self, request, *args, **kwargs):
        """
        用户地址列表数据
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        user = self.request.user
        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': constants.USER_ADDRESS_COUNTS_LIMIT,
            'addresses': serializer.data,
        })

    # POST /addresses/
    def create(self, request, *args, **kwargs):
        """
        保存用户地址数据
        """
        # 检查用户地址数据数目不能超过上限
        count = request.user.addresses.count()
        if count >= constants.USER_ADDRESS_COUNTS_LIMIT:
            return Response({'message': '保存地址数据已达到上限'}, status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)

    # delete /addresses/<pk>/
    def destroy(self, request, *args, **kwargs):
        """
        处理删除
        """
        address = self.get_object()

        # 进行逻辑删除
        address.is_deleted = True
        address.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

    # put /addresses/pk/status/
    @action(methods=['put'], detail=True)
    def status(self, request, pk=None):
        """
        设置默认地址
        """
        address = self.get_object()
        request.user.default_address = address
        request.user.save()
        return Response({'message': 'OK'}, status=status.HTTP_200_OK)

    # put /addresses/pk/title/
    # 需要请求体参数 title
    @action(methods=['put'], detail=True)
    def title(self, request, pk=None):
        """
        修改标题
        """
        address = self.get_object()
        serializer = serializers.AddressTitleSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# get emails/verification/
class VerifyEmailView(APIView):
    """
    邮箱验证
    """

    def get(self, request):
        # 获取token
        token = request.query_params.get('token')
        if not token:
            return Response({'message': '缺少token'}, status=status.HTTP_400_BAD_REQUEST)

        # 验证token
        user = User.check_verify_email_token(token)
        if user is None:
            return Response({'message': '链接信息无效'}, status=status.HTTP_400_BAD_REQUEST)

        else:
            user.email_active = True
            user.save()
            return Response({'message': 'OK'})


class EmailView(UpdateAPIView):
    """
    保存用户邮箱
    """
    permission_classes = [IsAuthenticated]
    serializer_class = EmailSerializer

    def get_object(self, *args, **kwargs):
        return self.request.user


class UserDetailView(RetrieveAPIView):
    """
    用户详情
    """
    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UsernameCountView(CreateAPIView):
    """CreateAPIView视图"""

    serializer_class = CreateUserSerializer


# POST /browse_histories/
class UserBrowseHistoryView(CreateAPIView):
    """保存用户浏览记录的视图"""
    # 指定序列化器
    serializer_class = AddUserBrowsingHistorySerializer
    # 登录用户才能访问此接口
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """获取用户的浏览记录"""

        # 获取用户id
        user_id = request.user.id

        # 创建redis连接
        redis_conn = get_redis_connection('history')

        # 取出当前用户redis浏览数据
        sku_ids = redis_conn.lrange('history_%s' % user_id, 0, -1)
        sku_list = []
        # 遍历sku_ids列表
        for sku_id in sku_ids:
            sku_model = SKU.objects.get(id=sku_id)
            sku_list.append(sku_model)
        serializer = SKUSerializer(sku_list,many=True)

        return Response(serializer.data)





