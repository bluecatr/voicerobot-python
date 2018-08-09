#coding:utf-8
"""
    The Mic class handles all interactions with the Respeaker 2 microphone array
    
    Repuirements:
    None
    
"""
import sys
import threading
import time

from robot import configuration
from robot.configuration import cmInstance
from robot.ear.BaseMic import BaseMic


sys.path.append(configuration.tools("respeaker"))

if cmInstance.getConfig("active_mic") == "respeaker-7mic":
    class ReSpeaker7ArrayMic(BaseMic):
        
        SLUG = "respeaker-7mic"
            
        class Pixels:
            from pixel_ring import PixelRing
            pixels = PixelRing()
            listening = False
            
            @classmethod
            def wakeup(cls):
                cls.pixels.arc(12)
                
            @classmethod
            def listen(cls):
                cls.listening = True
                thread = threading.Thread(target=cls._listen)
                thread.start()
            
            @classmethod
            def _listen(cls):
                level = 0
                while level < 13 and cls.listening:
                    cls.pixels.set_direction(level * 30)
                    time.sleep(1)
                    level += 1
                    if level == 13:
                        level = 1
                        
            @classmethod
            def think(cls):
                cls.listening = False
                cls.pixels.set_color(rgb=0xFF0000)
            
            @classmethod
            def speak(cls):
                cls.listening = False
                cls.pixels.spin()
            
            @classmethod
            def off(cls):
                cls.listening = False
                try: 
                    cls.pixels.off()
                except Exception,e:
                    cls.pixels.off()
                    print e


