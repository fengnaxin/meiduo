from django.conf.urls import url
from . import views
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [

    # this.host + '/usernames/' + this.username + '/count/'
    url(r'^users/$', views.UsernameCountView.as_view()),
    # 用户登录验证
    url(r'^user/$', views.UserDetailView.as_view()),
    # 用户登录验证接口
    url(r'^authorizations/$', obtain_jwt_token),
    # 保存邮箱
    url(r'^email/$', views.EmailView.as_view()),
    url(r'^emails/verification/$', views.VerifyEmailView.as_view())
]
