from django.contrib import admin
# imports from within the Django web app must be scoped below the web package
from twistedbrew.models import Brew, Worker, Measurement, Command

admin.site.register(Brew)
admin.site.register(Worker)
admin.site.register(Measurement)
admin.site.register(Command)