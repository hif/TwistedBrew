#!/usr/bin python
import django.conf
import sys
import twisted_brew.settings

django.conf.settings.configure()
django.conf.settings.DATABASES = twisted_brew.settings.DATABASES
django.conf.settings.INSTALLED_APPS = twisted_brew.settings.INSTALLED_APPS

from core.utils import coreutils
import core.defaults as defaults
from core.master import Master

configfile = defaults.DEFAULT_CONFIG

if len(sys.argv) > 1:
    configfile = sys.argv[1]

print('Starting Twisted Brew (config:{0})'.format(configfile))

master = None
config = coreutils.parse_config(configfile)
if config.master is not None:
    master = Master(config.communication, config.master)
coreutils.start_workers(config)
if not master is None:
    master.info()
    master.start()