from devices.device import Device
import utils.logging as log
import re

class SSR(Device):
    def __init__(self, config):
        Device.__init__(self, config)

    def init(self):
        # TODO:Implment
        pass

    def register(self):
        gpioNumb = re.search('\d{1,2}', self.io)

        try:
            fo = open(io[:16]+"export", mode='w')
            fo.write('gpioNumb')
            fo = open(io[:23]+"direction", mode='w')
            fo.write('out')
            return
        except Exception, e:
            raise Exception('Cannot register')

    def write(self, value):
        # TODO:Implment
        pass

    def read(self):
        # TODO:Implment
        pass