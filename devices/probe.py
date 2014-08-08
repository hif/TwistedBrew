#!/usr/bin python
from devices.device import Device
import utils.logging as log
import subprocess

class Probe(Device):
    def __init__(self, config=None):
        Device.__init__(self, config)

    def init(self):
        # TODO: Implment
        pass

    def register(self):
        log.error("Can not register probe at \"{0}\", try to run \"sudo modprobe w1-gpio && sudo modprobe w1_therm\" in commandline or check your probe connections".format(self.io))

    def write(self, value):
        # TODO:Implment
        pass

    def read(self):
        fo = open(self.io, mode='r')
        probe_crc = fo.readline()[-4:].rstrip()
        log.debug(probe_crc)
        if probe_crc != 'YES':
            log.debug('Temp reading wrong, do not update temp, wait for next reading')
        else:
            probe_heat = fo.readline().split('=')[1]
            log.debug(float(probe_heat)/1000)
        fo.close()
