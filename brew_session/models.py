from django.db import models
import datetime

COLUMN_SMALL_SIZE = 124

class Session(models.Model):
    name = models.CharField(max_length=COLUMN_SMALL_SIZE)
    session_date = models.DateField(default=datetime.datetime.now())
    source = models.CharField(max_length=COLUMN_SMALL_SIZE)
    notes = models.TextField()
    locked = models.BooleanField()

    def __unicode__(self):
        if self.locked:
            status = 'locked'
        else:
            status = 'active'
        return u'[{1}] {0} ({2})'.format(self.name, self.session_date, status)


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
    name = models.CharField(max_length=COLUMN_SMALL_SIZE)
    worker = models.CharField(max_length=COLUMN_SMALL_SIZE)
    target = models.CharField(max_length=COLUMN_SMALL_SIZE)
    hold_time = models.IntegerField(default=1)
    time_unit_seconds = models.IntegerField(choices=HOLD_TIME_UNITS, default=MINUTES)
    notes = models.TextField()
    done = models.BooleanField()

    def __unicode__(self):
        return u'{0} ({1})'.format(self.name, self.worker)