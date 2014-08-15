from django.conf.urls import patterns, include, url
import views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'web_x.views.home', name='home'),
    # url(r'^web_x/', include('web_x.foo.urls')),
    # url(r'^$', include('twistedbrew.urls')),
    url(r'^$', views.home, name='home'),
    url(r'^index[/]$', views.home, name='home'),
    url(r'^home[/]$', views.home, name='home'),
    url(r'^brews[/]$', views.brews, name='brews'),
    url(r'^workers[/]$', views.workers, name='workers'),
    url(r'^commands[/]$', views.commands, name='commands'),
    url(r'^measurements[/]$', views.measurements, name='measurements'),
    url(r'^commander[/]$', views.commander, name='commander'),
    url(r'^charts[/]$', views.charts, name='charts'),
    url(r'^charts_update[/]$', views.charts_update, name='charts_update'),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
