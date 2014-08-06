import threading

import pika

from masters.defaults import *
from masters.messages import *
import utils.logging as log


MessageFunctions = {MessageInfo:'info', MessagePause:'pause', MessageResume:'resume', MessageReset:'reset', MessageStop:'stop'}

def loadWorker(config):
    modulename = config.classname.lower()
    if(not modulename.endswith('worker')):
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

class BrewWorker(threading.Thread):

    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
        self.ip = MessageServerIP
        self.port = MessageServerPort
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.ip, self.port))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=BroadcastExchange, type='fanout')
        self.channel.queue_declare(queue=self.name)
        self.outputs = {}
        self.inputs = {}

    def __str__(self):
        return 'BrewWorker - [name:{0}, type:{1}, out:{2}, in:{3}]'.\
            format(self.name, str(self.__class__.__name__), len(self.outputs), len(self.inputs))

    def work(self, ch, method, properties, body):
        log.debug('Waiting for schedule. To exit press CTRL+C')

    def run(self):
        self.listen()

    def listen(self):
        self.onStart()
        self.channel.queue_bind(exchange=BroadcastExchange, queue=self.name)
        self.channel.basic_consume(self.receive, queue=self.name, no_ack=True)
        self.channel.start_consuming()

    def stop(self):
        self.onStop()
        self.channel.stop_consuming()

    def sendMaster(self, data):
        log.debug('Sending to master - ' + data)

        connection = pika.BlockingConnection(pika.ConnectionParameters(self.ip, self.port))
        channel = connection.channel()
        channel.queue_declare(queue=MasterQueue)

        channel.basic_publish(exchange='', routing_key=MasterQueue, body=data)
        connection.close()

    def receive(self, ch, method, properties, body):
        if(MessageFunctions.__contains__(body) and hasattr(self, MessageFunctions[body])):
            command = MessageFunctions[body]
            getattr(self,command)()
            return
        self.work(ch, method, properties, body)

    def work(self, ch, method, properties, body):
        log.debug('Receiving data...')
        log.debug(body)

    def info(self):
        log.debug('{0} is sending info to master'.format(self.name))
        if(self.onInfo()):
            self.sendMaster(MessageInfo + MessageSplit + self.name + MessageSplit + self.__class__.__name__)
        else:
            self.reportError('Info failed')

    def pause(self):
        log.debug('{0} is sending paused to master'.format(self.name))
        if(self.onPause()):
            self.sendMaster(MessagePaused + ':' + self.name)
        else:
            self.reportError('Pause failed')
    def resume(self):
        log.debug('{0} is sending resumed to master'.format(self.name))
        if(self.onResume()):
            self.sendMaster(MessageResumed + ':' + self.name)
        else:
            self.reportError('Resume failed')

    def reset(self):
        log.debug('{0} is sending ready to master'.format(self.name))
        if(self.onReset()):
            self.sendMaster(MessageReady + ':' + self.name)
        else:
            self.reportError('Reset failed')

    def reportError(self, err):
        log.error(err)

    def onStart(self):
        pass

    def onStop(self):
        log.debug('Stopping {0}'.format(self))

    def onInfo(self):
        return True

    def onPause(self):
        return True

    def onResume(self):
        return True

    def onReset(self):
        return True