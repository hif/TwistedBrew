from django.conf.urls import patterns, include, url
import views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', views.home, name='home'),
    url(r'^index[/]$', views.home, name='home'),
    url(r'^home[/]$', views.home, name='home'),
    url(r'^commands[/]$', views.commands, name='commands'),
    url(r'^messages[/]$', views.MessageListView.as_view()),
    url(r'^warnings[/]$', views.WarningListView.as_view()),
    url(r'^errors[/]$', views.ErrorListView.as_view()),
    url(r'^messages_clear[/]$', views.messages_clear, name='messages_clear'),
    url(r'^message_head[/]$', views.message_head, name='message_head'),
    url(r'^message_rows/(?P<latest_timestamp>\d+)/(?P<max_rows>\d+)[/]$', views.message_rows, name='message_rows'),
    url(r'^charts[/]$', views.charts, name='charts'),
    url(r'^charts_update[/]$', views.charts_update, name='charts_update'),
    (r'^brew/', include('brew.urls')),
    (r'^session/', include('session.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
