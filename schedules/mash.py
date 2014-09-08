#!/usr/bin python
import HTMLParser
from schedules.schedule import *


class MashStep:
    def __init__(self):
        pass

    name = ''
    temp = 0.0
    min = 0

    def __str__(self):
        return 'name:{0} - temp:{1} - min:{2}'.format(self.name, self.temp, self.min)


class MashSchedule(Schedule):
    def __init__(self):
        Schedule.__init__(self)
        self.name = 'Mash'
        self.type = 'Mash'

    def parse(self, recipe):
        html_parser = HTMLParser.HTMLParser()
        # Mash Schedule extracted
        self.name = html_parser.unescape(recipe.data["F_R_NAME"])
        for mashItem in recipe.children["F_R_MASH"].children["steps"].subdata:
            if mashItem.name == "MashStep":
                mashstep = MashStep()
                mashstep.name = html_parser.unescape(mashItem.data["F_MS_NAME"])
                mashstep.temp = convert_f2c(mashItem.data["F_MS_STEP_TEMP"])
                mashstep.min = mashItem.data["F_MS_STEP_TIME"][:-8]
                self.steps.append(mashstep)
        return self
