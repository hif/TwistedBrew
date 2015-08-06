from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
    url(r'^$', 'brew.views.brews'),
    url(r'^brews/$', 'brew.views.brews'),
    url(r'^brew_selection/$', 'brew.views.brew_selection'),
    url(r'^brew_data/$', 'brew.views.brew_data'),
    url(r'^brew_delete/(?P<pk>\d+)/$', 'brew.views.brew_delete'),
    url(r'^brews_delete_all/$', 'brew.views.brews_delete_all'),
    url(r'^brews_import/$', 'brew.views.brews_import'),
)
