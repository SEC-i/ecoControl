import os
import json
import logging
import pytz
import calendar

from django.http import HttpResponse

from server.forecasting import Simulation
from server.models import DeviceConfiguration, SensorValue

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

        return json.JSONEncoder.default(self, obj)


def create_json_response(request, data):
    if 'callback' in request.GET:
        response = HttpResponse(
            "%s(%s);" % (
                request.GET['callback'], json.dumps(data, cls=WebAPIEncoder)),
            content_type='application/json'
        )
    else:
        response = HttpResponse(
            json.dumps(data, cls=WebAPIEncoder), content_type='application/json')
    return response


def create_json_response_from_QuerySet(request, data):
    return create_json_response(request, list(data.values()))


def start_demo_simulation():
    simulation = Simulation(demo=True, initial_time=get_initial_time())
    simulation.start()


def get_initial_time():
    try:
        latest_value = SensorValue.objects.latest('timestamp')
        return calendar.timegm(latest_value.timestamp.timetuple())
    except SensorValue.DoesNotExist:
        return 1356998400  # Tuesday 1st January 2013 12:00:00

# checks if pid belongs to a running process


def pid_is_running(pid):
    try:
        os.kill(pid, 0)

    except OSError:
        return

    else:
        return pid

# writes pid to pidfile but returns false if pidfile belongs to running process


def write_pidfile_or_fail(path_to_pidfile):
    if os.path.exists(path_to_pidfile):
        pid = int(open(path_to_pidfile).read())

        if pid_is_running(pid):
            # print("Sorry, found a pidfile!  Process {0} is still running.".format(pid))
            return False

        else:
            os.remove(path_to_pidfile)

    open(path_to_pidfile, 'w').write(str(os.getpid()))
    return path_to_pidfile
