#coding:utf-8
from jpype import startJVM, getDefaultJVMPath, JClass
import json
import logging

from robot import configuration, utils
from robot.brain.ai import AbstractAIEngine
from robot.configuration import cmInstance


class TulingAI(AbstractAIEngine):

    SLUG = "tuling-ai"
    
    def __init__(self, APIkey, secret=None):
        self._logger = logging.getLogger(__name__)
        self.APIkey = APIkey
        self.secret = secret
    
    @classmethod
    def get_config(cls):
        config = {}
        profile = cmInstance.getConfig('ai_engines')
        if 'tuling' in profile:
            if 'APIkey' in profile.tuling:
                config['APIkey'] = profile.tuling.APIkey
            if 'secret' in profile.tuling:
                config['secret'] = profile.tuling.secret
        return config
    
    def getDataBody(self,msg):
        if self.secret and self.secret != '':
            jarpath = ":".join([configuration.tools('tuling','tuling.jar'),
                       configuration.tools('tuling','commons-codec-1.10.jar'),
                       configuration.tools('tuling','fastjson-1.2.37.jar')])
            startJVM(getDefaultJVMPath(), "-ea", "-Djava.class.path=%s" % jarpath)
            Tuling = JClass('com.turing.Tuling')
            body = json.loads(Tuling.getSecretData(self.APIkey,self.secret,msg))
        else:
            body = {'key': self.APIkey, 'info': msg}
        return body
    
    def chat(self, texts, session=None):
        """
        使用图灵机器人聊天

        Arguments:
        texts -- user input, typically speech, to be parsed by a module
        """
        msg = texts
        try:
            url = "http://www.tuling123.com/openapi/api"
            body = self.getDataBody(msg)
            respond = utils.restpost(url,body)
            result = ''
            if respond['code'] == 100000:
                result = respond['text'].replace('<br>', '  ')
                result = result.replace(u'\xa0', u' ')
            elif respond['code'] == 200000:
                result = respond['url']
            elif respond['code'] == 302000:
                for k in respond['list']:
                    result = result + u"【" + k['source'] + u"】 " +\
                             k['article'] + "\t" + k['detailurl'] + "\n"
            else:
                result = respond['text'].replace('<br>', '  ')
                result = result.replace(u'\xa0', u' ')
   
            return result
        except Exception:
            self._logger.critical("TulingAI failed to responsed for %r",
                                  msg, exc_info=True)
            return _("I'm sorry. I had some trouble with that operation. Please try again later.")
        
    @classmethod
    def is_available(cls):
        profile = cmInstance.getConfig('ai_engines')
        if 'tuling' in profile:
            return True
        else:
            return False