from django.conf.urls import patterns, include, url
from rest_framework import routers
from brew.views import BrewViewSet


router = routers.DefaultRouter()
router.register(r'brews', BrewViewSet)

urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
)
