#!/usr/bin python
from workers.brewworker import *
from schedules.fermentation import *


class FermentationWorker(BrewWorker):
    def __init__(self, name):
        BrewWorker.__init__(self, name)

    def on_start(self):
        log.debug('Waiting for fermentation schedule. To exit press CTRL+C')

    def work(self, ch, method, properties, body):
        log.debug('Receiving fermentation schedule...')
        self.schedule = FermentationSchedule()
        self.schedule.from_yaml(body)
        print(self.schedule.name)
        for step in self.schedule.steps:
            print(step)