#!/usr/bin python
import random
from workers.brewworker import *
from schedules.fermentation import *
from datetime import datetime as dt
from datetime import timedelta as timedelta
from utils.pid import PID
from devices.device import DEVICE_DEBUG


FERMENTATION_DEBUG_INIT_TEMP = 60.0
FERMENTATION_DEBUG_CYCLETIME = 10.0
FERMENTATION_DEBUG_DELAY = 4
FERMENTATION_DEBUG_WATTS = 5500.0  # 1 x 5500.0
FERMENTATION_DEBUG_LITERS = 50.0
FERMENTATION_DEBUG_COOLING = 0.002
FERMENTATION_DEBUG_TIME_DIVIDER = 1
FERMENTATION_DEBUG_STD = 1.0


class FermentationWorker(BrewWorker):
    def __init__(self, name):
        BrewWorker.__init__(self, name)
        self.pid = None
        self.kpid = None
        self.current_temperature = 0.0
        self.current_set_temperature = 0.0
        self.test_temperature = FERMENTATION_DEBUG_INIT_TEMP

    def on_start(self):
        log.debug('Waiting for fermentation schedule. To exit press CTRL+C')

    def work(self, ch, method, properties, body):
        try:
            log.debug('Receiving fermentation schedule...')
            self.working = True
            self.step = -1
            self.hold_timer = None
            self.hold_pause_timer = None
            self.pause_time = 0
            self.schedule = FermentationSchedule()
            self.schedule.from_yaml(body)
            print(self.schedule.name)
            for step in self.schedule.steps:
                print(step)

            self.next_step()
        except Exception, e:
            log.debug('Fermentation worker failed to start work: {0}'.format(e.message))
            self.stop_all_devices()

    def on_pause(self):
        log.debug('Pause {0}'.format(self))
        self.hold_pause_timer = dt.now()
        return True

    def on_resume(self):
        log.debug('Resume {0}'.format(self))
        self.pause_time += (dt.now() - self.hold_pause_timer)
        return True

    def on_reset(self):
        self.pause_all_devices()
        return True

    def on_stop(self):
        self.stop_all_devices()
        return True

    def on_next_step(self):
        self.current_set_temperature = float(self.schedule.steps[self.step].starttemp)
        # Convert time in minutes to seconds
        self.hold_timer = None
        self.hold_pause_timer = None
        days = int(self.schedule.steps[self.step].days)
        if DEVICE_DEBUG:
            days /= FERMENTATION_DEBUG_TIME_DIVIDER
            self.current_hold_time = timedelta(minutes=days)
        else:
            self.current_hold_time = timedelta(days=days)
        cycle_time = float(self.inputs['Temperature'].cycle_time)
        if self.pid is None:
            self.pid = PID(None, self.current_set_temperature, cycle_time)
        else:
            self.pid = PID(self.pid.pid_params, self.current_set_temperature, cycle_time)

    def fermentation_temperature_callback(self, measured_value):
        self.current_temperature = random.gauss(self.current_set_temperature, FERMENTATION_DEBUG_STD)
        self.send_update(self.inputs['Temperature'], [self.current_temperature, self.current_set_temperature])
        log.debug('{0} reports measured value {1}'.format(self.name, self.current_temperature))
        if self.step >= 0 and self.hold_timer is None:
            self.hold_timer = dt.now()
        if not self.starting_next_step and self.is_step_done():
            self.starting_next_step = True
            self.next_step()
            self.starting_next_step = False
#
#        try:
#            calc = 0.0
#            if self.pid is not None:
#                calc = self.pid.calculate(measured_value, self.current_set_temperature)
#                log.debug('{0} reports measured value {1} and pid calculated {2}'.
#                          format(self.name, measured_value, calc))
#            else:
#                log.debug('{0} reports measured value {1}'.format(self.name, measured_value))
#            self.current_temperature = measured_value
#            if DEVICE_DEBUG:
#                self.test_temperature = self.current_temperature
#            self.send_update(self.inputs['Temperature'], [self.current_temperature, self.current_set_temperature])
#            if self.step >= 0 and self.hold_timer is None and measured_value >= self.current_set_temperature:
#                self.hold_timer = dt.now()
#
#            if not self.starting_next_step and self.is_step_done():
#                self.starting_next_step = True
#                self.next_step()
#                self.starting_next_step = False
#            elif self.pid is not None:
#                self.outputs['Fermenter'].write(calc)
#        except Exception, e:
#            log.error('Fermentation worker unable to react to temperature update, shutting down: {0}'.format(e.message))
#            self.stop_all_devices()

    def fermentation_heating_callback(self, heating_time):
        return
#        try:
#            log.debug('{0} reports heating time of {1} seconds'.format(self.name, heating_time))
#            device = self.outputs['Mash Tun']
#            self.send_update(device, [heating_time, device.cycle_time])
#            if DEVICE_DEBUG:
#                try:
#                    self.inputs['Temperature'].test_temperature = \
#                        PID.calc_heating(self.current_temperature,
#                                         FERMENTATION_DEBUG_WATTS,
#                                         heating_time,
#                                         device.cycle_time,
#                                         FERMENTATION_DEBUG_LITERS,
#                                         FERMENTATION_DEBUG_COOLING,
#                                         FERMENTATION_DEBUG_DELAY,
#                                         FERMENTATION_DEBUG_INIT_TEMP)
#                except Exception, e:
#                    log.debug('Fermentation worker unable to update test temperature for debug: {0}'.format(e.message))
#        except Exception, e:
#            log.error('Fermentation worker unable to react to heating update, shutting down: {0}'.format(e.message))
#            self.stop_all_devices()
#