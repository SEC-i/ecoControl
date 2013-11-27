import logging
from datetime import datetime
from software_layer_django.models import Sensor, SensorEntry, SensorRule, SensorDelta, Task

logger = logging.getLogger('planner')

# crawl data and save sensor entries
def update_delta():
    logger.debug("update delta")



def check_rules():
    sensor_rules = SensorRule.Objects.all()
    for rule in sensor_rules:
        sensor_value = SensorEntry.Objects.all().filter(sensor= rule.Sensor).order_by('-timestamp')[0]
        condition_string = str(sensor_value) + str(rule.comparison) + str(rule.threshold)
        if eval(condition_string) == True:
            create_or_update_task()

def create_or_update_task():
    logger.debug("updating or creating task")



def check_tasks():
    for task in Task.Objects.all():
        if task.execution_timestamp <= datetime.now():
            logger.debug("execute task" + task.command)