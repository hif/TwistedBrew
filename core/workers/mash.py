#!/usr/bin python

from core.workers.baseworker import *
from core.utils.pid import PID


MASH_DEBUG_INIT_TEMP = 60.0
MASH_DEBUG_CYCLE_TIME = 10.0
MASH_DEBUG_DELAY = 4
MASH_DEBUG_WATTS = 5500.0  # 1 x 5500.0
MASH_DEBUG_LITERS = 50.0
MASH_DEBUG_COOLING = 0.002
MASH_DEBUG_TIME_DIVIDER = 60
MASH_DEBUG_TIMEDELTA = 10  # seconds


class MashWorker(BaseWorker):

    def __init__(self, name):
        BaseWorker.__init__(self, name)
        self.pid = None
        self.kpid = None
        self.current_temperature = 0.0
        self.current_set_temperature = 0.0
        self.test_temperature = MASH_DEBUG_INIT_TEMP

    def on_start(self):
        log.debug('Waiting for mash schedule. To exit press CTRL+C', True)

    #def work(self, ch, method, properties, body):
    def work(self, data):
        try:
            log.debug('Receiving mash schedule...')
            self.working = True
            self.hold_timer = None
            self.hold_pause_timer = None
            self.pause_time = timedelta(seconds=0)
            self.do_work(data)
        except Exception as e:
            log.debug('Mash worker failed to start work: {0}'.format(e.args[0]))
            self.stop_all_devices()

    def do_work(self, data):
        self.pause_all_devices()
        self.current_set_temperature = float(data.target)
        self.hold_timer = None
        self.hold_pause_timer = None
        seconds = data.hold_time * data.time_unit_seconds
        if self.simulation:
            seconds /= MASH_DEBUG_TIME_DIVIDER
            self.inputs['Temperature'].test_temperature = MASH_DEBUG_INIT_TEMP
        self.current_hold_time = timedelta(seconds=seconds)
        cycle_time = float(self.inputs['Temperature'].cycle_time)
        if self.pid is None:
            self.pid = PID(None, self.current_set_temperature, cycle_time)
        else:
            self.pid = PID(self.pid.pid_params, self.current_set_temperature, cycle_time)
        self.resume_all_devices()

    def mash_temperature_callback(self, measured_value):
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
            if self.hold_timer is None:
                measurement.work = 'Current temperature'
                measurement.remaining = '{:.2f}'.format(self.current_temperature)
            else:
                measurement.work = 'Mashing'
                measurement.remaining = self.remaining_time_info()
            if self.simulation:
                self.test_temperature = self.current_temperature
                measurement.debug_timer = self.debug_timer
                self.debug_timer += timedelta(seconds=MASH_DEBUG_TIMEDELTA)
            else:
                measurement.debug_timer = None
            self.send_measurement(measurement)
            if self.working and self.hold_timer is None and measured_value >= self.current_set_temperature:
                self.hold_timer = dt.now()
            if self.is_done():
                self.finish()
            elif self.pid is not None:
                self.outputs['Mash Tun'].write(calc)
        except Exception as e:
            log.error('Mash worker unable to react to temperature update, shutting down: {0}'.format(e.args[0]))
            self.stop_all_devices()

    def mash_heating_callback(self, heating_time):
        try:
            log.debug('{0} reports heating time of {1} seconds'.format(self.name, heating_time))
            device = self.outputs['Mash Tun']
            measurement = self.generate_worker_measurement(self, device)
            measurement.value = heating_time
            measurement.set_point = device.cycle_time
            if self.hold_timer is None:
                measurement.work = 'Heating left'
                measurement.remaining = '{:.2f}'.format(self.current_set_temperature - self.current_temperature)
            else:
                measurement.work = 'Holding temperature'
                measurement.remaining = '{:.2f} -> {:.2f} ({:+.2f})'.format(
                    self.current_temperature,
                    self.current_set_temperature,
                    (self.current_temperature - self.current_set_temperature))
            if self.simulation:
                measurement.debug_timer = self.debug_timer
            else:
                measurement.debug_timer = None
            self.send_measurement(measurement)
            if self.simulation:
                try:
                    self.inputs['Temperature'].test_temperature = \
                        PID.calc_heating(self.current_temperature,
                                         MASH_DEBUG_WATTS,
                                         heating_time,
                                         device.cycle_time,
                                         MASH_DEBUG_LITERS,
                                         MASH_DEBUG_COOLING,
                                         MASH_DEBUG_DELAY,
                                         MASH_DEBUG_INIT_TEMP)
                except Exception as e:
                    log.debug('Mash worker unable to update test temperature for debug: {0}'.format(e.args[0]))
        except Exception as e:
            log.error('Mash worker unable to react to heating update, shutting down: {0}'.format(e.args[0]))
            self.stop_all_devices()
