#!/usr/bin/env python2
#coding:utf-8

import json
import logging
import os
from paho.mqtt.client import Client
import sys
import time

from robot import utils
from robot.configuration import cmInstance
from robot.configuration.const import const
from robot.ear.ReSpeaker7ArrayMic import ReSpeaker7ArrayMic


# from robot.ear.ReSpeaker7ArrayMic import ReSpeaker7ArrayMic
class VoiceRobot(object):
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self.config = cmInstance.getRootConfig()
 
    def testconfig(self):
        #print self.config
        try:
#             print self.config.homeassistant
#             print self.config.homeassistant.broadlink
#             print self.config.homeassistant["broadlink"].services
#             print self.config.homeassistant.broadlink.services
#             print self.config.homeassistant.broadlink.codes
#             print self.config.homeassistant.broadlink.codes.tv_up
#             print self.config.homeassistant.broadlink.tasks
#             print self.config.homeassistant.broadlink.tasks.tv_power_on.service
#             print self.config.homeassistant.hass_tasks.bed_room_light_on
            
            
            print self.config.homeassistant.hass_tasks.tv_power_on.service
            service_url = "".join(self.config.homeassistant.hass_tasks.tv_power_on.service)
            print service_url
            
            print self.config.has_key("2array_mic_hat")
            
        except Exception as e:
            print e.message




    def test2Array(self):
        try:
            if self.config.has_key("2array_mic_hat"):
                sys.path.append(self.config["2array_mic_hat"])
                from pixels import Pixels
                pixels = Pixels()
                pixels.wakeup()
                time.sleep(3)
                pixels.off()
                time.sleep(2)
                pixels.think()
                time.sleep(3)
                for i in range(0,5):
                    pixels.speak()
                    time.sleep(1)
                
                pixels.off()
                time.sleep(1)
        except Exception as e:
            print e.message
    
    def test7Array(self):
        try:
            sys.path.append("/home/huyd/workspace/mic_array")
            from pixel_ring import PixelRing
            pixels = PixelRing()


            #wakeup
#             pixels.arc(12)
#             time.sleep(3)
#              
#             #think
#             pixels.spin()
#             time.sleep(6)
            
            #speak
#             for level in range(0, 13):
#                 pixels.set_direction(level * 30)
#                 time.sleep(1)

            level = 0
            while level < 13:
                pixels.set_direction(level * 30)
                time.sleep(1)
                level += 1
                if level == 13:
                    level = 1
#             for level in range(1, 13):
#                 pixels.arc(level)
#                 time.sleep(1)

            pixels.off()
                
        except Exception as e:
            print e.message
            
    def testConst(self):
        print type(const)
        const.CHANNEL = 2
        
        print const.CHANNEL
        
        const.CHANNEL = 1
        
        print const.CHANNEL
        
        
    def testMic(self):
        mic = ReSpeaker7ArrayMic(None,None,None)
        #wakeup
        mic.Pixels.wakeup()
        time.sleep(3)
          
        #think
        mic.Pixels.think()
        time.sleep(3)
         
        #think
        mic.Pixels.speak()
        time.sleep(3)
        
        mic.Pixels.off()()
    
    def testpubsub(self):
        client = Client()
        HOST = "localhost"

        client.connect(HOST, 1883, 60)
        topic = "TOPIC_PASSIVE_LISTEN"
        while True:
            str = raw_input()
            if str:
                client.publish(topic, json.dumps({"transcribed":"HEYXIAORUI","threshold":None}))
    #             Publish.single("chat", json.dumps({"user": user, "say": str}))
#                 Publish.single(topic, json.dumps({"transcribed":"HEYXIAORUI","threshold":None}))
    
    
if __name__ == "__main__":
    try:
        app = VoiceRobot()
        #app.testconfig()
        #app.test2Array()
        #app.test7Array()
        #app.testConst()
        #app.testMic()
        app.testpubsub()
    except Exception,e:
        print e
        sys.exit(1)
 
    #app.run()
