from masters.defaults import *
from masters.brewmaster import BrewMaster
import thread
import time

from workers.boil import BoilWorker
from workers.mash import MashWorker
from workers.fermentation import FermentationWorker

def startWorkers():
    worker = MashWorker("TheDude(Mashworker)")
    worker.start()

    worker = BoilWorker("Mr Boiler(Boilworker)")
    worker.start()

    worker = FermentationWorker("AA(Fermentationworker)")
    worker.start()

startWorkers()

r = "dummy"
f = "dummy"

master = BrewMaster()
master.loadRecipe(r, f)
master.start()

print("[*] Giving workers time to register")
while(len(master.workers) < 3):
    time.sleep(1)
print("[*] Workers:{0}".format(master.workers))

mashworker = master.getWorkers("MashWorker")[0]
boilworker = master.getWorkers("BoilWorker")[0]
fermentationworker = master.getWorkers("FermentationWorker")[0]

master.sendCommand('mash',mashworker)
master.sendCommand('boil',boilworker)
master.sendCommand('ferment',fermentationworker)

master.sendCommand('pause',mashworker)
master.sendCommand('reset',boilworker)
master.sendCommand('resume',fermentationworker)
