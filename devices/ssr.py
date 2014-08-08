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
        log.debug(gpio_numb)


        try:
            fo = open(io[:16]+"export", mode='w')
            fo.write('gpio_numb')
            fo = open(io[:23]+"direction", mode='w')
            fo.write("out")
            return
        except Exception, e:
            raise Exception("Cannot register gpio{0}".format(gpio_numb))

    def write(self, value):
        fo = open(self.io, mode='w')
        fo.write(value)

    def read(self):
        fo = open(self.io, mode='r')
        value = fo.read()
        return value


