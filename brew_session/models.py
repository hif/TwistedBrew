from django.db import models
import datetime
import brew.models

COLUMN_SMALL_SIZE = 124


class Session(models.Model):
    name = models.CharField(max_length=COLUMN_SMALL_SIZE)
    session_date = models.DateField(default=datetime.datetime.now())
    source = models.ForeignKey(brew.models.Brew)
    notes = models.TextField()
    locked = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        adding = self._state.adding
        models.Model.save(self, *args, **kwargs)
        if self.source and adding :
            index = 1
            for section in self.source.brewsection_set.all():
                for step in section.brewstep_set.all():
                    detail = SessionDetail()
                    detail.session = self
                    detail.name = step.name
                    detail.index = index
                    detail.worker = section.worker_type
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
    worker = models.CharField(max_length=COLUMN_SMALL_SIZE)
    target = models.CharField(max_length=COLUMN_SMALL_SIZE)
    hold_time = models.IntegerField(default=1)
    time_unit_seconds = models.IntegerField(choices=HOLD_TIME_UNITS, default=MINUTES)
    notes = models.TextField()
    done = models.BooleanField(default=False)
    skip = models.BooleanField(default=False)

    def __unicode__(self):
        return u'{0}) {1} [{2}]'.format(self.index, self.name, self.worker)


class SessionWork(models.Model):
    timestamp = models.DateTimeField(auto_now=True)
    session_detail = models.ForeignKey('SessionDetail')
    worker = models.ForeignKey('Worker')
    work = models.CharField(max_length=COLUMN_SMALL_SIZE)
    remaining = models.CharField(max_length=COLUMN_SMALL_SIZE)

    def __unicode__(self):
        return u'[{0}] {1} ({2})'.format(self.timestamp, self.work, self.remaining)


class Worker(models.Model):
    AVAILABLE = 0
    BUSY = 1
    PAUSED = 2
    WORKER_STATUS = (
        (AVAILABLE, 'Available'),
        (BUSY, 'Busy'),
        (PAUSED, 'Paused'),
    )
    name = models.CharField(max_length=COLUMN_SMALL_SIZE)
    type = models.CharField(max_length=COLUMN_SMALL_SIZE)
    status = models.IntegerField(choices=WORKER_STATUS, default=AVAILABLE)

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
