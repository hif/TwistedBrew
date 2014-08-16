#!/usr/bin python
from devices.device import Device, DEVICE_DEBUG, DEVICE_OFF, DEVICE_ON
import utils.logging as log
import re
import threading
import time
import datetime

SSR_DEFAULT_CYCLETIME = 2.0

class SSR(Device, threading.Thread):
    def __init__(self, config=None):
        threading.Thread.__init__(self)
        Device.__init__(self, config)
        self.cycletime = SSR_DEFAULT_CYCLETIME
        self.on_percent = 0.0

    def init(self):
        # TODO:Implment
        pass

    def start_device(self):
        Device.start_device(self)
        self.start()

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
        self.on_percent = value
        if self.on_percent > 1.0:
            self.on_percent = 1.0
        elif self.on_percent < 0.0:
            self.on_percent = 0.0
        return True

    def set_ssr_state(self, on = False):
        if DEVICE_DEBUG:
            return True
        fo = open(self.io, mode='w')
        if on:
            fo.write('1')
        else:
            fo.write('0')
        fo.close()
        return True

    def read(self):
        if DEVICE_DEBUG:
            return 1
        fo = open(self.io, mode='r')
        value = fo.read()
        fo.close()
        return value

    def run(self):
        while self.state != DEVICE_OFF:
            # grab the current value if it should be changed during the cycle
            on_percent = self.on_percent

            if DEVICE_DEBUG:
                loop_start = datetime.datetime.now()

            if self.on_percent > 0.0:
                self.set_ssr_state(True)

                if DEVICE_DEBUG:
                    on_start = datetime.datetime.now()
                    log.debug('Turning on SSR')

                time.sleep(on_percent * self.cycletime)

                if DEVICE_DEBUG:
                    log.debug('SSR was on for {0}'.format(datetime.datetime.now()-on_start))

            if self.on_percent < 1.0:
                self.set_ssr_state(False)

                if DEVICE_DEBUG:
                    log.debug('Turning off SSR')
                    off_start = datetime.datetime.now()

                time.sleep((1.0-on_percent)*self.cycletime)

                if DEVICE_DEBUG:
                    log.debug('SSR was off for {0}'.format(datetime.datetime.now()-off_start))

            if DEVICE_DEBUG:
                log.debug(' * On/Off cycle lasted for {0} *'.format(datetime.datetime.now()-loop_start))
