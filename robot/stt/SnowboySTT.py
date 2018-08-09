#coding:utf-8
import logging
import os
import sys

from robot import configuration
from robot.utils import diagnose
from robot.configuration import cmInstance
from robot.stt import AbstractSTTEngine


reload(sys)
sys.setdefaultencoding('utf-8')

class SnowboySTT(AbstractSTTEngine):
    """
    Snowboy STT 离线识别引擎（只适用于离线唤醒）
        ...
        snowboy:
            model: '/home/pi/.voicerobot/snowboy/hey_watson.umdl'  # 唤醒词模型
            sensitivity: "0.5"  # 敏感度
        ...
    """
 
    SLUG = "snowboy-stt"
 
    def __init__(self, sensitivity, model, hotword):
        self._logger = logging.getLogger(__name__)
        self.sensitivity = sensitivity
        self.hotword = hotword
        self.model = model
        self.resource_file = os.path.join(configuration.LIB_PATH,
                                          'snowboy/common.res')
        try:
            from robot.snowboy import snowboydetect
        except Exception, e:
            self._logger.critical(e)
            if 'libf77blas.so' in e.message:
                self._logger.critical("您可能需要安装一个so包加载库：" +
                                      "sudo apt-get install libatlas-base-dev")
            return
        self.detector = snowboydetect.SnowboyDetect(
            resource_filename=self.resource_file,
            model_str=self.model)
        self.detector.SetAudioGain(1)
        self.detector.SetSensitivity(self.sensitivity)
 
    @classmethod
    def get_config(cls):
        # FIXME: Replace this as soon as we have a config module
        config = {}
        # Try to get snowboy config from config
        profile = cmInstance.getConfig('voice_engines')
        if 'snowboy' in profile:
            if 'model' in profile['snowboy']:
                config['model'] = \
                    profile['snowboy']['model']
            else:
                config['model'] = os.path.join(
                    configuration.LIB_PATH, 'snowboy/hey_watson.umdl')
            if 'sensitivity' in profile['snowboy']:
                config['sensitivity'] = \
                    profile['snowboy']['sensitivity']
            else:
                config['sensitivity'] = "0.5"
            if 'robot_name' in profile:
                config['hotword'] = profile['robot_name']
            else:
                config['hotword'] = 'HEYWATSON'
        return config
 
    def transcribe(self, fp):
        fp.seek(44)
        data = fp.read()
        ans = self.detector.RunDetection(data)
        if ans > 0:
            self._logger.info('Transcribed: %r', self.hotword)
            return self.hotword
        else:
            return None
 
    @classmethod
    def is_available(cls):
        return diagnose.check_python_import('snowboy.snowboydetect')

