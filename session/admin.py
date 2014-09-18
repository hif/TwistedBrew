from django.contrib import admin
from models import Session, SessionDetail, Worker, Measurement

admin.site.register(Session)
admin.site.register(SessionDetail)
admin.site.register(Worker)
admin.site.register(Measurement)
