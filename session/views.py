from django.http import HttpResponse
from django.views.generic import DetailView, ListView, UpdateView, DeleteView
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from django.template import RequestContext
from django.shortcuts import render_to_response
from core.master import Master
from models import Worker, Measurement
from forms import *


class SessionView(DetailView):
    template_name = 'session_start.html'
    model = Session

    def get_context_data(self, **kwargs):
        context = super(SessionView, self).get_context_data(**kwargs)
        context['session_active'] = True
        context['details'] = SessionDetail.objects.all().filter(session=context['object'].pk)
        context['workers'] = Worker.objects.all()   #.filter(status=Worker.AVAILABLE)
        return context


class SessionsView(ListView):
    template_name = 'sessions.html'
    model = Session

    def get_context_data(self, **kwargs):
        context = super(SessionsView, self).get_context_data(**kwargs)
        context['session_active'] = True
        if 'pk' in self.kwargs:
            context['selection'] = int(self.kwargs['pk'])
        else:
            context['selection'] = 0
        return context


class SessionUpdateView(UpdateView):
    template_name = 'session_update.html'
    model = Session
    success_url = '/session/sessions/'

    def get_success_url(self):
        return self.success_url + self.kwargs['pk'] + "/"


class SessionDetailUpdateView(UpdateView):
    template_name = 'session_detail_update.html'
    model = SessionDetail
    success_url = '/session/sessions/'

    def get_success_url(self):
        return self.success_url + str(self.get_object().session.id) + "/"


class SessionDeleteView(DeleteView):
    template_name = 'session_delete.html'
    model = Session
    success_url = ('/session/sessions/')

def session(request, session_id):
    context = RequestContext(request)
    if session_id:
        s = Session.objects.get(id=session_id)
        if s:
            context_dict = {
                'sessions_active': True,
                'object': s,
    }

    return render_to_response('session.html', context_dict, context)


def session_create(request):
    if request.POST:
        form = SessionForm(request.POST)
        if form.is_valid():
            instance = form.save()
            return HttpResponseRedirect('/session/sessions/' + str(instance.pk) + '/')
        return HttpResponseRedirect('/session/sessions/')
    else:
        form = SessionForm()
    args = {}
    args.update(csrf(request))
    args['form'] = form
    return render_to_response('session_create.html', args)


def session_detail_create(request, session_id):
    if request.POST:
        form = SessionDetailForm(request.POST)
        if form.is_valid():
            session_detail = form.save(commit=False)
            session_detail.session_id = int(session_id)
            session_detail.save()
        return HttpResponseRedirect('/session/session/%s' % session_id)
    else:
        form = SessionDetailForm()
    args = {}
    args.update(csrf(request))
    args['form'] = form
    session = Session.objects.get(id=session_id)
    args['session'] = session
    return render_to_response('session_detail_create.html', args)


def session_detail_start(request):
    if request.POST:
        session_detail_id = request.POST['session_detail_id']
        worker_id = request.POST['worker_id']
        Master.start_work(worker_id, session_detail_id)
        return HttpResponse('Session detail started')
    return HttpResponse('Missing session detail to start, use POST')


def send_master_command(request):
    if request.POST:
        command = request.POST['command']
        Master.send_master(command)
        return HttpResponse('Command sent to master')
    return HttpResponse('Missing command to send, use POST')


def send_worker_command(request):
    if request.POST:
        command = request.POST['command']
        worker_id = request.POST['worker_id']
        Master.send_master(command, worker_id)
        return HttpResponse('Command sent to worker')
    return HttpResponse('Missing command and worker to send, use POST')



def workers(request):
    context = RequestContext(request)
    worker_list = Worker.objects.order_by('type')

    context_dict = {
        'workers_active' : True,
        'workers': worker_list,
    }

    return render_to_response('workers.html', context_dict, context)


def session_selection(request):
    if request.method == 'POST':
       session_list = Session.objects.order_by('name')
    else:
        session_list = []
    if 'init_brew_selection' in request.POST:
        init_selection = int(request.POST['init_brew_selection'])
    else:
        init_selection = 0
    return render_to_response('session_selection.html', {'selection': session_list, 'init_selection': init_selection})


def session_data(request):
    if request.method == 'POST':
        brew = Session.objects.get(pk=(request.POST['pk']))
    else:
        brew = None
    return render_to_response('session_data.html', {'data': brew})


class MeasurementListView(ListView):
    template_name = 'measurements.html'
    model = Measurement
    paginate_by = 15
    heading = 'Measurements'
    active_tab = 'measurements_active'

    class Meta:
        ordering = ['-timestamp']

    def get_context_data(self, **kwargs):
        context = super(MeasurementListView, self).get_context_data(**kwargs)
        context[self.active_tab] = True
        context['heading'] = self.heading
        return context


def measurements_clear(request):
    Measurement.objects.all().delete()
    return HttpResponseRedirect('/session/measurements/')