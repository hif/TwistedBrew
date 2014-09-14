#!/usr/bin python
from devices.device import Device, DEVICE_DEBUG_CYCLE_TIME
import utils.logging as log
import re
import threading
import time


class SSR(Device):
    def __init__(self, owner, config, simulation):
        threading.Thread.__init__(self)
        Device.__init__(self, owner, config, simulation)
        self.on_percent = 0.0
        self.last_on_time = 0.0

    def init(self):
        # TODO:Implment
        pass

    def register(self):
        if self.simulation:
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
        self.on_percent = value
        if self.on_percent > 1.0:
            self.on_percent = 1.0
        elif self.on_percent < 0.0:
            self.on_percent = 0.0
        return True

    def set_ssr_state(self, on = False):
        if self.simulation:
            return True
        with self.read_write_lock:
            fo = open(self.io, mode='w')
            if on:
                fo.write('1')
            else:
                fo.write('0')
            fo.close()
            ok = True
        return ok

    def read(self):
        if self.simulation:
            return 1
        with self.read_write_lock:
            fo = open(self.io, mode='r')
            value = fo.read()
            fo.close()
        return value

    def run_cycle(self):
        # grab the current value if it should be changed during the cycle
        on_percent = self.on_percent
        on_time = on_percent * self.cycle_time
        if self.simulation:
            time.sleep(DEVICE_DEBUG_CYCLE_TIME)
            self.do_callback(on_time)
            return
        if self.on_percent > 0.0:
            self.set_ssr_state(True)
            time.sleep(on_time)
        if self.on_percent < 1.0:
            self.set_ssr_state(False)
            time.sleep((1.0-on_percent)*self.cycle_time)
        self.do_callback(on_time)
