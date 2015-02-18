from django.db import models


COLUMN_SMALL_SIZE = 128


class Command(models.Model):
    name = models.CharField(max_length=COLUMN_SMALL_SIZE)
    type = models.CharField(max_length=COLUMN_SMALL_SIZE)
    description = models.TextField()

    def __str__(self):
        return '{0} - {1}'.format(self.name, self.description)


class Message(models.Model):
    timestamp = models.DateTimeField(auto_now=True)
    type = models.CharField(max_length=COLUMN_SMALL_SIZE)
    text = models.TextField()

    class Meta:
        ordering = ['-timestamp']

    @staticmethod
    def clear():
        Message.objects.all().delete()

    def __str__(self):
        return '{0} [{1}] {2}'.format(self.timestamp, self.type, self.text)
