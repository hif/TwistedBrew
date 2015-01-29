#!/usr/bin python

import pika
from core.comm.mq import MQ


class RabbitMQ(MQ):

    def __init__(self, ip, port, queue, broadcast_queue, ignore_broadcasts=False):
        MQ.__init__(self, ip, port, queue, broadcast_queue, ignore_broadcasts)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.ip, self.port))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue)
        self.channel.exchange_declare(exchange=self.broadcast_queue, exchange_type='fanout')
        if not self.ignore_broadcasts:
            self.channel.queue_bind(exchange=self.broadcast_queue, queue=self.queue)

    def __del__(self):
        self.connection.close()

    def publish(self, queue, data):
        connection = pika.BlockingConnection(pika.ConnectionParameters(self.ip, self.port))
        channel = connection.channel()
        channel.basic_publish(exchange='', routing_key=queue, body=data)
        connection.close()

    def broadcast(self, data):
        connection = pika.BlockingConnection(pika.ConnectionParameters(self.ip, self.port))
        channel = connection.channel()
        channel.basic_publish(exchange=self.broadcast_queue, routing_key='', body=data)
        connection.close()

    def check(self):
        method, properties, body = self.channel.basic_get(queue=self.queue, no_ack=True)
        return body
