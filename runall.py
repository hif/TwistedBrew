#!/usr/bin python
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

    mashworker = brewmaster.get_workers("MashWorker")[0]
    boilworker = brewmaster.get_workers("BoilWorker")[0]
    fermentationworker = brewmaster.get_workers("FermentationWorker")[0]

    brewmaster.send_command('mash', mashworker)
    time.sleep(1)
    brewmaster.send_command('boil', boilworker)
    time.sleep(1)
    brewmaster.send_command('ferment', fermentationworker)
    time.sleep(1)
    brewmaster.send_command('pause', mashworker)
    time.sleep(1)
    brewmaster.send_command('reset', boilworker)
    time.sleep(1)
    brewmaster.send_command('resume', fermentationworker)

    time.sleep(1)
    print("[*] Giving all processes time to finish their work before killing all")
    time.sleep(1)
    print("[*] Killing workers")
    brewmaster.send_command('stop', mashworker)
    brewmaster.send_command('stop', boilworker)
    brewmaster.send_command('stop', fermentationworker)
    time.sleep(1)
    print("[*] Killing master")
    brewmaster.shutdown()


def startautomatically():
    return brewutils.start_from_config()

# master = startManually()
master = startautomatically()
test(master)