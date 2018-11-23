# 返回值中增加username和user_id
import re

from django.contrib.auth.backends import ModelBackend

from users.models import User


def jwt_response_payload_handler(token, user=None, request=None):
    # 自定义返回字典
    return {
        "token": token,
        "username": user.username,
        "use_id": user.id
    }


def get_user_by_account(account):
    try:
        if re.match(r"1[3-9]\d{9}$", account):
            user = User.objects.get(mobile=account)
        else:
            user = User.objects.get(username=account)
    except User.DoeNotEixt:
        return None
    else:
        return user


class UsernameMobileAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_user_by_account(username)
        if user is not None and user.check_password(password):
            return user
