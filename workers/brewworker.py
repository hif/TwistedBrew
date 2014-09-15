#!/usr/bin python
import threading
import time
import pika
from django.core import serializers
from datetime import datetime as dt
from datetime import timedelta as timedelta
from masters.defaults import *
from masters.messages import *
import utils.logging as log


DEBUG_WORK_MINUTES = 1

MessageFunctions = (MessageInfo,
                    MessagePause,
                    MessageResume,
                    MessageReset,
                    MessageStop)

POSTFIX = 'Worker'

class BrewWorker(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.working = False
        self.name = name
        self.simulation = False
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
        self.enabled = False
        self.active = False
        self.pausing_all_devices = False
        self.current_hold_time = timedelta(minutes=0)
        self.hold_timer = None
        self.hold_pause_timer = None
        self.pause_time = 0.0
        self.debug_timer = dt.now()
        self.session_detail_id = 0

    def __str__(self):
        return 'BrewWorker - [name:{0}, type:{1}, out:{2}, in:{3}]'. \
            format(self.name, str(self.__class__.__name__), len(self.output_config), len(self.input_config))

    @staticmethod
    def load_device(owner, config, simulation):
        try:
            module_name = config.device.lower()
            package = 'devices.' + module_name
            module = __import__(package)
            device_class = getattr(getattr(module, module_name), config.device)
            instance = device_class(owner, config, simulation)
            return instance
        except Exception, e:
            log.error('Unable to load device from config: {0}'.format(e))
            return None

    def create_device_threads(self):
        for i in self.input_config:
            device = self.load_device(self, i, self.simulation)
            if device is None:
                return False
            self.inputs[i.name] = device
        for o in self.output_config:
            device = self.load_device(self, o, self.simulation)
            if device is None:
                return False
            self.outputs[o.name] = device
        return True

    def start_all_devices(self):
        for i in self.inputs.itervalues():
            self.inputs[i.name] = i.start_device()
        for o in self.outputs.itervalues():
            self.outputs[o.name] = o.start_device()

    def is_any_device_enabled(self):
        for i in self.inputs.itervalues():
            if i.enabled:
                return True
        for o in self.outputs.itervalues():
            if o.enabled:
                return True
        return False

    def is_device_enabled(self, name):
        if len(self.inputs) != 0:
            if self.inputs[name].enabled:
                return True
        if len(self.outputs) != 0:
            if self.outputs[name].enabled:
                return True
        return False

    def pause_all_devices(self):
        if self.pausing_all_devices:
            return
        self.pausing_all_devices = True
        while self.is_any_device_enabled():
            log.debug('Trying to pause all passive devices...')
            for i in self.inputs.itervalues():
                i.pause_device()
            for o in self.outputs.itervalues():
                o.pause_device()
            time.sleep(1)
        log.debug('All passive devices paused')
        self.pausing_all_devices = False

    def resume_all_devices(self):
        while self.pausing_all_devices:
            time.sleep(1)
        log.debug('Resuming all passive devices...')
        for i in self.inputs.itervalues():
            i.resume_device()
        for o in self.outputs.itervalues():
            o.resume_device()
        log.debug('All passive devices resumed')
        self.pausing_all_devices = False

    def stop_all_devices(self):
        for i in self.inputs.itervalues():
            i.stop_device()
        for o in self.outputs.itervalues():
            o.stop_device()

    #def work(self, ch, method, properties, body):
    def work(self, data):
        pass

    def run(self):
        if not self.create_device_threads():
            log.error('Unable to load all devices, shutting down')
        self.listen()

    def listen(self):
        self.enabled = True
        self.on_start()
        self.channel.queue_bind(exchange=BroadcastExchange, queue=self.name)
        #self.channel.basic_consume(self.receive, queue=self.name, no_ack=True)
        #self.channel.start_consuming()
        while self.enabled:
            method, properties, body = self.channel.basic_get(queue=self.name, no_ack=True)
            if body is not None:
                self.receive(self.channel, method, properties, body)
            time.sleep(0.5)
        log.debug('Shutting down worker {0}'.format(self))

    def stop(self):
        self.stop_all_devices()
        self.on_stop()
        #self.channel.stop_consuming()
        self.enabled = False

    def send_to_master(self, data):
        #log.debug('Sending to master - ' + data)
        connection = pika.BlockingConnection(pika.ConnectionParameters(self.ip, self.port))
        channel = connection.channel()
        channel.queue_declare(queue=MasterQueue)

        channel.basic_publish(exchange='', routing_key=MasterQueue, body=data)
        connection.close()

    def send_measurement(self, device, data):
        message = MessageMeasurement + MessageSplit + self.name + MessageSplit + \
                  unicode(self.session_detail_id) + MessageSplit + device.name
        for item in data:
            message += "{0}{1}".format(MessageSplit, item)
        self.send_to_master(message)

    def receive(self, ch, method, properties, body):
        if body in MessageFunctions and hasattr(self, body):
            getattr(self, body)()
            return
        for work_data in serializers.deserialize("json", body):
            session_detail = work_data.object
            self.session_detail_id = session_detail.id
            self.work(session_detail)
            break   # only the first instance
        #self.work(ch, method, properties, body)

    def info(self):
        log.debug('{0} is sending info to master'.format(self.name))
        if self.on_info():
            self.send_to_master(MessageReady + MessageSplit + self.name + MessageSplit + self.__class__.__name__)
        else:
            self.report_error('Info failed')

    def pause(self):
        log.debug('{0} is sending paused to master'.format(self.name))
        if not self.on_pause():
            self.report_error('Pause failed')

    def resume(self):
        log.debug('{0} is sending resumed to master'.format(self.name))
        if not self.on_resume():
            self.report_error('Resume failed')

    def reset(self):
        log.debug('{0} is sending ready to master'.format(self.name))
        if self.on_reset():
            self.send_to_master(MessageReady + MessageSplit + self.name)
        else:
            self.report_error('Reset failed')

    def report_error(self, err):
        log.error('{0}: {1}'.format(self.name, err))

    def is_done(self):
        if self.hold_timer is None:
            return False
        pause_total = timedelta(seconds=self.pause_time)
        finish_time = dt.now() - self.hold_timer
        work_time = self.current_hold_time + pause_total
        if self.simulation:
            work_time = timedelta(minutes=DEBUG_WORK_MINUTES)
        if finish_time >= work_time:
            return True
        log.debug('Time untill work done: {0}'.format(work_time - finish_time))
        return False

    def done(self):
        try:
            self.pause_all_devices()
            self.session_detail_id = 0
            self.working = False
            self.info()
            return True
        except Exception, e:
            log.error('Error in cleaning up after work: {0}'.format(e.message))
            return False

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