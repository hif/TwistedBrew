from django.http import HttpResponse
from django.views.generic import DetailView, ListView, UpdateView, DeleteView
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from django.template import RequestContext
from django.shortcuts import render_to_response
from core.master import Master
from models import Worker, Measurement
from forms import *
import json


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


def session_reset(request, pk):
    selected_session = Session.objects.get(pk=pk)
    if not selected_session is None:
        selected_session.reset()
        return HttpResponse('Session reset')
    else:
        return HttpResponse('Session not found for resetting')


def session_archive(request, pk):
    selected_session = Session.objects.get(pk=pk)
    if not selected_session is None:
        selected_session.locked = True
        selected_session.reset()
        return HttpResponse('Session archived')
    else:
        return HttpResponse('Session not found for archiving')


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
    selected_session = Session.objects.get(id=session_id)
    args['session'] = selected_session
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


def send_session_detail_command(request):
    if request.POST:
        command = request.POST['command']
        session_detail_id = request.POST['session_detail_id']
        session_detail = SessionDetail.objects.get(pk=int(session_detail_id))
        if session_detail.assigned_worker is None:
            return HttpResponse('Session detail has no assigned worker')
        worker_id = str(session_detail.assigned_worker.id)
        Master.send_master(command, worker_id)
        return HttpResponse('Command sent to worker')
    return HttpResponse('Missing command and worker to send, use POST')


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
        'workers_active': True,
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


def session_available_options(request):
    session_set = Session.objects.all().filter(locked=False)
    options = ''
    for s in session_set:
        options += '<option value="{0}">{1}</option>'.format(str(s.id), s.name)
    return HttpResponse(options)


def worker_available_options(request):
    if request.method == 'POST':
        worker_set = Worker.objects.all().filter(type=request.POST['worker_type']).filter(status=Worker.AVAILABLE)
        if len(worker_set) == 0:
            options = '<option value="0">No worker available</option>'
        else:
            options = ''
            for w in worker_set:
                options += '<option value="{0}">{1}</option>'.format(str(w.id), w.name)
    else:
        options = '<option value="0">No worker available</option>'
    return HttpResponse(options)


def session_data(request):
    context = RequestContext(request)
    context.update(csrf(request))
    if request.method == 'POST':
        brew = Session.objects.get(pk=(request.POST['pk']))
    else:
        brew = None
    return render_to_response('session_data.html', {'data': brew}, context)


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


def session_dashboard(request):
    args = {}
    args.update(csrf(request))
    args['session_dashboard_active'] = True
    return render_to_response('session_dashboard.html', args)


def session_dashboard_details(request):
    context = RequestContext(request)
    context.update(csrf(request))
    if request.method == 'POST':
        session_selected = Session.objects.get(pk=(request.POST['pk']))
    else:
        session_selected = None
    return render_to_response('session_dashboard_details.html', {'session': session_selected}, context)


def session_work_status(request, session_id):
    #context = RequestContext(request)
    #context.update(csrf(request))
    work_status = {}
    selected_session = Session.objects.get(pk=int(session_id))
    if selected_session.active_detail is None:
        work_status['active_detail'] = '0'
        work_status['worker_status'] = '0'
    else:
        work_status['active_detail'] = str(selected_session.active_detail.id)
        work_status['worker_status'] = str(selected_session.active_detail.assigned_worker.status)
    return HttpResponse(json.dumps(work_status), content_type="application/json")

def worker_widget(request, session_id):
    selected_session = Session.objects.get(pk=int(session_id))
    selected_session_detail = selected_session.active_detail
    selected_worker = None
    if not selected_session_detail is None:
        selected_worker = selected_session_detail.assigned_worker
    last_measurements = None
    if not selected_worker is None:
        last_measurements = list()
        for device in selected_worker.workerdevice_set.all():
            try:
                last_measurement = Measurement.objects.\
                    filter(session_detail=selected_session_detail).\
                    filter(worker=selected_worker.name).\
                    filter(device=device).\
                    latest('timestamp')
            except Exception:
                last_measurement = "-n/a-"
            last_measurements.append(last_measurement)
    args = {}
    args.update(csrf(request))
    args['session'] = selected_session
    args['session_detail'] = selected_session_detail
    args['worker'] = selected_worker
    args['last_measurements'] = last_measurements
    return render_to_response('worker_widget_data.html', args)



