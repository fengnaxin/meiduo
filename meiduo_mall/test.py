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
        # 未登录用户操作cookie购物车

        # 获取cookie中原有的购物车数据
        cookie_str = request.COOKIES.get('cart')
        if cookie_str:
            # 把cookie_str转换成python中的标准字典
            # 把cookie_str字符串转换成cookie_str_bytes
            cookie_str_bytes = cookie_str.encode()

            # 把cookie_str_bytes用b64转换为cookie_dict_bytes类型
            cookie_dict_bytes = base64.b64decode(cookie_str_bytes)

            # cookie_dict_bytes类型转换成Python中标准的字典
            cart_dict = pickle.loads(cookie_dict_bytes)
            # cart_dict = pickle.loads(base64.decode(cookie_str.encode()))

            # 判断当前要新加入购物车的sku_id是否在原cookie中已存,如果存在,做增量,不存在新加入字典中
            if sku_id in cart_dict:
                # 如果if成立说明新增的商品购物车中已存在
                origin_count = cart_dict[sku_id]['count']
                count += origin_count  # count = origin_count + count
        else:  # 第一次来添加到cookie购物车
            cart_dict = {}

        # 不管之前有没有这个商品都重新包一下
        cart_dict[sku_id] = {
            'count': count,
            'selected': selected

        }

        # 把cart_dict 转换成cookie_str类型
        # 把Python的字典转换成cookie_dict_bytes字典的bytes类型
        cookie_dict_bytes = pickle.dumps(cart_dict)
        # 把cookie_dict_bytes字典的bytes类型转换成cookie_str_bytes字符串类型的bytes
        cookie_str_bytes = base64.b64encode(cookie_dict_bytes)
        # 把cookie_str_bytes类型转换成字符串
        cookie_str = cookie_str_bytes.decode()

        # 把cookie写入到浏览器
        # 创建响应对象
        response = Response(serializer.data, status=status.HTTP_201_CREATED)
        # 设置cookies
        response.set_cookie('cart', cookie_str)
        # 响应
        return response