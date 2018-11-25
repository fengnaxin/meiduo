from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData

from oauth import constants


def generate_save_user_token(openid):
    """
       生成保存用户数据的token
       :param openid: 用户的openid
       :return: token
       """
    serializer = Serializer(settings.SECRET_KEY, constants.SAVE_QQ_USER_TOKEN_EXPIRES)
    data = {'openid': openid}
    # 对openid进行签名，返回的是byte类型
    token = serializer.dumps(data)
    # 对token进行解码
    return token.decode()
def check_save_user_token(access_token):
    """
    检验保存用户数据的token
    :param token: token
    :return: openid or None
    """
    serializer = Serializer(settings.SECRET_KEY, constants.SAVE_QQ_USER_TOKEN_EXPIRES)
    try:
        data = serializer.loads(access_token)
    except BadData:
        return None
    else:
        return data.get('openid')