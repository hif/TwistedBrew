from masters.defaults import *
from masters.brewmaster import BrewMaster
import thread
import time
import brewutils

from workers.boil import BoilWorker
from workers.mash import MashWorker
from workers.fermentation import FermentationWorker

def startWorkers():
    worker = MashWorker("The Mashing Dude")
    worker.start()

    worker = BoilWorker("Mr Boiler")
    worker.start()

    worker = FermentationWorker("Fermat")
    worker.start()

def startManually():
    print("[*] Giving workers time to initialize")
    startWorkers()
    time.sleep(1)

    master = BrewMaster()
    master.start()
    return master

def test(master):
    r = "dummy"
    f = "dummy"

    master.loadRecipe(r, f)
    master.info()

    print("[*] Giving workers time to register")
    while(len(master.workers) < 3):
        time.sleep(1)
    print("[*] Workers:")
    for worker in master.workers:
        print('    - {0}'.format(worker))

    mashworker = master.getWorkers("MashWorker")[0]
    boilworker = master.getWorkers("BoilWorker")[0]
    fermentationworker = master.getWorkers("FermentationWorker")[0]

    master.sendCommand('mash',mashworker)
    time.sleep(1)
    master.sendCommand('boil',boilworker)
    time.sleep(1)
    master.sendCommand('ferment',fermentationworker)
    time.sleep(1)
    master.sendCommand('pause',mashworker)
    time.sleep(1)
    master.sendCommand('reset',boilworker)
    time.sleep(1)
    master.sendCommand('resume',fermentationworker)

    time.sleep(1)
    print("[*] Giving all processes time to finish their work before killing all")
    time.sleep(3)
    print("[*] Killing workers")
    master.sendCommand('stop', mashworker)
    master.sendCommand('stop', boilworker)
    master.sendCommand('stop', fermentationworker)
    time.sleep(1)
    print("[*] Killing master")
    master.shutdown()

def startAutomatically():
    return brewutils.startFromConfig()

#master = startManually()
master = startAutomatically()
test(master)