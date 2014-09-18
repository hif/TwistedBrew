#!/usr/bin python
from core.devices.probe import Probe
from core.devices.ssr import SSR
import core.utils.logging as log

# Fix for RasberryPi
probe = Probe()
probe.name = 'Temperature'
probe.io = 'C:\\temp\\28-00000607f0de\\w1_slave'
ssr = SSR()
ssr.name = 'Mash Tun'
ssr.io = 'C:\\temp\\gpio17\\value'

# Use built in function to initialize, check if registered and if not register the device
ok, message = probe.auto_setup()
if not ok:
    log.error(message)
ok, message = ssr.auto_setup()
if not ok:
    log.error(message)

# Example of accessing device data intially read from YAML(here faked)
print ('Device of type {0} is named {1} and uses io path {2}'.format(probe.devicetype(), probe.name, probe.io))
print ('Device of type {0} is named {1} and uses io path {2}'.format(ssr.devicetype(), ssr.name, ssr.io))

# Do something with the devices

# Do something more

