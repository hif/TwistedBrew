#!/usr/bin python
import threading

import pika

from masters.defaults import *
from masters.messages import *
import utils.logging as log


MessageFunctions = {MessageInfo: 'info', MessagePause: 'pause', MessageResume: 'resume', MessageReset: 'reset',
                    MessageStop: 'stop'}


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
        self.input_config = None
        self.output_config = None
        self.outputs = {}
        self.inputs = {}
        self.schedule = None
        self.step = -1

    def __str__(self):
        return 'BrewWorker - [name:{0}, type:{1}, out:{2}, in:{3}]'. \
            format(self.name, str(self.__class__.__name__), len(self.outputs), len(self.inputs))

    def load_device(self, config):
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

    def create_device_threads(self):
        for i in self.input_config:
            self.inputs[i.name] = self.load_device(i)
        for o in self.output_config:
            self.outputs[o.name] = self.load_device(o)

    def work(self, ch, method, properties, body):
        log.debug('Waiting for schedule. To exit press CTRL+C')

    def run(self):
        self.listen()

    def listen(self):
        self.on_start()
        self.channel.queue_bind(exchange=BroadcastExchange, queue=self.name)
        self.channel.basic_consume(self.receive, queue=self.name, no_ack=True)
        self.channel.start_consuming()

    def stop(self):
        self.on_stop()
        self.channel.stop_consuming()

    def send_to_master(self, data):
        log.debug('Sending to master - ' + data)

        connection = pika.BlockingConnection(pika.ConnectionParameters(self.ip, self.port))
        channel = connection.channel()
        channel.queue_declare(queue=MasterQueue)

        channel.basic_publish(exchange='', routing_key=MasterQueue, body=data)
        connection.close()

    def send_update(self, data):
        message = MessageUpdate + MessageSplit + self.name
        for item in data:
            message += "{0}{1}".format(MessageSplit, item)
        self.send_to_master(message)

    def receive(self, ch, method, properties, body):
        if MessageFunctions.__contains__(body) and hasattr(self, MessageFunctions[body]):
            command = MessageFunctions[body]
            getattr(self, command)()
            return
        self.work(ch, method, properties, body)

    def info(self):
        log.debug('{0} is sending info to master'.format(self.name))
        if self.on_info():
            self.send_to_master(MessageInfo + MessageSplit + self.name + MessageSplit + self.__class__.__name__)
        else:
            self.report_error('Info failed')

    def pause(self):
        log.debug('{0} is sending paused to master'.format(self.name))
        if self.on_pause():
            self.send_to_master(MessagePaused + MessageSplit + self.name)
        else:
            self.report_error('Pause failed')

    def resume(self):
        log.debug('{0} is sending resumed to master'.format(self.name))
        if self.on_resume():
            self.send_to_master(MessageResumed + MessageSplit + self.name)
        else:
            self.report_error('Resume failed')

    def reset(self):
        self.step = -1
        log.debug('{0} is sending ready to master'.format(self.name))
        if self.on_reset():
            self.send_to_master(MessageReady + MessageSplit + self.name)
        else:
            self.report_error('Reset failed')

    def report_error(self, err):
        log.error('{0}: {1}'.format(self.name, err))

    def on_start(self):
        log.debug('Starting {0}'.format(self))

    def on_stop(self):
        log.debug('Stopping {0}'.format(self))

    def on_info(self):
        log.debug('Info {0}'.format(self))
        return True

    def on_pause(self):
        log.debug('Pause {0}'.format(self))
        return True

    def on_resume(self):
        log.debug('Resume {0}'.format(self))
        return True

    def on_reset(self):
        log.debug('Reset {0}'.format(self))
        return True