from masters.defaults import *
from workers.mash import MashWorker

worker = MashWorker("TheDude(Mashworker)")
worker.start()