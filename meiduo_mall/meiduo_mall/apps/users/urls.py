from django.conf.urls import url
from rest_framework.routers import DefaultRouter

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
router = DefaultRouter()
router.register(r'addresses', views.AddressViewSet, base_name='addresses')

urlpatterns += router.urls
# POST /addresses/ 新建  -> create
# PUT /addresses/<pk>/ 修改  -> update
# GET /addresses/  查询  -> list
# DELETE /addresses/<pk>/  删除 -> destroy
# PUT /addresses/<pk>/status/ 设置默认 -> status
# PUT /addresses/<pk>/title/  设置标题 -> title