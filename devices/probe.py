from devices.device import Device
import utils.logging as log

class Probe(Device):
    def __init__(self, config):
        Device.__init__(self, config)

    def init(self):
        # TODO:Implment
        pass

    def register(self):
        try:
            #something
            return
        except Exception, e:
            raise Exception('Cannot register')

    def write(self, value):
        # TODO:Implment
        pass

    def read(self):
        # TODO:Implment
        pass