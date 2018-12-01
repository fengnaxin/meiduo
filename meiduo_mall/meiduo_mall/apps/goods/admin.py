from django.contrib import admin

from celery_tasks.html.tasks import generate_static_list_search_html
from . import models


# Register your models here.
class GoodsCategoryAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        """
        :param request: 本次请求的对象
        :param obj: 本次保存的模型类对象
        :param form:本次保存的表单内容
        :param change: 本次保存与之前的数据变化
        :return: None
        """
        obj.save()
        generate_static_list_search_html.delay()

    def delete_model(self, request, obj):
        """
        :param request: 本次请求的对象
        :param obj: 本次删除的模型类对象
        :param form:本次删除的表单内容
        :param change: 本次删除与之前的数据变化
        :return: None
        """
        obj.delete()
        generate_static_list_search_html.delay()


admin.site.register(models.GoodsCategory, GoodsCategoryAdmin)
admin.site.register(models.GoodsChannel)
admin.site.register(models.Goods)
admin.site.register(models.Brand)
admin.site.register(models.GoodsSpecification)
admin.site.register(models.SpecificationOption)
admin.site.register(models.SKU)
admin.site.register(models.SKUSpecification)
admin.site.register(models.SKUImage)
