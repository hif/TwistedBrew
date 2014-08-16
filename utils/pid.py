#!/usr/bin python
from devices.device import Device
import time
import datetime
import threading

# Psudo Code
#previous_error = 0
#integral = 0
#start:
#  error = setpoint - measured_value
#  integral = integral + error*dt
#  derivative = (error - previous_error)/dt
#  output = Kp*error + Ki*integral + Kd*derivative
#  previous_error = error
#  wait(dt)
#  goto start



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
    def __init__(self, setpoint, kp = 1, ki = 1, kd = 1):
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
        derivative = (error - self.previous_error)/dt
        output = float((self.kp * error) + (self.ki * self.integral) + (self.kd * derivative))
        self.previous_error = error
        if output > PID_UPPER_LIMIT:
            output = PID_UPPER_LIMIT
        elif output < PID_LOWER_LIMIT:
            output = PID_LOWER_LIMIT
        output = output/PID_UPPER_LIMIT
        return output