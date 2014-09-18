#!/usr/bin python
from core.workers.baseworker import *
import core.utils.logging as log
from session.models import SessionDetail, Worker, Measurement
from twisted_brew.models import Command
import datetime as dt


class Master(threading.Thread):

    def __init__(self, communication_config=None, config=None, configfile=None):
        threading.Thread.__init__(self)
        self.measurements_lock = threading.Lock()
        if communication_config is None:
            self.ip = MessageServerIP
            self.port = MessageServerPort
            self.master_queue = MasterQueue
            self.broadcast_exchange = BroadcastExchange
        else:
            self.ip = communication_config.ip
            self.port = communication_config.port
            self.master_queue = communication_config.master_queue
            self.broadcast_exchange = communication_config.broadcast_exchange
        if config is None:
            self.name = MasterQueue
        else:
            self.name = config.name

        self.broadcasts = {}
        self.messages = {}
        self.instructions = {}
        self.instructions = {}
        self.register_commands()

        self.workers = {}

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.ip, self.port))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.master_queue)
        self.enabled = False

    def run(self):
        self.listen()

    def register_commands(self):
        Command.objects.all().delete()
        self.broadcasts = {
            MessageInfo: "Drop current workers and make all available workers register with master",
            MessageShutdown: "Shutdown brew master and workers",
        }
        self.store_commands(self.broadcasts, "Broadcast")
        self.messages = {
            MessageReset: "Reset worker",
            MessagePause: "Pause worker",
            MessageResume: "Resume worker",
        }
        self.store_commands(self.messages, "Message")
        self.instructions = {
            MessageWork: "Make worker start a session detail process",
        }
        self.store_commands(self.instructions, "Instruction")

    @staticmethod
    def store_commands(commands, command_type):
        for name, description in commands.iteritems():
            tmp = Command()
            tmp.name = name
            tmp.type = command_type
            tmp.description = description
            tmp.save()

    def add_worker(self, worker, worker_type):
        brew_workers = Worker.objects.filter(name=worker, type=worker_type)
        if len(brew_workers) == 0:
            brew_worker = Worker()
            brew_worker.name = worker
            brew_worker.type = worker_type
            brew_worker.status = Worker.AVAILABLE
            brew_worker.save()
            self.workers[brew_worker.id] = brew_worker.name
        else:
            for brew_worker in brew_workers:
                    break
            brew_worker.status = Worker.AVAILABLE
            brew_worker.save()

    def listen(self):
        log.debug('Waiting for worker updates. To exit press CTRL+C')
        self.enabled = True
        #self.channel.basic_consume(self.handle, queue=self.master_queue, no_ack=True)
        #self.channel.start_consuming()
        while self.enabled:
            method, properties, body = self.channel.basic_get(queue=self.master_queue, no_ack=True)
            if body is not None:
                self.handle(self.channel, method, properties, body)
            time.sleep(0.5)
        self.stop_all_workers()
        Worker.objects.all().delete()
        log.debug('Shutting down Brew master')

    def stop_all_workers(self):
        for worker in self.workers.keys():
            self.send(worker, 'stop')

    def handle(self, ch, method, properties, body):
        #log.debug('Handling message')
        #log.debug(body)
        if str(body).startswith(MessageReady):
            self.handle_ready(body)
            return
        if str(body).startswith(MessageMeasurement):
            self.handle_measurement(body)
            return
        self.process_command(body)

    def handle_ready(self, body):
        data = str(body).split(MessageSplit)
        self.add_worker(data[1], data[2])

    def handle_measurement(self, body):
        #log.debug('Receiving worker update...')
        try:
            with self.measurements_lock:
                data = body.split(MessageSplit)
                measurement = Measurement()
                measurement.worker = data[1]
                session_detail_id = int(data[2])
                session_detail = SessionDetail.objects.get(pk=session_detail_id)
                measurement.session_detail = session_detail
                measurement.device = data[3]
                measurement.value = data[4]
                measurement.set_point = data[5]
                measurement.work = ''   # TODO
                measurement.remaining = ''  # TODO
                if len(data) > 6:   # In simulation mode, use fake timestamps
                    measurement.timestamp = dt.datetime.strptime(data[6], "%Y-%m-%d %H:%M:%S.%f")
                else:
                    measurement.timestamp = dt.datetime.now()
                measurement.save()
        except Exception, e:
            log.error('Brewmaster could not save measurement to database ({0})'.format(e.message))

    def lookup_worker(self, worker_id):
        if int(worker_id) in self.workers.keys():
            return self.workers[int(worker_id)]
        return None

    def send(self, worker_id, data):
        worker = self.lookup_worker(worker_id)
        if worker is None:
            log.warning('Worker {0} not available'.format(worker))
            return
        log.debug('Sending:{0} to {1}'.format(data, worker))
        connection = pika.BlockingConnection(pika.ConnectionParameters(self.ip, self.port))
        channel = connection.channel()
        channel.queue_declare(queue=worker)

        channel.basic_publish(exchange='', routing_key=worker, body=data)
        connection.close()

    def send_all(self, data):
        log.debug('Sending:{0}'.format(data))
        connection = pika.BlockingConnection(pika.ConnectionParameters(self.ip, self.port))
        channel = connection.channel()
        channel.exchange_declare(exchange=BroadcastExchange, type='fanout')

        channel.basic_publish(exchange=BroadcastExchange, routing_key='', body=data)
        connection.close()

    def info(self):
        Worker.objects.all().delete()
        self.send_all(MessageInfo)

    def reset(self, worker_id):
        self.send(worker_id, MessageReset)

    def pause(self, worker_id):
        status = Worker.get_worker_status(worker_id)
        if status != Worker.BUSY:
            return
        Worker.set_worker_status(worker_id, Worker.PAUSED)
        self.send(worker_id, MessagePause)

    def resume(self, worker_id):
        status = Worker.get_worker_status(worker_id)
        if status != Worker.PAUSED:
            return
        Worker.set_worker_status(worker_id, Worker.BUSY)
        self.send(worker_id, MessageResume)

    def work(self, worker_id, session_detail_id):
        status = Worker.get_worker_status(worker_id)
        if status != Worker.AVAILABLE:
            return
        Worker.set_worker_status(worker_id, Worker.BUSY)
        session_detail = SessionDetail.objects.all().filter(pk=int(session_detail_id))
        data = serializers.serialize("json", session_detail)
        self.send(worker_id, data)
        log.debug('Work detail sent to {0}'.format(self.workers[int(worker_id)]))
        return True

    def shutdown(self):
        #self.channel.stop_consuming()
        self.enabled = False

    def process_command(self, body):
        data = body.split(MessageSplit)
        command = data[0]
        if len(data) > 1:
            worker_id = data[1]
        else:
            worker_id = None
        if len(data) > 2:
            instruction = data[2]
        else:
            instruction = None
        if not hasattr(self, command):
            log.error('No such command in Master ({0})'.format(command))
            return
        method = getattr(self, command)
        if command in self.broadcasts.keys():
            method()
        elif command in self.messages.keys():
            method(worker_id)
        elif command in self.instructions.keys():
            method(worker_id, instruction)
        else:
            log.debug('Master requested to send an unauthorized command: {0}'.format(command))

    @staticmethod
    def send_master(command, params=None, ip = None, port=None):
        if ip is None:
            ip = MessageServerIP
        if port is None:
            port = MessageServerPort
        data = command
        if not params is None:
            data += (MessageSplit + params)
        log.debug(u'Commanding master - {0}'.format(data))

        connection = pika.BlockingConnection(pika.ConnectionParameters(ip, port))
        channel = connection.channel()
        channel.queue_declare(queue=MasterQueue)

        channel.basic_publish(exchange='', routing_key=MasterQueue, body=data)
        connection.close()

    @staticmethod
    def start_work(worker_id, session_detail_id, ip = None, port=None):
        if ip is None:
            ip = MessageServerIP
        if port is None:
            port = MessageServerPort
        body = MessageWork + MessageSplit + worker_id + MessageSplit + session_detail_id

        log.debug(u'Commanding master - {0}'.format(body))

        connection = pika.BlockingConnection(pika.ConnectionParameters(ip, port))
        channel = connection.channel()
        channel.queue_declare(queue=MasterQueue)

        channel.basic_publish(exchange='', routing_key=MasterQueue, body=body)
        connection.close()