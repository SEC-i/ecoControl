import logging
from time import time

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST
from django.utils.timezone import utc

from models import Device, DeviceConfiguration, Sensor, SensorValue
from helpers import create_json_response, create_json_response_from_QuerySet, parse_value
from forecasting import Simulation


logger = logging.getLogger('django')

DEFAULT_FORECAST_INTERVAL = 3600.0 * 24 * 30 # one month


def index(request):
    return create_json_response(request, {'version': 0.2})

@require_POST
def login(request):
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

def logout(request):
    logout(request)
    return create_json_response(request, {"logout": "successful"})

def status(request):
    if request.user.is_authenticated():
        return create_json_response(request, {"login": "active", "user": request.user.get_full_name()})
    else:
        return create_json_response(request, {"login": "inactive"})

def install_devices(request):
    devices = []
    devices.append(Device(name='Heat Storage', type=Device.HS))
    devices.append(Device(name='Power Meter', type=Device.PM))
    devices.append(Device(name='Cogeneration Unit', type=Device.CU))
    devices.append(Device(name='Peak Load Boiler', type=Device.PLB))
    devices.append(Device(name='Thermal Consumer', type=Device.TC))
    devices.append(Device(name='Electrical Consumer', type=Device.EC))
    devices.append(Device(name='Code Executer', type=Device.CE))
    
    Device.objects.bulk_create(devices)
    return create_json_response(request, {"status": "default setup created"})

@require_POST
def configure(request, persistent=True):
    """
    In persistent mode the configuration is stored in the database.
    Otherwise no changes will be saved and it returns the configuration
    """
    configurations = []
    if 'config' in request.POST:
        for config_data in request.POST['config']:
            for (device_name, key, value, value_type) in config_data:
                try:
                    device = Device.objects.get(name=device_name)
                except ObjectDoesNotExist:
                    logger.error("Unknown device " + str(device_name))
                    continue
                configurations.append(
                    DeviceConfiguration(device=device, key=key, value=value, value_type=value_type))

    if persistent:
        DeviceConfiguration.objects.bulk_create(configurations)

    if persistent:
        return create_json_response(request, {"status": "success"})
    else:
        return configurations

def forecast(request):
    if request.method == 'POST':
        configurations = configure(request, False)
    else:
        configurations = DeviceConfiguration.objects.all()

    simulation_config = []
    for configuration in configurations:
        # configuration tripel (device, variable, value)
        value = parse_value(configuration.value, configuration.value_type)
        simulation_config.append(
            (str(configuration.device.type), configuration.key, value))

    simulation = Simulation(simulation_config, time())
    simulation.forward(seconds=DEFAULT_FORECAST_INTERVAL, blocking=True)
    return create_json_response(request, simulation.get_measurements())
