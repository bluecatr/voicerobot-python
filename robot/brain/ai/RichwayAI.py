#coding:utf-8
import logging

from robot import utils
from robot.brain.ai import AbstractAIEngine
from robot.configuration import cmInstance


class RichwayAI(AbstractAIEngine):

    SLUG = "richway-ai"
    
    def __init__(self, service_url, robotId, sessionId=None, unknown_reply=None):
        self._logger = logging.getLogger(__name__)
        self.serviceurl = service_url
        self.robotId = robotId
        self.sessionId = sessionId
        self.unknown_reply = unknown_reply
    
    @classmethod
    def get_config(cls):
        config = {}
        profile = cmInstance.getConfig('ai_engines')
        if 'richway' in profile:
            if 'service_url' in profile.richway:
                config['service_url'] = profile.richway.service_url
            if 'robotId' in profile.richway:
                config['robotId'] = profile.richway.robotId
            if 'sessionId' in profile.richway:
                config['sessionId'] = profile.richway.sessionId
            if 'unknown_reply' in profile.richway:
                config['unknown_reply'] = profile.richway.unknown_reply
        return config
    
    def chat(self, texts, sessionId=None):
        if not sessionId:
            sessionId = self.sessionId
        
        session = "robotId=%s,sessionId=%s" % (self.robotId,sessionId)
        msg = texts
        databody = {'session':session,'message':msg}
        answer = None
        control = None
        try:
            response = utils.restpost(self.serviceurl, databody)
            if response:
                self._logger.debug("RichwayAI reply '%s'", response)
                if 'conversation' in response:
                    answer = response['conversation'].encode('utf-8')
                if 'control' in response and response['control']:
                    control = response['control']
            if self.unknown_reply and answer in self.unknown_reply:
                self._logger.info("RichwayAI can not understand the voice message and reply '%s'", answer)
                answer =  None
        except Exception:
            self._logger.critical("RichwayAI failed to responsed for %r",
                                  msg, exc_info=True)
            return _("I'm sorry. I had some trouble with that operation. Please try again later.")
        return answer,control
        
    @classmethod
    def is_available(cls):
        profile = cmInstance.getConfig('ai_engines')
        if 'richway' in profile:
            return True
        else:
            return False