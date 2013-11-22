import logging
from urllib import urlopen, urlencode

from django.shortcuts import render
from django.http import HttpResponse

from helpers import create_json_response, create_json_response_for_model, create_json_response_for_models
from models import Device, Sensor, SensorEntry

logger = logging.getLogger('webapi')

def index(request):
    return create_json_response({ 'version':0.1 })
    
def show_device(request, device_id):
    try:
        device = Device.objects.get(id = int(device_id))
        return create_json_response_for_model(device)
    except ValueError:
        logger.error("ValueError")
        return HttpResponse("ValueError")

def list_devices(request, limit):
    try:
        devices = Device.objects.all()
        if not limit:
            limit = 10
        devices = devices[:int(limit)]
            
        return create_json_response_for_models(devices)
    except ValueError:
        logger.error("ValueError")
        return HttpResponse("ValueError")
    
def list_sensors(request, device_id, limit):
    try:
        device_id = int(device_id)
        sensors = Sensor.objects.all().filter(device_id = device_id)
        if not limit:
            limit = 10
        sensors = sensors[:int(limit)]

        return create_json_response_for_models(sensors)
    except ValueError:
        logger.error("ValueError")
        return HttpResponse("ValueError")
        
def show_sensor(request, sensor_id):
    try:
        sensor = Sensor.objects.get(id = int(sensor_id))
        return create_json_response_for_model(sensor)
    except ValueError:
        logger.error("ValueError")
        return HttpResponse("ValueError")

    
def list_sensor_entries(request, sensor_id, limit):
    try:
        sensor_id = int(sensor_id)
        entries = SensorEntry.objects.all().filter(sensor_id = sensor_id)
        if not limit:
            limit = 10
        entries = entries[:int(limit)]
            
        return create_json_response_for_models(entries)
    except ValueError:
        logger.error("ValueError")
        return HttpResponse("ValueError")
    
def list_entries(request, device_id, limit):
    try:
        device_id = int(device_id)
        sensors = Sensor.objects.all().filter(device_id = device_id)
        if not limit:
            limit = 10
        entries = SensorEntry.objects.all().filter(sensor__in = sensors).order_by('-timestamp')[:limit]
        
        return create_json_response_for_models(entries)
    except ValueError:
        logger.error("ValueError")
        return HttpResponse("ValueError")

def show_entry(request, entry_id):
    try:
        entry = SensorEntry.objects.get(id = int(entry_id))
        return create_json_response_for_model(entry)
    except ValueError:
        logger.error("ValueError")
        return HttpResponse("ValueError")

def set_device(request, device_id):
    workload = '100'
    
    if request.method == 'POST':
        workload = request.POST['workload']
        
    postData = [('workload', workload)]
    urlopen("http://172.16.64.130:9000/device/0/set", urlencode(postData))
    
    logger.debug("Post request triggered by " + request.META['REMOTE_ADDR'])

    return create_json_response({"status": "ok"})
