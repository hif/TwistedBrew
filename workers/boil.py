#!/usr/bin python
from workers.brewworker import *
from schedules.boil import *
from datetime import datetime as dt
from datetime import timedelta as timedelta
from utils.pid import PID
from devices.device import DEVICE_DEBUG


BOIL_DEBUG_INIT_TEMP = 60.0
BOIL_DEBUG_CYCLETIME = 10.0
BOIL_DEBUG_DELAY = 4
BOIL_DEBUG_WATTS = 5500.0  # 1 x 5500.0
BOIL_DEBUG_LITERS = 50.0
BOIL_DEBUG_COOLING = 0.002
BOIL_DEBUG_TIME_DIVIDER = 1


class BoilWorker(BrewWorker):
    def __init__(self, name):
        BrewWorker.__init__(self, name)
        self.pid = None
        self.kpid = None
        self.current_temperature = 0.0
        self.current_set_temperature = 0.0
        self.test_temperature = BOIL_DEBUG_INIT_TEMP

    def on_start(self):
        log.debug('Waiting for boil schedule. To exit press CTRL+C')

    def work(self, ch, method, properties, body):
        try:
            log.debug('Receiving boil schedule...')
            self.working = True
            self.step = -1
            self.hold_timer = None
            self.hold_pause_timer = None
            self.pause_time = 0
            self.schedule = BoilSchedule()
            self.schedule.from_yaml(body)
            print(self.schedule.name)
            for step in self.schedule.steps:
                print(step)

            self.next_step()
        except Exception, e:
            log.debug('Boil worker failed to start work: {0}'.format(e.message))
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
        self.current_set_temperature = float(self.schedule.steps[self.step].temp)
        # Convert time in minutes to seconds
        self.hold_timer = None
        self.hold_pause_timer = None
        minutes = int(self.schedule.steps[self.step].min)
        if DEVICE_DEBUG:
            minutes /= MASH_DEBUG_TIME_DIVIDER
        self.current_hold_time = timedelta(minutes=minutes)
        temperature = float(self.schedule.steps[self.step].temp)
        cycle_time = float(self.inputs['Temperature'].cycle_time)
        if self.pid is None:
            self.pid = PID(None, temperature, cycle_time)
        else:
            self.pid = PID(self.pid.pid_params, temperature, cycle_time)

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
            if DEVICE_DEBUG:
                self.test_temperature = self.current_temperature
            self.send_update(self.inputs['Temperature'], [self.current_temperature, self.current_set_temperature])
            if self.step >= 0 and self.hold_timer is None and measured_value >= self.current_set_temperature:
                self.hold_timer = dt.now()

            if not self.starting_next_step and self.is_step_done():
                self.starting_next_step = True
                self.next_step()
                self.starting_next_step = False
            elif self.pid is not None:
                self.outputs['Mash Tun'].write(calc)
        except Exception, e:
            log.error('Mash worker unable to react to temperature update, shutting down: {0}'.format(e.message))
            self.stop_all_devices()

    def boil_heating_callback(self, heating_time):
        try:
            log.debug('{0} reports heating time of {1} seconds'.format(self.name, heating_time))
            device = self.outputs['Mash Tun']
            self.send_update(device, [heating_time, device.cycle_time])
            if DEVICE_DEBUG:
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
                    log.debug('Mash worker unable to update test temperature for debug: {0}'.format(e.message))
        except Exception, e:
            log.error('Mash worker unable to react to heating update, shutting down: {0}'.format(e.message))
            self.stop_all_devices()
