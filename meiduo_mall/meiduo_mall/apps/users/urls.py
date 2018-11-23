from django.conf.urls import url
from . import views
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [

    # this.host + '/usernames/' + this.username + '/count/'
url(r'^users/$', views.UsernameCountView.as_view()),
    # 用户登录验证接口
url(r'^authorizations/$', obtain_jwt_token),
]






