from django.db import models

class Device(models.Model):
    name = models.CharField(max_length = 100)

    def __unicode__(self):
        return self.name + " (#" + str(self.pk) + ")"

class DeviceConfiguration(models.Model):
    STR = 0
    INT = 1
    FLOAT = 2
    TYPES = (
        (STR, 'str'),
        (INT, 'int'),
        (FLOAT, 'float'),
    )

    device = models.ForeignKey('Device')
    key = models.CharField(max_length = 100)
    value = models.CharField(max_length = 255)
    value_type = models.PositiveSmallIntegerField(choices = TYPES, default = STR)

class Sensor(models.Model):
    STR = 0
    INT = 1
    FLOAT = 2
    TYPES = (
        (STR, 'str'),
        (INT, 'int'),
        (FLOAT, 'float'),
    )

    device = models.ForeignKey('Device')
    name = models.CharField(max_length = 100)
    key = models.CharField(max_length = 100)
    unit = models.CharField(max_length = 50)
    value_type = models.PositiveSmallIntegerField(choices = TYPES, default = STR)

    def __unicode__(self):
        return self.name + " (#" + str(self.pk) + ")"
    
class SensorValue(models.Model):
    sensor = models.ForeignKey('Sensor')
    value = models.CharField(max_length = 200)
    timestamp = models.DateTimeField(auto_now = False)

    def __unicode__(self):
        return str(self.pk) + " (" + self.sensor.name + ")"