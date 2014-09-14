from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from views import SessionView, SessionsView, SessionUpdateView, SessionDeleteView


urlpatterns = patterns('',
    url(r'^$', SessionsView.as_view()),
    url(r'^brew_sessions/$', SessionsView.as_view()),
    url(r'^brew_session_selection/$', 'brew_session.views.brew_session_selection'),
    url(r'^brew_session_data/$', 'brew_session.views.brew_session_data'),
    url(r'^brew_session/(?P<pk>\d+)/$', SessionView.as_view()),
    url(r'^brew_session_update/(?P<pk>\d+)/$', SessionUpdateView.as_view()),
    url(r'^brew_session_delete/(?P<pk>\d+)/$', SessionDeleteView.as_view()),
    url(r'^brew_session_execute/(?P<pk>\d+)/$', 'brew_session.views.brew_session_execute'),
    url(r'^create/$', 'brew_session.views.create'),
    url(r'^create_detail/(?P<session_id>\d+)/$', 'brew_session.views.create_detail'),
    url(r'^set_source/(?P<session_id>\d+)/$', 'brew_session.views.set_source'),
    url(r'^scheduler/$', 'brew_session.views.scheduler'),
)
