from devices.device import Device
import utils.logging as log
import subprocess

class Probe(Device):
    def __init__(self, config):
        Device.__init__(self, config)

    def init(self):
        # TODO:Implment
        pass

    def register(self):
        try:
            subprocess.call(["sudo modprobe", "w1-gpio"])
            subprocess.call(["sudo modprobe", "w1_therm"])
            return
        except Exception, e:
            raise Exception('Cannot register')

    def write(self, value):
        # TODO:Implment
        pass

    def read(self):
        fo = open(self.io, mode='r')
        fo.readall()