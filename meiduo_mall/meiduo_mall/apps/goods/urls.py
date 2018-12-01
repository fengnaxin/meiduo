from rest_framework.urls import url
from . import views

urlpatterns = [
    # 获取商品列表信息

    url(r"^categories/(?P<category_id>\d+)/skus/$",views.SKUListAPIView.as_view())
]