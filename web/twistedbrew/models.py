from django.db import models
import random

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

    @staticmethod
    def populate(size=100, append=False):
        if not append:
            Measurement.objects.all().delete()
        random.seed()
        count = 0
        while count < size:
            tmp = Measurement()
            tmp.user = 'debug'
            tmp.value = random.random()*100.0
            tmp.save()
            count += 1

    def __unicode__(self):
        return '{0} [{1}] {2}'.format(self.timestamp, self.user, self.value)


class Command(models.Model):
    name = models.CharField(max_length=COLUMN_SMALL_SIZE)
    type = models.CharField(max_length=COLUMN_SMALL_SIZE)
    description = models.CharField(max_length=COLUMN_LARGE_SIZE)

    def __unicode__(self):
        return '{0} ({1})'.format(self.name, self.type)