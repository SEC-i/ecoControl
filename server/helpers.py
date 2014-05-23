import os
import json
import logging
import pytz
import calendar
import time
import csv

from django.http import HttpResponse

from server.forecasting import Simulation
from server.worker import Worker
from server.models import Configuration, DeviceConfiguration, SensorValue

logger = logging.getLogger('django')


class WebAPIEncoder(json.JSONEncoder):

    def default(self, obj):
        import calendar
        import datetime
        # Support datetime instances
        if isinstance(obj, datetime.datetime):
            if obj.utcoffset() is not None:
                obj = obj - obj.utcoffset()
            obj.replace(tzinfo=pytz.timezone('CET'))
            milliseconds = int(
                calendar.timegm(obj.timetuple()) * 1000 +
                obj.microsecond / 1000
            )
            return milliseconds
        if isinstance(obj, datetime.date):
            timestamp = int(
                calendar.timegm(obj.timetuple()) * 1000
            )
            return timestamp

        return json.JSONEncoder.default(self, obj)


def create_json_response(request, data):
    return HttpResponse(
        json.dumps(data, cls=WebAPIEncoder, sort_keys=True), content_type='application/json')


def create_json_response_from_QuerySet(request, data):
    return create_json_response(request, list(data.values()))


def create_csv_response_from_list(headers, rows):
    response = HttpResponse(content_type='text/csv')
    response[
        'Content-Disposition'] = 'attachment; filename="export_%s.csv"' % time.time()

    writer = csv.writer(response)
    writer.writerow(headers)
    for row in rows:
        writer.writerow(row)

    return response


def create_csv_response_from_dict_list(data):
    response = HttpResponse(content_type='text/csv')
    response[
        'Content-Disposition'] = 'attachment; filename="export_%s.csv"' % time.time()

    writer = csv.writer(response)
    for row in data:
        writer.writerow(row.keys())
        writer.writerow(row.values())

    return response


def create_csv_response_from_QuerySet(queryset):
    response = HttpResponse(content_type='text/csv')
    response[
        'Content-Disposition'] = 'attachment; filename="export_%s.csv"' % time.time()

    model = queryset.model
    writer = csv.writer(response)

    headers = []
    for field in model._meta.fields:
        headers.append(field.name)
    writer.writerow(headers)

    for obj in queryset:
        row = []
        for field in headers:
            val = getattr(obj, field)
            if callable(val):
                val = val()
            if type(val) == unicode:
                val = val.encode("utf-8")
            row.append(val)
        writer.writerow(row)

    return response


def is_member(user, group_name):
    return True if user.groups.filter(name=group_name) else False


def start_worker():
    if not write_pidfile_or_fail("/tmp/worker.pid"):
        print 'Starting worker...'
        worker = Worker()
        worker.start()


def start_demo_simulation(print_visible=False):
    """
    This method start a new demo simulation
    if neccessary and it makes sure that only
    one demo simulation can run at once
    """
    if not write_pidfile_or_fail("/tmp/simulation.pid"):
        # Start demo simulation if in demo mode
        system_mode = Configuration.objects.get(key='system_mode')
        if system_mode.value == 'demo':
            if print_visible:
                print 'Starting demo simulation...'
            else:
                logger.debug('Starting demo simulation...')

            simulation = Simulation(get_initial_time(), demo=True)
            simulation.start()


def get_initial_time():
    try:
        latest_value = SensorValue.objects.latest('timestamp')
        return calendar.timegm(latest_value.timestamp.timetuple())
    except SensorValue.DoesNotExist:
        return 1356998400  # Tuesday 1st January 2013 12:00:00


def pid_is_running(pid):
    """
    checks if pid belongs to a running process
    """
    try:
        os.kill(pid, 0)

    except OSError:
        return

    else:
        return pid


def write_pidfile_or_fail(path_to_pidfile):
    """
    writes pid to pidfile but returns false
    if pidfile belongs to running process
    """
    if os.path.exists(path_to_pidfile):
        pid = int(open(path_to_pidfile).read())

        if pid_is_running(pid):
            return False

        else:
            os.remove(path_to_pidfile)

    open(path_to_pidfile, 'w').write(str(os.getpid()))
    return path_to_pidfile
