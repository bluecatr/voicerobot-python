#!/usr/bin/env python2
# -*- coding: utf-8  -*-
import logging
import sys

from robot import tts, utils
from robot.configuration import cmInstance


answer = sys.argv[1]
cachefile = sys.argv[2]
if __name__ == "__main__":
    logging.basicConfig()
    #专门用于科大讯飞合成的子程序
    tts_engine_slug = cmInstance.getConfig['tts_engine']
    tts_engine_class = tts.get_engine_by_slug(tts_engine_slug)
    tts_engine = tts_engine_class.get_instance()
    
    audiofile = tts_engine.synthesise(answer)
    utils.movefile(audiofile, cachefile)