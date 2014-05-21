import sys
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


logger = logging.getLogger('django')

