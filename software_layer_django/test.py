import unittest
import os
import time
import datetime


class TestPlanner(unittest.TestCase):
    
    def setUp(self):
        #self.sensor = 
        for sensor in Sensor.objects.all():
            if sensor.key_name  == "plant2_value":
                self.sensor = sensor
                break
        print SensorEntry.objects.all().filter(sensor= sensor).order_by('-timestamp')[0] 
        planner.functions.update_delta()

    def testRule(self):
        rule = SensorRule()
        rule.sensor_id = self.sensor.id
        rule.threshold = 310
        rule.comparison ="<"
        rule.target_function = "test"
        rule.save()
        planner.functions.check_rules()

    def testDelta(self):
        sensor_delta = SensorDelta()
        sensor_delta = self.sensor.id
        sensor_delta.delta = 0.3
        sensor_delta.interval = 1 #seconds
        sensor_delta.timestamp = datetime.now()

        entry = SensorEntry()
        entry.sensor_id = self.sensor.id
        entry.value = 600
        entry.timestamp = datetime.now()

        time.sleep(1.1)

        entry2 = SensorEntry()
        entry2.sensor_id = self.sensor.id
        entry2.value = 700
        entry2.timestamp = datetime.now()

        planner.functions.update_delta()

        self.assertTrue(sensor_delta.delta > 0.3)

        entry.delete()
        entry2.delete()
        sensor_delta.delete()



        
    def tearDown(self):
        for rule in SensorRule.objects.filter(target_function= "test"):
            rule.delete()









if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "software_layer_django.settings")
    import planner
    from software_layer_django.webapi.models import Sensor, SensorEntry, SensorRule, SensorDelta, Task


    unittest.main()
