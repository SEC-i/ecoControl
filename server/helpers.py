import json
import logging
import pytz

from django.http import HttpResponse

from models import DeviceConfiguration

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