import logging
from time import time
import json

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST
from django.utils.timezone import utc

from functions import perform_configuration
from models import Device, Configuration, DeviceConfiguration, Sensor, SensorValue
from helpers import create_json_response, create_json_response_from_QuerySet
from forecasting import Simulation


logger = logging.getLogger('django')

DEFAULT_FORECAST_INTERVAL = 3600.0 * 24 * 30  # one month


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

    simulation = Simulation(demo=True, initial_time=time())
    simulation.forward(60 * 60 * 24 * 30, blocking=True)
    simulation.start()

    return create_json_response(request, {"status": "success"})


def settings(request):
    return create_json_response(request, {"status": "success"})


def forecast(request):
    if request.method == 'POST':
        configurations = parse_configurations(request.POST)
        simulation = Simulation(configurations, initial_time=time())
    else:
        simulation = Simulation(initial_time=time())

    simulation.forward(seconds=DEFAULT_FORECAST_INTERVAL, blocking=True)
    return create_json_response(request, simulation.get_measurements())
