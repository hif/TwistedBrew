#!/usr/bin python
from core.workers.baseworker import *
import core.utils.logging as log
from session.models import SessionDetail, Worker, Measurement
from twisted_brew.models import Command
from django.utils import timezone as dt
from core.comm.connection import MasterConnection, CONNECTION_MASTER_QUEUE, PushConnection
from django.conf import settings

class Master(threading.Thread):

    def __init__(self, communication_config=None, config=None, configfile=None):
        threading.Thread.__init__(self)
        self.measurements_lock = threading.Lock()
        if communication_config is None:
            self.ip = settings.MASTER_IP  # MessageServerIP
            self.master_port = settings.MASTER_PORT  # MessageServerMasterPort
            self.worker_port = settings.WORKER_PORT  # MessageServerWorkerPort
        else:
            self.ip = communication_config.ip
            self.master_port = communication_config.master_port
            self.worker_port = communication_config.worker_port
        self.name = CONNECTION_MASTER_QUEUE

        self.broadcasts = {}
        self.messages = {}
        self.instructions = {}
        self.instructions = {}
        self.register_commands()

        self.workers = {}

        self.connection = MasterConnection(self.ip, self.master_port, self.worker_port)
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
        for name, description in commands.items():
            tmp = Command()
            tmp.name = name
            tmp.type = command_type
            tmp.description = description
            tmp.save()

    def add_worker(self, worker, worker_type, devices):
        added_worker = Worker.enlist_worker(worker, worker_type, devices)
        if added_worker.id not in self.workers.keys():
            self.workers[added_worker.id] = added_worker.name

    def listen(self):
        Worker.force_workers_off_line()
        log.debug('Waiting for worker updates. To exit press CTRL+C')
        self.enabled = True
        while self.enabled:
            data = self.connection.check()
            if data is not None:
                self.handle(data)
            time.sleep(0)
        self.stop_all_workers()
        Worker.force_workers_off_line()
        #Worker.objects.all().delete()
        log.debug('Shutting down Brew master')

    def stop_all_workers(self):
        for worker in self.workers.keys():
            self.send(worker, 'stop')

    def handle(self, data):
        #log.debug('Handling message')
        #log.debug(data)
        if str(data).startswith(MessageReady):
            self.handle_ready(data)
            return
        if str(data).startswith(MessageDone):
            self.handle_done(data)
            return
        if str(data).startswith(MessageMeasurement):
            self.handle_measurement(data)
            return
        if str(data).startswith(MessagePing):
            self.handle_ping()
            return
        self.process_command(data)

    def handle_ready(self, body):
        data = str(body).split(MessageSplit)
        log.debug("Ready reply from {0} - {1}".format(data[1], data[2]))
        devices = list()
        for device in range(3, len(data)):
            devices.append(data[device])
        self.add_worker(data[1], data[2], devices)

    def handle_done(self, body):
        data = str(body).split(MessageSplit)
        worker_name = data[1]
        session_detail_id = int(data[2])
        session_detail = SessionDetail.objects.get(pk=session_detail_id)
        session_detail.end_work()
        done_measurement = Measurement()
        done_measurement.timestamp = dt.now()
        done_measurement.worker_name = worker_name
        done_measurement.session_detail_id = session_detail_id
        done_measurement.value = 0
        done_measurement.set_point = 0
        done_measurement.work = "Done"
        done_measurement.remaining = "0";
        done_measurement.save()

    def handle_measurement(self, worker_measurement_data):
        #log.debug('Receiving worker measurement...')
        try:
            with self.measurements_lock:
                worker_measurement = WorkerMeasurement.deserialize_message(worker_measurement_data)
                measurement = Measurement()
                measurement.worker = worker_measurement.worker_name
                session_detail_id = worker_measurement.session_detail_id
                session_detail = SessionDetail.objects.get(pk=session_detail_id)
                measurement.session_detail = session_detail
                measurement.device = worker_measurement.device_name
                measurement.value = worker_measurement.value
                measurement.set_point = worker_measurement.set_point
                measurement.work = worker_measurement.work
                measurement.remaining = worker_measurement.remaining
                if not worker_measurement.debug_timer is None:   # In simulation mode, use fake timestamps
                    #measurement.timestamp = datetime.strptime(worker_measurement.debug_timer, "%Y-%m-%d %H:%M:%S.%f")
                    #measurement.timestamp = dt.get_current_timezone.localize(measurement.timestamp)
                    measurement.timestamp = worker_measurement.debug_timer
                else:
                    measurement.timestamp = dt.now()
                measurement.save()
        except Exception as e:
            log.error('Master could not save measurement to database ({0})'.format(e.args[0]))

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
        self.connection.send(data, worker)

    def send_all(self, data):
        log.debug('Sending:{0}'.format(data))
        self.connection.broadcast(data)

    def info(self):
        Worker.take_workers_off_line()
        #Worker.objects.all().delete()
        self.send_all(MessageInfo)

    def reset(self, worker_id):
        reset_worker = Worker.objects.get(pk=int(worker_id))
        if not reset_worker.working_on is None:
            reset_worker.working_on.end_work(True)
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
        session_detail_set = SessionDetail.objects.filter(pk=int(session_detail_id))
        if len(session_detail_set) == 0:
            return
        session_detail = session_detail_set[0]
        session_detail.begin_work(worker_id)
        data = serializers.serialize("json", session_detail_set)
        self.send(worker_id, data)
        try:
            log.debug('Work detail sent to {0}'.format(self.workers[int(worker_id)]))
        except Exception as e:
            log.debug('Work detail not sent: {0}'.format(e.args[0]))
        return True

    def shutdown(self):
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

    def handle_ping(self):
        log.info(MessagePong)


    @staticmethod
    def send_ping(ip=None, port=None):
        if ip is None:
            ip = settings.MASTER_IP  # MessageServerIP
        if port is None:
            port = settings.MASTER_PORT  # MessageServerMasterPort
        data = MessagePing
        log.debug('Commanding master - {0}'.format(data))

        mq = PushConnection(ip, port)
        mq.send(data)


    @staticmethod
    def send_master(command, params=None, ip=None, port=None):
        if ip is None:
            ip = settings.MASTER_IP  # MessageServerIP
        if port is None:
            port = settings.MASTER_PORT  # MessageServerMasterPort
        data = command
        if params is not None:
            data += (MessageSplit + params)
        log.debug('Commanding master - {0}'.format(data))

        mq = PushConnection(ip, port)
        mq.send(data)

    @staticmethod
    def start_work(worker_id, session_detail_id, ip=None, port=None):
        if ip is None:
            ip = settings.MASTER_IP  # MessageServerIP
        if port is None:
            port = settings.MASTER_PORT  # MessageServerMasterPort
        data = MessageWork + MessageSplit + worker_id + MessageSplit + session_detail_id

        log.debug('Commanding master - {0}'.format(data))

        mq = PushConnection(ip, port)
        mq.send(data)