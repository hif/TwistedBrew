from config import brewconfig
from masters import brewmaster
from workers import brewworker
import masters.defaults as defaults
import utils.logging as log


def loadworker(config):
    try:
        modulename = config.classname.lower()
        if not modulename.endswith('worker'):
            log.debug('Worker module {0} not found'.format(modulename), log.ERROR)
            return None
        modulename = modulename[:-6]
        package = 'workers.' + modulename
        module = __import__(package)
        workerclass = getattr(getattr(module, modulename), config.classname)
        instance = workerclass(config.name)
        instance.ip = config.ip
        instance.port = config.port
        instance.inputs = config.inputs
        instance.outputs = config.outputs
        return instance
    except Exception, e:
        log.error('Unable to load worker from config: {0}'.format(e))
        return None

def startfromconfig(configfile=defaults.DEFAULT_CONFIG):
    try:
        config = brewconfig.BrewConfig(configfile)
        master = None
        if config.master is not None:
            master = brewmaster.BrewMaster(config.master)
        workers = []
        for workerconfig in config.workers:
            workers.append(loadworker(workerconfig))

        for worker in workers:
            worker.start()
        if master is not None:
            master.start()
        return master
    except Exception, e:
        log.error('Unable to start all from config: {0}'.format(e))
        return None