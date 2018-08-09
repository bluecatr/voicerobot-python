#coding:utf-8
import json

from robot import utils
from robot.configuration import cmInstance
from robot.hand import AbstractController


class MultimediaController(AbstractController):
    SLUG = "multimedia"

    def handleControl(self, session, answer, control):
        isWechat = False
        if session:
            isWechat = session.startswith('wechat')
            
        if not isWechat:
            return None
        
        if control.action.lower() == "show_search_result":
            answer = json.dumps(control.parameters)
        return {"answer":answer}
    

    @classmethod
    def is_available(cls):
        return True
