import HTMLParser
from schedules.schedule import *


class FermentationStep:
    starttemp = 0.0
    endtemp = 0.0
    days = 0

    def __str__(self):
        return 'starttemp:{0} - endtemp:{1} - days:{2}'.format(self.starttemp, self.endtemp, self.days)


class FermentationSchedule(Schedule):
    def __init__(self):
        Schedule.__init__(self)
        self.steps.append(FermentationStep())  # Primary step
        self.steps.append(FermentationStep())  # Secondary step
        self.steps.append(FermentationStep())  # Tertiary step
        self.steps.append(FermentationStep())  # Age step

    def primaryStep(self):
        return self.steps[0]

    def secondaryStep(self):
        return self.steps[1]

    def tertiaryStep(self):
        return self.steps[2]

    def ageStep(self):
        return self.steps[3]

    def parse(self, recipe):
        html_parser = HTMLParser.HTMLParser()
        # Fermentation Schedule extracted
        self.name = html_parser.unescape(recipe.data["F_R_NAME"])
        self.primaryStep().starttemp = convert_f2c(recipe.children["F_R_AGE"].data["F_A_PRIM_TEMP"])
        self.primaryStep().endtemp = convert_f2c(recipe.children["F_R_AGE"].data["F_A_PRIM_END_TEMP"])
        self.primaryStep().days = recipe.children["F_R_AGE"].data["F_A_PRIM_DAYS"][:-8]
        self.secondaryStep().starttemp = convert_f2c(recipe.children["F_R_AGE"].data["F_A_SEC_TEMP"])
        self.secondaryStep().endtemp = convert_f2c(recipe.children["F_R_AGE"].data["F_A_SEC_END_TEMP"])
        self.secondaryStep().days = recipe.children["F_R_AGE"].data["F_A_SEC_DAYS"][:-8]
        self.tertiaryStep().starttemp = convert_f2c(recipe.children["F_R_AGE"].data["F_A_TERT_TEMP"])
        self.tertiaryStep().endtemp = convert_f2c(recipe.children["F_R_AGE"].data["F_A_TERT_END_TEMP"])
        self.tertiaryStep().days = recipe.children["F_R_AGE"].data["F_A_TERT_DAYS"][:-8]
        self.ageStep().starttemp = convert_f2c(recipe.children["F_R_AGE"].data["F_A_AGE_TEMP"])
        self.ageStep().endtemp = convert_f2c(recipe.children["F_R_AGE"].data["F_A_END_AGE_TEMP"])
        self.ageStep().days = recipe.children["F_R_AGE"].data["F_A_AGE"][:-8]
