import json
from django.http import HttpResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import Group

def create_json_response(data):
    response = HttpResponse(json.dumps(data, cls=DjangoJSONEncoder), content_type='application/json')
    return response

def create_json_response_from_QuerySet(data):
    return create_json_response(list(data.values()))

def is_in_group(user, group_id):
    """
    Takes a user and a group id, and returns `True` if the user is in that group.
    """
    return Group.objects.get(id=group_id).user_set.filter(id=user.id).exists()