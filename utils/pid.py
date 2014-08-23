#!/usr/bin python
from devices.device import Device
import time
import datetime
import threading
import Queue


GMA_HLIM = 100.0
GMA_LLIM = 0.0


class PIDParams:
    def __init__(self):
        kc = 0.0 		# Controller gain
        ti = 0.0 		# Time-constant for I action
        td = 0.0 		# Time-constant for D action
        ts = 0.0 		# Sample time [sec.] from Dialog Box
        k_lpf = 0.0 	# Time constant [sec.] for LPF
        k0 = 0.0 		# k0 value for PID controller
        k1 = 0.0 		# k1 value for PID controller
        k2 = 0.0 		# k2 value for PID controller
        k3 = 0.0 		# k3 value for PID controller
        lpf1 = 0.0 	# value for LPF filter
        lpf2 = 0.0 	# value for LPF filter
        ts_ticks = 0 	# ticks for timer
        pid_model = 0 	# PID Controller type [0..3]
        pp = 0.0 		# debug
        pi = 0.0 		# debug
        pd = 0.0 		# debug




PID_ACTIVE = 0
PID_INACTIVE = 1
PID_TERMINATE = 2

PID_UPPER_LIMIT = 256.0
PID_LOWER_LIMIT = -256.0


class ProcessPID(threading.Thread):
    def __init__(self, pid, device, dt, callback):
        threading.Thread.__init__(self)
        self.pid = pid
        self.device = device
        self.dt = dt
        self.status = PID_INACTIVE
        self.callback = callback

    def run(self):
        self.status = PID_ACTIVE
        while self.status != PID_TERMINATE:
            measured_value = float(self.device.read())
            calc = self.pid.calculate(measured_value, self.dt)
            self.callback(measured_value, calc)
            time.sleep(self.dt)


class PID():
    def __init__(self, setpoint, kp=1, ki=1, kd=1):
        # Parameters
        self.kp = kp
        self.ki = ki
        self.kd = kd
        # Variables for the PID algorithm
        self.previous_error = 0
        self.integral = 0
        self.setpoint = setpoint
        self.timestamp = None

    def calculate(self, measured_value, dt):
        error = self.setpoint - measured_value
        self.integral = error * dt
        derivative = (error - self.previous_error) / dt
        output = float((self.kp * error) + (self.ki * self.integral) + (self.kd * derivative))
        self.previous_error = error
        if output > PID_UPPER_LIMIT:
            output = PID_UPPER_LIMIT
        elif output < PID_LOWER_LIMIT:
            output = PID_LOWER_LIMIT
        output /= PID_UPPER_LIMIT
        return output

    heating_delay = Queue.Queue()

    @staticmethod
    def calc_heating(current, watts, seconds, liters, cooling, delay=10, minimum=10.0):
        if seconds > 0:
            # 4,184 watts will heat a liter up by 1C every second.
            time_watts = watts / seconds
            liter_watts = time_watts / 4184
            result = liter_watts / liters
        else:
            result = 0.0
        PID.heating_delay.put(result)
        if PID.heating_delay.qsize() >= delay:
            result = PID.heating_delay.get()
        else:
            result = 0.0
        result = current + result - (cooling * seconds)
        if result < minimum:
            return minimum
        return result
