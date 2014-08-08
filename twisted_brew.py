#!/usr/bin python
import django.conf
import web.web.settings


django.conf.settings.configure()
django.conf.settings.DATABASES = web.web.settings.DATABASES

import sys
from utils import brewutils
import masters.defaults as defaults

configfile = defaults.DEFAULT_CONFIG
if len(sys.argv) > 1:
    configfile = sys.argv[1]

print('Starting Twisted Brew (config:{0})'.format(configfile))

master = brewutils.start_from_config(configfile)
if not master is None:
    master.info()

# Uncomment next two lines to insert mesurement debug data
#from web.twistedbrew.models import Measurement
#Measurement.populate()
