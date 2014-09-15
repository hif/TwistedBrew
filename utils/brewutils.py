#!/usr/bin python
import HTMLParser

from config import brewconfig
from masters import brewmaster
from workers import brewworker
import masters.defaults as defaults
import utils.logging as log
from brew.models import Brew, BrewSection, BrewStep
from schedules.mash import MashSchedule
from schedules.boil import BoilSchedule
from schedules.fermentation import FermentationSchedule


def load_device(owner, config, simulation):
    try:
        module_name = config.device.lower()
        package = 'devices.' + module_name
        module = __import__(package)
        device_class = getattr(getattr(module, module_name), config.device, simulation)
        instance = device_class(owner, config)
        return instance
    except Exception, e:
        log.error('Unable to load device from config: {0}'.format(e))
        return None


def load_worker(config):
    try:
        module_name = config.class_name.lower()
        if not module_name.endswith('worker'):
            log.error('Worker module {0} not found'.format(module_name))
            return None
        module_name = module_name[:-6]
        package = 'workers.' + module_name
        module = __import__(package)
        worker_class = getattr(getattr(module, module_name), config.class_name)
        instance = worker_class(config.name)
        instance.simulation = config.simulation
        instance.ip = config.ip
        instance.port = config.port
        instance.input_config = config.inputs
        instance.output_config = config.outputs
        return instance
    except Exception, e:
        log.error('Unable to load worker from config: {0}'.format(e))
        return None


def start_from_config(configfile=defaults.DEFAULT_CONFIG):
    try:
        config = brewconfig.BrewConfig(configfile)
        master = None
        if config.master is not None:
            master = brewmaster.BrewMaster(config.master)
        workers = []
        for worker_config in config.workers:
            workers.append(load_worker(worker_config))
        for worker in workers:
            worker.start()
        if master is not None:
            master.start()
        return master
    except Exception, e:
        log.error('Unable to start all from config: {0}'.format(e))
        return None

BREW_NAME_NODE = "F_R_NAME"
BREW_BREWER_NODE = "F_R_BREWER"
BREW_STYLE_NODE = "F_R_STYLE"
BREW_STYLE_NAME_NODE = "F_S_NAME"
BREW_STYLE_CATEGORY_NODE = "F_S_CATEGORY"
BREW_STYLE_DESCRIPTION_NODE = "F_S_DESCRIPTION"
BREW_STYLE_PROFILE_NODE = "F_S_PROFILE"
BREW_STYLE_INGREDIENTS_NODE = "F_S_INGREDIENTS"
BREW_STYLE_WEB_NODE = "F_S_WEB_LINK"

__brew_html_parser__ = HTMLParser.HTMLParser()


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
    section.name = schedule.type
    section.worker_type = schedule.worker_type()
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
        return __brew_html_parser__.unescape(data.data[key])
    return None


def lookup_brew_name(data):
    return lookup_brew_info(data, BREW_NAME_NODE)


def lookup_brewstyle_info(data, key):
    if not data.children.__contains__(BREW_STYLE_NODE):
        return None
    style = data.children[BREW_STYLE_NODE]
    if style.data.__contains__(key):
        return __brew_html_parser__.unescape(style.data[key])
    return None