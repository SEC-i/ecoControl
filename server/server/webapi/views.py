import logging
from datetime import datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST
from django.utils.timezone import utc

from server.models import Actuator, Device, Sensor, SensorEntry
from functions import save_device_data, dispatch_device_request
from helpers import create_json_response, create_json_response_from_QuerySet, is_in_group, check_user_permissions

logger = logging.getLogger('webapi')

def index(request):
    return render(request, 'index.html')

def api_index(request):
    return create_json_response(request, { 'version': 0.1 })

@require_POST
def api_login(request):
    if 'username' in request.POST and 'password' in request.POST:
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
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

def api_logout(request):
    logout(request)
    return create_json_response(request, {"logout": "successful"})

def api_status(request):
    if request.user.is_authenticated():
        return create_json_response(request, {"login": "active", "user": request.user.get_full_name()})
    else:
        return create_json_response(request, {"login": "inactive"})

def show_item(request, item_id, model):
    check_user_permissions(request)

    item = list(model.objects.filter(id = int(item_id)).values())
    if not item:
        raise Http404('No %s matches the given query.' % queryset.model._meta.object_name)

    return create_json_response(request, item)

def list_items(request, model, limit, device_id=None):
    check_user_permissions(request)

    if limit is None:
        limit = 10

    if device_id is None:
        items = model.objects.all().order_by('name')[:int(limit)]
    else:
        items = model.objects.filter(device_id = int(device_id)).order_by('name')[:int(limit)]

    return create_json_response_from_QuerySet(request, items)

def list_entries(request, device_id, start, end):
    check_user_permissions(request)

    sensors = Sensor.objects.filter(device_id = int(device_id)).order_by('name')

    start_time = end_time = 0
    if start:
            start_time = datetime.fromtimestamp(int(start)/1000.0).replace(tzinfo=utc)
    if end:
            end_time = datetime.fromtimestamp(int(end)/1000.0).replace(tzinfo=utc)

    output = []
    for sensor in sensors:
        if not is_in_group(request.user, sensor.group):
            continue

        entries = SensorEntry.objects.filter(sensor__id = sensor.id).order_by('timestamp')
        if start:
            entries = entries.filter(timestamp__gte = start_time)

        if end:
            entries = entries.filter(timestamp__lte = end_time)

        output.append({
                'id': sensor.id,
                'name': sensor.name,
                'unit': sensor.unit,
                'data': list(entries.values_list('timestamp', 'value'))
            })

    return create_json_response(request, output)

@require_POST
def set_device(request, device_id):
    # check_user_permissions(request)

    device = get_object_or_404(Device, id = int(device_id))

    dispatch_device_request(device, request.POST.dict())
    logger.debug("Post request triggered by " + request.META['REMOTE_ADDR'])
    return create_json_response(request, {"status": "ok"})

@require_POST
def receive_device_data(request, device_id):
    # check_user_permissions(request)

    if 'data' in request.POST:
        # Get device to make sure that it exists
        device = get_object_or_404(Device, id = int(device_id))
        if save_device_data(device, request.POST['data']):
            return create_json_response(request, {"status": "ok"})

    return create_json_response(request, {"status": "failed"})
