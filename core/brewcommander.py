#!/usr/bin python
import pika

import core.defaults as default
import core.utils.logging as log
import core.messages as msg


class BrewCommand():
    def __init__(self):
        self.command = ''
        self.worker = ''
        self.parameters = ''

    def __str__(self):
        w = self.worker
        if w is None or w == '':
            w = '-N/A-'
        if w is None or w == '':
            w = '-N/A-'
        return '{0} to {1} with {2}'.format(self.command, w, p)

    def list_parameters(self):
        return self.parameters.split(msg.MessageSplit)

class BrewCommander():
    def __init__(self, ip=default.MessageServerIP, port=default.MessageServerPort):
        self.ip = ip
        self.port = port

    def send_master(self, command, params=None):
        data = command
        if not params is None:
            data += (msg.MessageSplit + params)
        log.debug(u'Commanding master - {0}'.format(data))

        connection = pika.BlockingConnection(pika.ConnectionParameters(self.ip, self.port))
        channel = connection.channel()
        channel.queue_declare(queue=default.MasterQueue)

        channel.basic_publish(exchange='', routing_key=default.MasterQueue, body=data)
        connection.close()

    def start_work(self, worker_id, session_detail_id):
        body = msg.MessageWork + msg.MessageSplit + worker_id + msg.MessageSplit + session_detail_id

        log.debug(u'Commanding master - {0}'.format(body))

        connection = pika.BlockingConnection(pika.ConnectionParameters(self.ip, self.port))
        channel = connection.channel()
        channel.queue_declare(queue=default.MasterQueue)

        channel.basic_publish(exchange='', routing_key=default.MasterQueue, body=body)
        connection.close()


    def parse_command(self, line):
        cmd = line
        param = ''
        if line.__contains__(' '):
            index = line.find(' ')
            cmd = line[:index]
            param = line[(index + 1):]
        return cmd, param
