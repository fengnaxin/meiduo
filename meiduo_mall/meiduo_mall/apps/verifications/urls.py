from django.conf.urls import url
from . import views

urlpatterns = [
    # 通过APIVIew视图，获取手机验证码接口
    url(r"^sms_codes/(?P<mobile>1[3-9]\d{9})/$", views.SMSCodeView.as_view()),
    #  通过GenericAPIView视图，获取手机验证码接口

    # this.host + '/usernames/' + this.username + '/count/'
    url(r"^usernames/(?P<username>[a-zA-Z\d|_]{5,20})/count/$", views.UsernameCountView.as_view()),
    # (this.host + '/mobiles/' + this.mobile + '/',

    url(r"^mobiles/(?P<mobile>1[3-9]\d{9})/$",views.UserMobileCountView.as_view()),
]
