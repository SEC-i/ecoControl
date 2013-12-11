import calendar
import datetime
from django.db import models

class Actuator(models.Model):
    device = models.ForeignKey('Device')
    name = models.CharField(max_length = 100)
    target_parameter = models.CharField(max_length = 100)
    value_min = models.IntegerField(default=0)
    value_max = models.IntegerField(default=1)
    input_type = models.CharField(max_length = 50)

    class Meta:
        permissions = ()

    def __unicode__(self):
        return self.name + " (#" + str(self.pk) + ")"

class Device(models.Model):
    name = models.CharField(max_length = 100)
    interval = models.IntegerField()

    class Meta:
        permissions = ()

    def __unicode__(self):
        return self.name + " (#" + str(self.pk) + ")"
    
class Sensor(models.Model):
    device = models.ForeignKey('Device')
    name = models.CharField(max_length = 100)
    key_name = models.CharField(max_length = 100)
    unit = models.CharField(max_length = 50)
    group = models.IntegerField()

    class Meta:
        permissions = ()

    def __unicode__(self):
        return self.name + " (#" + str(self.pk) + ")"
    
class SensorEntry(models.Model):
    sensor = models.ForeignKey('Sensor')
    value = models.CharField(max_length = 200)
    timestamp = models.DateTimeField(auto_now = False)

    class Meta:
        permissions = ()

    def __unicode__(self):
        return str(self.pk) + " (" + self.sensor.name + ")"

class SensorDelta(models.Model):
    sensor = models.ForeignKey('Sensor')
    delta = models.CharField(max_length = 200)
    interval = models.CharField(max_length = 200) #in seconds
    timestamp = models.DateTimeField(auto_now = False)



    class Meta:
        permissions = ()

class SensorRule(models.Model):
    sensor = models.ForeignKey('Sensor')
    threshold = models.CharField(max_length = 200)
    comparison = models.CharField(max_length = 10) #<>=
    target_function = models.CharField(max_length = 200)

    class Meta:
        permissions = ()

class Task(models.Model):
    command = models.CharField(max_length = 200) #reference to a function
    execution_timestamp = models.DateTimeField(auto_now = False)
    status = models.IntegerField() #on/off for now
    sensor = models.ForeignKey('Sensor')

    class Meta:
        permissions = ()
