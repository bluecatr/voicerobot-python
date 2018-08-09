#coding:utf-8
from robot.configuration import Const
const = Const()

"""
语音公共常量
"""
const.RATE = 16000
const.CHUNK = 1024
const.CHANNEL = 1
const.LISTEN_TIME = 12

"""
科大讯飞常量列表
"""
const.MSP_SUCCESS = 0
# 音频枚举常量audioStatus
const.MSP_AUDIO_SAMPLE_INIT = 0x00
const.MSP_AUDIO_SAMPLE_FIRST = 0x01
const.MSP_AUDIO_SAMPLE_CONTINUE = 0x02
const.MSP_AUDIO_SAMPLE_LAST = 0x04
# 端点检测器所处的状态epStatus
const.MSP_EP_IN_SPEECH = 1
const.MSP_EP_AFTER_SPEECH = 3#检测到后端点时，msc已不再接收音频，停止音频写入
# 识别器返回的状态recogSatus
const.MSP_REC_STATUS_COMPLETE = 5 #当识别结果返回时，即可从msc缓存中获取结果
#语言返回的状态
const.MSP_TTS_FLAG_DATA_END = 2

const.TOPIC_PASSIVE_LISTEN = "TOPIC_PASSIVE_LISTEN"
