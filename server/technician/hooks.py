import sys
import os
import logging
from time import time
import json
import calendar
from datetime import datetime, timedelta
import dateutil.relativedelta

from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST
from django.views.decorators.debug import sensitive_post_parameters
from django.utils.timezone import utc
from django.db.models import Count, Min, Sum, Avg
from django.db import connection
from django.core.cache import cache
from django.core.exceptions import PermissionDenied

from server.models import Device, Configuration, DeviceConfiguration, Sensor, SensorValue, SensorValueHourly, SensorValueDaily, SensorValueMonthlySum, Threshold, Notification
from server.helpers import create_json_response
from server.functions import get_device_configurations, get_past_time
from server.systems import perform_configuration
from server.forecasting import get_forecast, DemoSimulation
import functions
from server.forecasting.forecasting.auto_optimization import auto_forecast,\
    auto_optimize

logger = logging.getLogger('django')

DEMO_SIMULATION = None

##testing optimization
def test_auto(request):
    config = DeviceConfiguration.objects.all()
    measurements = auto_optimize(config)
    return create_json_response(measurements, request)

####

def handle_snippets(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    if request.method == 'POST':
        data = json.loads(request.body)
        if 'name' in data:
            if 'code' in data:
                return create_json_response(functions.save_snippet(data['name'], data['code']), request)
            else:
                return create_json_response(functions.get_snippet_code(data['name']), request)

    return create_json_response(functions.get_snippet_list(), request)


def handle_code(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    if request.method == 'POST':
        data = json.loads(request.body)
        if 'code' in data:
            return create_json_response(functions.apply_snippet(data['code']), request)

    return create_json_response(functions.get_current_snippet(), request)


@require_POST
def configure(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    cache.clear()
    perform_configuration(json.loads(request.body))
    return create_json_response({"status": "success"}, request)


@require_POST
def start_system(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    data = json.loads(request.body)

    system_status = Configuration.objects.get(key='system_status')
    system_mode = Configuration.objects.get(key='system_mode')

    if system_status.value != 'running':
        system_status.value = 'running'
        system_status.save()
        if 'demo' in data and data['demo'] == '1':
            system_mode.value = 'demo'
            system_mode.save()
            DEMO_SIMULATION = DemoSimulation.start_or_get()
            return create_json_response({"status": "demo started"}, request)
        system_mode.value = 'normal'
        system_mode.save()
        return create_json_response({"status": "system started without demo"}, request)

    return create_json_response({"status": "system already running"}, request)


def get_tunable_device_configurations(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    output = dict(get_device_configurations(tunable=True))
    return create_json_response(output, request)


def forecast(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    try:
        latest_timestamp = get_past_time()
        initial_time = calendar.timegm(latest_timestamp.timetuple())
    except SensorValue.DoesNotExist:
        initial_time = time()

    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            code = None
            if 'code' in data:
                code = data['code']

            configurations = None
            if 'configurations' in data:
                configurations = functions.get_modified_configurations(data['configurations'])

            output = get_forecast(initial_time, configurations=configurations, code=code)
        except ValueError:
            return create_json_response({"status": "failed"})
    else:
        output = get_forecast(initial_time)

    return create_json_response(output, request)


@require_POST
def forward(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    data = json.loads(request.body)
    forward_time = float(data['forward_time']) * 24 * 3600

    demo_sim = DemoSimulation.start_or_get()

    if demo_sim.env.forward > 0:
        return create_json_response(request, "simulation is still forwarding", request)

    demo_sim.forward_demo(forward_time)

    return create_json_response(request, "ok", request)


def list_thresholds(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    thresholds = Threshold.objects.extra(select={
        'sensor_name': 'SELECT name FROM server_sensor WHERE id = sensor_id'
    }).order_by('id')

    return create_json_response(list(thresholds.values()), request)


@require_POST
def handle_threshold(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    data = json.loads(request.body)
    if 'id' in data:

        threshold = Threshold.objects.get(id=data['id'])
        if threshold is not None:
            if 'delete' in data:
                threshold.delete()
            else:
                print data
                if 'name' in data:
                    threshold.name = data['name']
                if 'sensor_id' in data:
                    threshold.sensor_id = int(data['sensor_id'])
                if 'min_value' in data:
                    if data['min_value'] == '':
                        threshold.min_value = None
                    else:
                        try:
                            threshold.min_value = float(data['min_value'])
                        except ValueError:
                            pass
                if 'max_value' in data and data['max_value'] != '':
                    if data['max_value'] == '':
                        threshold.max_value = None
                    else:
                        try:
                            threshold.max_value = float(data['max_value'])
                        except ValueError:
                            pass
                if 'category' in data:
                    threshold.category = int(data['category'])
                if 'show_manager' in data:
                    threshold.show_manager = True if data[
                        'show_manager'] == '1' else False
                threshold.save()
            return create_json_response({"status": "success"}, request)
    else:
        if all(x in data for x in ['name', 'sensor_id', 'min_value', 'max_value', 'category']):
            threshold = Threshold(name=data['name'], sensor_id=int(
                data['sensor_id']), category=int(data['category']))
            try:
                threshold.min_value = float(data['min_value'])
            except ValueError:
                pass
            try:
                threshold.max_value = float(data['max_value'])
            except ValueError:
                pass
            threshold.save()
            return create_json_response({"status": "success"}, request)

    return create_json_response({"status": "failed"}, request)


def list_sensor_values(request, start, accuracy='hour'):
    if not request.user.is_superuser:
        raise PermissionDenied

    if start is None:
        if accuracy == 'hour':
            start = get_past_time(months=1, use_view=True)
        else:
            start = get_past_time(years=1, use_view=True)
    else:
        start = datetime.utcfromtimestamp(int(start)).replace(tzinfo=utc)
    output = []

    if accuracy == 'hour':
        sensor_values = SensorValueHourly.objects.\
            filter(sensor__in_diagram=True).\
            select_related(
                'sensor__name', 'sensor__unit', 'sensor__key', 'sensor__device__name')
    else:
        sensor_values = SensorValueDaily.objects.\
            filter(date__gte=datetime.date(start), sensor__in_diagram=True).\
            select_related(
                'sensor__name', 'sensor__unit', 'sensor__key', 'sensor__device__name')

    values = {}
    output = {}
    for value in sensor_values:
        # Save sensor data
        if value.sensor.id not in values.keys():
            values[value.sensor.id] = []
            output[value.sensor.id] = {
                'id': value.sensor.id,
                'device': value.sensor.device.name,
                'name': value.sensor.name,
                'unit': value.sensor.unit,
                'key': value.sensor.key,
            }
        # Save sensor values
        if accuracy == 'hour':
            values[value.sensor.id].append((value.timestamp, value.value))
        else:
            values[value.sensor.id].append((value.date, value.value))

    for sensor_id in output.keys():
        output[sensor_id]['data'] = values[sensor_id]

    return create_json_response(output.values(), request)


def get_statistics(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    end = get_past_time(use_view=True)
    start = end + dateutil.relativedelta.relativedelta(months=-1)

    output = []
    output += functions.get_statistics_for_cogeneration_unit(start, end)
    output += functions.get_statistics_for_peak_load_boiler(start, end)
    output += functions.get_statistics_for_thermal_consumer(start, end)
    output += functions.get_statistics_for_electrical_consumer(start, end)
    output += functions.get_statistics_for_power_meter(start, end)

    return create_json_response(output, request)


def get_monthly_statistics(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    end = get_past_time(use_view=True)
    start = end + dateutil.relativedelta.relativedelta(years=-1)

    sensor_values = SensorValueMonthlySum.objects.filter(
        date__gte=start, date__lte=end)

    months = sensor_values.extra({'month': "date_trunc('month', date)"}).values(
        'month').annotate(count=Count('id'))
    output = []
    for month in months:
        month_start = month['month']
        month_end = month['month'] + dateutil.relativedelta.relativedelta(
            months=1) - timedelta(days=1)
        month_data = []
        month_data += functions.get_statistics_for_cogeneration_unit(
            month_start, month_end)
        month_data += functions.get_statistics_for_peak_load_boiler(
            month_start, month_end)
        month_data += functions.get_statistics_for_thermal_consumer(
            month_start, month_end)
        month_data += functions.get_statistics_for_electrical_consumer(
            month_start, month_end)
        month_data += functions.get_statistics_for_power_meter(
            month_start, month_end)

        output.append(month_data)

    return create_json_response(output, request)


def live_data(request):
    if not request.user.is_superuser:
        raise PermissionDenied

    return create_json_response(functions.get_live_data(), request)
