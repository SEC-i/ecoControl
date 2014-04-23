import logging

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST
from django.utils.timezone import utc

from models import Device, DeviceConfiguration, Sensor, SensorValue
from helpers import create_json_response, create_json_response_from_QuerySet


logger = logging.getLogger('django')


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


@require_POST
def configure(request):
    configurations = []
    if 'config' in request.POST:
        for config_data in request.POST['config']:
            for (device_name, key, value, value_type) in config_data:
                try:
                    device = Device.objects.get(name=device_name)
                except ObjectDoesNotExist:
                    device = Device(name=device_name)
                    device.save()

                configurations.append(
                    DeviceConfiguration(device=device, key=key, value=value, value_type=value_type))

    DeviceConfiguration.objects.bulk_create(configurations)

    return create_json_response(request, {"status": "success"})


def forecast(request):
    if request.method == 'POST':
        # create simulation with modified configuration
        pass
    else:
        # create simulation with original configuration
        pass

    return create_json_response(request, {"data": "measurements"})
