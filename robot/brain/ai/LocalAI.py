#coding:utf-8
import logging

from robot import utils
from robot.brain.ai import AbstractAIEngine
from robot.configuration import cmInstance


class LocalAI(AbstractAIEngine):

    SLUG = "local-ai"
    
    def __init__(self):
        self._logger = logging.getLogger(__name__)
    
    @classmethod
    def get_config(cls):
        config = {}
        return config
    
    def chat(self, texts, session=None):
        text = ''.join(texts)
        if utils.checkKeyWords(text,["电视","投影"]):
            if utils.checkKeyWords(text,["打开","开"]):
                taskname = "tv_power_on"
            elif utils.checkKeyWords(text,["关闭","关"]):
                taskname = "tv_power_off"
            elif utils.checkKeyWords(text,["导航"]):
                pass
        elif utils.checkKeyWords(text,["空调"]):
            if utils.checkKeyWords(text,["打开","开"]):
                taskname = "air_power_on"
            elif utils.checkKeyWords(text,["关闭","关"]):
                taskname = "air_power_off"
            elif utils.checkKeyWords(text,["温度"]):
                if utils.checkKeyWords(text,["升高","调高"]):
                    taskname = "air_temp_up"
                elif utils.checkKeyWords(text,["降低","调低"]):
                    taskname = "air_temp_down"
        elif utils.checkKeyWords(text,["电扇"]):
            if utils.checkKeyWords(text,["打开","开"]):
                taskname = "fan_power_on"
            elif utils.checkKeyWords(text,["关闭","关"]):
                taskname = "fan_power_off"
        elif utils.checkKeyWords(text,["水循环"]):
            if utils.checkKeyWords(text,["打开","开"]):
                taskname = "water_power_on"
            elif utils.checkKeyWords(text,["关闭","关"]):
                taskname = "water_power_off"
        elif utils.checkKeyWords(text,["白灯","书房灯"]):
            if utils.checkKeyWords(text,["打开","开"]):
                taskname = "white_light_on"
            elif utils.checkKeyWords(text,["关闭","关"]):
                taskname = "white_light_off"
        elif utils.checkKeyWords(text,["彩灯","客厅灯"]):
            if utils.checkKeyWords(text,["打开","开"]):
                taskname = "color_light_on"
            elif utils.checkKeyWords(text,["关闭","关"]):
                taskname = "color_light_off"
        
        answer = None
        return answer

    @classmethod
    def is_available(cls):
        return True
