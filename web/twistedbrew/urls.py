from django.conf.urls import patterns, include, url
# imports from within the Django web app must be scoped below the web package
from twistedbrew import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'web.views.home', name='home'),
    # url(r'^web/', include('web.foo.urls')),

    url(r'^$', views.home, name='home'),
    url(r'^index[/]$', views.home, name='home'),
    url(r'^home[/]$', views.home, name='home'),
)
