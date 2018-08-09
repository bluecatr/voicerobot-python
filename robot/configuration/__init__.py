#coding:utf-8
import os
import yaml
import logging
import shutil
import gettext

# Jasper main directory
APP_PATH = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, os.pardir))
DATA_PATH = os.path.join(APP_PATH, "static")
LIB_PATH = os.path.join(APP_PATH, "robot")
TOOLS_PATH = os.path.join(APP_PATH, "tools")
LOCALE_PATH =  os.path.join(APP_PATH, "locale")
PLUGIN_PATH = os.path.join(LIB_PATH, "modules")

CORE_CONFIGURATION = 'profile.yml'
CONFIG_PATH = os.path.expanduser(os.getenv('VOICEROBOT_CONFIG', '~/.voicerobot'))
VOCABULARIES_PATH = os.path.join(CONFIG_PATH, "vocabularies")
    
def config(*fname):
    return os.path.join(CONFIG_PATH, *fname)

def data(*fname):
    return os.path.join(DATA_PATH, *fname)

def tools(*fname):
    return os.path.join(TOOLS_PATH, *fname)

class Const(object):
    class ConstError(TypeError): pass
    def __setattr__(self, key, value):
        if self.__dict__.has_key(key):
            raise self.ConstError, "Can't rebind const: %s" % key
        self.__dict__[key] = value
        
class Loader(yaml.Loader):
    def __init__(self, stream):
        self._root = os.path.split(stream.name)[0]
        super(Loader, self).__init__(stream)

    def include(self, node):
        filename = os.path.join(self._root, self.construct_scalar(node))
        with open(filename, 'r') as f:
            return yaml.load(f, Loader)

Loader.add_constructor('!include', Loader.include)

class MappingDict(dict):    
    def __getattr__(self, key):
        return self[key]
    
    
    def __getitem__(self, *args, **kwargs):
        try:  
            currItem = dict.__getitem__(self, *args, **kwargs)
            if type(currItem) is dict:
                return MappingDict(currItem)
            elif type(currItem) is list:
                newlist = []
                for item in currItem:
                    if type(item) is dict:
                        newlist.append(MappingDict(item))
                    else:
                        newlist.append(item)
                return newlist
            else:
                return currItem
        except KeyError, k:  
            raise AttributeError, k
        
class ConfigurationManager(object):
    
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        
        # Create config dir if it does not exist yet
        if not os.path.exists(CONFIG_PATH):
            try:
                os.makedirs(CONFIG_PATH)
            except OSError:
                self._logger.error("Could not create config dir: '%s'",
                                   CONFIG_PATH, exc_info=True)
                raise
 
        # Check if config dir is writable
        if not os.access(CONFIG_PATH, os.W_OK):
            self._logger.critical("Config dir %s is not writable. VoiceRobot " +
                                  "won't work correctly.",CONFIG_PATH)
 
        configfile_template = data("profile.yml.template")
        configfile = config(CORE_CONFIGURATION)
        if not os.path.exists(configfile):
            if os.path.exists(configfile_template):
                self._logger.warning("Profile file '%s' doesn't exist. " +
                                     "Trying to create it from template '%s'.",
                                     configfile, configfile_template)
                try:
                    shutil.copy2(configfile_template, configfile)
                    self._logger.warning("Profile file is created. To enable the feature you want to use, " + 
                                                "you should modify and set your private data in the profile")
                except shutil.Error:
                    self._logger.error("Unable to copy config file. " +
                                       "Please copy it manually.",
                                       exc_info=True)
                    raise
        
        self.loadConfiguration(configfile)
    
            
    def loadConfiguration(self,configfile):
        # Read core configuration file
        self._logger.debug("Trying to read config file: '%s'", configfile)
        try:
            with open(configfile, "r") as f:
                self.config = MappingDict(yaml.load(f,Loader))
        except OSError:
            self._logger.error("Can't open config file: '%s'", configfile)
            raise

    def getRootConfig(self):
        return self.config
    
    def getConfig(self,*keys):
        config = self.config
        try:
            self._logger.debug("Trying to read config file to locate '%s'", keys)
            for index in range(len(keys)):
                if keys[index].strip() != "":
                    config = config[keys[index]]
        except AttributeError:
            self._logger.warning("Can't find the key '%s'", keys[index])
            config = None
        return config
    
    def hasConfig(self, key):
        return self.config.has_key(key)

# the only instance of Configuration Manager
cmInstance = ConfigurationManager()
gettext.translation('phrase', LOCALE_PATH, languages=[cmInstance.getConfig('language')]).install(True)