#coding:utf-8
import json
import logging
import os
import pkgutil

from robot import configuration as config, hand
from robot.brain import ai
from robot.configuration import cmInstance, MappingDict


class Brain(object):

    def __init__(self):
        """
        Instantiates a new Brain object, which cross-references user
        input with a list of modules. Note that the order of brain.modules
        matters, as the Brain will cease execution on the first module
        that accepts a given input.
        """

        self.profile = cmInstance.getRootConfig()
        self.modules= self.get_modules()
        self._logger = logging.getLogger(__name__)
        self.handling = False

    @classmethod
    def get_modules(cls):
        """
        Dynamically loads all the modules in the modules folder and sorts
        them by the PRIORITY key. If no PRIORITY is defined for a given
        module, a priority of 0 is assumed.
        """

        logger = logging.getLogger(__name__)
        locations = [config.PLUGIN_PATH]
        logger.debug("Looking for modules in: %s",
                     ', '.join(["'%s'" % location for location in locations]))
        modules = []
        for finder, name, ispkg in pkgutil.walk_packages(locations):
            try:
                loader = finder.find_module(name)
                mod = loader.load_module(name)
            except:
                logger.warning("Skipped module '%s' due to an error.", name,
                               exc_info=True)
            else:
                if hasattr(mod, 'WORDS'):
                    logger.debug("Found module '%s' with words: %r", name,
                                 mod.WORDS)
                    modules.append(mod)
                else:
                    logger.warning("Skipped module '%s' because it misses " +
                                   "the WORDS constant.", name)
        modules.sort(key=lambda mod: mod.PRIORITY if hasattr(mod, 'PRIORITY')
                     else 0, reverse=True)
        return modules

    def query(self, texts, session=None):
        """
        Passes user input to the appropriate module, testing it against
        each candidate module's isValid function.

        Arguments:
        text -- user input, typically speech, to be parsed by a module
        session -- to separate different user conversation session
        """
        
        answer = None
        control = None
        if cmInstance.hasConfig('ai_engine'):
            ai_engine_slug = cmInstance.getConfig('ai_engine')
            try:
                ai_engine_class = ai.get_engine_by_slug(ai_engine_slug)
                answer,control = ai_engine_class.get_instance().chat(texts, session)
            except ValueError:
                pass
        
        if control:
            self._logger.info("Get Conversation control %s " % json.dumps(control).decode('unicode-escape'))
            control = MappingDict(control)
            platform = control.platform.lower()
            controller_class = hand.get_controller_by_slug(str(platform))
            controlanswer = controller_class.get_instance().handleControl(session,answer,control)
            if controlanswer:
                return controlanswer
        
        #Get the answer from AI engine
        if answer:
            return {"answer":answer}
        else: # go through all available module to handle the original text
            for module in self.modules:
                if module.isValid(texts):
                    self._logger.debug("'%s' is a valid phrase for module " +
                                       "'%s'", texts, module.__name__)
                    try:
                        self.handling = True
                        answer = module.handle(texts)
                        self.handling = False
                    except Exception:
                        self._logger.error('Failed to execute module',
                                           exc_info=True)
                        answer = _("I'm sorry. I had some trouble with that operation. Please try again later.")
                    else:
                        self._logger.debug("Handling of phrase '%s' by " +
                                           "module '%s' completed", texts,
                                           module.__name__)
                    finally:
                        return {"answer":answer}
            self._logger.debug("No module was able to handle any of these " +
                               "phrases: %r", texts)
