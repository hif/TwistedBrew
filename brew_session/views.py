from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import DetailView, ListView
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from django.template import RequestContext
from django.shortcuts import render_to_response
from models import Session, SessionDetail
from forms import *
from masters.brewcommander import BrewCommander
import json, random
import utils.logging as log


class SessionView(DetailView):
    template_name = 'session.html'
    model = Session

    def get_context_data(self, **kwargs):
        context = super(SessionView, self).get_context_data(**kwargs)
        context['brew_session_active'] = True
        context['details'] = SessionDetail.objects.all().filter(session=context['object'].pk)
        return context


class SessionsView(ListView):
    template_name = 'sessions.html'
    model = Session

    def get_context_data(self, **kwargs):
        context = super(SessionsView, self).get_context_data(**kwargs)
        context['brew_session_active'] = True
        return context


def session(request, session_id):
    context = RequestContext(request)
    if session_id:
        s = Session.objects.get(id=session_id)
        if s:
            context_dict = {
                'brew_sessions_active': True,
                'object': s,
    }

    return render_to_response('session.html', context_dict, context)


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


def create_detail(request, session_id):
    if request.POST:
        form = SessionDetailForm(request.POST)
        if form.is_valid():
            session_detail = form.save(commit=False)
            session_detail.session_id = int(session_id)
            session_detail.save()
        return HttpResponseRedirect('/brew_session/session/%s' % session_id)
    else:
        form = SessionDetailForm()
    args = {}
    args.update(csrf(request))
    args['form'] = form
    session = Session.objects.get(id=session_id)
    args['session'] = session
    return render_to_response('create_detail.html', args)


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