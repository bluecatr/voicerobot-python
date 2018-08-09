#coding:utf-8
import base64
import datetime
import hashlib
import hmac
import logging
import os
import tempfile
import urllib2

from robot import utils
from robot.configuration import cmInstance
from robot.tts import AbstractTTSEngine
from robot.utils import diagnose


def get_current_date():
    date = datetime.datetime.strftime(datetime.datetime.utcnow(), "%a, %d %b %Y %H:%M:%S GMT")
    return date


def to_md5_base64(strBody):
    """
    :type strBody: basestring
    """
    hash = hashlib.md5()
    hash.update(strBody)
    return hash.digest().encode('base64').strip()


def to_sha1_base64(stringtosign, secret):
    """
    :param stringtosign:
    :param secret:
    """
    hmacsha1 = hmac.new(secret.encode('utf-8'), stringtosign.encode('utf-8'), hashlib.sha1)
    return base64.b64encode(hmacsha1.digest()).decode('utf-8')


class AliTTS(AbstractTTSEngine):
    SLUG = "ali-tts"

    def __init__(self, ak_id, ak_secret, voice_name):
        self._logger = logging.getLogger(__name__)
        self.ak_id = ak_id
        self.ak_secret = ak_secret
        self.voice_name = voice_name
        self.audioFormat = "mp3" # or wav format

    @classmethod
    def get_config(cls):
        config = {}
        profile = cmInstance.getConfig('voice_engines')
        if 'aliyun' in profile:
            if 'ak_id' in profile.aliyun:
                config['ak_id'] = profile.aliyun.ak_id
            if 'ak_secret' in profile.aliyun:
                config['ak_secret'] = profile.aliyun.ak_secret
            if 'voice_name' in profile.aliyun:
                config['voice_name'] = profile.aliyun.voice_name
        return config

    @classmethod
    def is_available(cls):
        return diagnose.check_network_connection()

    def create_request(self, text, volume=50, sample_rate=16000, speech_rate=50,pitch_rate=0):
        options = {
            'url': 'https://nlsapi.aliyun.com/speak?encode_type=%s&voice_name=%s&volume=%s&sample_rate=%s&speech_rate=%s&pitch_rate=%s' % (
                       self.audioFormat, self.voice_name, volume, sample_rate, speech_rate, pitch_rate),
            'method': 'POST',
            'body': text,
            'headers': {
                'accept': 'audio/%s,application/json'%self.audioFormat,
                'content-type': 'text/plain',
                'date': get_current_date(),
                'authorization': ''
            }}
        
        body = ''
        if 'body' in options:
            body = options['body']
        bodymd5 = ''
        if not body == '':
            bodymd5 = to_md5_base64(body)
        stringToSign = options['method'] + '\n' + options['headers']['accept'] + '\n' + bodymd5 + '\n' + \
                       options['headers'][
                           'content-type'] + '\n' + options['headers']['date']
        signature = to_sha1_base64(stringToSign, self.ak_secret)
        authHeader = 'Dataplus ' + self.ak_id + ':' + signature
        options['headers']['authorization'] = authHeader
        request = None
        method = options['method']
        url = options['url']
        if 'GET' == method or 'DELETE' == method:
            request = urllib2.Request(url)
        elif 'POST' == method or 'PUT' == method:
            request = urllib2.Request(url, body)
        request.get_method = lambda: method
        for key, value in options['headers'].items():
            request.add_header(key, value)
        return request

    def tts(self, text):
        request = self.create_request(text)
        conn = urllib2.urlopen(request)
        with tempfile.NamedTemporaryFile(suffix='.%s'%self.audioFormat, mode='w+b', delete=False) as f:
            f.write(conn.read())
            f.seek(0)
            f.close
            return f.name
        
    def synthesise(self, phrase):
        self._logger.debug(u"Synthesise '%s' with '%s'", phrase, self.SLUG)
        audiofile = self.tts(str(phrase))
        return audiofile
