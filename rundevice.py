#!/usr/bin python
from devices.device import Device
from devices.probe import Probe
from devices.ssr import SSR
#from config.brewconfig import IOConfig
import utils.logging as log

# Fake the configs that are normally read from YAML file and built by a brewworker
# Mash probe
#probeconfig = IOConfig('Temperature', 'Probe', '/sys/bus/w1/devices/28-00000607f0de/w1_slave')
# Mash SSR
#ssrconfig = IOConfig('Mash Tun', 'SSR', '/sys/class/gpio/gpio17/value')

# Construct the devices
#probe = Probe(probeconfig)
#ssr = SSR(ssrconfig)

# Fix for RasberryPi
probe = Probe()
probe.name = 'Temperature'
probe.io = '/sys/bus/w1/devices/28-00000607f0de/w1_slave'
ssr = SSR()
ssr.name = 'Mash Tun'
ssr.io = '/sys/class/gpio/gpio17/value'

# Use built in function to initialize, check if registered and if not register the device
ok, message = probe.autostart()
if not ok:
    log.error(message)
ok, message = ssr.autostart()
if not ok:
    log.error(message)

# Example of accessing device data intially read from YAML(here faked)
print ('Device of type {0} is named {1} and uses io path {2}'.format(probe.devicetype(), probe.name, probe.io))
print ('Device of type {0} is named {1} and uses io path {2}'.format(ssr.devicetype(), ssr.name, ssr.io))

# Do something with the devices

# Do something more
log.debug(probe.read())