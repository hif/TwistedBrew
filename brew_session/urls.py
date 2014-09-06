from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
                       url(r'^sessions/$', 'brew_session.views.sessions'),
                       url(r'^scheduler/$', 'brew_session.views.scheduler'),
)
