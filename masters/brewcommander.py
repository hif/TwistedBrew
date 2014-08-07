import pika
import masters.defaults as default
import utils.logging as log
import masters.messages as msg


class BrewCommander():
    def __init__(self, ip=default.MessageServerIP, port=default.MessageServerPort):
        self.ip = ip
        self.port = port

    def sendmaster(self, command, params=None):
        data = command
        if params is not None and params != '':
            data = '{0}{1}{2}'.format(data, msg.MessageSplit, params)

        if command != msg.MessageLoad:
            data = '{0}{1}{2}'.format(msg.MessageExecute, msg.MessageSplit, data)

        log.debug('Commanding master - {0}'.format(data))

        connection = pika.BlockingConnection(pika.ConnectionParameters(self.ip, self.port))
        channel = connection.channel()
        channel.queue_declare(queue=default.MasterQueue)

        channel.basic_publish(exchange='', routing_key=default.MasterQueue, body=data)
        connection.close()
