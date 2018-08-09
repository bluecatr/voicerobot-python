#coding:utf-8
import HTMLParser

from robot import utils
from robot.configuration import cmInstance
"""
Speech Synthesis Markup Language 转换服务
当前由Richway提供转换服务
"""

def translation(text,mode):
    richway = cmInstance.getConfig('ai_engines','richway')
    if 'translation_url' in richway:
        translation_url = richway.translation_url
    else:
        return text
    body = {"text":text,"type":mode}
    data = utils.restpost(translation_url, body)
    result = data["result"]
    html_parser = HTMLParser.HTMLParser()
    translatedTxt = html_parser.unescape(result)
    return translatedTxt

