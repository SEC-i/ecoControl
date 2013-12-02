import json
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder

def create_json_response(data):
    response = HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')
    return response

def create_json_response_from_QuerySet(data):
    return create_json_response(list(data.values()))