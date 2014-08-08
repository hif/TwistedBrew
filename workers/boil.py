#!/usr/bin python
from workers.brewworker import *
from schedules.boil import *


class BoilWorker(BrewWorker):
    def __init__(self, name):
        BrewWorker.__init__(self, name)

    def on_start(self):
        log.debug('Waiting for boil schedule. To exit press CTRL+C')

    def work(self, ch, method, properties, body):
        log.debug('Receiving boil schedule...')
        scde = BoilSchedule()
        scde.from_yaml(body)
        print(scde.name)
        for step in scde.steps:
            print(step)