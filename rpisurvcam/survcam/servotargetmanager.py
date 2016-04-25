import threading

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class ServoTargetManager(object):
    __metaclass__ = Singleton

    def __init__(self):
        self.__targets = {'pan': 0, 'tilt': 0}
        self.__lock = threading.Lock()

    def set_target(self, axis, target):
        with self.__lock:
            self.__targets[axis] = target

    def get_target(self, axis):
        with self.__lock:
            return self.__targets[axis]
