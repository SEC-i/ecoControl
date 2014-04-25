import logging
from time import time

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST
from django.utils.timezone import utc

from functions import parse_configurations
from models import Device, DeviceConfiguration, Sensor, SensorValue
from helpers import create_json_response, create_json_response_from_QuerySet, parse_value
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
    if request.user.is_authenticated():
        return create_json_response(request, {"login": "active", "user": request.user.get_full_name()})
    else:
        return create_json_response(request, {"login": "inactive"})


@require_POST
def configure(request, persistent=True):
    configurations = parse_configurations(request.POST)
    DeviceConfiguration.objects.bulk_create(configurations)
    return create_json_response(request, {"status": "success"})


def forecast(request):
    if request.method == 'POST':
        configurations = parse_configurations(request.POST)
    else:
        configurations = DeviceConfiguration.objects.all()

    simulation_config = []
    for configuration in configurations:
        value = parse_value(configuration.value, configuration.value_type)
        # configuration tripel (device, variable, value)
        simulation_config.append(configuration.device_id, configuration.key, value)

    simulation = Simulation(simulation_config, time())
    simulation.forward(seconds=DEFAULT_FORECAST_INTERVAL, blocking=True)
    return create_json_response(request, simulation.get_measurements())
