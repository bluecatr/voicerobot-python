#!/usr/bin/env python2
# -*- coding: utf-8  -*-

import argparse
import logging
import os
import sys

from robot import stt, tts, utils, ear
from robot.brain import Brain
from robot.configuration import cmInstance
from robot.mouth import mouth


class VoiceRobot(object):
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self.config = cmInstance.getRootConfig()
  
        try:
            stt_engine_slug = self.config['stt_engine']
        except KeyError:
            pass
        stt_engine_class = stt.get_engine_by_slug(stt_engine_slug)
        self.stt = stt_engine_class.get_active_instance()
        
        try:
            tts_engine_slug = self.config['tts_engine']
        except KeyError:
            pass
        tts_engine_class = tts.get_engine_by_slug(tts_engine_slug)
        self.tts = tts_engine_class.get_instance()
        
        self.brain = Brain()
        
        mouth.setTTS(self.tts)
        
 
    def processAudio(self, userid, audiofile, returnType='text'):
        """
        userid is the wechat user id
        audiofile is the user's voice audio (amr file)
        returnType can be text or voice, if the type is voice, a file path will be returned.
        """
        result = self.transcribeAudio(audiofile)
        print "识别出来: %s" % result
        return self.processText(userid,result, returnType)
    
    
    def processText(self, userid, statement, returnType='text'):
        """
        userid is the wechat user id
        statement is the user's voice message
        returnType can be text or voice, if the type is voice, a file path will be returned.
        """
        #不要轻易更换wechat前缀，此前缀标示来自wechat的对话
        sessionId = "wechat_%s" % userid
        result = self.brain.query(statement,sessionId)
        text = result["answer"]
        
        if not utils.isJSON(text):
            if "voice" == returnType:
                if 'audio_cache' in result and result['audio_cache'] is not None:
                    return result['audio_cache']
                #150个字左右比较合适
                max_length = self.config['max_length']
                unicodetext = unicode(str(text),"utf-8")
                if len(unicodetext) > max_length:
                    text = "文字内容太多，以文本方式展示： %s" % text
                    return text
                return self.synthesiseAudio(text)
            elif "voice_text" == returnType:
                if 'audio_cache' in result and result['audio_cache'] is not None:
                    return result['audio_cache'] + ";" + text
                #150个字左右比较合适
                max_length = self.config['max_length']
                unicodetext = unicode(str(text),"utf-8")
                audiotext = text
                if len(unicodetext) > max_length:
                    audiotext = "文字太多，只读部分内容： %s" % unicodetext[0:max_length]
                return self.synthesiseAudio(audiotext) + ";" + text
        return text
        
    def process(self, userid, content, type, returnType='text'):
        result = None
        if type == "text":
            result = self.processText(userid, content, returnType)
        elif type == "voice":
            result = self.processAudio(userid, audiofile, returnType)
        return result
        
    def transcribeAudio(self,audiofile):
        wavAudiofile = utils.audiofileToWav(audiofile)
        result = self.stt.transcribe(wavAudiofile)
        os.remove(wavAudiofile)
        return result
    
    def synthesiseAudio(self,text):
        audiofile = self.tts.synthesise(text)
        if utils.isMp3Format(audiofile):
            mp3file = audiofile
        else: #默认都是wav格式
            mp3file = utils.wavToMP3(audiofile)
            os.remove(audiofile)
        
        #微信限制只能上传1分钟内容声音文件
        utils.cutMP3(mp3file, 59)
        return mp3file
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='WeChat Conversation Tool')
    parser.add_argument('content', help='The text statement from WeChat, if --file is specified, it is the audio file path')
    parser.add_argument('-u','--userid', help='the user id in current conversation session',required=True)
    parser.add_argument('-f','--file', action='store_true', help='use audio file as input, if not specified it, use text as default input')
    parser.add_argument('-t','--type', choices=["text","voice","voice_text"], help='specify the type of the output, if not specified it, use text as default output')
    args = parser.parse_args()
    
    logging.basicConfig()
    logger = logging.getLogger()
    logger.getChild("robot.brain").setLevel(logging.INFO)
    #logger.getChild("robot.brain.ai").setLevel(logging.DEBUG)
    logger.getChild("robot.hand").setLevel(logging.DEBUG)
#     logger.getChild("robot.utils").setLevel(logging.INFO)
    
    try:
        app = VoiceRobot()
        if args.file:
            audiofile = args.content
            print "the audio file: %s"%(audiofile)
            if not os.path.exists(audiofile):
                print "识别不出语音信息"
                sys.exit(1)
            answer = app.process(args.userid, audiofile,"voice",args.type)
        else:
            statement = args.content
            print "你: %s" %statement
            answer = app.process(args.userid, statement,"text",args.type)
             
#         if args.type and "voice" == args.type:
#             answer = "合成的语音文件在%s"% answer
        mouth.say(answer,echo=True)
    except Exception:
        logger.critical("Wechat Conversation Tool failed", exc_info=True)
        sys.exit(1)
