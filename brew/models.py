from django.db import models

COLUMN_SMALL_SIZE = 128


class Brew(models.Model):
    name = models.CharField(max_length=COLUMN_SMALL_SIZE)
    brewer = models.CharField(max_length=COLUMN_SMALL_SIZE)
    style = models.CharField(max_length=COLUMN_SMALL_SIZE)
    category = models.CharField(max_length=COLUMN_SMALL_SIZE)
    description = models.TextField()
    profile = models.TextField()
    ingredients = models.TextField()
    web_link = models.CharField(max_length=COLUMN_SMALL_SIZE)

    def __str__(self):
        return '{0} ({1}) by {2}'.format(self.name, self.style, self.brewer)

    class Meta:
        ordering = ['name']


class BrewSection(models.Model):
    brew = models.ForeignKey('Brew')
    index = models.IntegerField()
    name = models.CharField(max_length=COLUMN_SMALL_SIZE)
    worker_type = models.CharField(max_length=COLUMN_SMALL_SIZE)

    def __str__(self):
        return '{0} using {1}'.format(self.name, self.worker_type)

    class Meta:
        ordering = ['index']


class BrewStep(models.Model):
    SECONDS = 1
    MINUTES = 60
    HOURS = 60 * MINUTES
    DAYS = 24 * HOURS
    HOLD_TIME_UNITS = (
        (SECONDS, 'Seconds'),
        (MINUTES, 'Minutes'),
        (HOURS, 'Hours'),
        (DAYS, 'Days')
    )
    brew_section = models.ForeignKey('BrewSection')
    index = models.IntegerField()
    name = models.CharField(max_length=COLUMN_SMALL_SIZE)
    unit = models.CharField(max_length=COLUMN_SMALL_SIZE)
    target = models.FloatField(max_length=COLUMN_SMALL_SIZE)
    hold_time = models.IntegerField(default=1)
    time_unit_seconds = models.IntegerField(choices=HOLD_TIME_UNITS, default=MINUTES)

    def __str__(self):
        return '{0} with target {1}'.format(self.name, self.target)

    class Meta:
        ordering = ['index']

