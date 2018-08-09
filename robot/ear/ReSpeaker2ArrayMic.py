#coding:utf-8
"""
    The Mic class handles all interactions with the Respeaker 2 microphone array
    
    Repuirements:
    sudo pip install spidev
    
"""
import sys

from robot import configuration
from robot.configuration import cmInstance
from robot.ear.BaseMic import BaseMic


sys.path.append(configuration.tools("respeaker"))
if cmInstance.getConfig("active_mic") == "respeaker-2mic":
    class ReSpeaker2ArrayMic(BaseMic):
        SLUG = "respeaker-2mic"
    
        class Pixels:
            from pixels import Pixels
            pixels = Pixels()
            thinking = False
            
            @classmethod
            def wakeup(cls):
                cls.pixels.wakeup()
                
            @classmethod
            def think(cls):
                cls.pixels.think()
                        
            @classmethod
            def speak(cls):
                cls.thinking = False
                cls.pixels.spin()
            
            @classmethod
            def off(cls):
                cls.thinking = False
                cls.pixels.off()
            
