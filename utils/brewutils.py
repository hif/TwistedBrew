from config import brewconfig
from masters import brewmaster
from workers import brewworker
import masters.defaults as defaults
import utils.logging as log
import HTMLParser
from web.twistedbrew.models import Brew


def loadworker(config):
    try:
        modulename = config.classname.lower()
        if not modulename.endswith('worker'):
            log.debug('Worker module {0} not found'.format(modulename), log.ERROR)
            return None
        modulename = modulename[:-6]
        package = 'workers.' + modulename
        module = __import__(package)
        workerclass = getattr(getattr(module, modulename), config.classname)
        instance = workerclass(config.name)
        instance.ip = config.ip
        instance.port = config.port
        instance.inputs = config.inputs
        instance.outputs = config.outputs
        return instance
    except Exception, e:
        log.error('Unable to load worker from config: {0}'.format(e))
        return None

def startfromconfig(configfile=defaults.DEFAULT_CONFIG):
    try:
        config = brewconfig.BrewConfig(configfile)
        master = None
        if config.master is not None:
            master = brewmaster.BrewMaster(config.master)
        workers = []
        for workerconfig in config.workers:
            workers.append(loadworker(workerconfig))

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

def modelbrew(data):
    brew = Brew()
    brew.name = recipename(data)
    brew.brewer = lookupinfo(data, BREW_BREWER_NODE)
    brew.style = lookupstyleinfo(data, BREW_STYLE_NAME_NODE)
    brew.category = lookupstyleinfo(data, BREW_STYLE_CATEGORY_NODE)
    brew.description = lookupstyleinfo(data, BREW_STYLE_DESCRIPTION_NODE)
    brew.profile = lookupstyleinfo(data, BREW_STYLE_PROFILE_NODE)
    brew.ingredients = lookupstyleinfo(data, BREW_STYLE_INGREDIENTS_NODE)
    brew.weblink = lookupstyleinfo(data, BREW_STYLE_WEB_NODE)
    return brew

def lookupinfo(data, key):
    if data.data.__contains__(key):
        return __brew_html_parser__.unescape(data.data[key])
    return None


def recipename(data):
    return lookupinfo(data, BREW_NAME_NODE)


def lookupstyleinfo(data, key):
    if not data.children.__contains__(BREW_STYLE_NODE):
        return None
    style = data.children[BREW_STYLE_NODE]
    if style.data.__contains__(key):
        return __brew_html_parser__.unescape(style.data[key])
    return None