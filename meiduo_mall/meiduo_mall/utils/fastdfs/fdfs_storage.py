from django.core.files.storage import Storage

from fdfs_client.client import Fdfs_client


class FastDFSStorage(Storage):
    """自定义Django文件储存系统"""

    def __init__(self, option=None):
        pass

    def _open(self, name, mode):
        """
        此方法为django自定义储存系统打开文件，必须实现，
        但是此处文件只是储存，不需要打开文件，所以打开后什么也不做
        :param name:要打开文件的文件名
        :param mode:打开模式,read bytes
        :return:None
        """
        pass

    def _save(self, name, content):
        """
        实现文件存储: 在这个方法里面将文件转存到FastDFS服务器
        :param name:要储存文件的文件名字
        :param content:要存储的文件对象, File类型的对象,将来使用content.read()读取对象中的文件二进制
        :return: file_id
        """
        client = Fdfs_client('meiduo_mall/utils/fastdfs/client.conf')
        ret = client.upload_by_filename('/Users/naxin_fung/Desktop/1.png')
        """{'Group name': 'group1',
            'Remote file_id': 'group1/M00/00/00/wKgO6VwABMaAEEMDAAAj9N_m3yU194.png',
            'Status': 'Upload successed.',
            'Local file name': '/Users/naxin_fung/Desktop/1.png',
             'Uploaded size': '8.00KB',
            'Storage IP': '192.168.14.233'}
            """

        status = ret.get("Status")
        # 判断是否储存文件成功
        if status != "Upload successed.":
            raise Exception("Upload file failed")

        file_id = ret.get("Remote file_id")

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
        return '192.168.14.233:8888'+name


