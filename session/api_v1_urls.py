from django.conf.urls import patterns, include, url
from rest_framework import routers
from session.views import SessionViewSet, SessionDetailViewSet
from session.views import WorkerViewSet, WorkerDeviceViewSet
from session.views import MeasurementViewSet


router = routers.DefaultRouter()
router.register(r'sessions', SessionViewSet)
router.register(r'session_details', SessionDetailViewSet)
router.register(r'workers', WorkerViewSet)
router.register(r'worker_devices', WorkerDeviceViewSet)
router.register(r'measurements', MeasurementViewSet)


urlpatterns = patterns('',
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
)
