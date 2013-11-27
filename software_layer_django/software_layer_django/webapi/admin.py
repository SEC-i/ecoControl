from django.contrib import admin
from models import Device, Sensor, SensorEntry

# Register models
admin.site.register(Device)
admin.site.register(Sensor)
admin.site.register(SensorEntry)