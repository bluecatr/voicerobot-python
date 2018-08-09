#coding:utf-8
from abc import ABCMeta, abstractmethod
import json
import logging
import os
import pkgutil
import sys
from uuid import getnode as get_mac

from robot.configuration import cmInstance


class AbstractMIC(object):

    __metaclass__ = ABCMeta

    @classmethod
    def get_instance(cls,stt_engine):
        config = cls.get_config()
        instance = cls(stt_engine,**config)
        return instance

    @classmethod
    def get_config(cls):
        config = {}
        return config

    @classmethod
    @abstractmethod
    def is_available(cls):
        return True
    
    class Pixels:
        @classmethod
        def wakeup(cls):
            pass
        @classmethod
        def listen(cls):
            pass
        @classmethod
        def think(cls):
            pass
        @classmethod
        def speak(cls):
            pass
        @classmethod
        def off(cls):
            pass
    

def get_default_mic_slug():
    return 'base-mic'

def get_mic_by_slug(slug=None):
    """
    Returns:
        A Mic implementation available on the current platform

    Raises:
        ValueError if no Mic implementation is supported on this platform
    """

    if not slug or type(slug) is not str:
        raise TypeError("Invalid slug '%s'", slug)

    selected_mics = filter(lambda mic: hasattr(mic, "SLUG") and
                              mic.SLUG == slug, get_mics())
    if len(selected_mics) == 0:
        raise ValueError("No MIC found for slug '%s'" % slug)
    else:
        if len(selected_mics) > 1:
            print(("WARNING: Multiple MIC found for slug '%s'. " +
                   "This is most certainly a bug.") % slug)
        mic = selected_mics[0]
        if not mic.is_available():
            raise ValueError(("MIC '%s' is not available (due to " +
                              "missing dependencies, missing " +
                              "dependencies, etc.)") % slug)
        return mic


def get_mics():
    def get_subclasses(cls):
        subclasses = set()
        for subclass in cls.__subclasses__():
            subclasses.add(subclass)
            subclasses.update(get_subclasses(subclass))
        return subclasses
    return [mic for mic in
            list(get_subclasses(AbstractMIC))
            if hasattr(mic, 'SLUG') and mic.SLUG]
    
for finder, name, ispkg in pkgutil.walk_packages([os.path.dirname(os.path.abspath(__file__))],__name__+"."):
    #print name,ispkg
    __import__(name)
