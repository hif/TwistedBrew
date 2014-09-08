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
    description = models.TextField()
    profile = models.TextField()
    ingredients = models.TextField()
    weblink = models.CharField(max_length=COLUMN_SMALL_SIZE)

    def __unicode__(self):
        return u'{0} ({1}) by {2}'.format(self.name, self.style, self.brewer)

    class Meta:
        ordering = ['pk']


class BrewSection(models.Model):
    brew = models.ForeignKey('Brew')
    name = models.CharField(max_length=COLUMN_SMALL_SIZE)
    worker_type = models.CharField(max_length=COLUMN_SMALL_SIZE)

    def __unicode__(self):
        return u'{0} - {1} using {2}'.format(self.brew.name, self.name, self.worker_type)

    class Meta:
        ordering = ['pk']

class BrewStep(models.Model):
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
    brew_section = models.ForeignKey('BrewSection')
    name = models.CharField(max_length=COLUMN_SMALL_SIZE)
    unit = models.CharField(max_length=COLUMN_SMALL_SIZE)
    target = models.FloatField(max_length=COLUMN_SMALL_SIZE)
    hold_time = models.IntegerField(default=1)
    time_unit_seconds = models.IntegerField(choices=HOLD_TIME_UNITS, default=MINUTES)

    def __unicode__(self):
        return u'{0} - {1} - {2} with target {3}'.format(
            self.brew_section.brew.name, self.brew_section.name, self.name, self.target)

    class Meta:
        ordering = ['pk']


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
    text = models.TextField()

    @staticmethod
    def clear():
        Message.objects.all().delete()

    def __unicode__(self):
        return '{0} [{1}] {2}'.format(self.timestamp, self.type, self.text)
