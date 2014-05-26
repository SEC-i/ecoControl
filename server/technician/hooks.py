import sys
import os
import logging
from time import time
import json

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST
from django.views.decorators.debug import sensitive_post_parameters
from django.utils.timezone import utc
from django.db.models import Count, Min, Sum, Avg
from django.db import connection

from server.models import Device, Configuration, DeviceConfiguration, Sensor, SensorValue, SensorValueHourly, SensorValueDaily, Threshold, Notification
from server.helpers import create_json_response

import functions

logger = logging.getLogger('django')


def handle_snippets(request):
    output = []

    if request.method == 'POST':
        data = json.loads(request.body)
        if 'name' in data:
            if 'code' in data:
                return create_json_response(functions.save_snippet(data['name'], data['code']))
            else:
                return create_json_response(functions.get_snippet_code(data['name']))

    return create_json_response(functions.get_snippet_list())
