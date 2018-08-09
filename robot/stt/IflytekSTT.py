#coding:utf-8
from ctypes import *
import logging
import os
import wave
import random
import sys
import time
import json

from robot import configuration
from robot.utils import diagnose
from robot.configuration import cmInstance
from robot.configuration.const import const
from robot.stt import AbstractSTTEngine


class IflytekSTT(AbstractSTTEngine):
    """
    科大讯飞
    http://www.xfyun.cn/
    iflytek:
        ostype: x64 # x64, x86, pi 分别和iflytek_msc libs下的文件名对应
        accounts:
            - appid : "appid1" # <configuration home>/iflytek_msc/appid1/libs/$ostype/libmsc.so
            - appid : "appid2" # <configuration home>/iflytek_msc/appid2/libs/$ostype/libmsc.so
        accent: mandarin # mandarin:普通话; cantonese:粤语
        voice_name: yanping # yanping 女;yufeng 男;babyxu 童声;xiaomeng 女;xiaolin 台湾女;
                xiaoqian 东北女;xiaorong 四川女;xiaokun 河南男;xiaoqiang 湖南男;xiaomei 粤语女;dalong 粤语男;catherine 美式纯英女;john 美式纯英男
    """
    
    SLUG = "iflytek-stt"
    
    def __init__(self, appid,ostype,accent):
        self._logger = logging.getLogger(__name__)
        self.appid = appid
        sofile = configuration.config("iflytek_msc",appid,"libs",ostype,"libmsc.so")
        self._logger.debug("Loading iflytec msc libaray file: %s" % sofile)
        self.sdk = cdll.LoadLibrary(sofile) #sr: speech recognition
        self.login_params = "appid = %s, work_dir = ." % appid
        
        new_session_begin_params = "sch=1,nlp_version=3.0,scene=main,"
#         if ostype == 'pi':
#             new_session_begin_params = ""
        self.session_begin_params =  new_session_begin_params + "sub=iat,aue=speex-wb;7,result_type=plain,result_encoding=utf8," \
            "language=zh_cn,accent=" + accent + ",sample_rate=%s,domain=iat"
        self.grammar_id = None  #当需要连续语音识别时，设为None

        
    @classmethod
    def get_config(cls):
        config = {}
        profile = cmInstance.getConfig('voice_engines')
        if 'iflytek' in profile:
            if 'ostype' in profile.iflytek:
                config['ostype'] = profile.iflytek.ostype
            else:
                config['ostype'] = "x64"
            if 'accounts' in profile.iflytek:
                account = random.choice(profile.iflytek.accounts)
                config['appid'] = account.appid
            if 'accent' in profile.iflytek:
                config['accent'] = profile.iflytek.accent
            else:
                config['accent'] = "mandarin"
        return config
    
    def login(self):
        ret = self.sdk.MSPLogin(None, None, self.login_params)
        if const.MSP_SUCCESS != ret:
            self._logger.error("MSPLogin failedm Error code %d.\n"%ret)
        self._logger.debug('MSPLogin => %s'% ret)
        
    def stt(self, audiofile, session_begin_params, grammar_id):
        try:
            wav_file = wave.open(audiofile, 'rb')
        except IOError:
            self._logger.critical('wav file not found: %s',
                                  audiofile,
                                  exc_info=True)
        
        frame_rate = wav_file.getframerate()
        session_begin_params = session_begin_params % frame_rate
        self._logger.debug("QISRSessionBegin parameters: %s" % session_begin_params)
        
        data = ''
        ret = c_int()
        sessionID = self.sdk.QISRSessionBegin(grammar_id, session_begin_params, byref(ret))
        self._logger.debug('QISRSessionBegin => sessionID: %s ret: %s'% (sessionID, ret.value))

        epStatus = c_int(0)
        recogStatus = c_int(0)
        times = 0
        while True:
            wavData = wav_file.readframes(const.CHUNK)
            if len(wavData) == 0:
                break
            
            aud_stat = const.MSP_AUDIO_SAMPLE_CONTINUE
            if times == 0:
                aud_stat = const.MSP_AUDIO_SAMPLE_FIRST
            
            ret = self.sdk.QISRAudioWrite(sessionID, wavData, len(wavData), aud_stat, byref(epStatus), byref(recogStatus))
            self._logger.debug('len(wavData): %s QISRAudioWrite ret: %s epStatus: %s recogStatus: %s' % (len(wavData), ret, epStatus, recogStatus))
            time.sleep(0.02)
            times += 1

            if epStatus.value == const.MSP_EP_AFTER_SPEECH:
                break

        ret = self.sdk.QISRAudioWrite(sessionID, None, 0, const.MSP_AUDIO_SAMPLE_LAST, byref(epStatus), byref(recogStatus))
        if const.MSP_SUCCESS != ret:
            self._logger.error("QISRAudioWrite failed! error code:%d"%ret)
            return data
        self._logger.debug('QISRAudioWrite ret: %s epStatus: %s recogStatus: %s' % (ret, epStatus, recogStatus))

        #获取音频
        while recogStatus.value != const.MSP_REC_STATUS_COMPLETE:
            ret = c_int()
            self.sdk.QISRGetResult.restype = c_char_p
            retstr = self.sdk.QISRGetResult(sessionID, byref(recogStatus), 0, byref(ret))
            if retstr is not None:
                data += retstr
            self._logger.debug('ret: %s recogStatus: %s'% (ret, recogStatus))
            time.sleep(0.2)

        return data

    def logout(self):
        ret = self.sdk.MSPLogout()
        if const.MSP_SUCCESS != ret:
            self._logger.error("MSPLogout failed Error code %d.\n"%ret)
        else:
            self._logger.debug("MSPLogout SUCCESS=> %s"% ret)
    
    def transcribe(self, fp):
        text = None
        try:
            self.login()
            data = self.stt(fp, self.session_begin_params, self.grammar_id)
            if data.strip() != '':
                try: 
                    data = json.loads(data)
                    text = data["text"]
                except ValueError: 
                    self._logger.debug('Get the original string response')
                    text = data
        except KeyError:
            self._logger.critical('Cannot parse response.',exc_info=True)
            return None
        else:
            transcribed = None
            if text:
                transcribed = text.upper()
            self._logger.info(u'Transcribed: %s' % text)
            self.logout()
            return transcribed
        
    
    @classmethod
    def is_available(cls):
        return diagnose.check_network_connection()
    
