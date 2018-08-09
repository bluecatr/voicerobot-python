#coding:utf-8
import logging
import os
import requests
import tempfile
from uuid import getnode as get_mac

from robot import utils
from robot.configuration import cmInstance
from robot.tts import AbstractTTSEngine
from robot.utils import diagnose
from robot.utils.SSML import translation


class BaiduTTS(AbstractTTSEngine):
    """
    使用百度语音合成技术

    要使用本模块, 首先到 yuyin.baidu.com 注册一个开发者账号,
    之后创建一个新应用, 然后在应用管理的"查看key"中获得 API Key 和 Secret Key
    填入 profile.xml 中.
    """

    SLUG = "baidu-tts"

    def __init__(self, api_key, secret_key, per=0):
        self._logger = logging.getLogger(__name__)
        self.api_key = api_key
        self.secret_key = secret_key
        self.per = per
        self.token = ''
        self.translation_type = "baidu"

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
            if 'per' in profile.baidu_yuyin:
                config['per'] = profile.baidu_yuyin.per
        return config

    @classmethod
    def is_available(cls):
        return diagnose.check_network_connection()

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

    def split_sentences(self, text):
        punctuations = ['.', '。', ';', '；', '\n']
        for i in punctuations:
            text = text.replace(i, '@@@')
        return text.split('@@@')

    def get_speech(self, phrase):
        if self.token == '':
            self.token = self.get_token()
        data = {'tex': phrase,
                 'lan': 'zh',
                 'tok': self.token,
                 'ctp': 1,
                 'cuid': str(get_mac())[:32],
                 'spd': 5,
                 'per': self.per
                 }
        r = requests.post('http://tsn.baidu.com/text2audio',
                          data=data,
                          headers={'content-type': 'application/json'})
        try:
            r.raise_for_status()
            if r.json()['err_msg'] is not None:
                self._logger.critical('Baidu TTS failed with response: %r',
                                      r.json()['err_msg'],
                                      exc_info=True)
                return None
        except Exception:
            pass
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
            f.write(r.content)
            return f.name

    def synthesise(self, phrase):
        self._logger.debug(u"Synthesise '%s' with '%s'", phrase, self.SLUG)
        translatedText = translation(phrase,self.translation_type)
        self._logger.debug("The translated text is '%s'", translatedText)
        audiofile = self.get_speech(translatedText)
        return audiofile
