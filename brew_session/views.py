from django.shortcuts import render
from django.http import HttpResponse
from django.core.context_processors import csrf
from django.views.generic import DetailView, ListView, UpdateView, DeleteView
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from django.template import RequestContext
from django.shortcuts import render_to_response
from models import Session, SessionDetail
from web.models import Worker
from forms import *
from masters.brewcommander import BrewCommander
import json, random
import utils.logging as log


class SessionView(DetailView):
    template_name = 'brew_session_start.html'
    model = Session

    def get_context_data(self, **kwargs):
        context = super(SessionView, self).get_context_data(**kwargs)
        context['brew_session_active'] = True
        context['details'] = SessionDetail.objects.all().filter(session=context['object'].pk)
        context['workers'] = Worker.objects.all().filter(status=Worker.AVAILABLE)
        return context


class SessionsView(ListView):
    template_name = 'brew_sessions.html'
    model = Session

    def get_context_data(self, **kwargs):
        context = super(SessionsView, self).get_context_data(**kwargs)
        context['brew_session_active'] = True
        if 'pk' in self.kwargs:
            context['selection'] = int(self.kwargs['pk'])
        else:
            context['selection'] = 0
        return context


class SessionUpdateView(UpdateView):
    template_name = 'brew_session_update.html'
    model = Session
    success_url = '/brew_session/brew_sessions/'

    def get_success_url(self):
        return self.success_url + self.kwargs['pk'] + "/"


class SessionDetailUpdateView(UpdateView):
    template_name = 'brew_session_detail_update.html'
    model = SessionDetail
    success_url = '/brew_session/brew_sessions/'

    def get_success_url(self):
        return self.success_url + str(self.get_object().session.id) + "/"


class SessionDeleteView(DeleteView):
    template_name = 'brew_session_delete.html'
    model = Session
    success_url = ('/brew_session/brew_sessions/')

def session(request, session_id):
    context = RequestContext(request)
    if session_id:
        s = Session.objects.get(id=session_id)
        if s:
            context_dict = {
                'brew_sessions_active': True,
                'object': s,
    }

    return render_to_response('brew_session.html', context_dict, context)


def brew_session_create(request):
    if request.POST:
        form = SessionForm(request.POST)
        if form.is_valid():
            instance = form.save()
            return HttpResponseRedirect('/brew_session/brew_sessions/' + str(instance.pk) + '/')
        return HttpResponseRedirect('/brew_session/brew_sessions/')
    else:
        form = SessionForm()
    args = {}
    args.update(csrf(request))
    args['form'] = form
    return render_to_response('brew_session_create.html', args)


def create_detail(request, session_id):
    if request.POST:
        form = SessionDetailForm(request.POST)
        if form.is_valid():
            session_detail = form.save(commit=False)
            session_detail.session_id = int(session_id)
            session_detail.save()
        return HttpResponseRedirect('/brew_session/brew_session/%s' % session_id)
    else:
        form = SessionDetailForm()
    args = {}
    args.update(csrf(request))
    args['form'] = form
    session = Session.objects.get(id=session_id)
    args['session'] = session
    return render_to_response('create_detail.html', args)


def start_session_detail(request):
    if request.POST:
        session_detail_id = request.POST['session_detail_id']
        worker_id = request.POST['worker_id']
        brew_commander = BrewCommander()
        brew_commander.start_work(worker_id, session_detail_id)
        return HttpResponse('Session detail started')
    return HttpResponse('Missing session detail to start, use POST')


def send_brewmaster(request):
    if request.POST:
        command = request.POST['command']
        brew_commander = BrewCommander()
        brew_commander.send_master(command)
        return HttpResponse('Command sent to master')
    return HttpResponse('Missing command to send, use POST')


def send_brewworker(request):
    if request.POST:
        command = request.POST['command']
        worker_id = request.POST['worker_id']
        brew_commander = BrewCommander()
        brew_commander.send_master(command, worker_id)
        return HttpResponse('Command sent to worker')
    return HttpResponse('Missing command and worker to send, use POST')


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


def brew_session_selection(request):
    if request.method == 'POST':
       session_list = Session.objects.order_by('name')
    else:
        session_list = []
    if 'init_brew_selection' in request.POST:
        init_selection = int(request.POST['init_brew_selection'])
    else:
        init_selection = 0
    return render_to_response('brew_session_selection.html', {'selection': session_list, 'init_selection': init_selection})


def brew_session_data(request):
    if request.method == 'POST':
        brew = Session.objects.get(pk=(request.POST['pk']))
    else:
        brew = None
    return render_to_response('brew_session_data.html', {'data': brew})
