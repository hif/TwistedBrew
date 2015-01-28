#!/usr/bin python
#import django.conf
#import sys
#import twisted_brew.settings

#django.conf.settings.configure()
#django.conf.settings.DATABASES = twisted_brew.settings.DATABASES
#django.conf.settings.INSTALLED_APPS = twisted_brew.settings.INSTALLED_APPS

from django.core.management.base import BaseCommand, CommandError
from django.utils import translation

from core.utils import coreutils
import core.defaults as defaults
from core.master import Master


class Command(BaseCommand):
    help = 'Starts the Twisted Brew master and or workers according to the given config file'
    can_import_settings = True

    def handle(self, *args, **options):
        from django.conf import settings
        translation.activate(settings.LANGUAGE_CODE)
        if len(args) > 0:
            config_file = args[0]
        else:
            config_file = defaults.DEFAULT_CONFIG
        try:
            self.stdout.write('Starting Twisted Brew (config:{0})'.format(config_file))
            master = None
            config = coreutils.parse_config(config_file)
            if config.master is not None:
                master = Master(config.communication, config.master)
            coreutils.start_workers(config)
            if not master is None:
                master.info()
                master.start()
        except Exception as e:
            raise CommandError('Could not start Twisted Brew: {0}'.format(e.__class__.__name__))
        self.stdout.write('Successfully started Twisted Brew')
