import logging
from datetime import datetime

from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist

from helpers import create_json_response, create_json_response_for_model, create_json_response_for_models
from models import Device, Sensor, SensorEntry

logger = logging.getLogger('webapi')

def index(request):
    return HttpResponse("BP2013H1")

def api_index(request):
    return create_json_response({ 'version':0.1 })
    
def show_device(request, device_id):
    try:
        device = Device.objects.get(id = int(device_id))
        return create_json_response_for_model(device)
    except ValueError:
        logger.error("ValueError")
        return HttpResponse("ValueError")
    except ObjectDoesNotExist:
        logger.warning("Device #" + device_id + " does not exists")
        return HttpResponse("Device #" + device_id + " does not exists")

def list_devices(request, limit):
    try:
        if not limit:
            limit = 10
        devices = Device.objects.all()[:int(limit)]
            
        return create_json_response_for_models(devices)
    except ValueError:
        logger.error("ValueError")
        return HttpResponse("ValueError")
    
def list_sensors(request, device_id, limit):
    try:
        if not limit:
            limit = 10
        device_id = int(device_id)
        sensors = Sensor.objects.all().filter(device_id = device_id)[:int(limit)]

        return create_json_response_for_models(sensors)
    except ValueError:
        logger.error("ValueError")
        return HttpResponse("ValueError")
    except ObjectDoesNotExist:
        logger.warning("Device #" + device_id + " does not exists")
        return HttpResponse("Device #" + device_id + " does not exists")
        
def show_sensor(request, sensor_id):
    try:
        sensor = Sensor.objects.get(id = int(sensor_id))
        return create_json_response_for_model(sensor)
    except ValueError:
        logger.error("ValueError")
        return HttpResponse("ValueError")
    except ObjectDoesNotExist:
        logger.warning("Sensor #" + sensor_id + " does not exists")
        return HttpResponse("Sensor #" + sensor_id + " does not exists")

    
def list_sensor_entries(request, sensor_id, limit):
    try:
        sensor_id = int(sensor_id)
        if not limit:
            limit = 10
        entries = SensorEntry.objects.all().filter(sensor_id = sensor_id)[:int(limit)]
            
        return create_json_response_for_models(entries)
    except ValueError:
        logger.error("ValueError")
        return HttpResponse("ValueError")
    except ObjectDoesNotExist:
        logger.warning("Sensor #" + sensor_id + " does not exists")
        return HttpResponse("Sensor #" + sensor_id + " does not exists")
    
def list_entries(request, device_id, start, limit):
    try:
        device_id = int(device_id)
        sensors = Sensor.objects.all().filter(device_id = device_id)
        if not limit:
            limit = 10

        if not start:
            entries = SensorEntry.objects.all().filter(sensor__in = sensors).order_by('-timestamp')[:int(limit)]
        else:
            start_time = datetime.utcfromtimestamp(int(start)/1000.0)
            entries = SensorEntry.objects.all().filter(sensor__in = sensors, timestamp__gte = start_time).order_by('-timestamp')
        
        return create_json_response_for_models(entries)
    except ValueError:
        logger.error("ValueError")
        return HttpResponse("ValueError")
    except ObjectDoesNotExist:
        logger.warning("Device #" + device_id + " does not exists")
        return HttpResponse("Device #" + device_id + " does not exists")

def show_entry(request, entry_id):
    try:
        entry = SensorEntry.objects.get(id = int(entry_id))
        return create_json_response_for_model(entry)
    except ValueError:
        logger.error("ValueError")
        return HttpResponse("ValueError")
    except ObjectDoesNotExist:
        logger.warning("Entry #" + entry_id + " does not exists")
        return HttpResponse("Entry #" + entry_id + " does not exists")

def set_device(request, device_id):
    try:
        device = Device.objects.get(id = int(device_id))

        if request.method == 'POST':
            driver_name = device.name.lower()
            try:
                logger.debug("Trying to load 'drivers." + driver_name + "'")
                driver = __import__('drivers.' + driver_name, globals(), locals(), ['handle_post_data'], -1)
            except ImportError:
                driver = __import__('drivers.default', globals(), locals(), ['handle_post_data'], -1)

            driver.handle_post_data(request.POST.dict())
            logger.debug("Post request triggered by " + request.META['REMOTE_ADDR'])
            return create_json_response({"status": "ok"})
        else:
            return create_json_response({"status": "fail"})
    except ValueError:
        logger.error("ValueError")
        return HttpResponse("ValueError")
    except ObjectDoesNotExist:
        logger.warning("Device #" + device_id + " does not exists")
        return HttpResponse("Device #" + device_id + " does not exists")
