#!/usr/bin python
from workers.brewworker import *
from schedules.mash import *
from datetime import datetime as dt
import time


MASH_PID_CYCLE_TIME = 5.0

class MashWorker(BrewWorker):
    def __init__(self, name):
        BrewWorker.__init__(self, name)
        self.process = None
        self.current_goal_temp = 0.0
        self.current_hold_time = 0.0
        self.hold_temperature_timer = None
        self.hold_temperature_pause_timer = None
        self.pause_time = 0.0

    def on_start(self):
        log.debug('Waiting for mash schedule. To exit press CTRL+C')

    def work(self, ch, method, properties, body):
        log.debug('Receiving mash schedule...')
        self.schedule = MashSchedule()
        self.schedule.from_yaml(body)
        print(self.schedule.name)
        for step in self.schedule.steps:
            print("Name: ", step.name)
            print("Temp: ", step.temp)
            print("Min : ", step.min)
        self.next_step()

    def on_pause(self):
        log.debug('Pause {0}'.format(self))
        self.hold_temperature_pause_timer = dt.now()
        return True

    def on_resume(self):
        log.debug('Resume {0}'.format(self))
        self.pause_time += (dt.now() - self.hold_temperature_pause_timer)
        return True

    def is_step_done(self):
        if self.hold_temperature_timer is None:
            return False
        if (dt.now()-self.hold_temperature_timer) - self.pause_time >= self.current_hold_time:
            return True
        return False

    def next_step(self):
        try:
            if self.step > -1:
                self.process.status = PID_TERMINATE
                self.inputs['Temperature'].stop_device()
                self.outputs['Mash Tun'].stop_device()
                time.sleep(MASH_PID_CYCLE_TIME)
            self.step += 1
            if self.step >= len(self.schedule.steps):
                return False
            self.current_goal_temp = float(self.schedule.steps[self.step].temp)
            # Convert time in minutes to seconds
            self.current_hold_time = float(self.schedule.steps[self.step].min) * 60.0
            pid = PID(float(self.schedule.steps[self.step].temp))
            self.process = ProcessPID(pid, self.inputs['Temperature'], MASH_PID_CYCLE_TIME, self.pid_callback)
            self.inputs['Temperature'].start_device()
            self.outputs['Mash Tun'].start_device()
            self.process.run()
            return True
        except Exception, e:
            log.error('Error in next_step: {0}'.format(e.message))

    def pid_callback(self, measured_value, calc):
        log.debug('{0} reports measured value {1} and pid calculated {2}'.format(self.name, measured_value, calc))

        if self.hold_temperature_timer is None and measured_value >= self.current_goal_temp:
            self.hold_temperature_timer = dt.now()

        if self.is_step_done():
            self.next_step()
        else:
            self.outputs['Mash Tun'].write(calc)

