#!/usr/bin python
import html
from brew.importing.brew_importer import BrewImporter
from brew.importing.beer_smith_parser import *
import core.utils.logging as log
from brew.models import Brew, BrewSection, BrewStep
from core.schedules.mash import MashSchedule
from core.schedules.boil import BoilSchedule
from core.schedules.fermentation import FermentationSchedule


class BeerSmithImporter(BrewImporter):
    def __init__(self):
        BrewImporter.__init__(self)
        self.display_name = 'Beer Smith Importer'
        self.recipe_file = ''
        self.counter = 0

    def do_import(self, uri):
        try:
            if uri is None:
                return 0
            self.recipe_file = uri
            log.debug('Loading recipe file {0}...'.format(self.recipe_file))
            beer = BeerParser()
            recipe_data = beer.get_recipes(self.recipe_file)
            self.counter = 0
            for item in recipe_data:
                name = lookup_brew_name(item).strip()
                if name is not None:
                    # Save to database
                    brew, sections = create_brew_model(item)
                    brew.save()
                    self.counter += 1
                    s_count = m_count = b_count = f_count = 0
                    for section in sections:
                        s_count += 1
                        s = create_section(section, brew, s_count)
                        s.save()
                        for step in section.steps:
                            brew_step = None
                            if s.worker_type == 'core.workers.mash.MashWorker':
                                m_count += 1
                                brew_step = create_mash_step(step, s, m_count)
                            elif s.worker_type == 'core.workers.boil.BoilWorker':
                                b_count += 1
                                brew_step = create_boil_step(step, s, b_count)
                            elif s.worker_type == 'core.workers.fermentation.FermentationWorker':
                                f_count += 1
                                brew_step = create_fermentation_step(step, s, f_count)
                            if brew_step is not None:
                                brew_step.save()
            log.debug('...done loading recipe file {0}'.format(self.recipe_file))
        except Exception as e:
            log.error('Failed to load recipes {0} ({1})'.format(self.recipe_file, e.args[0]))
        return self.counter


BREW_NAME_NODE = "F_R_NAME"
BREW_BREWER_NODE = "F_R_BREWER"
BREW_STYLE_NODE = "F_R_STYLE"
BREW_STYLE_NAME_NODE = "F_S_NAME"
BREW_STYLE_CATEGORY_NODE = "F_S_CATEGORY"
BREW_STYLE_DESCRIPTION_NODE = "F_S_DESCRIPTION"
BREW_STYLE_PROFILE_NODE = "F_S_PROFILE"
BREW_STYLE_INGREDIENTS_NODE = "F_S_INGREDIENTS"
BREW_STYLE_WEB_NODE = "F_S_WEB_LINK"


def create_brew_model(data):
    brew = Brew()
    brew.name = lookup_brew_name(data)
    brew.brewer = lookup_brew_info(data, BREW_BREWER_NODE)
    brew.style = lookup_brewstyle_info(data, BREW_STYLE_NAME_NODE)
    brew.category = lookup_brewstyle_info(data, BREW_STYLE_CATEGORY_NODE)
    brew.description = lookup_brewstyle_info(data, BREW_STYLE_DESCRIPTION_NODE)
    brew.profile = lookup_brewstyle_info(data, BREW_STYLE_PROFILE_NODE)
    brew.ingredients = lookup_brewstyle_info(data, BREW_STYLE_INGREDIENTS_NODE)
    brew.web_link = lookup_brewstyle_info(data, BREW_STYLE_WEB_NODE)
    mash = generate_brew_section(data, MashSchedule())
    boil = generate_brew_section(data, BoilSchedule())
    ferment = generate_brew_section(data, FermentationSchedule())
    sections = [mash, boil, ferment]
    return brew, sections


def generate_brew_section(data, section):
    return section.parse(data)


def create_section(schedule, brew, index):
    section = BrewSection()
    section.index = index
    section.brew = brew
    section.name = schedule.name
    section.worker_type = schedule.type
    return section


def create_mash_step(step, section, index):
    brew_step = BrewStep()
    brew_step.brew_section = section
    brew_step.index = index
    brew_step.name = step.name
    brew_step.unit = ''
    brew_step.target = step.temp
    brew_step.hold_time = step.min
    brew_step.unit = BrewStep.MINUTES
    return brew_step


def create_boil_step(step, section, index):
    brew_step = BrewStep()
    brew_step.brew_section = section
    brew_step.index = index
    brew_step.name = step.type
    brew_step.unit = step.unit
    brew_step.target = step.amount
    brew_step.hold_time = step.min
    brew_step.time_unit_seconds = BrewStep.MINUTES
    return brew_step


def create_fermentation_step(step, section, index):
    brew_step = BrewStep()
    brew_step.brew_section = section
    brew_step.index = index
    brew_step.name = section.name
    brew_step.unit = ''
    brew_step.target = step.start_temp
    brew_step.hold_time = step.days
    brew_step.time_unit_seconds = BrewStep.DAYS
    return brew_step


def lookup_brew_info(data, key):
    if data.data.__contains__(key):
        return html.unescape(data.data[key])
    return ""


def lookup_brew_name(data):
    return lookup_brew_info(data, BREW_NAME_NODE)


def lookup_brewstyle_info(data, key):
    if not data.children.__contains__(BREW_STYLE_NODE):
        return ""
    style = data.children[BREW_STYLE_NODE]
    if style.data.__contains__(key):
        return html.unescape(style.data[key])
    return ""