# coding:utf-8
import Queue
from ctypes import cdll
import logging
import time

from robot import configuration
from robot.configuration import cmInstance


_logger = logging.getLogger(__name__)
_logger.setLevel(logging.INFO)

def init_iflytck_sdk(appid):
    profile = cmInstance.getConfig('voice_engines')
    ostype = "x64"
    if 'ostype' in profile.iflytek:
        ostype = profile.iflytek.ostype
    sofile = configuration.config("iflytek_msc",appid,"libs",ostype,"libmsc.so")
    _logger.info("Loading iflytec msc libaray file: %s" % sofile)
    sdk = cdll.LoadLibrary(sofile) #sdk:speech synthesis
    return sdk

class AppidQueue(object):
    queue = Queue.Queue()
    profile = cmInstance.getConfig('voice_engines')
    if 'accounts' in profile.iflytek:
        accounts = profile.iflytek.accounts
        for account in accounts:
            queue.put_nowait(str(account.appid))
#         while len(accounts) > 1:
#             account = random.choice(accounts)
#             queue.put_nowait(str(account.appid))
#             accounts.remove(account)

    @staticmethod
    def put(appid):
        _logger.debug("put %s back into appid pool" % appid)
        AppidQueue.queue.put(appid)

    @staticmethod
    def get():
        while True:
            if AppidQueue.queue.not_empty:
                appid = AppidQueue.queue.get()
                _logger.debug("get %s from appid pool" % appid)
                return appid
            else:
                time.sleep(0.1)


    
    