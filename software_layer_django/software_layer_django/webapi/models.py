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
    

