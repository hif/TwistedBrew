#!/usr/bin python
from django.core import serializers
from workers.brewworker import *
import utils.logging as log
from brew_session.models import SessionDetail
from web.models import Worker, Command, Measurement
import datetime as dt
import time


class BrewMaster(threading.Thread):

    def __init__(self, config=None, configfile=None):
        threading.Thread.__init__(self)
        self.measurements_lock = threading.Lock()
        if config is None:
            self.name = MasterQueue
            self.ip = MessageServerIP
            self.port = MessageServerPort
        else:
            self.name = config.name
            self.ip = config.ip
            self.port = config.port

        self.instructions = {}
        self.broadcasts = {}
        self.messages = {}
        self.register_commands()

        self.workers = []

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.ip, self.port))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=MasterQueue)
        self.enabled = False

    def run(self):
        self.listen()

    def register_commands(self):
        Command.objects.all().delete()
        self.instructions = {
            MessageInfo: "Register worker info",
            MessageExecute: "Send message to worker",
            MessageUpdate: "Register measurement update",
            MessageShutdown: "Shutdown brew master",
        }
        self.store_commands(self.instructions, "Instruction")
        self.broadcasts = {
            "info": "Drop current workers and make all available workers register with master",
            "reset": "Reset all workers",
        }
        self.store_commands(self.broadcasts, "Broadcast")
        self.messages = {
            "reset": "Reset worker",
            "pause": "Pause worker",
            "resume": "Resume worker",
            "stop": "stop worker (shutdown)",
            "work": "Make worker start a session detail process",
        }
        self.store_commands(self.messages, "Message")

    def store_commands(self, commands, command_type):
        for name, description in commands.iteritems():
            tmp = Command()
            tmp.type = command_type
            tmp.name = name
            tmp.description = description
            tmp.save()

    def add_worker(self, worker, workertype):
        brew_workers = Worker.objects.filter(name=worker, type=workertype)
        if len(brew_workers) == 0:
            brew_worker = Worker()
            brew_worker.name = worker
            brew_worker.type = workertype
            self.workers.append(brew_worker.name)
        else:
            for brew_worker in brew_workers:
                break
        brew_worker.status = Worker.AVAILABLE
        brew_worker.save()

    def listen(self):
        log.debug('Waiting for worker updates. To exit press CTRL+C')
        self.enabled = True
        #self.channel.basic_consume(self.handle, queue=MasterQueue, no_ack=True)
        #self.channel.start_consuming()
        while self.enabled:
            method, properties, body = self.channel.basic_get(queue=MasterQueue, no_ack=True)
            if body is not None:
                self.handle(self.channel, method, properties, body)
            time.sleep(0.5)
        self.stop_all_workers()
        log.debug('Shutting down Brew master')

    def stop_all_workers(self):
        for worker in self.workers:
            self.send_command('stop', worker)

    def shutdown(self):
        #self.channel.stop_consuming()
        self.enabled = False

    def handle(self, ch, method, properties, body):
        #log.debug('Handling message')
        #log.debug(body)
        if str(body).startswith(MessageUpdate):
            self.handle_update(body)
            return
        if str(body).startswith(MessageInfo):
            self.handle_info(body)
            return
        if str(body).startswith(MessageWork):
            self.handle_work(body)
            return
        if str(body).startswith(MessageExecute):
            self.handle_execute(body)
            return
        if str(body).startswith(MessageShutdown):
            self.handle_shutdown()
            return
        log.debug('Ignorable reply from from worker: {0}'.format(body))

    def handle_info(self, body):
        data = str(body).split(MessageSplit)
        self.add_worker(data[1], data[2])

    def handle_work(self, body):
        data = str(body).split(MessageSplit)
        session_detail_id = data[1]
        worker_id = data[2]
        self.work(session_detail_id, worker_id)

    def handle_execute(self, body):
        data = str(body).split(MessageSplit)
        command = data[1]
        worker = ''
        if len(data) > 2:
            worker = data[2]
        self.send_command(command, worker)

    def handle_shutdown(self):
        self.shutdown()

    def handle_update(self, body):
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
                if len(data) > 6:   # In simulation mode, use fake timestamps
                    measurement.timestamp = dt.datetime.strptime(data[6], "%Y-%m-%d %H:%M:%S.%f")
                else:
                    measurement.timestamp = dt.datetime.now()
                measurement.save()
        except Exception, e:
            log.error('Brewmaster could not save measurement to database ({0})'.format(e.message))

    def verify_worker(self, worker):
        for available_worker in self.workers:
            if available_worker == worker:
                return True
        return False

    def send(self, worker, data):
        if not self.verify_worker(worker):
            log.warning('Worker {0} not available'.format(worker))
            return
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

    def reset_all(self):
        self.send_all(MessageReset)

    def reset(self, worker=None):
        if worker is None:
            self.reset_all()
        else:
            self.send(worker, MessageReset)

    def pause(self, worker):
        self.send(worker, MessagePause)

    def resume(self, worker):
        self.send(worker, MessageResume)

    def stop(self, worker):
        self.send(worker, MessageStop)

    def work(self, session_detail_id, worker_id):
        worker = Worker.objects.get(pk=worker_id)
        if worker is None or worker.status == Worker.BUSY:
            return False
        worker.status = Worker.BUSY
        worker.save()
        session_detail = SessionDetail.objects.all().filter(pk=session_detail_id)
        data = serializers.serialize("json", session_detail)
        self.send(worker.name, data)
        log.debug('Work detail sent to {0}'.format(worker.name))
        return True

    def send_command(self, command, worker):
        if not hasattr(self, command):
            log.error('No such command in BrewMaster ({0})'.format(command))
            return
        method = getattr(self, command)
        if worker is not None and worker != '' and command in self.messages.keys():
            method(worker)
        elif command in self.broadcasts.keys():
            method()
        else:
            log.debug('Master requested to send an unauthorized command: {0}'.format(command))
