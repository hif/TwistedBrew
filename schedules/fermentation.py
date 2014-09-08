#!/usr/bin python
import HTMLParser
from schedules.schedule import *


class FermentationStep:
    def __init__(self):
        pass

    start_temp = 0.0
    end_temp = 0.0
    days = 0

    def __str__(self):
        return 'starttemp:{0} - endtemp:{1} - days:{2}'.format(self.start_temp, self.end_temp, self.days)


class FermentationSchedule(Schedule):
    def __init__(self):
        Schedule.__init__(self)
        self.name = 'Ferment'
        self.type = 'Fermentation'
        self.steps.append(FermentationStep())  # Primary step
        self.steps.append(FermentationStep())  # Secondary step
        self.steps.append(FermentationStep())  # Tertiary step
        self.steps.append(FermentationStep())  # Age step

    def primarystep(self):
        return self.steps[0]

    def secondarystep(self):
        return self.steps[1]

    def tertiarystep(self):
        return self.steps[2]

    def agestep(self):
        return self.steps[3]

    def parse(self, recipe):
        html_parser = HTMLParser.HTMLParser()
        # Fermentation Schedule extracted
        self.name = html_parser.unescape(recipe.data["F_R_NAME"])
        self.primarystep().start_temp = convert_f2c(recipe.children["F_R_AGE"].data["F_A_PRIM_TEMP"])
        self.primarystep().end_temp = convert_f2c(recipe.children["F_R_AGE"].data["F_A_PRIM_END_TEMP"])
        self.primarystep().days = recipe.children["F_R_AGE"].data["F_A_PRIM_DAYS"][:-8]
        self.secondarystep().start_temp = convert_f2c(recipe.children["F_R_AGE"].data["F_A_SEC_TEMP"])
        self.secondarystep().end_temp = convert_f2c(recipe.children["F_R_AGE"].data["F_A_SEC_END_TEMP"])
        self.secondarystep().days = recipe.children["F_R_AGE"].data["F_A_SEC_DAYS"][:-8]
        self.tertiarystep().start_temp = convert_f2c(recipe.children["F_R_AGE"].data["F_A_TERT_TEMP"])
        self.tertiarystep().end_temp = convert_f2c(recipe.children["F_R_AGE"].data["F_A_TERT_END_TEMP"])
        self.tertiarystep().days = recipe.children["F_R_AGE"].data["F_A_TERT_DAYS"][:-8]
        self.agestep().start_temp = convert_f2c(recipe.children["F_R_AGE"].data["F_A_AGE_TEMP"])
        self.agestep().end_temp = convert_f2c(recipe.children["F_R_AGE"].data["F_A_END_AGE_TEMP"])
        self.agestep().days = recipe.children["F_R_AGE"].data["F_A_AGE"][:-8]
        return self
