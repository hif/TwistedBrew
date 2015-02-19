#!/usr/bin python
# The default config file name
DEFAULT_CONFIG = 'config/twisted_brew.yml'

MessageServerIP = "192.168.1.65"
MessageServerMasterPort = 9991
MessageServerWorkerPort = 9992

DefaultDBHost = 'localhost'
DefaultDBPort = '5432'
DefaultDBUser = 'twistedbrewer'
DefaultDBPassword = 'twistedbrewer'
DefaultDB = 'twistedbrew'

DefaultDBConnectionString = "dbname='{4}' user='{2}' host='{0}' port='{1}' password='{3}'".\
    format(DefaultDBHost, DefaultDBPort, DefaultDBUser, DefaultDBPassword, DefaultDB)
