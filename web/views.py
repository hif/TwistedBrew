from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.shortcuts import render_to_response
from models import Brew, Worker, Command, Measurement
from forms import CommanderForm
from masters.brewcommander import BrewCommander

def home(request):
    context = RequestContext(request)
    welcome_message = 'Welcome to Twisted Brew'
    context_dict = {
        'welcome_message': welcome_message,
    }

    return render_to_response('home.html', context_dict, context)

def brews(request):
    context = RequestContext(request)
    brew_list = Brew.objects.order_by('name')

    context_dict = {
        'brews': brew_list,
    }

    return render_to_response('brews.html', context_dict, context)


def workers(request):
    context = RequestContext(request)
    worker_list = Worker.objects.order_by('type')

    context_dict = {
        'workers': worker_list,
    }

    return render_to_response('workers.html', context_dict, context)


def commands(request):
    context = RequestContext(request)
    command_list = Command.objects.order_by('type')

    context_dict = {
        'commands': command_list,
    }
    return render_to_response('commands.html', context_dict, context)


def measurements(request):
    context = RequestContext(request)
    measurement_list = Measurement.objects.order_by('-timestamp')

    context_dict = {
        'measurements': measurement_list,
    }
    return render_to_response('measurements.html', context_dict, context)

def commander(request):
    context = RequestContext(request)
    worker_list = Worker.objects.order_by('-type')
    brew_list = Brew.objects.order_by('-name')
    lastmessage = 'None'

    # A HTTP POST?
    if request.method == 'POST':
        form = CommanderForm(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.

            # Now call the index() view.
            # The user will be shown the homepage.
            lastmessage = form.cleaned_data['command']
            commander = BrewCommander()
            command, params = commander.parse_command(lastmessage)
            commander.sendmaster(command, params)
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
        'workers': worker_list,
        'brews': brew_list,
        'form':form,
        'lastmessage':lastmessage,
    }

    return render_to_response('commander.html', context_dict, context)
