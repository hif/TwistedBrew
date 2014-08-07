import sys
from utils import brewutils
import config.brewconfig as cfg

configfile = cfg.DEFAULT_CONFIG
if len(sys.argv) > 1:
    configfile = sys.argv[1]

print('Starting Twisted Brew (config:{0})'.format(configfile))

master = brewutils.startfromconfig(configfile)
if not master is None:
    master.info()