import sys
import logging
from time import time
import json
from datetime import datetime, timedelta
import calendar
import dateutil.relativedelta

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.debug import sensitive_post_parameters
from django.utils.timezone import utc
from django.db.models import Count, Min, Sum, Avg
from django.db import connection
from django.core.cache import cache
import cProfile


import functions
from models import Device, Configuration, DeviceConfiguration, Sensor, SensorValue, SensorValueHourly, SensorValueDaily, SensorValueMonthlySum, Threshold, Notification
from helpers import create_json_response, create_json_response_from_QuerySet, is_member, DemoSimulation
from forecasting import Simulation
from filecmp import demo


logger = logging.getLogger('django')

DEFAULT_FORECAST_INTERVAL = 3600.0 * 24 * 14
DEMO_SIMULATION = None


def index(request):
    return create_json_response({'version': 0.2})


@require_POST
@sensitive_post_parameters('password')
def login_user(request):
    if 'username' in request.POST and 'password' in request.POST:
        user = authenticate(username=request.POST[
                            'username'], password=request.POST['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                return create_json_response({"login": "successful", "user": request.user.get_full_name()})
            else:
                return create_json_response({"login": "disabled", "user": request.user.get_full_name()})
        else:
            return create_json_response({"login": "invalid"})
    else:
        return create_json_response({"login": "failed"})


def logout_user(request):
    logout(request)
    return create_json_response({"logout": "successful"})


def status(request):

    output = [("system_status", functions.get_configuration("system_status"))]
    output.append(("system_mode", functions.get_configuration("system_mode")))

    if request.user.is_authenticated():
        output.append(("login", "active"))
        output.append(("user", request.user.get_full_name()))
        output.append(("technician", is_member(request.user, 'Technician')))
        output.append(("manager", is_member(request.user, 'Manager')))
    else:
        output.append(("login", "inactive"))

    return create_json_response(dict(output))

@require_POST
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response[
        'Content-Disposition'] = 'attachment; filename="export_%s.csv"' % time()

    if 'csv' in request.POST:
        response.write(request.POST['csv'])

    return response

@require_POST
def configure(request):
    cache.clear()
    functions.perform_configuration(json.loads(request.body))
    return create_json_response({"status": "success"})


@require_POST
def start_system(request):
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
            return create_json_response({"status": "demo started"})
        system_mode.value = 'normal'
        system_mode.save()
        return create_json_response({"status": "system started without demo"})

    return create_json_response({"status": "system already running"})


def settings(request):
    output = []
    output += functions.get_configurations()
    output += functions.get_device_configurations()
    return create_json_response(dict(output))


def get_tunable_device_configurations(request):
    output = dict(functions.get_device_configurations(tunable=True))
    return create_json_response(output)


def forecast(request):
    try:
        latest_timestamp = functions.get_past_time()
        initial_time = calendar.timegm(latest_timestamp.timetuple())
    except SensorValue.DoesNotExist:
        initial_time = time()
    if request.method == 'POST':
        configurations = functions.get_modified_configurations(
            json.loads(request.body))
        simulation = Simulation(initial_time, configurations)
    else:
        simulation = Simulation(initial_time)

    simulation.forward(seconds=DEFAULT_FORECAST_INTERVAL, blocking=True)

    return create_json_response(simulation.measurements.get())

@require_POST
def forward(request):
    data = json.loads(request.body)
    forward_time = float(data['forward_time']) * 24 * 3600
    
    demo_sim = DemoSimulation.start_or_get()
    
    if demo_sim.env.forward > 0:
        return create_json_response(request, "simulation is still forwarding")
    
    start = demo_sim.env.now
    demo_sim.forward_demo(seconds=forward_time, blocking=True)
    
    return create_json_response(request, "ok")


def get_statistics(request):
    end = functions.get_past_time(use_view=True)
    start = end + dateutil.relativedelta.relativedelta(months=-1)

    output = []
    output += functions.get_statistics_for_cogeneration_unit(start, end)
    output += functions.get_statistics_for_peak_load_boiler(start, end)
    output += functions.get_statistics_for_thermal_consumer(start, end)
    output += functions.get_statistics_for_electrical_consumer(start, end)
    output += functions.get_statistics_for_power_meter(start, end)

    return create_json_response(output)


def get_monthly_statistics(request):
    end = functions.get_past_time(use_view=True)
    start = end + dateutil.relativedelta.relativedelta(years=-1)

    sensor_values = SensorValueMonthlySum.objects.filter(date__gte=start, date__lte=end)

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

    return create_json_response(output)


def list_values(request, start, accuracy='hour'):

    if start is None:
        start = functions.get_past_time(months=1, use_view=True)
    else:
        start = datetime.fromtimestamp(int(start)).replace(tzinfo=utc)
    output = []

    if accuracy == 'hour':
        sensor_values = SensorValueHourly.objects.\
            filter(timestamp__gte=start, sensor__in_diagram=True).\
            select_related(
                'sensor__name', 'sensor__unit', 'sensor__key', 'sensor__device__name')
    elif accuracy == 'day':
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
        values[value.sensor.id].append((value.timestamp, value.value))

    for sensor_id in output.keys():
        output[sensor_id]['data'] = values[sensor_id]

    return create_json_response(output.values())


def list_sensors(request):
    sensors = Sensor.objects.filter(in_diagram=True).values(
        'id', 'name', 'unit', 'device__name', 'aggregate_sum', 'aggregate_avg')

    # rename device__name to device for convenience
    output = [{'id': x['id'], 'name': x['name'], 'unit': x['unit'], 'device': x['device__name'], 'sum': x['aggregate_sum'], 'avg': x['aggregate_avg']}
              for x in sensors]

    return create_json_response(output)


def live_data(request):
    return create_json_response(functions.get_live_data())


def list_thresholds(request):
    thresholds = Threshold.objects.extra(select={
        'sensor_name': 'SELECT name FROM server_sensor WHERE id = sensor_id'
    }).order_by('id')

    return create_json_response_from_QuerySet(thresholds)


@require_POST
def handle_threshold(request):
    data = json.loads(request.body)
    if 'id' in data:
        if not is_member(request.user, 'Technician'):
            return create_json_response({"status": "not a technician"})

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
            return create_json_response({"status": "success"})
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
            return create_json_response({"status": "success"})

    return create_json_response({"status": "failed"})


def list_notifications(request, start, end):
    start = 0 if start is None else start
    end = 25 if end is None else end

    if is_member(request.user, 'Technician'):
        notifications = Notification.objects.all()
    else:
        notifications = Notification.objects.filter(show_manager=True)

    output = {
        'total': len(notifications),
        'notifications': list(notifications.order_by('-timestamp')[int(start):int(end)].values())
    }

    return create_json_response(output)
