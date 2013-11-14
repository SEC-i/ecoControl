#from django.utils import simplejson
import json
from django.http import HttpResponse

def create_json_response(data):
    response = HttpResponse(json.dumps(data))
    response['Access-Control-Allow-Origin'] = '*'
    response['Content-Type'] = 'application/json'
    return response

def create_json_response_for_model(data):
    objects = data.to_dict()
    response = HttpResponse(json.dumps(objects))
    response['Access-Control-Allow-Origin'] = '*'
    response['Content-Type'] = 'application/json'
    return response

def create_json_response_for_models(data):
    objects = [ item.to_dict() for item in data]
    response = HttpResponse(json.dumps(objects))
    response['Access-Control-Allow-Origin'] = '*'
    response['Content-Type'] = 'application/json'
    return response
