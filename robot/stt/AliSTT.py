#coding:utf-8
import base64
import datetime
import hashlib
import hmac
import json
import logging
import urllib2
import wave

from robot.configuration import cmInstance
from robot.stt import AbstractSTTEngine
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


class AliSTT(AbstractSTTEngine):
    SLUG = "ali-stt"

    def __init__(self, ak_id, ak_secret, model):
        self._logger = logging.getLogger(__name__)
        self.ak_id = ak_id
        self.ak_secret = ak_secret
        self.model = model

    @classmethod
    def get_config(cls):
        config = {}
        profile = cmInstance.getConfig('voice_engines')
        if 'aliyun' in profile:
            if 'ak_id' in profile.aliyun:
                config['ak_id'] = profile.aliyun.ak_id
            if 'ak_secret' in profile.aliyun:
                config['ak_secret'] = profile.aliyun.ak_secret
            if 'model' in profile.aliyun:
                config['model'] = profile.aliyun.model
        return config

    @classmethod
    def is_available(cls):
        return diagnose.check_network_connection()

    def stt(self, filepath):
        wav_file = wave.open(filepath, 'rb')
        samplerate = wav_file.getframerate()
        n_frames = wav_file.getnframes()
        audiodata = wav_file.readframes(n_frames)
        request = self.create_request(audiodata,samplerate)
        response = urllib2.urlopen(request)
        return response
        

    def create_request(self, audiodata, samplerate=16000, version='2.0'):
        options = {
            'url': "https://nlsapi.aliyun.com/recognize?model=%s&version=%s" % (self.model, version),
            'method': 'POST',
            'body': audiodata,
            'headers': {
                'accept': 'application/json',
                'content-type': 'audio/wav;samplerate=%s'%samplerate,
                'date': get_current_date(),
                'authorization': '',
                'content-length': len(audiodata)
            }
        }
        
        body = ''
        if 'body' in options:
            body = options['body']
        bodymd5 = ''
        if not body == '':
            bodymd5 = to_md5_base64(body)
        # REST ASR 接口，需要做两次鉴权
        bodymd5 = to_md5_base64(bodymd5)
        stringToSign = options['method'] + '\n' + options['headers']['accept'] + '\n' + bodymd5 + '\n' + \
                       options['headers']['content-type'] + '\n' + options['headers']['date']
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
        
    def transcribe(self, fp):
        text = None
        try:
            data = self.stt(fp)
            data = json.load(data)
            text = data["result"]
        except KeyError:
            self._logger.critical('Cannot parse response.',exc_info=True)
            return None
        else:
            transcribed = None
            if text:
                transcribed = text.upper()
            self._logger.info(u'Transcribed: %s' % text)
            return transcribed
