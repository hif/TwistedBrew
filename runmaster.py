# coding=utf-8
from masters.brewmaster import BrewMaster
import time

#mashworker = "TheDude(Mashworker)"
#boilworker = "Mr Boiler(Boilworker)"
#fermentationworker = "AA(Fermentationworker)"

master = BrewMaster()
master.load(u'Bríó klón')
master.start()

print("[*] Giving workers time to register")
while len(master.workers) < 3:
    time.sleep(1)
print("[*] Workers:{0}".format(master.workers))

mashworker = master.getworkers("MashWorker")[0]
boilworker = master.getworkers("BoilWorker")[0]
fermentationworker = master.getworkers("FermentationWorker")[0]

master.mash(mashworker)
master.boil(boilworker)
master.ferment(fermentationworker)

master.pause(mashworker)
master.reset(boilworker)
master.resume(fermentationworker)
