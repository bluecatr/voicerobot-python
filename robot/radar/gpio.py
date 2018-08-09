#coding:utf-8
import json
import logging
import subprocess
from threading import Thread
import time

from robot import utils
from robot.configuration import cmInstance
from robot.configuration.const import const

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

if utils.isPi():
    import RPi.GPIO as GPIO


class GPIOListener(Thread):
    
    def __init__(self):
        Thread.__init__(self,name ="GPIO Listener")
        self._logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.INFO)
        self.SWITCH_PIN = 14
        
        self.config = cmInstance.getRootConfig()
    
    def __del__(self):
        GPIO.cleanup()
        
    def run(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.SWITCH_PIN, GPIO.IN)
        GPIO.add_event_detect(self.SWITCH_PIN, GPIO.RISING, callback=self.callback, bouncetime=300)


    def callback(self,channel):
        persona = self.config.robot_name
        self._logger.info('Edge detected on channel %s'%channel)
#         cmd = ['aplay', str("/home/pi/voicerobot-python/static/audio/beep_hi.wav")]
#         subprocess.Popen(cmd)
        utils.publish(const.TOPIC_PASSIVE_LISTEN, json.dumps({"transcribed":persona,"threshold":None}))


def listenGPIO():
    try:
        if not utils.isPi():
            _logger.info("Current system don't support GPIO")
            return
        gpio = GPIOListener()
        gpio.setDaemon(True)
        gpio.start()
    except Exception,e:
        GPIO.cleanup()
        print e

if __name__ == "__main__":
    logging.basicConfig()
    listenGPIO()
    while True:
        time.sleep(10)
    