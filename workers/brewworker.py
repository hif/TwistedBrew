import threading

import pika

from masters.defaults import *
from masters.messages import *
import utils.logging as log


MessageFunctions = {MessageInfo: 'info', MessagePause: 'pause', MessageResume: 'resume', MessageReset: 'reset',
                    MessageStop: 'stop'}


def loadworker(config):
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
        return 'BrewWorker - [name:{0}, type:{1}, out:{2}, in:{3}]'. \
            format(self.name, str(self.__class__.__name__), len(self.outputs), len(self.inputs))

    def work(self, ch, method, properties, body):
        log.debug('Waiting for schedule. To exit press CTRL+C')

    def run(self):
        self.listen()

    def listen(self):
        self.onstart()
        self.channel.queue_bind(exchange=BroadcastExchange, queue=self.name)
        self.channel.basic_consume(self.receive, queue=self.name, no_ack=True)
        self.channel.start_consuming()

    def stop(self):
        self.onstop()
        self.channel.stop_consuming()

    def sendmaster(self, data):
        log.debug('Sending to master - ' + data)

        connection = pika.BlockingConnection(pika.ConnectionParameters(self.ip, self.port))
        channel = connection.channel()
        channel.queue_declare(queue=MasterQueue)

        channel.basic_publish(exchange='', routing_key=MasterQueue, body=data)
        connection.close()

    def receive(self, ch, method, properties, body):
        if MessageFunctions.__contains__(body) and hasattr(self, MessageFunctions[body]):
            command = MessageFunctions[body]
            getattr(self, command)()
            return
        self.work(ch, method, properties, body)

    def info(self):
        log.debug('{0} is sending info to master'.format(self.name))
        if self.oninfo():
            self.sendmaster(MessageInfo + MessageSplit + self.name + MessageSplit + self.__class__.__name__)
        else:
            self.reporterror('Info failed')

    def pause(self):
        log.debug('{0} is sending paused to master'.format(self.name))
        if self.onpause():
            self.sendmaster(MessagePaused + MessageSplit + self.name)
        else:
            self.reporterror('Pause failed')

    def resume(self):
        log.debug('{0} is sending resumed to master'.format(self.name))
        if self.onresume():
            self.sendmaster(MessageResumed + MessageSplit + self.name)
        else:
            self.reporterror('Resume failed')

    def reset(self):
        log.debug('{0} is sending ready to master'.format(self.name))
        if self.onreset():
            self.sendmaster(MessageReady + MessageSplit + self.name)
        else:
            self.reporterror('Reset failed')

    def reporterror(self, err):
        log.error('{0}: {1}'.format(self.name, err))

    def onstart(self):
        log.debug('Starting {0}'.format(self))

    def onstop(self):
        log.debug('Stopping {0}'.format(self))

    def oninfo(self):
        log.debug('Info {0}'.format(self))
        return True

    def onpause(self):
        log.debug('Pause {0}'.format(self))
        return True

    def onresume(self):
        log.debug('Resume {0}'.format(self))
        return True

    def onreset(self):
        log.debug('Reset {0}'.format(self))
        return True