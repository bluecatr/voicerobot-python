#coding:utf-8
"""
For debugging, the wxtool as the replacement is better than local mic.
so local mic is not supported now. just keep the codes for reference.

A drop-in replacement for the Mic class that allows for all I/O to occur
over the terminal. Useful for debugging. Unlike with the typical Mic
implementation, Robot is always active listening with local_mic.
"""
from robot.configuration import cmInstance
from robot.ear import AbstractMIC

class LocalMic(AbstractMIC):
    SLUG = "local-mic"

    def __init__(self, stt_engine):
        self.config = cmInstance.getRootConfig()
        return

    def passiveListen(self, passive_stt_engine, PERSONA):
        return True, self.config["robot_name"]

    def activeListen(self, THRESHOLD=None):
        input = raw_input("YOU: ")
        return input

