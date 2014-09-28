#!/usr/bin python

from core.workers.baseworker import *
from core.utils.pid import PID


BOIL_DEBUG_INIT_TEMP = 60.0
BOIL_DEBUG_CYCLE_TIME = 10.0
BOIL_DEBUG_DELAY = 4
BOIL_DEBUG_WATTS = 5500.0  # 1 x 5500.0
BOIL_DEBUG_LITERS = 50.0
BOIL_DEBUG_COOLING = 0.002
BOIL_DEBUG_TIME_DIVIDER = 60
BOIL_DEBUG_TIMEDELTA = 10  # seconds


class BoilWorker(BaseWorker):
    def __init__(self, name):
        BaseWorker.__init__(self, name)
        self.pid = None
        self.kpid = None
        self.current_temperature = 0.0
        self.current_set_temperature = 0.0
        self.test_temperature = BOIL_DEBUG_INIT_TEMP

    def on_start(self):
        log.debug('Waiting for boil schedule. To exit press CTRL+C')

    def work(self, data):
        try:
            log.debug('Receiving boil schedule...')
            self.working = True
            self.hold_timer = None
            self.hold_pause_timer = None
            self.pause_time = timedelta(seconds=0)
            self.do_work(data)
        except Exception, e:
            log.debug('Boil worker failed to start work: {0}'.format(e.message))
            self.stop_all_devices()

    def do_work(self, data):
        self.pause_all_devices()
        self.current_set_temperature = float(data.target)
        self.hold_timer = None
        self.hold_pause_timer = None
        seconds = data.hold_time * data.time_unit_seconds
        if self.simulation:
            seconds /= BOIL_DEBUG_TIME_DIVIDER
            self.inputs['Temperature'].test_temperature = BOIL_DEBUG_INIT_TEMP
        self.current_hold_time = timedelta(seconds=seconds)
        cycle_time = float(self.inputs['Temperature'].cycle_time)
        if self.pid is None:
            self.pid = PID(None, self.current_set_temperature, cycle_time)
        else:
            self.pid = PID(self.pid.pid_params, self.current_set_temperature, cycle_time)
        self.resume_all_devices()

    def boil_temperature_callback(self, measured_value):
        try:
            calc = 0.0
            if self.pid is not None:
                calc = self.pid.calculate(measured_value, self.current_set_temperature)
                log.debug('{0} reports measured value {1} and pid calculated {2}'.
                          format(self.name, measured_value, calc))
            else:
                log.debug('{0} reports measured value {1}'.format(self.name, measured_value))
            self.current_temperature = measured_value
            measurement = self.generate_worker_measurement(self, self.inputs['Temperature'])
            measurement.value = self.current_temperature
            measurement.set_point = self.current_set_temperature
            measurement.work = 'Probing temperature'
            measurement.remaining = self.remaining_time_info()
            if self.simulation:
                self.test_temperature = self.current_temperature
                measurement.debug_timer = self.debug_timer
                self.debug_timer += timedelta(seconds=BOIL_DEBUG_TIMEDELTA)
            else:
                measurement.debug_timer = None
            self.send_measurement(measurement)
            if self.working and self.hold_timer is None and measured_value >= self.current_set_temperature:
                self.hold_timer = dt.now()
            if self.is_done():
                self.finish()
            elif self.pid is not None:
                self.outputs['Mash Tun'].write(calc)
        except Exception, e:
            log.error('Boil worker unable to react to temperature update, shutting down: {0}'.format(e.message))
            self.stop_all_devices()

    def boil_heating_callback(self, heating_time):
        try:
            log.debug('{0} reports heating time of {1} seconds'.format(self.name, heating_time))
            device = self.outputs['Mash Tun']
            measurement = self.generate_worker_measurement(self, device)
            measurement.value = heating_time
            measurement.set_point = device.cycle_time
            if self.hold_timer is None:
                measurement.work = 'Bringing to Boil'
                measurement.remaining = self.current_set_temperature - self.current_temperature
            else:
                measurement.work = 'Boiling'
                measurement.remaining = 0.0
            if self.simulation:
                measurement.debug_timer = self.debug_timer
            else:
                measurement.debug_timer = None
            self.send_measurement(measurement)
            if self.simulation:
                try:
                    self.inputs['Temperature'].test_temperature = \
                        PID.calc_heating(self.current_temperature,
                                         BOIL_DEBUG_WATTS,
                                         heating_time,
                                         device.cycle_time,
                                         BOIL_DEBUG_LITERS,
                                         BOIL_DEBUG_COOLING,
                                         BOIL_DEBUG_DELAY,
                                         BOIL_DEBUG_INIT_TEMP)
                except Exception, e:
                    log.debug('Boil worker unable to update test temperature for debug: {0}'.format(e.message))
        except Exception, e:
            log.error('Boil worker unable to react to heating update, shutting down: {0}'.format(e.message))
            self.stop_all_devices()
