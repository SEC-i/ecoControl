import logging

from datetime import datetime, timedelta
from django.utils.timezone import utc
from server.models import  Sensor, SensorEntry, SensorRule, SensorDelta, Task

logger = logging.getLogger('planner')

# crawl data and save sensor entries
def update_delta():
    logger.debug("update delta")
    for sensor in Sensor.objects.all():
        # all rules to the sensor
        sensor_delta_list = SensorDelta.objects.all().filter(sensor_id= sensor.id)
        if len(sensor_delta_list) == 0:
            continue
        sensor_delta = sensor_delta_list[0]
        old_delta = float(sensor_delta.delta)
        
        newest_data = SensorEntry.objects.filter(sensor_id= sensor.id).order_by('-timestamp')[0]
        last_interval = datetime.now().replace(tzinfo=utc) - timedelta(seconds=int(sensor_delta.interval))
        #get the first dataSet from the data before the interval
        intervall_ago_data = SensorEntry.objects.filter(sensor_id= sensor.id, timestamp__lte= last_interval).order_by('-timestamp')
       
        current_delta  = float(newest_data.value) - float(intervall_ago_data[0].value)
        #weight the deltas
        sensor_delta.delta = 0.3 * old_delta + 0.7 * current_delta
        sensor_delta.save()




def check_rules():
    sensor_rules = SensorRule.objects.all()
    for rule in sensor_rules:
        #get newest value
        sensor_value = SensorEntry.objects.all().filter(sensor_id= rule.sensor_id).order_by('-timestamp')[0].value
        #build condition condition with comparison (f.e <,>,=,..)
        condition_string = str(sensor_value) + str(rule.comparison) + str(rule.threshold)
        if eval(condition_string) == True:
            create_or_update_task()
            return True #just for test
    return False

def create_or_update_task():
    logger.debug("updating or creating task")



def check_tasks():
    for task in Task.objects.all():
        if task.execution_timestamp <= datetime.now().replace(tzinfo=utc):
            logger.debug("execute task" + task.command)
