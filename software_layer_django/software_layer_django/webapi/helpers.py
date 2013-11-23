#from django.utils import simplejson
import json
from django.http import HttpResponse

def create_api_response(data):
    response = HttpResponse(data)
    response['Content-Type'] = 'application/json'
    return response

def create_json_response(data):
    return create_api_response(json.dumps(data))

def create_json_response_for_model(data):
    objects = data.to_dict()
    return create_api_response(json.dumps(objects))

def create_json_response_for_models(data):
    objects = [ item.to_dict() for item in data]
    return create_api_response(json.dumps(objects))