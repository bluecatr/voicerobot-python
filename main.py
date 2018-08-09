#!/usr/bin/env python2
#coding:utf-8

import argparse
import logging
import os
import sys

from robot import configuration
from robot import ear
from robot import radar
from robot import stt
from robot import tts
from robot.configuration import cmInstance
from robot.conversation import Conversation
from robot.mouth import mouth
from robot.utils import diagnose


# from robot.tts import SimpleMp3Player
sys.path.append(configuration.LIB_PATH)

parser = argparse.ArgumentParser(description='Voice Control Center')
parser.add_argument('-nnc','--no-network-check', action='store_true',
                    help='Disable the network connection check')
parser.add_argument('-d','--diagnose', action='store_true',
                    help='Run diagnose and exit')
parser.add_argument("-ll", "--loglevel", choices=["debug","info"],
                    help="Show the message under the specified log level")
args = parser.parse_args()

class VoiceRobot(object):
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        
        self.config = cmInstance.getRootConfig()
        try:
            stt_engine_slug = self.config['stt_engine']
        except KeyError:
            stt_engine_slug = 'sphinx-stt'
            logger.warning("stt_engine not specified in profile, defaulting " +
                           "to '%s'", stt_engine_slug)
        stt_engine_class = stt.get_engine_by_slug(stt_engine_slug)
  
        try:
            tts_engine_slug = self.config['tts_engine']
        except KeyError:
            tts_engine_slug = tts.get_default_engine_slug()
            logger.warning("tts_engine not specified in profile, defaulting " +
                           "to '%s'", tts_engine_slug)
        tts_engine_class = tts.get_engine_by_slug(tts_engine_slug)
  
        try:
            mic_slug = self.config['active_mic']
        except KeyError:
            mic_slug = ear.get_default_mic_slug()
            logger.warning("active_mic not specified in profile, defaulting " +
                           "to '%s'", mic_slug)
        mic_class = ear.get_mic_by_slug(mic_slug)
        self.ear = mic_class.get_instance(stt_engine_class.get_active_instance())
        
        mouth.setTTS(tts_engine_class.get_instance())
        
    def run(self):
        if 'first_name' in self.config:
            salutation = (_("How can I be of service, %s?")
                          % self.config["first_name"])
        else:
            salutation = _("How can I be of service?")
        mouth.say(salutation)
 
        persona = ''
        if 'robot_name' in self.config:
            persona = self.config["robot_name"]
        
        radar.start()
        conversation = Conversation(persona, self.ear)
        conversation.handleForever()


if __name__ == "__main__":

    print "*******************************************************"
    print "*                  中文语音对话机器人                    *"
    print "*******************************************************"

    logging.basicConfig()
    logger = logging.getLogger()
    
    #always show robot.stt log in INFO level 
    logger.setLevel(logging.INFO)
#     logger.getChild("robot.tts").setLevel(logging.INFO)
#     logger.getChild("robot.hand").setLevel(logging.INFO)
    #logger.getChild("robot.stt.IflytekSTT").setLevel(logging.DEBUG)
#     logger.getChild("robot.conversation").setLevel(logging.DEBUG)
#     logger.getChild("robot.mouth").setLevel(logging.DEBUG)

    if args.loglevel == "debug":
        logger.setLevel(logging.DEBUG)
    elif args.loglevel == "info":
        logger.setLevel(logging.INFO)

    if not args.no_network_check and not diagnose.check_network_connection():
        logger.warning("Network not connected. This may prevent VoiceRobot " +
                       "from running properly.")
 
    if args.diagnose:
        failed_checks = diagnose.run()
        sys.exit(0 if not failed_checks else 1)
 
    try:
        app = VoiceRobot()
    except Exception:
        logger.error("Error occured!", exc_info=True)
        sys.exit(1)
  
    app.run()
