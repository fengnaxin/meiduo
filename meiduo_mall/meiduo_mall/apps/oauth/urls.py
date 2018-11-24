from rest_framework.urls import url
from . import views

urlpatterns = [
    # 返回qq扫码url
    url(r'^qq/authorization/$', views.QQAuthURLView.as_view()),
    # qq验证
    url(r'^qq/user/$', views.QQUserGenericAPIView.as_view()),


]
