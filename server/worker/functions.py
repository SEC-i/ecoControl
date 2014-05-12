import logging
import time

from server.models import Threshold
import functions

logger = logging.getLogger('worker')


def check_thresholds():
    for threshold in Threshold.objects.all():
        try:
            latest_sensorvalue = SensorValue.objects.filter(
                sensor=threshold.sensor).latest('timestamp')

            if threshold.min_value is not None:
                if latest_sensorvalue.value < threshold.min_value:
                    logger.debug('Threshold "%s" triggered (%s < %s)' %
                                 (threshold.name, latest_sensorvalue.value, threshold.min_value))

            if threshold.max_value is not None:
                if latest_sensorvalue.value > threshold.max_value:
                    logger.debug('Threshold "%s" triggered (%s > %s)' %
                                 (threshold.name, latest_sensorvalue.value, threshold.max_value))

        except SensorValue.DoesNotExist:
            logger.debug('No SensorValue found for Sensor #%s' %
                         threshold.sensor__id)
