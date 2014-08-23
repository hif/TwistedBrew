from django.db import models
import random
import time

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
    user = models.CharField(max_length=COLUMN_SMALL_SIZE)
    timestamp = models.DateTimeField(auto_now=True)
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
            tmp.user = 'debug'
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

#class Commander(models.Model):
#    command = models.CharField(max_length=100)
#
#    def __unicode__(self):
#        return self.command