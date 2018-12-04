import base64, pickle

from rest_framework.views import APIView

from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework import status

from .serializers import CartSerializer
from goods.models import SKU
from .serializers import CartSKUSerializer


class CartView(APIView):
    """购物车视图"""

    def perform_authentication(self, request):
        """系统默认在请求分发时会做验证，
        重写此方法表示默认分发时先不要验证
        目的：让未登录用户也可以访问此视图
        """
        pass

    def post(self, request):
        """增加购物车"""

        # 创建序列序列器,进行反序列化
        serializer = CartSerializer(data=request.data)
        # 校验数据
        serializer.is_valid(raise_exception=True)

        # 取出校验之后的数据
        sku_id = serializer.validated_data.get('sku_id')
        count = serializer.validated_data.get('count')
        selected = serializer.validated_data.get('selected')

        try:
            user = request.user
        except Exception:
            user = None

        if user is not None and user.is_authenticated:  # 判断当前是不是登录用户
            # 如果当前是登录用户我们操作redis购物车
            # 获取到连接redis的对象
            redis_conn = get_redis_connection('carts')
            # 创建管道
            pl = redis_conn.pipeline()
            # cart_user_idA : {sku_id1: count, sku_id2: count}
            # cart_user_idB : {sku_id1: count, sku_id2: count}
            # hincrby(name, key, amount=1)  此方法如果要添加的key在原哈希中不存就是新增,如果key已经存在,就后面的value和原有value相加
            pl.hincrby('cart_%s' % user.id, sku_id, count)

            # 用哈希来存商品及它的数量
            # card_dict = redis_conn.hgetall('cart_%s' % user.id)
            # if sku_id in card_dict:
            #     origin_count = card_dict[sku_id]
            #     count = origin_count + count

            # 用set来存商品是否被勾选
            if selected:
                # sadd(name, *values)
                pl.sadd('selected_%s' % user.id, sku_id)
            # 执行管道
            pl.execute()

            # 响应
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # 未登录用户
            # 获取cookie中原有的购物车数据
            cookie_str = request.COOKIES.get('cart')
            if cookie_str:
                # # 把cookie_str转换成python中的标准字典
                # # 把cookie_str字符串转换成cookie_str_bytes
                # cookie_str_byte = cookie_str.encode()
                # # 把cookie_str_bytes用b64转换为cookie_dict_bytes类型
                # cookie_dict_bytes = base64.b64decode(cookie_str_byte)
                # # 把cookie_dict_bytes用pickle转为python字典
                # cart_dict = pickle.loads(cookie_dict_bytes)
                # # 或者一行搞定
                cart_dict = pickle.loads(base64.b64decode(cookie_str.encode()))

                # 判断新加入购物的sku_id是否在原cookie,如果存在,做增量，不存在新加入字典中
                if sku_id in cart_dict:
                    # 如果if成立说明新增的商品购物车中已存在
                    origin_count = cart_dict[sku_id]['count']
                    count += origin_count

                # 第一次来添加到cookie购物车
            else:
                cart_dict = {}
            cart_dict[sku_id] = {
                'count': count,
                'selected': selected
            }
            # 把cart_dict 转换成cookie_str类型
            # 把Python的字典转换成cookie_dict_bytes字典的bytes类型
            cart_dict_bytes = pickle.dumps(cart_dict)
            # 把cookie_dict_bytes字典的bytes类型转换成cookie_str_bytes字符串类型的bytes
            cart_str_bytes = base64.b64encode(cart_dict_bytes)
            # 把cookie_str_bytes类型转换成字符串
            cart_str = cart_str_bytes.decode()
            # 创建响应对象
            response = Response(serializer.data, status=status.HTTP_201_CREATED)
            # 设置cookie
            response.set_cookie('cart', cart_str)

            return response

    def get(self, request):
        """查询购物车"""

        # 获取user
        try:
            user = request.user
        except Exception:
            user = None

        ## 登录用户
        if user is not None and user.is_authenticate:

            # 从redis取出购物车
            # 创建redis连接对象
            redis_conn = get_redis_connection('carts')
            # 从哈希表取出购物车数据
            redis_cart = redis_conn.hgetall('cart_%s' % user.id)
            # 从列表取出selected数据
            selected_list = redis_conn.smembers('cart_%s' % user.id)
            cart_dict = {}
            for sku_id, count in redis_cart.items():
                # cart_dict[int(sku_id)]['count']= int(count)
                # cart_dict[int(sku_id)]['selected']= sku_id in selected_list

                cart_dict[int(sku_id)] = {
                    'count': int(count),
                    # 判断当前的sku_id是否在set无序集体中,如果存在说明它是勾选
                    'selected': sku_id in selected_list
                }
        # 未登录用户
        else:
            # 从cookies获取购物车数据
            cookie_str = request.COOKIES.get('cart')
            if cookie_str:
                # 把cookie_str转为bytes数据类型
                cookie_str_bytes = cookie_str.encode()
                # 把cookie_str_bytes通过base64转为btyes数据类型的字典
                cookie_dict_bytes = base64.b64decode(cookie_str_bytes)
                # 把cookie_dict_bytes转为python字典类型
                cookie_cart_dict = pickle.loads(cookie_dict_bytes)
            else:
                cart_dict = {}

        cart_list = []
        for sku_id in cookie_cart_dict:
            sku = SKU.objects.get(id=sku_id)
            # 给模型多绑定两个属性
            sku.count = cookie_cart_dict[sku_id]['count']
            sku.selected = cookie_cart_dict[sku_id]['selected']
            cart_list.append(sku)
        # 只能把模型或列表里面装的模型进行序列化
        serializer = CartSKUSerializer(cart_list, many=True)
        return Response(serializer.data)

    def put(self, request):
        """修改购物车"""
        # 创建序列序列器,进行反序列化
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 校验之后取出数据
        sku_id = serializer.validated_data.get('sku_id')
        count = serializer.validated_data.get('count')
        selected = serializer.validated_data.get('selected')

        try:
            user = request.user
        except Exception:
            user = None

        # 判断当前用户是否为登录用户
        if user is not None and user.is_authenticated:
            # 创建redis连接对象
            redis_conn = get_redis_connection('carts')
            # 创建管道
            pl = redis_conn.pipeline()
            # 修改原有商品的数据,覆盖原来的数据
            pl.hset('cart_%s' % user.id, sku_id, count)
            # 修改商品的勾选状态
            if selected:
                pl.sadd('selected_%s' % user.id, sku_id)
            else:
                pl.srem('selected__%s' % user.id, sku_id)
            # 执行管道
            pl.execute()

        # 未登录用户

        else:
            # 从cookies取出数据
            cookie_str = request.COOKIES.get('cart')
            if cookie_str:
                # 把字符串类的cookies转化为python字典
                cart_dict = pickle.loads(base64.b64decode(cookie_str))
            else:
                # 第一次来添加到cookie购物车
                cart_dict = {}

            cart_dict = {
                'count': count,
                'selected': selected
            }
            # 把python字典转为cookies字符串数据
            # cookie_dict_bytes = pickle.dumps(cart_dict)
            # # 把cookie_dict_bytes字典的bytes类型转换成cookie_str_bytes字符串类型的bytes
            # cookie_dict_bytes = pickle.dumps(cart_dict)
            # # 把cookie_dict_bytes字典的bytes类型转换成cookie_str_bytes字符串类型的bytes
            # cookie_str_bytes = base64.b64encode(cookie_dict_bytes)
            # # 把cookie_str_bytes类型转换成字符串
            # cookie_str = cookie_str_bytes.decode()

            cart_str = base64.b64encode(pickle.dumps(cart_dict)).decode()
            # cookies写入浏览器
            # 创建响应头
            response = Response(serializer.data)
            response.set_cookie('cart',cart_str)

            return response



    def delete(self):
        """删除购物车"""
        pass
