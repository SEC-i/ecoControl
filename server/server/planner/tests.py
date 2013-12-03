import os
import time
from datetime import datetime, timedelta
from django.utils.timezone import utc
import planner

from server.models import Sensor, SensorDelta, SensorEntry, SensorRule, Device
from django.test import TestCase

class TestPlanner(TestCase):
    @classmethod  
    def setUpClass(cls): 
        ## Create test user for all tests
        #Sensor.objects.create_user(username = "test_user", password = "demo123", first_name="test_fn", last_name="test_ln")

        # Add test Device and Sensor
        device = Device.objects.create(name="arduino", data_source="http://172.16.19.114:9002/get/",interval=60)
        sensor = Sensor.objects.create(name="Plant #2", device=device, key_name="plant2_value", unit="hpi",group=0)

        SensorEntry.objects.create(sensor=sensor,value = 547,timestamp=datetime.now().replace(tzinfo=utc)-timedelta(seconds=10))
        SensorEntry.objects.create(sensor=sensor,value = 546,timestamp=datetime.now().replace(tzinfo=utc)-timedelta(seconds=9))
        SensorEntry.objects.create(sensor=sensor,value = 545,timestamp=datetime.now().replace(tzinfo=utc)-timedelta(seconds=8))
        SensorEntry.objects.create(sensor=sensor,value = 548,timestamp=datetime.now().replace(tzinfo=utc)-timedelta(seconds=7))
        SensorEntry.objects.create(sensor=sensor,value = 547,timestamp=datetime.now().replace(tzinfo=utc)-timedelta(seconds=6))
        SensorEntry.objects.create(sensor=sensor,value = 544,timestamp=datetime.now().replace(tzinfo=utc)-timedelta(seconds=5))
        SensorEntry.objects.create(sensor=sensor,value = 543,timestamp=datetime.now().replace(tzinfo=utc)-timedelta(seconds=4))
        SensorEntry.objects.create(sensor=sensor,value = 542,timestamp=datetime.now().replace(tzinfo=utc)-timedelta(seconds=3))
        SensorEntry.objects.create(sensor=sensor,value = 541,timestamp=datetime.now().replace(tzinfo=utc)-timedelta(seconds=2))
        SensorEntry.objects.create(sensor=sensor,value = 540,timestamp=datetime.now().replace(tzinfo=utc)-timedelta(seconds=1))


    def setUp(self):
        #self.sensor = 
        self.sensor = Sensor.objects.get(key_name="plant2_value")
        #print SensorEntry.objects.all().filter(sensor= self.sensor).order_by('-timestamp')[0] 
        planner.functions.update_delta()

    def testRule(self):
        rule = SensorRule()
        rule.sensor_id = self.sensor.id
        rule.threshold = 310
        #sensor_value  >  rule.threshold
        rule.comparison =">"
        rule.target_function = "test"
        rule.save()
        self.assertTrue(planner.functions.check_rules())

        rule.delete()

    def testDelta(self):
        """ create a delta representing an old value and calculate a new value
        based on two new sensor entrys"""
        sensor_delta = SensorDelta()
        sensor_delta.sensor_id = self.sensor.id
        sensor_delta.delta = 0.3
        sensor_delta.interval = 1 #seconds
        sensor_delta.timestamp = datetime.now().replace(tzinfo=utc)
        sensor_delta.save()

        entry = SensorEntry()
        entry.sensor_id = self.sensor.id
        entry.value = 600
        entry.timestamp = datetime.now().replace(tzinfo=utc)
        entry.save()

        time.sleep(1.1)

        entry2 = SensorEntry()
        entry2.sensor_id = self.sensor.id
        entry2.value = 700
        entry2.timestamp = datetime.now().replace(tzinfo=utc)
        entry2.save()

        # new delta is 700-600 = 100,so sensor_delta should get bigger
        planner.functions.update_delta()

        # get the updated sensor_delta (apparantly isnt tracked in sensor_delta)
        sensor_delta_updated = SensorDelta.objects.get(sensor_id= sensor_delta.sensor_id).delta
        self.assertTrue(sensor_delta_updated > 0.3)

        entry.delete()
        entry2.delete()
        sensor_delta.delete()
        
    def tearDown(self):
        for rule in SensorRule.objects.filter(target_function= "test"):
            rule.delete()
