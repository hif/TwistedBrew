import pika
import threading
import psycopg2
from masters.defaults import *
from masters.messages import *
from workers.brewworker import *
from recipies.beerparser import *
from schedules.mash import *
from schedules.boil import *
from schedules.fermentation import *
from config.brewconfig import MasterConfig

class Worker():
    def __init__(self, name, type):
        self.name = name
        self.type = type
    def __str__(self):
        return '{0} of type {1}'.format(self.name, self.type)

class BrewMaster(threading.Thread):
    def __init__(self, config = None):
        threading.Thread.__init__(self)
        if(config == None):
            self.name = MasterQueue
            self.ip = MessageServerIP
            self.port = MessageServerPort
        else:
            self.name = config.name
            self.ip = config.ip
            self.port = config.port

        self.recipiefile = "recipies/Recipe.bsmx"
        self.recipename = "My Beer"
        self.recipe = BeerData()
        self.recipeloaded = False

        self.broadcastcommands = {"info", "resetAll"}
        self.workercommands = {"reset", "pause", "resume", "mash", "boil", "ferment"}
        self.workers = []

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.ip, self.port))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=MasterQueue)

    def run(self):
        self.listen()

    def loadRecipe(self, recipe, file):
        # FAKE IT FOR NOW
        file = self.recipiefile
        #
        beer = BeerParser()
        recipies = beer.get_recipies(file)
        self.recipe = recipies[0]
        self.recipeloaded = True

    def clearWorkers(self):
        self.workers = []

    def addWorker(self, worker, type):
        self.workers.append(Worker(worker, type))

    def getWorkers(self, type):
        result = []
        for worker in self.workers:
            if(worker.type == type):
                result.append(worker.name)
        return result

    def getWorkerTypes(self, type):
        result = []
        for worker in self.workers:
            if(not result.__contains__(worker.type)):
                result.append(worker.type)
        return result

    def listen(self):
        #print("[*] Broadcasts :", self.listBroadcasts())
        #print("[*] Commands   :", self.listWorkerCommands())
        #self.info()

        print('[*] Waiting for worker updates. To exit press CTRL+C')
        self.channel.basic_consume(self.update, queue=MasterQueue, no_ack=True)
        self.channel.start_consuming()

    def shutdown(self):
        self.channel.stop_consuming()

    def update(self, ch, method, properties, body):
        print('[*] Receiving worker update...')
        if str(body).startswith(MessageInfo):
            data = str(body).split(MessageSplit)
            self.addWorker(data[1], data[2])
        print body


    def send(self, worker, data):
        connection = pika.BlockingConnection(pika.ConnectionParameters(self.ip, self.port))
        channel = connection.channel()
        channel.queue_declare(queue=worker)

        channel.basic_publish(exchange='', routing_key=worker, body=data)
        connection.close()

    def sendAll(self, data):
        print("[*] Sending:{0}".format(data))
        connection = pika.BlockingConnection(pika.ConnectionParameters(self.ip, self.port))
        channel = connection.channel()
        channel.exchange_declare(exchange=BroadcastExchange, type='fanout')

        channel.basic_publish(exchange=BroadcastExchange, routing_key='', body=data)
        connection.close()

    def sendSchedule(self, worker, schedule):
        schedule.parse(self.recipe)
        self.send(worker,schedule.toYaml())

    def info(self):
            self.clearWorkers()
            self.sendAll(MessageInfo)

    def resetAll(self):
            self.sendAll(MessageReset)

    def reset(self, worker):
            self.send(worker, MessageReset)

    def pause(self, worker):
            self.send(worker, MessagePause)

    def resume(self, worker):
            self.send(worker, MessageResume)

    def stop(self, worker):
            self.send(worker, MessageStop)

    def mash(self, worker):
        if (self.recipeloaded == False):
            print("[!] No recipe loaded!")
            return
        self.sendSchedule(worker, MashSchedule())
        print("[*] Mashing Schedule Sent")

    def boil(self, worker):
        if (self.recipeloaded == False):
            print("[!] No recipe loaded!")
            return
        self.sendSchedule(worker, BoilSchedule())
        print("[*] Boil Schedule Sent")

    def ferment(self, worker):
        if (self.recipeloaded == False):
            print("[!] No recipe loaded!")
            return
        scde = FermentationSchedule()
        self.sendSchedule(worker, scde)
        print("[*] Fermentation Schedule Sent")

    def listBroadcasts(self):
        return self.broadcastcommands

    def listWorkerCommands(self):
        return self.workercommands

    def sendCommand(self, command, worker):
        if(not hasattr(self, command)):
            print("[!] No such command in BrewMaster")
            return
        method = getattr(self, command)
        if command in self.broadcastcommands:
            method()
        else:
            method(worker)
        #print("[*] Command executed :", command)
