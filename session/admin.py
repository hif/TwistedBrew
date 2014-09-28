from django.contrib import admin
from models import Session, SessionDetail, Worker, WorkerDevice, Measurement

admin.site.register(Session)
admin.site.register(SessionDetail)
admin.site.register(Worker)
admin.site.register(WorkerDevice)
admin.site.register(Measurement)
