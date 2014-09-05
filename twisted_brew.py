#!/usr/bin python
import django.conf

import web.settings


django.conf.settings.configure()
django.conf.settings.DATABASES = web.settings.DATABASES

import sys
from utils import brewutils
import masters.defaults as defaults

from web.models import Measurement, Message, Session
#Measurement.populate()
#Measurement.clear()
#Message.clear()

#Session.objects.all().delete()
#s = Session();
#s.name = 'Test'
#s.source = 'No Source'
#s.notes = 'No notes'
#s.locked = False
#s.save()

configfile = defaults.DEFAULT_CONFIG
if len(sys.argv) > 1:
    configfile = sys.argv[1]

print('Starting Twisted Brew (config:{0})'.format(configfile))

master = brewutils.start_from_config(configfile)
if not master is None:
    master.info()
