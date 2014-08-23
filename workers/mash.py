#!/usr/bin python
from workers.brewworker import *
from schedules.mash import *
from datetime import datetime as dt
from datetime import timedelta as timedelta
import time
from utils.pid import PID
from devices.device import DEVICE_DEBUG,DEVICE_DEFAULT_CYCLETIME


MASH_DEBUG_INIT_TEMP = 67.0
MASH_DEBUG_CYCLETIME = 2.0
MASH_DEBUG_DELAY = 4
MASH_DEBUG_WATTS = 55000.0# 10 x 5500.0
MASH_DEBUG_LITERS = 50.0
MASH_DEBUG_COOLING = 0.001
MASH_DEBUG_TIME_DIVIDER = 60

class MashWorker(BrewWorker):
    def __init__(self, name):
        BrewWorker.__init__(self, name)
        #self.process = None
        self.pid = None
        self.current_temperature = 0.0
        self.current_set_temperature = 0.0
        self.current_hold_time = 0.0
        self.hold_temperature_timer = None
        self.hold_temperature_pause_timer = None
        self.pause_time = 0.0
        self.cycle_time = DEVICE_DEFAULT_CYCLETIME
        self.stopping_all_devices = False
        self.starting_next_step = False


    def on_start(self):
        log.debug('Waiting for mash schedule. To exit press CTRL+C')

    def work(self, ch, method, properties, body):
        try:
            log.debug('Receiving mash schedule...')
            self.working = True
            self.step = -1
            self.hold_temperature_timer = None
            hold_temperature_pause_timer = None
            self.pause_time = 0
            self.schedule = MashSchedule()
            self.schedule.from_yaml(body)
            print(self.schedule.name)
            for step in self.schedule.steps:
                print("Name: ", step.name)
                print("Temp: ", step.temp)
                print("Min : ", step.min)

            self.next_step()
        except Exception, e:
            log.debug('Mash worker failed to start work: {0}'.format(e.message))
            self.stop_all_devices()

    def on_pause(self):
        log.debug('Pause {0}'.format(self))
        self.hold_temperature_pause_timer = dt.now()
        return True

    def on_resume(self):
        log.debug('Resume {0}'.format(self))
        self.pause_time += (dt.now() - self.hold_temperature_pause_timer)
        return True

    def on_reset(self):
        self.stop_all_devices()
        return True

    def is_step_done(self):
        if self.hold_temperature_timer is None:
            return False
        pause_total = timedelta(seconds=self.pause_time)
        finish_time = dt.now()-self.hold_temperature_timer
        mash_time = self.current_hold_time + pause_total
        if finish_time >= mash_time:
            return True
        log.debug('Time untill step done: {0}'.format(finish_time - mash_time))
        return False

    def start_all_devices(self):
        log.debug('Starting all devices')
        if DEVICE_DEBUG:
            self.inputs['Temperature'].test_temperature = MASH_DEBUG_INIT_TEMP
        self.inputs['Temperature'].assign_callback(self.temperature_callback)
        self.outputs['Mash Tun'].assign_callback(self.heating_callback)
        self.inputs['Temperature'].start_device()
        time.sleep(self.cycle_time/2.0) # Let devices alternate
        self.outputs['Mash Tun'].start_device()

    def stop_all_devices(self):
        if self.stopping_all_devices:
            return
        self.stopping_all_devices = True
        while self.is_device_running():
            log.debug('Trying to stop all devices...')
            if len(self.inputs) != 0:
                self.inputs['Temperature'].stop_device()
            if len(self.outputs) != 0:
                self.outputs['Mash Tun'].stop_device()
            time.sleep(1)
        log.debug('All devices stopped')
        self.stopping_all_devices = False

    def is_device_running(self):
        if len(self.inputs) != 0:
            if self.inputs['Temperature'].enabled:
                return True
        if len(self.outputs) != 0:
            if self.outputs['Mash Tun'].enabled:
                return True

    def next_step(self):
        try:
            self.step += 1
            if self.step > 0:
                self.stop_all_devices()
            if self.step >= len(self.schedule.steps):
                return False
            log.debug('Starting step {0} of {1}'.format(self.step+1, self.schedule.steps))
            if DEVICE_DEBUG:
                self.cycle_time = MASH_DEBUG_CYCLETIME
            self.create_device_threads(self.cycle_time)
            self.current_set_temperature = float(self.schedule.steps[self.step].temp)
            # Convert time in minutes to seconds
            minutes = int(self.schedule.steps[self.step].min)
            if DEVICE_DEBUG:
                minutes /= MASH_DEBUG_TIME_DIVIDER
            self.current_hold_time = timedelta(minutes=minutes)
            temperature = float(self.schedule.steps[self.step].temp)
            cycle_time = float(self.inputs['Temperature'].cycle_time)
            self.pid = PID(temperature, cycle_time)
            self.start_all_devices()
            return True
        except Exception, e:
            log.error('Error in next_step: {0}'.format(e.message))

    def temperature_callback(self, measured_value):
        try:
            calc = self.pid.calculate(measured_value, self.current_set_temperature)
            log.debug('{0} reports measured value {1} and pid calculated {2}'.format(self.name, measured_value, calc))
            self.current_temperature = measured_value
            self.send_update(self.inputs['Temperature'], [self.current_temperature, self.current_set_temperature])
            if self.hold_temperature_timer is None and measured_value >= self.current_set_temperature:
                self.hold_temperature_timer = dt.now()

            if not self.starting_next_step and self.is_step_done():
                self.starting_next_step = True
                self.next_step()
                self.starting_next_step = False
            else:
                self.outputs['Mash Tun'].write(calc)
        except Exception, e:
            log.debug('Mash worker unable to react to temperature update, shutting down: {0}'.format(e.message))
            self.stop_all_devices()

    def heating_callback(self, heating_time):
        try:
            log.debug('{0} reports heating time of {1} seconds'.format(self.name, heating_time))
            device = self.outputs['Mash Tun']
            self.send_update(device, [heating_time, device.cycle_time])
            if DEVICE_DEBUG:
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
                except Exception, e:
                    log.debug('Mash worker unable to update test temperature for debug: {0}'.format(e.message))
        except Exception, e:
            log.debug('Mash worker unable to react to heating update, shutting down: {0}'.format(e.message))
            self.stop_all_devices()
