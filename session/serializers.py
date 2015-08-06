from rest_framework import serializers
from session.models import Session, SessionDetail, Worker, WorkerDevice, Measurement


class SessionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Session
        fields = ("id", "name", "session_date", "source", "notes", "locked", "active_detail")


class SessionDetailSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SessionDetail
        fields = ("id", "session", "index", "name", "worker_type",
                  "target", "hold_time", "time_unit_seconds", "notes", "done", "assigned_worker")


class WorkerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Worker
        fields = ("id", "name", "type", "status", "working_on")


class WorkerDeviceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = WorkerDevice
        fields = ("id", "name", "worker")


class MeasurementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Measurement
        fields = ("id", "timestamp", "session_detail", "worker", "device", "value", "set_point", "work", "remaining")
