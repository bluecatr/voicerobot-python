#coding:utf-8
import random
from sys import maxint

from robot.brain import ai

WORDS = []
PRIORITY = -(maxint + 1)

def handle(text):
    """
    Reports that the user has unclear or unusable input.

    Arguments:
    text -- user-input, typically transcribed speech
    mic -- used to interact with the user (for both input and output)
    profile -- contains information related to the user (e.g., phone
               number)
    """
    ai_engine_slug = ai.get_default_engine_slug()
    message = ""
    try:
        ai_engine_class = ai.get_engine_by_slug(ai_engine_slug)
        message = ai_engine_class.get_instance().chat(text, None)
    except ValueError:
        messages = [_("I'm sorry, could you repeat that?"),
                _("My apologies, could you try saying that again?"),
                _("Say that again?"),
                _("I beg your pardon?")]
        message = random.choice(messages)
    finally:
        return message

def isValid(text):
    return True
