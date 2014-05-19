import sys
import logging
from time import time
from datetime import date
import json

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST
from django.views.decorators.debug import sensitive_post_parameters
from django.utils.timezone import utc
from django.db.models import Count, Min, Sum, Avg
from django.db import connection

from server.models import Device, Configuration, DeviceConfiguration, Sensor, SensorValue, SensorValueHourly, SensorValueDaily, SensorValueMonthlySum, SensorValueMonthlyAvg, Threshold, Notification
from server.functions import get_configuration, get_past_time
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
                  .values('date').annotate(total_sum=Sum('sum')))
    if len(totals) > 0:
        output = []
        for total in totals:
            output.append({
                'date': total['date'],
                'total': round(total['total_sum'] * multiply_by, 2)
            })
        return create_json_response(request, output)
    return create_json_response(request, {"status": "failed"})


def get_sums(request, sensor_id=None, year=None):
    if year is None:
        start = date(date.today().year, 1, 1)
        end = date(date.today().year, 12, 31)
    else:
        start = date(int(year), 1, 1)
        end = date(int(year), 12, 31)

    sensorvaluemonthlysum = SensorValueMonthlySum.objects.filter(date__gte=start, date__lte=end)

    if sensor_id is None:
        output = {}
        for sensor in Sensor.objects.all().values_list('id', flat=True):
            output[sensor] = list(sensorvaluemonthlysum.filter(
                sensor_id=sensor).values('date').annotate(total=Sum('sum')).order_by('date'))
    else:
        output = list(sensorvaluemonthlysum.filter(
            sensor_id=sensor_id).values('date').annotate(total=Sum('sum')).order_by('date'))

    return create_json_response(request, output)


def get_avgs(request, sensor_id=None, year=None):
    if year is None:
        start = date(date.today().year, 1, 1)
        end = date(date.today().year, 12, 31)
    else:
        start = date(int(year), 1, 1)
        end = date(int(year), 12, 31)

    sensorvaluemonthlyavg = SensorValueMonthlyAvg.objects.filter(date__gte=start, date__lte=end)

    if sensor_id is None:
        output = {}
        for sensor in Sensor.objects.all().values_list('id', flat=True):
            output[sensor] = list(sensorvaluemonthlyavg.filter(
                sensor_id=sensor).values('date').annotate(total=Avg('avg')).order_by('date'))
    else:
        output = list(sensorvaluemonthlyavg.filter(
            sensor_id=sensor_id).values('date').annotate(total=Avg('avg')).order_by('date'))

    return create_json_response(request, output)


def get_sensorvalue_history_list(request):
    cursor = connection.cursor()
    cursor.execute('''SELECT DISTINCT date_part('year', server_sensorvaluemonthlysum.date) as year FROM server_sensorvaluemonthlysum ORDER BY year DESC''')
    
    output = [int(x[0]) for x in cursor.fetchall()]
    return create_json_response(request, output)
