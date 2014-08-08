from django.db import models

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
        return self.title


class Worker(models.Model):
    name = models.CharField(max_length=COLUMN_SMALL_SIZE)
    type = models.CharField(max_length=COLUMN_SMALL_SIZE)

    def __unicode__(self):
        return self.title