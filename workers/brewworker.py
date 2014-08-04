import pika
import threading
from schedules.mash import *
from masters.defaults import *
from masters.messages import *

MessageFunctions = {MessageInfo:"info", MessagePause:"pause", MessageResume:"resume", MessageReset:"reset", MessageStop:"stop"}

class BrewWorker(threading.Thread):

    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name
        self.ip = MessageServerIP
        self.port = MessageServerPort
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.ip, self.port))
        self.channel = self.connection.channel()
        self.channel.exchange_declare(exchange=BroadcastExchange, type='fanout')
        self.channel.queue_declare(queue=self.name)


    def __str__(self):
        return 'BrewWorker - [name:{0}, type:{1}]'.format(self.name, str(self.__class__.__name__))

    def work(self, ch, method, properties, body):
        print('[*] Waiting for schedule. To exit press CTRL+C')

    def run(self):
        self.listen()

    def listen(self):
        self.onStart()
        self.channel.basic_consume(self.receive, queue=self.name, no_ack=True)
        self.channel.queue_bind(exchange=BroadcastExchange, queue=self.name)
        self.channel.start_consuming()

    def stop(self):
        self.onStop()
        self.channel.stop_consuming()

    def sendMaster(self, data):
        print "[*] Sending to master - " + data

        connection = pika.BlockingConnection(pika.ConnectionParameters(self.ip, self.port))
        channel = connection.channel()
        channel.queue_declare(queue=MasterQueue)

        channel.basic_publish(exchange='', routing_key=MasterQueue, body=data)
        connection.close()

    def receive(self, ch, method, properties, body):
        #print("[*] Receiving:{0}".format(body))
        if(MessageFunctions.__contains__(body) and hasattr(self, MessageFunctions[body])):
            command = MessageFunctions[body]
            #print("[*] Executing:{0}".format(command))
            getattr(self,command)()
            return
        self.work(ch, method, properties, body)

    def work(self, ch, method, properties, body):
        print('[*] Receiving data...')
        print body

    def info(self):
        print("[*] {0} is sending info to master".format(self.name))
        if(self.onInfo()):
            self.sendMaster(MessageInfo + MessageSplit + self.name + MessageSplit + self.__class__.__name__)
        else:
            self.reportError("Info failed")

    def pause(self):
        print("[*] {0} is sending paused to master".format(self.name))
        if(self.onPause()):
            self.sendMaster(MessagePaused + ':' + self.name)
        else:
            self.reportError("Pause failed")
    def resume(self):
        print("[*] {0} is sending resumed to master".format(self.name))
        if(self.onResume()):
            self.sendMaster(MessageResumed + ':' + self.name)
        else:
            self.reportError("Resume failed")

    def reset(self):
        print("[*] {0} is sending ready to master".format(self.name))
        if(self.onReset()):
            self.sendMaster(MessageReady + ':' + self.name)
        else:
            self.reportError("Reset failed")

    def reportError(self, err):
        print("[!] Error:{0}", err)

    def onStart(self):
        pass

    def onStop(self):
        print("[*] Stopping {0}".format(self))

    def onInfo(self):
        return True

    def onPause(self):
        return True

    def onResume(self):
        return True

    def onReset(self):
        return True