#!/usr/bin python
from config import brewconfig
from masters import brewmaster
import masters.defaults as defaults
import utils.logging as log
import HTMLParser
from web.twistedbrew.models import Brew

def load_device(config):
    try:
        module_name = config.device.lower()
        package = 'devices.' + module_name
        module = __import__(package)
        device_class = getattr(getattr(module, module_name), config.device)
        instance = device_class(config)
        return instance
    except Exception, e:
        log.error('Unable to load device from config: {0}'.format(e))
        return None

def load_worker(config):
    try:
        module_name = config.classname.lower()
        if not module_name.endswith('worker'):
            log.debug('Worker module {0} not found'.format(module_name), log.ERROR)
            return None
        module_name = module_name[:-6]
        package = 'workers.' + module_name
        module = __import__(package)
        worker_class = getattr(getattr(module, module_name), config.classname)
        instance = worker_class(config.name)
        instance.ip = config.ip
        instance.port = config.port
        for input in config.inputs:
            instance.inputs[input.name] = load_device(input)
        for output in config.outputs:
            instance.outputs[output.name] = load_device(output)
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
        for workerconfig in config.workers:
            workers.append(load_worker(workerconfig))

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
    brew.weblink = lookup_brewstyle_info(data, BREW_STYLE_WEB_NODE)
    return brew

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