import os
import time
from datetime import datetime, timedelta

from django.utils.timezone import utc
from django.test import TestCase

from server.models import Sensor, SensorDelta, SensorEntry, SensorRule, Device, Task
from functions import *

class TestPlanner(TestCase):
    @classmethod  
    def setUpClass(cls): 
        ## Create test user for all tests
        #Sensor.objects.create_user(username = "test_user", password = "demo123", first_name="test_fn", last_name="test_ln")

        # Add test Device and Sensor
        device = Device.objects.create(name="arduino",interval=60)
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
        self.sensor_delta = SensorDelta()
        self.sensor_delta.sensor_id = self.sensor.id
        self.sensor_delta.delta =  0.3
        self.sensor_delta.interval = 10 #seconds
        self.sensor_delta.timestamp = datetime.now().replace(tzinfo=utc)
        self.sensor_delta.save()
        #update_delta()

    def testRule(self):
        rule = SensorRule()
        rule.sensor_id = self.sensor.id
        rule.threshold = 310
        #sensor_value  >  rule.threshold
        rule.comparison =">"
        rule.target_function = "test"
        rule.save()

        self.assertTrue(check_rules())

        rule.delete()


    def testDelta(self):
        """ create a delta representing an old value and calculate a new value
        based on two new sensor entrys"""

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
        update_delta()

        # get the updated sensor_delta (apparantly isnt tracked in sensor_delta)
        sensor_delta_updated = SensorDelta.objects.get(sensor_id= self.sensor_delta.sensor_id).delta
        self.assertTrue(sensor_delta_updated > 10.0)

        entry.delete()
        entry2.delete()
        self.sensor_delta.delete()

    def testTaskCreation(self):
        """create a rule which has a threshold that is not yet reached and a delta, which will
        reach the delta in near future"""
        rule = SensorRule()
        rule.sensor_id = self.sensor.id
        rule.threshold = 570
        #sensor_value  >  rule.threshold
        rule.comparison =">"
        rule.target_function = "test"
        rule.save()

        create_or_update_task(rule, self.sensor_delta)

        tasks = Task.objects.filter(command = "test")

        self.assertTrue(len(tasks)==1)
        #execution is in the future
        self.assertTrue(tasks[0].execution_timestamp > datetime.now().replace(tzinfo=utc))



        
    def tearDown(self):
        for rule in SensorRule.objects.filter(target_function = "test"):
            rule.delete()
        for task in Task.objects.filter(command = "test"):
            task.delete()


#some datafilling for a fresh database
# dev = Device()
# dev.name = "arduino"
# dev.data_source = u"http://172.16.19.114:9002/get/"
# dev.interval = 30
# dev.save()

# sens = Sensor()
# sens.key_name = "plant2_value"
# sens.device_id = 1
# sens.name = "Plant #2"
# sens.unit = "hpi"
# sens.group = 0
# sens.save()
# for rule in SensorRule.objects.all():
#     rule.delete()

# rule = SensorRule()
# rule.sensor_id = 1
# rule.threshold = 598
# rule.target_function = "water_plants"
# rule.comparison = "<"
# rule.save()

# delta = SensorDelta()
# delta.id = 1
# delta.sensor_id = 1
# delta.delta = 5.0
# delta.interval = 60 * 5
# delta.timestamp = datetime.now().replace(tzinfo=utc)
# delta.save()