from django.conf.urls import patterns, include, url
from twisted_brew.views import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()


urlpatterns = patterns('',
    url(r'^$', home, name='home'),
    url(r'^index[/]$', home, name='home'),
    url(r'^home[/]$', home, name='home'),
    url(r'^commands[/]$', commands, name='commands'),
    url(r'^messages[/]$', MessageListView.as_view()),
    url(r'^warnings[/]$', WarningListView.as_view()),
    url(r'^errors[/]$', ErrorListView.as_view()),
    url(r'^messages_clear[/]$', messages_clear, name='messages_clear'),
    url(r'^message_head[/]$', message_head, name='message_head'),
    url(r'^message_rows/(?P<latest_timestamp>\d+)/(?P<max_rows>\d+)[/]$', message_rows, name='message_rows'),
    url(r'^message_delete/(?P<message_id>\d+)[/]$', message_delete, name='message_delete'),
    url(r'^message_fake/(?P<calling_page>\w+)/(?P<message_type>\w+)[/]$', message_fake, name='message_fake'),
    url(r'^charts[/]$', charts, name='charts'),
    url(r'^charts_update[/]$', charts_update, name='charts_update'),
    url(r'^ping_master[/]$', ping_master, name='ping_master'),
    url(r'^fetch_master_info[/]$', fetch_master_info, name='fetch_master_info'),
    url(r'^set_master_info[/]$', set_master_info, name='set_master_info'),
    (r'^brew/', include('brew.urls')),
    (r'^session/', include('session.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),

    # Django REST framework
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/v1/', include('twisted_brew.api_v1_urls')),

    # Django Angular test
    url(r'^twistedbrew[/]$', twistedbrew, name='twistedbrew'),
)
