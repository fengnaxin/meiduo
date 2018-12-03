from django.shortcuts import render
from rest_framework import serializers

# Create your views here.
from goods.models import SKU


class CartSerializer(serializers.Serializer):
    sku_id = serializers.IntegerField(label="商品id", min_value=1)
    count = serializers.IntegerField(label="商品数量", min_value=1)
    selected = serializers.BooleanField(label='是否勾选', default=True)

    def validate_sku_id(self, value):
        try:
            SKU.objects.get(id=value)
        except SKU.DoesNotExist:
            return serializers.ValidationError('sku_id不存在')
        return value


class CartSKUSerializer(serializers.ModelSerializer):
    count = serializers.IntegerField(label="商品数量", min_value=1)
    selected = serializers.BooleanField(label='是否勾选', default=True)

    class Meta:
        model = SKU
        fields = ['id', 'name', 'price', 'count', 'selected', 'default_image_url']

