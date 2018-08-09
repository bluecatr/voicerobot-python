#coding:utf-8
import datetime
from semantic.dates import DateService

from robot import utils
from robot.configuration import cmInstance


WORDS = [u"TIME", u"SHIJIAN", u"JIDIAN"]
SLUG = "time"


def handle(text):
    """
        Reports the current time based on the user's timezone.

        Arguments:
        text -- user-input, typically transcribed speech
        mic -- used to interact with the user (for both input and output)
        profile -- contains information related to the user (e.g., phone
                   number)
    """

    tz = utils.getTimezone(cmInstance.getConfig("timezone"))
    now = datetime.datetime.now(tz=tz)
    service = DateService()
    response = service.convertTime(now)
    return _("Now it is %s") % response



def isValid(text):
    """
        Returns True if input is related to the time.

        Arguments:
        text -- user-input, typically transcribed speech
    """
    return any(word in text for word in ["时间", "几点"])
