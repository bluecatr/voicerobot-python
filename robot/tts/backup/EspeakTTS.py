#coding:utf-8
import os
import pipes
import subprocess
import sys
import tempfile

from robot.utils import diagnose
from robot.configuration import cmInstance
from robot.tts import AbstractTTSEngine


reload(sys)
sys.setdefaultencoding('utf8')


class EspeakTTS(AbstractTTSEngine):
    """
    Uses the eSpeak speech synthesizer included in the disk image
    Requires espeak to be available
    """
 
    SLUG = "espeak-tts"
 
    def __init__(self, voice='default+m3', pitch_adjustment=40,
                 words_per_minute=160):
        super(self.__class__, self).__init__()
        self.voice = voice
        self.pitch_adjustment = pitch_adjustment
        self.words_per_minute = words_per_minute
 
    @classmethod
    def get_config(cls):
        # FIXME: Replace this as soon as we have a config module
        config = {}
        profile = cmInstance.getRootConfig()
        if 'espeak-tts' in profile:
            if 'voice' in profile['espeak-tts']:
                config['voice'] = profile['espeak-tts']['voice']
            if 'pitch_adjustment' in profile['espeak-tts']:
                config['pitch_adjustment'] = \
                    profile['espeak-tts']['pitch_adjustment']
            if 'words_per_minute' in profile['espeak-tts']:
                config['words_per_minute'] = \
                    profile['espeak-tts']['words_per_minute']
        return config
 
    @classmethod
    def is_available(cls):
        return (super(cls, cls).is_available() and
                diagnose.check_executable('espeak'))
 
    def say(self, phrase):
        self._logger.debug("Saying '%s' with '%s'", phrase, self.SLUG)
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            fname = f.name
        cmd = ['espeak', '-v', self.voice,
                         '-p', self.pitch_adjustment,
                         '-s', self.words_per_minute,
                         '-w', fname,
                         phrase]
        cmd = [str(x) for x in cmd]
        self._logger.debug('Executing %s', ' '.join([pipes.quote(arg)
                                                     for arg in cmd]))
        with tempfile.TemporaryFile() as f:
            subprocess.call(cmd, stdout=f, stderr=f)
            f.seek(0)
            output = f.read()
            if output:
                self._logger.debug("Output was: '%s'", output)
        self.play(fname)
        os.remove(fname)


        