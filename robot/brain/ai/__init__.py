#coding:utf-8
from abc import ABCMeta, abstractmethod
import json
import logging
import os
import pkgutil
import sys
from uuid import getnode as get_mac

from robot.configuration import cmInstance


reload(sys)
sys.setdefaultencoding('utf-8')


class AbstractAIEngine(object):

    __metaclass__ = ABCMeta

    @classmethod
    def get_config(cls):
        return {}
    
    @classmethod
    def get_instance(cls):
        config = cls.get_config()
        instance = cls(**config)
        return instance

    @abstractmethod
    def chat(self, texts, session=None):
        pass

    @classmethod
    @abstractmethod
    def is_available(cls):
        return True
    
def get_default_engine_slug():
    return 'tuling-ai' if not cmInstance.hasConfig("default_ai_engine") else cmInstance.getConfig("default_ai_engine")

def get_engine_by_slug(slug=None):
    """
    Returns:
        An AI Engine implementation available on the current platform

    Raises:
        ValueError if no AI engine implementation is supported on this platform
    """

    if not slug or type(slug) is not str:
        raise TypeError("Invalid slug '%s'", slug)

    selected_engines = filter(lambda engine: hasattr(engine, "SLUG") and
                              engine.SLUG == slug, get_engines())
    if len(selected_engines) == 0:
        raise ValueError("No AI engine found for slug '%s'" % slug)
    else:
        if len(selected_engines) > 1:
            print(("WARNING: Multiple AI engines found for slug '%s'. " +
                   "This is most certainly a bug.") % slug)
        engine = selected_engines[0]
        if not engine.is_available():
            raise ValueError(("AI engine '%s' is not available (due to " +
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
            list(get_subclasses(AbstractAIEngine))
            if hasattr(stt_engine, 'SLUG') and stt_engine.SLUG]
    
for finder, name, ispkg in pkgutil.walk_packages([os.path.dirname(os.path.abspath(__file__))],__name__+"."):
    #print name,ispkg
    __import__(name)
