from django.db import models
import random
import time
import datetime
from brew_session.models import SessionDetail

COLUMN_SMALL_SIZE = 128


class Measurement(models.Model):
    timestamp = models.DateTimeField(auto_now=False)
    session_detail = models.ForeignKey(SessionDetail)
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
    description = models.TextField()

    def __unicode__(self):
        return '{0} - {1}'.format(self.name, self.description)


class Message(models.Model):
    timestamp = models.DateTimeField(auto_now=True)
    type = models.CharField(max_length=COLUMN_SMALL_SIZE)
    text = models.TextField()

    @staticmethod
    def clear():
        Message.objects.all().delete()

    def __unicode__(self):
        return '{0} [{1}] {2}'.format(self.timestamp, self.type, self.text)
