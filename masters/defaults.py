MessageServerIP = "localhost"
MessageServerPort = 5672
BroadcastExchange = "BrewBroadcast"
MasterQueue = "BrewMaster"
DefaultRecipeFile = "recipes/small.bsmx"

DefaultDBHost = 'localhost'
DefaultDBPort = '5432'
DefaultDBUser = 'twistedbrewer'
DefaultDBPassword = 'twistedbrewer'
DefaultDB = 'twistedbrew'

DefaultDBConnectionString = "dbname='{4}' user='{2}' host='{0}' port='{1}' password='{3}'".\
    format(DefaultDBHost, DefaultDBPort, DefaultDBUser, DefaultDBPassword, DefaultDB)
