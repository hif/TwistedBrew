#!/usr/bin python
# The default config file name
DEFAULT_CONFIG = 'config/twisted_brew.yml'

MessageServerIP = "localhost"
MessageServerPort = 5672
MasterQueue = "MasterQueue"
BroadcastExchange = "TwistedBrewBroadcast"

DefaultDBHost = 'localhost'
DefaultDBPort = '5432'
DefaultDBUser = 'twistedbrewer'
DefaultDBPassword = 'twistedbrewer'
DefaultDB = 'twistedbrew'

DefaultDBConnectionString = "dbname='{4}' user='{2}' host='{0}' port='{1}' password='{3}'".\
    format(DefaultDBHost, DefaultDBPort, DefaultDBUser, DefaultDBPassword, DefaultDB)
