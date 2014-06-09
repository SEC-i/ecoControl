import logging
import time

from django.db import connection

from server.systems import get_initialized_scenario
from server.models import SensorValue, Threshold, Notification
import functions

logger = logging.getLogger('worker')


def check_thresholds():
    for threshold in Threshold.objects.all():
        try:
            latest_sensorvalue = SensorValue.objects.filter(
                sensor=threshold.sensor).latest('timestamp')

            min_threshold_triggered = threshold.min_value is not None and latest_sensorvalue.value < threshold.min_value
            max_threshold_triggered = threshold.max_value is not None and latest_sensorvalue.value > threshold.max_value

            if min_threshold_triggered or max_threshold_triggered:
                    try:
                        Notification.objects.get(
                            sensor_value=latest_sensorvalue)
                    except Notification.DoesNotExist:
                        if min_threshold_triggered:
                            target = threshold.min_value
                        elif max_threshold_triggered:
                            target = threshold.max_value
                        Notification.objects.create(
                            threshold=threshold, sensor_value=latest_sensorvalue, target=target)
        except SensorValue.DoesNotExist:
            logger.debug('No SensorValue found for Sensor #%s' %
                         threshold.sensor_id)


def execute_user_code():
    system_list = get_initialized_scenario()
    # user_function = get_user_function(system_list)
    # user_function(*system_list)


def refresh_views():
    logger.debug('Trigger views refresh')

    cursor = connection.cursor()
    cursor.execute('''REFRESH MATERIALIZED VIEW server_sensorvaluedaily;''')
    cursor.execute(
        '''REFRESH MATERIALIZED VIEW server_sensorvaluemonthlysum;''')
    cursor.execute(
        '''REFRESH MATERIALIZED VIEW server_sensorvaluemonthlyavg;''')

    logger.debug('Successfully refreshed views')
