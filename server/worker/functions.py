import logging
import time

from server.models import Threshold, Notification
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
                    Notification(threshold=threshold, message=message).save()
                    logger.debug(message)

            if threshold.max_value is not None:
                if latest_sensorvalue.value > threshold.max_value:
                    message = 'Threshold "%s" triggered (%s > %s)' % (
                        threshold.name, latest_sensorvalue.value, threshold.max_value)
                    Notification(threshold=threshold, message=message).save()
                    logger.debug(message)

        except SensorValue.DoesNotExist:
            logger.debug('No SensorValue found for Sensor #%s' %
                         threshold.sensor__id)
