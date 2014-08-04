import yaml

units = ["mg", "g", "oz", "lb", "kg", "ml", "tsp", "tbsp", "cup", "pt", "qt", "l", "gal", "items"]
use = ["boil", "mash", "primary", "secondary", "bottling"]


def convert_f2c(S):
    """(str): float

    Converts a Fahrenheit temperature represented as a string
    to a Celsius temperature.
    """
    fahrenheit = float(S)
    celsius = round((fahrenheit - 32) * 5 / 9, 1)
    return str(celsius)


def convert_o2g(S):
    """(str): float

    Converts a Ounces represented as a string
    to grams.
    """
    ounce = float(S)
    grams = round(ounce / 0.035274, 1)
    return str(grams)


class Schedule:
    def __init__(self):
        self.name = ''
        self.steps = []

    def __str__(self):
        str = self.name + "\r\n"
        for step in self.steps:
            str  = str + step

    def parse(self, recipe):
        pass

    def toYaml(self):
        l = list()
        l.append(self.name)
        for item in self.steps:
            l.append(item)
        return yaml.dump_all(l)

    def fromYaml(self, yamldata):
        l = yaml.load_all(yamldata)
        self.name = ""
        self.steps = list()
        index = 0
        for item in l:
            if (index == 0):
                self.name = item
            else:
                self.steps.append(item)
            index = index + 1
