#!/usr/bin python
from devices.device import Device, DEVICE_DEBUG
import utils.logging as log
import re

class SSR(Device):
    def __init__(self, config=None):
        Device.__init__(self, config)

    def init(self):
        # TODO:Implment
        pass

    def register(self):
        if DEVICE_DEBUG:
            return True
        found = re.search('\d{1,2}', self.io)
        gpio_numb = found.group()
        #log.debug(gpio_numb)
        #log.debug(self.io[:16]+"export")
        #log.debug(self.io[:23]+"direction")

        try:
            fo = open(self.io[:16]+"export", mode='w')
            fo.write(gpio_numb)
            fo.close()
            fo = open(self.io[:23]+"direction", mode='w')
            fo.write("out")
            fo.close()
            return True
        except Exception, e:
            raise Exception("Cannot register gpio{0}".format(gpio_numb))
        return False

    def write(self, value):
        if DEVICE_DEBUG:
            return True
        fo = open(self.io, mode='w')
        fo.write(value)
        fo.close()
        return True

    def read(self):
        if DEVICE_DEBUG:
            return 1
        fo = open(self.io, mode='r')
        value = fo.read()
        fo.close()
        return value


