#!/usr/bin python
import threading
import time

import core.utils.logging as log


DEVICE_DEBUG_CYCLE_TIME = 1.0
DEVICE_PAUSE_CYCLE_TIME = 2.0

class Device(threading.Thread):
    def __init__(self, config, owner=None, simulation=False):
        threading.Thread.__init__(self)
        self.shutdown = False
        self.owner = owner
        self.name = config.name
        self.io = config.io
        self.active = config.active
        self.cycle_time = config.cycle_time
        self.enabled = False
        self.simulation = simulation
        self.read_write_lock = threading.Lock()
        self.callback_name = config.callback
        self.callback = None

    def init(self):
        pass

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def is_active(self):
        return self.active

    def do_callback(self, measured_value):
        if self.enabled or self.active:
            self.callback(measured_value)

    def run_device(self):
        if self.enabled:
            return
        if hasattr(self.owner, self.callback_name):
            self.callback = getattr(self.owner, self.callback_name)
        else:
            log.error('Callback function {0} not found for owner {1}'.format(self.callback_name, self.owner))
        self.auto_setup()
        self.start()

    def pause_device(self):
        self.enabled = False

    def resume_device(self):
        self.enabled = True

    def stop_device(self):
        self.shutdown = True

    def run(self):
        while not self.shutdown:
            if self.enabled or self.active:
                self.run_cycle()
            else:
                time.sleep(DEVICE_PAUSE_CYCLE_TIME)

    def run_cycle(self):
        pass

    def check(self):
        if self.simulation:
            return True
        try:
            with open(self.io) as file:
                return True
        except IOError as e:
            log.warning("Unable to find/open \"{0}\"".format(self.io))
            return False

    def register(self):
        pass

    def write(self, value):
        pass

    def read(self):
        pass

    def devicetype(self):
        return self.__class__.__name__

    def auto_setup(self):
        """
        Calls the default startup sequence for any device using the device interface functions.
        First it is initalized, the checks for registration in the OS (if needed) and finally
        registers it if no registration is found.
        :return: True, None if everything is ok or False, [error message] if it fails.
        """
        try:
            self.init()
            if not self.check():
                self.register()
            return True, None
        except Exception, e:
            return False, e.message

