#!/usr/bin python

from core.comm.mq import MQ


class ZeroMQ(MQ):

    def __init__(self, ip, port, queue, broadcast_queue, ignore_broadcasts=False):
        MQ.__init__(self, ip, port, queue, broadcast_queue, ignore_broadcasts)

    def publish(self, queue, data):
        pass

    def broadcast(self, data):
        pass

    def check(self):
        pass