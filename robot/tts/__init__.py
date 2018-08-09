#coding:utf-8
"""
A Speaker handles audio output

Speaker methods:
    say - output 'phrase' as speech
    play - play the audio in 'filename'
    is_available - returns True if the platform supports this implementation
"""
from abc import ABCMeta, abstractmethod
import argparse
import glob
import logging
import os
import pipes
import pkgutil
import platform
import subprocess
import sys
import tempfile

from robot.utils import diagnose

# 
# reload(sys)
# sys.setdefaultencoding('utf8')

class AbstractTTSEngine(object):
    """
    Generic parent class for all speakers
    """
    __metaclass__ = ABCMeta

    @classmethod
    def get_config(cls):
        return {}

    @classmethod
    def get_instance(cls):
        config = cls.get_config()
        instance = cls(**config)
        return instance

    @classmethod
    @abstractmethod
    def is_available(cls):
        return diagnose.check_executable('aplay') and diagnose.check_python_import('mad')

    def __init__(self, **kwargs):
        self._logger = logging.getLogger(__name__)

    @abstractmethod
    def synthesise(self, phrase):
        pass


def get_default_engine_slug():
    return 'osx-tts' if platform.system().lower() == 'darwin' else 'espeak-tts'


def get_engine_by_slug(slug=None):
    """
    Returns:
        A speaker implementation available on the current platform

    Raises:
        ValueError if no speaker implementation is supported on this platform
    """

    if not slug or type(slug) is not str:
        raise TypeError("Invalid slug '%s'", slug)

    selected_engines = filter(lambda engine: hasattr(engine, "SLUG") and
                              engine.SLUG == slug, get_engines())
    if len(selected_engines) == 0:
        raise ValueError("No TTS engine found for slug '%s'" % slug)
    else:
        if len(selected_engines) > 1:
            print("WARNING: Multiple TTS engines found for slug '%s'. " +
                  "This is most certainly a bug." % slug)
        engine = selected_engines[0]
        if not engine.is_available():
            raise ValueError(("TTS engine '%s' is not available (due to " +
                              "missing dependencies, etc.)") % slug)
        return engine


def get_engines():
    def get_subclasses(cls):
        subclasses = set()
        for subclass in cls.__subclasses__():
            subclasses.add(subclass)
            subclasses.update(get_subclasses(subclass))
        return subclasses
    return [tts_engine for tts_engine in
            list(get_subclasses(AbstractTTSEngine))
            if hasattr(tts_engine, 'SLUG') and tts_engine.SLUG]

for finder, name, ispkg in pkgutil.walk_packages([os.path.dirname(os.path.abspath(__file__))], __name__+"."):
    #print name,ispkg
    __import__(name)
    
