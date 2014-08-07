import time

from masters.brewmaster import BrewMaster
from utils import brewutils
from workers.boil import BoilWorker
from workers.mash import MashWorker
from workers.fermentation import FermentationWorker


def startworkers():
    worker = MashWorker("The Mashing Dude")
    worker.start()

    worker = BoilWorker("Mr Boiler")
    worker.start()

    worker = FermentationWorker("Fermat")
    worker.start()


def startmanually():
    print("[*] Giving workers time to initialize")
    startworkers()
    time.sleep(1)

    brewmaster = BrewMaster()
    brewmaster.start()
    return brewmaster


def test(brewmaster):
    r = "dummy"
    f = "dummy"

    brewmaster.load(r, f)
    brewmaster.info()

    print("[*] Giving workers time to register")
    while len(brewmaster.workers) < 3:
        time.sleep(1)
    print("[*] Workers:")
    for worker in brewmaster.workers:
        print('    - {0}'.format(worker))

    mashworker = brewmaster.getworkers("MashWorker")[0]
    boilworker = brewmaster.getworkers("BoilWorker")[0]
    fermentationworker = brewmaster.getworkers("FermentationWorker")[0]

    brewmaster.sendcommand('mash', mashworker)
    time.sleep(1)
    brewmaster.sendcommand('boil', boilworker)
    time.sleep(1)
    brewmaster.sendcommand('ferment', fermentationworker)
    time.sleep(1)
    brewmaster.sendcommand('pause', mashworker)
    time.sleep(1)
    brewmaster.sendcommand('reset', boilworker)
    time.sleep(1)
    brewmaster.sendcommand('resume', fermentationworker)

    time.sleep(1)
    print("[*] Giving all processes time to finish their work before killing all")
    time.sleep(1)
    print("[*] Killing workers")
    brewmaster.sendcommand('stop', mashworker)
    brewmaster.sendcommand('stop', boilworker)
    brewmaster.sendcommand('stop', fermentationworker)
    time.sleep(1)
    print("[*] Killing master")
    brewmaster.shutdown()


def startautomatically():
    return brewutils.startfromconfig()

# master = startManually()
master = startautomatically()
test(master)