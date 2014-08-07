from config import brewconfig
from masters import brewmaster
from workers import brewworker


def startfromconfig(configfile=brewconfig.DEFAULT_CONFIG):
    config = brewconfig.BrewConfig(configfile)
    master = None
    if config.master is not None:
        master = brewmaster.BrewMaster(config.master)
    workers = []
    for workerconfig in config.workers:
        workers.append(brewworker.loadworker(workerconfig))

    for worker in workers:
        worker.start()
    if master is not None:
        master.start()
    return master