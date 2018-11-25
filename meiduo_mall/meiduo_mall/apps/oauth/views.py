from QQLoginTool.QQtool import OAuthQQ
from django.conf import settings
from django.shortcuts import render
from rest_framework import status, serializers
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView
from rest_framework_jwt.settings import api_settings

from rest_framework.response import Response

from meiduo_mall.settings import dev
from meiduo_mall.utils.exceptions import logger
from oauth.models import OAuthQQUser
from oauth.utils import generate_save_user_token
from .serializer import QQAuthUserSerializer


# Create your views here.
class QQAuthURLView(APIView):
    """提供QQ登录页面网址
     https://graph.qq.com/oauth2.0/authorize?response_type=code&client_id=xxx&redirect_uri=xxx&state=xxx
     """

    def get(self, request):
        # next表示从哪个页面进入到的登录页面，将来登录成功后，就自动回到那个页面
        next = request.query_params.get('next')
        if not next:
            next = '/'

        # 获取QQ登录页面网址
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI, state=next)
        login_url = oauth.get_qq_url()

        return Response({'login_url': login_url})


class QQUserGenericAPIView(GenericAPIView):
    """用户扫码登录的回调处理"""
    # 指定序列化器

    serializer_class = QQAuthUserSerializer

    def get(self, request):

        code = request.query_params.get("code")

        if not code:
            return Response({"message": "缺少code"}, status=status.HTTP_400_BAD_REQUEST)
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID, client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI)
        # 通过code向qq服务器请求获取access_token
        try:
            access_token = oauth.get_access_token(code)
            openid = oauth.get_open_id(access_token)
        except Exception:
            logger.error("向qq服务器请求失败")
            return Response({'message': 'QQ服务异常'}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        try:
            oauth_user = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 如果openid没绑定美多商城用户，创建用户并绑定到openid
            # 为了能够在后续的绑定用户操作中前端可以使用openid，在这里将openid签名后响应给前端
            access_token_openid = generate_save_user_token(openid)
            return Response({'access_token': access_token_openid})
        else:
            # 如果openid已绑定美多商城用户，直接生成JWT token，并返回
            user = oauth_user.user
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            payload = jwt_payload_handler(user)
            token = jwt_encode_handler(payload)

            response = Response({
                'token': token,
                'user_id': user.id,
                'username': user.username
            })

            return response

    def post(self, request):
        # serializer = self.get_serializer(data=request.data)
        # # 开启校验
        # serializer.is_valid(raise_exception=True)
        # # 保存校验结果，并接收
        # user = serializer.save()
        # # 生成JWT token，并响应
        # jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        # jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        # payload = jwt_payload_handler(user)
        # token = jwt_encode_handler(payload)
        """openid绑定到用户"""

        # 获取序列化器对象
        serializer = self.get_serializer(data=request.data)
        # # 开启校验
        serializer.is_valid()
        serializer.errors
        # # 保存校验结果，并接收
        user = serializer.save()
        #
        # # 生成JWT token，并响应
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        response = Response({
            'token': token,
            'user_id': user.id,
            'username': user.username
        })

        return response
