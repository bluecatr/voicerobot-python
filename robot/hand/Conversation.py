#coding:utf-8
import logging
import os
import subprocess
import threading

from robot import utils, configuration
from robot.configuration import cmInstance
from robot.hand import AbstractController
from robot.mouth import mouth
from robot.tts import IflytekTTS


class ConversationController(AbstractController):
    SLUG = "conversation"

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self.cachePath = configuration.data("audio","cache")
        self.audioFormat = "mp3" # or wav format
        
    def handleControl(self, session, answer, control):
        isWechat = False
        if session:
            isWechat = session.startswith('wechat')
        
        parameters = control.parameters
        static = False
        cachefile = None
        if 'static' in parameters:
            static = parameters.static
        
        #处理各个action
        if control.action.lower() == "reply_answer":
            if static:
                cachefile = self.checkAndCreateCachFile("",parameters,answer)
                return {"answer":answer,"audio_cache": cachefile}

        if control.action.lower() == "ask_question":
            if isWechat:
                if static:
                    cachefile = self.checkAndCreateCachFile("WQ_",parameters,answer)
            else:
                answer = "%s，请在滴一声后进行回复"%answer
                if static:
                    cachefile = self.checkAndCreateCachFile("Q_",parameters,answer)
                    
            return {"answer":answer,"audio_cache": cachefile,"needInfo": True}
        return None

    def checkAndCreateCachFile(self,prefix,parameters,answer):
        identity = prefix
        #intent是必须的，否则不缓存
        if 'intent' in parameters:
            identity = identity  + parameters.intent
        else:
            return None

        if 'entity' in parameters:
            if type(parameters.entity) == unicode:
                identity = identity + "_" + parameters.entity
            else:
                identity = identity + "_" + parameters.entity.entityName
            
        cachefile = os.path.join(self.cachePath,identity) + "." + self.audioFormat
        if not os.path.exists(cachefile):
            self._logger.debug("Cache file %s doesn't exist, create it in backend." % cachefile)
            #利用单开进程的方式解决科大讯飞不能在子线程中运行的问题
            if "iflytek-tts" == cmInstance.config['tts_engine']:
                cmd = ['python', os.path.join(configuration.APP_PATH,"iflytektool.py"),answer,cachefile]
                subprocess.Popen(cmd)
            else:
                thread = threading.Thread(target=self.createCacheFile,args=(answer,cachefile))
                thread.start()
            cachefile = None
        return cachefile
        
    def createCacheFile(self,answer,cachefile):
        audiofile = mouth.say_in_silence(answer)
        utils.movefile(audiofile, cachefile)
        
    @classmethod
    def is_available(cls):
        return True