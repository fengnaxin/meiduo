# 定义耗时任务
import logging
from celery_tasks.main import celery_app
from .yuntongxun.sms import CCP
from .constants import SMS_CODE_REDIS_EXPIRES

logger = logging.getLogger("django")
# 验证码短信模板
SMS_CODE_TEMP_ID = 1


@celery_app.task(name='send_sms_code')
def send_sms_code(mobile, sms_code):
    """
    发送短信验证码
    :param mobile: 手机号
    :param code: 验证码
    :param expires: 有效期
    :return: None
    """

    try:
        ccp = CCP()
        result = ccp.send_template_sms(mobile, [sms_code, SMS_CODE_REDIS_EXPIRES // 60], 1)
    except Exception as e:
        logger.error("发送验证码短信[异常][ mobile: %s, message: %s ]" % (mobile, e))
    else:
        if result == 0:
            logger.info("发送验证码短信[正常][ mobile: %s ]" % mobile)
        else:
            logger.warning("发送验证码短信[失败][ mobile: %s ]" % mobile)
