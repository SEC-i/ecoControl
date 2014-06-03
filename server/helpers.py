import os
import json
import logging
import datetime
import calendar
from django.http import HttpResponse

from server.worker import Worker
from server.models import Configuration, DeviceConfiguration, SensorValue

logger = logging.getLogger('django')


class WebAPIEncoder(json.JSONEncoder):

    def default(self, obj):
        # Support datetime and date instances
        if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
            return obj.isoformat()

        return json.JSONEncoder.default(self, obj)


def create_json_response(data, request):
    indent = None if request.is_ajax() else 2
    return HttpResponse(
        json.dumps(data, cls=WebAPIEncoder, sort_keys=True, indent=indent), content_type='application/json')


def start_worker():
    if not write_pidfile_or_fail("/tmp/worker.pid"):
        print 'Starting worker...'
        worker = Worker()
        worker.start()


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
