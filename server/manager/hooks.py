import sys
import logging
from time import time
import json

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST
from django.views.decorators.debug import sensitive_post_parameters
from django.utils.timezone import utc
from django.db.models import Count, Min, Sum, Avg
from django.db import connection

from server.models import Device, Configuration, DeviceConfiguration, Sensor, SensorValue, SensorValueHourly, SensorValueDaily, SensorValueMonthly, Threshold, Notification
from server.functions import get_configuration
from server.helpers import create_json_response, create_json_response_from_QuerySet


logger = logging.getLogger('django')


def get_totals(request):
    return create_json_response(request, {"status": "success"})


def get_infeed(request):
    sensor = Sensor.objects.get(device__device_type=Device.PM, key='fed_in_electricity')
    if sensor is not None:
        feed_in_reward = get_configuration('feed_in_reward')
        totals = list(SensorValueMonthly.objects.filter(sensor=sensor))

        output = []
        for total in totals:
            output.append({
                'timestamp': total.timestamp,
                'total': round(total.sum * feed_in_reward, 2)
            }) 

        return create_json_response(request, output)

    return create_json_response(request, {"status": "failed"})


def get_purchase(request):
    sensor = Sensor.objects.get(device__device_type=Device.PM, key='purchased')
    if sensor is not None:
        feed_in_reward = get_configuration('feed_in_reward')
        totals = list(SensorValueMonthly.objects.filter(sensor=sensor))

        output = []
        for total in totals:
            output.append({
                'timestamp': total.timestamp,
                'total': round(total.sum * feed_in_reward, 2)
            }) 

        return create_json_response(request, output)

    return create_json_response(request, {"status": "failed"})


def get_thermal_consumption(request):
    return create_json_response(request, {"status": "success"})


def get_electrical_consumption(request):
    return create_json_response(request, {"status": "success"})


def get_maintenance_costs(request):
    return create_json_response(request, {"status": "success"})
