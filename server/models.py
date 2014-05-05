from django.db import models

class Device(models.Model):
    HS = 0 # HeatStorage(self.env)
    PM = 1 # PowerMeter(self.env)
    CU = 2 # CogenerationUnit(self.env, self.hs, self.pm)
    PLB = 3 # PeakLoadBoiler(self.env, self.hs)
    TC = 4 # ThermalConsumer(self.env, self.hs)
    EC = 5 # ElectricalConsumer(self.env, self.pm)
    CE = 6 # CodeExecuter(self.env, {'env': self.env, 'hs': self.hs, ... })
    DEVICE_TYPES = (
        (HS, 'HeatStorage'),
        (PM, 'PowerMeter'),
        (CU, 'CogenerationUnit'),
        (PLB, 'PeakLoadBoiler'),
        (TC, 'ThermalConsumer'),
        (EC, 'ElectricalConsumer'),
        (CE, 'CodeExecuter'),
    )

    name = models.CharField(max_length = 100)
    device_type = models.PositiveSmallIntegerField(choices = DEVICE_TYPES)

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
        
class WeatherSource(models.Model):
    location = models.CharField(max_length = 200)

class WeatherValue(models.Model):
    temperature = models.CharField(max_length = 20) # in degree celsius
    timestamp = models.DateTimeField(auto_now = False) # time when the value was taken
    target_time = models.DateTimeField(auto_now = False) # time the temperature should be effective
