import json
from django.http import HttpResponse
from django.core import serializers

class JSONSerializer(json.JSONEncoder):
    def default(self, obj):
        import calendar, datetime
        # Support datetime instances
        if isinstance(obj, datetime.datetime):
            if obj.utcoffset() is not None:
                obj = obj - obj.utcoffset()
            milliseconds = int(
                calendar.timegm(obj.timetuple()) * 1000 +
                obj.microsecond / 1000
            )
            return milliseconds

        return json.JSONEncoder.default(self, obj)

def create_json_response(data):
    response = HttpResponse(json.dumps(data, cls=JSONSerializer), content_type='application/json')
    return response

def create_json_response_from_QuerySet(data):
    return create_json_response(list(data.values()))