#!/usr/bin python
import yaml

from masters import defaults
import utils.logging as log


# Config file keys
CONFIG_MASTER = 'master'
CONFIG_WORKERS = 'workers'
CONFIG_WORKER = 'worker'
CONFIG_NAME = 'name'
CONFIG_IP = 'ip'
CONFIG_PORT = 'port'
CONFIG_CLASS = 'class'
CONFIG_DEVICE = 'device'
CONFIG_INPUTS = 'inputs'
CONFIG_INPUT = 'input'
CONFIG_OUTPUTS = 'outputs'
CONFIG_OUTPUT = 'output'
CONFIG_IO = 'io'


# Check if master or workers sections
def ismaster(node):
    return node == CONFIG_MASTER


def isworkers(node):
    return str(node).startswith(CONFIG_WORKERS)


def isworker(node):
    return str(node).startswith(CONFIG_WORKER)


class IOConfig():
    def __init__(self, name, device, io):
        self.name = name
        self.device = device
        self.io = io

    def __str__(self):
        return '{0} of type {1} using io {2}'.format(self.name, self.device, self.io)


class MasterConfig():
    def __init__(self):
        self.name = ''
        self.ip = ''
        self.port = 0
        self.verifydata()

    def set(self, name, ip=defaults.MessageServerIP, port=defaults.MessageServerPort):
        self.name = name
        self.ip = ip
        self.port = port

    def verifydata(self):
        if self.name is None:
            self.name = defaults.MasterQueue
        if self.ip is None:
            self.ip = defaults.MessageServerIP
        if self.port is None:
            self.port = defaults.MessageServerPort

    def setfromyaml(self, yamldata):
        self.name = yamldata[CONFIG_NAME]
        self.ip = yamldata[CONFIG_IP]
        self.port = yamldata[CONFIG_PORT]
        self.verifydata()

    def __str__(self):
        return 'Master({0}) - {1}:{2}\r\n'.format(self.name, self.ip, self.port)


class WorkerConfig(MasterConfig):
    def __init__(self):
        MasterConfig.__init__(self)
        self.classname = ''
        self.outputs = []
        self.inputs = []

    def __str__(self):
        tmp = 'Worker ({0} as {3}) - {1}:{2}\r\n'.format(self.name, self.ip, self.port, self.classname)
        for config in self.outputs.itervalues():
            tmp = tmp + '* Output: {0}\r\n'.format(config)
        for config in self.inputs.itervalues():
            tmp = tmp + '* Input: {0}\r\n'.format(config)
        return tmp

    def setfromyaml(self, yamldata):
        self.name = yamldata[CONFIG_NAME]
        self.ip = yamldata[CONFIG_IP]
        self.port = yamldata[CONFIG_PORT]
        self.verifydata()
        self.classname = yamldata[CONFIG_CLASS]
        for iooutput in yamldata[CONFIG_OUTPUTS]:
            iooutput = iooutput[CONFIG_OUTPUT]
            self.outputs.append(IOConfig(iooutput[CONFIG_NAME], iooutput[CONFIG_DEVICE], iooutput[CONFIG_IO]))
        for ioinput in yamldata[CONFIG_INPUTS]:
            ioinput = ioinput[CONFIG_INPUT]
            self.inputs.append(IOConfig(ioinput[CONFIG_NAME], ioinput[CONFIG_DEVICE], ioinput[CONFIG_IO]))


class BrewConfig():
    def __init__(self, configfile):
        self.master = None
        self.workers = []
        self.file = configfile
        self.readconfig()

    def __str__(self):
        tmp = ''
        if self.master is not None:
            tmp += str(self.master)
            tmp += '\r\n'
        for worker in self.workers:
            tmp += str(worker)
            tmp += '\r\n'
        return tmp

    def readconfig(self, configfile=''):
        if configfile == '':
            configfile = self.file
        raw = open(configfile, 'r')
        data = yaml.load(raw)
        masterfound = False
        for name, section in data.iteritems():
            if ismaster(name):
                if masterfound:
                    log.warning('More than one master found, discarding')
                else:
                    masterfound = True
                    self.master = MasterConfig()
                    self.master.setfromyaml(section)
            elif isworkers(name):
                for workernode in section:
                    worker = WorkerConfig()
                    worker.setfromyaml(workernode[CONFIG_WORKER])
                    self.workers.append(worker)
            else:
                log.warning('Unknown module found {0}!'.format(str(name)))

