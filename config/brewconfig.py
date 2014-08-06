import yaml
import io
from masters import defaults

# The default config file name
DEFAULT_CONFIG = 'twisted_brew.yml'

# Config file keys
CONFIG_MASTER = 'master'
CONFIG_WORKERS = 'workers'
CONFIG_WORKER = 'worker'
CONFIG_NAME = 'name'
CONFIG_IP = 'ip'
CONFIG_PORT = 'port'
CONFIG_CLASS = 'class'
CONFIG_TYPE = 'type'
CONFIG_INPUTS = 'inputs'
CONFIG_INPUT = 'input'
CONFIG_OUTPUTS = 'outputs'
CONFIG_OUTPUT = 'output'
CONFIG_IO = 'io'

# Check if master or workers sections
def isMaster(node):
    return node == CONFIG_MASTER
def isWorkers(node):
    return str(node).startswith(CONFIG_WORKERS)
def isWorker(node):
    return str(node).startswith(CONFIG_WORKER)


class IOConfig():
    def __init__(self, name, type, io):
        self.name = name
        self.type = type
        self.io = io

    def __str__(self):
        return '{0} of type {1} using io {2}'.format(self.name, self.type, self.io)

class MasterConfig():
    def __init__(self):
        self.name = ""
        self.ip = ""
        self.port = 0
        self.verifyData()

    def set(self, name, ip=defaults.MessageServerIP, port=defaults.MessageServerPort):
        self.name = name
        self.ip = ip
        self.port = port

    def verifyData(self):
        if(self.name == None):
            self.name = defaults.MasterQueue
        if(self.ip == None):
            self.ip = defaults.MessageServerIP
        if(self.port == None):
            self.port = defaults.MessageServerPort

    def setFromYaml(self, yamldata):
        self.name = yamldata[CONFIG_NAME]
        self.ip = yamldata[CONFIG_IP]
        self.port = yamldata[CONFIG_PORT]
        self.verifyData()

    def __str__(self):
        return 'Master({0}) - {1}:{2}\r\n'.format(self.name, self.ip, self.port)

class WorkerConfig(MasterConfig):
    def __init__(self):
        MasterConfig.__init__(self)
        self.classname = ''
        self.outputs = {}
        self.inputs = {}

    def __str__(self):
        tmp = 'Worker ({0} as {3}) - {1}:{2}\r\n'.format(self.name, self.ip, self.port, self.classname)
        for config in self.outputs.itervalues():
            tmp = tmp + '* Output: {0}\r\n'.format(config)
        for config in self.inputs.itervalues():
            tmp = tmp + '* Input: {0}\r\n'.format(config)
        return tmp

    def setFromYaml(self, yamldata):
        self.name = yamldata[CONFIG_NAME]
        self.ip = yamldata[CONFIG_IP]
        self.port = yamldata[CONFIG_PORT]
        self.verifyData()
        self.classname = yamldata[CONFIG_CLASS]
        for output in yamldata[CONFIG_OUTPUTS]:
            output = output[CONFIG_OUTPUT]
            self.outputs[output[CONFIG_NAME]] = IOConfig(output[CONFIG_NAME], output[CONFIG_TYPE], output[CONFIG_IO])
        for input in yamldata[CONFIG_INPUTS]:
            input = input[CONFIG_INPUT]
            self.inputs[input[CONFIG_NAME]] = IOConfig(input[CONFIG_NAME], input[CONFIG_TYPE], input[CONFIG_IO])

class BrewConfig():
    def __init__(self, file = DEFAULT_CONFIG):
        self.master = None
        self.workers = []
        self.file = file
        self.readConfig()

    def __str__(self):
        tmp = ""
        if(not self.master == None):
            tmp = tmp + str(self.master)
            tmp = tmp + "\r\n"
        for worker in self.workers:
            tmp = tmp + str(worker)
            tmp = tmp + "\r\n"
        return tmp

    def readConfig(self, file = ''):
        if(file == ''):
            file = self.file
        raw = open(file, 'r')
        data = yaml.load(raw)
        masterfound = False
        for name, section in data.iteritems():
            if(isMaster(name)):
                #print(section)
                if(masterfound == True):
                    print("Warning, more than one master found, discarding")
                else:
                    masterfound = True
                    self.master = MasterConfig()
                    self.master.setFromYaml(section)
            elif(isWorkers(name)):
                for workernode in section:
                    #print(workernode[CONFIG_WORKER])
                    worker = WorkerConfig()
                    worker.setFromYaml(workernode[CONFIG_WORKER])
                    self.workers.append(worker)
            else:
                print ("Warning, unknown module found {0}!".format(str(name)))


#cfg = BrewConfig()
#cfg = BrewConfig("mash_config.yml")
#cfg.readConfig()

#print(cfg)
