#coding:utf-8
import json
import logging
import sys
import threading
import time

from brain import Brain
#from notifier import Notifier
from robot import utils, stt
from robot.configuration import cmInstance
from robot.configuration.const import const
from robot.mouth import mouth


class Conversation(object):
    
    def __init__(self, persona, ear):
        self._logger = logging.getLogger(__name__)
        self.persona = persona
        self.mic = ear
        self.profile = cmInstance.getRootConfig()
        self.brain = Brain()
        #self.notifier = Notifier(self.brain)

    def listenKeyword(self):
        try:
            slug = self.profile['stt_passive_engine']
            stt_passive_engine_class = stt.get_engine_by_slug(slug)
        except KeyError:
            pass
            
        passive_stt_engine = stt_passive_engine_class.get_passive_instance()
        while True:
            self._logger.debug("Started listening for keyword '%s'",
                                   self.persona)
            threshold, transcribed = self.mic.passiveListen(passive_stt_engine,self.persona)
            #threshold, transcribed = None,None
            self._logger.debug("Stopped listening for keyword '%s'",
                               self.persona)
            if transcribed and threshold:
                utils.publish(const.TOPIC_PASSIVE_LISTEN, json.dumps({"transcribed":transcribed,"threshold":threshold}))
            else:
                self._logger.debug("Nothing has been said or transcribed.")
            time.sleep(0.1)
    
    event = threading.Event()
    def wakeup(self, client, userdata, msg):
        payload = json.loads(msg.payload)
        self.threshold =  payload.get("threshold")
        self._logger.debug("Keyword '%s' has been said!", self.persona)
        if mouth.isSaying():
            mouth.shutup()
            time.sleep(0.1)
        self._logger.info("wake up event set")
        self.event.set()
        
    def listenAndThink(self,threshold):
        self._logger.debug("Started to listen actively with threshold: %r",
                          threshold)
        self.mic.Pixels.wakeup()
        voicemessage = self.mic.activeListen(threshold)
        self._logger.debug("Stopped to listen actively with threshold: %r",
                          threshold)
        
        self.mic.Pixels.think()
        result = None
        audio_cache = None
        if voicemessage:
            result = self.brain.query(voicemessage)
            answer = result["answer"]
            if 'audio_cache' in result and result['audio_cache'] is not None:
                audio_cache = result['audio_cache']
            if 'needInfo' in result and result['needInfo']:
                self.mic.Pixels.speak()
                if audio_cache:
                    self._logger.info("Cached audio file %s exist, play it without synthesize." % audio_cache)
                    mouth.play(audio_cache)
                else:
                    mouth.say(answer)
                answer,audio_cache = self.listenAndThink(threshold)
        else:
            answer = _("Pardon?")
        return answer,audio_cache
            
    def handleForever(self):
        """
        Delegates user input to the handling function when activated.
        """
        self._logger.info("Starting to handle conversation with keyword '%s'.",self.persona)
        utils.subscribe(const.TOPIC_PASSIVE_LISTEN, self.wakeup)
        
        #树莓派不使用被动听
        if not utils.isPi():
            thread = threading.Thread(target=self.listenKeyword)
            thread.setDaemon(True)
            thread.start()
        
        while True:
            self.event.wait()
            answer,audio_cache = self.listenAndThink(self.threshold)
            
            self.mic.Pixels.speak()
            self._logger.info("Answer: %s" % answer)
            
            max_length = cmInstance.getConfig('max_length')
            unicodetext = unicode(str(answer),"utf-8")
            if len(unicodetext) > max_length:
                mouth.say('文字内容太多，是否需要全部读出，请在滴一声后进行确认')
                input = self.mic.activeListen()
                if input and any(word in input for word in ["确认", "可以", "好的", "是", "OK"]):
                    self.mic.Pixels.speak()
                    if audio_cache:
                        self._logger.info("Cached audio file %s exist, play it without synthesize." % audio_cache)
                        mouth.play(audio_cache)
                    else:
                        mouth.say(answer)
            else:
                if audio_cache:
                    self._logger.info("Cached audio file %s exist, play it without synthesize." % audio_cache)
                    mouth.play(audio_cache)
                else:
                    mouth.say(answer)
            
            self.mic.Pixels.off()
            self._logger.info("wake up event clear")
            self.event.clear()

