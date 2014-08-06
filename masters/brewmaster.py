from workers.brewworker import *
from recipies.beerparser import *
from schedules.mash import *
from schedules.boil import *
from schedules.fermentation import *
import utils.logging as log

class Worker():
    def __init__(self, name, type):
        self.name = name
        self.type = type
    def __str__(self):
        return '{0} of type {1}'.format(self.name, self.type)

class BrewMaster(threading.Thread):
    def __init__(self, config = None, file = None):
        threading.Thread.__init__(self)
        if(config == None):
            self.name = MasterQueue
            self.ip = MessageServerIP
            self.port = MessageServerPort
        else:
            self.name = config.name
            self.ip = config.ip
            self.port = config.port

        self.recipiefile = DefaultRecipeFile
        if(file != None):
            self.recipiefile = file
        self.recipename = "My Beer"
        self.recipe = BeerData()
        self.recipeloaded = False
        self.recipedata = None
        self.recipies = []
        self.loadRecipies()

        self.instructions = {MessageInfo, MessageLoad, MessageExecute, MessageUpdate}
        self.broadcastcommands = {"info", "reset"}
        self.workercommands = {"reset", "pause", "resume", "mash", "boil", "ferment"}
        self.workers = []

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.ip, self.port))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=MasterQueue)

    def run(self):
        self.listen()

    def loadRecipies(self, file = None):
        if(file != None):
            self.recipiefile = file
        log.debug('Loading recipe file {0}...'.format(self.recipiefile))
        beer = BeerParser()
        self.recipedata = beer.get_recipies(self.recipiefile)
        for item in self.recipedata:
            self.recipies.append(item.name)
        log.debug('...done loading recipe file {0}'.format(self.recipiefile))

    def load(self, recipe):
        if(len(self.recipies) == 0):
            log.debug('No recipies found in {}'.format(self.recipiefile), log.WARNING)
        self.recipename = recipe
        log.debug('Loading {0}'.format(recipe))
        beer = BeerParser()
        self.recipe = None
        if(not self.recipedata.data.__contains__(self.recipename)):
            log.debug('Recipe {0} not found in data file', log.WARNING)
            #Fake result
            self.recipe = self.recipiesdata[0]
            return
        self.recipe = self.recipiesdata.children[self.recipiename]
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
        log.debug('Waiting for worker updates. To exit press CTRL+C')
        self.channel.basic_consume(self.handle, queue=MasterQueue, no_ack=True)
        self.channel.start_consuming()

    def shutdown(self):
        self.channel.stop_consuming()

    def handle(self, ch, method, properties, body):
        log.debug('Handling message')
        log.debug(body)
        if str(body).startswith(MessageUpdate):
            self.handleUpdate(body)
            return
        if str(body).startswith(MessageInfo):
            self.handleInfo(body)
            return
        if str(body).startswith(MessageExecute):
            self.handleExecute(body)
            return
        if str(body).startswith(MessageLoad):
            self.handleLoad(body)
            return
        log.debug('Unknown master message', log.WARNING)

    def handleInfo(self, body):
        data = str(body).split(MessageSplit)
        self.addWorker(data[1], data[2])

    def handleExecute(self, body):
        data = str(body).split(MessageSplit)
        command = data[1]
        worker = ''
        if(len(data) > 2):
            worker = data[2]
        self.sendCommand(command, worker)

    def handleLoad(self, body):
        data = str(body).split(MessageSplit)
        self.load(data[1])

    def handleUpdate(self, body):
        log.debug('Receiving worker update...')
        #TODO:Implement handling updates from workers
        print('****** UPDATE *****' + str(body))

    def send(self, worker, data):
        connection = pika.BlockingConnection(pika.ConnectionParameters(self.ip, self.port))
        channel = connection.channel()
        channel.queue_declare(queue=worker)

        channel.basic_publish(exchange='', routing_key=worker, body=data)
        connection.close()

    def sendAll(self, data):
        log.debug('Sending:{0}'.format(data))
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

    def reset(self, worker = None):
        if(worker == None):
            self.resetAll()
        else:
            self.send(worker, MessageReset)

    def pause(self, worker):
            self.send(worker, MessagePause)

    def resume(self, worker):
            self.send(worker, MessageResume)

    def stop(self, worker):
            self.send(worker, MessageStop)

    def mash(self, worker):
        if (self.recipeloaded == False):
            log.debug('No recipe loaded!', log.WARNING)
            return
        self.sendSchedule(worker, MashSchedule())
        log.debug('Mashing Schedule Sent')

    def boil(self, worker):
        if (self.recipeloaded == False):
            log.debug('No recipe loaded!', log.ERROR)
            return
        self.sendSchedule(worker, BoilSchedule())
        log.debug('Boil Schedule Sent')

    def ferment(self, worker):
        if (self.recipeloaded == False):
            log.debug('No recipe loaded!', log.ERROR)
            return
        scde = FermentationSchedule()
        self.sendSchedule(worker, scde)
        log.debug('Fermentation Schedule Sent')

    def listBroadcasts(self):
        return self.broadcastcommands

    def listWorkerCommands(self):
        return self.workercommands

    def sendCommand(self, command, worker):
        if(not hasattr(self, command)):
            log.debug('No such command in BrewMaster', log.ERROR)
            return
        method = getattr(self, command)
        if command in self.broadcastcommands:
            method()
        else:
            method(worker)
