#coding:utf-8
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import json
import logging
import os
from paho.mqtt.client import Client
import platform
from pydub.audio_segment import AudioSegment
from pytz import timezone
import requests
import shutil
import smtplib
import subprocess
import urllib
import urllib2

import paho.mqtt.publish as Publish
import paho.mqtt.subscribe as Subscribe
from robot import configuration


_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

def isPi():
    isPi = True
    pp = platform.platform()
    if not "arm" in pp:
        isPi = False
        
    return isPi

def getTimezone(timezone):
    """
    Returns the pytz timezone for a given profile.

    Arguments:
        profile -- contains information related to the user (e.g., email
                   address)
    """
    try:
        return timezone(timezone)
    except:
        return None

def restget(service,params,headers={"Content-type":"application/json;charset=UTF-8","Accept": "application/json"}):
    """
    params is type of dict
    """
    params = urllib.urlencode(params)
    _logger.debug("service_url: %s"%service)
    _logger.debug("params: %s" % params)
    r = requests.get(service,params=params,headers=headers)
    try:
        r.raise_for_status()
        response = r.json()
    except requests.exceptions.HTTPError:
        _logger.critical('Request failed with response: %r',
                              r.text,
                              exc_info=True)
        response = None
    return response


def restpost(service,data,headers={"Content-type":"application/json;charset=UTF-8","Accept": "application/json"}):
    """
    data is type of dict
    """
    databody = json.dumps(data)
    _logger.debug("service_url: %s"%service)
    _logger.debug("data: %s" % databody.decode('unicode-escape'))
    r = requests.post(service,data=databody,headers=headers)
    try:
        r.raise_for_status()
        response = r.json()
    except requests.exceptions.HTTPError:
        _logger.critical('Request failed with response: %r',
                              r.text,
                              exc_info=True)
        response = None
    return response


def audiofileToWav(audiofile):
    converter = os.path.join(configuration.TOOLS_PATH, "silk-v3-decoder", "converter.sh")
    subprocess.call(['/bin/sh',converter,audiofile,'wav'])
    wavfile = os.path.splitext(audiofile)[0] + '.wav'
    return wavfile
    
def wavToMP3(wavfile):
    wav = AudioSegment.from_wav(wavfile)
    mp3file = os.path.splitext(wavfile)[0] + '.mp3'
    wav.export(mp3file, format="mp3")
    return mp3file

def cutMP3(mp3file,time=59):
    """
    mp3file: the file need to be checked and cut off 
    time:  if the duration of mp3 is more than the time, a new mp3 will be exported with the time duration
    """
    mp3 = AudioSegment.from_mp3(mp3file)
    if mp3.duration_seconds > time:
        _logger.info("Mp3 %s duration is %s more than %s, need cut off " % (mp3file, mp3.duration_seconds, time))
        mp3.get_sample_slice(0,time*mp3.frame_rate).export(mp3file, format="mp3")
        #mp3[:time*1000].export(mp3file, format="mp3")

def isMp3Format(mp3filePath):
    #读取文件内字符串
    f =  open(mp3filePath, "r");
    fileStr = f.read();
    f.close();
    head3Str = fileStr[:3];
    
    #判断开头是不是ID3
    if head3Str == "ID3":
        return True
    
    #判断结尾有没有TAG
    last32Str = fileStr[-32:]
    if last32Str[:3] == "TAG":
        return True;
    
    #判断第一帧是不是FFF开头, 转成数字
    # fixme 应该循环遍历每个帧头，这样才能100%判断是不是mp3
    ascii = ord(fileStr[:1]);
    if ascii == 255:
        return True;
    
    return False;

def checkKeyWords(text, texts):
    return any(word in text for word in texts)

def isJSON(jsonstr):
    try:
        json.loads(jsonstr)
    except ValueError:
        return False
    return True
  
  
def publish(topic,content):
    # content is string
    Publish.single(topic, content)
    
def subscribe(topic,on_message=None):
    if on_message:
        client = Client()
        client.on_message = on_message
        HOST = "localhost"
        client.connect(HOST, 1883, 60)
        client.subscribe(topic)
        client.loop_start()
#         Subscribe.callback(on_message,topic)
    else:
        result = Subscribe.simple(topic)
        return result.payload
  
def movefile(src, dst):
    shutil.move(src, dst)
    
    