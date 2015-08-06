from rest_framework import serializers
from brew.models import Brew


class BrewSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Brew
        fields = ("id", "name", "brewer", "style", "category", "description", "profile", "ingredients", "web_link")
