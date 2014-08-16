#!/usr/bin python
from workers.brewworker import *
from recipes.beerparser import *
from schedules.mash import *
from schedules.boil import *
from schedules.fermentation import *
import utils.logging as log
import utils.brewutils
from web.models import Brew, Worker, Command, Measurement


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

        self.recipie_file = DefaultRecipeFile
        if configfile is not None:
            self.recipie_file = configfile
        self.recipe_name = "My Beer"
        self.recipe = BeerData()
        self.recipe_loaded = False
        self.recipes = {}
        self.load_recipies()

        self.instructions = {}
        self.broadcasts = {}
        self.messages = {}
        self.register_commands()

        self.workers = []

        self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.ip, self.port))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=MasterQueue)

    def run(self):
        self.listen()

    def register_commands(self):
        Command.objects.all().delete()
        self.instructions = {
            MessageInfo:"Register worker info",
            MessageLoad:"Load recipe",
            MessageExecute:"Send message to worker",
            MessageUpdate:"Register mesurement update",
        }
        self.store_commands(self.instructions, "Instruction")
        self.broadcasts = {
            "info":"Drop current workers and make all available workers register with master",
            "reset":"Reset all workers",
        }
        self.store_commands(self.broadcasts, "Broadcast")
        self.messages = {
            "reset":"Reset worker",
            "pause":"Pause worker",
            "resume":"Resume worker",
            "mash":"Make worker start a mash process",
            "boil":"Make worker start a boil process",
            "ferment":"Make a worker start a fermentation process",
        }
        self.store_commands(self.messages, "Message")

    def store_commands(self, commands, type):
        for name, description in commands.iteritems():
            tmp = Command()
            tmp.type = type
            tmp.name = name
            tmp.description = description
            tmp.save()


    def load_recipies(self, recipefile=None):
        try:
            Brew.objects.all().delete()
            if recipefile is not None:
                self.recipie_file = recipefile
            log.debug('Loading recipe file {0}...'.format(self.recipie_file))
            beer = BeerParser()
            recipedata = beer.get_recipes(self.recipie_file)
            self.recipes = {}
            brews = []
            for item in recipedata:
                name = utils.brewutils.lookup_brew_name(item).strip()
                if name is not None:
                    self.recipes[name] = item
                    # Save to database
                    brew = utils.brewutils.create_brew_model(item)
                    brew.save()
            log.debug('...done loading recipe file {0}'.format(self.recipie_file))
        except Exception, e:
            log.error('Failed to load recipes {0} ({1})'.format(self.recipie_file, e.message))

    def load(self, recipe):
        try:
            if len(self.recipes) == 0:
                log.debug('No recipes found in {}'.format(self.recipie_file), log.WARNING)
            self.recipe_name = recipe.strip().decode('utf-8')
            log.debug('Loading {0}'.format(recipe))
            self.recipe = None
            if not self.recipe_name in self.recipes:
                log.debug('Recipe {0} not found in data file', log.WARNING)
                # Fake result
                self.recipe = self.recipes.values()[0]
                self.recipe_loaded = True
                print self.recipe
                #
                return
            self.recipe = self.recipes[self.recipe_name]
            self.recipe_loaded = True
        except Exception, e:
            log.error('Unable to find recipe {0} ({1})'.format(self.recipe, e))

    def add_worker(self, worker, workertype):
        new_worker = Worker()
        new_worker.name = worker
        new_worker.type = workertype
        self.workers.append(new_worker)
        new_worker.save()

    def get_workers(self, workertype):
        result = []
        for worker in self.workers:
            if worker.type == workertype:
                result.append(worker.name)
        return result

    def get_worker_types(self):
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
            self.handle_update(body)
            return
        if str(body).startswith(MessageInfo):
            self.handle_info(body)
            return
        if str(body).startswith(MessageExecute):
            self.handle_execute(body)
            return
        if str(body).startswith(MessageLoad):
            self.handle_load(body)
            return
        log.debug('Ignorable reply from from worker: {0}'.format(body))

    def handle_info(self, body):
        data = str(body).split(MessageSplit)
        self.add_worker(data[1], data[2])

    def handle_execute(self, body):
        data = str(body).split(MessageSplit)
        command = data[1]
        worker = ''
        if len(data) > 2:
            worker = data[2]
        self.send_command(command, worker)

    def handle_load(self, body):
        data = str(body).split(MessageSplit)
        self.load(data[1])

    def handle_update(self, body):
        log.debug('Receiving worker update...')
        data = body.split(MessageSplit)
        measurement = Measurement()
        measurement.user = data[1]
        measurement.value = data[2]
        measurement.save()

    def verify_worker(self, worker):
        for available_worker in self.workers:
            if available_worker.name == worker:
                return True
        return False

    def send(self, worker, data):
        if not self.verify_worker(worker):
            log.debug('Worker {0} not available'.format(worker), log.WARNING)
            return
        connection = pika.BlockingConnection(pika.ConnectionParameters(self.ip, self.port))
        channel = connection.channel()
        channel.queue_declare(queue=worker)

        channel.basic_publish(exchange='', routing_key=worker, body=data)
        connection.close()

    def send_all(self, data):
        log.debug('Sending:{0}'.format(data))
        connection = pika.BlockingConnection(pika.ConnectionParameters(self.ip, self.port))
        channel = connection.channel()
        channel.exchange_declare(exchange=BroadcastExchange, type='fanout')

        channel.basic_publish(exchange=BroadcastExchange, routing_key='', body=data)
        connection.close()

    def send_schedule(self, worker, schedule):
        schedule.parse(self.recipe)
        self.send(worker, schedule.to_yaml())

    def info(self):
        Worker.objects.all().delete()
        self.send_all(MessageInfo)

    def reset_all(self):
        self.send_all(MessageReset)

    def reset(self, worker=None):
        if worker is None:
            self.reset_all()
        else:
            self.send(worker, MessageReset)

    def pause(self, worker):
        self.send(worker, MessagePause)

    def resume(self, worker):
        self.send(worker, MessageResume)

    def stop(self, worker):
        self.send(worker, MessageStop)

    def mash(self, worker):
        if not self.recipe_loaded:
            log.debug('No recipe loaded!', log.WARNING)
            return
        self.send_schedule(worker, MashSchedule())
        log.debug('Mashing Schedule Sent')

    def boil(self, worker):
        if not self.recipe_loaded:
            log.debug('No recipe loaded!', log.ERROR)
            return
        self.send_schedule(worker, BoilSchedule())
        log.debug('Boil Schedule Sent')

    def ferment(self, worker):
        if not self.recipe_loaded:
            log.debug('No recipe loaded!', log.ERROR)
            return
        scde = FermentationSchedule()
        self.send_schedule(worker, scde)
        log.debug('Fermentation Schedule Sent')

    def send_command(self, command, worker):
        if not hasattr(self, command):
            log.debug('No such command in BrewMaster', log.ERROR)
            return
        method = getattr(self, command)
        if worker is not None and worker != '' and command in self.messages.keys():
            method(worker)
        elif command in self.broadcasts.keys():
            method()
        else:
            log.debug('Master requested to send an unauthorized command: {0}'.format(command))
