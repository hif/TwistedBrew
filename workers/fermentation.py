from workers.brewworker import *
from schedules.fermentation import *


class FermentationWorker(BrewWorker):
    def __init__(self, name):
        BrewWorker.__init__(self, name)

    def onstart(self):
        log.debug('Waiting for fermentation schedule. To exit press CTRL+C')

    def work(self, ch, method, properties, body):
        log.debug('Receiving fermentation schedule...')
        scde = FermentationSchedule()
        scde.fromyaml(body)
        print(scde.name)
        for step in scde.steps:
            print(step)