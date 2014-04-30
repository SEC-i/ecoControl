import sys
import logging
from time import time
import json
from datetime import datetime, timedelta
import calendar

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST
from django.utils.timezone import utc
from django.db.models import Count, Min, Sum, Avg
from django.db import connection

from functions import perform_configuration
from models import Device, Configuration, DeviceConfiguration, Sensor, SensorValue
from helpers import create_json_response, create_json_response_from_QuerySet
from forecasting import Simulation


logger = logging.getLogger('django')

DEFAULT_FORECAST_INTERVAL = 3600.0 * 24 * 7  # one month


def index(request):
    return create_json_response(request, {'version': 0.2})


@require_POST
def login_user(request):
    if 'username' in request.POST and 'password' in request.POST:
        user = authenticate(username=request.POST[
                            'username'], password=request.POST['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                return create_json_response(request, {"login": "successful", "user": request.user.get_full_name()})
            else:
                return create_json_response(request, {"login": "disabled", "user": request.user.get_full_name()})
        else:
            return create_json_response(request, {"login": "invalid"})
    else:
        return create_json_response(request, {"login": "failed"})


def logout_user(request):
    logout(request)
    return create_json_response(request, {"logout": "successful"})


def status(request):
    system_status = Configuration.objects.get(key='system_status')

    if request.user.is_authenticated():
        return create_json_response(request, {"system": system_status.value, "login": "active", "user": request.user.get_full_name()})
    else:
        return create_json_response(request, {"system": system_status.value, "login": "inactive"})


@require_POST
def configure(request):
    perform_configuration(json.loads(request.body))
    system_status = Configuration.objects.get(key='system_status')
    system_status.value = 'running'
    system_status.save()

    simulation = Simulation(
        demo=True, initial_time=time() - DEFAULT_FORECAST_INTERVAL)
    if 'test' in sys.argv:
        simulation.forward(60 * 60, blocking=False)
    else:
        simulation.forward(DEFAULT_FORECAST_INTERVAL, blocking=False)
    simulation.start()

    return create_json_response(request, {"status": "success"})


def settings(request):
    return create_json_response(request, {"status": "success"})


def forecast(request):
    try:
        latest_value = SensorValue.objects.latest('timestamp')
        initial_time = calendar.timegm(latest_value.timestamp.utctimetuple())
    except SensorValue.DoesNotExist:
        initial_time = time()
    if request.method == 'POST':
        configurations = parse_configurations(request.POST)
        simulation = Simulation(configurations, initial_time=initial_time)
    else:
        simulation = Simulation(initial_time=initial_time)

    simulation.forward(seconds=DEFAULT_FORECAST_INTERVAL, blocking=True)
    output = []
    for sensor in simulation.measurements.sensors:
        output.append({
            'id': sensor.id,
            'device_id': sensor.device_id,
            'name': sensor.name,
            'unit': sensor.unit,
            'key': sensor.key,
            'data': list(simulation.measurements.data[sensor.id - 1])
        })

    return create_json_response(request, output)


def list_values(request, start):
    sensors = Sensor.objects.all()

    start_time = end_time = 0
    if start:
        start_time = datetime.fromtimestamp(
            int(start) / 1000.0).replace(tzinfo=utc)

    output = []
    for sensor in sensors:
        values = []
        for date in SensorValue.objects.filter(timestamp__gte=start_time).extra({'hour':"date_trunc('hour', timestamp)"}).values('hour').annotate(count=Count('id')):
            start_date = date['hour']
            end_date = start_date + timedelta(hours=1) - timedelta(seconds=1)
            # print SensorValue.objects.filter(sensor=sensor, timestamp__gte=date['hour'], timestamp__lte=end_date).query
            cursor = connection.cursor()
            cursor.execute('SELECT AVG(CAST(value AS decimal)) FROM "server_sensorvalue" WHERE ("server_sensorvalue"."sensor_id" = %s AND "server_sensorvalue"."timestamp" >= \'%s\'  AND "server_sensorvalue"."timestamp" <= \'%s\' ) GROUP BY  "server_sensorvalue"."sensor_id"' % (sensor.id, start_date, end_date))
            values.append([calendar.timegm(start_date.utctimetuple()) * 1000, float(cursor.fetchone()[0])])

        output.append({
            'id': sensor.id,
            'device_id': sensor.device_id,
            'name': sensor.name,
            'unit': sensor.unit,
            'key': sensor.key,
            'data': values
        })

    return create_json_response(request, output)


def list_sensors(request):
    sensors = Sensor.objects.all()

    return create_json_response_from_QuerySet(request, sensors)
