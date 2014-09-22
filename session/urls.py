from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from views import SessionView, SessionsView, SessionUpdateView, SessionDeleteView, SessionDetailUpdateView, MeasurementListView


urlpatterns = patterns('',
    url(r'^$', SessionsView.as_view()),
    url(r'^sessions/$', SessionsView.as_view()),
    url(r'^sessions/(?P<pk>\d+)/$', SessionsView.as_view()),
    url(r'^workers[/]$', 'session.views.workers', name='workers'),
    url(r'^session_selection/$', 'session.views.session_selection'),
    url(r'^session_data/$', 'session.views.session_data'),
    url(r'^session_update/(?P<pk>\d+)/$', SessionUpdateView.as_view()),
    url(r'^session_detail_update/(?P<pk>\d+)/$', SessionDetailUpdateView.as_view()),
    url(r'^session_delete/(?P<pk>\d+)/$', SessionDeleteView.as_view()),
    url(r'^session_create/$', 'session.views.session_create'),
    url(r'^session_start/(?P<pk>\d+)/$', SessionView.as_view()),
    url(r'^session_detail_create/(?P<session_id>\d+)/$', 'session.views.session_detail_create'),
    url(r'^session_detail_start/$', 'session.views.session_detail_start'),
    url(r'^measurements[/]$', MeasurementListView.as_view()),
    url(r'^measurements_clear[/]$', 'session.views.measurements_clear', name='measurements_clear'),
    url(r'^send_master_command/$', 'session.views.send_master_command'),
    url(r'^send_worker_command/$', 'session.views.send_worker_command'),
    url(r'^session_dashboard/$', 'session.views.session_dashboard'),
)
