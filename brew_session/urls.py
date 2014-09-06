from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from views import SessionView, SessionsView


urlpatterns = patterns('',
                       url(r'^sessions/$', SessionsView.as_view()),
                       url(r'^session/(?P<pk>\d+)/$', SessionView.as_view()),
                       #url(r'^session/(?P<session_id>\d+)/$', 'brew_session.views.session'),
                       url(r'^create/$', 'brew_session.views.create'),
                       url(r'^scheduler/$', 'brew_session.views.scheduler'),
)
