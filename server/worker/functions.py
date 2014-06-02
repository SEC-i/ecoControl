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

            if threshold.min_value is not None:
                if latest_sensorvalue.value < threshold.min_value:
                    message = 'Threshold "%s" triggered (%s < %s)' % (
                        threshold.name, latest_sensorvalue.value, threshold.min_value)
                    Notification(threshold=threshold, message=message,
                                 category=Notification.Danger, show_manager=threshold.show_manager).save()
                    logger.debug(message)

            if threshold.max_value is not None:
                if latest_sensorvalue.value > threshold.max_value:
                    message = 'Threshold "%s" triggered (%s > %s)' % (
                        threshold.name, latest_sensorvalue.value, threshold.max_value)
                    Notification(threshold=threshold, message=message,
                                 category=Notification.Danger, show_manager=threshold.show_manager).save()
                    logger.debug(message)

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