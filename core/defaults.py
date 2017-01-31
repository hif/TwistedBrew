#!/usr/bin python
# The default config file name
import os

DEFAULT_CONFIG = 'config/twisted_brew.yml'

MessageServerIP = os.environ.get('MASTER_IP', '0.0.0.0')
MessageServerMasterPort = int(os.environ.get('MASTER_PORT', '9991'))
MessageServerWorkerPort = int(os.environ.get('WORKER_PORT', '9992'))

DefaultDBHost = 'localhost'
DefaultDBPort = '5432'
DefaultDBUser = 'twistedbrewer'
DefaultDBPassword = 'twistedbrewer'
DefaultDB = 'twistedbrew'

DefaultDBConnectionString = "dbname='{4}' user='{2}' host='{0}' port='{1}' password='{3}'".\
    format(DefaultDBHost, DefaultDBPort, DefaultDBUser, DefaultDBPassword, DefaultDB)
