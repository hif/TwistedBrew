from masters.defaults import *
from workers.fermentation import FermentationWorker

worker = FermentationWorker("AA(Fermentationworker)")
worker.start()