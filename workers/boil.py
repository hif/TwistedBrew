from workers.brewworker import *
from masters.defaults import *
from masters.messages import *
from schedules.boil import *


class BoilWorker(BrewWorker):
    def __init__(self, name):
        BrewWorker.__init__(self,name)

    def onStart(self):
        print('[*] Waiting for boil schedule. To exit press CTRL+C')

    def work(self, ch, method, properties, body):
        print('[*] Receiving boil schedule...')
        scde = BoilSchedule()
        scde.fromYaml(body)
        print(scde.name)
        for step in scde.steps:
            print(step)