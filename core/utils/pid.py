#!/usr/bin python
from collections import deque

KC_DEFAULT = 75.0
TI_DEFAULT = 75.0
TD_DEFAULT = 5.0

class PIDParams:
    def __init__(self, last=None):
        # From http://www.vandelogt.nl/datasheets/pid_controller_calculus_v320.pdf
        self.kc = 0.0  # Controller gain
        self.ti = 0.0  # Time-constant for I action
        self.td = 0.0  # Time-constant for D action
        self.ts = 0.0  # Sample time [sec.]
        self.k_lpf = 0.0  # Time constant [sec.] for LPF
        self.k0 = 0.0  # k0 value for PID controller
        self.k1 = 0.0  # k1 value for PID controller
        self.k2 = 0.0  # k2 value for PID controller
        self.k3 = 0.0  # k3 value for PID controller
        self.lpf1 = 0.0  # value for LPF filter
        self.lpf2 = 0.0  # value for LPF filter
        self.ts_ticks = 0  # ticks for timer
        self.pid_model = 0  # PID Controller type [0..3]
        self.pp = 0.0  # debug
        self.pi = 0.0  # debug
        self.pd = 0.0  # debug
        if last is None:
            self.xk_1 = 0.0
            self.xk_2 = 0.0
            self.yk = 0.0
        else:
            self.xk_1 = last.xk_1
            self.xk_2 = last.xk_2
            self.yk = last.yk

    def update(self, xk):
        self.xk_2 = self.xk_1
        self.xk_1 = xk


class PID():
    GMA_HLIM = 100.0
    GMA_LLIM = 0.0
    def __init__(self, last_params, setpoint, cycle_time, kc=KC_DEFAULT, ti=TI_DEFAULT, td=TD_DEFAULT):
        self.setpoint = setpoint
        self.cycle_time = cycle_time
        # Parameters
        self.pid_params = PIDParams(last_params)
        self.pid_params.ts = self.cycle_time
        self.pid_params.kc = kc
        self.pid_params.ti = ti
        self.pid_params.td = td
        self.init_pid4(self.pid_params)

    def init_pid4(self, p):
        # From http://www.vandelogt.nl/datasheets/pid_controller_calculus_v320.pdf
        # Purpose  :
        # Variables:
        # Returns :
        # This function initialises the Allen Bradley Type A PID controller.
        # p: pointer to struct containing all PID parameters
        #       Kc.Ts
        # k0 =  -----   (for I-term)
        #        Ti
        #           Td
        # k1 = Kc . --  (for D-term)
        #           Ts
        # The LPF parameters are also initialised here:
        #      lpf[k] = lpf1 * lpf[k-1] + lpf2 * lpf[k-2]
        # No values are returned

        if p.ti == 0.0:
            p.k0 = 0.0
        else:
            p.k0 = p.kc * p.ts / p.ti
            #print 'k0 = {0} = p.{1} * {2} / {3}'.format(p.k0, p.kc, p.ts, p.ti)
        p.k1 = p.kc * p.td / p.ts
        #print 'k1 = {0} = {1} * {2} / {3}'.format(p.k1, p.kc, p.td, p.ts)
        p.lpf1 = (2.0 * p.k_lpf - p.ts) / (2.0 * p.k_lpf + p.ts)
        p.lpf2 = p.ts / (2.0 * p.k_lpf + p.ts)

    def pid_reg4(self, xk, tset, p, vrg):
        # From http:#www.vandelogt.nl/datasheets/pid_controller_calculus_v320.pdf
        # This function implements the Takahashi PID controller,
        # which is a type C controller: the P and D term are no
        # longer dependent on the set-point, only on PV (which is Thlt). The D term is NOT low-pass filtered.
        # This function should be called once every TS seconds.
        # The input variable x[k] (= measured temperature)
        # The output variable y[k] (= gamma value for power electronics)
        # The setpoint value for the temperature
        # Pointer to struct containing PID parameters
        # Release signal: 1 = Start control, 0 = disable PID controller No values are returned

        lpf = 0.0  # LPF output
        ek = tset - xk  # calculate e[k] = SP[k] - PV[k]
        if vrg:
            # Calculate PID controller:
            p.pp = p.kc * (p.xk_1 - xk)  # y[k] = y[k - 1] + Kc * (PV[k - 1] - PV[k])
            p.pi = p.k0 * ek           # + Kc * Ts / Ti * e[k]
            p.pd = p.k1 * (2.0 * p.xk_1 - xk - p.xk_2)
            p.yk += p.pp + p.pi + p.pd

        else:
            p.yk = p.pp = p.pi = p.pd = 0.0

        #print '{0} += {1} + {2} + {3}'.format(p.yk, p.pp, p.pi, p.pd)
        p.update(xk) # PV[k-2] = PV[k-1] and PV[k-1] = PV[k]
        # limit y[k] to GMA_HLIM and GMA_LLIM
        if p.yk > PID.GMA_HLIM:
            p.yk = PID.GMA_HLIM
        elif p.yk < PID.GMA_LLIM:
            p.yk = PID.GMA_LLIM

        return p.yk


    def calculate(self, measured_value, set_point):
        output = self.pid_reg4(measured_value, set_point, self.pid_params, True)
        return output / 100.0

    heating_delay = deque()

    @staticmethod
    def calc_heating(current, watts, seconds, dt, liters, cooling, delay=10, minimum=10.0):
        #log.debug('current={0}, watts={1}, seconds={2}, dt={3}, liters={4}, cooling={5}, delay={6}, minimum={7}'.format(current, watts, seconds, dt, liters, cooling, delay, minimum))
        if seconds > 0:
            # 4,184 watts will heat a liter up by 1C every second.
            time_watts = watts * seconds
            liter_watts = time_watts / 4184
            result = liter_watts / liters
        else:
            result = 0.0
        PID.heating_delay.appendleft(result)
        #log.debug('calc_heating: pushed {0}'.format(result))
        if len(PID.heating_delay) > delay:
            result = PID.heating_delay.pop()
            #log.debug('calc_heating: popped {0}'.format(result))
        else:
            result = 0.0
        #log.debug('calc_heating: {0} = {1} + {2} - ({3} * {4})'.format((current + result - (cooling * dt)),current, result, cooling, dt))
        result = current + result - (cooling * dt)
        if result < minimum:
            return minimum
        return result
