#coding:utf-8
import logging
import os
import pipes
import psutil
import subprocess
import tempfile
import threading

from robot import utils
from robot.configuration import cmInstance
from robot.configuration.const import const


class Mouth(object):
    
    def __init__(self):
        """
        Initiates the Mouth instance.

        Arguments:
        tts_engine -- handles platform-independent audio output
        """
        self._logger = logging.getLogger(__name__)
        self.config = cmInstance.getRootConfig()
    
    def setTTS(self, tts_engine):
        """
        tts_engine -- handles platform-independent audio output
        """
        self.tts_engine = tts_engine
    
    def say(self, phrase, echo=False):
        if echo:
            self.echo(phrase)
            return
        
        if self.tts_engine.SLUG == "osx-tts":
            self.tts_engine.macos_say(phrase)
            return
        
        audiofile = self.tts_engine.synthesise(phrase)
        if utils.isMp3Format(audiofile):
            self.play_mp3(audiofile)
        else:
            self.play(audiofile)
        os.remove(audiofile)
        
    def shutup(self):
        # self.lock.acquire(True)
        if self.proc_play is not None and psutil.pid_exists(self.proc_play.pid):
            self._logger.debug("Terminating subprocess pid:%s", self.proc_play.pid)
            self.proc_play.kill()
            # self.proc_play.wait()
            self.proc_play = None
        # self.lock.release()
    
    def isSaying(self):
        if self.proc_play:
            return True
        return False
    
    def play(self, filename):
        if utils.isMp3Format(filename):
            self.play_mp3(filename)
        else:
            self.play_wav(filename)
                
    def play_wav(self, filename):
        cmd = ['aplay', str(filename)]
        self._logger.debug('Executing %s', ' '.join([pipes.quote(arg)
                                                     for arg in cmd]))
        with tempfile.TemporaryFile() as f:
            f.seek(0)
            self.proc_play = subprocess.Popen(cmd, stdout=f, stderr=f)
            self.proc_play.wait()
            output = f.read()
            if output:
                self._logger.debug("Output was: '%s'", output)


    def play_mp3(self, filename):
        cmd = ['play', str(filename)]
        self._logger.debug('Executing %s', ' '.join([pipes.quote(arg)
                                                     for arg in cmd]))
        with tempfile.TemporaryFile() as f:
            f.seek(0)
            self.proc_play = subprocess.Popen(cmd, stdout=f, stderr=f)
            self.proc_play.wait()
            output = f.read()
            if output:
                self._logger.debug("Output was: '%s'", output)
    
    def echo(self, phrase):
        print("%s: %s" % (self.config["robot_name_cn"],phrase))
                
    
    def say_in_silence(self, phrase):
        #200个字左右比较合适
        max_length = 200
        unicodetext = unicode(str(phrase),"utf-8")
        if len(unicodetext) > max_length:
            phrase = "文字太多，只读部分内容： %s" % unicodetext[0:max_length]
        audiofile = self.tts_engine.synthesise(phrase)
        return audiofile
        
mouth = Mouth()