from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from django.template import RequestContext
from django.shortcuts import render_to_response
from models import Worker, Command, Measurement, Message
from brew.models import Brew
from forms import *
from masters.brewcommander import BrewCommander
import json, random
import utils.logging as log
from utils.dateutils import *


def home(request):
    context = RequestContext(request)
    welcome_message = 'Welcome to Twisted Brew'
    context_dict = {
        'home_active' : True,
        'welcome_message': welcome_message,
    }

    return render_to_response('home.html', context_dict, context)

def workers(request):
    context = RequestContext(request)
    worker_list = Worker.objects.order_by('type')

    context_dict = {
        'workers_active' : True,
        'workers': worker_list,
    }

    return render_to_response('workers.html', context_dict, context)


def commands(request):
    context = RequestContext(request)
    command_list = Command.objects.order_by('type')

    context_dict = {
        'commands_active' : True,
        'commands': command_list,
    }
    return render_to_response('commands.html', context_dict, context)


def measurements(request):
    context = RequestContext(request)
    measurement_list = Measurement.objects.order_by('-timestamp')

    context_dict = {
        'measurements_active' : True,
        'measurements': measurement_list,
    }
    return render_to_response('measurements.html', context_dict, context)


def measurements_clear(request):
    Measurement.objects.all().delete()
    return HttpResponseRedirect('/measurements')


def messages(request):
    context = RequestContext(request)
    message_list = Message.objects.order_by('-timestamp')

    context_dict = {
        'messages_active': True,
        'messages': message_list,
    }
    return render_to_response('messages.html', context_dict, context)


def messages_clear(request):
    Message.objects.all().delete()
    return HttpResponseRedirect('/messages')


def warnings(request):
    context = RequestContext(request)
    message_list = Message.objects.filter(type='Warning').order_by('-timestamp')

    context_dict = {
        'warnings_active': True,
        'messages': message_list,
    }
    return render_to_response('warnings.html', context_dict, context)


def errors(request):
    context = RequestContext(request)
    message_list = Message.objects.filter(type='Error').order_by('-timestamp')

    context_dict = {
        'errors_active': True,
        'messages': message_list,
    }
    return render_to_response('errors.html', context_dict, context)


def charts(request):
    context = RequestContext(request)

    chart_time = json.dumps(['00:00','00:05','00:10','00:15'])
    chart_data = [0, 10, 15, 20]
    chart_set = [65, 65, 65, 65]

    context_dict = {
        'charts_active': True,
        'chart_label': chart_time,
        'chart_data': chart_data,
        'chart_set': chart_set,
        'mash_worker': 'Mash Dude',
        'fermentation_worker': 'Fermat',
    }
    context_dict.update(csrf(request))
    return render_to_response('charts.html', context_dict, context)


def charts_update(request):

    if request.POST:
        last_timestamp_ms = request.POST.getlist('timestamp')
        worker = request.POST.get('worker')
    log.debug(last_timestamp_ms)
    last_timestamp = ms_to_datetime(int(last_timestamp_ms[0]))
    log.debug(last_timestamp)

    #latest_measurement_set = Measurement.objects.filter(device__iexact='Temperature').filter(timestamp__gt=last_timestamp)
    latest_measurement_set = Measurement.objects.filter(worker=worker).\
        filter(device__iexact='Temperature').filter(timestamp__gt=last_timestamp)

    latest_timestamps = list()
    latest_probe_temps = list()
    latest_set_points = list()

    if latest_measurement_set:
        for item in latest_measurement_set:
            latest_timestamps.append(datetime_to_ms(item.timestamp))
            latest_probe_temps.append(item.value)
            latest_set_points.append(item.set_point)

    update_data = {"latest_set_point": latest_set_points, "latest_probe_temp": latest_probe_temps, "latest_timestamp": latest_timestamps}

    return HttpResponse(json.dumps(update_data), content_type="application/json")


def commander(request):
    context = RequestContext(request)
    worker_list = Worker.objects.order_by('-type')
    brew_list = Brew.objects.order_by('-name')
    last_message = 'None'


    if request.method == 'POST':
        form = CommanderForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.

            # Now call the index() view.
            # The user will be shown the homepage.
            last_message = form.cleaned_data['command']
            commander = BrewCommander()
            command, params = commander.parse_command(last_message)
            commander.send_master(command, params)
            #return HttpResponseRedirect('/')
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.
        form = CommanderForm()

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).

    context_dict = {
        'commander_active': True,
        'workers': worker_list,
        'brews': brew_list,
        'form': form,
        'lastmessage': last_message,
    }

    return render_to_response('commander.html', context_dict, context)

