from config import brewconfig
from masters import brewmaster
from workers import brewworker
import time


def startFromConfig(file = brewconfig.DEFAULT_CONFIG):
    config = brewconfig.BrewConfig(file)
    master = None
    if(not config.master == None):
        master = brewmaster.BrewMaster(config.master)
    workers = []
    for workerconfig in config.workers:
        workers.append(brewworker.loadWorker(workerconfig))

    for worker in workers:
        worker.start()
    if(not master == None):
        master.start()
    return master