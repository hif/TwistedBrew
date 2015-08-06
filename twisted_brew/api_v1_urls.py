from django.conf.urls import patterns, include, url
from rest_framework import routers
from twisted_brew.views import MessageViewSet, CommandViewSet


router = routers.DefaultRouter()
router.register(r'messages', MessageViewSet)
router.register(r'commands', CommandViewSet)


urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
)
