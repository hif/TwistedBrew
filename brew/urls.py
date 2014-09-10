from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView


urlpatterns = patterns('',
                       url(r'^brews/$', 'brew.views.brews'),
                       url(r'^brew_selection/$', 'brew.views.brew_selection'),
                       url(r'^brew_data/$', 'brew.views.brew_data'),
)
