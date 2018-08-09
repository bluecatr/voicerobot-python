#!/usr/bin/env python2
#coding:utf-8
from abc import ABCMeta, abstractmethod
import glob
import os
import pkgutil
import sys
import gettext

from robot import configuration
from robot.utils import vocabcompiler


reload(sys)
sys.setdefaultencoding('utf8')


class AbstractSTTEngine(object):
    """
    Generic parent class for all STT engines
    """
        
    __metaclass__ = ABCMeta
    VOCABULARY_TYPE = None

    @classmethod
    def get_config(cls):
        return {}

    @classmethod
    def get_instance(cls, vocabulary_name, phrases):
        config = cls.get_config()
        if cls.VOCABULARY_TYPE:
            vocabulary = cls.VOCABULARY_TYPE(vocabulary_name,
                                             path=configuration.VOCABULARIES_PATH)
            if not vocabulary.matches_phrases(phrases):
                vocabulary.compile(phrases)
            config['vocabulary'] = vocabulary
        instance = cls(**config)
        return instance

    @classmethod
    def get_passive_instance(cls):
        phrases = vocabcompiler.get_keyword_phrases()
        return cls.get_instance('keyword', phrases)

    @classmethod
    def get_active_instance(cls):
        phrases = vocabcompiler.get_all_phrases()
        return cls.get_instance('default', phrases)

    @classmethod
    def get_music_instance(cls):
        phrases = vocabcompiler.get_all_phrases()
        return cls.get_instance('music', phrases)

    @classmethod
    @abstractmethod
    def is_available(cls):
        return True

    @abstractmethod
    def transcribe(self, fp):
        pass

def get_engine_by_slug(slug=None):
    """
    Returns:
        An STT Engine implementation available on the current platform

    Raises:
        ValueError if no speaker implementation is supported on this platform
    """

    if not slug or type(slug) is not str:
        raise TypeError("Invalid slug '%s'", slug)

    selected_engines = filter(lambda engine: hasattr(engine, "SLUG") and
                              engine.SLUG == slug, get_engines())
    if len(selected_engines) == 0:
        raise ValueError("No STT engine found for slug '%s'" % slug)
    else:
        if len(selected_engines) > 1:
            print(("WARNING: Multiple STT engines found for slug '%s'. " +
                   "This is most certainly a bug.") % slug)
        engine = selected_engines[0]
        if not engine.is_available():
            raise ValueError(("STT engine '%s' is not available (due to " +
                              "missing dependencies, missing " +
                              "dependencies, etc.)") % slug)
        return engine


def get_engines():
    def get_subclasses(cls):
        subclasses = set()
        for subclass in cls.__subclasses__():
            subclasses.add(subclass)
            subclasses.update(get_subclasses(subclass))
        return subclasses
    return [stt_engine for stt_engine in
            list(get_subclasses(AbstractSTTEngine))
            if hasattr(stt_engine, 'SLUG') and stt_engine.SLUG]

for finder, name, ispkg in pkgutil.walk_packages([os.path.dirname(os.path.abspath(__file__))],__name__+"."):
    #print name,ispkg
    __import__(name)
