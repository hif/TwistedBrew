#!/usr/bin python
from workers.brewworker import *
from recipes.beerparser import *
from schedules.mash import *
from schedules.boil import *
from schedules.fermentation import *
import utils.logging as log
import utils.brewutils
from brew.models import Brew, BrewSection, BrewStep
from web.models import Worker, Command, Measurement
from devices.device import DEVICE_DEBUG
import datetime as dt
import time


class BrewMaster(threading.Thread):

    def __init__(self, config=None, configfile=None):
        threading.Thread.__init__(self)
        self.measurements_lock = threading.Lock()
        if config is None:
            self.name = MasterQueue
            self.ip = MessageServerIP
            self.port = MessageServerPort
        else:
            self.name = config.name
            self.ip = config.ip
            self.port = config.port

        self.recipe_file = DefaultRecipeFile
        if configfile is not None:
            self.recipe_file = configfile
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
        self.enabled = False

    def run(self):
        self.listen()

    def register_commands(self):
        Command.objects.all().delete()
        self.instructions = {
            MessageInfo: "Register worker info",
            MessageLoad: "Load recipe",
            MessageExecute: "Send message to worker",
            MessageUpdate: "Register mesurement update",
            MessageShutdown: "Shutdown brew master",
        }
        self.store_commands(self.instructions, "Instruction")
        self.broadcasts = {
            "info": "Drop current workers and make all available workers register with master",
            "reset": "Reset all workers",
        }
        self.store_commands(self.broadcasts, "Broadcast")
        self.messages = {
            "reset": "Reset worker",
            "pause": "Pause worker",
            "resume": "Resume worker",
            "stop": "stop worker (shutdown)",
            "mash": "Make worker start a mash process",
            "boil": "Make worker start a boil process",
            "ferment": "Make a worker start a fermentation process",
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
            #BrewStep.objects.all().delete()
            #BrewSection.objects.all().delete()
            #Brew.objects.all().delete()
            if recipefile is not None:
                self.recipe_file = recipefile
            log.debug('Loading recipe file {0}...'.format(self.recipe_file))
            beer = BeerParser()
            recipedata = beer.get_recipes(self.recipe_file)
            self.recipes = {}
            brews = []
            for item in recipedata:
                name = utils.brewutils.lookup_brew_name(item).strip()
                if name is not None:
                    self.recipes[name] = item
                    # Save to database
     #              brew, sections = utils.brewutils.create_brew_model(item)
     #              brew.save()
     #              s_count = m_count = b_count = f_count = 0
     #              for section in sections:
     #                  s_count += 1
     #                  s = utils.brewutils.create_section(section, brew, s_count)
     #                  s.save()
     #                  for step in section.steps:
     #                      brew_step = None
     #                      if s.worker_type == 'MashWorker':
     #                          m_count += 1
     #                          brew_step = utils.brewutils.create_mash_step(step, s, m_count)
     #                      elif s.worker_type == 'BoilWorker':
     #                          b_count += 1
     #                          brew_step = utils.brewutils.create_boil_step(step, s, b_count)
     #                      elif s.worker_type == 'FermentationWorker':
     #                          f_count += 1
     #                          brew_step = utils.brewutils.create_fermentation_step(step, s, f_count)
     #                      if brew_step is not None:
     #                          brew_step.save()
            log.debug('...done loading recipe file {0}'.format(self.recipe_file))
        except Exception, e:
            log.error('Failed to load recipes {0} ({1})'.format(self.recipe_file, e.message))

    def load(self, recipe):
        try:
            if len(self.recipes) == 0:
                log.warning('No recipes found in {}'.format(self.recipe_file))
            self.recipe_name = recipe.strip().decode('utf-8')
            log.debug('Loading {0}'.format(recipe))
            self.recipe = None
            if not self.recipe_name in self.recipes:
                log.warning('Recipe {0} not found in data file')
                # Fake result
                self.recipe = self.recipes.values()[0]
                self.recipe_loaded = True
                print('Loding {0} instead'.format(recipe.strip().decode('utf-8')))
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
        self.enabled = True
        #self.channel.basic_consume(self.handle, queue=MasterQueue, no_ack=True)
        #self.channel.start_consuming()
        while self.enabled:
            method, properties, body = self.channel.basic_get(queue=MasterQueue, no_ack=True)
            if body is not None:
                self.handle(self.channel, method, properties, body)
            time.sleep(0.5)
        self.stop_all_workers()
        log.debug('Shutting down Brew master')

    def stop_all_workers(self):
        for worker in self.workers:
            self.send_command('stop', worker.name)

    def shutdown(self):
        #self.channel.stop_consuming()
        self.enabled = False

    def handle(self, ch, method, properties, body):
        #log.debug('Handling message')
        #log.debug(body)
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
        if str(body).startswith(MessageShutdown):
            self.handle_shutdown()
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

    def handle_shutdown(self):
        self.shutdown()

    def handle_update(self, body):
        #log.debug('Receiving worker update...')
        try:
            with self.measurements_lock:
                data = body.split(MessageSplit)
                measurement = Measurement()
                measurement.worker = data[1]
                measurement.device = data[2]
                measurement.value = data[3]
                measurement.set_point = data[4]
                if DEVICE_DEBUG:
                    measurement.timestamp = dt.datetime.strptime(data[5], "%Y-%m-%d %H:%M:%S.%f")
                else:
                    measurement.timestamp = dt.datetime.now()
                measurement.save()
        except Exception, e:
            log.error('Brewmaster could not save measurement to database ({0})'.format(e.message))

    def verify_worker(self, worker):
        for available_worker in self.workers:
            if available_worker.name == worker:
                return True
        return False

    def send(self, worker, data):
        if not self.verify_worker(worker):
            log.warning('Worker {0} not available'.format(worker))
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
            log.warning('No recipe loaded!')
            return
        self.send_schedule(worker, MashSchedule())
        log.debug('Mashing Schedule Sent')

    def boil(self, worker):
        if not self.recipe_loaded:
            log.error('No recipe loaded!')
            return
        self.send_schedule(worker, BoilSchedule())
        log.debug('Boil Schedule Sent')

    def ferment(self, worker):
        if not self.recipe_loaded:
            log.error('No recipe loaded!')
            return
        scde = FermentationSchedule()
        self.send_schedule(worker, scde)
        log.debug('Fermentation Schedule Sent')

    def send_command(self, command, worker):
        if not hasattr(self, command):
            log.error('No such command in BrewMaster')
            return
        method = getattr(self, command)
        if worker is not None and worker != '' and command in self.messages.keys():
            method(worker)
        elif command in self.broadcasts.keys():
            method()
        else:
            log.debug('Master requested to send an unauthorized command: {0}'.format(command))
