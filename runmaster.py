from masters.defaults import *
from masters.brewmaster import BrewMaster
import thread
import time

r = "dummy"
f = "dummy"
#mashworker = "TheDude(Mashworker)"
#boilworker = "Mr Boiler(Boilworker)"
#fermentationworker = "AA(Fermentationworker)"

master = BrewMaster()
master.load(r, f)
master.start()

print("[*] Giving workers time to register")
while(len(master.workers) < 3):
    time.sleep(1)
print("[*] Workers:{0}".format(master.workers))

mashworker = master.getWorkers("MashWorker")[0]
boilworker = master.getWorkers("BoilWorker")[0]
fermentationworker = master.getWorkers("FermentationWorker")[0]

master.mash(mashworker)
master.boil(boilworker)
master.ferment(fermentationworker)

master.pause(mashworker)
master.reset(boilworker)
master.resume(fermentationworker)
