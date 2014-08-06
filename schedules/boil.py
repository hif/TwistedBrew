import HTMLParser
from recipes import *
from schedules.schedule import *

Hop = 0
Misc = 1
HopUnit = "Grams"


class BoilStep:
    name = ""
    type = Hop
    unit = HopUnit
    amount = 0.0
    min = 0

    def __str__(self):
        return 'name:{0} - type:{1} - unit:{2} - amount:{3} - min:{4}'.format(self.name, self.type, self.unit, self.amount, self.min)


class BoilSchedule(Schedule):
    def __init__(self):
        Schedule.__init__(self)

    def parse(self, recipe):
        html_parser = HTMLParser.HTMLParser()
        # Boil Schedule extracted
        self.name = html_parser.unescape(recipe.data["F_R_NAME"])
        # Hops
        for ingredient in recipe.children["Ingredients"].subdata:
            if (ingredient.name == "Hops" and int(ingredient.data["F_H_DRY_HOP_TIME"][-9]) == 0):
                boilstep = BoilStep()
                boilstep.name = html_parser.unescape(ingredient.data["F_H_NAME"])
                boilstep.type = Hop
                boilstep.unit = HopUnit
                boilstep.amount = convert_o2g(ingredient.data["F_H_AMOUNT"])
                boilstep.min = ingredient.data["F_H_BOIL_TIME"][:-8]
                self.steps.append(boilstep)
        # Misc ingredients
        for ingredient in recipe.children["Ingredients"].subdata:
            if (ingredient.name == "Misc"):
                boilstep = BoilStep()
                boilstep.name = html_parser.unescape(ingredient.data["F_M_NAME"])
                boilstep.type = Misc
                boilstep.unit = units[int(ingredient.data["F_M_UNITS"])]
                boilstep.amount = ingredient.data["F_M_AMOUNT"]
                boilstep.min = ingredient.data["F_M_TIME"][:-8]
                self.steps.append(boilstep)
