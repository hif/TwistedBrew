from workers.brewworker import *
from recipes.beerparser import *
import recipes.brew
from schedules.mash import *
from schedules.boil import *
from schedules.fermentation import *
import utils.logging as log


class Worker():
    def __init__(self, name, workertype):
        self.name = name
        self.type = workertype

    def __str__(self):
        return '{0} of type {1}'.format(self.name, self.type)


class BrewMaster(threading.Thread):
    def __init__(self, config=None, configfile=None):
        threading.Thread.__init__(self)
        if config is None:
            self.name = MasterQueue
            self.ip = MessageServerIP
            self.port = MessageServerPort
        else:
            self.name = config.name
            self.ip = config.ip
            self.port = config.port

        self.recipiefile = DefaultRecipeFile
        if configfile is not None:
            self.recipiefile = configfile
        self.recipename = "My Beer"
        self.recipe = BeerData()
        self.recipeloaded = False
        self.recipes = {}
        self.loadrecipies()

        self.instructions = {MessageInfo, MessageLoad, MessageExecute, MessageUpdate}
        self.broadcastcommands = {"info", "reset"}
        self.workercommands = {"reset", "pause", "resume", "mash", "boil", "ferment"}
        self.workers = []

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.ip, self.port))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=MasterQueue)

    def run(self):
        self.listen()

    def loadrecipies(self, recipefile=None):
        try:
            if recipefile is not None:
                self.recipiefile = recipefile
            log.debug('Loading recipe file {0}...'.format(self.recipiefile))
            beer = BeerParser()
            recipedata = beer.get_recipes(self.recipiefile)
            self.recipes = {}
            brews = []
            for item in recipedata:
                name = recipes.brew.recipename(item).strip()
                if name is not None:
                    self.recipes[name] = item
                    brews.append(recipes.brew.Brew(item))
            log.debug('...done loading recipe file {0}'.format(self.recipiefile))
            self.storebrews(brews)
        except Exception, e:
            log.error('Failed to load recipes {0} ({1})'.format(self.recipiefile, e.message))

    @staticmethod
    def storebrews(brews):
        for brew in brews:
            log.debug(u'Storing {0}'.format(brew.name))

    def load(self, recipe):
        try:
            if len(self.recipes) == 0:
                log.debug('No recipes found in {}'.format(self.recipiefile), log.WARNING)
            self.recipename = recipe.strip()
            log.debug('Loading {0}'.format(recipe))
            self.recipe = None
            if not self.recipename in self.recipes:
                log.debug('Recipe {0} not found in data file', log.WARNING)
                # Fake result
                self.recipe = self.recipes.values()[0]
                self.recipeloaded = True
                print self.recipe
                #
                return
            self.recipe = self.recipes[self.recipename]
            self.recipeloaded = True
        except Exception, e:
            log.error('Unable to find recipe {0} ({1})'.format(self.recipe, e))

    def brewworkers(self):
        # TODO: Implement
        pass

    def brews(self):
        # TODO: Implement
        pass

    def clearworkers(self):
        self.workers = []

    def addworker(self, worker, workertype):
        self.workers.append(Worker(worker, workertype))

    def getworkers(self, workertype):
        result = []
        for worker in self.workers:
            if worker.type == workertype:
                result.append(worker.name)
        return result

    def getworkertypes(self):
        result = []
        for worker in self.workers:
            if not result.__contains__(worker.type):
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
            self.handleupdate(body)
            return
        if str(body).startswith(MessageInfo):
            self.handleinfo(body)
            return
        if str(body).startswith(MessageExecute):
            self.handleexecute(body)
            return
        if str(body).startswith(MessageLoad):
            self.handleload(body)
            return
        log.debug('Ignorable reply from from worker: {0}'.format(body))

    def handleinfo(self, body):
        data = str(body).split(MessageSplit)
        self.addworker(data[1], data[2])

    def handleexecute(self, body):
        data = str(body).split(MessageSplit)
        command = data[1]
        worker = ''
        if len(data) > 2:
            worker = data[2]
        self.sendcommand(command, worker)

    def handleload(self, body):
        data = str(body).split(MessageSplit)
        self.load(data[1])

    def handleupdate(self, body):
        log.debug('Receiving worker update...')
        # TODO:Implement handling updates from workers
        print('****** UPDATE *****' + str(body))

    def send(self, worker, data):
        connection = pika.BlockingConnection(pika.ConnectionParameters(self.ip, self.port))
        channel = connection.channel()
        channel.queue_declare(queue=worker)

        channel.basic_publish(exchange='', routing_key=worker, body=data)
        connection.close()

    def sendall(self, data):
        log.debug('Sending:{0}'.format(data))
        connection = pika.BlockingConnection(pika.ConnectionParameters(self.ip, self.port))
        channel = connection.channel()
        channel.exchange_declare(exchange=BroadcastExchange, type='fanout')

        channel.basic_publish(exchange=BroadcastExchange, routing_key='', body=data)
        connection.close()

    def sendschedule(self, worker, schedule):
        schedule.parse(self.recipe)
        self.send(worker, schedule.toyaml())

    def info(self):
        self.clearworkers()
        self.sendall(MessageInfo)

    def resetall(self):
        self.sendall(MessageReset)

    def reset(self, worker=None):
        if worker is None:
            self.resetall()
        else:
            self.send(worker, MessageReset)

    def pause(self, worker):
        self.send(worker, MessagePause)

    def resume(self, worker):
        self.send(worker, MessageResume)

    def stop(self, worker):
        self.send(worker, MessageStop)

    def mash(self, worker):
        if not self.recipeloaded:
            log.debug('No recipe loaded!', log.WARNING)
            return
        self.sendschedule(worker, MashSchedule())
        log.debug('Mashing Schedule Sent')

    def boil(self, worker):
        if not self.recipeloaded:
            log.debug('No recipe loaded!', log.ERROR)
            return
        self.sendschedule(worker, BoilSchedule())
        log.debug('Boil Schedule Sent')

    def ferment(self, worker):
        if not self.recipeloaded:
            log.debug('No recipe loaded!', log.ERROR)
            return
        scde = FermentationSchedule()
        self.sendschedule(worker, scde)
        log.debug('Fermentation Schedule Sent')

    def listbroadcasts(self):
        return self.broadcastcommands

    def listworkercommands(self):
        return self.workercommands

    def sendcommand(self, command, worker):
        if not hasattr(self, command):
            log.debug('No such command in BrewMaster', log.ERROR)
            return
        method = getattr(self, command)
        if command in self.broadcastcommands:
            method()
        else:
            method(worker)
