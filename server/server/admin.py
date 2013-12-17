from django.contrib import admin
from models import *

# Register models
admin.site.register(Actuator)
admin.site.register(Device)
admin.site.register(Sensor)
admin.site.register(SensorEntry)
admin.site.register(SensorDelta)
admin.site.register(SensorRule)
admin.site.register(Task)