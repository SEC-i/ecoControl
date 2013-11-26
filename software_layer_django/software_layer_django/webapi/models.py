import json, calendar

from django.db import models

class Device(models.Model):
    name = models.CharField(max_length = 100)
    data_source = models.CharField(max_length = 200)
    
    def to_dict(self):
        return { 'id':self.id, 'name':self.name, 'data_source':self.data_source }
    
class Sensor(models.Model):
    device = models.ForeignKey('Device')
    name = models.CharField(max_length = 100)
    unit = models.CharField(max_length = 50)
    
    def to_dict(self):
        return { 'id':self.id, 'device_id':self.device.id, 'name':self.name, 'unit':self.unit }
    
class SensorEntry(models.Model):
    sensor = models.ForeignKey('Sensor')
    value = models.CharField(max_length = 200)
    timestamp = models.DateTimeField(auto_now = True)
    
    def to_dict(self):
        return { 'id':self.id, 'sensor_id':self.sensor.id, 'value':self.value, 'timestamp':calendar.timegm(self.timestamp.utctimetuple()) }

class SensorDelta(models.Model):
    sensor = models.ForeignKey('Sensor')
    delta = models.CharField()
    interval = models.CharField() #in seconds
    timestamp = models.DateTimeField(auto_now = False)

    def to_dict(self):
        return { 'id':self.id, 'delta': self.delta,'interval':self.interval,'timestamp':self.timestamp }
    

class Task(models.Model):
    command = models.CharField() #reference to a function
    execution_timestamp = models.DateTimeField(auto_now = False)
    status = models.IntegerField() #on/off for now
    def to_dict(self):
        return { 'id':self.id, 'command': self.command,'status':self.status,'execution_timestamp':self.execution_timestamp }

class SensorRule(models.Model):
    sensor = models.ForeignKey('Sensor')
    threshold = models.CharField(max_length = 200)
    comparison = models.CharField(max_length = 10) #<>=
    target_function = models.DateTimeField(auto_now = False)

    def to_dict(self):
        return { 'id':self.id, 'sensor':self.sensor,'threshold': self.threshold,'comparison':self.comparison,'target_function':self.target_function }


