from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from session.views import SessionView, SessionsView, SessionUpdateView, SessionDeleteView, SessionDetailUpdateView
from session.views import MeasurementListView


urlpatterns = patterns('',
    url(r'^$', SessionsView.as_view()),
    url(r'^sessions/$', SessionsView.as_view()),
    url(r'^sessions/(?P<pk>\d+)/$', SessionsView.as_view()),
    url(r'^workers[/]$', 'session.views.workers', name='workers'),
    url(r'^session_selection/$', 'session.views.session_selection'),
    url(r'^session_available_options/$', 'session.views.session_available_options'),
    url(r'^session_data/$', 'session.views.session_data'),
    url(r'^session_update/(?P<pk>\d+)/$', SessionUpdateView.as_view()),
    url(r'^session_detail_update/(?P<pk>\d+)/$', SessionDetailUpdateView.as_view()),
    url(r'^session_delete/(?P<pk>\d+)/$', SessionDeleteView.as_view()),
    url(r'^session_create/$', 'session.views.session_create'),
    url(r'^session_start/(?P<pk>\d+)/$', SessionView.as_view()),
    url(r'^session_reset/(?P<pk>\d+)/$', 'session.views.session_reset'),
    url(r'^session_archive/(?P<pk>\d+)/$', 'session.views.session_archive'),
    url(r'^session_detail_create/(?P<session_id>\d+)/$', 'session.views.session_detail_create'),
    url(r'^session_detail_start/$', 'session.views.session_detail_start'),
    url(r'^measurements[/]$', MeasurementListView.as_view()),
    url(r'^measurements_clear[/]$', 'session.views.measurements_clear', name='measurements_clear'),
    url(r'^send_master_command/$', 'session.views.send_master_command'),
    url(r'^send_session_detail_command/$', 'session.views.send_session_detail_command'),
    url(r'^send_worker_command/$', 'session.views.send_worker_command'),
    url(r'^session_dashboard/$', 'session.views.session_dashboard'),
    url(r'^session_dashboard_details/$', 'session.views.session_dashboard_details'),
    url(r'^session_work_status/(?P<session_id>\d+)/$', 'session.views.session_work_status'),
    url(r'^worker_available_options/$', 'session.views.worker_available_options'),
    url(r'^workers_info/$', 'session.views.workers_info'),
    url(r'^session_worker_widget/(?P<session_id>\d+)/$', 'session.views.session_worker_widget'),
    url(r'^worker_widget/(?P<worker_id>\d+)/$', 'session.views.worker_widget'),
)
