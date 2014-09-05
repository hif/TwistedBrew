from django.db import models
import random
import time
import datetime

COLUMN_SMALL_SIZE = 128
COLUMN_LARGE_SIZE = 4096


class Brew(models.Model):
    name = models.CharField(max_length=COLUMN_SMALL_SIZE)
    brewer = models.CharField(max_length=COLUMN_SMALL_SIZE)
    style = models.CharField(max_length=COLUMN_SMALL_SIZE)
    category = models.CharField(max_length=COLUMN_SMALL_SIZE)
    description = models.CharField(max_length=COLUMN_LARGE_SIZE)
    profile = models.CharField(max_length=COLUMN_LARGE_SIZE)
    ingredients = models.CharField(max_length=COLUMN_LARGE_SIZE)
    weblink = models.CharField(max_length=COLUMN_SMALL_SIZE)

    def __unicode__(self):
        return u'{0} ({1}) by {2}'.format(self.name, self.style, self.brewer)


class Worker(models.Model):
    name = models.CharField(max_length=COLUMN_SMALL_SIZE)
    type = models.CharField(max_length=COLUMN_SMALL_SIZE)

    def __unicode__(self):
        return '{0} ({1})'.format(self.name, self.type)


class Measurement(models.Model):
    timestamp = models.DateTimeField(auto_now=False)
    session = models.CharField(max_length=COLUMN_SMALL_SIZE)
    worker = models.CharField(max_length=COLUMN_SMALL_SIZE)
    device = models.CharField(max_length=COLUMN_SMALL_SIZE)
    value = models.FloatField()
    set_point = models.FloatField()

    @staticmethod
    def populate(size=100, append=False):
        if not append:
            Measurement.objects.all().delete()
        random.seed()
        count = 0
        while count < size:
            time.sleep(1)
            tmp = Measurement()
            tmp.worker = 'debug'
            tmp.device = 'debug'
            tmp.value = random.random()*100.0
            tmp.save()
            count += 1
            print 'Added measurement {0} of {1}'.format(count, size)

    @staticmethod
    def clear():
        Measurement.objects.all().delete()

    def __unicode__(self):
        return '{0} [{1}] {2}'.format(self.timestamp, self.user, self.value)


class Command(models.Model):
    name = models.CharField(max_length=COLUMN_SMALL_SIZE)
    type = models.CharField(max_length=COLUMN_SMALL_SIZE)
    description = models.CharField(max_length=COLUMN_LARGE_SIZE)

    def __unicode__(self):
        return '{0} ({1})'.format(self.name, self.type)


class Message(models.Model):
    timestamp = models.DateTimeField(auto_now=True)
    type = models.CharField(max_length=COLUMN_SMALL_SIZE)
    text = models.CharField(max_length=COLUMN_LARGE_SIZE)

    @staticmethod
    def clear():
        Message.objects.all().delete()

    def __unicode__(self):
        return '{0} [{1}] {2}'.format(self.timestamp, self.type, self.text)


class Session(models.Model):
    name = models.CharField(max_length=COLUMN_SMALL_SIZE)
    session_date = models.DateField(default=datetime.datetime.now())
    source = models.CharField(max_length=COLUMN_SMALL_SIZE)
    notes = models.CharField(max_length=COLUMN_LARGE_SIZE)
    locked = models.BooleanField()

    def __unicode__(self):
        if self.locked:
            status = 'locked'
        else:
            status = 'active'
        return '[{1}] {0} ({2})'.format(self.name, self.session_date, status)


class SessionDetail(models.Model):
    SECONDS = 'FR'
    MINUTES = 'SO'
    HOURS = 'JR'
    DAYS = 'SR'
    HOLD_TIME_UNITS = (
        (SECONDS, 1),
        (MINUTES, 60),
        (HOURS, 60*MINUTES),
        (DAYS, 24*HOURS)
    )
    session = models.ForeignKey('Session')
    name = models.CharField(max_length=COLUMN_SMALL_SIZE)
    worker = models.CharField(max_length=COLUMN_SMALL_SIZE)
    target = models.CharField(max_length=COLUMN_SMALL_SIZE)
    hold_time = models.IntegerField(default=1)
    time_unit_seconds = models.IntegerField(choices=HOLD_TIME_UNITS, default=MINUTES)
    notes = models.CharField(max_length=COLUMN_LARGE_SIZE)
    done = models.BooleanField()
