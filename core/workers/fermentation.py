#!/usr/bin python
import random

from core.workers.baseworker import *
from core.utils.pid import PID


FERMENTATION_DEBUG_INIT_TEMP = 60.0
FERMENTATION_DEBUG_CYCLE_TIME = 10.0
FERMENTATION_DEBUG_DELAY = 4
FERMENTATION_DEBUG_WATTS = 5500.0  # 1 x 5500.0
FERMENTATION_DEBUG_LITERS = 50.0
FERMENTATION_DEBUG_COOLING = 0.002
FERMENTATION_DEBUG_TIME_DIVIDER = 21600
FERMENTATION_DEBUG_STD = 1.0
FERMENTATION_DEBUG_TIMEDELTA = 900  # seconds


class FermentationWorker(BaseWorker):
    def __init__(self, name):
        BaseWorker.__init__(self, name)
        self.pid = None
        self.kpid = None
        self.current_temperature = 0.0
        self.current_set_temperature = 0.0
        self.test_temperature = FERMENTATION_DEBUG_INIT_TEMP

    def on_start(self):
        log.debug('Waiting for fermentation schedule. To exit press CTRL+C')

    def work(self, data):
        try:
            log.debug('Receiving fermentation schedule...')
            self.working = True
            self.hold_timer = None
            self.hold_pause_timer = None
            self.pause_time = timedelta(seconds=0)
            self.do_work(data)
        except Exception, e:
            log.debug('Fermentation worker failed to start work: {0}'.format(e.message))
            self.stop_all_devices()

    def do_work(self, data):
        self.pause_all_devices()
        self.current_set_temperature = float(data.target)
        self.hold_timer = None
        self.hold_pause_timer = None
        seconds = data.hold_time * data.time_unit_seconds
        if self.simulation:
            seconds /= FERMENTATION_DEBUG_TIME_DIVIDER
        self.current_hold_time = timedelta(seconds=seconds)
        cycle_time = float(self.inputs['Temperature'].cycle_time)
        if self.pid is None:
            self.pid = PID(None, self.current_set_temperature, cycle_time)
        else:
            self.pid = PID(self.pid.pid_params, self.current_set_temperature, cycle_time)
        self.resume_all_devices()

    def fermentation_temperature_callback(self, measured_value):
        self.current_temperature = random.gauss(self.current_set_temperature, FERMENTATION_DEBUG_STD)
        if self.simulation:
            self.send_measurement(self.inputs['Temperature'],
                             [self.current_temperature, self.current_set_temperature, self.debug_timer])
            self.debug_timer += timedelta(seconds=FERMENTATION_DEBUG_TIMEDELTA)
        else:
            self.send_measurement(self.inputs['Temperature'], [self.current_temperature, self.current_set_temperature])
        log.debug('{0} reports measured value {1}'.format(self.name, self.current_temperature))
        if self.working and self.hold_timer is None:
            self.hold_timer = dt.now()
        if self.is_done():
            self.done()

    def fermentation_heating_callback(self, heating_time):
        return