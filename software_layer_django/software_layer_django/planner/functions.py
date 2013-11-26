import logging

from software_layer_django.models import Sensor, SensorEntry, SensorRule, SensorDelta, Task

logger = logging.getLogger('planner')

# crawl data and save sensor entries
def update_delta():
	logger.debug("update delta")
	


def check_rules():
	pass

def create_or_update_task():
	pass

