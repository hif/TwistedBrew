#!/usr/bin python

import zmq
import core.utils.logging as log

CONNECTION_MASTER_QUEUE = "MasterQueue"
CONNECTION_BROADCAST_QUEUE = "BroadcastQueue"
CONNECTION_PUSH_QUEUE = "PushQueue"


class Connection():

    def __init__(self, ip, master_port, worker_port, queue, ignore_broadcasts):
        self.ip = ip
        self.master_port = master_port
        self.worker_port = worker_port
        self.queue = queue
        self.ignore_broadcasts = ignore_broadcasts
        if queue == CONNECTION_MASTER_QUEUE:
            self.master_context = zmq.Context()
            self.master_socket = self.master_context.socket(zmq.PUB)
            self.master_socket.bind("tcp://*:{0}".format(worker_port))

            self.worker_context = zmq.Context()
            self.worker_socket = self.worker_context.socket(zmq.PULL)
            self.worker_socket.bind("tcp://{0}:{1}".format(self.ip, self.master_port))
        else:
            self.master_context = zmq.Context()
            self.master_socket = self.master_context.socket(zmq.PUSH)
            self.master_socket.connect("tcp://{0}:{1}".format(self.ip, self.master_port))
            if queue == CONNECTION_PUSH_QUEUE:
                return
            self.worker_context = zmq.Context()
            self.worker_socket = self.worker_context.socket(zmq.SUB)
            self.worker_socket.connect("tcp://{0}:{1}".format(self.ip, worker_port))
            self.worker_socket.setsockopt_string(zmq.SUBSCRIBE, CONNECTION_BROADCAST_QUEUE)
            self.worker_socket.setsockopt_string(zmq.SUBSCRIBE, self.queue)

    def send(self, data, worker=""):
        try:
            if worker == "":
                self.master_socket.send_string(data)
            else:
                data = "{0}#{1}".format(worker, data)
                self.master_socket.send_string(data)
        except Exception as e:
                log.error('Error sending message {0} ({1})'.format(data, e))

    def broadcast(self, data):
        self.master_socket.send_string("{0}#{1}".format(CONNECTION_BROADCAST_QUEUE, data))

    def check(self):
        try:
            if self.queue == CONNECTION_MASTER_QUEUE:
                return self.worker_socket.recv_string()
            else:
                data = self.worker_socket.recv_string()
                pos = data.find("#")
                data = data[pos+1:]
                return data
        except Exception as e:
                log.error('Error receiving message ({0})'.format(e))


class MasterConnection(Connection):
    def __init__(self, ip, master_port, worker_port):
        Connection.__init__(self, ip, master_port, worker_port, CONNECTION_MASTER_QUEUE, True)


class WorkerConnection(Connection):
    def __init__(self, ip, master_port, worker_port, queue):
        Connection.__init__(self, ip, master_port, worker_port, queue, False)


class PushConnection(Connection):
    def __init__(self, ip, master_port):
        Connection.__init__(self, ip, master_port, 0, CONNECTION_PUSH_QUEUE, False)
