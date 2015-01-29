#!/usr/bin python


class MQ:

    def __init__(self, ip, port, queue, broadcast_queue, ignore_broadcasts=False):
        self.ip = ip
        self.port = port
        self.queue = queue
        self.broadcast_queue = broadcast_queue
        self.ignore_broadcasts = ignore_broadcasts

    def publish(self, queue, data):
        pass

    def broadcast(self, data):
        pass

    def check(self):
        pass