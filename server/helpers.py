import json
import logging
import datetime
import calendar
from django.http import HttpResponse

from server.worker import Worker
from server.models import Configuration, DeviceConfiguration, SensorValue

from helpers_thread import write_pidfile_or_fail

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
