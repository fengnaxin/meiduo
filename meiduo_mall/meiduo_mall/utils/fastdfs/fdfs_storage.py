import logging

from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client
from django.conf import settings

logger = logging.getLogger("django")


class FastDFSStorage(Storage):
    """自定义Django文件储存系统"""

    def __init__(self, client_conf=None, base_url=None):
        self.client_conf = client_conf or settings.FDFS_CLIENT_CONF
        self.base_url = base_url or settings.FDFS_BASE_URL

    def _open(self, name, mode):
        """
        此方法为django自定义储存系统打开文件，必须实现，
        但是此处文件只是储存，不需要打开文件，所以打开后什么也不做
        :param name:要打开文件的文件名
        :param mode:打开模式,read bytes
        :return:None
        """
        pass

    def _save(self, name, content=None):
        """
        实现文件存储: 在这个方法里面将文件转存到FastDFS服务器
        :param name:要储存文件的文件名字
        :param content:要存储的文件对象, File类型的对象,将来使用content.read()读取对象中的文件二进制
        :return: file_id
        """
        client = Fdfs_client(self.client_conf)
        # print(content)
        # print("name=%s"%name)
        # ret = client.upload_by_filename('/Users/naxin_fung/Desktop/1.png')
        # ret = client.append_by_buffer(content.read())
        ret = client.upload_appender_by_buffer(content.read())

        status = ret.get("Status")
        # 判断是否储存文件成功
        if status != "Upload successed.":
            raise Exception("Upload file failed")
        # logger.info("上传成功")
        # 如果能执行到这里,说明文件上传成功了
        file_id = ret.get("Remote file_id")
        # logger.info("file_id=%s" % file_id)

        return file_id

    def exists(self, name):
        """
        判断要上传的文件是否已存在,判断storage中是否已存储了该文件,
        如果存储了就不会再存储,如果没有存储就调用_save()
        :param name: 要判断的文件名字
        :return: True(文件存在) / False(文件不存在)
        """
        return False

    def url(self, name):
        return self.base_url + name
