from rest_framework import serializers
from twisted_brew.models import Message, Command


class MessageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Message
        fields = ("id", "timestamp", "type", "text")


class CommandSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Command
        fields = ("id", "name", "type", "description")
