from django.conf.urls import patterns, include, url
import views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
    url(r'^index[/]$', views.home, name='home'),
    url(r'^home[/]$', views.home, name='home'),
    url(r'^workers[/]$', views.workers, name='workers'),
    url(r'^commands[/]$', views.commands, name='commands'),
    url(r'^measurements[/]$', views.measurements, name='measurements'),
    url(r'^measurements_clear[/]$', views.measurements_clear, name='measurements_clear'),
    (r'^brew/', include('brew.urls')),
    (r'^brew_session/', include('brew_session.urls')),
    url(r'^messages[/]$', views.messages, name='messages'),
    url(r'^messages_clear[/]$', views.messages_clear, name='messages_clear'),
    url(r'^warnings[/]$', views.warnings, name='warnings'),
    url(r'^errors[/]$', views.errors, name='errors'),
    url(r'^charts[/]$', views.charts, name='charts'),
    url(r'^charts_update[/]$', views.charts_update, name='charts_update'),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
