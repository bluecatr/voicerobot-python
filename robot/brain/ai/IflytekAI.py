#coding:utf-8
from ctypes import *
import json
import logging
import random
import time

from robot import configuration
from robot.brain.ai import AbstractAIEngine
from robot.configuration import cmInstance
from robot.configuration.const import const


class IflytekAI(AbstractAIEngine):

    SLUG = "iflytek-ai"
    
    def __init__(self, appid,ostype):
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
        self.appid = appid
        sofile = configuration.config("iflytek_msc",appid,"libs",ostype,"libmsc.so")
        self._logger.debug("Loading iflytec msc libaray file: %s" % sofile)
        self.sdk = cdll.LoadLibrary(sofile) #ss:speech synthesis
        self.login_params = "appid = %s, work_dir = ." % appid
        self.semantic_params = "nlp_version = 3.0, scene = main"
    
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
        return config
    
    def login(self):
        ret = self.sdk.MSPLogin(None, None, self.login_params)
        if const.MSP_SUCCESS != ret:
            self._logger.error("MSPLogin failedm Error code %d.\n"%ret)
        self._logger.debug('MSPLogin => %s'% ret)
        
    def chat(self, texts, sessionId=None):
        self.login()
        errorCode = c_int()
        len = c_uint()
        self.sdk.MSPSearch.restype = c_char_p
        result = self.sdk.MSPSearch(self.semantic_params, texts, byref(len), byref(errorCode))
        self._logger.debug('len: %s errocode: %s result: %s'% (len, errorCode,result))
        self.logout()

        answer =  None
        if errorCode.value == const.MSP_SUCCESS:
            #print result
            jsobj = json.loads(result)
            """
            0    操作成功
            1    输入异常
            2    系统内部异常
            3    业务操作失败，错误信息在error字段描述
            4    文本没有匹配的技能场景，技能不理解或不能处理该文本
            """
            if jsobj['rc'] == 4:
                answer = jsobj['text']
            elif jsobj['rc'] == 3:
                error = jsobj['error']
                self._logger.debug('error: %s'% (error))
                text = jsobj['answer']['text']
                answer = "，".join(text.split('"，"'))
            elif jsobj['rc'] == 0:
                if jsobj['service'] == "poetry":
                    answer = self.poetry(jsobj)
#                 elif jsobj['service'] == "weather":
#                     answer = self.weather(jsobj)
                elif jsobj['service'] == "datetime":
                    text = jsobj['answer']['text']
                    answer = "，".join(text.split('"，"'))
                else:
                    if jsobj['state']:
                        text = jsobj['answer']['text']
                        answer = "，".join(text.split('"，"'))
        return answer,None
        
    def logout(self):
        ret = self.sdk.MSPLogout()
        if const.MSP_SUCCESS != ret:
            self._logger.error("MSPLogout failed Error code %d.\n"%ret)
        else:
            self._logger.debug("MSPLogout SUCCESS=> %s"% ret)
            
    @classmethod
    def is_available(cls):
        profile = cmInstance.getConfig('ai_engines')
        if 'richway' in profile:
            return True
        else:
            return False
        
        
    def poetry(self,jsobj):
        return jsobj['data']['result'][0]['content']
    
    def weather(self,jsobj):
        return jsobj['data']['result'][0]['content']