import calendar

from django.db import models

class Actuator(models.Model):
    device = models.ForeignKey('Device')
    parameter_name = models.CharField(max_length = 100)
    value_min = models.IntegerField(default=0)
    value_max = models.IntegerField(default=1)
    input_type = models.CharField(max_length = 50)

class Device(models.Model):
    name = models.CharField(max_length = 100)
    data_source = models.CharField(max_length = 200)

    def __unicode__(self):
        return self.name + " (#" + str(self.pk) + ")"
    
class Sensor(models.Model):
    device = models.ForeignKey('Device')
    name = models.CharField(max_length = 100)
    key_name = models.CharField(max_length = 100)
    unit = models.CharField(max_length = 50)

    def __unicode__(self):
        return self.name + " (#" + str(self.pk) + ")"
    
class SensorEntry(models.Model):
    sensor = models.ForeignKey('Sensor')
    value = models.CharField(max_length = 200)
    timestamp = models.DateTimeField(auto_now = True)

class SensorDelta(models.Model):
    sensor = models.ForeignKey('Sensor')
    delta = models.CharField(max_length = 200)
    interval = models.CharField(max_length = 200) #in seconds
    timestamp = models.DateTimeField(auto_now = False)

class SensorRule(models.Model):
    sensor = models.ForeignKey('Sensor')
    threshold = models.CharField(max_length = 200)
    comparison = models.CharField(max_length = 10) #<>=
    target_function = models.CharField(max_length = 200)

class Task(models.Model):
    command = models.CharField(max_length = 200) #reference to a function
    execution_timestamp = models.DateTimeField(auto_now = False)
    status = models.IntegerField() #on/off for now

