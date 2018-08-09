from abc import ABCMeta, abstractmethod
import os
import pkgutil


class AbstractController(object):

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
    def handleControl(self, session, answer, control):
        pass
    
    @classmethod
    @abstractmethod
    def is_available(cls):
        return True
    
def get_controller_by_slug(slug=None):
    """
    Returns:
        An Controller Engine implementation

    Raises:
        ValueError if no Controller engine implementation
    """

    if not slug or type(slug) is not str:
        raise TypeError("Invalid slug '%s'", slug)

    selected_engines = filter(lambda engine: hasattr(engine, "SLUG") and
                              engine.SLUG == slug, get_controllers())
    if len(selected_engines) == 0:
        raise ValueError("No Controller engine found for slug '%s'" % slug)
    else:
        if len(selected_engines) > 1:
            print(("WARNING: Multiple Controller engines found for slug '%s'. " +
                   "This is most certainly a bug.") % slug)
        engine = selected_engines[0]
        if not engine.is_available():
            raise ValueError(("Controller engine '%s' is not available (due to " +
                              "missing dependencies, missing " +
                              "dependencies, etc.)") % slug)
        return engine


def get_controllers():
    def get_subclasses(cls):
        subclasses = set()
        for subclass in cls.__subclasses__():
            subclasses.add(subclass)
            subclasses.update(get_subclasses(subclass))
        return subclasses
    return [stt_engine for stt_engine in
            list(get_subclasses(AbstractController))
            if hasattr(stt_engine, 'SLUG') and stt_engine.SLUG]
    
for finder, name, ispkg in pkgutil.walk_packages([os.path.dirname(os.path.abspath(__file__))],__name__+"."):
    #print name,ispkg
    __import__(name)