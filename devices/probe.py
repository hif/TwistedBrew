#!/usr/bin python
from devices.device import Device, DEVICE_DEBUG, DEVICE_DEBUG_CYCLETIME
import utils.logging as log
import time


class Probe(Device):
    def __init__(self, config=None):
        Device.__init__(self, config)
        self.test_temperture = 0.0

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
            return self.test_temperature
        fo = open(self.io, mode='r')
        probe_crc = fo.readline()[-4:].rstrip()
        #log.debug(probe_crc)
        if probe_crc != 'YES':
            log.debug('Temp reading wrong, do not update temp, wait for next reading')
        else:
            probe_heat = fo.readline().split('=')[1]
            return float(probe_heat)/1000
        fo.close()

    def run(self):
        while self.enabled:
            measured_value = float(self.read())
            self.callback(measured_value)
            if DEVICE_DEBUG:
                time.sleep(DEVICE_DEBUG_CYCLETIME)
            else:
                time.sleep(self.cycle_time)

