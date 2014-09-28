from django.db import models
import datetime
import brew.models
import time
import random

COLUMN_SMALL_SIZE = 124


class Session(models.Model):
    name = models.CharField(max_length=COLUMN_SMALL_SIZE)
    session_date = models.DateField(default=datetime.datetime.now())
    source = models.ForeignKey(brew.models.Brew)
    notes = models.TextField(blank=True)
    locked = models.BooleanField(default=False)
    active_detail = models.ForeignKey('SessionDetail', related_name='session_active_detail', null=True)

    def save(self, *args, **kwargs):
        adding = self._state.adding
        models.Model.save(self, *args, **kwargs)
        if self.source and adding:
            index = 1
            for section in self.source.brewsection_set.all():
                for step in section.brewstep_set.all():
                    detail = SessionDetail()
                    detail.session = self
                    detail.name = step.name
                    detail.index = index
                    detail.worker_type = section.worker_type
                    detail.target = step.target
                    detail.hold_time = step.hold_time
                    detail.time_unit_seconds = step.time_unit_seconds
                    detail.notes = section.name
                    detail.done = False
                    detail.skip = False
                    detail.save()
                    index += 1

    def __unicode__(self):
        #if self.locked:
        #    status = 'locked'
        #else:
        #    status = 'active'
        #return u'[{1}] {0} ({2})'.format(self.name, self.session_date, status)
        return u'[{1}] {0}'.format(self.name, self.session_date)


class SessionDetail(models.Model):
    SECONDS = 1
    MINUTES = 60
    HOURS = 60*MINUTES
    DAYS = 24*HOURS
    HOLD_TIME_UNITS = (
        (SECONDS, 'Seconds'),
        (MINUTES, 'Minutes'),
        (HOURS, 'Hours'),
        (DAYS, 'Days')
    )
    session = models.ForeignKey('Session')
    index = models.IntegerField()
    name = models.CharField(max_length=COLUMN_SMALL_SIZE)
    worker_type = models.CharField(max_length=COLUMN_SMALL_SIZE)
    target = models.CharField(max_length=COLUMN_SMALL_SIZE)
    hold_time = models.IntegerField(default=1)
    time_unit_seconds = models.IntegerField(choices=HOLD_TIME_UNITS, default=MINUTES)
    notes = models.TextField()
    done = models.BooleanField(default=False)
    assigned_worker = models.ForeignKey('Worker', null=True, default=None)

    def begin_work(self, worker_id):
        assigned_worker = Worker.objects.get(pk=worker_id)
        assigned_worker.status = Worker.BUSY
        assigned_worker.save()
        self.assigned_worker = assigned_worker
        self.session.active_detail = self
        self.session.save()
        self.save()
        return True

    def end_work(self):
        self.assigned_worker.status = Worker.AVAILABLE
        self.assigned_worker.save()
        self.assigned_worker = None
        self.session.active_detail = None
        self.session.save()
        self.done = True
        self.save()

    def __unicode__(self):
        return u'{0}) {1} [{2}]'.format(self.index, self.name, self.worker_type)


class Worker(models.Model):
    AVAILABLE = 0
    BUSY = 1
    PAUSED = 2
    OFF_LINE = 3
    WORKER_STATUS = (
        (AVAILABLE, 'Available'),
        (BUSY, 'Busy'),
        (PAUSED, 'Paused'),
        (OFF_LINE, 'Off-line'),
    )
    name = models.CharField(max_length=COLUMN_SMALL_SIZE)
    type = models.CharField(max_length=COLUMN_SMALL_SIZE)
    status = models.IntegerField(choices=WORKER_STATUS, default=AVAILABLE)
    working_on = models.ForeignKey('SessionDetail', null=True)

    @staticmethod
    def enlist_worker(worker_name, worker_type, devices):
        worker_set = Worker.objects.filter(name=worker_name, type=worker_type)
        if len(worker_set) == 0:
            enlisted_worker = Worker()
            enlisted_worker.name = worker_name
            enlisted_worker.type = worker_type
        else:
            enlisted_worker = worker_set[0]
        enlisted_worker.status = Worker.AVAILABLE
        enlisted_worker.save()
        for device in devices:
            check_device = WorkerDevice.objects.filter(worker=enlisted_worker).filter(name=device)
            if len(check_device) == 0:
                add_device = WorkerDevice()
                add_device.name = device
                add_device.worker = enlisted_worker
                add_device.save()
        return enlisted_worker


    @staticmethod
    def take_workers_off_line():
        workers = Worker.objects.filter(status=Worker.AVAILABLE)
        for worker in workers:
            worker.status = Worker.OFF_LINE
            worker.save()

    @staticmethod
    def force_workers_off_line():
        workers = Worker.objects.all()
        for worker in workers:
            worker.status = Worker.OFF_LINE
            worker.save()

    @staticmethod
    def set_worker_status(worker_id, status):
        worker = Worker.objects.get(pk=worker_id)
        if worker is None:
            return False
        worker.status = status
        worker.save()
        return True

    @staticmethod
    def get_worker_status(worker_id):
        worker = Worker.objects.get(pk=worker_id)
        if worker is None:
            return None
        return worker.status

    def __unicode__(self):
        return '{0} - {1} ({2})'.format(self.name, self.type, Worker.WORKER_STATUS[self.status][1])


class WorkerDevice(models.Model):
    name = models.CharField(max_length=COLUMN_SMALL_SIZE)
    worker = models.ForeignKey(Worker)

    def __unicode__(self):
        return self.name


class WorkerMeasurement(models.Model):
    timestamp = models.DateTimeField(auto_now=False)
    session_detail = models.ForeignKey(SessionDetail)
    worker = models.CharField(max_length=COLUMN_SMALL_SIZE)
    device = models.CharField(max_length=COLUMN_SMALL_SIZE)
    value = models.FloatField()
    set_point = models.FloatField()
    work = models.CharField(max_length=COLUMN_SMALL_SIZE)
    remaining = models.CharField(max_length=COLUMN_SMALL_SIZE)

    class Meta:
        ordering = ['-timestamp']

    @staticmethod
    def clear():
        WorkerMeasurement.objects.all().delete()

    def __unicode__(self):
        return '{0} [{1}-{2}] {3}'.format(self.timestamp, self.worker, self.device, self.value)


