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
    feed_in_reward = get_configuration('feed_in_reward')
    return get_sum_response(request, Device.PM, 'fed_in_electricity', feed_in_reward)


def get_purchase(request):
    electrical_costs = get_configuration('electrical_costs')
    return get_sum_response(request, Device.PM, 'purchased', electrical_costs)


def get_thermal_consumption(request):
    return get_sum_response(request, Device.TC, 'get_consumption_power')


def get_warmwater_consumption(request):
    return get_sum_response(request, Device.TC, 'get_warmwater_consumption_power')


def get_electrical_consumption(request):
    return get_sum_response(request, Device.EC, 'get_consumption_power')


def get_maintenance_costs(request):
    return create_json_response(request, {"status": "success"})


def get_cu_consumption(request):
    return get_sum_response(request, Device.CU, 'current_gas_consumption')


def get_plb_consumption(request):
    return get_sum_response(request, Device.PLB, 'current_gas_consumption')


def get_sum_response(request, device_type, key, multiply_by=1):
    sensors = Sensor.objects.filter(
        device__device_type=device_type, key=key).values_list('id', flat=True)
    totals = list(SensorValueMonthly.objects.filter(sensor_id__in=sensors)
                  .values('timestamp').annotate(total_sum=Sum('sum')))
    if len(totals) > 0:
        output = []
        for total in totals:
            output.append({
                'timestamp': total['timestamp'],
                'total': round(total['total_sum'] * multiply_by, 2)
            })
        return create_json_response(request, output)
    return create_json_response(request, {"status": "failed"})
