import logging

from datetime import datetime, timedelta

from software_layer_django.webapi.models import  Sensor, SensorEntry, SensorRule, SensorDelta, Task

logger = logging.getLogger('planner')

# crawl data and save sensor entries
def update_delta():
    logger.debug("update delta")
    for sensor in Sensor.objects.all():
        sensor_delta_list = SensorDelta.objects.all().filter(sensor_id= sensor.id)
        
        if len(sensor_delta_list) == 0:
            continue
        sensor_delta = sensor_delta_list[0]
        old_delta = sensor_delta.delta
        
        newest_data = SensorEntry.objects.all().filter(sensor_id= rule.sensor_id).order_by('-timestamp')[0]
        last_interval = datetime.today() - timedelta(seconds=sensor_delta.interval)
        
        intervall_ago_data = SensorEntry.objects.all().filter(timestamp__lte= last_interval).order_by('-timestamp')[0]

        current_delta  = newest_data - intervall_ago_data
        sensor_delta.delta = 0.3 * old_delta + 0.7 * current_delta




def check_rules():
    sensor_rules = SensorRule.objects.all()
    for rule in sensor_rules:
        #get newest value
        sensor_value = SensorEntry.objects.all().filter(sensor_id= rule.sensor_id).order_by('-timestamp')[0].value
        condition_string = str(sensor_value) + str(rule.comparison) + str(rule.threshold)
        print condition_string
        if eval(condition_string) == True:
            create_or_update_task()

def create_or_update_task():
    logger.debug("updating or creating task")



def check_tasks():
    for task in Task.objects.all():
        if task.execution_timestamp <= datetime.now():
            logger.debug("execute task" + task.command)
