#!/usr/bin python
from devices.device import Device
import utils.logging as log
import re

class SSR(Device):
    def __init__(self, config=None):
        Device.__init__(self, config)

    def init(self):
        # TODO:Implment
        pass

    def register(self):
        found = re.search('\d{1,2}', self.io)
        gpio_numb = found.group()
        #log.debug(gpio_numb)
        log.debug(self.io[:16]+"export")

        try:
            fo = open(self.io[:16]+"export", mode='w')
            fo.write(gpio_numb)
            fo.close()
            fo = open(self.io[:23]+"direction", mode='w')
            fo.write("out")
            fo.close()
            return
        except Exception, e:
            raise Exception("Cannot register gpio{0}".format(gpio_numb))

    def write(self, value):
        fo = open(self.io, mode='w')
        fo.write(value)
        fo.close()

    def read(self):
        fo = open(self.io, mode='r')
        value = fo.read()
        fo.close()
        return value


