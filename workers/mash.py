#!/usr/bin/env python
from workers.brewworker import *
from schedules.mash import *


class MashWorker(BrewWorker):
    def __init__(self, name):
        BrewWorker.__init__(self, name)

    def on_start(self):
        log.debug('Waiting for mash schedule. To exit press CTRL+C')

    def work(self, ch, method, properties, body):
        log.debug('Receiving mash schedule...')
        scde = MashSchedule()
        scde.from_yaml(body)
        print(scde.name)
        for step in scde.steps:
            print("Name: ", step.name)
            print("Temp: ", step.temp)
            print("Min : ", step.min)
