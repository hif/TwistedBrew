#!/usr/bin python
from devices.device import Device, DEVICE_DEBUG
import utils.logging as log
import subprocess

class Probe(Device):
    def __init__(self, config=None):
        Device.__init__(self, config)
        self.test_volume = 50
        self.test_watts = 500
        self.test_init_temp = 10
        self.test_cur_temp = -99999

    def init(self):
        # TODO: Implment
        pass

    def register(self):
        if DEVICE_DEBUG:
            return True
        log.error("Can not register probe at \"{0}\", try to run \"sudo modprobe w1-gpio && sudo modprobe w1_therm\" in commandline or check your probe connections".format(self.io))

    def write(self, value):
        # TODO:Implment
        pass

    def read(self):
        if DEVICE_DEBUG:
            return self.test()
        fo = open(self.io, mode='r')
        probe_crc = fo.readline()[-4:].rstrip()
        #log.debug(probe_crc)
        if probe_crc != 'YES':
            log.debug('Temp reading wrong, do not update temp, wait for next reading')
        else:
            probe_heat = fo.readline().split('=')[1]
            return float(probe_heat)/1000
        fo.close()

    def test(self):
        if self.test_cur_temp == -99999:
            self.test_cur_temp = self.test_init_temp
        else:
            self.test_cur_temp += 1
        return self.test_cur_temp

