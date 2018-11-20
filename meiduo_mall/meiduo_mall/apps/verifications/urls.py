from django.conf.urls import url
from . import views

urlpatterns = [
    # 通过APIVIew视图，获取手机验证码接口
    # url(r"^sms_codes/(?P<mobile>1[3-9]\d{9})/$",views.SMSCodeView.as_view())
    #  通过GenericAPIView视图，获取手机验证码接口
     url(r"^sms_codes/(?P<mobile>1[3-9]\d{9})/$",views.SMSCodeView.as_view())
]