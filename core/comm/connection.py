#!/usr/bin python

import zmq
from core.defaults import MasterQueue
import core.utils.logging as log

SUB_PORT = 5999


class Connection():

    def __init__(self, ip, port, queue, broadcast_queue, ignore_broadcasts=False):
        self.ip = ip
        self.port = port
        self.queue = queue
        self.broadcast_queue = broadcast_queue
        self.ignore_broadcasts = ignore_broadcasts
        if queue == "Web":
            self.master_context = zmq.Context()
            self.master_socket = self.master_context.socket(zmq.PUSH)
            self.master_socket.connect("tcp://127.0.0.1:%s" % self.port)
        elif queue == MasterQueue:
            self.master_context = zmq.Context()
            self.master_socket = self.master_context.socket(zmq.PUB)
            self.master_socket.bind("tcp://*:%s" % SUB_PORT)

            self.worker_context = zmq.Context()
            self.worker_socket = self.worker_context.socket(zmq.PULL)
            self.worker_socket.bind("tcp://127.0.0.1:%s" % self.port)
        else:
            self.master_context = zmq.Context()
            self.master_socket = self.master_context.socket(zmq.PUSH)
            self.master_socket.connect("tcp://127.0.0.1:%s" % self.port)

            self.worker_context = zmq.Context()
            self.worker_socket = self.worker_context.socket(zmq.SUB)
            self.worker_socket.connect("tcp://127.0.0.1:%s" % SUB_PORT)
            self.worker_socket.setsockopt_string(zmq.SUBSCRIBE, self.broadcast_queue)
            self.worker_socket.setsockopt_string(zmq.SUBSCRIBE, self.queue)

    def publish(self, queue, data):
        try:
            if queue == "Web":
                self.master_socket.send_string(data)
            elif queue == MasterQueue:
                self.master_socket.send_string(data)
            else:
                data = "{0}#{1}".format(queue, data)
                self.master_socket.send_string(data)
        except Exception as e:
                log.error('Error sending message {0} ({1})'.format(data, e))

    def broadcast(self, data):
        self.master_socket.send_string("{0}#{1}".format(self.broadcast_queue, data))

    def check(self):
        try:
            if self.queue == MasterQueue:
                return self.worker_socket.recv_string()
            else:
                data = self.worker_socket.recv_string()
                pos = data.find("#")
                data = data[pos+1:]
                return data
        except Exception as e:
                log.error('Error receiving message ({0})'.format(e))