import logging


import random
from rest_framework import status

from rest_framework.response import Response
from django_redis import get_redis_connection

from meiduo_mall.utils.exceptions import logger
# from meiduo_mall.libs.yuntongxun.sms import CCP
# from meiduo_mall.utils import constants
from . import constants
from celery_tasks.main import app
from rest_framework.generics import GenericAPIView
from celery_tasks.sms import tasks as sms_tasks

# Create your views here.
from users.models import User

logger = logging.getLogger("django")


class UserMobileCountView(GenericAPIView):
    """判断用户是否存在"""

    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        data = {
            "username": mobile,
            "count": count
        }
        return Response(data)


class UsernameCountView(GenericAPIView):
    """判断用户是否存在"""

    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        data = {
            "username": username,
            "count": count
        }
        return Response(data)


class SMSCodeView(GenericAPIView):
    # 发送短信验证码
    def get(self, request, mobile):

        redis_con = get_redis_connection("verify_codes")

        # 60秒内不允许重发发送短信
        send_flag = redis_con.get('sms_%s' % mobile)
        if send_flag:
            return Response({"message": "发送短信过于频繁"}, status=status.HTTP_400_BAD_REQUEST)

        #  随机生成6位数字验证码
        sms_code = "%06d" % random.randint(0, 999999)

        logger.info(sms_code)
        # 创建redis管道
        pl = redis_con.pipeline()

        # 把手机验证码储存到redis数据库
        # redis_con.setex("sms_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES // 60, sms_code)
        pl.setex("sms_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
        #  保存发送短信验证码的标记
        # redis_con.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
        pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)

        # 执行
        pl.execute()

        # logger.info(a)
        logger.info("sms_%s" % mobile)
        # sms_code_expires = str(constants.SMS_CODE_REDIS_EXPIRES // 60)

        sms_tasks.send_sms_code.delay(mobile, sms_code)

        return Response({"message": "OK"})

# class SMSCodeView(APIView):
#     # 短信验证码发送视图
#
# def get(self, request, mobile):
#     # 创建redis连接对象
#     redis_con = get_redis_connection("default")
#     # 60秒内不允许重发发送短信
#     send_flag = redis_con.get('sms_%s' % mobile)
#     if send_flag:
#         return Response({"message": "发送短信过于频繁"}, status=status.HTTP_400_BAD_REQUEST)
#
#     #  随机生成6位数字验证码
#     sms_code = "%06d" % random.randint(0, 999999)
#
#     logger.debug(sms_code)
#     # 把手机验证码储存到redis数据库
#
#     redis_con.setex("sms_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES // 60, sms_code)
#
#         # 接入云通讯接口
#
#         # CCP().send_template_sms(mobile, [sms_code, constants.SMS_CODE_REDIS_EXPIRES // 60], 1)
#         # 以下代码演示redis管道pipeline的使用
#         pl = redis_con.pipeline()
#         pl.setex("sms_%s" % mobile, constants.SMS_CODE_REDIS_EXPIRES, sms_code)
#         pl.setex('send_flag_%s' % mobile, constants.SEND_SMS_CODE_INTERVAL, 1)
#         # 执行
#         pl.execute()
#
#         return Response({"message": "OK"})
