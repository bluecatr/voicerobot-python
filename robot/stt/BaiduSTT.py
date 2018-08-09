#coding:utf-8
import base64
import logging
from uuid import getnode as get_mac
import wave

from robot import utils
from robot.utils import diagnose
from robot.configuration import cmInstance
from robot.stt import AbstractSTTEngine


class BaiduSTT(AbstractSTTEngine):
    """
    百度的语音识别API.
    要使用本模块, 首先到 yuyin.baidu.com 注册一个开发者账号,
    之后创建一个新应用, 然后在应用管理的"查看key"中获得 API Key 和 Secret Key
    填入 profile.xml 中.

        ...
        baidu_yuyin: 'AIzaSyDoHmTEToZUQrltmORWS4Ott0OHVA62tw8'
            api_key: 'LMFYhLdXSSthxCNLR7uxFszQ'
            secret_key: '14dbd10057xu7b256e537455698c0e4e'
        ...
    """

    SLUG = "baidu-stt"

    def __init__(self, api_key, secret_key):
        self._logger = logging.getLogger(__name__)
        self.api_key = api_key
        self.secret_key = secret_key
        self.token = ''

    @classmethod
    def get_config(cls):
        # FIXME: Replace this as soon as we have a config module
        config = {}
        profile = cmInstance.getConfig('voice_engines')
        if 'baidu_yuyin' in profile:
            if 'api_key' in profile.baidu_yuyin:
                config['api_key'] = profile.baidu_yuyin.api_key
            if 'secret_key' in profile.baidu_yuyin:
                config['secret_key'] = profile.baidu_yuyin.secret_key
        return config

    def get_token(self):
        URL = 'http://openapi.baidu.com/oauth/2.0/token'
        params = {'grant_type': 'client_credentials',
                                   'client_id': self.api_key,
                                   'client_secret': self.secret_key}
        token = ''
        response = utils.restget(URL, params)
        if response:
            token = response['access_token']
        return token

    def transcribe(self, fp):
        try:
            wav_file = wave.open(fp, 'rb')
        except IOError:
            self._logger.critical('wav file not found: %s',
                                  fp,
                                  exc_info=True)
            return []
        n_frames = wav_file.getnframes()
        frame_rate = wav_file.getframerate()
        audio = wav_file.readframes(n_frames)
        base_data = base64.b64encode(audio)
        if self.token == '':
            self.token = self.get_token()
        data = {"format": "wav",
                "token": self.token,
                "len": len(audio),
                "rate": frame_rate,
                "speech": base_data,
                "cuid": str(get_mac())[:32],
                "channel": 1}
        
        transcribed = None
        response = utils.restpost('http://vop.baidu.com/server_api', data)
        if response and 'result' in response:
            text = response['result'][0].encode('utf-8')
            if text:
                transcribed = text.upper()
            self._logger.info(u'Transcribed: %s' % text)
        return transcribed

    @classmethod
    def is_available(cls):
        return diagnose.check_network_connection()
    
