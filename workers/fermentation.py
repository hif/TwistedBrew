from workers.brewworker import *
from masters.defaults import *
from masters.messages import *
from schedules.fermentation import *


class FermentationWorker(BrewWorker):
    def __init__(self, name):
        BrewWorker.__init__(self,name)

    def onStart(self):
        print('[*] Waiting for fermentation schedule. To exit press CTRL+C')

    def work(self, ch, method, properties, body):
        print('[*] Receiving fermentation schedule...')
        scde = FermentationSchedule()
        scde.fromYaml(body)
        print(scde.name)
        for step in scde.steps:
            print(step)