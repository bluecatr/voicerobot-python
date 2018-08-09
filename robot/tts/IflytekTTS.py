#coding:utf-8
from ctypes import *
import logging
import os
import pyaudio
import random
import tempfile
import time
import wave

from robot.configuration import cmInstance
from robot.configuration.const import const
from robot.tts import AbstractTTSEngine
from robot.utils import diagnose, Iflytek
from robot.utils.Iflytek import AppidQueue
from robot.utils.LameEncoder import LameEncoder
from robot.utils.SSML import translation


class IflytekTTS(AbstractTTSEngine):
    """
    科大讯飞
    http://www.xfyun.cn/
    iflytek:
        ostype: x64 # x64, x86, pi 分别和iflytek_msc libs下的文件名对应
        accounts:
            - appid : "appid1" # <configuration home>/iflytek_msc/appid1/libs/$ostype/libmsc.so
            - appid : "appid2" # <configuration home>/iflytek_msc/appid2/libs/$ostype/libmsc.so
        accent: mandarin # mandarin:普通话; cantonese:粤语
        voice_name: yufeng # xiaoyan 女;yanping 女;yufeng 男;babyxu 童声;xiaomeng 女;xiaolin 台湾女;xiaoqian 东北女;xiaorong 四川女;xiaokun 河南男;xiaoqiang 湖南男;xiaomei 粤语女;dalong 粤语男;catherine 美式纯英女;john 美式纯英男
    
    只有xiaoyan，yufeng和xiaomei支持CSSML标注，其他支持简单标注
    """
    SLUG = "iflytek-tts"
    
    def __init__(self, voice_name):
        self._logger = logging.getLogger(__name__)
        #self._logger.setLevel(logging.DEBUG)
        self.voice_name = voice_name
        self.audioFormat = "mp3" # or wav format
        if voice_name in ["xiaoyan","yufeng","xiaomei"]:
            self.translation_type = 'cssml'
        else:
            self.translation_type = 'simple'
    
    @classmethod
    def get_config(cls):
        config = {}
        profile = cmInstance.getConfig('voice_engines')
        if 'iflytek' in profile:
#             if 'accounts' in profile.iflytek:
#                 account = random.choice(profile.iflytek.accounts)
#                 config['appid'] = account.appid
            if 'voice_name' in profile.iflytek:
                config['voice_name'] = profile.iflytek.voice_name
            else:
                config['voice_name'] = "yanping"
        return config
    
    def login(self):
        ret = self.sdk.MSPLogin(None, None, self.login_params)
        if const.MSP_SUCCESS != ret:
            self._logger.error("MSPLogin failedm Error code %d.\n"%ret)
        self._logger.debug('MSPLogin => %s'% ret)
    
    def tts(self, text, session_begin_params):
        ret = c_int()
        sessionID = self.sdk.QTTSSessionBegin(session_begin_params, byref(ret))
        self._logger.debug('QTTSSessionBegin => sessionID: %s ret: %s'% (sessionID, ret.value))
        
        #input text
        ret = self.sdk.QTTSTextPut(sessionID, text, len(text), None)
        if const.MSP_SUCCESS != ret:
            self._logger.error("QTTSTextPut failed Error code %d.\n"%ret)
        else:
            self._logger.debug("QTTSTextPut SUCCESS=> %s"% ret)
        
        #systhesize audio
        audio_len = c_uint()
        synth_status = c_int()
        errorCode = c_int()
        lame = LameEncoder(const.RATE, const.CHANNEL, pyaudio.get_sample_size(pyaudio.paInt16))
        
        with tempfile.NamedTemporaryFile(suffix='.%s'%self.audioFormat,mode='w+b', delete=False) as f:
            audioFile = None
            if self.audioFormat == "mp3":
                audioFile = open(f.name, "wb+")
            else:
                audioFile = wave.open(f, "wb")
                # 配置声道数、量化位数、取样频率
                audioFile.setnchannels(const.CHANNEL)
                audioFile.setsampwidth(pyaudio.get_sample_size(pyaudio.paInt16))
                audioFile.setframerate(const.RATE)
        
            self._logger.debug('QTTSAudioGet => ')
            while True:
                self.sdk.QTTSAudioGet.restype = POINTER(c_ushort * (1024 * 1024))
                audio_data = self.sdk.QTTSAudioGet(sessionID, byref(audio_len), byref(synth_status), byref(errorCode))
                self._logger.debug('QTTSAudioGet => audio_len: %s synth_status: %s errorCode: %s'% (audio_len, synth_status,errorCode))
                if audio_data:
                    data = string_at(audio_data, audio_len.value)
                    if self.audioFormat == "mp3":
                        output = lame.encode(data)
                        audioFile.write(output)
                    else:
                        #将wav data 转换为二进制数据写入wav文件
                        audioFile.writeframes(data)
                if synth_status.value == const.MSP_TTS_FLAG_DATA_END or errorCode.value != const.MSP_SUCCESS:
                    break
                time.sleep(0.1)
                
            if self.audioFormat == "mp3":
                output = lame.flush()
                audioFile.write(output)
            audioFile.close()
            ret = self.sdk.QTTSSessionEnd(sessionID, "Normal")
            self._logger.debug('QTTSSessionEnd => ret: %s'% ret)
            f.seek(0)
            return f.name
        
    def logout(self):
        ret = self.sdk.MSPLogout()
        if const.MSP_SUCCESS != ret:
            self._logger.error("MSPLogout failed Error code %d.\n"%ret)
        else:
            self._logger.debug("MSPLogout SUCCESS=> %s"% ret)
    
    def synthesise(self, phrase):
        
        self.appid = AppidQueue.get()
        self.sdk = Iflytek.init_iflytck_sdk(self.appid)
        self.login_params = "appid = %s, work_dir = ." % self.appid
        self.session_begin_params = "voice_name=%s,text_encoding=UTF8,sample_rate= %s,speed=70,volume=50,pitch=50,rdn=2,ttp=ssml" \
                                % (self.voice_name, const.RATE)
                                
        self._logger.debug("Synthesise '%s' with '%s'", phrase, self.SLUG)
        self.login()
        translatedText = translation(phrase,self.translation_type)
        self._logger.debug("The translated text is '%s'", translatedText)
        audiofile = self.tts(str(translatedText),self.session_begin_params)
        self.logout()
        AppidQueue.put(self.appid)
        return audiofile
        
    @classmethod
    def is_available(cls):
        return diagnose.check_network_connection()
