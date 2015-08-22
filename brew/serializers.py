from rest_framework import serializers
from brew.models import Brew, BrewSection, BrewStep


class BrewSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Brew
        fields = ("id", "name", "brewer", "style", "category", "description", "profile", "ingredients", "web_link")


class BrewSectionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BrewSection
        fields = ("id", "brew", "index", "name", "worker_type")


class BrewStepSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = BrewStep
        fields = ("id", "brew_section", "index", "name", "unit", "target", "hold_time", "time_unit_seconds")
