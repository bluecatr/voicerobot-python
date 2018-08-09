#coding:utf-8
import os
import pipes
import subprocess
import sys
import tempfile

from robot import diagnose
from robot.configuration import cmInstance
from robot.tts import AbstractTTSEngine


reload(sys)
sys.setdefaultencoding('utf8')

class FliteTTS(AbstractTTSEngine):
    """
    Uses the flite speech synthesizer
    Requires flite to be available
    """
 
    SLUG = 'flite-tts'
 
    def __init__(self, voice=''):
        super(self.__class__, self).__init__()
        self.voice = voice if voice and voice in self.get_voices() else ''
 
    @classmethod
    def get_voices(cls):
        cmd = ['flite', '-lv']
        voices = []
        with tempfile.SpooledTemporaryFile() as out_f:
            subprocess.call(cmd, stdout=out_f)
            out_f.seek(0)
            for line in out_f:
                if line.startswith('Voices available: '):
                    voices.extend([x.strip() for x in line[18:].split()
                                   if x.strip()])
        return voices
 
    @classmethod
    def get_config(cls):
        # FIXME: Replace this as soon as we have a config module
        config = {}
        profile = cmInstance.getRootConfig()
        if 'flite-tts' in profile:
            if 'voice' in profile['flite-tts']:
                config['voice'] = profile['flite-tts']['voice']
        return config
 
    @classmethod
    def is_available(cls):
        return (super(cls, cls).is_available() and
                diagnose.check_executable('flite') and
                len(cls.get_voices()) > 0)
 
    def say(self, phrase):
        self._logger.debug("Saying '%s' with '%s'", phrase, self.SLUG)
        cmd = ['flite']
        if self.voice:
            cmd.extend(['-voice', self.voice])
        cmd.extend(['-t', phrase])
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            fname = f.name
        cmd.append(fname)
        with tempfile.SpooledTemporaryFile() as out_f:
            self._logger.debug('Executing %s',
                               ' '.join([pipes.quote(arg)
                                         for arg in cmd]))
            subprocess.call(cmd, stdout=out_f, stderr=out_f)
            out_f.seek(0)
            output = out_f.read().strip()
        if output:
            self._logger.debug("Output was: '%s'", output)
        self.play(fname)
        os.remove(fname)
        