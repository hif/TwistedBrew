from django.contrib import admin
from brew.models import Brew, BrewSection, BrewStep

admin.site.register(Brew)
admin.site.register(BrewSection)
admin.site.register(BrewStep)
