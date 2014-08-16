#!/usr/bin python
import utils.logging as log


DEVICE_DEBUG = True

DEVICE_OFF = 0
DEVICE_ON = 1

class Device():
    def __init__(self, config = None):
        self.name = "None"
        self.io = "None"
        if(config is not None):
            self.name = config.name
            self.io = config.io
        self.state = DEVICE_OFF

    def init(self):
        pass

    def start_device(self):
        self.state = DEVICE_ON

    def stop_device(self):
        self.state = DEVICE_OFF

    def check(self):
        try:
            with open(self.io) as file:
                return True
        except IOError as e:
            log.debug("Unable to find/open \"{0}\"".format(self.io), messagetype=log.WARNING)
            return False

    def register(self):
        pass

    def write(self, value):
        pass

    def read(self):
        pass

    def devicetype(self):
        return self.__class__.__name__

    def auto_setup(self):
        """
        Calls the default startup sequence for any device using the device interface functions.
        First it is initalized, the checks for registration in the OS (if needed) and finally
        registers it if no registration is found.
        :return: True, None if everything is ok or False, [error message] if it fails.
        """
        try:
            self.init()
            if not self.check():
                self.register()
            return True, None
        except Exception, e:
            return False, e.message

