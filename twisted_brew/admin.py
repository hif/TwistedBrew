from django.contrib import admin
# imports from within the Django web_x app must be scoped below the web_x package
from twisted_brew.models import Command, Message

admin.site.register(Command)
admin.site.register(Message)