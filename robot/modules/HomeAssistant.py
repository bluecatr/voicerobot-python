#coding:utf-8
import logging

from robot.configuration import cmInstance
from robot.utils import restpost


WORDS = ["DIANSHI"]
SLUG = "homeassistant"
PRIORITY = 1

def executeTask(taskname=None):
    try:
        profile = cmInstance.getRootConfig()
        service_url = "".join(profile.homeassistant.hass_tasks[taskname].service)
        data = profile.homeassistant.hass_tasks[taskname].data
        response =  restpost(service_url,data)
        if response == "[]":
            return False
    except Exception as e:
        print e.message
        raise
    return True

def handle(text):
    """
        Control the smart devices through Home Assistant

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone
                   number)
    """
    logger = logging.getLogger(__name__)
    errorMessage = u"%s没有执行成功，请确认您的命令" % text
    successMessage = u"%s执行完成" % text
    success = False
    taskname = None
    if any(word in text for word in ["电视","投影"]):
        if any(word in text for word in ["打开","开"]):
            taskname = "tv_power_on"
        elif any(word in text for word in ["关闭","关"]):
            taskname = "tv_power_off"
        elif any(word in text for word in ["导航"]):
            pass
    elif any(word in text for word in ["空调"]):
        if any(word in text for word in ["打开","开"]):
            taskname = "air_power_on"
        elif any(word in text for word in ["关闭","关"]):
            taskname = "air_power_off"
        elif any(word in text for word in ["温度"]):
            if any(word in text for word in ["升高","调高"]):
                taskname = "air_temp_up"
            elif any(word in text for word in ["降低","调低"]):
                taskname = "air_temp_down"
    elif any(word in text for word in ["电扇"]):
        if any(word in text for word in ["打开","开"]):
            taskname = "fan_power_on"
        elif any(word in text for word in ["关闭","关"]):
            taskname = "fan_power_off"
    elif any(word in text for word in ["水循环"]):
        if any(word in text for word in ["打开","开"]):
            taskname = "water_power_on"
        elif any(word in text for word in ["关闭","关"]):
            taskname = "water_power_off"
    elif any(word in text for word in ["白灯","书房灯"]):
        if any(word in text for word in ["打开","开"]):
            taskname = "white_light_on"
        elif any(word in text for word in ["关闭","关"]):
            taskname = "white_light_off"
    elif any(word in text for word in ["彩灯","客厅灯"]):
        if any(word in text for word in ["打开","开"]):
            taskname = "color_light_on"
        elif any(word in text for word in ["关闭","关"]):
            taskname = "color_light_off"
            
    if taskname:
        logger.info("Execute %s"%taskname)
        success = executeTask(taskname)

    if success: 
        return successMessage
    else:
        return errorMessage

def isValid(text):
    """
        Returns True if input is related to the home assistant.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    if not cmInstance.hasConfig(SLUG):
        return False
    return any(word in text for word in ["电视","投影","空调","电扇","水循环","灯"])
