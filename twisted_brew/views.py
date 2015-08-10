from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.db.models import Min
from django.views.generic import ListView
from django.template import RequestContext
from django.shortcuts import render_to_response
import json
from datetime import timedelta as timedelta
import time
from twisted_brew.models import Command,  Message
from session.models import Measurement
from core.master import Master
from core.messages import MessagePong
import core.utils.logging as log
from core.utils.dateutils import *
from django.conf import settings
from rest_framework import viewsets
from twisted_brew.serializers import MessageSerializer, CommandSerializer


class MessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows brewing sessions to be viewed or edited.
    """
    queryset = Message.objects.all().order_by('id')
    serializer_class = MessageSerializer


class CommandViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows commands to be viewed or edited.
    """
    queryset = Command.objects.all().order_by('name')
    serializer_class = CommandSerializer


def home(request):
    context = RequestContext(request)
    welcome_message = 'Welcome to Twisted Brew'
    context_dict = {
        'home_active' : True,
        'welcome_message': welcome_message,
    }

    return render_to_response('home.html', context_dict, context)


def commands(request):
    context = RequestContext(request)
    command_list = Command.objects.order_by('type')

    context_dict = {
        'commands_active' : True,
        'commands': command_list,
    }
    return render_to_response('commands.html', context_dict, context)


class MessageListView(ListView):
    template_name = 'messages.html'
    model = Message
    paginate_by = 15
    heading = 'Messages'
    messages_type = 'messages'
    active_tab = 'messages_active'

    class Meta:
        ordering = ['-timestamp']

    def get_context_data(self, **kwargs):
        context = super(MessageListView, self).get_context_data(**kwargs)
        context[self.active_tab] = True
        context['heading'] = self.heading
        context['messages_type'] = self.messages_type
        return context


class WarningListView(MessageListView):
    heading = 'Warnings'
    active_tab = 'warnings_active'
    messages_type = 'warnings'

    def get_queryset(self):
        return super(MessageListView, self).get_queryset().filter(type='Warning')


class ErrorListView(MessageListView):
    heading = 'Errors'
    active_tab = 'errors_active'
    messages_type = 'errors'

    def get_queryset(self):
        return super(MessageListView, self).get_queryset().filter(type='Error')


def messages_clear(request):
    Message.objects.all().delete()
    return HttpResponseRedirect('/messages')


def message_head(request):
    return HttpResponse('<tr><th>Timestamp</th><th>Type</th><th>Message</th></tr>')


def message_rows(request, latest_timestamp, max_rows):
    rows_html = list()
    counter = 0
    limit = int(max_rows)
    if latest_timestamp == '0':
        obj = Message.objects.all().aggregate(Min('timestamp'))
        if obj['timestamp__min'] is None:
            converted_timestamp = timezone.now()
        else:
            converted_timestamp = obj['timestamp__min'] - timedelta(seconds=1)
    else:
        converted_timestamp = datetime.fromtimestamp(float(latest_timestamp)/1000.0)
        converted_timestamp = timezone.get_current_timezone().localize(converted_timestamp)
    rows = Message.objects.filter(timestamp__gt=converted_timestamp)\
        .order_by('-timestamp')
    for row in rows:
        str_timestamp = '{0}:{1}:{2}'.format(
            str(row.timestamp.hour).zfill(2),
            str(row.timestamp.minute).zfill(2),
            str(row.timestamp.second).zfill(2))
        rows_html.append('<tr class="{3}"><td>{0}</td><td>{1}</td><td>{2}</td></tr>'.format(
            str_timestamp, row.type, row.text, row.type.lower()))
        counter += 1
        if counter >= limit:
            break;
    return HttpResponse(json.dumps(rows_html), content_type="application/json")


def message_delete(request, message_id):
    msg_id = int(message_id)
    Message.objects.get(pk=msg_id).delete()
    return HttpResponse('Message deleted')


def message_fake(request, calling_page, message_type):
    msg = Message()
    msg.type = message_type
    msg.text = "This is a faked message of type {0}".format(message_type)
    msg.save()
    return HttpResponseRedirect('/' + calling_page + '/')


def ping_master(request):
    stamp = timezone.now()
    Master.send_ping()
    pong = False
    count = 0
    while not pong and count < 5:
        found = Message.objects.filter(type=log.LOG_TYPE_TEXT[log.INFO], timestamp__gt=stamp, text=MessagePong)
        if len(found) > 0:
            pong = True
        else:
            time.sleep(1)
            count += 1
    if pong:
        return HttpResponse(MessagePong)
    return HttpResponse('No reply from master')


def fetch_master_info(request):
    response = {
        'master_ip': settings.MASTER_IP,
        'master_port': settings.MASTER_PORT,
    }
    return HttpResponse(json.dumps(response), content_type="application/json")

def set_master_info(request):
    if request.POST:
        master_ip = request.POST.get('master_ip')
        master_port = request.POST.get('master_port')
        settings.MASTER_IP = master_ip
        settings.MASTER_PORT = master_port
    return HttpResponse("Master info updated")


def charts(request):
    context = RequestContext(request)

    chart_time = json.dumps(['00:00', '00:05', '00:10', '00:15'])
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
    #context_dict.update(csrf(request))
    return render_to_response('charts.html', context_dict, context)


def charts_update(request):

    if request.POST:
        last_timestamp_ms = request.POST.getlist('timestamp')
        worker = request.POST.get('worker')
    log.debug('charts log: {0}'.format(last_timestamp_ms))
    #last_timestamp = ms_to_datetime(int(last_timestamp_ms[0]))
    last_timestamp = datetime.fromtimestamp(float(last_timestamp_ms[0])/1000.0)
    last_timestamp = timezone.get_current_timezone().localize(last_timestamp)
    log.debug('charts log: {0}'.format(last_timestamp))

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
    #update_data.update(csrf(request))

    return HttpResponse(json.dumps(update_data), content_type="application/json")

def ng_messages(request):
    context = RequestContext(request)
    return render_to_response('ng_messages.html', None, context)
