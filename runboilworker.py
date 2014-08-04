from masters.defaults import *
from workers.boil import BoilWorker

worker = BoilWorker("Mr Boiler(Boilworker)")
worker.start()
