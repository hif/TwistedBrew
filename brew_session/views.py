from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from django.template import RequestContext
from django.shortcuts import render_to_response
from models import Session, SessionDetail
from forms import *
from masters.brewcommander import BrewCommander
import json, random
import utils.logging as log


def sessions(request):
    context = RequestContext(request)
    welcome_message = 'Welcome to Brew Sessions'
    sessions = Session.objects.all()
    context_dict = {
        'brew_sessions_active': True,
        'welcome_message': welcome_message,
        'sessions': sessions,
    }

    return render_to_response('sessions.html', context_dict, context)


def create(request):
    if request.POST:
        form = SessionForm(request.POST)
        if form.is_valid():
            form.save()
        return HttpResponseRedirect('/brew_session/sessions')
    else:
        form = SessionForm()
    args = {}
    args.update(csrf(request))
    args['form'] = form
    return render_to_response('create_session.html', args)


def scheduler(request):
    context = RequestContext(request)

    if request.method == 'POST':
        form = SessionFormSet(request.POST)

        # Have we been provided with a valid form?
        if form.is_valid():
            # Save the new category to the database.

            # Now call the index() view.
            # The user will be shown the homepage.
            #commander = BrewCommander()
            #command, params = commander.parse_command(last_message)
            #commander.sendmaster(command, params)
            #return HttpResponseRedirect('/')
            log.debug('A valid session form was sent')
        else:
            # The supplied form contained errors - just print them to the terminal.
            print form.errors
    else:
        # If the request was not a POST, display the form to enter details.

        session = Session.objects.get(pk=1)
        form = SessionForm(instance=session)

    # Bad form (or form details), no form supplied...
    # Render the form with error messages (if any).

    context_dict = {
        'brew_sessions_active': True,
        'form': form,
    }

    return render_to_response('scheduler.html', context_dict, context)