#coding:utf-8
import json

from robot.configuration import cmInstance
from robot.utils import restpost


WORDS = ["screen"]
SLUG = "meetingscreen"
PRIORITY = 0

def executeTask(taskname=None, paras=None):
    try:
        profile = cmInstance.getRootConfig()
        print profile.meetingscreen.tasks[taskname]
        service_url = "".join(profile.meetingscreen.tasks[taskname].service)
        data = profile.meetingscreen.tasks[taskname].data
        if paras:
            data["parameters"] = paras
        response =  restpost(service_url,data)
        if response == "[]":
            return False
    except Exception as e:
        print e.message
        raise
    return True

def handle(text):
    """
        Control the screen show

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone
                   number)
    """
    errorMessage = u"%s没有执行成功，请确认您的命令" % text
    successMessage = u"%s执行完成" % text
    success = False
    paras = None
    taskname = None
    if any(word in text for word in ["会商系统"]):
        if any(word in text for word in ["打开","查看","开始"]):
            taskname = "show_huishang_sys"
    elif any(word in text for word in ["雨情"]):
        if any(word in text for word in ["打开","查看"]):
            taskname = "show_rain_info"
        elif any(word in text for word in ["关闭"]):
            taskname = "close_rain_info"
    elif any(word in text for word in ["水情"]):
        if any(word in text for word in ["打开","查看"]):
            taskname = "show_water_info"
        elif any(word in text for word in ["关闭"]):
            taskname = "close_water_info"
    elif any(word in text for word in ["云图"]):
        if any(word in text for word in ["打开"]):
            taskname = "show_cloud_map"
        elif any(word in text for word in ["关闭"]):
            taskname = "close_cloud_map"
        elif any(word in text for word in ["播放"]):
            if any(word in text for word in ["停止","暂停"]):
                taskname = "stop_cloud_map"
            else:
                taskname = "play_cloud_map"
    elif any(word in text for word in ["定位"]):
        taskname = "locate_in_map"
        locateName = text.replace("定位到","")
        paras = {"name":locateName}
                
    if taskname:
        success = executeTask(taskname,paras)

    if success: 
        return successMessage
    else:
        return errorMessage

def isValid(text):
    """
        Returns True if input is related to the meeting room screen.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    if not cmInstance.hasConfig(SLUG):
        return False
    return any(word in text for word in ["雨情","云图","水情","系统","定位"])
