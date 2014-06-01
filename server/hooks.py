import sys
import logging
from time import time
import json

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.debug import sensitive_post_parameters
from django.utils.timezone import utc
from django.db.models import Count, Min, Sum, Avg
from django.db import connection

import functions
from models import Device, Configuration, DeviceConfiguration, Sensor, SensorValue, SensorValueHourly, SensorValueDaily, SensorValueMonthlySum, Threshold, Notification
from helpers import create_json_response, is_member


logger = logging.getLogger('django')


def index(request):
    return create_json_response({'version': 0.2}, request)


@require_POST
@sensitive_post_parameters('password')
def login_user(request):
    if 'username' in request.POST and 'password' in request.POST:
        user = authenticate(username=request.POST[
                            'username'], password=request.POST['password'])
        if user is not None:
            if user.is_active:
                login(request, user)
                return create_json_response({"login": "successful", "user": request.user.get_full_name()}, request)
            else:
                return create_json_response({"login": "disabled", "user": request.user.get_full_name()}, request)
        else:
            return create_json_response({"login": "invalid"}, request)
    else:
        return create_json_response({"login": "failed"}, request)


def logout_user(request):
    logout(request)
    return create_json_response({"logout": "successful"}, request)


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

    return create_json_response(dict(output), request)


@require_POST
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response[
        'Content-Disposition'] = 'attachment; filename="export_%s.csv"' % time()

    if 'csv' in request.POST:
        response.write(request.POST['csv'])

    return response


def list_settings(request):
    output = []
    output += functions.get_configurations()
    output += functions.get_device_configurations()
    return create_json_response(dict(output), request)


def list_sensors(request):
    sensors = Sensor.objects.filter(in_diagram=True).values(
        'id', 'name', 'unit', 'device__name', 'aggregate_sum', 'aggregate_avg')

    # rename device__name to device for convenience
    output = [{'id': x['id'], 'name': x['name'], 'unit': x['unit'], 'device': x['device__name'], 'sum': x['aggregate_sum'], 'avg': x['aggregate_avg']}
              for x in sensors]

    return create_json_response(output, request)


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

    return create_json_response(output, request)
